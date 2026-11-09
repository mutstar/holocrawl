#include "AppHdr.h"
#include "holo-visual.h"
#include "holo-campaign.h"
#include "holo-batch-internal.h"
#include <algorithm>
#include "act-iter.h"
#include "env.h"
#include "fight.h"
#include "holocrawl.h"
#include "mon-util.h"
#include "mapmark.h"
#include "player.h"
#include "terrain.h"
namespace holo_batch {
namespace {
bool water(const coord_def &pos,int at) {
    return in_bounds(pos) && seen(pos) && feat_is_water(grd(pos));
}
bool su_terrain(const coord_def &pos,terrain_change_type type) {
    for(map_marker *m:env.markers.get_markers_at(pos))
        if(m->get_type()==MAT_TERRAIN_CHANGE
           && static_cast<map_terrain_change_marker *>(m)->change_type==type) return true;
    return false;
}
void su_field() {
    const int remaining=s.five_end-you.elapsed_time;
    std::vector<coord_def> outside;
    for(map_marker *m:env.markers.get_all(MAT_TERRAIN_CHANGE))
        if(static_cast<map_terrain_change_marker *>(m)->change_type==TERRAIN_CHANGE_SU_FIELD
           && (remaining<=0 || grid_distance(you.pos(),m->pos)>2 || !seen(m->pos))) outside.push_back(m->pos);
    for(const auto &p:outside) revert_terrain_change(p,TERRAIN_CHANGE_SU_FIELD);
    if(remaining<=0)return;
    for(int dx=-2;dx<=2;++dx)for(int dy=-2;dy<=2;++dy) {
        const coord_def p=you.pos()+coord_def(dx,dy);
        if(!in_bounds(p) || !seen(p))continue;
        if((grd(p)==DNGN_FLOOR && !is_temp_terrain(p))
           || su_terrain(p,TERRAIN_CHANGE_SU_PUDDLE) || su_terrain(p,TERRAIN_CHANGE_SU_FIELD))
            temp_change_terrain(p,DNGN_SHALLOW_WATER,remaining,TERRAIN_CHANGE_SU_FIELD);
    }
}
// extra: 0=pressure trigger, 1=legacy delayed fuse, 130/150=boost percent.
int bomb_multiplier(const hazard &h) { return h.extra==1 || h.extra==150?150:h.extra==130?130:100; }
void explosion(const coord_def &origin,int dice,int at,const coord_def *limit=nullptr,int multiplier=100) {
    holo_visual::impact(origin,1,true);
    const int raw=roll_dice(dice,8+s.inv/3)*multiplier/100,fire=raw/2,fragment=raw-fire;
    std::vector<mid_t> victims;
    for(monster_iterator mi;mi;++mi) if(mi->alive() && grid_distance(origin,mi->pos())<=1
        && (!limit || grid_distance(*limit,mi->pos())<=3) && line(origin,mi->pos())) victims.push_back(mi->mid);
    for(mid_t id:victims) {
        monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;if(!mon || !mon->alive()) continue;
        hurt(*mon,fire,BEAM_FIRE,false,true);if(mon->alive()) hurt(*mon,fragment);
    }
    if(grid_distance(origin,you.pos())<=1 && (!limit || grid_distance(*limit,you.pos())<=3) && line(origin,you.pos())) {
        int damage=resist_adjust_damage(&you,BEAM_FIRE,fire)+you.apply_ac(fragment);
        if(you.piety>=75 && damage>0) damage=max(1,div_rand_round(damage*75,100));
        const int before=you.hp;ouch(damage,KILLED_BY_WILD_MAGIC,you.mid,"carrot explosion");
        s.totals.self_damage+=max(0,before-you.hp);
    }
    // Mark for this same logical instant; the caller drains chains without re-entering this vector.
    for(auto &h:s.hazards) if(h.kind==10 && h.end>at && grid_distance(origin,h.pos)<=1 && line(origin,h.pos))  {h.next=at;if(multiplier>100)h.extra=max(multiplier,bomb_multiplier(h));}
}
void drain_bombs(int at) {
    holo_campaign::bomb_scope campaign_bombs;
    // Resolve connected chains before dealing damage, so vector order cannot
    // make a neighbour explode unboosted or multiply the bonus repeatedly.
    for(auto &h:s.hazards) if(h.kind==10 && h.end>at && h.extra==0 && h.arm<=at) {
        const monster *m=monster_at(h.pos);
        if(m && m->attitude==ATT_HOSTILE && !m->airborne())h.next=at;
    }
    bool spread=true;
    while(spread) {
        spread=false;
        for(auto &h:s.hazards)if(h.kind==10 && h.end>at && h.next<=at)
            for(auto &n:s.hazards)if(n.kind==10 && n.end>at && grid_distance(h.pos,n.pos)<=1 && line(h.pos,n.pos)) {
                const int boost=max(bomb_multiplier(h),bomb_multiplier(n));
                if(n.next>at){n.next=at;spread=true;}
                if(boost>bomb_multiplier(h)){h.extra=boost;spread=true;}
                if(boost>bomb_multiplier(n)){n.extra=boost;spread=true;}
            }
    }
    bool again=true;
    while(again && !holo_benchmark_finished()) {
        again=false;
        for(size_t i=0;i<s.hazards.size();++i) {
            auto &h=s.hazards[i];if(h.kind!=10 || h.end<=at) continue;
            const monster *mon=monster_at(h.pos);
            if(h.next>at && !(h.extra==0 && h.arm<=at && mon && mon->attitude==ATT_HOSTILE && !mon->airborne())) continue;
            const coord_def origin=h.pos;h.end=0;h.next=0;
            explosion(origin,2,at,nullptr,bomb_multiplier(h));again=true;
        }
    }
}
bool qualifies(const monster &mon) {
    return mon.alive() && mon.attitude==ATT_HOSTILE && you.can_see(mon)
        && s.one_end>you.elapsed_time && grid_distance(s.centre,mon.pos())<=2 && line(s.centre,mon.pos());
}
}
int space_action(monster *target)
{
    if((!target || !target->alive()) && !manual()) return 0;
    const int now=you.elapsed_time;
    if(is(god_id::su)) {
        if(want(5) && !five() && now>=s.five_ready && pay(6,12,120)) {
            s.five_end=now+10+60+2*s.inv;s.five_ready=s.five_end+150;s.last_event=now+20;su_field();return 10;
        }
        if(want(3) && (target || (manual() && manual_aim!=you.pos())) && now>=s.three_ready && grid_distance(you.pos(),manual()?manual_aim:target->pos())<=5) {
            coord_def d=(manual()?manual_aim:target->pos())-you.pos();d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
            bool wide=five();std::set<coord_def> cells;
            for(int r=1;r<=5;++r) {
                const coord_def p=you.pos()+d*r;if(!in_bounds(p) || feat_is_solid(grd(p)) || !line(you.pos(),p)) break;
                wide|=water(p,now);
                cells.insert(p);
                if(wide) for(int side:{-1,1}) {
                    const coord_def q=p+coord_def(-d.y*side,d.x*side);
                    if(in_bounds(q) && seen(q)) cells.insert(q);
                }
            }
            std::vector<mid_t> victims;
            for(mid_t id:enemies(you.pos(),6,true)) if(cells.count(monster_by_mid(id)->pos())) victims.push_back(id);
            if((!victims.empty() || manual()) && pay(3,3,75)) {
                holo_campaign::wave_bonus(wide);
                for(mid_t id:victims) {
                    monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;hurt(*mon,roll_dice(2,7+s.inv/3)+(five()?3+s.inv/3:0),BEAM_MISSILE,true,true);
                    if(mon->alive()) for(int step=0;step<(five()?2:1);++step) if(!move_actor(*mon,mon->pos()+d)) break;
                }
                s.three_ready=now+40;return 10;
            }
        }
    }
    if(is(god_id::towa)) {
        coord_def aim=manual()?manual_aim:target->pos();
        while(!manual() && grid_distance(you.pos(),aim)>5) {
            const coord_def delta=aim-you.pos();aim-=coord_def((delta.x>0)-(delta.x<0),(delta.y>0)-(delta.y<0));
        }
        if(want(3) && s.one_end<=now && (manual() || grid_distance(aim,target->pos())<=2) && seen(aim) && pay(4,4,75)) {
            s.centre=aim;s.one_end=now+10+60+2*s.inv;s.resource=4;s.five_end=0;return 10;
        }
        if(want(5) && s.one_end>now && seen(s.centre) && grid_distance(you.pos(),s.centre)<=6
            && !five() && now>=s.five_ready && pay(6,12,120)) {
            s.five_end=now+5+50+2*s.inv;s.one_end=s.five_end;s.five_ready=s.five_end+100;s.resource=8;return 5;
        }
    }
    if(!manual() && is(god_id::pekora)) {
        bool safe_ultimate=true,safe_detonation=true;
        if(policy()) {
            for(int dx=-1;dx<=1;++dx)
                if(grid_distance(you.pos(),target->pos()+coord_def(dx,0))<=1) safe_ultimate=false;
            for(const auto &h:s.hazards)
                if(h.kind==10 && h.end>now && grid_distance(you.pos(),h.pos)<=1) safe_detonation=false;
        }
        if(now>=s.five_ready && grid_distance(you.pos(),target->pos())<=5 && safe_ultimate
            && policy_can_spend(7) && pay(7,14,120)) {
            s.centre=target->pos();int index=0;
            for(int dx=-1;dx<=1 && index<3;++dx) {
                const coord_def p=target->pos()+coord_def(dx,0);
                if(!in_bounds(p) || grd(p)!=DNGN_FLOOR || !seen(p)) continue;
                hazard h;h.pos=p;h.kind=11;h.arm=now+30+10*index++;h.end=h.arm+1;s.hazards.push_back(h);
            }
            s.five_ready=now+50+150;return 10;
        }
        int count=0;bool armed=false;
        for(const auto &h:s.hazards) if(h.kind==10 && h.end>now) {
            ++count;
            if(h.arm<=now && seen(h.pos) && grid_distance(h.pos,target->pos())<=1) armed=true;
        }
        if(armed && safe_detonation && policy_can_spend(2) && pay(2,2,75)) {
            for(auto &h:s.hazards) if(h.kind==10 && h.end>now && h.arm<=now && seen(h.pos)) {h.next=now;h.extra=max(130,bomb_multiplier(h));}
            drain_bombs(now);return 5;
        }
        if(count<(you.piety>=75?5:3)) {
            // Fixed policy plants in a visible empty cell next to the current enemy.
            for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
                const coord_def p=target->pos()+coord_def(dx,dy);
                if(!in_bounds(p) || actor_at(p) || grd(p)!=DNGN_FLOOR || !seen(p)
                    || grid_distance(you.pos(),p)>(you.piety>=75?5:3)) continue;
                if(policy() && grid_distance(you.pos(),p)<=1) continue;
                bool occupied=false;for(const auto &h:s.hazards) if(h.kind==10 && h.end>now && h.pos==p) occupied=true;
                if(!occupied && policy_can_spend(2) && pay(2,1)) {
                    hazard h;h.pos=p;h.kind=10;h.arm=now+20;h.end=h.arm+200;h.next=h.end+1;s.hazards.push_back(h);return 5;
                }
            }
        }
    }
    return 0;
}
int policy_dodge()
{
    if(!policy() || !is(god_id::pekora) || you.cannot_act() || you.cannot_move() || you.caught()) return 0;
    const int now=you.elapsed_time;
    const auto danger=[&](const coord_def &p) {
        int n=0;
        for(const auto &h:s.hazards) if(h.end>now && grid_distance(p,h.pos)<=1 && line(h.pos,p)
            && ((h.kind==11 && h.arm>0 && h.arm<=now+10)
                || (h.kind==10 && (h.arm<=now+10 || h.next<=now+10)))) ++n;
        return n;
    };
    if(!danger(you.pos())) return 0;
    coord_def best=you.pos();int best_exposure=1000;
    for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
        const coord_def p=you.pos()+coord_def(dx,dy);
        if((!dx&&!dy) || !in_bounds(p) || grd(p)!=DNGN_FLOOR || actor_at(p) || danger(p)) continue;
        const int exposure=enemies(p,1).size();
        if(exposure<best_exposure) { best=p;best_exposure=exposure; }
    }
    if(best==you.pos()) return 0;
    const coord_def old=you.pos();
    if(!you.move_to_pos(best)) return 0;
    you.apply_location_effects(old);after_move(old,true);
    return player_speed()*player_movement_speed()/10;
}
void space_tick(int at)
{
    holo_campaign::bomb_scope campaign_bombs;
    if(is(god_id::su) && s.five_end>at && s.last_event<=at) {
        s.last_event+=10;
        for(mid_t id:enemies(you.pos(),2)) {
            monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;if(water(mon->pos(),at)) hurt(*mon,roll_dice(2,3+s.inv/6));
        }
    }
    if(!manual() && is(god_id::pekora)) {
        // Expiry wins ties; delayed bombs and chains may explode without player LOS.
        for(size_t i=0;i<s.hazards.size();++i) {
            auto &h=s.hazards[i];if(h.kind==11 && h.arm && h.arm<=at) {
                const coord_def pos=h.pos;h.arm=0;explosion(pos,3,at,&s.centre);
            }
        }
        drain_bombs(at);
        if(holo_campaign::active())for(auto &h:s.hazards)if(h.kind==10 && h.end<=at){h.end=0;h.arm=0;}
    }
    if(is(god_id::towa)) {
        if(at>=s.one_end) { s.candidates.clear();return; }
        const int bucket=at/10;
        if(s.last_event!=bucket) { s.last_event=bucket;s.secondary=0;s.performance_hits.clear(); }
        for(mid_t id:enemies(you.pos(),LOS_DEFAULT_RANGE)) {
            if(!s.candidates.count(id) || s.performance_hits.count(id) || s.resource<=0
                || s.secondary>=(s.five_end>at?2:1)) continue;
            monster *mon=monster_by_mid(id);if(!mon || !mon->alive()) continue;if(!qualifies(*mon)) continue;
            --s.resource;++s.secondary;s.performance_hits.insert(id);
            const bool hit=roll_hit(*mon,22+s.inv);
            holo_visual::towa_support(s.centre,mon->pos());
            if(hit) {
                hurt(*mon,roll_dice(2,5+s.inv/3));
                if(mon->alive()) s.targets[id].slowed_until=at+20;
            }
        }
        s.candidates.clear();
    }
}
void space_after_attack(monster *,int)
{
    if(!is(god_id::su) || !ctx.damaged) return;
    const auto p=ctx.position;
    if(!((grd(p)==DNGN_FLOOR && !is_temp_terrain(p))
         || su_terrain(p,TERRAIN_CHANGE_SU_PUDDLE) || su_terrain(p,TERRAIN_CHANGE_SU_FIELD))) return;
    s.hazards.erase(std::remove_if(s.hazards.begin(),s.hazards.end(),[](const hazard &h){return h.pos==ctx.position || h.end<=you.elapsed_time;}),s.hazards.end());
    if(s.hazards.size()>=12) {
        revert_terrain_change(s.hazards.front().pos,TERRAIN_CHANGE_SU_PUDDLE);
        s.hazards.erase(s.hazards.begin());
    }
    hazard h;h.pos=ctx.position;h.kind=20;h.end=you.elapsed_time+50+s.inv;s.hazards.push_back(h);
    temp_change_terrain(p,DNGN_SHALLOW_WATER,50+s.inv,TERRAIN_CHANGE_SU_PUDDLE);
}
void space_move(const coord_def &,bool) { if(is(god_id::su) && five())su_field(); }
void space_monster(monster &mon,const coord_def &old)
{
    holo_campaign::slime_moved(mon,old);
    garden_entry(mon,old);
    if(is(god_id::pekora) && old!=mon.pos()) drain_bombs(you.elapsed_time);
    if(is(god_id::towa) && old!=mon.pos() && qualifies(mon)) s.candidates.insert(mon.mid);
    if(is(god_id::towa) && old!=mon.pos()) s.targets[mon.mid].slowed_until=0;
    if(is(god_id::ayame) && five() && mon.mid!=s.marked && mon.attitude==ATT_HOSTILE
        && adjacent(old,mon.pos()) && grid_distance(s.centre,old)>2
        && grid_distance(s.centre,mon.pos())<=2 && s.targets[mon.mid].next<=you.elapsed_time) {
        mon.speed_increment-=(20*mon.speed+9)/10;s.targets[mon.mid].next=you.elapsed_time+30;
    }
    if(is(god_id::miko) && s.one_end>you.elapsed_time && s.three_end>you.elapsed_time) {
        const int radius=five()?3:you.piety>=75?2:1;
        if(grid_distance(s.centre,mon.pos())==radius && grid_distance(s.centre,old)!=radius
            && s.targets[mon.mid].next<=you.elapsed_time) {
            hurt(mon,roll_dice(1,5+s.inv/4),BEAM_FIRE,false);s.targets[mon.mid].next=you.elapsed_time+10;
        }
    }
}
void space_attempt(const actor *attacker,const actor *defender)
{
    if(!active() || !attacker || !defender || !defender->is_player() || !attacker->is_monster()) return;
    if(is(god_id::okayu)) s.last_event=you.elapsed_time+50;
    if(is(god_id::towa) && qualifies(*attacker->as_monster())) s.candidates.insert(attacker->mid);
}
int space_energy(const monster &mon,energy_use_type kind,int base)
{
    if(kind!=EUT_MOVE && kind!=EUT_SWIM) return base;
    int percent=100;
    if(is(god_id::towa) && s.targets[mon.mid].slowed_until>you.elapsed_time) percent=150;
    if(mon.has_ench(ENCH_SLOW)) return base;
    return (base*percent+99)/100;
}
}

namespace holo_batch {
int manual_space(monster *) {
 if(!manual() || !is(god_id::pekora))return -1;
 const int now=you.elapsed_time;
 if(manual_tier==-1){for(auto &h:s.hazards)if(h.kind==10 && h.end>now && h.pos==manual_aim && seen(h.pos)){h.end=0;return 10;}return 0;}
 if(manual_tier==1){
  int count=0;for(auto h:s.hazards)if(h.kind==10 && h.end>now){++count;if(h.pos==manual_aim)return 0;}
  if(count>=(you.piety>=75?5:3) || !in_bounds(manual_aim) || actor_at(manual_aim) || grd(manual_aim)!=DNGN_FLOOR || !seen(manual_aim) || grid_distance(you.pos(),manual_aim)>(you.piety>=75?5:3) || !pay(2,1))return 0;
  hazard h;h.pos=manual_aim;h.kind=10;h.arm=now+20;h.end=h.arm+200;h.next=h.end+1;s.hazards.push_back(h);return 5;
 }
 if(manual_tier==3){
  std::vector<size_t> selected;
  std::set<coord_def> points(manual_positions.begin(),manual_positions.end());
  if(points.empty())points.insert(manual_aim);
  if(points.size()>5)return 0;
  for(size_t i=0;i<s.hazards.size();++i){const auto &h=s.hazards[i];if(h.kind==10 && h.end>now && h.arm<=now && seen(h.pos) && points.count(h.pos) && (!manual_option || h.extra==0))selected.push_back(i);}
  if(selected.size()!=points.size())return 0;
  if(selected.empty() || !pay(2,2,75))return 0;
  for(size_t i:selected){auto &h=s.hazards[i];if(manual_option){h.next=now+25;h.extra=150;}else {h.next=now;h.extra=max(130,bomb_multiplier(h));}}
  if(!manual_option)drain_bombs(now);
  return 5;
 }
 if(manual_tier==5){
  if(now<s.five_ready || !in_bounds(manual_aim) || !seen(manual_aim) || grd(manual_aim)!=DNGN_FLOOR || grid_distance(you.pos(),manual_aim)>5 || manual_positions.size()!=3)return 0;
  std::set<coord_def> unique;
  for(auto p:manual_positions)if(!in_bounds(p) || !seen(p) || grd(p)!=DNGN_FLOOR || grid_distance(p,manual_aim)>3 || !unique.insert(p).second)return 0;
  if(!pay(7,14,120))return 0;
  s.centre=manual_aim;
  int index=0;for(auto p:manual_positions){hazard h;h.pos=p;h.kind=11;h.arm=now+30+10*index++;h.end=h.arm+1;s.hazards.push_back(h);}s.five_ready=now+200;return 10;
 }
 return 0;
}
}
