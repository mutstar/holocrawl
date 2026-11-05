#pragma once
#include <string>
#include "coord.h"
#include "holo-batch.h"
#include "mon-enum.h"
#include "skill-type.h"
namespace holo_campaign {
bool active();
bool combat_active();
void joined();
void leaving_god();
void save();
void load();
void leave_level();
void advance();
bool ability_menu(); // false selects the original racial/evocation abilities.
std::vector<std::string> status_lines(); // Read-only, no refresh or RNG.
std::vector<std::string> god_info(const std::string &god);
std::string unavailable(int tier,int option=0);
int invoke(int tier,monster *target=nullptr,const coord_def *aim=nullptr,int option=0,int amount=3);
void kill(monster &mon,killer_type killer,int killer_index,bool pet,bool valid);
void grant(int amount);
void penalty(int amount);
void voluntary_berserk();
void voluntary_hp_cost();
void ate_food(int subtype);
bool reactions_enabled();
void toggle_reactions();
void pulled(mid_t id);
void reaction(int kind,const monster &target);
void slime_moved(const monster &target,const coord_def &old);
void fox_attacked(const actor *source,const actor *target);
void wave_bonus(bool wide);
class reaction_scope { public: reaction_scope(int kind,const monster &target); ~reaction_scope(); };
class move_scope { coord_def old; public: bool voluntary=true; move_scope(); ~move_scope(); };
class bomb_scope { bool owner=false; public: bomb_scope(); ~bomb_scope(); };
void beam_target(monster *target,bool spell);
class command_scope { public: command_scope(); ~command_scope(); };
bool ordinary_damage(); // Excludes divine/invocation damage, including nested procs.
class damage_scope {
    bool old_damage,old_direct;
public: explicit damage_scope(bool direct); ~damage_scope();
};
int noel_skill_bonus(skill_type skill,int scale);
int noel_fighting_bonus(int scale);
int noel_armour();
int noel_shield();
bool noel_commander();
class attack_scope {
    bool owner=false;
public:
    attack_scope(actor *source,actor *target,holo_batch::attack_kind kind,bool simulated=false);
    ~attack_scope();
};
void finish_attack();
bool test_requested();
int run_tests();
}
