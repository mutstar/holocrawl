#include "AppHdr.h"
#include "holo-dungeon-test.h"
#include "holo-campaign.h"
#include "holo-worship.h"
#include "holo-batch-internal.h"
#include "holo-sopia.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <map>
#include <queue>
#include <sstream>
#include <stdexcept>
#include "act-iter.h"
#include "artefact.h"
#include "cloud.h"
#include "item-prop.h"
#include "item-status-flag-type.h"
#include "mon-info.h"
#include "clua.h"
#include "command-type.h"
#include "delay.h"
#include "env.h"
#include "files.h"
#include "food.h"
#include "item-name.h"
#include "item-use.h"
#include "items.h"
#include "macro.h"
#include "map-knowledge.h"
#include "message.h"
#include "mon-util.h"
#include "newgame.h"
#include "ng-setup.h"
#include "options.h"
#include "player.h"
#include "random.h"
#include "skills.h"
#include "state.h"
#include "store.h"
#include "tags.h"
#include "terrain.h"
#include "travel.h"
#include "view.h"

extern void process_command(command_type command);
extern void world_reacts();
namespace holo_dungeon {
namespace {
bool running=false,dead=false;
bool improved=false;
int death_cause=-1;
std::string death_aux;
std::ofstream events;
int actions=0,casts=0,max_depth=1,transitions=0,rests=0,failed=0;
int last_ring=-1000;
const coord_def dirs[]={coord_def(-1,0),coord_def(0,1),coord_def(0,-1),coord_def(1,0),
    coord_def(-1,-1),coord_def(-1,1),coord_def(1,-1),coord_def(1,1)};
const command_type moves[]={CMD_MOVE_LEFT,CMD_MOVE_DOWN,CMD_MOVE_UP,CMD_MOVE_RIGHT,
    CMD_MOVE_UP_LEFT,CMD_MOVE_DOWN_LEFT,CMD_MOVE_UP_RIGHT,CMD_MOVE_DOWN_RIGHT};
std::string env_string(const char *name,const char *fallback="") {
    const char *v=getenv(name);return v?v:fallback;
}
int number(const char *name,int fallback){const auto s=env_string(name);return s.empty()?fallback:std::stoi(s);}
void require(bool condition,const std::string &message){if(!condition)throw std::runtime_error("Dungeon pilot: "+message);}
std::string quoted(const std::string &value) {
    std::string result="\"";
    for(char c:value){if(c=='\\'||c=='\"')result+='\\';if(c=='\n')result+="\\n";else if(c=='\r')result+="\\r";else result+=c;}
    return result+'"';
}
void event(const std::string &kind,const std::string &detail="") {
    events<<"{\"event\":"<<quoted(kind)<<",\"detail\":"<<quoted(detail)
        <<",\"action\":"<<actions<<",\"aut\":"<<you.elapsed_time<<",\"depth\":"<<you.depth
        <<",\"xl\":"<<int(you.experience_level)<<",\"hp\":"<<you.hp<<",\"maxHp\":"<<you.hp_max
        <<",\"mp\":"<<int(you.magic_points)<<",\"piety\":"<<int(you.piety)
        <<",\"god\":"<<quoted(holo_worship::current())<<",\"x\":"<<you.pos().x<<",\"y\":"<<you.pos().y<<"}\n";
    events.flush();
}
std::string terrain_fingerprint() {
    // Audit only: hidden terrain is never consulted by the policy.
    uint64_t hash=1469598103934665603ULL;
    for(int x=0;x<GXM;++x)for(int y=0;y<GYM;++y){hash^=uint64_t(grd[x][y]);hash*=1099511628211ULL;}
    std::ostringstream out;out<<std::hex<<hash;return out.str();
}
std::string core_signature(bool include_ui=true) {
    std::ostringstream out;
    if(holo_worship::active())out<<holo_batch::save_campaign()<<'|'<<holo_sopia::save_campaign();
    else out<<"no_holo_core";
    out<<'|';
    for(int i=0;i<rng::NUM_RNGS;++i) {
        if(!include_ui && i==rng::UI)continue;
        // get_generator's argument is ignored in upstream 0.24. Select the
        // stream with its supported RAII scope and inspect without drawing.
        rng::generator selected{rng::rng_type(i)};
        auto &generator=rng::current_generator();
        out<<i<<' '<<generator.get_state()<<' '<<generator.get_inc()<<'\n';
    }
    return out.str();
}
bool known_step(const coord_def &p) {
    if(!in_bounds(p) || !env.map_knowledge(p).seen())return false;
    const auto occupant=you.see_cell(p)?monster_at(p):nullptr;
    if(occupant && you.can_see(*occupant) && occupant->attitude==ATT_FRIENDLY)return false;
    const auto f=env.map_knowledge(p).feat();
    return !feat_is_trap(f) && !feat_is_water(f) && !feat_is_lava(f)
        && (!improved || !you.see_cell(p) || cloud_type_at(p)==CLOUD_NONE)
        && (feat_is_traversable_now(f) || f==DNGN_CLOSED_DOOR);
}
bool frontier(const coord_def &p) {
    if(!known_step(p))return false;
    for(auto d:dirs)if(in_bounds(p+d) && !env.map_knowledge(p+d).known())return true;
    return false;
}
bool avoid_route_step(coord_def from,coord_def to);
coord_def path_to(const std::function<bool(coord_def)> &goal,bool avoid_danger=false) {
    std::queue<coord_def> queue;std::map<coord_def,coord_def> first;
    const auto origin=you.pos();queue.push(origin);first[origin]=origin;
    while(!queue.empty()) {
        const auto p=queue.front();queue.pop();
        if(p!=origin && goal(p))return first[p];
        for(auto d:dirs){const auto q=p+d;if(first.count(q) || !known_step(q) || (avoid_danger && !avoid_route_step(p,q)))continue;
            first[q]=p==origin?q:first[p];queue.push(q);}
    }
    return origin;
}
monster *enemy() {
    monster *target=nullptr;
    for(monster_iterator mi;mi;++mi)if(mi->alive() && mi->attitude==ATT_HOSTILE && you.can_see(**mi) && you.see_cell_no_trans(mi->pos()))
        if(!target || grid_distance(you.pos(),mi->pos())<grid_distance(you.pos(),target->pos()))target=*mi;
    return target;
}
int enemy_count(){int n=0;for(monster_iterator mi;mi;++mi)if(mi->attitude==ATT_HOSTILE && you.can_see(**mi) && you.see_cell_no_trans(mi->pos()))++n;return n;}
void command(command_type cmd) {
    you.turn_is_over=false;you.time_taken=player_speed();crawl_state.prev_cmd=cmd;process_command(cmd);
}
void move(const coord_def &dest) {
    for(size_t i=0;i<8;++i)if(you.pos()+dirs[i]==dest){command(moves[i]);return;}
}
bool cast(int tier,monster *target,const coord_def &aim,int option=0,int amount=3) {
    const int aut=holo_campaign::invoke(tier,target,&aim,option,amount);
    if(aut<=0)return false;
    ++casts;event("power",std::to_string(tier)+":"+std::to_string(option));return true;
}
bool powers(monster *m) {
    if(!m || !holo_worship::active() || you.piety<30)return false;
    using namespace holo_batch;
    const auto g=holo_worship::current();const auto here=you.pos(),aim=m->pos();
    const int distance=grid_distance(here,aim);const bool danger=you.hp*2<you.hp_max || enemy_count()>=3;
    you.turn_is_over=false;you.time_taken=0;manual_positions.clear();
    if(g=="noel"){if(danger && cast(5,nullptr,here))return true;return cast(1,nullptr,here);}
    if(g=="suisei"){
        if(danger && distance>1 && cast(5,nullptr,aim))return true;
        if(s.resource>=3 && cast(3,nullptr,aim))return true;
        return (s.marked!=m->mid || s.one_end<=you.elapsed_time) && cast(1,m,aim);
    }
    if(g=="miko"){
        if(danger && cast(5,nullptr,here))return true;
        if(s.one_end<=you.elapsed_time || grid_distance(s.centre,here)>2)return cast(1,nullptr,here);
        return s.three_end<=you.elapsed_time && cast(3,nullptr,here);
    }
    if(g=="aki"){
        if(s.one_end<=you.elapsed_time)return cast(1,nullptr,here);
        if(danger && cast(5,nullptr,here))return true;
        std::vector<coord_def> cells;for(auto d:dirs)if(in_bounds(here+d) && !actor_at(here+d) && grd(here+d)==DNGN_FLOOR)cells.push_back(here+d);
        if(cells.size()>=2){manual_second=cells[1];return cast(3,nullptr,cells[0]);}return false;
    }
    if(g=="fubuki"){
        if(danger && cast(5,nullptr,here))return true;
        if(you.hp*2<you.hp_max)for(auto c:s.companions){auto *fox=monster_by_mid(c.mid);if(fox && fox->alive() && you.can_see(*fox) && cast(3,fox,fox->pos()))return true;}
        for(auto d:dirs)if(in_bounds(here+d) && you.see_cell(here+d) && !actor_at(here+d) && grd(here+d)==DNGN_FLOOR)return cast(1,nullptr,here+d);
        return false;
    }
    if(g=="ayame"){if(distance==1 && danger && cast(5,m,aim))return true;return distance==1 && cast(3,m,aim);}
    if(g=="choco"){
        if(s.marked!=m->mid || s.one_end<=you.elapsed_time)return cast(1,m,aim);
        if(s.resource>=3 && cast(5,m,aim))return true;
        return distance==1 && cast(3,m,aim);
    }
    if(g=="korone"){if(danger && s.resource>=6 && cast(5,nullptr,here))return true;return distance==1 && s.resource>=3 && cast(3,m,aim);}
    if(g=="okayu"){
        if(s.targets[m->mid].stacks>=2 && distance<=3 && cast(5,m,aim))return true;
        return (s.marked!=m->mid || s.one_end<=you.elapsed_time) && cast(3,m,aim);
    }
    if(g=="pekora"){
        for(auto h:s.hazards)if(h.kind==10 && h.end>you.elapsed_time && h.arm<=you.elapsed_time
            && you.see_cell(h.pos) && grid_distance(here,h.pos)>1 && grid_distance(aim,h.pos)<=1)return cast(3,nullptr,h.pos);
        if(distance>=3)for(auto d:dirs){const auto p=aim+d;if(in_bounds(p) && you.see_cell(p) && !actor_at(p) && grd(p)==DNGN_FLOOR && grid_distance(here,p)>1 && grid_distance(here,p)<=3 && cast(1,nullptr,p))return true;}
        return false;
    }
    if(g=="watame"){if(danger && cast(5,nullptr,here))return true;return cast(3,nullptr,here);}
    if(g=="towa"){if(danger && cast(5,nullptr,here))return true;return s.one_end<=you.elapsed_time && distance<=5 && cast(3,nullptr,aim);}
    if(g=="lamy"){
        if(danger && s.resource>=61 && cast(5,nullptr,here))return true;
        if(s.resource>=20 && distance<=4 && cast(3,m,aim))return true;
        return s.resource<30 && cast(1,nullptr,here);
    }
    if(g=="polka"){
        if(s.resource>=3 && cast(5,nullptr,here,you.hp*3<you.hp_max*2?1:2,std::min(6,s.resource)))return true;
        return s.secondary==0 && cast(1,m,aim,m->get_experience_level()>=you.experience_level?1:2);
    }
    if(g=="koyori"){
        if(danger && cast(5,nullptr,here,3))return true;
        const int type=s.targets[m->mid].kind==1?2:1;
        if(s.stock[type-1]>0)return cast(1,m,aim,10+type);
        return cast(1,nullptr,here,type);
    }
    if(g=="lui"){
        if(danger && cast(5,nullptr,here))return true;
        if(cast(1,nullptr,here))return true;
        return cast(3,m,aim);
    }
    if(g=="raden"){
        if(danger && cast(5,nullptr,here))return true;
        return distance>=3 && s.targets[m->mid].paint>0 && cast(3,m,aim,0);
    }
    if(g=="hajime"){if(danger && cast(5,nullptr,here))return true;return distance>=2 && distance<=3 && cast(3,m,aim);}
    if(g=="su"){if(danger && cast(5,nullptr,here))return true;return distance<=5 && cast(3,nullptr,aim);}
    if(g=="vivi"){
        if(danger && cast(5,nullptr,here))return true;
        if(s.one_end<=you.elapsed_time)return cast(1,nullptr,here);
        return distance<=2 && cast(3,nullptr,here);
    }
    if(g=="sopia"){
        if(danger && cast(5,nullptr,here))return true;
        if(cast(6,nullptr,here))return true;
        if(you.elapsed_time-last_ring>=100 && cast(1,nullptr,here)){last_ring=you.elapsed_time;return true;}
        return false;
    }
    if(g=="mela"){if(danger && cast(5,nullptr,here))return true;return s.resource>=3 && distance<=3 && cast(3,nullptr,aim);}
    return false;
}
bool consume(monster *m) {
    for(auto &item:you.inv) {
        if(!item.defined())continue;
        if(!m && you.hunger<HUNGER_HUNGRY && item.base_type==OBJ_FOOD && can_eat(item,true)) {
            you.turn_is_over=false;you.time_taken=0;if(eat_item(item)){event("food");return true;}
        }
        if(m && item.base_type==OBJ_POTIONS && item_type_known(item)
            && ((you.hp*3<you.hp_max*2 && (item.sub_type==POT_HEAL_WOUNDS || item.sub_type==POT_CURING))
                || (grid_distance(you.pos(),m->pos())==1 && m->get_experience_level()>you.experience_level+1 && item.sub_type==POT_MIGHT && !you.duration[DUR_MIGHT]))) {
            you.turn_is_over=false;you.time_taken=0;drink(&item);if(you.turn_is_over){event("potion");return true;}
        }
    }
    return false;
}

int bot_value(const std::string &key) {
    return you.props.exists(key)?you.props[key].get_int():0;
}
void bot_add(const std::string &key) {you.props[key]=bot_value(key)+1;}
// Use base item properties and identified bonuses only. No unknown curse,
// enchantment, artefact property or unseen floor item is read by scoring.
int gear_score(const item_def &item) {
    if(!item.defined())return -10000;
    const int plus=item_ident(item,ISFLAG_KNOW_PLUSES)?item.plus:0;
    if(item.base_type==OBJ_WEAPONS) {
        // Keep this Human Fighter's trained, shield-compatible long blades.
        if(item.sub_type!=WPN_FALCHION && item.sub_type!=WPN_LONG_SWORD
            && item.sub_type!=WPN_SCIMITAR && item.sub_type!=WPN_DEMON_BLADE
            && item.sub_type!=WPN_DOUBLE_SWORD)return -10000;
        int brand=0;
        if(item_type_known(item)) {
            switch(get_weapon_brand(item)) {
            case SPWPN_DISTORTION:case SPWPN_CHAOS:return -10000;
            case SPWPN_ELECTROCUTION:case SPWPN_SPEED:brand=30;break;
            case SPWPN_FLAMING:case SPWPN_FREEZING:case SPWPN_VENOM:
            case SPWPN_DRAINING:case SPWPN_VAMPIRISM:brand=18;break;
            default:break;
            }
        }
        return (property(item,PWPN_DAMAGE)*10+plus*7+brand)*14/property(item,PWPN_SPEED);
    }
    if(item.base_type==OBJ_ARMOUR) {
        const auto slot=get_armour_slot(item);
        // Do not jump to an untrained large shield and its heavy attack penalty.
        if(slot==EQ_SHIELD && item.sub_type==ARM_LARGE_SHIELD)return -10000;
        return (property(item,PARM_AC)+plus)*20
            + (slot==EQ_BODY_ARMOUR?property(item,PARM_EVASION)/2:0);
    }
    return -10000;
}
bool gear_upgrade(const item_def &item) {
    if(item_known_cursed(item) || is_artefact(item))return false;
    const int score=gear_score(item);if(score<=-10000)return false;
    const auto slot=item.base_type==OBJ_WEAPONS?EQ_WEAPON:get_armour_slot(item);
    const int old=you.equip[slot];
    if(old>=0 && item_known_cursed(you.inv[old]))return false;
    if(old>=0 && slot==EQ_WEAPON && item_type_known(you.inv[old])
        && get_weapon_brand(you.inv[old])==SPWPN_DISTORTION)return false;
    if(old>=0 && score<=gear_score(you.inv[old])+3)return false;
    return item.base_type==OBJ_WEAPONS?can_wield(&item,false):can_wear_armour(item,false,false);
}
bool equipment() {
    for(int i=0;i<ENDOFPACK;++i) {
        auto &item=you.inv[i];
        if(!item.defined() || item_is_equipped(item) || !gear_upgrade(item))continue;
        const auto name=item.name(DESC_PLAIN);
        you.turn_is_over=false;you.time_taken=player_speed();
        const bool ok=item.base_type==OBJ_WEAPONS?wield_weapon(false,i):wear_armour(i);
        if(ok){event("equipment_change_requested",name);return true;}
        if(you.turn_is_over || you_are_delayed())return true;
    }
    if(inv_count()>=ENDOFPACK-2)return false;
    const auto *item=top_item_at(you.pos());
    // Walk the visible stack so a corpse/gold pile cannot hide useful armour.
    for(int index=item?int(item-&mitm[0]):NON_ITEM;index!=NON_ITEM;) {
        const auto &floor=mitm[index];const int next=floor.link;
        if(gear_upgrade(floor)) {
            const auto name=floor.name(DESC_PLAIN);
            you.turn_is_over=false;you.time_taken=player_speed();
            if(pickup_single_item(index,1)){bot_add("holo_bot_pickups");event("equipment_pickup",name);return true;}
        }
        index=next;
    }
    return false;
}
std::string avoid_key(){return "holo_bot_avoid_"+std::to_string(you.depth);}
void avoid_enemy(const monster &m) {
    const auto key=avoid_key();you.props[key+"x"]=m.pos().x;you.props[key+"y"]=m.pos().y;
    you.props[key+"xl"]=int(you.experience_level);you.props[key+"at"]=you.elapsed_time;
}
bool avoid_cell(coord_def p) {
    const auto key=avoid_key();if(!you.props.exists(key+"xl"))return false;
    // Reconsider after two levels, rather than repeatedly re-engaging a unique.
    if(int(you.experience_level)>=bot_value(key+"xl")+2)return false;
    return grid_distance(p,coord_def(bot_value(key+"x"),bot_value(key+"y")))<=4;
}
bool avoid_route_step(coord_def from,coord_def to) {
    if(!improved || !avoid_cell(to))return true;
    if(!avoid_cell(from))return false;
    const auto key=avoid_key();const coord_def centre(bot_value(key+"x"),bot_value(key+"y"));
    // Permit escape from the remembered danger, never route back through it.
    return grid_distance(to,centre)>grid_distance(from,centre);
}
bool banned_down(coord_def p) {
    const auto key="holo_bot_banned_down_"+std::to_string(you.depth);
    return you.props.exists(key+"xl") && int(you.experience_level)<bot_value(key+"xl")+2
        && p==coord_def(bot_value(key+"x"),bot_value(key+"y"));
}
std::vector<coord_def> visible_threats() {
    std::vector<coord_def> result;
    for(monster_iterator mi;mi;++mi)if(mi->alive() && mi->attitude==ATT_HOSTILE
        && you.can_see(**mi) && you.see_cell_no_trans(mi->pos()))result.push_back(mi->pos());
    return result;
}
int threat_distance(coord_def p,const std::vector<coord_def> &enemies) {
    int nearest=100;for(auto q:enemies)nearest=std::min(nearest,grid_distance(p,q));return nearest;
}
bool retreat(monster *m) {
    if(!m)return false;
    const monster_info info(m);const auto enemies=visible_threats();
    const int distance=threat_distance(you.pos(),enemies);
    int adjacent_count=0;for(auto p:enemies)adjacent_count+=adjacent(p,you.pos());
    bool nasty=false;
    for(monster_iterator mi;mi;++mi)if(mi->alive() && mi->attitude==ATT_HOSTILE && you.can_see(**mi)
        && you.see_cell_no_trans(mi->pos()) && mons_threat_level(**mi)==MTHRT_NASTY){nasty=true;avoid_enemy(**mi);}
    const bool low=you.hp*100<you.hp_max*50;
    const bool crowded=(enemies.size()>=3 || adjacent_count>=2) && you.hp*4<you.hp_max*3;
    if(!nasty && !low && !crowded
        && (bot_value("holo_bot_flee_until")<you.elapsed_time || you.hp*4>=you.hp_max*3))return false;
    if(nasty || low || crowded)you.props["holo_bot_flee_until"]=you.elapsed_time+20;
    // Take an actual staircase escape, preserving native pursuit and delay.
    if(you.depth>1 && feat_is_stone_stair_up(grd(you.pos()))) {
        if(nasty && bot_value("holo_bot_entry_depth")==you.depth-1) {
            const auto key="holo_bot_banned_down_"+std::to_string(you.depth-1);
            you.props[key+"x"]=bot_value("holo_bot_entry_x");you.props[key+"y"]=bot_value("holo_bot_entry_y");
            you.props[key+"xl"]=int(you.experience_level);
        }
        bot_add("holo_bot_retreats");event("retreat_stairs",m->name(DESC_PLAIN));command(CMD_GO_UPSTAIRS);return true;
    }
    // A faster adjacent pursuer cannot be kited indefinitely. Fight/use powers
    // if no step reduces the number of enemies in contact.
    const bool fast_adjacent=distance==1 && info.base_speed()>10;
    const auto upstairs=path_to([](coord_def p){return feat_is_stone_stair_up(env.map_knowledge(p).feat());});
    coord_def best=you.pos();int best_score=-100000;
    for(auto d:dirs) {
        const auto p=you.pos()+d;
        if(!known_step(p) || env.map_knowledge(p).feat()==DNGN_CLOSED_DOOR)continue;
        const auto occupant=monster_at(p);if(occupant && you.can_see(*occupant))continue;
        int contacts=0;for(auto q:enemies)contacts+=adjacent(p,q);
        const int away=threat_distance(p,enemies);
        if(away<distance || (fast_adjacent && contacts>=adjacent_count))continue;
        int exits=0;for(auto step:dirs)if(known_step(p+step))++exits;
        int score=away*100-contacts*80+std::min(4,exits)*3;
        if(p==upstairs && you.depth>1)score+=70;
        if(p==coord_def(bot_value("holo_bot_prev_x"),bot_value("holo_bot_prev_y")))score-=12;
        if(score>best_score){best=p;best_score=score;}
    }
    if(best==you.pos() || (distance==1 && threat_distance(best,enemies)==1 && adjacent_count<=1))return false;
    you.props["holo_bot_prev_x"]=you.pos().x;you.props["holo_bot_prev_y"]=you.pos().y;
    bot_add("holo_bot_retreats");event("retreat",m->name(DESC_PLAIN)+":"+(nasty?"nasty":low?"low_hp":"crowded"));move(best);return true;
}

void policy(const std::string &target_god,const std::string &mode) {
    holo_dungeon_prep_input();
    if(you.cannot_act()){you.time_taken=10;you.turn_is_over=true;return;}
    if(you_are_delayed()){handle_delay();if(you.time_taken>0)you.turn_is_over=true;return;}
    monster *m=enemy();
    if(consume(m))return;
    if(improved && retreat(m))return;
    if(m) {
        if(powers(m))return;
        if(adjacent(you.pos(),m->pos())){move(m->pos());return;}
        const auto next=path_to([&](coord_def p){return adjacent(p,m->pos());});
        if(next!=you.pos()){move(next);return;}
        command(CMD_WAIT);return;
    }
    if(mode=="natural" && target_god!="no_god" && !holo_worship::active() && feat_is_altar(grd(you.pos()))) {
        const auto gods=holo_worship::gods();const auto it=std::find(gods.begin(),gods.end(),target_god);
        macro_sendkeys_end_add_expanded('a'+(it-gods.begin()));macro_sendkeys_end_add_expanded('Y');
        command(CMD_GO_UPSTAIRS);
        if(holo_worship::active()){you.train[SK_INVOCATIONS]=TRAINING_ENABLED;reset_training();event("natural_join");}return;
    }
    if(need_to_autopickup()){autopickup();if(you.turn_is_over)return;}
    if(improved){you.props["holo_bot_flee_until"]=0;if(equipment())return;}
    if(you.hp<you.hp_max || you.magic_points<you.max_magic_points){++rests;command(CMD_WAIT);return;}
    // One genuine up/down staircase round trip, with native delays/followers.
    const int trip=you.props.exists("holo_pilot_stairs")?you.props["holo_pilot_stairs"].get_int():0;
    if(trip==1 && you.depth==2) {
        if(feat_is_stone_stair_up(grd(you.pos()))){command(CMD_GO_UPSTAIRS);return;}
        const auto p=path_to([](coord_def q){return feat_is_stone_stair_up(env.map_knowledge(q).feat());});
        if(p!=you.pos()){move(p);return;}
    }
    if(trip==2 && you.depth==1 && feat_is_stone_stair_down(grd(you.pos()))){command(CMD_GO_DOWNSTAIRS);return;}
    if(mode=="natural" && target_god!="no_god" && !holo_worship::active()) {
        const auto p=path_to([](coord_def q){return feat_is_altar(env.map_knowledge(q).feat());});
        if(p!=you.pos()){move(p);return;}
    }
    if(improved && inv_count()<ENDOFPACK-2) {
        const auto loot=path_to([](coord_def p){
            if(!you.see_cell(p) || avoid_cell(p))return false;
            const auto *top=top_item_at(p);
            for(int index=top?int(top-&mitm[0]):NON_ITEM;index!=NON_ITEM;index=mitm[index].link)
                if(gear_upgrade(mitm[index]))return true;
            return false;
        },true);
        if(loot!=you.pos()){move(loot);return;}
    }
    auto next=path_to([](coord_def p){return frontier(p) && (!improved || (!avoid_cell(p) && !banned_down(p)));},improved);
    if(next!=you.pos()){move(next);return;}
    if(feat_is_stone_stair_down(grd(you.pos())) && (!improved || !banned_down(you.pos()))){command(CMD_GO_DOWNSTAIRS);return;}
    next=path_to([](coord_def p){return feat_is_stone_stair_down(env.map_knowledge(p).feat()) && (!improved || (!avoid_cell(p) && !banned_down(p)));},improved);
    if(next!=you.pos()){move(next);return;}
    ++failed;command(CMD_WAIT);
}
void close_save(){if(you.save){delete you.save;you.save=nullptr;}}
void report(const std::string &dir,const std::string &outcome,int seed,const std::string &god,const std::string &mode,int target) {
    std::ofstream out(dir+"/result.json");
    out<<"{\"status\":\"completed\",\"outcome\":"<<quoted(outcome)<<",\"seed\":"<<seed
        <<",\"requestedGod\":"<<quoted(god)<<",\"mode\":"<<quoted(mode)<<",\"targetDepth\":"<<target
        <<",\"maxDepth\":"<<max_depth<<",\"actions\":"<<actions<<",\"aut\":"<<you.elapsed_time
        <<",\"xl\":"<<int(you.experience_level)<<",\"hp\":"<<you.hp<<",\"piety\":"<<int(you.piety)
        <<",\"joinedGod\":"<<quoted(holo_worship::current())<<",\"powers\":"<<casts<<",\"stairs\":"<<transitions
        <<",\"restActions\":"<<rests<<",\"policyFailures\":"<<failed<<",\"deathCause\":"<<death_cause
        <<",\"stairsRoundtrip\":"<<(you.props.exists("holo_pilot_stairs") && you.props["holo_pilot_stairs"].get_int()==3?"true":"false")
        <<",\"policyVersion\":"<<quoted(improved?"equipment-retreat01":"baseline")
        <<",\"equipmentChanges\":"<<bot_value("holo_bot_equips")
        <<",\"equipmentPickups\":"<<bot_value("holo_bot_pickups")
        <<",\"retreatActions\":"<<bot_value("holo_bot_retreats")
        <<",\"deathAux\":"<<quoted(death_aux)<<",\"rngNotResetDuringPlay\":true,\"startingStatsUnmodified\":true}\n";
}
}
bool requested(){return crawl_state.test && env_string("HOLOCRAWL_DUNGEON_TEST")=="1";}
bool active(){return running;}
bool finished(){return running && dead;}
bool record_death(kill_method_type cause,const char *aux,mid_t source) {
    if(!running || you.hp>0)return false;
    if(!dead){
        dead=true;death_cause=int(cause);death_aux=aux?aux:"";
        const auto attacker=monster_by_mid(source);
        if(attacker)death_aux=attacker->name(DESC_PLAIN)+(death_aux.empty()?"":" / "+death_aux);
        event("death",death_aux);
    }
    return true;
}
int run() {
    running=true;dead=false;improved=env_string("HOLOCRAWL_DUNGEON_POLICY","improved")=="improved";
    const auto dir=env_string("HOLOCRAWL_DUNGEON_OUTPUT");require(!dir.empty(),"output directory required");
    const int seed=number("HOLOCRAWL_DUNGEON_SEED",101),target=number("HOLOCRAWL_DUNGEON_DEPTH",5),budget=number("HOLOCRAWL_DUNGEON_ACTIONS",5000);
    const auto god=env_string("HOLOCRAWL_DUNGEON_GOD","no_god"),mode=env_string("HOLOCRAWL_DUNGEON_MODE","natural");
    require(mode=="natural" || mode=="assigned","unknown mode");
    const auto gods=holo_worship::gods();require(god=="no_god" || std::find(gods.begin(),gods.end(),god)!=gods.end(),"unknown god");
    const auto character_name=env_string("HOLOCRAWL_DUNGEON_NAME","HoloDungeon");
    Options.no_save=false;Options.save_dir=env_string("HOLOCRAWL_DUNGEON_SAVEDIR",dir.c_str());Options.morgue_dir=dir;Options.pregen_dungeon=false;Options.seed=seed;
    crawl_state.show_more_prompt=false;set_more_autoclear(true);
    const bool resume=env_string("HOLOCRAWL_DUNGEON_RESUME")=="1";
    events.open(dir+"/events.jsonl",resume?std::ios::app:std::ios::out);
    if(resume) {
        crawl_state.bypassed_startup_menu=true;
        require(restore_game(get_save_filename(character_name)),"restore real dungeon save");
        {
            std::ifstream core(dir+"/checkpoint-core.txt");
            const std::string expected((std::istreambuf_iterator<char>(core)),{});
            require(expected==core_signature(),"native restore changed saved core/RNG state before UI startup");
        }
        holo_dungeon_post_init(false);
        std::ifstream state(dir+"/checkpoint.txt");int hp,piety,depth,at;
        state>>actions>>casts>>max_depth>>transitions>>rests>>failed>>last_ring>>hp>>piety>>depth>>at;
        require(bool(state) && hp==you.hp && piety==you.piety && depth==you.depth && at==you.elapsed_time,"checkpoint player state changed");event("resume");
        event("native_save_all_rng_exact");
        // Upstream viewwindow's monster safety/pathfinding may also consume
        // GAMEPLAY on restart. The full saved state was checked before it.
        // Preserve those native draws; require the ability state unchanged.
        std::ifstream core(dir+"/checkpoint-gameplay-core.txt");
        const std::string expected((std::istreambuf_iterator<char>(core)),{});
        const auto actual=core_signature(false);
        if(expected!=actual){std::ofstream debug(dir+"/restore-actual-core.txt");debug<<actual;}
        require(expected.substr(0,expected.rfind('|'))==actual.substr(0,actual.rfind('|')),
                "native restart changed persisted ability state");
        event("resume_core_exact");
        if(expected!=actual)event("native_restart_rng_advanced","upstream viewwindow / monster safety pathfinding; RNG preserved, not reset");
        std::ifstream allies(dir+"/checkpoint-allies.txt");int count=0;allies>>count;
        for(int i=0;i<count;++i){mid_t mid;int mhp,x,y;allies>>mid>>mhp>>x>>y;const auto m=monster_by_mid(mid);
            require(m && m->alive() && m->hit_points==mhp && m->pos()==coord_def(x,y),"native companion missing or moved during restore");}
        require(bool(allies),"companion checkpoint missing");event("resume_native_allies_exact",std::to_string(count));
    } else {
        newgame_def ng;ng.name=character_name;ng.type=GAME_TYPE_CUSTOM_SEED;ng.species=SP_HUMAN;ng.job=JOB_FIGHTER;ng.weapon=WPN_LONG_SWORD;ng.seed=seed;
        setup_game(ng);holo_dungeon_post_init(true);
        require(you.experience_level==1 && you.depth==1 && !you.wizard && !holo_worship::active(),"normal D:1 startup invariant");
        event("start",terrain_fingerprint());
        if(mode=="assigned" && god!="no_god") {
            const auto original=grd(you.pos());grd(you.pos())=DNGN_ALTAR_OKAWARU;
            require(holo_worship::join(god,false),"diagnostic D:1 membership assignment");grd(you.pos())=original;
            you.train[SK_INVOCATIONS]=TRAINING_ENABLED;reset_training();event("diagnostic_assignment","membership only; original terrain restored; initial piety 15");
            world_reacts();
        } else {command(CMD_WAIT);world_reacts();}
    }
    // Supported native user hook; every third XL chooses Strength through
    // the ordinary attribute prompt path, without writing character stats.
    require(clua.execstring("function choose_stat_gain() return 'S' end")==0,"native stat-choice hook");
    if(improved)require(clua.execstring(
        "function c_answer_prompt(prompt) "
        "if prompt == 'Keep equipping yourself?' or prompt == 'Keep disrobing?' then return false end "
        "return nil end")==0,"native equipment interruption response");
    int stuck=0;std::string outcome="action_limit";
    const int checkpoint_at=number("HOLOCRAWL_DUNGEON_CHECKPOINT",250);
    while(actions<budget && !dead) {
        if(you.where_are_you!=BRANCH_DUNGEON){outcome="left_main_dungeon";break;}
        if(you.depth>=target){outcome="target_reached";break;}
        const auto old=level_id::current();const auto old_pos=you.pos();const int before=you.elapsed_time;
        std::vector<int> equipment_before;for(int i=0;i<NUM_EQUIP;++i)equipment_before.push_back(you.equip[i]);
        // A rejected move must not freeze timers: reconsider after a normal
        // wait, just as a player can wait for a stationary image to expire.
        if(stuck>0 && !you_are_delayed())command(CMD_WAIT);else policy(god,mode);
        ++actions;
        if(you.turn_is_over)world_reacts();
        if(improved)for(int i=0;i<NUM_EQUIP;++i)if(equipment_before[i]!=you.equip[i] && you.equip[i]>=0) {
            bot_add("holo_bot_equips");event("equipment_equipped",std::to_string(i)+":"+you.inv[you.equip[i]].name(DESC_PLAIN));
        }
        if(you.elapsed_time==before){++stuck;event("no_time_action");}else stuck=0;
        if(stuck>=20 || failed>=20){outcome="policy_stalled";break;}
        if(level_id::current()!=old){
            if(improved && you.depth>old.depth) {you.props["holo_bot_entry_x"]=old_pos.x;you.props["holo_bot_entry_y"]=old_pos.y;you.props["holo_bot_entry_depth"]=old.depth;}
            ++transitions;max_depth=std::max(max_depth,you.depth);event("level",terrain_fingerprint());
            int trip=you.props.exists("holo_pilot_stairs")?you.props["holo_pilot_stairs"].get_int():0;
            if(trip==0 && you.depth==2)you.props["holo_pilot_stairs"]=1;
            else if(trip==1 && you.depth==1)you.props["holo_pilot_stairs"]=2;
            else if(trip==2 && you.depth==2){you.props["holo_pilot_stairs"]=3;event("stairs_roundtrip_complete");}
        }
        if(actions%100==0)event("progress");
        if(!resume && checkpoint_at>0 && actions>=checkpoint_at && !dead && !you_are_delayed()) {
            holo_dungeon_save_level();save_game(false);
            {std::ofstream core(dir+"/checkpoint-core.txt");core<<core_signature();}
            {std::ofstream core(dir+"/checkpoint-gameplay-core.txt");core<<core_signature(false);}
            {
                std::vector<mid_t> alive;
                for(auto c:holo_batch::s.companions){const auto m=monster_by_mid(c.mid);if(m && m->alive())alive.push_back(c.mid);}
                std::ofstream allies(dir+"/checkpoint-allies.txt");allies<<alive.size()<<'\n';
                for(auto mid:alive){const auto m=monster_by_mid(mid);allies<<mid<<' '<<m->hit_points<<' '<<m->pos().x<<' '<<m->pos().y<<'\n';}
            }
            std::ofstream state(dir+"/checkpoint.txt");
            state<<actions<<' '<<casts<<' '<<max_depth<<' '<<transitions<<' '<<rests<<' '<<failed<<' '<<last_ring<<' '<<you.hp<<' '<<int(you.piety)<<' '<<you.depth<<' '<<you.elapsed_time;
            event("checkpoint");report(dir,"checkpoint",seed,god,mode,target);close_save();running=false;return 0;
        }
    }
    if(dead)outcome="death";
    event("finish",outcome);report(dir,outcome,seed,god,mode,target);
    if(!dead){holo_dungeon_save_level();save_game(false);}
    close_save();running=false;return 0;
}
}
