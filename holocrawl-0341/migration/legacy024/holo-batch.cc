#include "AppHdr.h"
#include "holo-lamy.h"
#include "holo-campaign.h"
#include <sstream>
#include "holo-batch-internal.h"
#include <algorithm>
#include <stdexcept>
#include <fstream>
#include "act-iter.h"
#include "beam.h"
#include "cloud.h"
#include "env.h"
#include "fight.h"
#include "holocrawl.h"
#include "los.h"
#include "melee-attack.h"
#include "mon-util.h"
#include "mon-tentacle.h"
#include "mgen-data.h"
#include "mon-place.h"
#include "mon-death.h"
#include "player.h"
#include "spl-cast.h"
#include "terrain.h"
#include "traps.h"

namespace holo_batch {
state s;
action_context ctx;
bool internal_damage=false;
namespace {
int waking_spell_depth=0;mid_t waking_spell_target=MID_NOBODY;bool waking_spell_sleep=false;
bool dream_asleep(monster *mon) {
    if(!mon || !is(god_id::okayu) || mon->mid!=s.marked || s.one_end<=you.elapsed_time) return false;
    const auto it=s.targets.find(mon->mid);
    return it!=s.targets.end() && it->second.kind!=3 && it->second.root>you.elapsed_time && mon->asleep();
}
}
waking_spell_scope::waking_spell_scope(bool direct)
    :old_depth(waking_spell_depth),old_target(waking_spell_target),old_sleep(waking_spell_sleep) {
    if(direct) {++waking_spell_depth;waking_spell_target=s.marked;waking_spell_sleep=dream_asleep(monster_by_mid(s.marked));}
}
waking_spell_scope::~waking_spell_scope() {
    waking_spell_depth=old_depth;waking_spell_target=old_target;waking_spell_sleep=old_sleep;
}
int waking_damage(monster &mon,const actor *source,int damage,kill_method_type kind) {
    if(!is(god_id::okayu) || damage<=0 || !mon.alive() || !source || !source->is_player()
        || internal_damage || !holo_campaign::ordinary_damage() || mon.mid!=s.marked
        || s.one_end<=you.elapsed_time) return damage;
    if(kind!=KILLED_BY_MONSTER && kind!=KILLED_BY_BEAM && kind!=KILLED_BY_DISINT) return damage;
    if(!ctx.ordinary && !waking_spell_depth) return damage;
    auto it=s.targets.find(mon.mid);if(it==s.targets.end())return damage;
    auto &t=it->second;
    if(t.kind==3 || t.root<=you.elapsed_time) return damage;
    const bool snapped=(ctx.ordinary && ctx.dream_target==mon.mid && ctx.dream_sleep)
        || (waking_spell_depth && waking_spell_target==mon.mid && waking_spell_sleep);
    if(!mon.asleep() && !snapped) return damage;
    // Apply once to already AC/resistance-adjusted damage. The cap keeps
    // native sleeping stabs from multiplying into an unbounded second crit.
    const int bonus=min(8+s.inv/3,max(1,damage/10*3+(damage%10)*3/10));
    t.kind=3;t.root=0;mon.behaviour=BEH_SEEK;
    ++s.totals.procs;
    return damage+bonus;
}

namespace { std::string probe_name;bool preparation_phase=false; }
void set_probe(const std::string &name,bool preparing) { probe_name=name;preparation_phase=preparing; }
bool probe_is(const char *name) { return probe_name==name; }
bool probe_preparing() { return preparation_phase; }
namespace { int balance_mela=0,balance_vivi=0; }
void configure_balance(int mela_level,int vivi_level) { balance_mela=mela_level;balance_vivi=vivi_level; }
int mela_heat_multiplier() { return balance_mela==2?2:balance_mela==1?3:4; }
int vivi_burst_sides() { return balance_vivi==2?5+s.inv/4:balance_vivi==1?5+s.inv/3:6+s.inv/3; }
namespace {
bool selective_policy=false;
std::string policy_build="melee";
int policy_next=0;
}
void set_policy(bool enabled,const std::string &build) { selective_policy=enabled;policy_build=build;policy_next=0; }
bool policy() { return selective_policy; }
bool policy_melee() { return policy_build=="melee"; }
bool policy_can_spend(int mp) {
    return !policy() || policy_build!="magic" || you.magic_points-mp>=(you.experience_level>=20?6:2);
}
int manual_tier=0,manual_option=0,manual_amount=3;
coord_def manual_aim,manual_second;
std::vector<coord_def> manual_positions;
bool manual() { return manual_tier!=0; }
bool want(int tier) { return !manual() || manual_tier==tier; }
bool active() { return s.god!=god_id::none && (holo_benchmark_active() || holo_campaign::combat_active()); }
bool is(god_id id) { return active() && s.god==id; }
bool passive() { return !holo_campaign::active() || you.piety>=30; }
bool five() { return active() && s.five_end>you.elapsed_time; }
const metrics &get_metrics() { return s.totals; }
std::vector<std::string> implemented()
{
    return {"suisei","miko","aki","fubuki","ayame","choco","korone","okayu","pekora",
        "watame","towa","lamy","polka","koyori","lui","raden","hajime","su","vivi","mela"};
}
void reset(const std::string &name,int invocation)
{
    s=state(); ctx=action_context(); internal_damage=false;
    policy_next=0;
    if (name.empty()) return;
    const std::map<std::string,god_id> names={
        {"suisei",god_id::suisei},{"miko",god_id::miko},{"aki",god_id::aki},
        {"fubuki",god_id::fubuki},{"ayame",god_id::ayame},{"choco",god_id::choco},
        {"korone",god_id::korone},{"okayu",god_id::okayu},{"pekora",god_id::pekora},
        {"watame",god_id::watame},{"towa",god_id::towa},{"lamy",god_id::lamy},
        {"polka",god_id::polka},{"koyori",god_id::koyori},{"lui",god_id::lui},
        {"raden",god_id::raden},{"hajime",god_id::hajime},{"su",god_id::su},
        {"vivi",god_id::vivi},{"mela",god_id::mela}};
    const auto ready=implemented();
    if (std::find(ready.begin(),ready.end(),name)==ready.end())
        throw std::runtime_error("Unimplemented combat core requested: "+name);
    s.god=names.at(name); s.inv=invocation;
    for(monster_iterator mi;mi;++mi) if(eligible(**mi)) s.eligible_sources.insert(mi->mid);
    s.next_tick=you.elapsed_time+1;
    if (s.god==god_id::okayu) { s.resource=30;s.shield=4+s.inv/3+1;s.last_event=you.elapsed_time+50; }
}
bool eligible(const monster &mon)
{
    return !mon.is_summoned() && mons_gives_xp(mon,you) && mon.attitude==ATT_HOSTILE;
}
bool line(const coord_def &from,const coord_def &to)
{ return from==to || exists_ray(from,to,opc_solid_see); }
bool seen(const coord_def &pos) { return you.see_cell(pos) && line(you.pos(),pos); }
std::vector<mid_t> enemies(const coord_def &origin,int radius,bool far,bool require_seen)
{
    std::vector<mid_t> ids;
    for (monster_iterator mi;mi;++mi)
        if (mi->alive() && mi->attitude==ATT_HOSTILE && (!require_seen || you.can_see(**mi))
            && grid_distance(origin,mi->pos())<=radius && line(origin,mi->pos()))
            ids.push_back(mi->mid);
    std::sort(ids.begin(),ids.end(),[&](mid_t a,mid_t b) {
        const monster *ma=monster_by_mid(a),*mb=monster_by_mid(b);
        int da=grid_distance(origin,ma->pos()),db=grid_distance(origin,mb->pos());
        if(da!=db) return far ? da>db : da<db;
        if(ma->pos().x!=mb->pos().x) return ma->pos().x<mb->pos().x;
        return ma->pos().y<mb->pos().y;
    });
    return ids;
}
int hurt(monster &mon,int raw,beam_type flavour,bool ac,bool direct)
{
    if (!mon.alive()) return 0;
    int amount=ac ? mon.apply_ac(raw) : raw;
    if (flavour!=BEAM_MISSILE && flavour!=BEAM_MAGIC)
        amount=resist_adjust_damage(&mon,flavour,amount);
    const mid_t id=mon.mid; const int hd=mon.get_experience_level();
    const bool credit=eligible(mon);
    ++s.totals.hits;
    holo_campaign::damage_scope campaign_damage(direct);
    const int dealt=mon.hurt(&you,max(0,amount),flavour);
    s.totals.damage+=dealt;
    if (credit && !mon.alive()) on_kill(id,hd,direct,false);
    return dealt;
}
int heal(int amount)
{
    if (amount<=0 || you.hp<=0 || holo_benchmark_finished() || you.duration[DUR_DEATHS_DOOR]) return 0;
    const int gain=min(amount,you.hp_max-you.hp);
    if (gain>0) you.heal(gain);
    s.totals.healed+=gain;
    return gain;
}
class strike_probe:public melee_attack {
public:
    strike_probe(actor &source,monster &mon):melee_attack(&source,&mon) {}
    bool hits(int accuracy,bool shields) {
        to_hit=random2(accuracy+1);
        return (!shields || !attack_shield_blocked(false))
            && test_hit(to_hit,defender->evasion(ev_ignore::none,&you),true)>=0;
    }
};
bool roll_hit(monster &mon,int accuracy,bool shield)
{ strike_probe probe(you,mon); return probe.hits(accuracy,shield); }
bool roll_hit_from(actor &source,monster &mon,int accuracy,bool shield)
{ strike_probe probe(source,mon);return probe.hits(accuracy,shield); }
bool move_actor(monster &mon,const coord_def &destination)
{
    if (!mon.alive() || mon.is_stationary() || mons_is_tentacle_or_tentacle_segment(mon.type)
        || !in_bounds(destination) || actor_at(destination) || trap_at(destination)
        || !mon.can_pass_through(destination) || !mon.is_habitable(destination)) return false;
    const coord_def old=mon.pos();
    if(!mon.move_to_pos(destination)) return false;
    mon.apply_location_effects(old,KILL_YOU,MHITYOU);
    return true;
}
void push(monster &mon,const coord_def &origin,int distance)
{
    coord_def d=mon.pos()-origin;
    if(!d.x && !d.y) d=mon.pos()-you.pos();
    d.x=(d.x>0)-(d.x<0);d.y=(d.y>0)-(d.y<0);
    for(int i=0;i<distance && mon.alive();++i)
        if(!move_actor(mon,mon.pos()+d)) break;
}
bool pay(int mp,int piety,int stars)
{
    if (you.piety<stars || you.piety<piety || you.magic_points<mp) return false;
    you.magic_points-=mp; you.piety-=piety; ++s.totals.casts;
    return true;
}
int choose_action(monster *target)
{
    if(policy() && active()) { const int dodge=policy_dodge();if(dodge) return dodge; }
    if(!active() || !target) return 0;
    if(policy() && you.elapsed_time<policy_next) return 0;
    int aut=martial_action(target);
    if(!aut) aut=resource_action(target);
    if(!aut) aut=experiment_action(target);
    if(!aut) aut=space_action(target);
    if(!aut) aut=summon_action(target);
    if(policy() && aut) {
        const int interval=is(god_id::koyori) || is(god_id::aki)?30:
            is(god_id::hajime) || is(god_id::lui) || is(god_id::okayu) || is(god_id::pekora)?20:10;
        policy_next=you.elapsed_time+interval;
    }
    return aut;
}
void advance(int now)
{
    if((!active() && !holo_campaign::active()) || holo_benchmark_finished()) return;
    while(s.next_tick<=now && !holo_benchmark_finished()) {
        const int at=s.next_tick; ++s.next_tick;
        if(at%10==0) martial_tick(at);
        resource_tick(at); experiment_tick(at);space_tick(at); summon_tick(at);
    }
}
bool pending_resolution()
{
    if(!active()) return false;
    if(s.deferred>0) return true;
    for(const auto &h:s.hazards) if((h.kind==1 || h.kind==11) && h.arm>0) return true;
    if(is(god_id::choco) && s.secondary<0) {
        const monster *mon=monster_by_mid(s.marked);
        return mon && mon->alive();
    }
    return false;
}
void begin_attack(monster &target,attack_kind kind)
{
    ctx=action_context();
    if(!active()) return;
    ctx.ordinary=true;ctx.kind=kind;ctx.target=target.mid;
    ctx.hp_before=target.hit_points;ctx.hd=target.get_experience_level();ctx.position=target.pos();
    ctx.eligible=eligible(target);
    ctx.ayame_zanshin_unlocked=is(god_id::ayame) && you.piety>=50;
    if(is(god_id::ayame) && you.piety>=50 && kind==attack_kind::melee && ctx.eligible
        && adjacent(you.pos(),target.pos()) && s.tertiary>you.elapsed_time
        && (s.marked!=target.mid || s.one_end<=you.elapsed_time))ctx.ayame_zanshin_end=s.tertiary;
    if(is(god_id::suisei)) {
        ctx.stars_before=s.marked==target.mid && s.one_end>you.elapsed_time ? s.resource : 0;
        if(s.three_end>you.elapsed_time) ctx.bonus=s.offence;
    }
    if(is(god_id::korone) && s.defence) ctx.bonus=roll_dice(1,4+s.inv/3);
    if(is(god_id::okayu)) {
        s.last_event=you.elapsed_time+50;ctx.dream_target=s.marked;
        ctx.dream_sleep=dream_asleep(monster_by_mid(s.marked));
    }
    if(is(god_id::hajime) && passive() && kind==attack_kind::melee) {
        ctx.bonus=s.resource*(3+s.inv/6);ctx.stars_before=s.resource;s.resource=0;
    }
    if(is(god_id::vivi) && five()) {
        for(mid_t id:enemies(you.pos(),LOS_DEFAULT_RANGE)) {
            const monster *mon=monster_by_mid(id);
            if(eligible(*mon) && !mon->asleep() && mon->foe==MHITYOU
                && mon->get_experience_level()>=max(1,(you.experience_level+2)/3))
                ++ctx.attention;
        }
        ctx.attention=min(5,ctx.attention);
    }
}
void note_primary_hit(const actor *target)
{
    if(active() && ctx.ordinary && target && target->mid==ctx.target) ctx.primary=true;
}
void note_primary_damage(const actor *target,int damage)
{
    if(active() && ctx.ordinary && target && target->mid==ctx.target) {
        ctx.primary=true;ctx.damage+=max(0,damage);ctx.damaged|=damage>0;
        if(is(god_id::suisei) && ctx.bonus>0) {
            monster *mon=monster_by_mid(ctx.target);
            const int bonus=ctx.bonus;ctx.bonus=0;s.three_end=0;s.offence=0;
            if(mon && mon->alive()) {
                ctx.damaged|=hurt(*mon,bonus)>0;ctx.reward_kill=!mon->alive();
                ctx.star_inheritance=you.piety>=100 && ctx.stars_before==0 && ctx.damaged && !ctx.reward_kill;
            }
        }
    }
}
void end_attack(int aut)
{
    if(!active() || !ctx.ordinary) return;
    monster *target=monster_by_mid(ctx.target);
    if(is(god_id::suisei) && ctx.primary && ctx.bonus>0) {
        const int bonus=ctx.bonus;ctx.bonus=0;s.three_end=0;s.offence=0;
        if(target && target->alive()) {
            ctx.damaged|=hurt(*target,bonus)>0;ctx.reward_kill=!target->alive();
            ctx.star_inheritance=you.piety>=100 && ctx.stars_before==0 && ctx.damaged && !ctx.reward_kill;
        }
    }
    if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && aut>0) {
        if(s.tertiary==ctx.ayame_zanshin_end)s.tertiary=0;
        ++s.totals.procs;
    }
    if(ctx.damaged && ctx.eligible && !ctx.reward_kill && (!target || !target->alive())) {
        if(is(god_id::ayame) && ctx.ayame_zanshin_unlocked && you.piety>=50 && aut>0 && ctx.kind==attack_kind::melee
            && ctx.target==s.marked && s.one_end>you.elapsed_time && adjacent(you.pos(),ctx.position))
            s.tertiary=you.elapsed_time+aut+30;
        on_kill(ctx.target,ctx.hd,true,true);
    }
    // A reward-only kill must clear the dead mark without earning a new reward.
    if(is(god_id::suisei) && ctx.reward_kill && s.marked==ctx.target) {s.marked=MID_NOBODY;s.resource=0;}
    martial_after_attack(target,aut);resource_after_attack(target,aut);
    experiment_after_attack(target);
    space_after_attack(target,aut);summon_after_attack(target,aut);
    ctx=action_context();
}
void cancel_attack() { ctx=action_context(); }
int suisei_focus_accuracy(const actor *target)
{
    if(!is(god_id::suisei) || you.piety<50 || !holo_campaign::ordinary_damage()
        || internal_damage || !target || !target->is_monster() || !target->alive()
        || target->as_monster()->attitude!=ATT_HOSTILE || target->mid!=s.marked
        || s.one_end<=you.elapsed_time || s.resource<2)return 0;
    return 3;
}
int to_hit(const actor *attacker,const actor *defender)
{
    if(!active()) return 0;
    if(attacker->is_player() && defender->is_monster()) {
        int bonus=0;
        if(ctx.ordinary && (ctx.kind==attack_kind::melee || ctx.kind==attack_kind::ranged))
            bonus+=suisei_focus_accuracy(defender);
        if(is(god_id::ayame) && ctx.ordinary && ctx.kind==attack_kind::melee && s.marked==defender->mid && s.one_end>you.elapsed_time
            && adjacent(you.pos(),defender->pos())) bonus+=3+s.inv/6+(five() ? 4 : 0);
        else if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && ctx.target==defender->mid
            && adjacent(you.pos(),defender->pos()))bonus+=3+s.inv/6;
        if(is(god_id::hajime) && ctx.ordinary && ctx.kind==attack_kind::melee) bonus+=ctx.stars_before;
        if(is(god_id::korone)) bonus+=five() ? 6 : s.resource;
        if(is(god_id::korone) && s.defence) bonus+=6;

        if(is(god_id::polka) && s.one_end>you.elapsed_time) bonus+=3;
        if(is(god_id::towa) && ctx.ordinary && ctx.kind==attack_kind::ranged) {
            if(enemies(you.pos(),1).empty()) bonus+=4+s.inv/6;
            if(five() && grid_distance(s.centre,defender->pos())<=2 && seen(defender->pos())) bonus+=6;
        }
        if(is(god_id::ayame) && ctx.double_hit) bonus+=8;
        return bonus;
    }
    if(attacker->is_monster() && defender->is_player()) {
        const auto it=s.targets.find(attacker->mid);
        int bonus=0;
        if(is(god_id::choco) && attacker->mid==s.marked && s.one_end>you.elapsed_time)
            bonus-=s.resource*(mental_immune(*attacker->as_monster())?1:2);
        if(it!=s.targets.end()) {
            if(is(god_id::polka) && it->second.weak_until>you.elapsed_time)bonus-=5;
            if(it->second.blind_ready<0) bonus-=5;
            if(is(god_id::lui) && you.piety>=75) {
                int n=0;for(const auto &p:it->second.raven_hits) if(p.second>you.elapsed_time) ++n;
                bonus-=2*min(3,n);
            }
        }
        return bonus;
    }
    return 0;
}
int slaying(const actor *defender,bool aux)
{
    if(!active() || aux || !ctx.ordinary || ctx.kind!=attack_kind::melee) return 0;
    if(is(god_id::ayame) && s.marked==defender->mid && s.one_end>you.elapsed_time
        && adjacent(you.pos(),defender->pos())) return 2+s.inv/9+(five() ? 3 : 0);
    if(is(god_id::ayame) && ctx.ayame_zanshin_end>0 && ctx.target==defender->mid
        && adjacent(you.pos(),defender->pos()))return 2+s.inv/9;
    if(is(god_id::korone)) return (five() ? 6 : passive()?s.resource:0)/2;
    return 0;
}
int raw_bonus(const actor *defender)
{
    return active() && !is(god_id::suisei) && ctx.ordinary && ctx.kind==attack_kind::melee && defender->mid==ctx.target
        ? ctx.bonus : 0;
}
int multiplier(int damage,bool auxiliary)
{
    if(!active() || auxiliary || !ctx.ordinary) return damage;
    int percent=100;
    if(is(god_id::vivi) && (s.one_end>you.elapsed_time || five()))
        percent+=10+s.inv/6+(five() ? 5*ctx.attention : 0);

    if(is(god_id::polka)) {
        if(s.one_end>you.elapsed_time) percent+=10;
        if(s.tertiary>you.elapsed_time) percent+=20;
    }
    if(is(god_id::towa) && passive() && ctx.kind==attack_kind::ranged && enemies(you.pos(),1).empty()) percent+=10;
    return percent==100 ? damage : div_rand_round(damage*percent,100);
}
int evasion(const actor *attacker)
{
    return active() && is(god_id::ayame) && attacker && attacker->mid==s.marked
        && s.one_end>you.elapsed_time && adjacent(you.pos(),attacker->pos())
        ? 2+s.inv/9+(five() ? 3 : 0) : 0;
}
int armour()
{
    return is(god_id::raden) && ((passive() && s.exhibit==1) || five()) && you.elapsed_time>=s.rest[1]
        ? 2+s.inv/9 : 0;
}
int status_percent(duration_type kind)
{
    if(is(god_id::miko) && s.one_end>you.elapsed_time
        && grid_distance(s.centre,you.pos())<=(five()?3:2)
        && (kind==DUR_CONF || kind==DUR_SLOW || kind==DUR_AFRAID || kind==DUR_POISONING))
        return five()?50:75;
    if(is(god_id::polka) && five() && (kind==DUR_CONF || kind==DUR_SLOW || kind==DUR_AFRAID || kind==DUR_POISONING)) return 50;
    return 100;
}
int status_duration(duration_type kind,int aut) {
    const int percent=status_percent(kind);return percent==100?aut:max(10,div_rand_round(aut*percent,100));
}
bool revealing() { return is(god_id::vivi) && (five() || s.one_end>you.elapsed_time); }
int resistance(beam_type flavour)
{
    if(flavour==BEAM_FIRE && is(god_id::mela)) return probe_is("no_fire_ward")?0:(passive()?1:0)+(five()?1:0);

    return 0;
}
int natural_regen(int base)
{ return is(god_id::okayu) && passive() && s.resource>=50 ? base*120/100 : base; }
int spell_damage(int damage,mid_t source)
{ return active() && source==you.mid && ctx.ordinary && ctx.kind==attack_kind::spell ? multiplier(damage):damage; }
void note_spell_damage(const actor *target,int damage,beam_type flavour,mid_t source)
{
    if(active() && source==you.mid && ctx.ordinary && ctx.kind==attack_kind::spell && target->mid==ctx.target) {
        ctx.element=flavour;note_primary_damage(target,damage);
    }
}
int spell_failure(int raw) { return raw; }
int monster_armour(const monster &mon,int base)
{
    base=max(0,base-monster_ac_penalty(mon));
    return is(god_id::towa) && five() && ctx.ordinary && ctx.kind==attack_kind::ranged
        && mon.mid==ctx.target && grid_distance(s.centre,mon.pos())<=2 && seen(mon.pos()) ? base*70/100:base;
}
bool rooted(const monster &mon)
{
    if(!active() || is(god_id::okayu)) return false;
    const auto it=s.targets.find(mon.mid);
    return it!=s.targets.end() && it->second.root>you.elapsed_time;
}
void after_move(const coord_def &old,bool voluntary)
{
    if(!active()) return;
    ++s.totals.moves; martial_move(old,voluntary);resource_move(old,voluntary);experiment_move(old,voluntary);space_move(old,voluntary);
}
void on_kill(mid_t mid,int hd,bool direct,bool ordinary)
{
    ++s.totals.kills;
    martial_kill(mid,hd,direct,ordinary);resource_kill(mid,hd,direct,ordinary);
}
int incoming(int damage,kill_method_type kind,mid_t source)
{
    if(!active() || internal_damage || damage==INSTANT_DEATH) return damage;
    damage=martial_incoming(damage,kind,source);
    return resource_incoming(damage,kind,source);
}
void post_damage()
{
    if(is(god_id::watame) && s.tertiary>0) { const int amount=s.tertiary;s.tertiary=0;heal(amount); }
}
bool suppress_aux() { return is(god_id::ayame) && s.defence!=0; }
void contact(const actor *attacker,beam_type flavour) { resource_contact(attacker,flavour);experiment_contact(attacker,flavour); }
void defended(const actor *attacker,bool)
{
    if(!is(god_id::watame) || you.piety<75 || !attacker || !attacker->is_monster()
        || !attacker->alive() || !adjacent(you.pos(),attacker->pos())
        || you.elapsed_time<s.proc_ready || !x_chance_in_y(20+s.inv,100)) return;
    s.proc_ready=you.elapsed_time+10;
    monster &mon=*monster_by_mid(attacker->mid);
    if(roll_hit(mon,20+s.inv)) hurt(mon,roll_dice(1,6+s.inv/2));
    ++s.totals.procs;
}
int monster_energy(const monster &mon,energy_use_type kind,int base)
{
    if(!active() || mon.stasis()) return base;
    base=summon_energy(mon,kind,base);
    base=experiment_energy(mon,kind,base);
    if(mon.attitude!=ATT_HOSTILE) return base;
    base=space_energy(mon,kind,base);
    const auto it=s.targets.find(mon.mid);if(it==s.targets.end()) return base;
    const auto &t=it->second;const int now=you.elapsed_time;
    const bool moving=kind==EUT_MOVE || kind==EUT_SWIM;
    int percent=100;
    if(is(god_id::okayu) && mon.mid==s.marked && s.one_end>now
        && (moving || kind==EUT_ATTACK || kind==EUT_SPELL))
        percent+=t.stacks*(mental_immune(mon)?4:8);
    if(is(god_id::lamy) && moving && t.slowed_until>now)
        percent=max(percent,150);
    if(is(god_id::korone) && moving && t.slowed_until>now) percent=max(percent,150);
    // Native slow already doubles action costs through speed, so keep the stronger effect.
    if(mon.has_ench(ENCH_SLOW) && percent<=200) return base;
    return (base*percent+99)/100;
}
bool before_monster(monster &mon) { return summon_before_monster(mon); }
void after_monster(monster &mon,const coord_def &old) { space_monster(mon,old); }
void attack_attempt(const actor *attacker,const actor *defender) { holo_campaign::fox_attacked(attacker,defender); space_attempt(attacker,defender); }
namespace { bool ward_recording=false;mid_t ward_victim=MID_NOBODY;int ward_nonfire=0; }
void ward_fixture_damage(const actor *victim,beam_type flavour,int actual);
void ward_fixture_damage(const actor *victim,beam_type flavour,int actual)
{
    if(ward_recording && victim && victim->mid==ward_victim
        && flavour!=BEAM_FIRE && flavour!=BEAM_STICKY_FLAME)
        ward_nonfire+=max(0,actual);
}
static void validate_fire_ward_paths()
{
    const char *output=getenv("HOLOCRAWL_WARD_RESULTS");
    std::ofstream log(output?output:"ward-regression.jsonl");
    if(!log) throw std::runtime_error("Cannot open fire-ward regression evidence");
    const auto require=[](bool ok,const char *message) {
        if(!ok) throw std::runtime_error(std::string("Mela actual damage regression: ")+message);
    };
    const auto run=[&](int path,int seed,bool ward,bool expired)->int {
        holo_reset_validation_fixture();reset("mela",12);
        set_probe(ward?"":"no_extra_fire_ward");s.five_end=expired?0:1000;
        you.equip[EQ_SHIELD]=-1;
        monster *source=nullptr;
        for(monster_iterator mi;mi;++mi) if(mi->attitude==ATT_HOSTILE) { source=*mi;break; }
        require(source!=nullptr,"missing source");
        const bool allied=path==1 || path==5 || path==6;
        actor *victim=&you;
        if(allied) {
            mgen_data mg(MONS_RAT,BEH_FRIENDLY,you.pos()+coord_def(0,1),MHITNOT,MG_FORCE_PLACE);
            monster *friend_mon=create_monster(mg,false);require(friend_mon!=nullptr,"missing ally");
            friend_mon->hit_points=friend_mon->max_hit_points=10000;victim=friend_mon;
        }
        if(path==2 || path==5) {
            monster_die(*source,KILL_DISMISSED,NON_MONSTER,true);
            mgen_data mg=mgen_data::hostile_at(MONS_FIRE_ELEMENTAL,false,victim->pos()+coord_def(1,0));
            mg.flags|=MG_FORCE_PLACE;source=create_monster(mg,false);
            require(source!=nullptr,"missing actual fire elemental");
        } else {
            require(source->move_to_pos(victim->pos()+coord_def(3,0)),"cannot place beam source");
        }
        you.time_taken=10;you.turn_is_over=true;
        rng::seed(43000+seed);const int before=victim->stat_hp();
        ward_nonfire=0;ward_victim=victim->mid;ward_recording=true;
        if(path==0 || path==1 || path==7 || path==8) {
            bolt beam;beam.name="ward regression bolt";beam.source=source->pos();beam.target=victim->pos();
            beam.source_id=source->mid;beam.thrower=KILL_MON;beam.range=5;
            beam.flavour=beam.real_flavour=path==7?BEAM_COLD:path==8?BEAM_MISSILE:BEAM_FIRE;
            beam.damage=dice_def(60,1);beam.auto_hit=true;beam.hit=AUTOMATIC_HIT;beam.ac_rule=ac_type::none;
            beam.aimed_at_spot=true;beam.animate=false;beam.fire();
        } else if(path==2 || path==5) {
            fight_melee(source,victim);
        } else if(path==3 || path==6) {
            place_cloud(CLOUD_FIRE,victim->pos(),10,source);actor_apply_cloud(victim);
        } else {
            you.duration[DUR_LIQUID_FLAMES]=20;dec_napalm_player(10);
        }
        ward_recording=false;return before-victim->stat_hp();
    };
    const char *names[]={"player_beam","ally_beam","player_fire_melee","player_fire_cloud","player_sticky_flame","ally_fire_melee","ally_fire_cloud","cold_control","physical_control"};
    for(int path=0;path<9;++path) {
        int total=0;
        for(int seed=0;seed<16;++seed) {
            const int control=run(path,seed,false,false),control_physical=ward_nonfire;
            const int protected_damage=run(path,seed,true,false),ward_physical=ward_nonfire;
            const int fire_control=control-control_physical,fire_ward=protected_damage-ward_physical;
            log<<"{\"path\":\""<<names[path]<<"\",\"seed\":"<<seed<<",\"same_native_fire_resistance\":true,\"control_damage\":"<<control<<",\"ward_damage\":"<<protected_damage
                <<",\"native_nonfire_control\":"<<control_physical<<",\"native_nonfire_ward\":"<<ward_physical<<",\"fire_component_control\":"<<fire_control<<",\"fire_component_ward\":"<<fire_ward<<"}\n";log.flush();
            require(control_physical==ward_physical,"native physical part changed");
            if(path<7) require(fire_control>=0 && fire_ward>=0 && std::abs(2*fire_ward-fire_control)<=1,"extra fire ward not applied exactly once");
            else require(protected_damage==control && control==60,"non-fire damage changed");
            if(path==0) require(control==20 && protected_damage==10,"actual beam HP loss differs from native rF2 then half");
            if(path==1) require(control==60 && protected_damage==30,"actual allied beam is not halved once");
            total+=control;
        }
        require(total>0,"damage path never exercised");
    }
    require(run(0,0,true,true)==30,"expired ultimate keeps ward or rF2");
    set_probe("");holo_reset_validation_fixture();reset();
    fprintf(stderr,"Mela actual HP fire-ward regressions passed: 9 paths x16 paired seeds; beam rF2 20->10, ally60->30, expiry30\n");
}
void validate()
{
    const auto require=[](bool ok,const std::string &message) {
        if(!ok) throw std::runtime_error("Holo batch native validation: "+message);
    };
    const auto target=[]()->monster* {
        for(monster_iterator mi;mi;++mi) if(mi->alive() && mi->attitude==ATT_HOSTILE) return *mi;
        return nullptr;
    };
    holo_reset_validation_fixture();
    require(!active() && armour()==0 && resistance(BEAM_FIRE)==0 && multiplier(100)==100,
        "inactive hooks change the baseline");
    for(const std::string &god:implemented()) {
        holo_reset_validation_fixture();reset(god,12);
        for(int turn=0;turn<60 && !holo_benchmark_finished();++turn) {
            monster *mon=target();int aut=choose_action(mon);
            if(!aut && mon && adjacent(you.pos(),mon->pos())) {
                begin_attack(*mon);you.time_taken=10;fight_melee(&you,mon);aut=max(1,you.time_taken);end_attack(aut);
            }
            holo_validation_spend_time(aut?aut:10);
            require(s.resource>=0 && s.shield>=0 && s.deferred>=0,god+" has negative resources");
            require(you.magic_points>=0 && you.piety>=0 && you.hp_max==10000,god+" changes a fixed kit or overspends");
        }
        require(!holo_benchmark_finished() && s.totals.casts>0,god+" has no live native ability action");
    }
    holo_reset_validation_fixture();reset("choco",12);
    monster *mon=target();s.marked=mon->mid;s.secondary=-1;s.five_end=20;mon->attitude=ATT_FRIENDLY;
    require(pending_resolution(),"last charmed enemy produces a premature victory");
    you.elapsed_time=19;advance(19);require(mon->attitude==ATT_FRIENDLY,"charm expires early");
    you.elapsed_time=20;advance(20);require(mon->attitude==ATT_HOSTILE && !pending_resolution(),"charm fails to restore hostility");
    holo_reset_validation_fixture();reset("korone",12);
    mon=target();mon->attitude=ATT_FRIENDLY;you.hp=3;
    s.deferred=10;s.five_end=1;s.debt_next=11;s.debt_ticks=5;s.secondary=1;
    require(pending_resolution(),"unpaid deferred damage produces a premature victory");
    you.elapsed_time=11;advance(11);require(you.hp==1 && s.deferred==8,"first debt payment is not exact");
    you.elapsed_time=21;advance(21);require(holo_benchmark_finished() && you.hp<=0,"deferred damage cannot kill after combat");
    holo_reset_validation_fixture();reset("mela",12);mon=target();
    contact(mon,BEAM_MISSILE);contact(mon,BEAM_FIRE);contact(mon,BEAM_FIRE);
    require(s.resource==2 && resistance(BEAM_FIRE)==1,"heat cap or base fire resistance is wrong");
    you.elapsed_time=10;contact(mon,BEAM_FIRE);require(s.resource==4,"heat does not reset its 10-aut budget");
    contact(&you,BEAM_FIRE);require(s.resource==4,"self damage generates heat");
    holo_reset_validation_fixture();reset("mela",12);mon=target();
    you.equip[EQ_SHIELD]=-1;you.slot_item(EQ_BODY_ARMOUR)->plus=200;
    bool zero_incoming=false;
    for(int attempt=0;attempt<20 && !zero_incoming;++attempt) {
        you.elapsed_time=10*attempt;s.resource=0;s.secondary=0;s.last_incoming=-1000;
        const int hp_before=you.hp;bool hit=false;fight_melee(mon,&you,&hit);
        if(hit && you.hp==hp_before) {
            require(s.resource>0,"a native hit fully absorbed by armour fails to generate heat");zero_incoming=true;
        }
    }
    require(zero_incoming,"armour-zero native hit fixture did not exercise its branch");
    holo_reset_validation_fixture();reset("ayame",12);mon=target();mon->hit_points=1;
    s.marked=mon->mid;s.one_end=s.five_end=1000;you.magic_points=100;
    bool duel_kill=false;
    for(int attempt=0;attempt<20 && !duel_kill;++attempt) {
        s.three_ready=0;const int mp_before=you.magic_points;const mid_t id=mon->mid;
        require(martial_action(mon)>0,"double strike fixture cannot activate");
        mon=monster_by_mid(id);duel_kill=!mon || !mon->alive();
        if(duel_kill) require(s.three_ready==you.elapsed_time && s.five_end==you.elapsed_time
            && you.magic_points==mp_before-3+5,"double-strike completion overwrites the duel kill cooldown/MP reset");
    }
    require(duel_kill,"duel fixture never lands a killing native melee attack");
    holo_reset_validation_fixture();reset("su",12);mon=target();
    begin_attack(*mon);note_primary_damage(mon,0);end_attack(10);require(s.hazards.empty(),"zero damage creates water");
    begin_attack(*mon);note_primary_damage(mon,1);end_attack(10);
    require(s.hazards.size()==1 && grd(mon->pos())==DNGN_SHALLOW_WATER
        && monster_energy(*mon,EUT_MOVE,10)==10 && monster_energy(*mon,EUT_ATTACK,10)==10,
        "Su lacks native shallow water or retains extra movement cost");
    holo_reset_validation_fixture();reset("lamy",12);s.resource=80;mon=target();begin_attack(*mon);
    require(multiplier(100)==100 && resistance(BEAM_COLD)==0 && holo_lamy::power_bonus()==16 && holo_lamy::evasion_penalty()==3,"Lamy caster retained old melee/resistance modifiers");
    s.five_end=100;require(multiplier(100)==100,"blizzard retains the high-drunk direct damage bonus");
    holo_reset_validation_fixture();reset("raden",12);mon=target();you.piety=100;
    const int mp=you.magic_points;
    require(change_exhibit(1)==10 && you.magic_points==mp-1 && armour()==3,"exhibit switching has wrong cost or armour");
    s.rest[1]=40;require(change_exhibit(0)==10 && change_exhibit(1)==10 && armour()==0,"switching resets a resting exhibit");
    require(change_exhibit(2)==10,"craft exhibit cannot be selected");you.duration[DUR_SLOW]=100;
    require(martial_action(mon)==10 && s.shield==26 && s.three_end==90 && you.duration[DUR_SLOW]==50,"craft shield scaling, duration or cleansing is missing");
    holo_reset_validation_fixture();reset("mela",12);mon=target();mon->type=MONS_FIRE_ELEMENTAL;
    const int hp=mon->hit_points;
    require(hurt(*mon,20,BEAM_FIRE,false)==0 && mon->hit_points==hp,"fire damage bypasses native rF+++ immunity");
    require(hurt(*mon,20,BEAM_MISSILE,false)>0,"resistance fixture rejects ordinary physical damage");
    validate_experiments();validate_summons();
    if(getenv("HOLOCRAWL_WARD_SELFTEST")) validate_fire_ward_paths();
    holo_reset_validation_fixture();reset("mela",12);set_probe("no_fire_ward");s.five_end=100;
    require(resistance(BEAM_FIRE)==0 && fire_protection(you,20,BEAM_FIRE)==20,"fire-ward ablation retains protection");
    holo_reset_validation_fixture();reset("mela",12);set_probe("no_ultimate");mon=target();
    require(experiment_action(mon)==10 && s.five_end==0 && s.totals.casts==1,"ultimate ablation blocks other actions or activates ultimate");
    holo_reset_validation_fixture();reset("vivi",12);set_probe("no_blind");mon=target();s.five_ready=1000;s.one_end=1000;
    require(martial_action(mon)==10 && s.totals.blind_attempts>0 && s.totals.blind_successes==0 && !mon->has_ench(ENCH_BLIND),"blind-only ablation changes burst selection or applies blindness");
    holo_reset_validation_fixture();reset("miko",12);set_probe("shrine_only");mon=target();s.one_end=1000;s.centre=you.pos();
    require(martial_action(mon)==0,"shrine-only ablation activates fire or ultimate");
    set_probe("");
    // Regression for native summoner death removing a later actor in an AoE ID snapshot.
    const auto linked_sphere=[&](monster *owner,const coord_def &pos) {
        mgen_data mg(MONS_BATTLESPHERE,BEH_HOSTILE,pos,MHITNOT,MG_FORCE_PLACE);
        mg.set_summoned(owner,0,SPELL_BATTLESPHERE,GOD_NO_GOD);
        monster *sphere=create_monster(mg,false);require(sphere!=nullptr,"cannot create linked sphere fixture");
        sphere->summoner=owner->mid;owner->props["battlesphere"].get_int()=sphere->mid;
        return sphere->mid;
    };
    for(const std::string god:{"mela","vivi","polka"}) {
        holo_reset_validation_fixture();reset(god,12);mon=target();mon->hit_points=1;
        const mid_t sphere=linked_sphere(mon,you.pos()+coord_def(2,0));
        s.five_ready=1000;s.one_end=1000;
        if(god=="polka") { s.resource=3;s.five_ready=0; }
        require(enemies(you.pos(),3).size()==2,"cascade fixture is outside AoE snapshot");
        const int aut=god=="mela"?experiment_action(mon):god=="polka"?polka_finale(0,3,mon):martial_action(mon);
        require(aut==10 && !monster_by_mid(sphere),"AoE does not resolve native linked-summon disappearance safely");
    }
    holo_reset_validation_fixture();reset("miko",12);mon=target();mon->hit_points=1;
    require(mon->move_to_pos(you.pos()+coord_def(2,0)),"cannot place cascade boundary fixture");
    const mid_t sphere=linked_sphere(mon,you.pos()+coord_def(2,1));
    s.centre=you.pos();s.one_end=1000;s.three_end=1000;martial_tick(10);
    require(!monster_by_mid(sphere),"shrine fire does not resolve linked-summon disappearance safely");
    fprintf(stderr,"HoloCrawl AoE linked-summon cascade regressions passed: Mela/Vivi/Miko/Polka\n");
    fprintf(stderr,"HoloCrawl five-god probe checks passed: ward/ultimate/blind/shrine selection\n");
    // Action-selection regressions. Existing native effect fixtures above run with policy disabled.
    holo_reset_validation_fixture();reset("miko",12);set_policy(true,"melee");mon=target();
    s.centre=you.pos();s.one_end=1000;s.five_ready=1000;
    const int shrine_mp=you.magic_points;
    require(martial_action(mon)==0 && you.magic_points==shrine_mp,"policy wastes shrine fire on an empty boundary");
    require(mon->move_to_pos(you.pos()+coord_def(2,0)),"cannot place shrine boundary target");
    require(martial_action(mon)==10 && you.magic_points==shrine_mp-3,"policy blocks useful shrine fire or changes its cost");
    holo_reset_validation_fixture();reset("koyori",12);set_policy(true,"melee");mon=target();
    require(choose_action(mon)==10 && s.stock[0]==2,"policy cannot prepare initial reagent");
    const int reagent_mp=you.magic_points;
    require(choose_action(mon)==0 && you.magic_points==reagent_mp,"policy permits consecutive active actions inside30 aut");
    you.elapsed_time=30;
    require(choose_action(mon)==10 && s.stock[0]==1,"policy fails to resume reagent use after its selection interval");
    holo_reset_validation_fixture();reset("polka",12);set_policy(true,"melee");mon=target();s.one_ready=1000;
    const coord_def polka_pos=you.pos();
    require(experiment_action(mon)==0 && you.pos()==polka_pos,"policy performs pointless acrobatics without a performance");
    holo_reset_validation_fixture();reset("hajime",12);set_policy(true,"ranged");mon=target();
    require(mon->move_to_pos(you.pos()+coord_def(2,0)),"cannot place dash fixture");
    require(martial_action(mon)==0,"ranged policy forces an approach or an empty ultimate");
    holo_reset_validation_fixture();reset("aki",12);set_policy(true,"magic");mon=target();you.magic_points=4;
    require(summon_action(mon)==0 && you.magic_points==4,"policy consumes reserved spell MP");
    holo_reset_validation_fixture();reset("pekora",12);set_policy(true,"melee");mon=target();
    hazard bomb;bomb.kind=11;bomb.pos=you.pos()+coord_def(1,0);bomb.arm=10;bomb.end=11;s.hazards.push_back(bomb);
    require(policy_dodge()>0 && grid_distance(you.pos(),bomb.pos)>1,"policy fails to move out of a known imminent blast");
    set_policy(false,"melee");
    fprintf(stderr,"HoloCrawl selective policy checks passed: boundary/resource/interval/movement/blast selection\n");
    holo_reset_validation_fixture();reset();you.hp=1;
    ouch(2,KILLED_BY_WILD_MAGIC,you.mid,"terminal healing regression");
    require(holo_benchmark_finished() && you.hp<=0,"terminal fixture did not die");
    const int terminal_hp=you.hp;inc_hp(50);calc_hp(true,false);dec_hp(5,false);set_hp(50);
    require(heal(50)==0 && you.hp==terminal_hp,"native or divine healing changes terminal HP");
    holo_reset_validation_fixture();reset();you.hp=1;inc_hp(5);
    require(you.hp==6 && heal(5)==5 && you.hp==11,"terminal guard suppresses live healing");
    fprintf(stderr,"HoloCrawl terminal HP guards passed: native/divine healing, scaled maxHP, nonfatal floor and setHP blocked after death; live healing preserved\n");
    holo_reset_validation_fixture();
    reset();
    fprintf(stderr,"HoloCrawl batch native core checks passed: 20 modules, resource/charm/debt/water/resistance fixtures\n");
}
}

namespace holo_batch {
std::string save_campaign() {
 std::ostringstream o;o<<(s.god==god_id::suisei?2:1)<<" "<<int(s.god)<<" ";
 o<<s.inv<<" ";
 o<<s.next_tick<<" ";
 o<<s.one_end<<" ";
 o<<s.three_end<<" ";
 o<<s.five_end<<" ";
 o<<s.one_ready<<" ";
 o<<s.three_ready<<" ";
 o<<s.five_ready<<" ";
 o<<s.resource<<" ";
 o<<s.shield<<" ";
 o<<s.regen_fraction<<" ";
 o<<s.last_event<<" ";
 o<<s.last_incoming<<" ";
 o<<s.proc_ready<<" ";
 o<<s.deferred<<" ";
 o<<s.debt_next<<" ";
 o<<s.debt_ticks<<" ";
 o<<s.secondary<<" ";
 o<<s.tertiary<<" ";
 o<<s.offence<<" ";
 o<<s.defence<<" ";
 o<<s.exhibit<<" ";
 for(int x:s.rest)o<<x<<" ";
 for(int x:s.stock)o<<x<<" ";
 o<<s.marked<<" "<<s.centre.x<<" "<<s.centre.y<<" ";
 o<<s.targets.size()<<" ";for(const auto &e:s.targets){o<<e.first<<" ";const auto &t=e.second;
o<<t.stacks<<" ";o<<t.expires<<" ";o<<t.next<<" ";o<<t.immune<<" ";o<<t.root<<" ";o<<t.kind<<" ";o<<t.blind_ready<<" ";o<<t.slowed_until<<" ";o<<t.weak_until<<" ";o<<t.paint<<" ";o<<t.paint_end<<" ";
o<<t.raven_hits.size()<<" ";for(auto p:t.raven_hits)o<<p.first<<" "<<p.second<<" ";}
 o<<s.companions.size()<<" ";for(auto c:s.companions)o<<c.mid<<" "<<c.expires<<" "<<c.natural_end<<" "<<c.next<<" "<<c.shield<<" "<<c.kind<<" "<<c.extra<<" ";
 o<<s.hazards.size()<<" ";for(auto h:s.hazards)o<<h.pos.x<<" "<<h.pos.y<<" "<<h.arm<<" "<<h.end<<" "<<h.next<<" "<<h.kind<<" "<<h.extra<<" "<<h.target<<" ";
 o<<s.rewarded.size()<<" ";for(auto x:s.rewarded)o<<x<<" ";
 o<<s.performance_hits.size()<<" ";for(auto x:s.performance_hits)o<<x<<" ";
 o<<s.candidates.size()<<" ";for(auto x:s.candidates)o<<x<<" ";
 o<<s.eligible_sources.size()<<" ";for(auto x:s.eligible_sources)o<<x<<" ";
o<<s.totals.casts<<" ";o<<s.totals.hits<<" ";o<<s.totals.damage<<" ";o<<s.totals.healed<<" ";o<<s.totals.absorbed<<" ";o<<s.totals.moves<<" ";o<<s.totals.summons<<" ";o<<s.totals.procs<<" ";o<<s.totals.kills<<" ";o<<s.totals.self_damage<<" ";o<<s.totals.deferred_paid<<" ";o<<s.totals.ap_earned<<" ";o<<s.totals.ap_spent<<" ";o<<s.totals.performances_started<<" ";o<<s.totals.performances_completed<<" ";o<<s.totals.performances_expired<<" ";o<<s.totals.blind_attempts<<" ";o<<s.totals.blind_successes<<" ";
 return o.str();}
void load_campaign(const std::string &blob) {
 if(blob.empty()){reset();return;}std::istringstream i(blob);int v=0,g=0;i>>v>>g;if((v!=1 && !(v==2 && g==int(god_id::suisei))) || g<0 || g>20)throw std::runtime_error("Unsupported combat save state");state n;n.god=god_id(g);
i>>n.inv;i>>n.next_tick;i>>n.one_end;i>>n.three_end;i>>n.five_end;i>>n.one_ready;i>>n.three_ready;i>>n.five_ready;i>>n.resource;i>>n.shield;i>>n.regen_fraction;i>>n.last_event;i>>n.last_incoming;i>>n.proc_ready;i>>n.deferred;i>>n.debt_next;i>>n.debt_ticks;i>>n.secondary;i>>n.tertiary;i>>n.offence;i>>n.defence;i>>n.exhibit;
for(int &x:n.rest)i>>x;
for(int &x:n.stock)i>>x;
i>>n.marked>>n.centre.x>>n.centre.y;
auto count=[&](){int length=-1;i>>length;if(!i || length<0 || length>100000)throw std::runtime_error("Invalid combat save collection");return length;};
int size=count();for(int a=0;a<size;++a){mid_t id; i>>id;auto &t=n.targets[id];i>>t.stacks;i>>t.expires;i>>t.next;i>>t.immune;i>>t.root;i>>t.kind;i>>t.blind_ready;i>>t.slowed_until;i>>t.weak_until;i>>t.paint;i>>t.paint_end;int k=count();for(int b=0;b<k;++b){mid_t raven_id;int at;i>>raven_id>>at;t.raven_hits[raven_id]=at;}}
size=count();for(int a=0;a<size;++a){companion c;i>>c.mid>>c.expires>>c.natural_end>>c.next>>c.shield>>c.kind>>c.extra;n.companions.push_back(c);}
size=count();for(int a=0;a<size;++a){hazard h;i>>h.pos.x>>h.pos.y>>h.arm>>h.end>>h.next>>h.kind>>h.extra>>h.target;n.hazards.push_back(h);}
size=count();for(int a=0;a<size;++a){mid_t id;i>>id;n.rewarded.insert(id);}
size=count();for(int a=0;a<size;++a){mid_t id;i>>id;n.performance_hits.insert(id);}
size=count();for(int a=0;a<size;++a){mid_t id;i>>id;n.candidates.insert(id);}
size=count();for(int a=0;a<size;++a){mid_t id;i>>id;n.eligible_sources.insert(id);}
i>>n.totals.casts;i>>n.totals.hits;i>>n.totals.damage;i>>n.totals.healed;i>>n.totals.absorbed;i>>n.totals.moves;i>>n.totals.summons;i>>n.totals.procs;i>>n.totals.kills;i>>n.totals.self_damage;i>>n.totals.deferred_paid;i>>n.totals.ap_earned;i>>n.totals.ap_spent;i>>n.totals.performances_started;i>>n.totals.performances_completed;i>>n.totals.performances_expired;i>>n.totals.blind_attempts;i>>n.totals.blind_successes;
if(!i)throw std::runtime_error("Truncated combat save payload");
i>>std::ws;if(!i.eof() || i.bad() || n.inv<0 || n.inv>27 || n.next_tick<0)throw std::runtime_error("Invalid combat save payload");
if(n.god==god_id::suisei) {
 // Preserve proportional progress from legacy 5-star saves. An already
 // rolled kill reward stays unchanged. In-flight old comets keep +5/old star.
 if(v==1) {
  n.resource=(3*max(0,min(5,n.resource))+4)/5;
  for(auto &h:n.hazards)if(h.kind==1 && h.arm>0)h.end=-1;
 }
 n.resource=max(0,min(3,n.resource));
}
s=n;ctx=action_context();internal_damage=false;set_policy(false,"melee");set_probe("");configure_balance(1,1);}
}

namespace holo_batch {
int manual_action(int tier,monster *target,const coord_def &aim,int option,int amount) {
 if(!active())return 0;
 manual_tier=tier;manual_option=option;manual_amount=amount;manual_aim=aim;
 struct clear_manual { ~clear_manual(){manual_tier=0;manual_positions.clear();} } guard;
 if(s.god==god_id::raden && tier==1)return change_exhibit(option);
 int aut=manual_resource(target);if(aut>=0)return aut;
 aut=manual_experiment(target);if(aut>=0)return aut;
 aut=manual_space(target);if(aut>=0)return aut;
 aut=manual_summon(target);if(aut>=0)return aut;
 aut=martial_action(target);if(!aut)aut=resource_action(target);
 if(!aut)aut=experiment_action(target);
 if(!aut)aut=space_action(target);
 if(!aut)aut=summon_action(target);
 return aut;
}
}
