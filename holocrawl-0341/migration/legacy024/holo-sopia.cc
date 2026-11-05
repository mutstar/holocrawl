#include "AppHdr.h"
#include "holo-campaign.h"
#include <sstream>
#include "holo-sopia.h"

#include <algorithm>
#include <map>
#include <stdexcept>
#include <vector>

#include "act-iter.h"
#include "env.h"
#include "holocrawl.h"
#include "los.h"
#include "mon-util.h"
#include "mon-tentacle.h"
#include "player.h"
#include "terrain.h"
#include "traps.h"

namespace holo_sopia {
namespace {
bool enabled=false, ring_only=false, field=false, big=false;
int inv=0, ring_end=0, ring_next=0, field_end=0, field_next=0;
int charge=0, charge_next=0, big_ready=0;
coord_def centre;
std::map<mid_t,int> pull_ready;
metrics counters;

bool clear_line(const coord_def &a,const coord_def &b)
{
    // Native find_ray intentionally rejects a zero-length ray.
    return a==b || exists_ray(a,b,opc_solid_see);
}

bool visible(const coord_def &p)
{
    return you.see_cell(p) && clear_line(you.pos(),p);
}

std::vector<mid_t> targets(const coord_def &origin, int radius, bool far_first=false)
{
    std::vector<mid_t> result;
    for (monster_iterator mi; mi; ++mi)
        if (mi->alive() && mi->attitude==ATT_HOSTILE
            && grid_distance(origin,mi->pos())<=radius && you.can_see(**mi) && visible(mi->pos())
            && clear_line(origin,mi->pos()))
            result.push_back(mi->mid);
    std::sort(result.begin(),result.end(),[&](mid_t a,mid_t b) {
        const monster *ma=monster_by_mid(a), *mb=monster_by_mid(b);
        const int da=grid_distance(origin,ma->pos()), db=grid_distance(origin,mb->pos());
        if (da!=db)
            return far_first ? da>db : da<db;
        if (ma->pos().x!=mb->pos().x)
            return ma->pos().x<mb->pos().x;
        return ma->pos().y<mb->pos().y;
    });
    return result;
}

bool movable(const monster &mon)
{
    return !mon.is_stationary() && !mons_is_tentacle_or_tentacle_segment(mon.type);
}

bool legal(const monster &mon,const coord_def &p)
{
    return in_bounds(p) && !actor_at(p) && !trap_at(p)
        && mon.can_pass_through(p) && mon.is_habitable(p);
}

bool relocate(monster &mon,const coord_def &p)
{
    const coord_def old=mon.pos();
    if (!legal(mon,p) || !mon.move_to_pos(p))
        return false;
    mon.apply_location_effects(old,KILL_YOU,MHITYOU);
    return true;
}

bool pull_one(monster &mon)
{
    if (!movable(mon))
        return false;
    const int distance=grid_distance(centre,mon.pos());
    // Fixed coordinate order, no extra path RNG and no occupied-centre collision.
    for (int x=mon.pos().x-1;x<=mon.pos().x+1;++x)
        for (int y=mon.pos().y-1;y<=mon.pos().y+1;++y)
        {
            const coord_def p(x,y);
            if (grid_distance(centre,p)<distance && relocate(mon,p))
                return true;
        }
    return false;
}

void damage(monster &mon,int raw,bool direct=true)
{
    holo_campaign::damage_scope campaign_damage(direct);
    const int dealt=mon.apply_ac(raw);
    counters.damage+=mon.hurt(&you,dealt,BEAM_MISSILE);
}

void end_field(int when)
{
    if (big)
        big_ready=when+150;
    field=big=false;
    charge=0;
}

bool cast_ring()
{
    if (you.piety<30 || you.magic_points<3)
        return false;
    you.magic_points-=3;
    const int complete=you.elapsed_time+10;
    if (!ring_end || you.elapsed_time>=ring_end)
        ring_next=complete+10;
    ring_end=complete+100+4*inv;
    ++counters.ring_casts;
    return true;
}

bool cast_field(bool empower,const coord_def &requested=you.pos())
{
    const int now=you.elapsed_time;
    if (big || you.piety<(empower ? 120 : 75)
        || you.magic_points<(empower ? 7 : 3) || (empower && now<big_ready))
        return false;
    const bool upgrade=empower && field;
    const coord_def pos=upgrade ? centre : requested;
    if ((!upgrade && grid_distance(you.pos(),pos)>4) || !visible(pos) || grd(pos)!=DNGN_FLOOR)
        return false;
    you.magic_points-=empower ? 7 : 3;
    you.piety-=empower ? 14 : 3;
    centre=pos;
    field=true;
    big=empower;
    field_end=now+10+60+2*inv;
    if (!upgrade)
        field_next=now+10+20;
    if (empower)
    {
        charge=0;
        charge_next=now+10+20;
        ++counters.big_casts;
    }
    else
        ++counters.field_casts;
    return true;
}

bool detonate()
{
    const int now=you.elapsed_time;
    if (!field || !big || now>=field_end || charge<1
        || !visible(centre) || grid_distance(you.pos(),centre)>6)
        return false;
    const int c=charge;
    const coord_def origin=centre;
    holo_visual::impact(origin,2);
    const auto victims=targets(origin,2,true);
    end_field(now);
    ++counters.detonations;
    for (mid_t id:victims)
    {
        monster *mon=monster_by_mid(id);
        if (!mon || !mon->alive())
            continue;
        damage(*mon,roll_dice(3,8+inv/3)+6*c);
        mon=monster_by_mid(id);
        if (!mon || !mon->alive() || !movable(*mon))
            continue;
        coord_def delta=mon->pos()-origin;
        if (!delta.x && !delta.y)
            delta=mon->pos()-you.pos();
        delta.x=(delta.x>0)-(delta.x<0);
        delta.y=(delta.y>0)-(delta.y<0);
        for (int step=0;step<2 && mon->alive();++step)
            if (!relocate(*mon,mon->pos()+delta))
                break;
    }
    return true;
}
}

void reset(bool active,int invocation,bool only_ring)
{
    enabled=active;
    inv=invocation;
    ring_only=only_ring;
    ring_end=ring_next=field_end=field_next=charge_next=big_ready=charge=0;
    field=big=false;
    pull_ready.clear();
    counters=metrics();
}

int choose_action(const coord_def *preferred)
{
    if (!enabled)
        return 0;
    const int now=you.elapsed_time;
    if (big && charge>=1 && (charge>=3 || field_end-now<=20) && detonate())
        return 10;
    const coord_def aim=preferred?*preferred:you.pos();
    if ((!preferred || grid_distance(aim,you.pos())<=1) && (!ring_end || now>=ring_end) && cast_ring())
        return 10;
    if (!ring_only && !big && now>=big_ready && cast_field(true,aim))
        return 10;
    if (!ring_only && !field && cast_field(false,aim))
        return 10;
    return 0;
}

void advance(int now)
{
    if (!enabled || holo_benchmark_finished())
        return;
    // Like native duration/cloud processing, positions are sampled at the
    // post-monster world phase. Multiple elapsed ticks are never collapsed.
    for (;;)
    {
        int at=INT_MAX;
        if (ring_end)
            at=min(at,min(ring_end,ring_next));
        if (field)
            at=min(at,min(field_end,field_next));
        if (big)
            at=min(at,charge_next);
        if (at>now)
            break;
        // Expiry wins exact-time ties. Gravity then ring on shared ticks.
        if (ring_end && at>=ring_end)
            ring_end=0;
        if (field && at>=field_end)
            end_field(at);
        if (big && at==charge_next)
        {
            charge=min(3,charge+1);
            charge_next+=20;
        }
        if (field && at==field_next)
        {
            field_next+=20;
            ++counters.field_ticks;
            if (visible(centre))
                for (mid_t id:targets(centre,big ? 3 : 2))
                {
                    monster *mon=monster_by_mid(id);
                    if (!mon || !mon->alive())
                        continue;
                    ++counters.field_hits;
                    damage(*mon,roll_dice(1,4+inv/3),false);
                    mon=monster_by_mid(id);
                    if (!mon || !mon->alive() || pull_ready[id]>at)
                        continue;
                    pull_ready[id]=at+20;
                    ++counters.pull_attempts;
                    const int chance=max(15,min(90,65+2*inv-3*mon->get_experience_level()));
                    if (x_chance_in_y(chance,100) && pull_one(*mon))
                    { ++counters.pulls;holo_campaign::pulled(mon->mid); }
                }
        }
        if (ring_end && at==ring_next)
        {
            ring_next+=10;
            ++counters.ring_ticks;
            for (mid_t id:targets(you.pos(),1))
            {
                monster *mon=monster_by_mid(id);
                if (mon && mon->alive())
                {
                    ++counters.ring_hits;
                    damage(*mon,roll_dice(1,4+inv/3));
                }
            }
        }
    }
}

const metrics &get_metrics() { return counters; }

void validate()
{
    const auto require=[](bool ok,const char *message) {
        if (!ok)
            throw std::runtime_error(string("Sopia validation: ")+message);
    };
    monster *mon=nullptr;
    for (monster_iterator mi;mi;++mi)
        if (mi->alive()) { mon=*mi; break; }
    require(mon!=nullptr,"native monster fixture required");
    mon->hit_points=mon->max_hit_points=10000;
    you.elapsed_time=0;
    reset(true,12);
    require(cast_ring(),"ring cast");
    advance(19); require(counters.ring_ticks==0,"no immediate ring tick");
    advance(20); require(counters.ring_ticks==1,"first tick at completion plus ten aut");
    advance(25); require(counters.ring_ticks==1,"five aut does not add a tick");
    advance(40); require(counters.ring_ticks==3,"all elapsed ten-aut ticks retained");
    you.elapsed_time=40;
    require(cast_ring(),"ring refresh");
    advance(50); require(counters.ring_ticks==4,"refresh must preserve tick phase");
    reset(true,0);
    you.elapsed_time=0;
    you.magic_points=22;
    require(cast_ring(),"expiry fixture cast");
    advance(110); require(counters.ring_ticks==9 && ring_end==0,"expiry before same-time tick");
    reset(true,12);
    you.elapsed_time=0;
    you.magic_points=22;
    you.piety=180;
    require(cast_field(true) && !detonate(),"C0 cannot detonate");
    advance(30); require(charge==1,"first charge at completion plus twenty aut");
    advance(70); require(charge==3,"charge capped at three");
    advance(94); require(!field && charge==0 && big_ready==244,"expiry has no explosion and starts cooldown");
    require(counters.detonations==0,"natural expiry does not explode");
    reset(true,12);
    centre=you.pos();
    mon->move_to_pos(you.pos()+coord_def(2,0));
    const int energy=mon->speed_increment;
    require(pull_one(*mon) && grid_distance(centre,mon->pos())==1
            && mon->speed_increment==energy,"legal pull changes position without consuming monster energy");
    require(!pull_one(*mon),"occupied player centre cannot be entered");
    mon->move_to_pos(you.pos()+coord_def(2,0));
    for (int y=you.pos().y-1;y<=you.pos().y+1;++y)
        grd[you.pos().x+1][y]=DNGN_ROCK_WALL;
    require(!pull_one(*mon),"no pulling through blocked destination cells");
    for (int y=you.pos().y-1;y<=you.pos().y+1;++y)
        grd[you.pos().x+1][y]=DNGN_FLOOR;
    los_changed();
    const monster_type original_type=mon->type;
    mon->type=MONS_OKLOB_PLANT;
    require(!movable(*mon) && !pull_one(*mon),"stationary monsters resist movement");
    reset(true,12);
    you.elapsed_time=0;
    you.magic_points=22;
    you.piety=180;
    require(cast_field(false),"ordinary field cast");
    advance(30);
    require(counters.field_hits==1 && counters.pulls==0,"stationary targets still take compression hits");
    mon->type=original_type;
    reset(true,12);
    you.elapsed_time=0;
    you.magic_points=22;
    you.piety=180;
    const int centre_hp=mon->hit_points;
    require(cast_field(false,mon->pos()),"off-player fixed field centre");
    advance(30);
    require(counters.field_hits==1 && mon->hit_points<centre_hp,
            "targets on the exact field centre still take damage");
    mon->move_to_pos(you.pos()+coord_def(1,0));
    mon->attitude=ATT_FRIENDLY;
    reset(true,12);
    you.elapsed_time=0;
    you.magic_points=22;
    const int friendly_hp=mon->hit_points;
    require(cast_ring(),"friendly exclusion fixture");
    advance(20);
    require(counters.ring_hits==0 && mon->hit_points==friendly_hp,"ring excludes allies");
    mon->attitude=ATT_HOSTILE;
    reset(true,12);
    you.elapsed_time=0;
    you.magic_points=22;
    you.piety=180;
    require(cast_field(true),"detonation fixture cast");
    advance(70);
    you.elapsed_time=70;
    const int mp_before=you.magic_points, piety_before=you.piety;
    require(detonate() && counters.detonations==1 && !field && big_ready==220,
            "manual detonation consumes field and starts cooldown");
    require(you.magic_points==mp_before && you.piety==piety_before,
            "detonation has no second resource cost");
    require(grid_distance(you.pos(),mon->pos())==3,"detonation pushes survivors two legal cells");
    reset(false,0);
    fprintf(stderr,"HoloCrawl Sopia timer/native movement checks passed\n");
}
}

namespace holo_sopia {
std::string save_campaign(){std::ostringstream o;o<<1<<" "<<enabled<<" "<<ring_only<<" "<<field<<" "<<big<<" "<<inv<<" "<<ring_end<<" "<<ring_next<<" "<<field_end<<" "<<field_next<<" "<<charge<<" "<<charge_next<<" "<<big_ready<<" "<<centre.x<<" "<<centre.y<<" "<<pull_ready.size()<<" ";for(auto e:pull_ready)o<<e.first<<" "<<e.second<<" ";o<<counters.ring_casts<<" "<<counters.ring_ticks<<" "<<counters.ring_hits<<" "<<counters.field_casts<<" "<<counters.field_ticks<<" "<<counters.field_hits<<" "<<counters.pull_attempts<<" "<<counters.pulls<<" "<<counters.big_casts<<" "<<counters.detonations<<" "<<counters.damage<<" ";return o.str();}
void load_campaign(const std::string &blob){if(blob.empty()){reset(false,0);return;}std::istringstream i(blob);int v=0,n=-1;i>>v>>enabled>>ring_only>>field>>big>>inv>>ring_end>>ring_next>>field_end>>field_next>>charge>>charge_next>>big_ready>>centre.x>>centre.y>>n;if(!i || v!=1 || n<0 || n>100000 || inv<0 || inv>27 || charge<0 || charge>3)throw std::runtime_error("Invalid Sopia campaign save");pull_ready.clear();for(int a=0;a<n;++a){mid_t id;int at;i>>id>>at;pull_ready[id]=at;}i>>counters.ring_casts>>counters.ring_ticks>>counters.ring_hits>>counters.field_casts>>counters.field_ticks>>counters.field_hits>>counters.pull_attempts>>counters.pulls>>counters.big_casts>>counters.detonations>>counters.damage;if(!i)throw std::runtime_error("Truncated Sopia campaign save");i>>std::ws;if(!i.eof())throw std::runtime_error("Trailing Sopia save data");}
int manual_action(int tier,const coord_def &aim,int option){if(!enabled)return 0;inv=you.skill(SK_INVOCATIONS,1);if(tier==1)return cast_ring()?10:0;if(tier==3)return cast_field(false,aim)?10:0;if(tier==5)return cast_field(true,aim)?10:0;if(tier==6)return detonate()?10:0;if(tier==-1){if(option==1 && ring_end){ring_end=0;return 5;}if(option==2 && field){end_field(you.elapsed_time);return 5;}}return 0;}
int cooldown(){return big_ready;}
coord_def field_centre(){return centre;}
bool five_active(){return enabled && field && big && field_end>you.elapsed_time;}
holo_visual::effect visual_at(const coord_def &p){
    if(!enabled)return holo_visual::effect::none;
    if(ring_end>you.elapsed_time && grid_distance(you.pos(),p)==1 && clear_line(you.pos(),p))return holo_visual::effect::orbit;
    if(field && field_end>you.elapsed_time && visible(centre) && grid_distance(centre,p)<=(big?3:2) && clear_line(centre,p))return holo_visual::effect::gravity;
    return holo_visual::effect::none;
}
std::string status(){std::ostringstream out;out<<"Orbit "<<std::max(0,ring_end-you.elapsed_time)/10.0<<" turns | Field "<<(field?std::max(0,field_end-you.elapsed_time)/10.0:0)<<" turns | Big Bang charge "<<charge<<"/3 | recovery "<<std::max(0,big_ready-you.elapsed_time)/10.0<<" turns";return out.str();}
void restore_cooldown(int ready){big_ready=ready;}
void leave_level(){ring_end=0;if(field)end_field(you.elapsed_time);pull_ready.clear();}
}
