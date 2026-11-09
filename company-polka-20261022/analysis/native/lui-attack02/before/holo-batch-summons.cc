#include "AppHdr.h"
#include "holo-wrath.h"
#include "holo-visual.h"
#include "holo-campaign.h"
#include "holo-batch-internal.h"
#include <algorithm>
#include <stdexcept>
#include "act-iter.h"
#include "beam.h"
#include "env.h"
#include "fight.h"
#include "holocrawl.h"
#include "mgen-data.h"
#include "mon-death.h"
#include "mon-ench.h"
#include "mon-place.h"
#include "mon-util.h"
#include "player.h"
#include "terrain.h"
namespace holo_batch {
namespace {
companion *find(mid_t id) {
    if(!active()) return nullptr;
    for(auto &c:s.companions) if(c.mid==id) return &c;
    return nullptr;
}
void dismiss(companion &c) {
    monster *mon=monster_by_mid(c.mid);c.expires=0;
    if(mon && mon->alive()) monster_die(*mon,KILL_DISMISSED,NON_MONSTER,true);
}
std::vector<coord_def> empty_cells(const coord_def &origin,int radius) {
    std::vector<coord_def> cells;
    for(int r=1;r<=radius;++r) for(int dx=-r;dx<=r;++dx) for(int dy=-r;dy<=r;++dy) {
        const coord_def p=origin+coord_def(dx,dy);
        if(probe_preparing() && (p==you.pos()+coord_def(1,0) || p==you.pos()+coord_def(0,1) || p==you.pos()+coord_def(-1,0))) continue;
        if(max(abs(dx),abs(dy))==r && in_bounds(p) && !actor_at(p) && grd(p)==DNGN_FLOOR && seen(p)) cells.push_back(p);
    }
    return cells;
}
bool spawn(const coord_def &pos,int kind,int end,bool extra=false) {
    // Native rats supply a single ordinary physical melee attack and no spells/brands.
    // Flight, stationary behavior, stats and first-action scheduling are set explicitly below.
    mgen_data mg(MONS_RAT,BEH_FRIENDLY,pos,MHITNOT,MG_FORCE_PLACE);
    mg.extra_flags|=MF_NO_REWARD|MF_HARD_RESET;mg.summoner=&you;
    mg.mname=kind==1?"Holo rose":kind==2?"Holo fox image":"Holo hawk";
    monster *mon=create_monster(mg,false);if(!mon) return false;
    companion c;c.mid=mon->mid;c.kind=kind;c.expires=end;c.natural_end=end;c.extra=extra;c.next=you.elapsed_time+20;
    if(kind==3 && five()) c.shield=6+s.inv/3;
    s.companions.push_back(c);
    mon->hit_points=mon->max_hit_points=kind==2?1:12+s.inv;
    mon->speed=10;mon->speed_increment=0;
    if(kind==3) mon->add_ench(mon_enchant(ENCH_FLIGHT,1,&you,end-you.elapsed_time+10));
    ++s.totals.summons;return true;
}
int count() {
    int n=0;for(auto &c:s.companions) {
        const monster *mon=monster_by_mid(c.mid);if(mon && mon->alive() && c.expires>you.elapsed_time) ++n;
    } return n;
}
void foxfire(monster &fox,monster &target,int raw,bool automatic) {
    if(raw<=0 || !target.alive() || !line(fox.pos(),target.pos())) return;
    if(!automatic && !roll_hit_from(fox,target,20+s.inv)) return;
    hurt(target,raw/2,BEAM_FIRE,false,holo_campaign::active());
    if(target.alive()) hurt(target,raw-raw/2,BEAM_MISSILE,true,holo_campaign::active());
}
void deceive(companion &c) {
    monster *fox=monster_by_mid(c.mid);if(!fox) return;
    const int now=you.elapsed_time;
    for(mid_t id:enemies(fox->pos(),4)) {
        monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;auto &t=s.targets[id];
        if(t.immune>now || !mon->can_see(*fox) || (five() && s.performance_hits.count(id))) continue;
        if(five()) {
            std::vector<mid_t> images;
            for(const auto &image:s.companions) {
                const monster *other=monster_by_mid(image.mid);
                if(other && other->alive() && grid_distance(mon->pos(),other->pos())<=4 && mon->can_see(*other)) images.push_back(image.mid);
            }
            if(images.empty() || images[id%images.size()]!=c.mid) continue;
        }
        t.immune=now+40;if(five()) s.performance_hits.insert(id);
        if(x_chance_in_y(max(20,min(85,65+2*s.inv-3*mon->get_experience_level())),100)) {
            t.raven_hits.clear();t.raven_hits[c.mid]=now+30;
            mon->foe=fox->mindex();mon->target=fox->pos();mon->behaviour=BEH_SEEK;
        }
    }
}
int garden_radius(int at) { return s.three_end>at?3:you.piety>=75?2:1; }
bool garden(const coord_def &pos,int at) {
    return s.one_end>at && s.one_ready<=at && grd(pos)==DNGN_FLOOR
        && grid_distance(s.centre,pos)<=garden_radius(at) && line(s.centre,pos);
}
}
int summon_action(monster *target)
{
    const int now=you.elapsed_time;
    if(is(god_id::aki)) {
        if(want(1) && s.one_end<=now && target && you.can_see(*target) && policy_can_spend(3) && pay(3,0)) {
            for(auto &c:s.companions) dismiss(c);
            s.centre=target->pos();
            while(grid_distance(you.pos(),s.centre)>4) {
                const coord_def delta=s.centre-you.pos();s.centre-=coord_def((delta.x>0)-(delta.x<0),(delta.y>0)-(delta.y<0));
            }
            s.one_ready=now+20;s.one_end=s.one_ready+200+5*s.inv;
            s.last_event=s.one_ready;s.proc_ready=s.one_ready+20;return 10;
        }
        if(s.one_end>now && seen(s.centre) && grid_distance(you.pos(),s.centre)<=6) {
            if(want(5) && now>=s.five_ready && s.one_ready<=now
                && (!policy() || enemies(s.centre,3).size()>=2 || you.hp*5<=you.hp_max*3)
                && policy_can_spend(6) && pay(6,12,120)) {
                s.three_end=now+70;s.five_end=now+50;s.five_ready=now+160;
                for(mid_t id:enemies(s.centre,3)) {
                    monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;auto &t=s.targets[id];const int stacks=min(3,t.stacks+1);
                    if(grd(mon->pos())!=DNGN_FLOOR) continue;
                    if(holo_campaign::active() && stacks==3)mon->props["holo_bloom_three"]=true;
                    t.stacks=0;if(stacks==3 && mon->res_constrict()<3) t.root=now+20;
                    hurt(*mon,roll_dice(2,8+s.inv/2)+6*stacks);
                    if(mon->alive())mon->props.erase("holo_bloom_three");
                }
                return 10;
            }
            if(want(3) && count()<2) {
                std::vector<coord_def> cells;
                for(const coord_def &p:empty_cells(s.centre,garden_radius(now)))
                    if(garden(p,now) && grid_distance(you.pos(),p)<=6) cells.push_back(p);
                if(cells.size()>=2 && policy_can_spend(4) && pay(4,3,75)) {
                    spawn(cells[0],1,now+10+80+3*s.inv);spawn(cells[1],1,now+10+80+3*s.inv);return 10;
                }
            }
        }
    }
    if(is(god_id::fubuki)) {
        if(want(5) && !five() && now>=s.five_ready && pay(6,12,120)) {
            s.five_end=now+10+40+s.inv;s.five_ready=s.five_end+100;s.performance_hits.clear();
            for(auto &c:s.companions) c.expires=max(c.expires,s.five_end);
            const auto cells=empty_cells(you.pos(),3);
            std::vector<coord_def> arrivals;
            for(const coord_def &p:cells) {
                if(count()>=4) break;
                if(spawn(p,2,s.five_end,true))arrivals.push_back(p);
            }
            for(auto &c:s.companions) if(c.kind==2) deceive(c);
            holo_visual::fox_gather(arrivals);
            return 10;
        }
        if(want(1) && !five() && count()<(you.piety>=75?2:1)) {
            const auto cells=empty_cells(you.pos(),4);
            if(!cells.empty() && pay(3,1)) {
                spawn(cells.front(),2,now+10+60+3*s.inv);deceive(s.companions.back());return 10;
            }
        }
        if(want(3) && now>=s.three_ready && (manual() || you.hp*2<you.hp_max) && !you.no_tele(true,false)) {
            for(auto &c:s.companions) {
                monster *fox=monster_by_mid(c.mid);
                if(!fox || !fox->alive() || (manual() && fox->pos()!=manual_aim) || !seen(fox->pos()) || grid_distance(you.pos(),fox->pos())>5) continue;
                if(pay(3,3,75)) {
                    const coord_def old=you.pos(),dest=fox->pos();
                    // Remove the image from the grid while moving the player, preserving its lifetime.
                    mgrd(dest)=NON_MONSTER;you.move_to_pos(dest);fox->moveto(old);mgrd(old)=fox->mindex();
                    you.apply_location_effects(old);
                    std::vector<coord_def> hit_positions;
                    for(mid_t id:enemies(old,1)) {
                        monster *mon=monster_by_mid(id);
                        if(mon && mon->alive()) {
                            const int before_hp=mon->hit_points;const coord_def hit_pos=mon->pos();
                            foxfire(*fox,*mon,roll_dice(1,6+s.inv/3),true);
                            if(mon->hit_points<before_hp)hit_positions.push_back(hit_pos);
                        }
                    }
                    s.three_ready=now+5+30;holo_visual::fox_swap(old,dest,hit_positions);return 5;
                }
            }
        }
    }
    if(is(god_id::lui)) {
        if(want(5) && !five() && now>=s.five_ready
            && (!policy() || (enemies(you.pos(),LOS_DEFAULT_RANGE).size()>=2 && you.hp*5<=you.hp_max*4))
            && !probe_preparing() && !probe_is("no_ultimate") && policy_can_spend(7) && pay(7,14,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;
            for(auto &c:s.companions) {
                c.expires=max(c.expires,s.five_end);c.shield=6+s.inv/3;
            }
            for(const coord_def &p:empty_cells(you.pos(),2)) {
                if(count()>=6) break;
                spawn(p,3,s.five_end,true);
            }
            return 10;
        }
        if(want(1) && count()<(five()?6:you.piety>=75?3:2)
            && (!policy() || (count()<2 && target && (grid_distance(you.pos(),target->pos())>1 || count()==0)))
            && policy_can_spend(3)) {
            const auto cells=empty_cells(you.pos(),1);
            if(!cells.empty() && pay(3,0)) { spawn(cells.front(),3,now+10+120+4*s.inv,count()>=3);return 10; }
        }
        if(want(3) && target && target->alive() && seen(target->pos()) && grid_distance(you.pos(),target->pos())<=5 && now>=s.three_ready && !probe_is("no_command")) {
            bool possible=false;int participating=0,out_of_melee=0;
            for(auto &c:s.companions) {
                monster *raven=monster_by_mid(c.mid);
                if(raven && raven->alive() && grid_distance(raven->pos(),target->pos())<=4
                    && !empty_cells(target->pos(),1).empty() && line(raven->pos(),target->pos())) {
                    possible=true;++participating;
                    if(grid_distance(raven->pos(),target->pos())>1) ++out_of_melee;
                }
            }
            if(possible && (!policy() || (participating>=2 && out_of_melee>0))
                && policy_can_spend(3) && pay(3,3,75)) {
                for(auto &c:s.companions) {
                    monster *raven=monster_by_mid(c.mid);
                    if(!raven || !raven->alive() || !target->alive() || grid_distance(raven->pos(),target->pos())>4) continue;
                    const auto cells=empty_cells(target->pos(),1);
                    for(const coord_def &p:cells) if(line(raven->pos(),p)) {
                        raven->move_to_pos(p);raven->foe=target->mindex();raven->target=target->pos();
                        if(roll_hit_from(*raven,*target,21+s.inv)) {
                            summon_hit(raven,target);hurt(*target,roll_dice(1,5+s.inv/3)+3+s.inv/6);
                        }
                        c.next=now+20;raven->speed_increment=0;break;
                    }
                }
                s.three_ready=now+50;return 10;
            }
        }
    }
    return 0;
}
void summon_tick(int at)
{
    for(auto &c:s.companions) {
        monster *mon=monster_by_mid(c.mid);if(!mon || !mon->alive()) continue;
        if(c.expires<=at || ((is(god_id::lui)||is(god_id::fubuki)) && c.extra && at>=s.five_end)
            || (is(god_id::aki) && at>=s.one_end)) { dismiss(c);continue; }
        if(is(god_id::lui) && at>=s.five_end) { c.shield=0;if(c.natural_end<=at) { dismiss(c);continue; } }
        if(c.kind==1 && c.next<=at) {
            c.next+=s.five_end>at?10:15;
            mid_t best=MID_NOBODY;int stacks=-1;
            for(mid_t id:enemies(mon->pos(),s.five_end>at?5:4)) {
                monster *enemy=monster_by_mid(id);
                if(garden(enemy->pos(),at) && s.targets[id].stacks>stacks) { best=id;stacks=s.targets[id].stacks; }
            }
            monster *enemy=monster_by_mid(best);
            if(enemy) {
                bolt thorn;thorn.source=mon->pos();thorn.target=enemy->pos();thorn.range=s.five_end>at?5:4;
                thorn.flavour=thorn.real_flavour=BEAM_MISSILE;thorn.damage=dice_def(1,4+s.inv/3);
                thorn.hit=18+s.inv;thorn.name="rose thorn";thorn.set_agent(mon);thorn.thrower=KILL_MON_MISSILE;
                thorn.animate=false;thorn.fire();++s.totals.hits;
            }
        }
    }
    if(is(god_id::aki)) {
        if(s.one_end>at && at>=s.one_ready && at>=s.three_end) {
            for(mid_t id:enemies(s.centre,garden_radius(at),false,false)) {
                monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;if(!garden(mon->pos(),at)) continue;
                auto &t=s.targets[id];
                if(t.next<=at) { t.stacks=min(3,t.stacks+1);t.expires=at+60;t.next=at+10; }
            }
        }
        if(at>=s.proc_ready) {
            s.proc_ready+=20;
            for(auto &entry:s.targets) {
                auto &t=entry.second;monster *mon=monster_by_mid(entry.first);
                if(at>=t.expires) t.stacks=0;
                if(mon && mon->alive() && t.stacks>0) hurt(*mon,roll_dice(1,2+s.inv/6)+t.stacks);
            }
        }
    }
    if(is(god_id::fubuki)) for(auto &h:s.hazards) if(h.kind==31 && h.arm && h.arm<=at) {
        h.arm=0;monster *mon=monster_by_mid(h.target);if(mon && mon->alive()) {
            hurt(*mon,h.extra/2,BEAM_FIRE,false);if(mon->alive()) hurt(*mon,h.extra-h.extra/2);
        }
    }
}
void summon_after_attack(monster *target,int aut)
{
    if(!is(god_id::fubuki) || !target || !target->alive() || aut<=0) return;
    const mid_t id=target->mid;
    for(auto &c:s.companions) {
        target=monster_by_mid(id);monster *fox=monster_by_mid(c.mid);
        if(target && target->alive() && fox && fox->alive() && you.can_see(*target) && you.can_see(*fox)
            && grid_distance(fox->pos(),target->pos())<=(five()?5:4))
            foxfire(*fox,*target,div_rand_round(roll_dice(1,6+s.inv/3)*min(aut,10),10),false);
    }
}
void garden_entry(monster &mon,const coord_def &old)
{
    const int now=you.elapsed_time;
    if(!is(god_id::aki) || mon.attitude!=ATT_HOSTILE || !garden(mon.pos(),now)
        || garden(old,now) || s.three_end>now) return;
    auto &t=s.targets[mon.mid];
    if(t.next<=now) { t.stacks=min(3,t.stacks+1);t.expires=now+60;t.next=now+10; }
}
bool summon_before_monster(monster &mon)
{
    if(!holo_wrath::before_monster(mon))return false;
    if(!active()) return true;
    companion *c=find(mon.mid);
    if(c) {
        if(c->kind!=3 || c->next>you.elapsed_time) { mon.speed_increment=0;return false; }
        const auto ids=enemies(mon.pos(),LOS_DEFAULT_RANGE);
        if(!ids.empty()) { monster *enemy=monster_by_mid(ids.front());mon.foe=enemy->mindex();mon.target=enemy->pos();mon.behaviour=BEH_SEEK; }
        else if(grid_distance(mon.pos(),you.pos())<=2) { mon.speed_increment=0;return false; }
        return true;
    }
    if(is(god_id::fubuki)) {
        auto &t=s.targets[mon.mid];bool decoy=false;
        for(const auto &entry:t.raven_hits) {
            monster *fox=monster_by_mid(entry.first);
            if(entry.second>you.elapsed_time && fox && fox->alive() && mon.can_see(*fox)) {
                mon.foe=fox->mindex();mon.target=fox->pos();mon.behaviour=BEH_SEEK;decoy=true;break;
            }
        }
        if(!decoy) { mon.foe=MHITYOU;mon.target=you.pos(); }
    }
    return true;
}
int summon_energy(const monster &mon,energy_use_type kind,int base)
{
    const companion *c=find(mon.mid);
    if(c && c->kind==3) return kind==EUT_MOVE || kind==EUT_SWIM ? (five()?6:8):10;
    if(is(god_id::aki) && (kind==EUT_MOVE || kind==EUT_SWIM) && !mon.has_ench(ENCH_SLOW)) {
        const auto &t=s.targets[mon.mid];if(t.expires>you.elapsed_time) return (base*(100+15*t.stacks)+99)/100;
    }
    return base;
}
bool summon_stationary(const monster &mon) { const companion *c=find(mon.mid);return c && c->kind!=3; }
bool custom_monster(const monster &mon,int &hp,int &ac,int &ev,int &hit,int &damage)
{
    if(holo_wrath::custom_monster(mon,hp,ac,ev,hit,damage))return true;
    const companion *c=find(mon.mid);if(!c) return false;
    hp=c->kind==2?1:12+s.inv;ac=c->kind==1?2:c->kind==2?0:1;
    ev=c->kind==1?0:c->kind==2?10+s.inv/3:14+s.inv/3+(five()?4:0);
    hit=16+s.inv;damage=c->kind==3?5+s.inv/3:0;return true;
}
int companion_hurt(monster &mon,const actor *source,int damage)
{
    companion *c=find(mon.mid);if(!c || damage<=0) return damage;
    const int absorbed=min(c->shield,damage);c->shield-=absorbed;damage-=absorbed;s.totals.absorbed+=absorbed;
    if(c->kind==2 && five() && damage>0 && source && source->is_monster()
        && source->as_monster()->attitude==ATT_HOSTILE && grid_distance(source->pos(),mon.pos())<=5
        && line(source->pos(),mon.pos()) && s.targets[source->mid].next<=you.elapsed_time) {
        s.targets[source->mid].next=you.elapsed_time+10;
        hazard h;h.kind=31;h.target=source->mid;h.arm=you.elapsed_time+1;h.extra=roll_dice(1,6+s.inv/3);s.hazards.push_back(h);
    }
    return damage;
}
bool passable_companion(const actor *actor) { const companion *c=actor?find(actor->mid):nullptr;return holo_wrath::decoy(actor) || (c && c->kind==2); }
void expire_passable_at(const coord_def &pos) {
    if(holo_wrath::decoy(actor_at(pos))){holo_wrath::expire_at(pos);return;}
    monster *mon=monster_at(pos);companion *c=mon?find(mon->mid):nullptr;if(c && c->kind==2) dismiss(*c);
}
bool swap_companion(const coord_def &destination)
{
    monster *mon=monster_at(destination);const companion *c=mon?find(mon->mid):nullptr;
    if(!c || c->kind==2 || !adjacent(you.pos(),destination)
        || (c->kind==1 && (!garden(you.pos(),you.elapsed_time) || !garden(destination,you.elapsed_time)))) return false;
    const coord_def old=you.pos();mgrd(destination)=NON_MONSTER;
    you.move_to_pos(destination);mon->moveto(old);mgrd(old)=mon->mindex();
    you.apply_location_effects(old);mon->apply_location_effects(destination,KILL_MISC,NON_MONSTER);return true;
}
void summon_hit(const actor *source,const actor *target) {
    if(!is(god_id::lui) || you.piety<75 || !source || !target || !target->is_monster()) return;
    const companion *c=find(source->mid);if(c && c->kind==3) s.targets[target->mid].raven_hits[source->mid]=you.elapsed_time+30;
}
void validate_summons()
{
    const auto require=[](bool ok,const char *message) { if(!ok) throw std::runtime_error(std::string("Companion native fixture: ")+message); };
    holo_reset_validation_fixture();reset("fubuki",12);you.piety=60;
    require(summon_action(nullptr)==10 && count()==1,"single image does not spawn");
    monster *fox=monster_by_mid(s.companions.front().mid);
    require(fox && fox->hit_points==1 && fox->evasion()==14 && passable_companion(fox),"image has wrong native HP/EV/passability");
    const coord_def image=fox->pos();expire_passable_at(image);
    require(!monster_at(image) && count()==0,"walking through an image leaves an occupied cell");
    holo_reset_validation_fixture();reset("lui",12);
    require(summon_action(nullptr)==10 && count()==6,"army does not create six native actors");
    monster *raven=monster_by_mid(s.companions.front().mid);
    require(raven && raven->hit_points==24 && raven->armour_class()==1 && raven->evasion()==22
        && raven->airborne() && !eligible(*raven),"raven stats/flight/XP isolation are wrong");
    raven->speed_increment=10;you.elapsed_time=10;
    require(!summon_before_monster(*raven) && raven->speed_increment==0,"raven acts during its summoning turn");
    you.elapsed_time=20;require(summon_before_monster(*raven),"raven never becomes ready");
    require(monster_energy(*raven,EUT_MOVE,10)==6 && monster_energy(*raven,EUT_ATTACK,10)==10,"army accelerates attacks instead of movement");
    monster *enemy=nullptr;for(monster_iterator mi;mi;++mi) if(mi->attitude==ATT_HOSTILE) enemy=*mi;
    const int hp=raven->hit_points;raven->hurt(enemy,5);
    require(raven->hit_points==hp && s.companions.front().shield==5,"raven barrier misses native incoming HP damage");
    const coord_def player_old=you.pos(),raven_old=raven->pos();
    require(swap_companion(raven_old) && you.pos()==raven_old && raven->pos()==player_old
        && monster_at(player_old)==raven,"native companion swap corrupts occupancy");
    enemy->type=MONS_IRON_DRAGON;
    require(raven->move_to_pos(enemy->pos()+coord_def(1,1)),"zero-damage raven fixture landing is occupied");
    bool zero_raven=false;
    for(int attempt=0;attempt<30 && !zero_raven;++attempt) {
        s.targets[enemy->mid].raven_hits.clear();const int hp_before=enemy->hit_points;
        bool hit=false;fight_melee(raven,enemy,&hit);zero_raven=hit && enemy->hit_points==hp_before;
        if(zero_raven) require(s.targets[enemy->mid].raven_hits.count(raven->mid)==1,
            "native armour-zero raven hit fails to contribute distraction");
    }
    require(zero_raven,"raven-zero native fixture did not exercise its branch");
}
}

namespace holo_batch {
int manual_summon(monster *) {
 if(!manual())return -1;
 const int now=you.elapsed_time;
 if(is(god_id::aki) && manual_tier==1){
  if(!in_bounds(manual_aim) || !seen(manual_aim) || grd(manual_aim)!=DNGN_FLOOR || grid_distance(you.pos(),manual_aim)>4 || !pay(3,0))return 0;
  for(auto &c:s.companions)dismiss(c);
  s.centre=manual_aim;s.one_ready=now+20;s.one_end=s.one_ready+200+5*s.inv;s.last_event=s.one_ready;s.proc_ready=s.one_ready+20;return 10;
 }
 if(is(god_id::aki) && manual_tier==3){
  if(s.one_end<=now || !seen(s.centre) || grid_distance(you.pos(),s.centre)>6 || count()>=2 || manual_aim==manual_second)return 0;
  for(auto p:{manual_aim,manual_second})if(!in_bounds(p) || actor_at(p) || !seen(p) || !garden(p,now) || grid_distance(you.pos(),p)>6)return 0;
  int free=0;for(const monster &m:menv)if(!m.alive())++free;if(free<2 || !pay(4,3,75))return 0;
  spawn(manual_aim,1,now+10+80+3*s.inv);spawn(manual_second,1,now+10+80+3*s.inv);return 10;
 }
 if(is(god_id::fubuki) && manual_tier==1){
  if(five() || count()>=(you.piety>=75?2:1) || !in_bounds(manual_aim) || actor_at(manual_aim) || grd(manual_aim)!=DNGN_FLOOR || !seen(manual_aim) || grid_distance(you.pos(),manual_aim)>4)return 0;
  int free=0;for(const monster &m:menv)if(!m.alive())++free;if(!free || !pay(3,1))return 0;
  if(!spawn(manual_aim,2,now+10+60+3*s.inv))return 0;
  deceive(s.companions.back());return 10;
 }
 return -1;
}
}
