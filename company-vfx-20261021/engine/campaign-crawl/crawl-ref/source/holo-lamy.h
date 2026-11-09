#pragma once
#include "spell-type.h"
#include "beam-type.h"
#include "ouch.h"
class monster;
class actor;
namespace holo_lamy {
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
public: spell_scope(spell_type spell,bool ordinary);~spell_scope();
};
}
