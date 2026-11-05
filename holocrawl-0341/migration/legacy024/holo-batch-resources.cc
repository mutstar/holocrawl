#include "AppHdr.h"
#include "holo-lamy.h"
#include "holo-visual.h"
#include "holo-campaign.h"
#include "env.h"
#include "act-iter.h"
#include "holo-batch-internal.h"
#include "monster.h"
#include "fight.h"
#include "food.h"
#include "holocrawl.h"
#include "mon-ench.h"
#include "mon-util.h"
#include "player.h"
namespace holo_batch {
bool mental_immune(const monster &mon)
{ return mons_intel(mon)==I_BRAINLESS && !(mon.holiness()&MH_NATURAL); }
namespace {
bool valid(monster *mon,int range=5) {
    return mon && mon->alive() && mon->attitude==ATT_HOSTILE
        && you.can_see(*mon) && grid_distance(you.pos(),mon->pos())<=range && seen(mon->pos());
}
void root(monster &mon,int duration) {
    if(!mon.is_stationary() && mon.res_constrict()<3)
        s.targets[mon.mid].root=you.elapsed_time+duration;
}
void charm_end(int at) {
    monster *mon=monster_by_mid(s.marked);
    if(mon && mon->alive()) {
        if(holo_campaign::active() && at>=s.five_end && mon->get_experience_level()>=you.experience_level && !mon->props.exists("holo_charm_survived")) {mon->props["holo_charm_survived"]=true;holo_campaign::grant(1);}
        mon->props.erase("holo_charmed");
        mon->attitude=ATT_HOSTILE;mon->foe=MHITYOU;mon->target=you.pos();mon->behaviour=BEH_SEEK;
        s.targets[mon->mid].immune=at+150;
    }
    s.secondary=0;s.marked=MID_NOBODY;s.five_ready=at+100;
}
coord_def direction(monster &mon) {
    coord_def d=mon.pos()-you.pos();return coord_def((d.x>0)-(d.x<0),(d.y>0)-(d.y<0));
}

}
int resource_action(monster *target)
{
    const int now=you.elapsed_time;
    if(is(god_id::suisei) && valid(target,6)) {
        const int stars=s.marked==target->mid && s.one_end>now?s.resource:0;
        bool pending=false;for(const auto &h:s.hazards) if(h.arm>now) pending=true;
        if(want(5) && !pending && stars>=3 && pay(6,10,120)) {
            hazard h;h.pos=target->pos();h.arm=now+30;h.kind=1;h.extra=stars;
            h.target=s.marked;s.hazards.push_back(h);s.resource=0;return 10;
        }
        if(want(3) && stars>=3 && valid(target,5) && pay(3,3,75)) {
            const coord_def d=direction(*target);
            for(mid_t id:enemies(you.pos(),5)) {
                monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;const coord_def delta=mon->pos()-you.pos();
                if(delta.x*d.y!=delta.y*d.x || delta.x*d.x+delta.y*d.y<=0) continue;
                if(roll_hit(*mon,20+s.inv,false)) {
                    const bool marked=mon->mid==s.marked;
                    hurt(*mon,roll_dice(2,8+s.inv/2)+(marked?5*stars:0));
                    if(marked) s.resource=0;
                }
            }
            return 10;
        }
    }
    if(is(god_id::choco)) {
        if(s.secondary<0) return 0;
        if(want(1) && valid(target) && (s.marked!=target->mid || s.one_end<=now) && pay(2,0)) {
            s.marked=target->mid;s.resource=1;s.one_end=now+10+100+3*s.inv;return 10;
        }
        if(target && target->mid==s.marked && s.one_end>now) {
            auto &t=s.targets[target->mid];const int stacks=s.resource;
            if(want(5) && stacks>=3 && now>=s.five_ready && now>=t.immune && pay(6,12,120)) {
                s.resource=0;s.one_end=0;
                if(mental_immune(*target)) {
                    t.weak_until=now+50;s.five_ready=t.weak_until+100;
                } else if(x_chance_in_y(max(15,min(85,50+2*s.inv+5*stacks-3*target->get_experience_level())),100)) {
                    // ENCH_CHARM also changes native summons; change only the selected actor.
                    if(holo_campaign::active())target->props["holo_charmed"]=true;
                    target->attitude=ATT_FRIENDLY;target->foe=MHITYOU;target->behaviour=BEH_SEEK;
                    s.five_end=now+10+max(20,min(80,40+2*s.inv-target->get_experience_level()));
                    s.secondary=-1;s.regen_fraction=0;s.last_event=-100;s.tertiary=0;
                } else { t.weak_until=now+30;s.five_ready=now+130; }
                return 10;
            }
            if(want(3) && stacks>=1 && valid(target,1) && now>=s.three_ready && pay(3,3,75)) {
                const bool ecstatic=t.root>now,credit=eligible(*target);
                const bool undead=bool(target->holiness()&MH_UNDEAD),nonliving=bool(target->holiness()&MH_NONLIVING);
                int raw=roll_dice(2,6+s.inv/3)+3*stacks;if(nonliving) raw/=2;
                const coord_def kiss_pos=target->pos();const int hp_before_kiss=you.hp;
                s.resource=0;const int dealt=hurt(*target,raw,BEAM_MAGIC,false,true);
                if(credit && !nonliving) heal(dealt*(ecstatic?60:40)/(undead?200:100));
                s.three_ready=now+40;holo_visual::choco_kiss(kiss_pos,dealt,you.hp-hp_before_kiss);return 10;
            }
        }
    }
    if(is(god_id::korone) && (valid(target,1) || (manual() && want(5)))) {
        if(want(5) && !five() && s.resource>=6 && now>=s.five_ready && pay(5,12,120)) {
            s.five_end=now+5+60+2*s.inv;s.five_ready=s.five_end+150;s.secondary=0;
            s.debt_next=s.five_end+10;s.debt_ticks=5;s.offence=s.five_end+50;return 5;
        }
        if(want(3) && valid(target,1) && (five() || (s.resource>=3 && (manual() || you.piety<120 || now<s.five_ready))) && now>=s.three_ready && pay(2,2,75)) {
            if(!five()) s.resource-=3;
            s.defence=1;begin_attack(*target);fight_melee(&you,target);
            const int aut=you.time_taken;const bool hit=ctx.primary;const mid_t id=target->mid;
            end_attack(aut);s.defence=0;target=monster_by_mid(id);
            if(hit && target && target->alive()) { s.marked=id;s.targets[id].slowed_until=now+aut+20+s.inv; }
            s.three_ready=now+aut+30;return max(1,aut);
        }
    }
    if(is(god_id::okayu)) {
        if(want(1) && s.resource<75 && now>=s.one_ready && (!policy() || (target && grid_distance(you.pos(),target->pos())>=3))) for(int slot=0;slot<ENDOFPACK;++slot) {
            item_def &food=you.inv[slot];
            if(food.defined() && food.base_type==OBJ_FOOD && can_eat(food,true)) {
                const int gain=food.sub_type==FOOD_RATION?20:8;
                if(eat_item(food)) {
                    s.resource=min(100,s.resource+gain);s.one_ready=now+110;++s.totals.casts;return 10;
                }
            }
        }
        if(want(5) && valid(target,3) && s.marked==target->mid && s.one_end>now && s.targets[s.marked].stacks>=2
            && s.resource>=25 && now>=s.five_ready
            && (!policy() || target->asleep() || s.targets[s.marked].stacks>=4)
            && policy_can_spend(5) && pay(5,8,120)) {
            auto &t=s.targets[s.marked];const bool sleeping=target->asleep();
            int raw=roll_dice(2,8+s.inv/2)+5*t.stacks;if(sleeping) raw=div_rand_round(raw*130,100);
            const bool credit=eligible(*target);s.resource-=25;t.stacks=0;s.one_end=0;
            hurt(*target,raw,BEAM_MAGIC,true,true);
            if(credit && !target->alive()) s.resource=min(100,s.resource+20);
            else if(target->alive() && target->asleep()) target->behaviour=BEH_SEEK;
            s.five_ready=now+60;return 10;
        }
        if(want(3) && valid(target) && (s.marked!=target->mid || s.one_end<=now) && s.resource>=10
            && (!policy() || (valid(target,3) && s.resource>=35 && you.magic_points>=8
                && !mental_immune(*target) && target->can_sleep()))
            && policy_can_spend(8) && pay(3,2,75)) {
            s.resource-=10;s.marked=target->mid;s.one_end=now+110+3*s.inv;
            auto &t=s.targets[s.marked];t.stacks=1;t.next=now+30;t.kind=0;return 10;
        }
    }
    if(is(god_id::lamy))return holo_lamy::action();
    return 0;
}
void resource_tick(int at)
{
    if(is(god_id::suisei)) {
        if(at>=s.one_end) s.resource=0;
        for(auto &h:s.hazards) if(h.arm && h.arm<=at) {
            holo_visual::comet_impact(h.pos);
            h.arm=0;const int raw=roll_dice(3,10+s.inv/2);
            for(mid_t id:enemies(h.pos,1,false,false)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) hurt(*mon,raw+(id==h.target?(h.end==-1?5*h.extra:8*h.extra):0)); }
            if(grid_distance(h.pos,you.pos())<=1 && line(h.pos,you.pos())) {
                const int before=you.hp;ouch(you.apply_ac(raw),KILLED_BY_WILD_MAGIC,you.mid,"comet impact");
                s.totals.self_damage+=max(0,before-you.hp);
            }
        }
    }
    if(is(god_id::choco)) {
        monster *mon=monster_by_mid(s.marked);
        if(s.secondary<0 && (!mon || !mon->alive() || at>=s.five_end)) charm_end(at);
        if(s.secondary>=0 && at>=s.one_end) s.resource=0;
    }
    if(is(god_id::korone)) {
        if(s.five_end && at>=s.five_end && s.secondary!=1) { s.resource=0;s.secondary=1;s.offence=s.five_end+50; }
        if(s.deferred>0 && at>=s.debt_next && s.debt_ticks>0 && at>=s.five_end) {
            const int payment=(s.deferred+s.debt_ticks-1)/s.debt_ticks;
            s.deferred-=payment;--s.debt_ticks;s.debt_next+=10;s.totals.deferred_paid+=payment;
            internal_damage=true;ouch(payment,KILLED_BY_WILD_MAGIC,you.mid,"deferred endurance damage");internal_damage=false;
        }
        if(at>=s.one_end && s.resource>0 && at>=s.five_end && at%10==0) --s.resource;
    }
    if(is(god_id::okayu)) {
        if(at%500==0) s.resource=max(0,s.resource-1);
        const int maximum=s.resource?4+s.inv/3+s.resource/20:0;s.shield=min(s.shield,maximum);
        if(passive() && at>=s.last_event) { s.shield=min(maximum,s.shield+1);s.last_event+=20; }
        monster *mon=monster_by_mid(s.marked);
        if(mon && mon->alive()) {
            auto &t=s.targets[s.marked];
            if(t.root && !mon->asleep()) {t.root=0;if(t.kind==2)t.kind=3;}
            if(t.root && at>=t.root) { if(mon->asleep()) mon->behaviour=BEH_SEEK;t.root=0; }
            if(at<s.one_end && at>=t.next) {
                t.next+=20;if(you.can_see(*mon)) t.stacks=min(4,t.stacks+1);
                if(t.stacks==4 && !t.kind) {
                    t.kind=1;
                    if(at>=t.immune) {
                        t.immune=at+100;
                        if(!mental_immune(*mon) && mon->can_sleep()
                            && x_chance_in_y(max(20,min(85,60+2*s.inv-3*mon->get_experience_level())),100)) {
                            mon->put_to_sleep(&you,0);t.root=at+20;t.kind=2;
                        }
                    }
                }
            }
        }
    }
    if(is(god_id::lamy))holo_lamy::tick(at);
}
void resource_after_attack(monster *target,int)
{
    const int now=you.elapsed_time;
    if(is(god_id::suisei) && ctx.damaged && target && target->alive()) {
        if(s.marked==MID_NOBODY || s.one_end<=now) { s.resource=0;s.marked=ctx.target; }
        if(s.marked==ctx.target) {
            const bool inherited=ctx.star_inheritance && s.resource==0 && target->attitude==ATT_HOSTILE;
            s.resource=min(3,s.resource+(inherited?2:1));s.one_end=now+100;
        }
    }
    if(is(god_id::choco) && ctx.damaged && s.secondary>=0 && target && target->alive()
        && target->mid==s.marked && s.one_end>now) {
        s.resource=min(5,s.resource+1);s.one_end=now+100+3*s.inv;
        auto &t=s.targets[s.marked];
        if(s.resource==5 && t.next<=now && !mental_immune(*target)) { root(*target,10);t.root=now+10;t.next=now+80; }
    }
    if(is(god_id::korone)) {
        if(passive() && ctx.eligible && ctx.damaged && ctx.kind==attack_kind::melee && now>=s.offence && !five()) {
            s.resource=min(6,s.resource+1);s.one_end=now+50;
        }
        if(five() && ctx.kind==attack_kind::melee && target && target->alive() && roll_hit(*target,20+s.inv))
            hurt(*target,roll_dice(1,6+s.inv/2));
    }

}
void resource_move(const coord_def &,bool) {}
void resource_kill(mid_t mid,int,bool direct,bool ordinary)
{
    if(is(god_id::suisei) && direct && ordinary && ctx.stars_before>0) {
        s.offence=roll_dice(1,3+4*ctx.stars_before);s.three_end=you.elapsed_time+30;
    }
    if(is(god_id::suisei) && s.marked==mid) { s.marked=MID_NOBODY;s.resource=0; }
    if(is(god_id::okayu) && direct) s.resource=min(100,s.resource+3);
    if(is(god_id::choco) && s.secondary<0 && s.marked==mid) charm_end(you.elapsed_time);
}
int resource_incoming(int damage,kill_method_type kind,mid_t source)
{
    const int now=you.elapsed_time;const monster *mon=monster_by_mid(source);
    const bool hostile=mon && eligible(*mon) && (kind==KILLED_BY_MONSTER || kind==KILLED_BY_BEAM);
    if(is(god_id::choco) && hostile && s.targets[source].weak_until>now) damage=div_rand_round(damage*80,100);
    if(is(god_id::korone)) {
        if(passive() && hostile && damage>=max(1,(you.hp_max*3+99)/100) && now>=s.proc_ready && now>=s.offence && !five()) {
            s.resource=min(6,s.resource+1);s.one_end=now+50;s.proc_ready=now+10;
        }
        if(five() && source!=you.mid && (kind==KILLED_BY_MONSTER || kind==KILLED_BY_BEAM)) {
            const int deferred=damage/4;s.deferred+=deferred;damage-=deferred;
        }
    }
    if(is(god_id::okayu) && passive() && hostile) {
        s.last_event=now+50;const int absorbed=min(s.shield,damage);
        s.shield-=absorbed;damage-=absorbed;s.totals.absorbed+=absorbed;
    }
    return damage;
}
void companion_damage(const actor *attacker,int damage)
{
    if(!is(god_id::choco) || s.secondary>=0 || !attacker || attacker->mid!=s.marked || damage<=0) return;
    const int bucket=you.elapsed_time/10;
    if(s.last_event!=bucket) { s.last_event=bucket;s.tertiary=0; }
    s.regen_fraction+=15*damage;const int wanted=min(3-s.tertiary,s.regen_fraction/100);
    s.regen_fraction%=100;s.tertiary+=wanted;heal(wanted);
}
void resource_contact(const actor *attacker,beam_type)
{
    if(is(god_id::okayu) && attacker && attacker->is_monster()) {
        const monster *mon=monster_by_mid(attacker->mid);
        if(mon && eligible(*mon)) s.last_event=you.elapsed_time+50;
    }
}
}

namespace holo_batch {
int manual_resource(monster *target) {
 if(!manual())return -1;
 const int now=you.elapsed_time;
 if(is(god_id::choco) && manual_tier==1) {
  if(s.secondary<0 || !valid(target,5) || !pay(2,0))return 0;
  if(s.marked!=target->mid || s.one_end<=now)s.resource=1;
  s.marked=target->mid;s.one_end=now+10+100+3*s.inv;
  return 10;
 }
 if(is(god_id::suisei)) {
  if(manual_tier==1) {
   if(!valid(target,6))return 0;
   if(s.marked!=target->mid){s.marked=target->mid;s.resource=0;s.one_end=now+110;}
   return 10;
  }
  if(manual_tier==5) {
   for(auto h:s.hazards)if(h.kind==1 && h.arm>now)return 0;
   if(!in_bounds(manual_aim) || !seen(manual_aim) || grd(manual_aim)!=DNGN_FLOOR || grid_distance(you.pos(),manual_aim)>6)return 0;
   if(!pay(6,10,120))return 0;
   hazard h;h.pos=manual_aim;h.arm=now+30;h.kind=1;
   monster *marked=monster_by_mid(s.marked);if(marked && marked->alive() && s.one_end>now && grid_distance(h.pos,marked->pos())<=1){h.target=s.marked;h.extra=s.resource;s.resource=0;}
   s.hazards.push_back(h);return 10;
  }
  if(manual_tier==3) {
   coord_def d=manual_aim-you.pos();d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
   if((!d.x&&!d.y) || !seen(manual_aim) || !pay(3,3,75))return 0;
   std::vector<mid_t> victims;for(monster_iterator mi;mi;++mi)if(mi->alive() && seen(mi->pos()) && grid_distance(you.pos(),mi->pos())<=5){auto delta=mi->pos()-you.pos();if(delta.x*d.y==delta.y*d.x && delta.x*d.x+delta.y*d.y>0)victims.push_back(mi->mid);}
   for(mid_t id:victims){monster *m=monster_by_mid(id);if(m && m->alive() && roll_hit(*m,20+s.inv,false)){bool marked=id==s.marked;int stars=marked && s.one_end>now?s.resource:0;hurt(*m,roll_dice(2,8+s.inv/2)+5*stars);if(marked)s.resource=0;}}
   return 10;
  }
  return 0;
 }
 // Eating uses the real inventory/food prompt, not the benchmark's first item.
 if(is(god_id::okayu) && manual_tier==1) {
  if(now<s.one_ready || s.resource>=100)return 0;
  return eat_food()?max(1,you.time_taken):0;
 }
 return -1;
}
}
