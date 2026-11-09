#pragma once
#include <string>
#include "coord.h"
#include "ouch.h"
class actor;
class monster;
namespace holo_wrath {
void depart(const std::string &god,int piety);
void gain_xp(unsigned int xp);
void advance();
void leave_level();
std::string status();
int indicator(); // Read-only: 0 none, 1 warning, 2 urgent, 3 active wrath.
int visual_at(const coord_def &pos); // 0 none, 1/2 warning/urgent, 3 fire, 4 slime.
bool effect(const char *god);
int accuracy(bool melee);
int armour();
int shield();
int skill_penalty();
std::string description(const std::string &god);
int evasion();
int cold(int resistance);
int regen(int rate);
int healing(int amount);
int action_time(int time,bool native_slow);
void charge_action(bool native_slow);
int movement(int cost);
bool revealing();
int incoming(int damage,kill_method_type cause,mid_t source);
bool before_monster(monster &mon);
void contact(const actor *source,const actor *target);
bool decoy(const actor *actor);
void expire_at(const coord_def &pos);
bool custom_monster(const monster &mon,int &hp,int &ac,int &ev,int &hit,int &damage);
void validate();
}
