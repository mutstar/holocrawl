#include "AppHdr.h"
#include "holo-batch-internal.h"
#include "act-iter.h"
#include "env.h"
#include "fight.h"
#include "holocrawl.h"
#include "mon-util.h"
#include "mon-ench.h"
#include "player.h"
#include "terrain.h"

namespace holo_batch {
namespace {
bool in_shrine() {
    return s.one_end>you.elapsed_time && seen(s.centre)
        && grid_distance(s.centre,you.pos())<=(five()?3:2);
}
int radius() { return five()?3:2; }
int attention() {
    int n=0;
    for(mid_t id:enemies(you.pos(),LOS_DEFAULT_RANGE)) {
        const monster &mon=*monster_by_mid(id);
        if(eligible(mon) && !mon.asleep() && mon.foe==MHITYOU
            && mon.get_experience_level()>=max(1,(you.experience_level+2)/3)) ++n;
    }
    return min(5,n);
}
bool allowed_step(const coord_def &p) {
    return in_bounds(p) && !actor_at(p) && grd(p)==DNGN_FLOOR;
}
void sculpture_wave(const coord_def &direction) {
    std::set<coord_def> cells;
    for(int side=five()?-1:0;side<=(five()?1:0);++side) for(int r=1;r<=3;++r) {
        const coord_def p=you.pos()+direction*r+coord_def(-direction.y*side,direction.x*side);
        if(!in_bounds(p) || feat_is_solid(grd(p))) break;
        if(seen(p)) cells.insert(p);
    }
    for(mid_t id:enemies(you.pos(),4,true)) {
        monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
        if(!cells.count(mon->pos())) continue;
        hurt(*mon,roll_dice(five()?4:3,6+s.inv/3)+s.inv/2);
        if(mon->alive()) push(*mon,you.pos(),five()?2:1);
    }
}
}

int change_exhibit(int piece)
{
    if(!is(god_id::raden) || five() || piece<0 || piece>2 || piece==s.exhibit || !pay(1,0)) return 0;
    s.exhibit=piece;return 10;
}
int martial_action(monster *target)
{
    const int now=you.elapsed_time;
    if(is(god_id::miko)) {
        if(want(1) && (s.one_end<=now || manual()) && grd(you.pos())==DNGN_FLOOR && policy_can_spend(3) && pay(3,0)) {
            s.centre=you.pos();s.one_end=now+10+200+5*s.inv;s.last_event=now+30;s.regen_fraction=0;return 10;
        }
        if(want(5) && in_shrine() && !five() && now>=s.five_ready && (!policy() || you.hp*4<=you.hp_max*3)
            && !probe_is("shrine_only") && !probe_is("no_ultimate") && policy_can_spend(6) && pay(6,10,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+100;
            s.one_end=max(s.one_end,s.five_end);
            for(duration_type dur:{DUR_POISONING,DUR_CONF,DUR_SLOW,DUR_AFRAID,DUR_LIQUID_FLAMES,DUR_CORROSION})
                if(you.duration[dur]) { you.duration[dur]=0;break; }
            return 10;
        }
        bool boundary_target=false;
        if(policy()) for(mid_t id:enemies(s.centre,radius()))
            if(grid_distance(s.centre,monster_by_mid(id)->pos())==radius()) boundary_target=true;
        if(want(3) && in_shrine() && s.three_end<=now && (!policy() || boundary_target)
            && !probe_is("shrine_only") && !probe_is("no_fire") && policy_can_spend(3) && pay(3,3,75)) {
            s.three_end=now+10+50+2*s.inv;return 10;
        }
    }
    if(is(god_id::watame)) {
        if(want(5) && !five() && now>=s.five_ready && pay(6,15,120)) {
            s.five_end=now+5+80+2*s.inv;s.five_ready=s.five_end+300;s.offence=0;return 5;
        }
        if(want(3) && s.three_end<=now && now>=s.three_ready && pay(3,3,75)) {
            s.resource=3;s.three_end=now+5+60+s.inv;s.three_ready=s.three_end+30;return 5;
        }
    }
    if(is(god_id::vivi)) {
        if(want(5) && !five() && now>=s.five_ready && !probe_is("no_ultimate") && pay(6,12,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;return 10;
        }
        if(want(1) && !five() && s.one_end<=now && !probe_is("no_makeup") && pay(2,0)) {
            s.one_end=now+10+150+5*s.inv;return 10;
        }
        const auto victims=enemies(you.pos(),five()?3:2);
        if(want(3) && !victims.empty() && now>=s.three_ready && !probe_is("no_burst") && pay(3,4,75)) {
            const int percent=100+((five() || s.one_end>now)?10+s.inv/6:0)+(five()?5*attention():0);
            for(mid_t id:victims) {
                monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
                if(!mon || !mon->alive()) continue;
                hurt(*mon,div_rand_round(roll_dice(2,vivi_burst_sides())*percent,100),BEAM_MAGIC,false,true);
                if(mon->alive() && now>=s.targets[id].blind_ready && mons_can_be_blinded(mon->type)) {
                    ++s.totals.blind_attempts;
                    const bool rolled=x_chance_in_y(max(15,min(85,60+2*s.inv-3*mon->get_experience_level())),100);
                    if(rolled) {
                    const int duration=20+s.inv/2;
                    s.targets[id].blind_ready=now+duration+80;
                    if(!probe_is("no_blind")) {
                        mon->add_ench(mon_enchant(ENCH_BLIND,1,&you,duration));
                        ++s.totals.blind_successes;
                    }
                    }
                }
            }
            s.three_ready=now+50;return 10;
        }
    }
    if(is(god_id::ayame) && target && adjacent(you.pos(),target->pos())) {
        if(want(5) && !five() && now>=s.five_ready && pay(5,10,120)) {
            s.marked=target->mid;s.centre=you.pos();s.five_end=now+10+60+2*s.inv;
            s.one_end=s.five_end;s.five_ready=s.five_end+100;return 10;
        }
        if(want(3) && now>=s.three_ready && pay(3,3,75)) {
            s.three_ready=now+20;
            const mid_t id=target->mid;
            bool first_hit=false;
            begin_attack(*target);fight_melee(&you,target,&first_hit);
            const int delay=you.time_taken;end_attack(delay);
            target=monster_by_mid(id);
            if(target && target->alive()) {
                begin_attack(*target);ctx.double_hit=first_hit;
                // Suppress auxiliaries on every second swing, including a miss on the first.
                s.defence=1;fight_melee(&you,target);s.defence=0;end_attack(delay);
            }
            return max(1,delay);
        }
    }
    if(is(god_id::raden)) {
        if(want(5) && !five() && now>=s.five_ready && pay(6,12,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;return 10;
        }
        // The baseline policy exhibits painting; defensive pieces become available in the exhibition.
        const int shield_piece=2;
        if(want(3) && (!manual() || manual_option==2) && (five() || s.exhibit==2) && s.shield==0 && now>=s.rest[shield_piece] && pay(3,3,75)) {
            s.shield=five()?22+3*s.inv/2:14+s.inv;
            s.three_end=now+10+10*((five()?8:6)+s.inv/6);s.rest[2]=now+50;
            holo_reduce_poison_time(50);
            for(duration_type dur:{DUR_CONF,DUR_SLOW,DUR_AFRAID}) you.duration[dur]=(you.duration[dur]+1)/2;
            return 10;
        }
        if(want(3) && (!manual() || manual_option==0) && target && seen(target->pos()) && grid_distance(you.pos(),target->pos())<=5
            && (s.exhibit==0 || five()) && s.targets[target->mid].paint>0
            && now>=s.rest[0] && pay(3,3,75)) {
            const coord_def origin=target->pos(); const int stacks=s.targets[target->mid].paint;
            s.targets[target->mid].paint=0;s.rest[0]=now+10+40;
            const int raw=roll_dice(five()?3:2,8+s.inv/2)+6*stacks;
            for(mid_t id:enemies(origin,five()?2:1)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) hurt(*mon,raw); }
            if(grid_distance(origin,you.pos())<=(five()?2:1) && line(origin,you.pos())) {
                const int before=you.hp;
                ouch(you.apply_ac(raw),KILLED_BY_WILD_MAGIC,you.mid,"painting explosion");
                s.totals.self_damage+=max(0,before-you.hp);
            }
            return 10;
        }
        if(want(3) && (!manual() || manual_option==1) && (target || (manual() && manual_aim!=you.pos() && seen(manual_aim))) && (five() || s.exhibit==1) && now>=s.rest[1] && pay(3,3,75)) {
            coord_def d=(manual()?manual_aim:target->pos())-you.pos();d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
            sculpture_wave(d);s.rest[1]=now+10+40;return 10;
        }
    }
    if(is(god_id::hajime)) {
        const bool close_crowd=enemies(you.pos(),1).size()>=2;
        if(want(5) && !five() && now>=s.five_ready && (!policy() || policy_melee() || close_crowd)
            && policy_can_spend(6) && pay(6,12,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;return 10;
        }
        if(!target) return 0;
        const int distance=grid_distance(you.pos(),target->pos());
        if(want(3) && distance>=2 && distance<=3 && now>=s.three_ready && !you.caught()
            && (!policy() || policy_melee()) && policy_can_spend(3)) {
            coord_def position=you.pos(); std::vector<coord_def> route;
            if(manual() && !manual_positions.empty()) {
                const coord_def goal=manual_positions.front();
                if(!allowed_step(goal) || !seen(goal) || !adjacent(goal,target->pos()))return 0;
                if(adjacent(position,goal))route.push_back(goal);
                else for(int dx=-1;dx<=1 && route.empty();++dx)for(int dy=-1;dy<=1 && route.empty();++dy) {
                    const coord_def p=position+coord_def(dx,dy);
                    if((dx || dy) && allowed_step(p) && seen(p) && adjacent(p,goal))route={p,goal};
                }
                if(!route.empty())position=goal;
            }
            else for(int step=0;step<2 && !adjacent(position,target->pos());++step) {
                coord_def d=target->pos()-position;d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
                position+=d;if(!allowed_step(position)) { route.clear();break; }route.push_back(position);
            }
            if(!route.empty() && adjacent(position,target->pos()) && pay(3,3,75)) {
                const int p=s.resource;s.resource=0;
                for(coord_def destination:route) {
                    const coord_def old=you.pos();
                    if(!you.move_to_pos(destination)) break;
                    you.apply_location_effects(old);
                    if(you.hp<=0 || you.cannot_act() || you.caught()) return 10;
                }
                if(target->alive() && roll_hit(*target,20+s.inv+2*p)) hurt(*target,roll_dice(2,6+s.inv/3)+3*p);
                if(five()) for(mid_t id:enemies(you.pos(),1)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) hurt(*mon,roll_dice(2,4+s.inv/3)); }
                s.three_ready=now+10+30;return 10;
            }
        }
        // During the ultimate, orbit the target at normal movement cost when possible.
        if(!manual() && five() && adjacent(you.pos(),target->pos()) && !you.caught()) {
            for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
                coord_def p=you.pos()+coord_def(dx,dy);
                if((dx||dy) && allowed_step(p) && adjacent(p,target->pos())) {
                    const coord_def old=you.pos();you.move_to_pos(p);you.apply_location_effects(old);after_move(old,true);
                    return player_speed()*player_movement_speed()/10;
                }
            }
        }
    }
    return 0;
}

void martial_tick(int at)
{
    if(is(god_id::miko) && s.one_end>at && seen(s.centre)) {
        const bool inside=grid_distance(s.centre,you.pos())<=radius();
        while(s.last_event<=at) {
            if(inside) { s.regen_fraction+=12+s.inv;heal(s.regen_fraction/12);s.regen_fraction%=12; }
            s.last_event+=20;
        }
        if(s.three_end>at) for(mid_t id:enemies(s.centre,radius())) {
            monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
            if(!mon || !mon->alive()) continue;
            if(grid_distance(s.centre,mon->pos())==radius() && s.targets[id].next<=at) {
                hurt(*mon,roll_dice(1,5+s.inv/4),BEAM_FIRE,false);
                s.targets[id].next=at+10;
            }
        }
    }
    if(is(god_id::watame) && passive()) {
        s.regen_fraction+=(27+s.inv)*(s.five_end>at?3:1);
        heal(s.regen_fraction/90);s.regen_fraction%=90;
    }
    if(is(god_id::vivi) && s.five_end>at) {
        for(mid_t id:enemies(you.pos(),LOS_DEFAULT_RANGE)) {
            monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;
            if(mon->asleep()) mon->behaviour=BEH_SEEK;
            mon->foe=MHITYOU;mon->target=you.pos();
        }
    }
    if(is(god_id::hajime) && at>=s.one_end) s.resource=0;
    if(is(god_id::ayame)) {
        monster *mon=monster_by_mid(s.marked);
        if(!mon || !mon->alive() || s.one_end<=at) {
            if(s.five_end>at) { s.five_end=at;s.five_ready=at+100; }
            s.marked=MID_NOBODY;
        }
        else if(s.five_end>at && (grid_distance(s.centre,you.pos())>2 || grid_distance(s.centre,mon->pos())>2)) {
            s.five_end=at;s.five_ready=at+100;
        }
    }
    if(is(god_id::raden)) {
        if(at>=s.three_end) s.shield=0;
        for(auto &p:s.targets) if(p.second.paint_end<=at) p.second.paint=0;
    }
}
void martial_after_attack(monster *target,int)
{
    if(is(god_id::ayame) && ctx.kind!=attack_kind::melee && ctx.target!=s.marked && ctx.eligible) {
        if(five()) { s.five_end=you.elapsed_time;s.five_ready=you.elapsed_time+100; }
        s.marked=MID_NOBODY;s.one_end=0;
    }
    if(is(god_id::ayame) && ctx.kind==attack_kind::melee && target && target->alive() && target->attitude==ATT_HOSTILE) {
        if(s.marked!=ctx.target && five()) { s.five_end=you.elapsed_time;s.five_ready=you.elapsed_time+100; }
        s.marked=ctx.target;s.one_end=five()?s.five_end:you.elapsed_time+30;
    }
    if(is(god_id::raden) && ctx.damaged && target && target->alive()
        && (s.exhibit==0 || five()) && you.elapsed_time>=s.rest[0]) {
        auto &t=s.targets[ctx.target];
        if(t.paint>0) hurt(*target,roll_dice(1,2+s.inv/6),BEAM_MAGIC,false);
        if(target->alive()) { t.paint=min(3,t.paint+1);t.paint_end=you.elapsed_time+60; }
    }
}
void martial_move(const coord_def &old,bool voluntary)
{
    if(!is(god_id::hajime) || !voluntary || you.confused() || you.cannot_act() || old==you.pos()) return;
    for(mid_t id:enemies(you.pos(),1)) {
        const monster &mon=*monster_by_mid(id);
        if(eligible(mon) && grid_distance(old,mon.pos())<=2 && line(old,mon.pos())) {
            s.resource=min(3,s.resource+1);s.one_end=you.elapsed_time+30;break;
        }
    }
    if(five()) for(mid_t id:enemies(you.pos(),1)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) hurt(*mon,roll_dice(2,4+s.inv/3)); }
}
void martial_kill(mid_t mid,int,bool direct,bool ordinary)
{
    if(is(god_id::raden) && (passive() || five()) && direct && ordinary && (s.exhibit==2 || five())
        && you.elapsed_time>=s.rest[2] && you.elapsed_time>=s.proc_ready) {
        heal(2+s.inv/6);s.proc_ready=you.elapsed_time+20;
    }
    if(is(god_id::ayame) && five() && mid==s.marked) {
        if(direct && ordinary && ctx.kind==attack_kind::melee) {
            s.three_ready=you.elapsed_time;
            you.magic_points=min(you.max_magic_points,you.magic_points+3+s.inv/6);
        }
        s.five_end=you.elapsed_time;s.five_ready=you.elapsed_time+100;
    }
}
int martial_incoming(int damage,kill_method_type kind,mid_t source)
{
    const int now=you.elapsed_time;
    if(is(god_id::miko) && in_shrine() && five())
        damage=damage>0?max(1,div_rand_round(damage*(100-15-s.inv/3),100)):0;
    if(is(god_id::miko) && in_shrine() && you.piety>=75 && kind==KILLED_BY_BEAM) {
        const monster *mon=monster_by_mid(source);
        if(mon && grid_distance(s.centre,mon->pos())>radius())
            damage=damage>0?max(1,div_rand_round(damage*(90-s.inv/3),100)):0;
    }
    if(is(god_id::raden) && s.three_end>now && s.shield>0) {
        const int absorbed=min(damage,s.shield);damage-=absorbed;s.shield-=absorbed;s.totals.absorbed+=absorbed;
    }
    if(is(god_id::watame)) {
        if((kind==KILLED_BY_MONSTER || kind==KILLED_BY_BEAM) && s.three_end>now && s.resource>0) {
            const int absorbed=min(5+s.inv/3,damage*4/10);
            if(absorbed>0) { damage-=absorbed;--s.resource;s.totals.absorbed+=absorbed; }
            if(!s.resource) { s.three_end=now;s.three_ready=now+30; }
        }
        if(five() && !s.offence && damage>=you.hp && you.hp>0) {
            damage=you.hp-1;s.offence=1;s.tertiary=max(1,you.hp_max*15/100);++s.totals.procs;
        }
    }
    return damage;
}
}
