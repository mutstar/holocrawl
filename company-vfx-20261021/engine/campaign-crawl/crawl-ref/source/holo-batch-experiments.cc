#include "AppHdr.h"
#include "holo-campaign.h"
#include "holo-batch-internal.h"
#include <algorithm>
#include <stdexcept>
#include "act-iter.h"
#include "cloud.h"
#include "env.h"
#include "fight.h"
#include "holocrawl.h"
#include "mon-ench.h"
#include "mon-util.h"
#include "player.h"
#include "terrain.h"

namespace holo_batch {
namespace {
bool valid(monster *mon,int range=5) {
    return mon && mon->alive() && mon->attitude==ATT_HOSTILE && you.can_see(*mon)
        && grid_distance(you.pos(),mon->pos())<=range && seen(mon->pos());
}
bool cone(const coord_def &pos,const coord_def &dir,int range) {
    const coord_def d=pos-you.pos();
    for(int r=1;r<=range;++r) for(int w=1-r;w<r;++w)
        if(d==coord_def(dir.x*r-dir.y*w,dir.y*r+dir.x*w)) return true;
    return false;
}
coord_def direction(monster &mon) {
    coord_def d=mon.pos()-you.pos();return coord_def((d.x>0)-(d.x<0),(d.y>0)-(d.y<0));
}
void quest_success(int hd) {
    const int old_ap=s.resource;
    s.resource=min(6,s.resource+1+(hd>=you.experience_level));s.one_end=you.elapsed_time+60;
    s.totals.ap_earned+=s.resource-old_ap;++s.totals.performances_completed;
    s.one_ready=you.elapsed_time+50;s.secondary=0;
    for(mid_t id:s.performance_hits) s.rewarded.insert(id);
    s.performance_hits.clear();++s.totals.procs;holo_campaign::grant(1);
}
void performance_hit(mid_t mid,int hd,bool killed) {
    if(!is(god_id::polka) || !s.secondary || s.three_end<=you.elapsed_time
        || s.rewarded.count(mid) || hd<max(1,(you.experience_level+1)/2)) return;
    s.performance_hits.insert(mid);if(mid==s.marked) ++s.offence;
    if(killed && ((mid==s.marked && ((s.secondary==1 && s.offence>=3)
        || (s.secondary==2 && s.defence>=2))) || (s.secondary==3 && s.performance_hits.size()>=3))) quest_success(hd);
}
void fire_area(const coord_def &origin,int radius,int raw,bool self) {
    std::vector<mid_t> ids;
    for(monster_iterator mi;mi;++mi) if(mi->alive() && grid_distance(origin,mi->pos())<=radius
        && line(origin,mi->pos())) ids.push_back(mi->mid);
    for(mid_t id:ids) {
        monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
        const bool credit=eligible(*mon);const int hd=mon->get_experience_level();
        const int dealt=hurt(*mon,raw,BEAM_FIRE,false,true);
        if(credit && dealt>0) performance_hit(id,hd,!mon->alive());
    }
    if(self && grid_distance(origin,you.pos())<=radius && line(origin,you.pos())) {
        const int before=you.hp;
        ouch(resist_adjust_damage(&you,BEAM_FIRE,raw),KILLED_BY_WILD_MAGIC,you.mid,"reagent combustion");
        s.totals.self_damage+=max(0,before-you.hp);
    }
}
void reagent(monster &mon,int type,int at) {
    auto &t=s.targets[mon.mid];const int previous=t.expires>at?t.kind:0;
    if(holo_campaign::reactions_enabled() && previous && previous!=type && you.piety>=75 && you.piety>=2) {
        you.piety-=2;++s.totals.procs;
        const int pair=previous+type;
        holo_campaign::reaction_scope campaign_reaction(pair,mon);
        const bool critical=s.five_end>at && s.exhibit==pair;
        const coord_def origin=mon.pos();t.kind=0;t.stacks=0;t.expires=0;
        if(critical) { s.five_end=0;s.five_ready=at+100; }
        if(pair==3) fire_area(origin,critical?2:1,roll_dice(critical?4:2,(critical?8:6)+s.inv/3),true);
        else if(pair==5) {
            if(critical) t.weak_until=at+40;
            hurt(mon,roll_dice(critical?4:3,(critical?6:4)+s.inv/3),BEAM_MISSILE,true,true);
        } else {
            hazard h;h.pos=origin;h.kind=4;h.extra=critical?2:1;
            h.end=at+(critical?60+2*s.inv:40+s.inv);s.hazards.push_back(h);
            if(critical) for(monster_iterator mi;mi;++mi) {
                auto &status=s.targets[mi->mid];
                if(mi->alive() && grid_distance(origin,mi->pos())<=2 && line(origin,mi->pos())
                    && !mi->airborne() && mi->res_constrict()<3 && status.immune<=at) {
                    status.root=at+20;status.immune=at+80;
                }
            }
            if(critical && !you.airborne() && you.res_constrict()<3 && grd(you.pos())==DNGN_FLOOR
                && grid_distance(origin,you.pos())<=2 && line(origin,you.pos()) && s.tertiary<=at) {
                s.defence=at+20;s.tertiary=at+80;
            }
        }
        return;
    }
    t.kind=type;t.expires=at+60;t.stacks=type==1?4:0;t.next=at+10;
    if(type!=1) hurt(mon,roll_dice(1,6+s.inv/3),type==2?BEAM_FIRE:BEAM_COLD,false,true);
}
void heat(int gain,int at) {
    const int bucket=at/10;
    if(s.last_incoming!=bucket) { s.last_incoming=bucket;s.secondary=0; }
    gain=min(2-s.secondary,gain);s.resource=min(6,s.resource+gain);s.secondary+=gain;
    if(gain>0) s.one_end=at+30;
}
bool extinguish(const coord_def &p,bool reward) {
    const cloud_struct *cloud=cloud_at(p);
    if(!cloud || cloud->type!=CLOUD_FIRE) return false;
    const bool eligible=s.eligible_sources.count(cloud->source);
    delete_cloud(p);if(reward && eligible) heat(2,you.elapsed_time);return true;
}
}

int polka_finale(int mode,int applause,monster *target)
{
    const int now=you.elapsed_time;
    if(!is(god_id::polka) || mode<0 || mode>2 || applause<3 || applause>6 || applause>s.resource
        || now<s.five_ready || (mode==0 && !manual() && !valid(target)) || (mode==2 && enemies(you.pos(),2).empty())
        || !pay(6,10,120)) return 0;
    s.resource-=applause;s.totals.ap_spent+=applause;s.five_ready=now+160;
    if(mode==0) fire_area(manual()?manual_aim:target->pos(),2,roll_dice(2,8+s.inv/3)+4*applause,false);
    else if(mode==1) { heal(8+s.inv/2+4*applause);s.five_end=now+30+10*applause; }
    else for(mid_t id:enemies(you.pos(),2,true)) {
        monster *mon=monster_by_mid(id);push(*mon,you.pos(),1);
        if(mon->alive() && !mental_immune(*mon) && !mon->clarity()
            && x_chance_in_y(max(15,min(85,45+2*s.inv+3*applause-3*mon->get_experience_level())),100))
            mon->add_ench(mon_enchant(ENCH_CONFUSION,1,&you,10+5*applause+s.inv/3));
    }
    return 10;
}
int prepare_reagent(int type)
{
    if(!is(god_id::koyori) || type<1 || type>3) return 0;
    const int free=min(6-s.stock[0]-s.stock[1]-s.stock[2],4-s.stock[type-1]);
    if(free<=0 || !pay(3,0)) return 0;
    s.stock[type-1]+=min(2,free);return 10;
}
int throw_reagent(monster &target,int type)
{
    if(!is(god_id::koyori) || type<1 || type>3 || s.stock[type-1]<=0 || !valid(&target)) return 0;
    --s.stock[type-1];++s.totals.casts;reagent(target,type,you.elapsed_time);return 10;
}
int coat_reagent(int type)
{
    if(!is(god_id::koyori) || type<1 || type>3 || s.stock[type-1]<=0) return 0;
    --s.stock[type-1];s.offence=type;s.one_end=you.elapsed_time+55;++s.totals.casts;return 5;
}
int experiment_action(monster *target)
{
    const int now=you.elapsed_time;
    if(is(god_id::polka)) {
        if(want(5) && s.resource>=3 && now>=s.five_ready) {
            const bool useful=!policy() || you.hp_max-you.hp>=8+s.inv/2+4*s.resource
                || enemies(you.pos(),5).size()>=2
                || (target && target->hit_points>=you.experience_level*2);
            if(useful && policy_can_spend(6)) {
                const bool heal_now=policy()?you.hp_max-you.hp>=8+s.inv/2+4*s.resource:you.hp*2<you.hp_max;
                const int aut=polka_finale(heal_now?1:0,s.resource,target);if(aut) return aut;
            }
        }
        if(want(1) && s.secondary==0 && now>=s.one_ready && (!policy() || s.one_end<=now) && policy_can_spend(1)) {
            std::vector<mid_t> candidates;
            for(mid_t id:enemies(you.pos(),6)) if(eligible(*monster_by_mid(id)) && !s.rewarded.count(id)
                && monster_by_mid(id)->get_experience_level()>=max(1,(you.experience_level+1)/2)) candidates.push_back(id);
            bool doable=!policy() || policy_melee() || candidates.size()>=3;
            if(policy()) for(mid_t id:candidates)
                if(monster_by_mid(id)->get_experience_level()>=you.experience_level) doable=true;
            if(!candidates.empty() && doable && pay(1,0)) {
                s.marked=candidates.front();s.secondary=candidates.size()>=3?3:2;
                for(mid_t id:candidates) if(monster_by_mid(id)->get_experience_level()>=you.experience_level) {
                    s.marked=id;s.secondary=1;break;
                }
                s.three_end=now+5+120+3*s.inv;s.offence=0;s.defence=0;
                ++s.totals.performances_started;
                s.performance_hits.clear();s.centre=you.pos();return 5;
            }
        }
        if(want(3) && valid(target,1) && now>=s.three_ready && !you.caught() && !you.cannot_act()
            && !probe_is("no_acrobat") && !probe_is("no_acrobat_bank3")
            && (!policy() || (policy_melee() && s.secondary==2 && s.offence>0 && s.defence<2))
            && policy_can_spend(3)) {
            const coord_def landing=target->pos()*2-you.pos();
            if(in_bounds(landing) && !actor_at(landing) && grd(landing)==DNGN_FLOOR && seen(landing) && (!manual() || !manual_option || s.resource>=1) && pay(3,2,75)) {
                const coord_def old=you.pos();you.move_to_pos(landing);you.apply_location_effects(old);after_move(old,true);
                s.tertiary=now+30;s.three_ready=now+40;
                if(manual() && manual_option==1){--s.resource;for(mid_t id:enemies(you.pos(),1))s.targets[id].weak_until=now+40;}
                return 10;
            }
        }
        if(!manual() && s.secondary==2 && s.offence>0 && s.defence<2 && valid(target,1) && !you.caught()
            && (!policy() || policy_melee())) {
            for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
                const coord_def p=you.pos()+coord_def(dx,dy);
                if((dx||dy) && in_bounds(p) && !actor_at(p) && grd(p)==DNGN_FLOOR
                    && p!=s.centre && adjacent(p,target->pos())) {
                    const coord_def old=you.pos();you.move_to_pos(p);you.apply_location_effects(old);after_move(old,true);
                    return player_speed()*player_movement_speed()/10;
                }
            }
        }
    }
    if(!manual() && is(god_id::koyori) && valid(target)) {
        const int prior=s.targets[target->mid].expires>now?s.targets[target->mid].kind:0;
        int type=s.secondary%3+1;
        const int distance=grid_distance(you.pos(),target->pos());
        if(policy() && prior && prior+type==3 && distance<=2) type=3;
        if(policy() && s.stock[type-1]==0 && distance<3 && s.totals.casts>0) {
            for(int available:{1,3,2}) if(s.stock[available-1]>0
                && !(prior && prior+available==3 && distance<=2)) { type=available;break; }
        }
        if(prior && (!policy() || prior!=type) && !five() && now>=s.five_ready
            && (!policy() || (distance>2 && enemies(target->pos(),2).size()>=2))
            && policy_can_spend(5) && pay(5,8,120)) {
            s.exhibit=prior+type;s.five_end=now+55;s.five_ready=s.five_end+100;return 5;
        }
        if(s.stock[type-1]==0) {
            if((!policy() || distance>=3 || (s.totals.casts==0 && you.hp*4>=you.hp_max*3))
                && policy_can_spend(3)) {
                const int aut=prepare_reagent(type);if(aut) return aut;
            }
        } else { const int aut=throw_reagent(*target,type);if(aut) { ++s.secondary;return aut; } }
    }
    if(is(god_id::mela)) {
        if(want(5) && !five() && now>=s.five_ready && !probe_is("no_ultimate") && pay(6,12,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;
            s.resource=6;s.last_event=now+30;you.duration[DUR_LIQUID_FLAMES]=0;return 10;
        }
        if(want(3) && (valid(target,five()?4:3) || (manual() && manual_aim!=you.pos() && seen(manual_aim) && grid_distance(you.pos(),manual_aim)<=(five()?4:3))) && now>=s.three_ready && !probe_is("no_breath") && pay(3,3,75)) {
            const int stored=s.resource;s.resource=0;coord_def d=manual()?manual_aim-you.pos():direction(*target);
            d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
            for(mid_t id:enemies(you.pos(),five()?4:3)) {
                monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
                if(cone(mon->pos(),d,five()?4:3))
                    hurt(*mon,roll_dice(five()?3:2,6+s.inv/3)+mela_heat_multiplier()*stored,BEAM_FIRE,false,true);
            }
            for(int dx=-4;dx<=4;++dx) for(int dy=-4;dy<=4;++dy) {
                const coord_def p=you.pos()+coord_def(dx,dy);
                if(in_bounds(p) && seen(p) && cone(p,d,five()?4:3)) extinguish(p,true);
            }
            s.three_ready=now+40;return 10;
        }
    }
    return 0;
}
void experiment_tick(int at)
{
    if(is(god_id::polka) && s.secondary && at>=s.three_end) { s.secondary=0;s.performance_hits.clear();++s.totals.performances_expired; }
    if(is(god_id::koyori)) for(auto &p:s.targets) {
        auto &t=p.second;monster *mon=monster_by_mid(p.first);
        if(at>=t.expires) { t.kind=0;t.stacks=0; }
        if(mon && mon->alive() && t.kind==1 && t.stacks>0 && at>=t.next) {
            t.next+=10;--t.stacks;hurt(*mon,2+s.inv/9,BEAM_POISON,false);
        }
    }
    if(is(god_id::mela)) {
        if(at<s.five_end) {
            if(at>=s.last_event) { s.last_event+=20;s.resource=min(6,s.resource+1);s.one_end=at+30; }
            if(at%10==0) {
                you.duration[DUR_LIQUID_FLAMES]=0;
                for(int dx=-2;dx<=2;++dx) for(int dy=-2;dy<=2;++dy) {
                    const coord_def p=you.pos()+coord_def(dx,dy);if(in_bounds(p) && seen(p)) extinguish(p,false);
                }
            }
        } else if(s.resource>0 && at>=s.one_end) { --s.resource;s.one_end=at+20; }
    }
}
void experiment_after_attack(monster *target)
{
    const int now=you.elapsed_time;
    if(is(god_id::polka)) {
        if(ctx.damaged && ctx.eligible) performance_hit(ctx.target,ctx.hd,!target || !target->alive());
        s.tertiary=0;
    }
    if(is(god_id::mela) && passive() && (!holo_campaign::active() || s.offence) && ctx.damaged && target && target->alive() && s.resource>0 && !s.defence) {
        --s.resource;hurt(*target,roll_dice(1,3+s.inv/6),BEAM_FIRE,false);
    }
    if(is(god_id::koyori) && ctx.primary && ctx.kind==attack_kind::spell && target && target->alive())
        experiment_spell(*target,ctx.element);
    if(is(god_id::koyori) && ctx.primary && ctx.kind!=attack_kind::spell
        && s.offence && s.one_end>now) {
        const int type=s.offence;s.offence=0;if(target && target->alive()) reagent(*target,type,now);
    }
}
void experiment_spell(monster &mon,beam_type flavour)
{
    if(!is(god_id::koyori) || !holo_campaign::reactions_enabled() || you.piety<75 || you.piety<2 || (flavour!=BEAM_FIRE && flavour!=BEAM_COLD)) return;
    const int old=s.targets[mon.mid].expires>you.elapsed_time?s.targets[mon.mid].kind:0;
    const int type=flavour==BEAM_FIRE?2:3;
    if(old && old!=type) reagent(mon,type,you.elapsed_time);
}
void experiment_move(const coord_def &old,bool voluntary)
{
    if(is(god_id::polka) && s.secondary==2 && s.offence>0 && voluntary && old!=you.pos()
        && you.pos()!=s.centre) { ++s.defence;s.centre=you.pos(); }
}
void experiment_contact(const actor *attacker,beam_type flavour)
{
    if(is(god_id::mela) && passive() && attacker && s.eligible_sources.count(attacker->mid))
        heat(flavour==BEAM_FIRE || flavour==BEAM_STICKY_FLAME?2:1,you.elapsed_time);
}
int experiment_energy(const monster &mon,energy_use_type kind,int base)
{
    if(!is(god_id::koyori) || mon.airborne() || mon.is_stationary() || grd(mon.pos())!=DNGN_FLOOR
        || (kind!=EUT_MOVE && kind!=EUT_SWIM) || mon.has_ench(ENCH_SLOW)) return base;
    for(const auto &h:s.hazards) if(h.kind==4 && h.end>you.elapsed_time
        && grid_distance(h.pos,mon.pos())<=h.extra && line(h.pos,mon.pos())) return (base*150+99)/100;
    return base;
}
int monster_ac_penalty(const monster &mon) {
    if(!is(god_id::koyori))return 0;
    const auto found=s.targets.find(mon.mid);
    return found!=s.targets.end() && found->second.weak_until>you.elapsed_time ? 6:0;
}
int elemental_damage(int damage,beam_type flavour,const actor *source)
{
    if(damage>0 && source) { attack_attempt(source,&you);contact(source,flavour); }
    return is(god_id::mela) && five() && !probe_is("no_fire_ward") && !probe_is("no_extra_fire_ward") && (flavour==BEAM_FIRE || flavour==BEAM_STICKY_FLAME) ? div_rand_round(damage,2):damage;
}
void fire_contact(mid_t source) {
    if(is(god_id::mela) && passive() && s.eligible_sources.count(source)) heat(2,you.elapsed_time);
}
int fire_protection(const actor &target,int damage,beam_type flavour) {
    return is(god_id::mela) && five() && !probe_is("no_fire_ward") && !probe_is("no_extra_fire_ward") && (flavour==BEAM_FIRE || flavour==BEAM_STICKY_FLAME)
        && (target.is_player() || target.is_monster() && target.as_monster()->attitude==ATT_FRIENDLY)
        && grid_distance(you.pos(),target.pos())<=2 && seen(target.pos()) ? div_rand_round(damage,2):damage;
}
int movement_cost(int base) {
    if(!is(god_id::koyori) || you.airborne() || you.duration[DUR_SLOW] || grd(you.pos())!=DNGN_FLOOR) return base;
    for(const auto &h:s.hazards) if(h.kind==4 && h.end>you.elapsed_time
        && grid_distance(h.pos,you.pos())<=h.extra && line(h.pos,you.pos())) return (base*150+99)/100;
    return base;
}
bool player_rooted() { return is(god_id::koyori) && s.defence>you.elapsed_time; }
void validate_experiments()
{
    const auto require=[](bool ok,const char *message) { if(!ok) throw std::runtime_error(std::string("Reagent native fixture: ")+message); };
    const auto enemy=[]()->monster* { for(monster_iterator mi;mi;++mi) if(mi->attitude==ATT_HOSTILE) return *mi;return nullptr; };
    holo_reset_validation_fixture();reset("koyori",12);monster *mon=enemy();
    const int before=mon->hit_points,mp=you.magic_points;
    reagent(*mon,1,0);require(mon->hit_points==before && s.targets[mon->mid].stacks==4,"poison deals immediate damage");
    you.elapsed_time=9;advance(9);require(mon->hit_points==before,"poison ticks before ten aut");
    you.elapsed_time=10;advance(10);require(mon->hit_points<before,"native poison resistance/damage path does not run");
    reagent(*mon,2,10);require(s.targets[mon->mid].kind==0 && s.targets[mon->mid].stacks==0
        && you.magic_points==mp && you.piety==178 && you.hp<you.hp_max,"combustion fails to consume residue/piety or damage its caster");
    holo_reset_validation_fixture();reset("koyori",12);mon=enemy();
    const int armour_before=mon->armour_class();
    require(s.targets.empty(),"AC display query inserted empty target state");reagent(*mon,2,0);
    s.five_end=50;s.exhibit=5;reagent(*mon,3,0);
    require(mon->armour_class()==max(0,armour_before-6) && s.five_end==0 && s.five_ready==100,"critical thermal shock has wrong AC or expiry");
    you.elapsed_time=40;require(mon->armour_class()==armour_before,"thermal AC penalty never expires");
    holo_reset_validation_fixture();reset("koyori",12);mon=enemy();reagent(*mon,3,0);reagent(*mon,1,0);
    require(experiment_energy(*mon,EUT_MOVE,10)==15 && experiment_energy(*mon,EUT_ATTACK,10)==10
        && movement_cost(10)==15,"slime does not slow both ground allies and enemies without slowing attacks");
    you.elapsed_time=52;require(experiment_energy(*mon,EUT_MOVE,10)==10 && movement_cost(10)==10,"slime persists beyond its lifetime");
    holo_reset_validation_fixture();reset("koyori",12);mon=enemy();
    require(prepare_reagent(3)==10 && coat_reagent(3)==5 && s.stock[2]==1,"manufacture/coating has wrong stock or time cost");
    begin_attack(*mon);end_attack(10);require(s.offence==3,"a miss consumes coating");
    const int cold_before=mon->hit_points;begin_attack(*mon);note_primary_damage(mon,0);end_attack(10);
    require(s.offence==0 && mon->hit_points<cold_before,"a zero-damage weapon hit fails to consume/apply coating");
    holo_reset_validation_fixture();reset("koyori",12);mon=enemy();mon->type=MONS_IRON_DRAGON;
    bool zero_weapon=false;
    for(int attempt=0;attempt<30 && !zero_weapon;++attempt) {
        s.offence=3;s.one_end=1000;begin_attack(*mon);bool hit=false;fight_melee(&you,mon,&hit);
        zero_weapon=hit && ctx.primary && !ctx.damaged;end_attack(10);
        if(zero_weapon) require(s.offence==0,"native armour-zero weapon hit never reaches the coating hook");
    }
    require(zero_weapon,"weapon-zero native fixture did not exercise its branch");
    holo_reset_validation_fixture();reset("polka",12);mon=enemy();s.resource=6;
    const coord_def before_push=mon->pos();require(polka_finale(2,3)==10 && s.resource==3
        && grid_distance(you.pos(),mon->pos())>grid_distance(you.pos(),before_push),"chaos finale does not push or charges the wrong applause");
}
}

namespace holo_batch {
int manual_experiment(monster *target) {
 if(!manual())return -1;
 const int now=you.elapsed_time;
 if(is(god_id::polka)) {
  if(manual_tier==-1){s.secondary=0;s.performance_hits.clear();return 0;}
  if(manual_tier==5)return polka_finale(manual_option,manual_amount,target);
  if(manual_tier==1){
   if(s.secondary || now<s.one_ready || manual_option<1 || manual_option>3)return 0;
   auto candidates=enemies(you.pos(),6);std::vector<mid_t> eligible_ids;
   for(mid_t id:candidates)if(eligible(*monster_by_mid(id)) && !s.rewarded.count(id) && monster_by_mid(id)->get_experience_level()>=max(1,(you.experience_level+1)/2))eligible_ids.push_back(id);
   if(!valid(target,6) || std::find(eligible_ids.begin(),eligible_ids.end(),target->mid)==eligible_ids.end() || (manual_option==1 && target->get_experience_level()<you.experience_level) || (manual_option==3 && eligible_ids.size()<3) || !pay(1,0))return 0;
   s.marked=target->mid;s.secondary=manual_option;s.three_end=now+5+120+3*s.inv;s.offence=0;s.defence=0;s.performance_hits.clear();s.centre=you.pos();++s.totals.performances_started;return 5;
  }
  return -1;
 }
 if(is(god_id::koyori)) {
  if(manual_tier==1){if(manual_option>=21)return coat_reagent(manual_option-20);if(manual_option>=11)return target?throw_reagent(*target,manual_option-10):0;return prepare_reagent(manual_option);}
  if(manual_tier==3){holo_campaign::toggle_reactions();return 0;}
  if(manual_tier==5){if(manual_option<3 || manual_option>5 || five() || now<s.five_ready || !pay(5,8,120))return 0;s.exhibit=manual_option;s.five_end=now+55;s.five_ready=s.five_end+100;return 5;}
  return 0;
 }
 if(is(god_id::mela) && manual_tier==-1){s.offence=s.offence?0:1;return 0;}
 return -1;
}
}
