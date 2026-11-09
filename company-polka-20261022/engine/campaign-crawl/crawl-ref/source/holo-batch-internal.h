#pragma once
#include "holo-batch.h"
#include <map>
#include <set>

namespace holo_batch {
enum class god_id { none,suisei,miko,aki,fubuki,ayame,choco,korone,okayu,pekora,
    watame,towa,lamy,polka,koyori,lui,raden,hajime,su,vivi,mela };
struct target_state {
    int stacks=0,expires=0,next=0,immune=0,root=0,kind=0;
    int blind_ready=0,slowed_until=0,weak_until=0,paint=0,paint_end=0;
    std::map<mid_t,int> raven_hits;
};
struct companion {
    mid_t mid=MID_NOBODY;
    int expires=0,natural_end=0,next=0,shield=0,kind=0;
    bool extra=false;
};
struct hazard { coord_def pos; int arm=0,end=0,next=0,kind=0,extra=0; mid_t target=MID_NOBODY; };
struct state {
    god_id god=god_id::none;
    int inv=0,next_tick=10,one_end=0,three_end=0,five_end=0;
    int one_ready=0,three_ready=0,five_ready=0,resource=0,shield=0;
    int regen_fraction=0,last_event=0,last_incoming=-1000,proc_ready=0;
    int deferred=0,debt_next=0,debt_ticks=0,secondary=0,tertiary=0;
    int offence=0,defence=0,exhibit=0,rest[3]={0,0,0},stock[3]={0,0,0};
    mid_t marked=MID_NOBODY;
    coord_def centre;
    std::map<mid_t,target_state> targets;
    std::vector<companion> companions;
    std::vector<hazard> hazards;
    std::set<mid_t> rewarded,performance_hits,candidates,eligible_sources;
    metrics totals;
};
struct action_context {
    bool ordinary=false,primary=false,damaged=false,double_hit=false,eligible=false,reward_kill=false;
    bool star_inheritance=false; // Per-action only; the banked reward uses existing saved fields.
    bool ayame_zanshin_unlocked=false;
    int ayame_zanshin_end=0; // Per-action snapshot; saved bank is state.tertiary.
    bool dream_sleep=false;mid_t dream_target=MID_NOBODY;
    attack_kind kind=attack_kind::melee;
    beam_type element=BEAM_MAGIC;
    mid_t target=MID_NOBODY;
    int damage=0,hp_before=0,hd=0,bonus=0,stars_before=0,attention=0;
    coord_def position;
};
extern state s;
extern action_context ctx;
extern bool internal_damage;
void set_probe(const std::string &name,bool preparing=false);
bool probe_is(const char *name);
bool probe_preparing();
// Experimental action-selection policy. Never changes damage, costs or cooldowns.
void set_policy(bool enabled,const std::string &build);
bool policy();
bool policy_melee();
bool policy_can_spend(int mp);
int policy_dodge();
void configure_balance(int mela_level,int vivi_level);
int mela_heat_multiplier();
int vivi_burst_sides();
bool manual();
bool want(int tier);
extern int manual_tier,manual_option,manual_amount;
extern coord_def manual_aim,manual_second;
extern std::vector<coord_def> manual_positions;
int manual_resource(monster *target);
int manual_experiment(monster *target);
int manual_space(monster *target);
int manual_summon(monster *target);
bool is(god_id id);
bool five();
bool passive();
bool eligible(const monster &mon);
bool seen(const coord_def &pos);
bool line(const coord_def &from,const coord_def &to);
std::vector<mid_t> enemies(const coord_def &origin,int radius,bool far=false,bool require_seen=true);
int hurt(monster &mon,int raw,beam_type flavour=BEAM_MISSILE,bool ac=true,bool direct=false);
int heal(int amount);
bool roll_hit(monster &mon,int accuracy,bool shield=true);
bool roll_hit_from(actor &source,monster &mon,int accuracy,bool shield=true);
bool move_actor(monster &mon,const coord_def &destination);
void push(monster &mon,const coord_def &origin,int distance);
bool pay(int mp,int piety,int stars=30);
void on_kill(mid_t mid,int hd,bool direct,bool ordinary);
int martial_action(monster *target);
void martial_tick(int at);
void martial_after_attack(monster *target,int aut);
void martial_move(const coord_def &old,bool voluntary);
void martial_kill(mid_t mid,int hd,bool direct,bool ordinary);
int martial_incoming(int damage,kill_method_type kind,mid_t source);
int resource_action(monster *target);
void resource_tick(int at);
void resource_after_attack(monster *target,int aut);
void resource_move(const coord_def &old,bool voluntary);
void resource_kill(mid_t mid,int hd,bool direct,bool ordinary);
int resource_incoming(int damage,kill_method_type kind,mid_t source);
int experiment_action(monster *target);
void experiment_tick(int at);
void experiment_after_attack(monster *target);
void experiment_move(const coord_def &old,bool voluntary);
void experiment_contact(const actor *attacker,beam_type flavour);
void experiment_spell(monster &mon,beam_type flavour);
void validate_experiments();
void validate_summons();
void garden_entry(monster &mon,const coord_def &old);
int experiment_energy(const monster &mon,energy_use_type kind,int base);
bool mental_immune(const monster &mon);
void resource_contact(const actor *attacker,beam_type flavour);
int space_action(monster *target);
void space_tick(int at);
void space_after_attack(monster *target,int aut);
void space_move(const coord_def &old,bool voluntary);
void space_monster(monster &mon,const coord_def &old);
int space_energy(const monster &mon,energy_use_type kind,int base);
void space_attempt(const actor *attacker,const actor *defender);
int summon_action(monster *target);
void summon_tick(int at);
void summon_after_attack(monster *target,int aut);
bool summon_before_monster(monster &mon);
int summon_energy(const monster &mon,energy_use_type kind,int base);
}
