#pragma once

#include <string>
#include <vector>
#include "coord.h"
#include "duration-type.h"
#include "energy-use-type.h"
#include "mon-enum.h"
#include "ouch.h"

namespace holo_batch {
enum class attack_kind { melee, ranged, spell };
struct metrics {
    int casts=0, hits=0, damage=0, healed=0, absorbed=0, moves=0;
    int summons=0, procs=0, kills=0, self_damage=0, deferred_paid=0;
    int ap_earned=0,ap_spent=0,performances_started=0,performances_completed=0,performances_expired=0;
    int blind_attempts=0,blind_successes=0;
};
std::vector<std::string> implemented();
void reset(const std::string &god="",int invocation=0);
bool active();
int choose_action(monster *target);
void advance(int now);
bool pending_resolution();
void begin_attack(monster &target,attack_kind kind=attack_kind::melee);
void note_primary_damage(const actor *target,int damage);
void note_primary_hit(const actor *target);
void end_attack(int aut);
void cancel_attack();
int waking_damage(monster &mon,const actor *source,int damage,kill_method_type kind);
class waking_spell_scope {
    int old_depth;mid_t old_target;bool old_sleep;
public: explicit waking_spell_scope(bool direct_player_spell);~waking_spell_scope();
};
void after_move(const coord_def &old,bool voluntary=true);
int suisei_focus_accuracy(const actor *target);
int to_hit(const actor *attacker,const actor *defender);
int slaying(const actor *defender,bool aux);
int raw_bonus(const actor *defender);
int multiplier(int damage,bool auxiliary=false);
int evasion(const actor *attacker);
int armour();
int incoming(int damage,kill_method_type kind,mid_t source);
void post_damage();
void contact(const actor *attacker,beam_type flavour);
bool suppress_aux();
void defended(const actor *attacker,bool blocked);
int status_duration(duration_type kind,int aut);
int status_percent(duration_type kind);
bool revealing();
int resistance(beam_type flavour);
int natural_regen(int base);
bool rooted(const monster &mon);
void companion_damage(const actor *attacker,int damage);
void attack_attempt(const actor *attacker,const actor *defender);
int monster_ac_penalty(const monster &mon);
int elemental_damage(int damage,beam_type flavour,const actor *source);
int spell_damage(int damage,mid_t source);
void note_spell_damage(const actor *target,int damage,beam_type flavour,mid_t source);
int spell_failure(int raw);
int monster_armour(const monster &mon,int base);
void fire_contact(mid_t source);
int fire_protection(const actor &target,int damage,beam_type flavour);
bool swap_companion(const coord_def &destination);
int change_exhibit(int piece);
int movement_cost(int base);
int polka_finale(int mode,int applause,monster *target=nullptr);
int prepare_reagent(int type);
int throw_reagent(monster &target,int type);
int coat_reagent(int type);
bool player_rooted();
int monster_energy(const monster &mon,energy_use_type kind,int base);
bool before_monster(monster &mon);
bool summon_stationary(const monster &mon);
void summon_hit(const actor *source,const actor *target);
void after_monster(monster &mon,const coord_def &old);
bool custom_monster(const monster &mon,int &hp,int &ac,int &ev,int &hit,int &damage);
int companion_hurt(monster &mon,const actor *source,int damage);
bool passable_companion(const actor *actor);
void expire_passable_at(const coord_def &pos);
const metrics &get_metrics();
std::string save_campaign();
void load_campaign(const std::string &blob);
int manual_action(int tier,monster *target,const coord_def &aim,int option=0,int amount=3);
void validate();
}
