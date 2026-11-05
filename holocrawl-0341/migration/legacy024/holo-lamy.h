#pragma once
#include "spell-type.h"
#include "beam-type.h"
#include "ouch.h"
class monster;
class actor;
struct coord_def;
namespace holo_lamy {
int cloud_use(const coord_def &pos);
void cloud_created(const coord_def &pos,const actor *agent);
void cloud_copy(const coord_def &from,const coord_def &to);
void cloud_clear(const coord_def &pos);
void cloud_swap(const coord_def &a,const coord_def &b);
bool attack_spell(spell_type spell);
int power_bonus();
int power(spell_type spell,int base);
int evasion_penalty();
int action();
void tick(int at);
void damage(monster &mon,const actor *source,int amount,beam_type flavour,kill_method_type kind);
class spell_scope {
public: struct context;
private: context *previous,*cast;
public: spell_scope(spell_type spell,bool ordinary,bool tool=false,int cloud=0);~spell_scope();
};
}
