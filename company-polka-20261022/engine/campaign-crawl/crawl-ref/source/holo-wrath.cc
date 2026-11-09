#include "AppHdr.h"
#include "holo-wrath.h"
#include "holo-visual.h"
#include "holo-worship.h"
#include "holo-batch-internal.h"
#include "holocrawl.h"
#include "act-iter.h"
#include "beam.h"
#include "fight.h"
#include "env.h"
#include "message.h"
#include "mgen-data.h"
#include "mon-death.h"
#include "mon-place.h"
#include "mon-ench.h"
#include "mon-util.h"
#include "player.h"
#include "random.h"
#include "shout.h"
#include "stringutil.h"
#include "terrain.h"
#include "traps.h"
#include <algorithm>
#include <stdexcept>
#include <cstdlib>
#include <fstream>

namespace holo_wrath {
namespace {
const char *key="holocrawl_wrath";
struct damage_guard {
    bool old;
    damage_guard():old(holo_batch::internal_damage){holo_batch::internal_damage=true;}
    ~damage_guard(){holo_batch::internal_damage=old;}
};
int get(const char *name) {
    if(holo_benchmark_active() || !you.props.exists(key))return 0;
    const auto &t=you.props[key].get_table();return t.exists(name)?t.at(name).get_int():0;
}
std::string god() {
    if(holo_benchmark_active() || !you.props.exists(key))return "";
    const auto &t=you.props[key].get_table();return t.exists("god")?t.at("god").get_string():"";
}
CrawlHashTable &data() {
    if(!you.props.exists(key))you.props[key].new_table();
    return you.props[key].get_table();
}
CrawlHashTable *ledger() {
    if(holo_benchmark_active() || !you.props.exists("holocrawl_worship"))return nullptr;
    return &you.props["holocrawl_worship"].get_table()["departures"].get_table();
}
int number(const CrawlHashTable &t,const char *name) {return t.exists(name)?t.at(name).get_int():0;}
bool owed(const CrawlHashTable &t) {return number(t,"wrath_remaining")>0 && number(t,"xp_remaining")>0;}
// Missing revisions identify legacy active effects: their saved rules stay intact.
bool modern() {return get("revision")>=2;}
int lifetime(int xl) {return 200+5*xl;}
struct servant_stats {int hp,ac,ev,hit,damage,speed,hd;};
servant_stats servant(const std::string &g,int x,bool decoy=false) {
    if(decoy)return {1,0,0,0,0,10,1};
    if(g=="aki")return {30+5*x,3+x/4,8,0,0,10,6+x/2};
    if(g=="fubuki")return {24+4*x,2+x/6,14+x/4,16+x,6+x,15,4+x/2};
    if(g=="ayame")return {40+6*x,3+x/3,10+x/5,16+x,8+7*x/5,x<10?10:12,5+x/2};
    if(g=="korone")return {32+5*x,2+x/5,12+x/6,16+x,7+x,15,4+x/2};
    return {20+3*x,1+x/8,14+x/4,14+x,5+3*x/4,15,4+x/2};
}
int group_size(const std::string &g,int x) {return g=="lui"?2+x/8:g=="aki" || g=="korone"?1+x/10:1+x/12;}
int slow_percent() {return effect("okayu")?(modern()?130+get("xl")/3:115):100;}
coord_def centre() {return coord_def(get("x"),get("y"));}
bool zone(const coord_def &p) {
    return grid_distance(p,centre())<=1 && holo_batch::line(centre(),p);
}
bool in_zone() {return zone(you.pos());}
void redraw() {
    you.redraw_armour_class=you.redraw_evasion=you.redraw_status_lights=you.redraw_title=true;
}
void cleanup() {
    for(monster_iterator mi;mi;++mi)if(mi->props.exists("holo_wrath_god"))
        monster_die(**mi,KILL_DISMISSED,NON_MONSTER,true);
}
void finish() {
    cleanup();auto &t=data();t["god"]=std::string();t["end"]=0;
    t["hound"]=0;t["accuracy"]=0;
    t["next"]=you.elapsed_time+100;redraw();
}
bool summoned(const monster &m) {return m.props.exists("holo_wrath_god");}
void harm(const coord_def &p,int sides,bool fire,bool single=false,int dice=2) {
    holo_visual::impact(p,single?0:1,fire);
    damage_guard scope;
    if((single?you.pos()==p:grid_distance(you.pos(),p)<=1) && holo_batch::line(p,you.pos())) {
        const int raw=roll_dice(dice,sides);
        const int damage=fire?resist_adjust_damage(&you,BEAM_FIRE,raw):you.apply_ac(raw);
        ouch(damage,KILLED_BY_DIVINE_WRATH,MID_NOBODY,(god()+"'s wrath").c_str());
    }
    // Environmental wrath never grants kill piety, XP, reaction procs or loot credit.
    for(monster_iterator mi;mi;++mi)if(!summoned(**mi)
        && (single?mi->pos()==p:grid_distance(mi->pos(),p)<=1) && holo_batch::line(p,mi->pos())) {
        const int raw=roll_dice(dice,sides);
        const int damage=fire?resist_adjust_damage(&**mi,BEAM_FIRE,raw):mi->apply_ac(raw);
        mi->hurt(nullptr,damage,fire?BEAM_FIRE:BEAM_MISSILE,KILLED_BY_DIVINE_WRATH);
    }
}
bool is_debuff(const std::string &g) {
    return g=="choco" || g=="okayu" || g=="noel" || g=="watame" || g=="lamy"
        || g=="polka" || g=="hajime" || g=="vivi";
}
bool is_summon(const std::string &g) {return g=="aki" || g=="fubuki" || g=="ayame" || g=="korone" || g=="lui";}
bool empty(const coord_def &p) {return in_bounds(p) && grd(p)==DNGN_FLOOR && !trap_at(p) && !actor_at(p) && holo_batch::line(you.pos(),p);}
void spawn(const std::string &g,int count,int duration,int xl,bool fake=false) {
    std::vector<coord_def> cells;
    for(int r=1;r<=3;++r)for(int x=-r;x<=r;++x)for(int y=-r;y<=r;++y) {
        const auto p=centre()+coord_def(x,y);
        if(std::max(abs(x),abs(y))==r && empty(p))cells.push_back(p);
    }
    for(int i=0;i<count && i<int(cells.size());++i) {
        const monster_type body=!modern() || fake?MONS_RAT:g=="aki"?MONS_OKLOB_PLANT:g=="ayame"?MONS_ORC_KNIGHT:g=="lui"?MONS_HARPY:MONS_WOLF;
        mgen_data mg(body,BEH_HOSTILE,cells[i],MHITYOU,MG_FORCE_PLACE);
        mg.extra_flags|=MF_NO_REWARD|MF_HARD_RESET;
        mg.mname=g=="aki"?"wrath rose":g=="fubuki"?(fake?"fox-tail decoy":"wrath spirit fox"):g=="ayame"?"wrath swordsman":g=="korone"?"wrath hound":"wrath hawk";
        monster *m=create_monster(mg,false);if(!m)continue;
        // Native templates supply bodies, not equipment, acid spells or loot.
        m->destroy_inventory();m->spells.clear();
        m->props["holo_wrath_revision"]=modern()?2:1;
        m->props["holo_wrath_decoy"]=fake?1:0;
        m->props["holo_wrath_god"]=g;m->props["holo_wrath_xl"]=xl;
        m->props["holo_wrath_end"]=you.elapsed_time+duration;
        m->props["holo_wrath_next"]=you.elapsed_time+15;
        m->props["holo_wrath_chain"]=0;m->props["holo_wrath_last"]=-100;
        m->hit_points=m->max_hit_points=g=="fubuki"?1:g=="aki"?10+xl:12+2*xl;
        m->speed=10;m->speed_increment=0;
        if(modern()) {
            const auto v=servant(g,xl,fake);m->hit_points=m->max_hit_points=v.hp;
            m->speed=v.speed;m->set_hit_dice(v.hd);
        }
        if(g=="fubuki")m->colour=WHITE;
        if(g=="lui")m->add_ench(mon_enchant(ENCH_FLIGHT,1,nullptr,duration));
    }
}
void start(const std::string &g,int xl) {
    auto &t=data();t["god"]=g;t["revision"]=2;t["xl"]=xl;t["x"]=you.pos().x;t["y"]=you.pos().y;
    t["arm"]=you.elapsed_time+20;t["tick"]=you.elapsed_time+20;
    t["hits"]=6;t["crow_hits"].new_table();t["accuracy"]=0;t["hound"]=0;
    t["time_fraction"]=0;t["healing_fraction"]=0;
    t["variant"]=g=="koyori"?random2(2):0;
    t["end"]=you.elapsed_time+(is_debuff(g)?100+5*xl:is_summon(g)?20+lifetime(xl):g=="miko" || (g=="koyori" && get("variant"))?120+3*xl:20);
    t["bombs"].new_table();
    if(g=="pekora") {
        // Two bombs on the same side leave an immediately reachable safe cell.
        bool placed=false;
        for(coord_def step:{coord_def(1,0),coord_def(0,1),coord_def(-1,0),coord_def(0,-1)}) {
            if(!empty(you.pos()-step))continue;
            const auto a=you.pos()+step,b=you.pos()+step*2;
            if(!in_bounds(a) || !in_bounds(b) || feat_is_solid(grd(a)) || feat_is_solid(grd(b)))continue;
            auto &bombs=t["bombs"].get_table();
            auto &one=bombs["0"].new_table();one["x"]=a.x;one["y"]=a.y;
            auto &two=bombs["1"].new_table();two["x"]=b.x;two["y"]=b.y;placed=true;break;
        }
        if(!placed){finish();return;}
    }
    if(is_debuff(g)) {
        mprf(MSGCH_WARN,"%s's wrath afflicts you for %.1f turns. See ^ for effects.",g.c_str(),(get("end")-you.elapsed_time)/10.0);
        if(g=="vivi" || g=="polka")for(monster_iterator mi;mi;++mi)
            if(mi->attitude==ATT_HOSTILE && you.can_see(**mi)){mi->foe=MHITYOU;mi->target=you.pos();mi->behaviour=BEH_SEEK;}
        if(g=="polka")noisy(20+xl/2,you.pos());
    } else {
        mprf(MSGCH_WARN,"%s's wrath: %s at (%d,%d) in 2 turns; move away!",g.c_str(),is_summon(g)?"hostile summon":g=="towa"?"one-cell shot":"3x3 strike",centre().x,centre().y);
        if(g=="pekora")for(const auto &entry:t["bombs"].get_table()) {
            const auto &b=entry.second.get_table();mprf(MSGCH_WARN,"Carrot bomb: (%d,%d), radius 1.",number(b,"x"),number(b,"y"));
        }
    }
    redraw();
}
}
void depart(const std::string &g,int piety) {
    auto *all=ledger();if(!all)return;
    bool prior_pending=!god().empty();
    for(const auto &entry:*all)if(owed(entry.second.get_table()))prior_pending=true;
    const bool pending=all->exists(g) && owed((*all)[g].get_table());
    const int old_count=pending?number((*all)[g].get_table(),"wrath_remaining"):0;
    const int old_xp=pending?number((*all)[g].get_table(),"xp_remaining"):0;
    auto &d=(*all)[g].new_table();d["xl"]=int(you.experience_level);d["at_aut"]=you.elapsed_time;d["piety"]=piety;
    // Native 50 penance commonly decays by 1..3 per event (~25 events).
    // Preserve existing debts; only new abandonment adds the new obligation.
    d["revision"]=2;
    d["wrath_remaining"]=std::max(0,old_count)+18+std::max(0,std::min(200,piety))/25;
    const int xl=you.experience_level;
    d["xp_remaining"]=std::max(0,old_xp)+std::max(200,int(exp_needed(xl+2)-exp_needed(xl)));
    if(!you.props.exists(key))data()["god"]=std::string();
    if(!prior_pending)data()["next"]=you.elapsed_time+100;
}
void gain_xp(unsigned int xp) {
    auto *all=ledger();if(!all || !xp)return;
    for(auto &entry:*all) {
        auto &t=entry.second.get_table();if(!owed(t))continue;
        const int rest=number(t,"xp_remaining");t["xp_remaining"]=xp>=unsigned(rest)?0:rest-int(xp);
        if(!number(t,"xp_remaining")){t["wrath_remaining"]=0;mprf(MSGCH_GOD,"%s's wrath is appeased by experience.",entry.first.c_str());if(god()==entry.first)finish();}
    }
}
bool effect(const char *g) {return god()==g && get("end")>you.elapsed_time;}
int accuracy(bool melee) {return effect("choco") || effect("lamy") || effect("polka")?-(modern()?6+get("xl")/10:5):effect("hajime") && melee?-(modern()?4+get("xl")/10:3):effect("lui")?-get("accuracy"):0;}
int armour(){return effect("noel")?-(modern()?4+get("xl")/6:4):0;}
int shield(){return armour();}
int skill_penalty(){return effect("noel")?(modern()?5+get("xl")/8:5):0;}
int evasion(){return effect("hajime")?-(modern()?4+get("xl")/8:3):0;}
int cold(int resistance){return effect("lamy") && resistance>-1?resistance-1:resistance;}
int regen(int rate){return effect("okayu") || effect("watame") || (effect("miko") && get("arm")<=you.elapsed_time && in_zone())?0:rate;}
int healing(int amount){if(!effect("choco") || amount<=0)return amount;const int scaled=amount*(modern()?60:75)+get("healing_fraction");data()["healing_fraction"]=scaled%100;return scaled/100;}
int action_time(int time,bool native_slow){return effect("okayu") && !native_slow?(time*slow_percent()+99)/100:time;}
void charge_action(bool native_slow){if(!effect("okayu") || native_slow || you.time_taken<=0)return;const int scaled=you.time_taken*slow_percent()+get("time_fraction");data()["time_fraction"]=scaled%100;you.time_taken=scaled/100;}
int movement(int cost){int percent=effect("korone") && get("hound")>you.elapsed_time?(modern()?130:120):100;if(effect("koyori") && get("variant") && get("arm")<=you.elapsed_time && in_zone())percent=modern()?175:150;return (cost*percent+99)/100;}
bool revealing(){return effect("vivi") || (modern() && effect("polka"));}
int incoming(int damage,kill_method_type cause,mid_t source) {
    if(damage<=0 || source==MID_NOBODY || (cause!=KILLED_BY_MONSTER && cause!=KILLED_BY_BEAM))return damage;
    if(modern() && effect("vivi"))return damage+std::min(10+get("xl")/2,(damage+2)/3);
    if(!effect("watame") || get("hits")<=0)return damage;
    data()["hits"]=get("hits")-1;
    return damage+std::min(modern()?10+get("xl")/2:10,modern()?(damage*2+4)/5:(damage+4)/5);
}
bool decoy(const actor *a){return a && a->is_monster() && summoned(*a->as_monster()) && a->as_monster()->props["holo_wrath_god"].get_string()=="fubuki" && (number(a->as_monster()->props,"holo_wrath_revision")<2 || number(a->as_monster()->props,"holo_wrath_decoy"));}
void expire_at(const coord_def &p){monster *m=monster_at(p);if(decoy(m))monster_die(*m,KILL_DISMISSED,NON_MONSTER,true);}
bool custom_monster(const monster &m,int &hp,int &ac,int &ev,int &hit,int &damage) {
    if(!summoned(m))return false;
    const auto g=m.props["holo_wrath_god"].get_string();const int xl=m.props["holo_wrath_xl"].get_int();
    hp=g=="fubuki"?1:g=="aki"?10+xl:12+2*xl;ac=g=="aki"?2:0;ev=g=="fubuki"?0:10;
    hit=14+xl/2;damage=3+xl/4;
    if(number(m.props,"holo_wrath_revision")>=2) {
        const auto v=servant(g,xl,decoy(&m));hp=v.hp;ac=v.ac;ev=v.ev;hit=v.hit;damage=v.damage;
    }
    if(g=="ayame" && you.elapsed_time-number(m.props,"holo_wrath_last")<30)hit+=std::min(6,number(m.props,"holo_wrath_chain"))*2;
    if(decoy(&m) || g=="aki")damage=0;
    return true;
}
void contact(const actor *source,const actor *target) {
    if(!source || !target || !target->is_player() || !source->is_monster())return;
    auto &m=*const_cast<monster*>(source->as_monster());if(!summoned(m))return;
    const auto g=m.props["holo_wrath_god"].get_string();
    if(g=="korone")data()["hound"]=you.elapsed_time+(modern()?30:20);
    if(g=="ayame"){const bool recent=you.elapsed_time-number(m.props,"holo_wrath_last")<30;m.props["holo_wrath_chain"]=recent?number(m.props,"holo_wrath_chain")+1:1;m.props["holo_wrath_last"]=you.elapsed_time;}
    if(g=="lui") {auto &hits=data()["crow_hits"].get_table();hits[std::to_string(m.mid)]=true;data()["accuracy"]=std::min(6,int(hits.size())*2);}
}
bool before_monster(monster &m) {
    damage_guard scope;
    if(!summoned(m))return true;
    if(number(m.props,"holo_wrath_end")<=you.elapsed_time){monster_die(m,KILL_DISMISSED,NON_MONSTER,true);return false;}
    const auto g=m.props["holo_wrath_god"].get_string();
    if(g!="aki" && !decoy(&m))return true;
    m.speed_increment=0;
    if(g=="aki" && number(m.props,"holo_wrath_next")<=you.elapsed_time) {
        m.props["holo_wrath_next"]=you.elapsed_time+15;
        const bool v2=number(m.props,"holo_wrath_revision")>=2;const int xl=number(m.props,"holo_wrath_xl");
        if(grid_distance(m.pos(),you.pos())<=(v2?6:4) && holo_batch::line(m.pos(),you.pos()))
            ouch(you.apply_ac(roll_dice(v2?2:1,v2?5+xl/2:4+xl/6)),KILLED_BY_DIVINE_WRATH,m.mid,"Aki's wrath rose");
    }
    return false;
}
void advance() {
    damage_guard scope;
    auto *all=ledger();if(!all)return;const int now=you.elapsed_time;
    if(!you.props.exists(key)){data()["god"]=std::string();data()["next"]=now+100;return;}
    if(!god().empty()) {
        const auto g=god();
        if(get("arm")>0 && get("arm")<=now) {
            const int xl=get("xl");data()["arm"]=0;
            if(is_summon(g)) {
                if(modern()) {
                    spawn(g,group_size(g,xl),lifetime(xl),xl);
                    if(g=="fubuki")spawn(g,2+xl/12,lifetime(xl),xl,true);
                } else if(g!="fubuki")spawn(g,g=="lui"?3:1,g=="lui" || g=="aki"?60:80,xl);
            }
            else if(!is_debuff(g) && !is_summon(g) && g!="miko" && !(g=="koyori" && get("variant"))) {
                if(g=="pekora")for(const auto &entry:data()["bombs"].get_table()) {const auto &b=entry.second.get_table();harm(coord_def(number(b,"x"),number(b,"y")),(modern()?8+xl/2:5+xl/4),false);}
                else {
                    const int sides=modern()?(g=="suisei" || g=="sopia"?8+xl:g=="mela"?6+xl:g=="koyori"?5+xl:g=="su"?6+xl:7+xl):(g=="suisei"?6+xl/2:g=="koyori"?5+xl/4:6+xl/3);
                    harm(centre(),sides,g=="mela" || g=="koyori",g=="towa",modern()?3:2);
                }
            }
        }
        if(g=="miko")while(get("tick")<=now && get("tick")<get("end")) {
            data()["tick"]=get("tick")+10;
            if(in_zone())ouch(resist_adjust_damage(&you,BEAM_FIRE,roll_dice(1,modern()?8+get("xl")/2:4+get("xl")/4)),KILLED_BY_DIVINE_WRATH,MID_NOBODY,"Miko's wrath sanctuary");
        }
        if(get("end")<=now)finish();
        return;
    }
    if(get("next")>now)return;
    bool combat=false;for(monster_iterator mi;mi;++mi)if(mi->attitude==ATT_HOSTILE && !decoy(&**mi) && you.can_see(**mi)){combat=true;break;}
    if(!combat)return;
    const auto ids=holo_worship::gods();int cursor=get("cursor");
    for(size_t n=0;n<ids.size();++n) {
        const int index=(cursor+n)%ids.size();const auto &g=ids[index];
        if(!all->exists(g))continue;
        auto &t=(*all)[g].get_table();if(!owed(t))continue;
        t["wrath_remaining"]=number(t,"wrath_remaining")-1;
        data()["cursor"]=int((index+1)%ids.size());start(g,int(you.experience_level));return;
    }
}
void leave_level(){
    // Resolved v2 servants remain native level actors: stairs cannot dismiss them.
    // Off-level servants retain their own expiry, checked when they next act.
    if(modern() && is_summon(god()) && !get("arm"))return;
    if(!god().empty() && !is_debuff(god()))finish();else cleanup();
}
int visual_at(const coord_def &p) {
    const auto g=god();const int now=you.elapsed_time;
    if(g.empty() || get("end")<=now)return 0;
    if(get("arm")>now && !is_debuff(g) && (g!="fubuki" || modern())) {
        bool hit=is_summon(g)?p==centre():g=="towa"?p==centre():zone(p);
        if(g=="pekora") {
            hit=false;const auto &t=you.props[key].get_table();
            if(t.exists("bombs"))for(const auto &entry:t.at("bombs").get_table()) {
                const auto &b=entry.second.get_table();const coord_def q(number(b,"x"),number(b,"y"));
                if(grid_distance(q,p)<=1 && holo_batch::line(q,p))hit=true;
            }
        }
        return hit?(get("arm")-now<=10?2:1):0;
    }
    if(!get("arm") && zone(p))return g=="miko"?3:g=="koyori" && get("variant")?4:0;
    return 0;
}
int indicator() {
    if(god().empty() || get("end")<=you.elapsed_time)return 0;
    if(get("arm")>you.elapsed_time)return get("arm")-you.elapsed_time<=10?2:1;
    return 3;
}
static std::string describe(const std::string &g,int x);
std::string status() {
    std::string result;auto *all=ledger();if(!all)return result;
    for(const auto &entry:*all) {const auto &t=entry.second.get_table();if(owed(t))result+=make_stringf("%s: %d events / %d XP; ",entry.first.c_str(),number(t,"wrath_remaining"),number(t,"xp_remaining"));}
    if(!god().empty()) {
        result+=make_stringf("ACTIVE %s: %.1f turns",god().c_str(),std::max(0,get("end")-you.elapsed_time)/10.0);
        const auto g=god();
        if(modern())result+=" | "+describe(g,get("xl"));
        else result+=g=="choco"?" (accuracy -5, healing -25%)":g=="noel"?" (weapon/unarmed skill -5, AC/SH -4)":g=="okayu"?" (action time +15%, no natural HP regen)":g=="watame"?" (no natural HP regen, next 3 direct hits +20%, cap +10)":g=="lamy"?" (accuracy -5, rC -1)":g=="polka"?" (accuracy -5, revealed, noise)":g=="hajime"?" (EV -3, melee accuracy -3)":g=="vivi"?" (stealth 0, invisibility suppressed)":"";
        if(get("arm")>you.elapsed_time)result+=make_stringf(" | warning (%d,%d): %.1f turns",centre().x,centre().y,(get("arm")-you.elapsed_time)/10.0);
    }
    return result;
}
std::string description(const std::string &g) {return describe(g,you.experience_level);}
static std::string describe(const std::string &g,int x) {
    const double turns=(100+5*x)/10.0;
    if(is_summon(g)) {
        const auto v=servant(g,x);
        std::string result=make_stringf("Wrath at current XL %d: %d hostile %s, after 2 turns for %.1f turns; each HP %d, AC %d, EV %d, speed %d, hit %d, damage %d.",x,group_size(g,x),g=="aki"?"roses":g=="fubuki"?"spirit foxes":g=="ayame"?"swordsmen":g=="korone"?"hounds":"hawks",lifetime(x)/10.0,v.hp,v.ac,v.ev,v.speed,v.hit,v.damage);
        if(g=="aki")result+=make_stringf(" Stationary; range 6 thorns, 2d%d physical every 1.5 turns; AC applies.",5+x/2);
        if(g=="fubuki")result+=make_stringf(" Plus %d harmless 1-HP decoys; only decoys can be walked through.",2+x/12);
        if(g=="ayame")result+=" Consecutive hits add up to +12 accuracy; resets after 3 turns without a hit.";
        if(g=="korone")result+=" A hit adds 30% movement time for 3 turns; does not stack.";
        if(g=="lui")result+=" Flying; different hawks give up to -6 accuracy on contact.";
        return result+" No XP or loot; resolved servants persist across stairs until expiry.";
    }
    std::string d;
    if(g=="choco")d=make_stringf("accuracy -%d; received healing -40%%",6+x/10);
    if(g=="okayu")d=make_stringf("action time +%d%%, no natural HP regen; native Slow takes precedence",30+x/3);
    if(g=="noel")d=make_stringf("effective weapon/unarmed skill -%d, AC/SH -%d; trained points unchanged",5+x/8,4+x/6);
    if(g=="watame")d=make_stringf("no natural HP regen; next 6 direct hits +40%% damage, capped at +%d per hit",10+x/2);
    if(g=="lamy")d=make_stringf("accuracy -%d, rC -1 (minimum rC-)",6+x/10);
    if(g=="polka")d=make_stringf("accuracy -%d, invisibility suppressed, stealth 0; noise %d",6+x/10,20+x/2);
    if(g=="hajime")d=make_stringf("EV -%d, melee accuracy -%d",4+x/8,4+x/10);
    if(g=="vivi")d=make_stringf("stealth 0, invisibility suppressed; direct hits +33%% damage, capped at +%d",10+x/2);
    if(!d.empty())return make_stringf("Wrath at current XL %d: %.1f turns: ",x,turns)+d+".";
    if(g=="miko")return make_stringf("Wrath: fixed 3x3 sanctuary warns for 2 turns, then lasts %.1f turns; no natural regen inside, 1d%d fire each turn; rF applies.",(100+3*x)/10.0,8+x/2);
    if(g=="pekora")return make_stringf("Wrath: two fixed radius-1 bombs after 2 turns, each 2d%d physical; AC applies; an adjacent escape cell stays clear.",8+x/2);
    if(g=="koyori")return make_stringf("Wrath: fixed 3x3 zone after 2 turns; either 3d%d fire (rF applies), or %.1f turns of +75%% movement time inside slime.",5+x,(100+3*x)/10.0);
    const int sides=g=="suisei" || g=="sopia"?8+x:g=="mela"?6+x:g=="su"?6+x:7+x;
    return make_stringf("Wrath at current XL %d: fixed %s after 2 turns, 3d%d %s; %s applies. Walls block it; allies may be hit.",x,g=="towa"?"single cell":"3x3 strike",sides,g=="mela"?"fire":"physical",g=="mela"?"rF":"AC");
}
void validate() {
    // Called by the isolated native campaign fixture, never in ordinary play.
    const auto old=you.props;const int now=you.elapsed_time,hp=you.hp,taken=you.time_taken;const auto origin=you.pos();
    auto require=[](bool ok){if(!ok)throw std::runtime_error("Holo wrath regression");};
    for(const auto &g:holo_worship::gods()) {
        data()["revision"]=1;data()["god"]=g;data()["end"]=now+50;data()["arm"]=now+20;
        require(effect(g.c_str()));require(!status().empty());
        require(regen(100)==((g=="okayu" || g=="watame")?0:100));
        require(healing(20)==(g=="choco"?15:20));
        require(cold(0)==(g=="lamy"?-1:0));
        require(action_time(10,false)==(g=="okayu"?12:10));
        require(action_time(15,true)==15);
        require(revealing()==(g=="vivi"));
    }
    // Every dispatcher runs inside a native level. Move outside each warned
    // square before resolving it, then confirm that no strike follows us.
    for(const auto &g:holo_worship::gods()) {
        you.elapsed_time=now;you.hp=hp;
        start(g,12);const int end=get("end");
        if(g=="pekora")require(data()["bombs"].get_table().size()==2);
        if(!is_debuff(g) && (g!="fubuki" || modern())) {
            require(get("arm")==now+20 && you.hp==hp);
            you.moveto(origin+coord_def(0,-3));you.elapsed_time=now+20;advance();
            require(you.hp==hp);
        }
        for(monster_iterator mi;mi;++mi)if(summoned(**mi)) {
            require(testbits(mi->flags,MF_NO_REWARD) && mi->inv[MSLOT_WEAPON]==NON_ITEM);
            if(decoy(&**mi))require(!before_monster(**mi));else if(g=="fubuki")require(before_monster(**mi));
            const auto xp=you.experience;const int piety=you.piety;
            mi->hurt(&you,10000,BEAM_MISSILE);
            require(you.experience==xp && you.piety==piety);
        }
        you.elapsed_time=end;advance();require(god().empty());
        for(monster_iterator mi;mi;++mi)require(!summoned(**mi));
        you.moveto(origin);
    }
    // Returning and leaving again adds obligations; XP cannot be replaced by
    // waiting, and legacy eight-event debt is retained.
    you.elapsed_time=now;you.props=old;
    auto &departures=*ledger();departures.clear();
    depart("noel",120);require(number(departures["noel"].get_table(),"wrath_remaining")==22);
    depart("noel",0);require(number(departures["noel"].get_table(),"wrath_remaining")==40);
    const int debt=number(departures["noel"].get_table(),"xp_remaining");
    gain_xp(1);require(number(departures["noel"].get_table(),"xp_remaining")==debt-1);
    gain_xp(debt);require(!owed(departures["noel"].get_table()));
    // A pending warning delivers damage at its fixed square, with no current
    // worship needed. The alternate path above proves that movement avoids it.
    you.hp=hp;you.elapsed_time=now;start("towa",12);you.elapsed_time=now+20;advance();require(you.hp<hp);
    you.elapsed_time=now;start("watame",12);data()["hits"]=3;
    require(incoming(20,KILLED_BY_MONSTER,MID_PLAYER)==28);
    require(incoming(20,KILLED_BY_POISON,MID_PLAYER)==20 && get("hits")==2);
    require(incoming(100,KILLED_BY_BEAM,MID_PLAYER)==116);
    leave_level();require(effect("watame"));
    start("suisei",12);leave_level();require(god().empty());
    start("okayu",12);you.time_taken=10;charge_action(false);require(you.time_taken==13);
    you.time_taken=10;charge_action(false);require(you.time_taken==13);
    you.time_taken=15;charge_action(true);require(you.time_taken==15);
    start("choco",12);int received=0;for(int i=0;i<4;++i)received+=healing(1);require(received==2);
    const int resist=you.duration[DUR_RESISTANCE];
    you.duration[DUR_RESISTANCE]=0;you.elapsed_time=now;you.hp=hp;start("mela",12);rng::seed(12345);you.elapsed_time=now+20;advance();const int fire_damage=hp-you.hp;
    you.duration[DUR_RESISTANCE]=100;you.elapsed_time=now;you.hp=hp;start("mela",12);rng::seed(12345);you.elapsed_time=now+20;advance();require(hp-you.hp<fire_damage);
    you.duration[DUR_RESISTANCE]=resist;
    // Exercise real actors and native melee at five progression points, rather
    // than treating formula comparisons as combat validation.
    const int old_xl=you.experience_level;
    int profiles=0,attacks=0,real_foxes=0,decoys=0;
    std::ofstream report;
    if(const char *dir=std::getenv("HOLOCRAWL_CAMPAIGN_OUTPUT"))report.open(std::string(dir)+"/wrath02-validation.json");
    if(report)report<<"{\"profiles\":[";
    for(int xl:{5,10,15,20,27})for(const std::string g:{"aki","fubuki","ayame","korone","lui"}) {
        cleanup();you.moveto(origin);you.hp=hp;you.elapsed_time=now;you.experience_level=xl;
        start(g,xl);you.elapsed_time=now+20;advance();
        int count=0,fakes=0;monster *fighter=nullptr;
        for(monster_iterator mi;mi;++mi)if(summoned(**mi)) {
            require(mi->spells.empty());
            for(int slot=0;slot<NUM_MONSTER_SLOTS;++slot)require(mi->inv[slot]==NON_ITEM);
            if(decoy(&**mi)){++fakes;continue;}
            ++count;fighter=*mi;
            int ph,pa,pe,pt,pd;require(custom_monster(**mi,ph,pa,pe,pt,pd));
            const auto v=servant(g,xl);
            require(mi->max_hit_points==v.hp && mi->speed==v.speed && mi->get_hit_dice()==v.hd);
            require(mi->armour_class()==v.ac && mi->evasion()==v.ev && pd==v.damage);
        }
        require(count==group_size(g,xl));
        require(fakes==(g=="fubuki"?2+xl/12:0));
        if(g=="fubuki"){real_foxes+=count;decoys+=fakes;}
        leave_level();require(effect(g.c_str()));
        // Actual native combat: reset HP each trial to prevent fixture deaths.
        int total_damage=0,hits=0;
        require(fighter);
        for(int n=0;n<32;++n) {
            you.hp=10000;
            if(g=="aki") {
                fighter->props["holo_wrath_next"]=you.elapsed_time;
                require(!before_monster(*fighter));
                if(you.hp<10000)++hits;
            } else {bool hit=false;fight_melee(fighter,&you,&hit);hits+=hit;}
            total_damage+=10000-you.hp;++attacks;
        }
        require(total_damage>0);
        const auto v=servant(g,xl);
        if(report){if(profiles)report<<',';report<<"{\"god\":\""<<g<<"\",\"xl\":"<<xl<<",\"count\":"<<count<<",\"decoys\":"<<fakes<<",\"hp\":"<<v.hp<<",\"ac\":"<<v.ac<<",\"ev\":"<<v.ev<<",\"speed\":"<<v.speed<<",\"damage\":"<<v.damage<<",\"nativeAttackTrials\":32,\"hits\":"<<hits<<",\"totalDamage\":"<<total_damage<<'}';}
        ++profiles;
        const int expiry=number(fighter->props,"holo_wrath_end");
        require(expiry==get("end"));you.elapsed_time=expiry;
        require(!before_monster(*fighter));advance();require(god().empty());
    }
    cleanup();you.experience_level=old_xl;you.hp=hp;you.elapsed_time=now;
    // Old active effects and pending debt survive without being multiplied.
    departures.clear();auto &legacy=departures["noel"].new_table();
    legacy["wrath_remaining"]=8;legacy["xp_remaining"]=500;
    depart("noel",0);require(number(departures["noel"].get_table(),"wrath_remaining")==26);
    start("noel",12);data()["revision"]=1;require(armour()==-4 && skill_penalty()==5);
    finish();departures.clear();depart("ayame",120);
    const int next=get("next");depart("noel",120);require(get("next")==next);
    you.experience_level=old_xl+1;you.elapsed_time=next;advance();require(get("xl")==old_xl+1);
    you.experience_level=old_xl;
    finish();start("choco",20);require(healing(20)==12 && accuracy(true)==-8);
    start("watame",20);for(int i=0;i<6;++i)require(incoming(100,KILLED_BY_MONSTER,MID_PLAYER)==120);
    require(incoming(100,KILLED_BY_MONSTER,MID_PLAYER)==100);
    start("vivi",20);require(incoming(100,KILLED_BY_BEAM,MID_PLAYER)==120 && revealing());
    start("polka",20);require(revealing() && accuracy(false)==-8);
    start("noel",20);require(armour()==-7 && shield()==-7 && skill_penalty()==7);
    start("hajime",20);require(evasion()==-6 && accuracy(true)==-6 && accuracy(false)==0);
    start("lamy",20);require(cold(-1)==-1 && cold(3)==2 && accuracy(false)==-8);
    if(report)report<<"],\"status\":\"passed\",\"nativeProfiles\":"<<profiles<<",\"nativeAttackTrials\":"<<attacks<<",\"realFoxes\":"<<real_foxes<<",\"decoys\":"<<decoys<<",\"legacyRules\":true,\"stairsRetainServants\":true,\"currentXLAtTrigger\":true,\"debuffs\":true,\"expiry\":true}\n";
    cleanup();you.moveto(origin);you.hp=hp;
    you.props=old;you.elapsed_time=now;you.time_taken=taken;
}
}
