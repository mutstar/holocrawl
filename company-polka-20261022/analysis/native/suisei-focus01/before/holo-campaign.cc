#include "AppHdr.h"
#include "holo-koyori.h"
#include "holo-lamy.h"
#include "holo-visual.h"
#include "holo-wrath.h"
#include "output.h"
#include "holo-campaign.h"
#include "holo-worship.h"
#include "holo-batch-internal.h"
#include "holo-sopia.h"
#include "holocrawl.h"
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include "act-iter.h"
#include "beam.h"
#include "artefact.h"
#include "god-item.h"
#include "items.h"
#include "item-use.h"
#include "makeitem.h"
#include "mapdef.h"
#include "random.h"
#include "directn.h"
#include "env.h"
#include "fight.h"
#include "food.h"
#include "item-prop.h"
#include "libutil.h"
#include "menu.h"
#include "message.h"
#include "mon-death.h"
#include "mon-util.h"
#include "player.h"
#include "prompt.h"
#include "skills.h"
#include "spl-util.h"
#include "state.h"
#include "store.h"
#include "stringutil.h"
#include "terrain.h"
#include "view.h"

namespace holo_campaign {
namespace {
const char *key="holocrawl_campaign";
int command_depth=0,invoking=0,stored_resource=0;
bool divine_damage=false,divine_direct=false,wide_wave=false,pending_friendly=false;
int bomb_depth=0,bomb_kills=0,reaction_depth=0;
CrawlHashTable &data() {
    if(!you.props.exists(key)) {
        auto &t=you.props[key].new_table();t["version"]=1;
        t["god"]=std::string();t["decay_next"]=you.elapsed_time+3000;
        t["noel_skill_end"]=0;t["noel_command_end"]=0;t["noel_ready"]=0;
        t["noel_skill_inv"]=0;t["noel_command_inv"]=0;
        t["debt"]=0;t["debt_next"]=0;t["debt_ticks"]=0;t["debt_paid"]=0;
        t["batch"]=std::string();t["sopia"]=std::string();t["catalyst"]=1;
    }
    return you.props[key].get_table();
}
int value(const char *field) {
    if(!you.props.exists(key))return 0;
    const auto &t=you.props[key].get_table();return t.exists(field)?t.at(field).get_int():0;
}
bool noel() { return active() && holo_worship::current()=="noel"; }
CrawlHashTable &supplies() {
    if(!you.props.exists("holo_noel_supplies")) {
        auto &t=you.props["holo_noel_supplies"].new_table();
        t["half_points"]=0;t["gifts"]=0;t["last_gift"]=-1000;
    }
    return you.props["holo_noel_supplies"].get_table();
}
void deliver_supplies() {
    if(!noel() || you.piety<75)return;
    auto &t=supplies();
    const int threshold=2*std::min(200,100+25*t["gifts"].get_int());
    if(t["half_points"].get_int()<threshold || you.elapsed_time-t["last_gift"].get_int()<1000)return;
    coord_def drop=you.pos();
    if(feat_destroys_items(grd(drop))) {
        bool found=false;
        for(int dx=-1;dx<=1 && !found;++dx)for(int dy=-1;dy<=1 && !found;++dy) {
            const auto p=you.pos()+coord_def(dx,dy);
            if(in_bounds(p) && grd(p)==DNGN_FLOOR && !actor_at(p) && holo_batch::seen(p)){drop=p;found=true;}
        }
        if(!found)return;
    }
    std::vector<int> weapons,armour,shields;
    int best=0;
    for(int kind=0;kind<NUM_WEAPONS;++kind) {
        item_def candidate;candidate.base_type=OBJ_WEAPONS;candidate.sub_type=kind;candidate.quantity=1;
        if(!weapon_rarity(kind) || is_range_weapon(candidate) || !you.could_wield(candidate,true,true))continue;
        const int training=you.skill(item_attack_skill(candidate),1,true);
        if(training>best){best=training;weapons.clear();}
        if(training==best)weapons.push_back(kind);
    }
    if(you.skill(SK_UNARMED_COMBAT,1,true)>=best)weapons.clear();
    for(int kind:{ARM_ROBE,ARM_LEATHER_ARMOUR,ARM_RING_MAIL,ARM_SCALE_MAIL,ARM_CHAIN_MAIL,ARM_PLATE_ARMOUR,ARM_HELMET,ARM_HAT,ARM_CLOAK,ARM_GLOVES,ARM_BOOTS,ARM_BUCKLER,ARM_SHIELD,ARM_LARGE_SHIELD}) {
        item_def candidate;candidate.base_type=OBJ_ARMOUR;candidate.sub_type=kind;candidate.quantity=1;
        if(!can_wear_armour(candidate,false,true))continue;
        if(is_shield(candidate))shields.push_back(kind);else armour.push_back(kind);
    }
    if(you.weapon() && you.hands_reqd(*you.weapon(),true)==HANDS_TWO && !you.skill(SK_SHIELDS,1,true))shields.clear();
    const int roll=random2(100);
    const bool weapon=roll<40 && !weapons.empty();
    auto &types=weapon?weapons:roll>=80 && !shields.empty()?shields:armour;
    if(types.empty())return;
    const int slot=items(false,weapon?OBJ_WEAPONS:OBJ_ARMOUR,types[random2(types.size())],ISPEC_GOOD_ITEM);
    if(slot==NON_ITEM)return;
    item_def &item=mitm[slot];
    if(x_chance_in_y(15,100)) {
        if(!make_item_randart(item)){destroy_item(slot,true);return;}
    }
    if(god_hates_item(item)){destroy_item(slot,true);return;}
    item.plus=std::max(int(item.plus),weapon?2:armour_is_enchantable(item)?1:0);
    do_uncurse_item(item,false);
    int placed=slot;
    if(!move_item_to_grid(&placed,drop,true) || placed==NON_ITEM){if(mitm[slot].defined())destroy_item(slot,true);return;}
    mitm[placed].props["holo_gift"]=std::string("noel");
    t["half_points"]=t["half_points"].get_int()-threshold;t["gifts"]=t["gifts"].get_int()+1;t["last_gift"]=you.elapsed_time;
    holo_visual::invocation("noel",3,drop);
    mprf(MSGCH_GOD,"Noel sends equipment from the knightly order.");
}

bool skill_up() { return noel() && value("noel_skill_end")>you.elapsed_time; }
void refresh() {
    if(!active())return;
    holo_batch::s.inv=you.skill(SK_INVOCATIONS,1);
    holo_koyori::initialise();
    // Preserve legacy saves: only presentation names change, not companion IDs/state.
    for(monster_iterator mi;mi;++mi){
        if(mi->mname=="Holo raven")mi->mname="Holo hawk";
        else if(mi->mname=="wrath crow" && mi->props.exists("holo_wrath_god")
            && mi->props["holo_wrath_god"].get_string()=="lui")mi->mname="wrath hawk";
    }

    // The first unlock grants Okayu's initial fullness once per character.
    if(holo_worship::current()=="okayu" && you.piety>=30) {
        if(!you.props.exists("holo_initial_resources"))you.props["holo_initial_resources"].new_table();
        auto &t=you.props["holo_initial_resources"].get_table();
        if(!t.exists("okayu")){t["okayu"]=true;holo_batch::s.resource=30;holo_batch::s.shield=5+holo_batch::s.inv/3;}
    }
}
bool pay(int mp,int piety,int threshold) {
    if(!active() || you.piety<threshold || you.piety<piety || you.magic_points<mp)return false;
    you.magic_points-=mp;you.piety-=piety;you.redraw_magic_points=true;you.redraw_title=true;return true;
}
void transfer_debt() {
    auto &s=holo_batch::s;
    if(s.deferred<=0)return;
    auto &t=data();t["debt"]=value("debt")+s.deferred;
    t["debt_next"]=std::max(value("debt_next"),std::max(you.elapsed_time+1,s.debt_next));
    t["debt_ticks"]=std::max(1,s.debt_ticks);s.deferred=0;s.debt_ticks=0;
}
bool target_ok(monster *m,int range) {
    return m && m->alive() && m->attitude==ATT_HOSTILE && you.can_see(*m)
        && grid_distance(you.pos(),m->pos())<=range && holo_batch::seen(m->pos());
}
struct choice { std::string name;int tier,option,target,range; };
std::vector<choice> choices(const std::string &g=holo_worship::current()) {
    // target: 0 self, 1 enemy, 2 floor/direction, 3 friendly companion.
    if(g=="noel")return {{"Knight's skill (MP2, piety2)",1,0,0,0},{"Silver commander (MP5, piety10)",5,0,0,0}};
    if(g=="suisei")return {{"Select constellation target",1,0,1,6},{"Orbital cut (MP3, piety3)",3,0,2,5},{"Comet (MP6, piety10)",5,0,2,6}};
    if(g=="miko")return {{"Place sanctuary (MP3)",1,0,0,0},{"Sacred boundary (MP3, piety3)",3,0,0,0},{"Great sanctuary (MP6, piety10)",5,0,0,0}};
    if(g=="aki")return {{"Place garden (MP3)",1,0,2,4},{"Place two roses (MP4, piety3)",3,0,2,6},{"Full bloom (MP6, piety12)",5,0,0,0}};
    if(g=="fubuki")return {{"Place fox image (MP3, piety1)",1,0,2,4},{"Swap with image (MP3, piety3)",3,0,3,5},{"Fox gathering (MP6, piety12)",5,0,0,0}};
    if(g=="ayame")return {{"Twin strike (MP3, piety3)",3,0,1,1},{"Duel (MP5, piety10)",5,0,1,1}};
    if(g=="choco")return {{"Temptation (MP2)",1,0,1,5},{"Kiss (MP3, piety3)",3,0,1,1},{"Charm (MP6, piety12)",5,0,1,5}};
    if(g=="korone")return {{"Pursuing punch (MP2, piety2)",3,0,1,1},{"Endurance (MP5, piety12)",5,0,0,0}};
    if(g=="okayu")return {{"Eat food",1,0,0,0},{"Nap mark (MP3, piety2)",3,0,1,5},{"Dream eater (MP5, piety8)",5,0,1,3}};
    if(g=="pekora")return {{"Plant carrot (MP2, piety1)",1,0,2,you.piety>=75?5:3},{"Detonate carrot (MP2, piety2)",3,0,2,7},{"Delayed fuse (MP2, piety2)",3,1,2,7},{"Pekoland: select three strikes (MP7, piety14)",5,0,2,5},{"Dismantle carrot",-1,0,2,7}};
    if(g=="watame")return {{"Wool barrier (MP3, piety3)",3,0,0,0},{"Won't die (MP6, piety15)",5,0,0,0}};
    if(g=="towa")return {{"Covering fire zone (MP4, piety4)",3,0,2,5},{"Crossfire (MP6, piety12)",5,0,0,0}};
    if(g=="lamy")return {{"Drink (MP2, piety1)",1,0,0,0},{"Snow banquet (MP6, piety12, intox40)",5,0,0,0}};
    if(g=="polka")return {{"Performance: strong target (MP1)",1,1,1,6},{"Performance: tightrope (MP1)",1,2,1,6},{"Performance: juggling (MP1)",1,3,1,6},{"Acrobatics (MP3, piety2)",3,0,1,1},{"Acrobatics + 1 applause (MP3, piety2)",3,1,1,1},{"Firework finale (MP6, piety10)",5,0,2,5},{"Curtain call (MP6, piety10)",5,1,0,0},{"Confusion finale (MP6, piety10)",5,2,0,0},{"Abandon performance",-1,0,0,0}};
    if(g=="koyori")return {{"Critical experiment (MP6, piety10)",5,0,0,0}};
    if(g=="lui")return {{"Summon hawk (MP3)",1,0,0,0},{"Hunting command (MP3, piety3)",3,0,1,5},{"Hawk host (MP7, piety14)",5,0,0,0}};
    if(g=="raden")return {{"Exhibit painting (MP1)",1,0,0,0},{"Exhibit sculpture (MP1)",1,1,0,0},{"Exhibit craft (MP1)",1,2,0,0},{"Painting burst (MP3, piety3)",3,0,1,5},{"Sculpture wave (MP3, piety3)",3,1,2,3},{"Craft shield (MP3, piety3)",3,2,0,0},{"Special exhibition (MP6, piety12)",5,0,0,0}};
    if(g=="hajime")return {{"Dive in (MP3, piety3)",3,0,1,3},{"Bancho time (MP6, piety12)",5,0,0,0}};
    if(g=="su")return {{"Wave (MP3, piety3)",3,0,2,5},{"High tide (MP6, piety12)",5,0,0,0}};
    if(g=="vivi")return {{"Makeup (MP2)",1,0,0,0},{"Dazzling entrance (MP3, piety4)",3,0,0,0},{"Runway (MP6, piety12)",5,0,0,0}};
    if(g=="sopia")return {{"Orbit ring (MP3)",1,0,0,0},{"Gravity field (MP3, piety3)",3,0,2,4},{"Big Bang (MP7, piety14)",5,0,2,4},{"Detonate Big Bang",6,0,0,0},{"Dismiss ring",-1,1,0,0},{"Dismiss field",-1,2,0,0}};
    if(g=="mela")return {{"Toggle ember counter",-1,0,0,0},{"Reverse jet (MP3, piety3)",3,0,2,holo_batch::five()?4:3},{"Fire brigade (MP6, piety12)",5,0,0,0}};
    return {};
}
bool pick(coord_def &pos,int range,const char *prompt) {
    dist target;direction_chooser_args args;args.restricts=DIR_TARGET;args.mode=TARG_ANY;
    args.range=range;args.needs_path=true;args.top_prompt=prompt;
    direction(target,args);
    if(!target.isValid || target.isCancel)return false;
    pos=target.target;return in_bounds(pos) && holo_batch::seen(pos) && grid_distance(you.pos(),pos)<=range;
}
}
bool active() { return !holo_benchmark_active() && holo_worship::active(); }
bool combat_active() {
    if(!active())return false;
    if(you.piety>=30)return true;
    const auto &s=holo_batch::s;const auto g=holo_worship::current();int now=you.elapsed_time;
    if(s.five_end>now || s.three_end>now)return true;
    if(g=="choco" && s.secondary<0)return true;
    if((g=="lamy" || g=="korone" || g=="mela" || g=="okayu") && s.resource>0)return true;
    for(auto h:s.hazards)if(h.arm>0 || h.end>now)return true;
    if(g=="miko" || g=="aki" || g=="choco" || g=="towa" || g=="vivi" || g=="okayu" || g=="koyori")return s.one_end>now;
    if(g=="fubuki" || g=="lui" || g=="aki")for(auto c:s.companions){auto *m=monster_by_mid(c.mid);if(m && m->alive())return true;}
    return false;
}
void joined() {
    if(holo_benchmark_active())return;
    auto &t=data();t["god"]=holo_worship::current();t["decay_next"]=you.elapsed_time+3000;
    t["noel_skill_end"]=0;t["noel_command_end"]=0;t["noel_ready"]=0;
    const auto g=holo_worship::current();
    holo_batch::reset(g=="noel" || g=="sopia"?"":g,you.skill(SK_INVOCATIONS,1));
    if(g=="okayu"){holo_batch::s.resource=0;holo_batch::s.shield=0;}
    if(g=="mela")holo_batch::s.offence=1;
    t["catalyst"]=1;
    if(t.exists("cooldowns") && t["cooldowns"].get_table().exists(g)) {
        const auto &c=t["cooldowns"].get_table().at(g).get_table();
        holo_batch::s.one_ready=c.at("one").get_int();holo_batch::s.three_ready=c.at("three").get_int();holo_batch::s.five_ready=c.at("five").get_int();
        for(int n=0;n<3;++n)holo_batch::s.rest[n]=c.at(std::to_string(n)).get_int();
        if(g=="noel")t["noel_ready"]=c.at("noel").get_int();
    }
    holo_batch::set_policy(false,"melee");holo_batch::configure_balance(1,1);
    holo_sopia::reset(g=="sopia",you.skill(SK_INVOCATIONS,1));
    if(g=="sopia")holo_sopia::restore_cooldown(holo_batch::s.five_ready);
    refresh();save();
}
void leaving_god() {
    if(holo_benchmark_active())return;
    transfer_debt();
    if(holo_worship::current()=="sopia")holo_sopia::leave_level();
    auto &ledger=data();if(!ledger.exists("cooldowns"))ledger["cooldowns"].new_table();
    auto &cooldown=ledger["cooldowns"].get_table()[holo_worship::current()].new_table();
    cooldown["one"]=holo_batch::s.one_ready;cooldown["three"]=holo_batch::s.three_ready;cooldown["five"]=holo_batch::s.five_ready;
    if(holo_worship::current()=="sopia")cooldown["five"]=holo_sopia::cooldown();
    cooldown["noel"]=value("noel_ready");for(int n=0;n<3;++n)cooldown[std::to_string(n)]=holo_batch::s.rest[n];
    if(ledger.exists("pulled"))ledger["pulled"].get_table().clear();
    if(holo_batch::s.secondary<0 && holo_worship::current()=="choco") {
        monster *m=monster_by_mid(holo_batch::s.marked);if(m){m->attitude=ATT_HOSTILE;m->foe=MHITYOU;m->props.erase("holo_charmed");}
    }
    for(auto c:holo_batch::s.companions){monster *m=monster_by_mid(c.mid);if(m && m->alive())monster_die(*m,KILL_DISMISSED,NON_MONSTER,true);}
    holo_batch::reset();holo_sopia::reset(false,0);
    auto &t=data();t["god"]=std::string();t["noel_skill_end"]=0;t["noel_command_end"]=0;t["batch"]=std::string();t["sopia"]=std::string();
}
void save() {
    if(holo_benchmark_active() || (!active() && !you.props.exists(key)))return;
    auto &t=data();
    if(active()){t["god"]=holo_worship::current();t["batch"]=holo_batch::save_campaign();t["sopia"]=holo_sopia::save_campaign();}
}
void load() {
    if(holo_benchmark_active())return;
    holo_batch::reset();holo_sopia::reset(false,0);
    if(!you.props.exists(key)){if(active())joined();return;}
    auto &t=data();
    if(t["version"].get_int()!=1)throw std::runtime_error("Unsupported Holo campaign save");
    if(active()) {
        if(t["god"].get_string()!=holo_worship::current())throw std::runtime_error("Campaign god/save mismatch");
        holo_batch::load_campaign(t["batch"].get_string());holo_sopia::load_campaign(t["sopia"].get_string());
        const auto names=holo_batch::implemented();
        const int id=int(holo_batch::s.god);
        const auto god=holo_worship::current();
        if((id==0 && god!="noel" && god!="sopia") || (id>0 && names.at(id-1)!=god))
            throw std::runtime_error("Combat core/save god mismatch");
    }
}
void penalty(int amount) {
    if(!active() || amount<=0)return;
    you.piety=std::max(0,int(you.piety)-amount);you.redraw_title=true;
    mprf(MSGCH_GOD,"%s disapproves (-%d piety).",holo_worship::display_name().c_str(),amount);
}
void voluntary_berserk() {
    if(!noel())return;
    auto &t=data();
    if(value("noel_command_end")>you.elapsed_time)t["noel_ready"]=you.elapsed_time+100;
    t["noel_skill_end"]=0;t["noel_command_end"]=0;penalty(10);
    you.redraw_armour_class=true;
}
void voluntary_hp_cost() {if(active() && holo_worship::current()=="watame")penalty(5);}
void grant(int amount) {
    if(!active() || amount<=0)return;
    const int before=you.piety;you.piety=std::min(200,before+amount);you.redraw_title=true;
    for(int threshold:{30,75,120})if(before<threshold && you.piety>=threshold)mprf(MSGCH_GOD,"%s grants a new tier of abilities.",holo_worship::display_name().c_str());
    refresh();
}
void advance() {
    if(holo_benchmark_active())return;
    if(!active() && !you.props.exists(key))return;
    auto &t=data();const int now=you.elapsed_time;
    if(active()) {
        refresh();deliver_supplies();if(holo_worship::current()=="lamy")you.redraw_status_lights=true;int next=value("decay_next");if(next<=0)next=now+3000;
        if(now>=next){const int n=(now-next)/3000+1;you.piety=std::max(0,int(you.piety)-n);t["decay_next"]=next+3000*n;you.redraw_title=true;}
        if(!combat_active())transfer_debt();
        for(monster_iterator mi;mi;++mi)if(holo_batch::eligible(**mi))holo_batch::s.eligible_sources.insert(mi->mid);
    }
    while(value("debt")>0 && value("debt_ticks")>0 && now>=value("debt_next") && you.hp>0){
        const int paid=(value("debt")+value("debt_ticks")-1)/value("debt_ticks");t["debt"]=value("debt")-paid;t["debt_ticks"]=value("debt_ticks")-1;t["debt_next"]=value("debt_next")+10;t["debt_paid"]=value("debt_paid")+paid;
        bool old=holo_batch::internal_damage;holo_batch::internal_damage=true;ouch(paid,KILLED_BY_WILD_MAGIC,you.mid,"deferred endurance damage");holo_batch::internal_damage=old;
    }
}
bool noel_commander(){return noel() && value("noel_command_end")>you.elapsed_time;}
int noel_armour(){return noel_commander()?4+value("noel_command_inv")/6:0;}
int noel_shield(){return noel_commander() && you.shield()?3+value("noel_command_inv")/9:0;}
int noel_skill_bonus(skill_type skill,int scale){
    if(!skill_up())return 0;
    // Fighting uses its attack-only hook below, preserving maximum HP.
    return skill>SK_FIGHTING && skill<=SK_LAST_MUNDANE?6*scale:0;
}
int noel_fighting_bonus(int scale){return skill_up()?6*scale:0;}
int invoke(int tier,monster *target,const coord_def *aim,int option,int amount) {
    if(!active() || you.cannot_act())return 0;
    const auto g=holo_worship::current();const int need=tier==5?120:tier==3?75:tier==6?0:tier<0?0:30;
    if(you.piety<need)return 0;
    // Most invocations require speech/control; the documented defensive
    // confusion exceptions remain usable without giving all powers that exception.
    if(you.berserk() || (you.confused() && !(g=="miko" && tier==5) && !(g=="polka" && tier==5 && option==1) && !(g=="vivi" && tier==3)))return 0;
    bool legal=false;
    for(const auto &c:choices())if(c.tier==tier && c.option==option) {
        legal=true;
        if(c.target==1 && !target_ok(target,c.range))return 0;
        if(c.target==2 && (!aim || !in_bounds(*aim) || !holo_batch::seen(*aim) || grid_distance(you.pos(),*aim)>c.range))return 0;
        if(c.target==3 && (!target || !target->alive() || target->attitude!=ATT_FRIENDLY || !you.can_see(*target) || grid_distance(you.pos(),target->pos())>c.range))return 0;
        break;
    }
    if(!legal)return 0;
    refresh();invoking=tier;wide_wave=false;stored_resource=holo_batch::s.resource;
    struct done {~done(){invoking=0;}} guard;
    int aut=0;const int now=you.elapsed_time,I=you.skill(SK_INVOCATIONS,1);
    if(g=="noel") {
        auto &t=data();
        if(tier==1 && value("noel_skill_end")<=now && pay(2,2,30)){t["noel_skill_end"]=now+10*min(110,15+random2avg(I*6,2));t["noel_skill_inv"]=I;aut=10;}
        if(tier==5 && value("noel_command_end")<=now && value("noel_ready")<=now && pay(5,10,120)){t["noel_command_end"]=now+5+60+2*I;t["noel_ready"]=now+5+60+2*I+100;t["noel_command_inv"]=I;aut=5;}
    } else if(g=="sopia")aut=holo_sopia::manual_action(tier,aim?*aim:you.pos(),option);
    else aut=holo_batch::manual_action(tier,target,aim?*aim:you.pos(),option,amount);
    if(aut>0)holo_visual::invocation(g,tier,aim?*aim:target?target->pos():you.pos(),option);
    if(aut>0){if(!(g=="okayu" && tier==1))exercise(SK_INVOCATIONS,1);you.time_taken=aut;you.turn_is_over=true;you.redraw_magic_points=true;you.redraw_armour_class=true;you.redraw_evasion=true;you.redraw_title=true;}
    return aut;
}
namespace {
std::string turns(int until) {return make_stringf("%.1f turns",std::max(0,until-you.elapsed_time)/10.0);}
int cooldown(const choice &c) {
    const auto g=holo_worship::current();const auto &s=holo_batch::s;
    if(g=="noel")return c.tier==5?value("noel_ready"):0;
    if(g=="sopia")return c.tier==5?holo_sopia::cooldown():0;
    if(g=="raden" && c.tier==3)return s.rest[c.option];
    if(c.tier==5)return s.five_ready;
    if(c.tier==3 && (g=="ayame" || g=="korone" || g=="watame" || g=="hajime" || g=="vivi"))return s.three_ready;
    if(c.tier==1 && (g=="polka" || g=="okayu"))return s.one_ready;
    return 0;
}
int mp_cost(const choice &c) {
    const auto pos=c.name.find("MP");return pos==std::string::npos?0:atoi(c.name.c_str()+pos+2);
}
std::string reason(const choice &c) {
    const int need=c.tier==5?120:c.tier==3?75:c.tier==1?30:0;
    const auto g=holo_worship::current();const auto &s=holo_batch::s;int now=you.elapsed_time;
    if(you.cannot_act())return "cannot act";
    if(you.berserk())return "berserk";
    if(you.confused() && !(g=="miko" && c.tier==5) && !(g=="polka" && c.tier==5 && c.option==1) && !(g=="vivi" && c.tier==3))return "confused";
    if(you.piety<need)return make_stringf("need %d piety (+%d)",need,need-you.piety);
    if(you.magic_points<mp_cost(c))return make_stringf("need %d MP",mp_cost(c));
    if(cooldown(c)>now)return "cooldown "+turns(cooldown(c));
    if(g=="noel" && ((c.tier==1 && value("noel_skill_end")>now) || (c.tier==5 && value("noel_command_end")>now)))return "already active";
    if(g=="raden" && c.tier==1 && c.option==s.exhibit)return "already exhibited";
    if(g=="raden" && c.tier==1 && holo_batch::five())return "exhibition active";
    if(g=="raden" && c.tier==3 && !holo_batch::five() && c.option!=s.exhibit)return "requires matching exhibit";
    if(g=="koyori" && c.tier==1 && c.option>=11 && s.stock[c.option%10-1]<=0)return "no reagent stock";
    if(g=="koyori" && holo_batch::five())return "critical experiment active";
    if(g=="lamy" && holo_batch::five())return "banquet active";
    if(g=="lamy" && c.tier==1 && s.resource>=100)return "intoxication is full";
    if(g=="lamy" && c.tier==5 && s.resource<40)return "need 40 intoxication";
    if(g=="okayu" && c.tier==1 && s.resource>=100)return "fullness is full";
    return "";
}
}
std::string unavailable(int tier,int option) {
    for(const auto &c:choices())if(c.tier==tier && c.option==option)return reason(c);
    return "unknown ability";
}
std::vector<std::string> status_lines() {
    std::vector<std::string> lines;if(!active())return lines;
    const auto &s=holo_batch::s;const auto g=holo_worship::current();
    const int rank=holo_worship::rank();
    lines.push_back(make_stringf("[%s%s] Piety %d/200 | MP %d | unlocks 30 / 75 / 120",std::string(rank,'*').c_str(),std::string(5-rank,'.').c_str(),int(you.piety),int(you.magic_points)));
    const char *resource=g=="suisei"?"Stars":g=="ayame"?"Combo":g=="choco"?"Temptation":g=="korone"?"Momentum":g=="okayu"?"Fullness":g=="lamy"?"Intoxication":g=="polka"?"Applause":g=="hajime"?"Rhythm":g=="su"?"Water":g=="vivi"?"Spotlight":g=="mela"?"Heat":g=="koyori"?"Cycle":"Resource";
    lines.push_back(make_stringf("%s %d | Shield %d | 1*/3*/5* duration %s / %s / %s",resource,s.resource,s.shield,turns(g=="noel"?value("noel_skill_end"):s.one_end).c_str(),turns(s.three_end).c_str(),turns(g=="noel"?value("noel_command_end"):s.five_end).c_str()));
    if(g=="suisei")lines.push_back(make_stringf("Constellation stars: %d/3 | next-hit reward: %d (%s)",s.resource,s.three_end>you.elapsed_time?s.offence:0,turns(s.three_end).c_str()));
    lines.push_back("Corner marks: upper-left power; lower-left protection; upper-right wrath; lower-right recovery/resource.");
    if(g=="sopia")lines.push_back(holo_sopia::status());
    if(g=="koyori")lines.push_back(holo_koyori::status());
    if(g=="raden")lines.push_back(make_stringf("Exhibit: %s | recovery: %s / %s / %s",s.exhibit==0?"painting":s.exhibit==1?"sculpture":"craft",turns(s.rest[0]).c_str(),turns(s.rest[1]).c_str(),turns(s.rest[2]).c_str()));
    if(g=="noel" && you.props.exists("holo_noel_supplies")){const auto &t=you.props["holo_noel_supplies"].get_table();lines.push_back(make_stringf("Knightly supplies: %.1f / %d points",t.at("half_points").get_int()/2.0,std::min(200,100+25*t.at("gifts").get_int())));}
    const auto wrath=holo_wrath::status();if(!wrath.empty())lines.push_back("Wrath: "+wrath);
    std::vector<std::string> wrapped;
    for(auto line:lines){while(line.size()>72){auto split=line.rfind(' ',72);if(split==std::string::npos)split=72;wrapped.push_back(line.substr(0,split));line.erase(0,split+(line[split]==' '));}wrapped.push_back(line);}
    return wrapped;
}
std::vector<std::string> god_info(const std::string &g) {
    const std::vector<std::string> concepts={
        "Mark a constellation target, build stars through attacks, then strike with orbit and comet.",
        "Fight inside a placed sanctuary; strengthen its boundary and expand it at five stars.",
        "Build a garden, grow roses and entangle enemies; full bloom strengthens the garden.",
        "Fox images distract enemies. Place images, swap positions, then gather the foxes.",
        "Build a melee combo against one opponent; twin strikes and duels reward sustained contact.",
        "Build temptation, weaken enemies with a kiss, then temporarily charm a target.",
        "Build momentum through melee pressure. Pursue enemies and defer damage during endurance.",
        "Food supplies fullness and shielding. Mark prey for a nap, then consume their dreams.",
        "Plant carrots, arm and detonate them. Explosions can hit you and your allies.",
        "A knight's skill temporarily raises fighting and equipment skills. Earn equipment supplies.",
        "Wool protects you; a barrier and five-star survival power help withstand direct attacks.",
        "Ranged attacks build pressure. Establish a covering-fire zone and activate crossfire.",
        "Drink for attack-spell power. Damaging spells/tools and first cloud damage per use build chill; Snow banquet adds frost bursts. Overdrinking reduces EV by3.",
        "Complete performances to earn applause; spend it on acrobatics and selectable finales.",
        "Attack spells cycle heat, cold and poison reagents. Learn longer-range catalyst reactions; Critical experiment injects paired reagents.",
        "Summon hawks, mark a hunting target and call a hawk host; bird kills support worship.",
        "Choose painting, sculpture or craft. Each exhibit has a matching active power and recovery.",
        "Build rhythm through movement and melee. Dive in; five stars damage adjacent foes on movement.",
        "Turn floor into shallow water and release waves. Worship grants immunity to shallow-water movement delay and melee fumbling, including natural pools. Deep water is unchanged. High tide empowers the water-based combat cycle.",
        "Build a dazzling spotlight through combat. Makeup, entrance and runway reward flashy pressure.",
        "An orbit ring continuously hits nearby foes. Gravity also deals damage; charge and detonate Big Bang.",
        "Build heat and ember counters. Reverse jet and fire brigade combine fire with physical pressure."};
    const auto ids=holo_worship::gods();const auto it=std::find(ids.begin(),ids.end(),g);
    if(it==ids.end())return {};
    const std::vector<std::string> income={
        "Bonus piety: +1 for a strong non-pet kill; +1 for an ordinary kill with at least 3 stars.",
        "Bonus piety: +1 for a direct kill when both you and the target are inside the sanctuary.",
        "Bonus piety: +1 for a direct kill on an enemy with 3 entanglement stacks.",
        "Bonus piety: +1 for a direct kill on an enemy that attacked a fox image within 3 turns.",
        "Bonus piety: +1 for an ordinary melee kill of your combo target; another +1 if strong during Duel.",
        "Bonus piety: +1 for a direct Kiss kill or a direct kill at 5+ temptation; +1 when a strong charm target survives to its end.",
        "Bonus piety: +1 for an ordinary melee kill at 4+ momentum; another +1 for a strong kill during Endurance.",
        "Bonus piety: +2 for each first food subtype eaten; Dream eater direct kills also grant +1.",
        "Bonus piety: +1 for killing 2-3 enemies in one bomb activation, +2 for 4 or more.",
        "Bonus piety: +1 for a strong non-pet kill. At 3*, kills also accumulate knightly equipment supplies.",
        "Bonus piety: +1 for a strong non-pet kill. Voluntarily spending HP costs 5 piety.",
        "Bonus piety: +1 for an ordinary ranged kill from more than 1 tile away.",
        "Bonus piety: +1 for a direct kill at intoxication 20-69, or during Banquet.",
        "Bonus piety: +1 for a successfully completed performance; finale costs and applause are separate.",
        "Bonus piety: +3 for each first reaction discovered; +1 for a strong direct reaction kill.",
        "Bonus piety: +1 for a strong enemy killed by one of your hawks.",
        "Bonus piety: +1 for a strong kill, including a qualifying companion kill.",
        "Bonus piety: +1 for a strong ordinary melee kill at 2+ rhythm, or a direct Dive kill starting at 2+ rhythm.",
        "Bonus piety: +1 for a strong direct Wave kill when the wave is wide or High tide is active.",
        "Bonus piety: +1 for a strong direct kill during Makeup or Runway.",
        "Bonus piety: +1 for a strong direct kill of an enemy pulled by gravity on this floor.",
        "Bonus piety: +1 for a strong direct Reverse jet kill starting at 3+ heat."};
    std::vector<std::string> lines={concepts[it-ids.begin()],
        "Unlocks: 1* at 30 piety; 3* at 75; 5* at 120. Maximum piety: 200.",
        "First worship starts at 15 piety; returning starts at 0. Natural kills: +1, with god-specific bonuses.",
        "Summoned/no-reward monsters give no kill piety. Piety decays by 1 every 300 normal turns.",
        "Deliberately attack an ally: -10 piety. Abandonment leaves saved, combat-only wrath.",
        "Wrath: one effect at a time, at least 10 turns apart. Area strikes warn for 2 turns.",
        "New abandonment: 18 + piety/25 events (18-26), or XP equal to two XL advances (minimum 200). Current XL sets each new event. Rejoining never erases debt.",
        "Listed costs are charged only on a successful invocation; cancellation costs no turn."};
    lines.push_back(income[it-ids.begin()]);
    lines.push_back("Strong means monster HD >= your XL. Direct excludes pet kills; ordinary means your normal attack.");
    if(g=="koyori")lines.push_back("1*: passive direct attack spells cycle Heat/Cold/Poison; no extra MP/piety. Heat1d(4+Inv/6), Cold1d(3+Inv/9) and move+15%/2t, Poison(2+Inv/12)x2 ticks. Marks6t. 3*: eligible ranged attack spells +1 range, LOS cap, no blast-radius change. Different reagents react once/cast: fire2d(5+Inv/4) radius1, thermal3d(6+Inv/4) half AC, slime2d(3+Inv/6) radius1 and move+35%/3t. All reaction damage x0.85 rounded down once. No self/ally splash. 5*: MP6/piety10,0.5t;8t or4 successful attack casts;20t cooldown from activation. Pairs thermal/fire/slime/thermal; reaction x1.5 for thermal(ignore AC), x1.35 otherwise; slime move+50%/4t. No tools/clouds/pets/poison followup/recursion. One reagent application per target and one reaction centre per cast. Existing marks and sequence saved.");
    if(g=="lamy")lines.push_back("1*: MP2/piety1, +40 intoxication, decay1/turn; >=20 attack spell power +(12+Inv/3)%, capped normally. >=70 EV-3; no failure penalty. 3*: passive, damaging spells and tools: one chill/target/use. A cloud field plus all spread cells share that use; first positive damage only, no direct+cloud double stack, expires6turns; third stack:2d(3+Inv/6) cold and movement +50% for2turns. 5*: requires40, consumes all; MP6/piety12,1turn; aftercast6+Inv/6 turns, treats intoxication as20. One burst/use and per10aut (a cloud field can burst once total):2d(5+Inv/3) cold at first hit, half adjacent, once-per-target chill. Cooldown15turns after end. No recursive/pet/divine/poison-DoT procs. Tool charges and costs remain normal; cloud ticks do not repeatedly stack. Old untagged clouds are excluded.");
    if(g=="suisei")lines.push_back("1* passive: one star per positive direct attack, max3, expires10 turns since last hit. A marked kill grants next-hit1d(3+4*stars) for3 turns, AC applies. Manual retarget costs1 turn. 3* active: MP3/piety3/1turn, range5 piercing,2d(8+Inv/2)+5 per marked star; consumes stars only on hit. 5* active: MP6/piety10/1turn, range6 fixed3x3, lands2turns after completion;3d(10+Inv/2)+8 per snapshotted marked star, AC applies. No tracking. Allies/self may be hit.");
    if(g=="okayu")lines.push_back("3*: A foe put to sleep by Nap takes +30% on the first positive ordinary direct hit (minimum +1, cap 8 + Invocations/3). Melee, ranged and attack spells qualify. Pets, poison, clouds and divine powers do not. Dream eater keeps its own sleep bonus without stacking this one.");
    if(g=="noel")lines.push_back("Taboo: voluntary berserk costs 10 piety and ends Knight's skill / Silver commander.");
    lines.push_back(holo_wrath::description(g));
    for(const auto &c:choices(g))lines.push_back(((c.tier==1 || c.tier==3 || c.tier==5)?make_stringf("%d*: ",c.tier):"Utility: ")+c.name);
    return lines;
}
bool ability_menu() {
    if(!active())return false;
    const auto list=choices();Menu menu(MF_SINGLESELECT);
    menu.set_title(new MenuEntry(holo_worship::display_name()+" - invocations",MEL_TITLE));
    for(const auto &line:status_lines())menu.add_entry(new MenuEntry(line,MEL_SUBTITLE));
    for(size_t i=0;i<list.size();++i){const auto &c=list[i];const auto why=reason(c);menu.add_entry(new MenuEntry(c.name+((c.tier==1 || c.tier==3 || c.tier==5)?make_stringf(" [%d*]",c.tier):"")+(why.empty()?"":" ["+why+"]"),MEL_ITEM,1,'a'+i));}
    menu.add_entry(new MenuEntry("God description and worship rules",MEL_ITEM,1,'?'));
    menu.add_entry(new MenuEntry("Racial, item and other abilities",MEL_ITEM,1,'z'));
    auto selected=menu.show();redraw_screen();if(selected.empty())return true;
    int index=selected[0]->hotkeys[0]-'a';if(selected[0]->hotkeys[0]=='z')return false;
    if(selected[0]->hotkeys[0]=='?'){holo_worship::show_info(holo_worship::current());return true;}
    if(index<0 || index>=int(list.size()))return true;
    const auto c=list[index];
    const auto why=reason(c);if(!why.empty()){mpr(why);return true;}
    const int required=c.tier==5?120:c.tier==3?75:c.tier==1?30:0;
    if(you.piety<required){mpr("Your piety is too low for that ability.");return true;}
    coord_def aim=you.pos();monster *target=nullptr;
    if(c.target && !pick(aim,c.range,"Choose an ability target (Esc cancels)."))return true;
    if(c.target==1){target=monster_at(aim);if(!target_ok(target,c.range)){mpr("Choose a visible enemy in range.");return true;}}
    if(c.target==3){target=monster_at(aim);if(!target || target->attitude!=ATT_FRIENDLY){mpr("Choose a friendly companion.");return true;}}
    const auto g=holo_worship::current();
    if(g=="aki" && c.tier==3 && !pick(holo_batch::manual_second,6,"Choose the second rose (Esc cancels)."))return true;
    holo_batch::manual_positions.clear();
    if(g=="hajime" && c.tier==3) {
        coord_def landing;
        if(!pick(landing,2,"Choose an empty landing cell adjacent to that enemy."))return true;
        holo_batch::manual_positions.push_back(landing);
    }
    if(g=="pekora" && c.tier==3) {
        holo_batch::manual_positions.push_back(aim);
        while(holo_batch::manual_positions.size()<5
              && yesno("Select another carrot for the same activation?",false,'n')) {
            coord_def p;
            if(!pick(p,7,"Choose another armed carrot (Esc cancels activation).")) {
                holo_batch::manual_positions.clear();return true;
            }
            if(std::find(holo_batch::manual_positions.begin(),holo_batch::manual_positions.end(),p)==holo_batch::manual_positions.end())
                holo_batch::manual_positions.push_back(p);
        }
    }
    if(g=="pekora" && c.tier==5)for(int i=0;i<3;++i){coord_def p;if(!pick(p,8,"Choose a strike inside the selected 7x7 zone.")){holo_batch::manual_positions.clear();return true;}holo_batch::manual_positions.push_back(p);}
    int amount=3;
    if(g=="polka" && c.tier==5){Menu ap(MF_SINGLESELECT);ap.set_title(new MenuEntry("Spend how much applause?",MEL_TITLE));for(int n=3;n<=6;++n)ap.add_entry(new MenuEntry(std::to_string(n),MEL_ITEM,1,'0'+n));auto s=ap.show();redraw_screen();if(s.empty())return true;amount=s[0]->hotkeys[0]-'0';}
    bool danger=false;
    if(g=="pekora" && c.tier>1)for(auto p:holo_batch::manual_positions) {
        if(grid_distance(you.pos(),p)<=1 && holo_batch::line(you.pos(),p))danger=true;
        for(monster_iterator mi;mi;++mi)
            if(mi->attitude==ATT_FRIENDLY && grid_distance(mi->pos(),p)<=1 && holo_batch::line(mi->pos(),p))danger=true;
    }
    if(g=="pekora" || (g=="polka" && c.tier==5 && c.option==0) || (g=="raden" && c.tier==3 && c.option==0) || (g=="koyori" && c.target)) {
        for(monster_iterator mi;mi;++mi)if(mi->attitude==ATT_FRIENDLY && grid_distance(mi->pos(),aim)<=2 && holo_batch::line(mi->pos(),aim))danger=true;
        if((g=="pekora" || g=="koyori" || g=="raden") && grid_distance(you.pos(),aim)<=2)danger=true;
    }
    if(danger && !yesno("You or your allies may be caught in the explosion. Continue?",false,'n'))return true;
    const int aut=invoke(c.tier,target,&aim,c.option,amount);
    if(!aut && !(c.tier<0 || (g=="koyori" && c.tier==3)))mpr("That ability is not available: check resources, cooldown and target conditions.");
    return true;
}
bool ordinary_damage(){return !divine_damage && !invoking;}
damage_scope::damage_scope(bool direct):old_damage(divine_damage),old_direct(divine_direct){divine_damage=true;divine_direct=direct;}
damage_scope::~damage_scope(){divine_damage=old_damage;divine_direct=old_direct;}
command_scope::command_scope(){++command_depth;}
command_scope::~command_scope(){if(!--command_depth)finish_attack();}
attack_scope::attack_scope(actor *source,actor *target,holo_batch::attack_kind kind,bool simulated){
    if(!simulated && active() && source && source->is_player() && target && target->is_monster() && !holo_batch::ctx.ordinary){holo_batch::begin_attack(*target->as_monster(),kind);owner=true;pending_friendly=target->as_monster()->attitude==ATT_FRIENDLY && !you.confused();}
}
attack_scope::~attack_scope(){if(owner)finish_attack();}
void beam_target(monster *target,bool spell){if(command_depth && active() && !invoking && !divine_damage && target && !holo_batch::ctx.ordinary){holo_batch::begin_attack(*target,spell?holo_batch::attack_kind::spell:holo_batch::attack_kind::ranged);pending_friendly=target->attitude==ATT_FRIENDLY && !you.confused();}}
void finish_attack(){if(!active() || !holo_batch::ctx.ordinary)return;if(you.turn_is_over && you.hp>0){if(pending_friendly)penalty(10);holo_batch::end_attack(you.time_taken);}else holo_batch::cancel_attack();pending_friendly=false;}
void kill(monster &m,killer_type killer,int killer_index,bool pet,bool valid){
    if(!active() || !valid || m.is_summoned() || testbits(m.flags,MF_NO_REWARD) || m.props.exists("holo_piety_paid") || !(YOU_KILL(killer)||pet))return;
    if(m.attitude!=ATT_HOSTILE && !m.props.exists("holo_charmed"))return;
    m.props["holo_piety_paid"]=true;
    using namespace holo_batch;const auto g=holo_worship::current();const int hd=m.get_experience_level();const bool strong=hd>=you.experience_level;
    const bool ordinary=!divine_damage && ctx.ordinary && ctx.target==m.mid;
    const bool direct=!pet && (divine_damage?divine_direct:ctx.ordinary);
    int extra=0;
    if((g=="noel" || g=="watame" || g=="suisei") && strong && !pet)++extra;
    if(g=="raden" && strong)++extra;
    if(g=="suisei" && ordinary && ctx.stars_before>=3)++extra;
    if(g=="fubuki" && direct && m.props.exists("holo_fox_attacked_until") && m.props["holo_fox_attacked_until"].get_int()>you.elapsed_time)++extra;
    if(g=="sopia" && direct && strong && data().exists("pulled") && data()["pulled"].get_table().exists(std::to_string(m.mid)))++extra;
    if(g=="koyori" && direct && strong && reaction_depth>0)++extra;
    if(g=="pekora" && bomb_depth>0)++bomb_kills;
    if(g=="miko" && direct && s.one_end>you.elapsed_time && grid_distance(s.centre,you.pos())<=(five()?3:you.piety>=75?2:1) && grid_distance(s.centre,m.pos())<=(five()?3:you.piety>=75?2:1))++extra;
    if(g=="aki" && direct && (s.targets[m.mid].stacks>=3 || m.props.exists("holo_bloom_three")))++extra;
    if(g=="ayame" && ordinary && ctx.kind==attack_kind::melee && s.marked==m.mid && s.one_end>you.elapsed_time){++extra;if(five()&&strong)++extra;}
    if(g=="choco" && direct && ((invoking==3) || s.resource>=5))++extra;
    if(g=="korone" && ordinary && ctx.kind==attack_kind::melee){if((invoking==3?stored_resource:s.resource)>=4)++extra;if(five()&&strong)++extra;}
    if(g=="okayu" && direct && invoking==5)++extra;
    if(g=="towa" && ordinary && ctx.kind==attack_kind::ranged && grid_distance(you.pos(),m.pos())>1)++extra;
    if(g=="lamy" && direct && ((s.resource>=20&&s.resource<=69)||five()))++extra;
    if(g=="lui" && pet && strong && !invalid_monster_index(killer_index)){for(auto c:s.companions)if(c.mid==menv[killer_index].mid && c.kind==3){++extra;break;}}
    if(g=="hajime" && strong && ((ordinary && ctx.kind==attack_kind::melee && ctx.stars_before>=2)||(direct && invoking==3 && stored_resource>=2)))++extra;
    if(g=="su" && direct && invoking==3 && strong && (five() || wide_wave))++extra;
    if(g=="vivi" && direct && strong && (five() || s.one_end>you.elapsed_time))++extra;
    if(g=="mela" && direct && invoking==3 && strong && stored_resource>=3)++extra;
    if(g=="noel" && you.piety>=75) {
        auto &t=supplies();const int points=hd<(you.experience_level+1)/2?1:strong?6:4;
        t["half_points"]=t["half_points"].get_int()+points*(pet?1:2);
    }
    grant(1+extra);
    if(g=="noel")deliver_supplies();
}
void leave_level(){
    holo_visual::clear();
    holo_wrath::leave_level();
    if(!active())return;
    using namespace holo_batch;const auto g=holo_worship::current();const int now=you.elapsed_time;
    if(g=="sopia")holo_sopia::leave_level();
    if(g=="lui")for(auto &c:s.companions){monster *m=monster_by_mid(c.mid);if(m && m->alive() && !adjacent(m->pos(),you.pos())){monster_die(*m,KILL_DISMISSED,NON_MONSTER,true);c.expires=0;}}
    if(g=="aki" || g=="fubuki")for(auto &c:s.companions){monster *m=monster_by_mid(c.mid);if(m && m->alive())monster_die(*m,KILL_DISMISSED,NON_MONSTER,true);c.expires=0;}
    if(g=="choco" && s.secondary<0){monster *m=monster_by_mid(s.marked);if(m){m->attitude=ATT_HOSTILE;m->foe=MHITYOU;m->props.erase("holo_charmed");}s.secondary=0;}
    if(data().exists("pulled"))data()["pulled"].get_table().clear();
    s.targets.clear();s.marked=MID_NOBODY;s.hazards.clear();s.candidates.clear();s.performance_hits.clear();
    if(g=="miko" || g=="aki" || g=="ayame" || g=="choco" || g=="towa" || g=="hajime" || g=="mela")s.one_end=0;
    if(g=="miko" || g=="aki" || g=="raden")s.three_end=0;
    if(g=="raden")s.shield=0;
    if(g=="polka")s.secondary=0;
    if(g=="hajime" || g=="mela" || g=="suisei")s.resource=0;
    if(g=="miko" || g=="aki" || g=="ayame" || g=="choco" || g=="towa" || g=="lamy" || g=="raden" || g=="hajime" || g=="su" || g=="vivi" || g=="mela" || g=="koyori"){
        if(s.five_end>now && g!="koyori")s.five_ready=now+(g=="ayame" || g=="choco" || g=="towa" || g=="koyori"?100:150);
        s.five_end=0;
    }
    save();
}
bool reactions_enabled(){return !active() || value("catalyst")!=0;}
void toggle_reactions(){data()["catalyst"]=value("catalyst")?0:1;}
void ate_food(int subtype){
 if(!active() || holo_worship::current()!="okayu" || you.piety<30)return;
 refresh();auto &s=holo_batch::s;s.resource=std::min(100,s.resource+(subtype==FOOD_CHUNK?8:20));
 if(!you.props.exists("holo_food_discoveries"))you.props["holo_food_discoveries"].new_table();
 auto &t=you.props["holo_food_discoveries"].get_table();auto name=std::to_string(subtype);
 if(!t.exists(name)){t[name]=true;grant(2);}
}

reaction_scope::reaction_scope(int kind,const monster &m){++reaction_depth;reaction(kind,m);}
reaction_scope::~reaction_scope(){--reaction_depth;}
move_scope::move_scope():old(you.pos()){}
move_scope::~move_scope(){if(active() && voluntary && you.turn_is_over && grid_distance(you.pos(),old)==1)holo_batch::after_move(old,true);}
bomb_scope::bomb_scope(){if(active() && holo_worship::current()=="pekora"){owner=true;if(!bomb_depth++)bomb_kills=0;}}
bomb_scope::~bomb_scope(){if(owner && !--bomb_depth){int n=bomb_kills;bomb_kills=0;if(n>=2)grant(n>=4?2:1);}}
void pulled(mid_t id){if(!active() || holo_worship::current()!="sopia")return;auto &t=data();if(!t.exists("pulled"))t["pulled"].new_table();t["pulled"].get_table()[std::to_string(id)]=true;}
void fox_attacked(const actor *source,const actor *target){
 if(!active() || holo_worship::current()!="fubuki" || !source || !source->is_monster() || !target || !holo_batch::eligible(*source->as_monster()))return;
 for(auto c:holo_batch::s.companions)if(c.mid==target->mid && c.kind==2){monster_by_mid(source->mid)->props["holo_fox_attacked_until"]=you.elapsed_time+30;break;}
}
void wave_bonus(bool wide){wide_wave=wide;}
void reaction(int kind,const monster &target){
 if(!active() || holo_worship::current()!="koyori" || !holo_batch::eligible(target))return;
 if(kind==4)return; // Slime is discovered only when it really delays movement.
 auto &t=data();if(!t.exists("discoveries"))t["discoveries"].new_table();auto &d=t["discoveries"].get_table();
 const auto id=std::to_string(kind);if(!d.exists(id)){d[id]=true;grant(3);}
}
void slime_moved(const monster &m,const coord_def &old){
 if(!active() || holo_worship::current()!="koyori" || old==m.pos() || m.airborne() || m.has_ench(ENCH_SLOW) || !holo_batch::eligible(m))return;
 if(holo_koyori::enabled()){
  const auto it=holo_batch::s.targets.find(m.mid);
  if(it!=holo_batch::s.targets.end() && (it->second.slowed_until>you.elapsed_time || it->second.weak_until>you.elapsed_time)){
   auto &t=data();if(!t.exists("discoveries"))t["discoveries"].new_table();auto &discoveries=t["discoveries"].get_table();
   if(!discoveries.exists("4")){discoveries["4"]=true;grant(3);}
  }
  return;
 }
 for(auto h:holo_batch::s.hazards)if(h.kind==4 && h.end>you.elapsed_time && grid_distance(old,h.pos)<=h.extra && holo_batch::line(old,h.pos)){
  auto &t=data();if(!t.exists("discoveries"))t["discoveries"].new_table();auto &d=t["discoveries"].get_table();if(!d.exists("4")){d["4"]=true;grant(3);}break;
 }
}

}
