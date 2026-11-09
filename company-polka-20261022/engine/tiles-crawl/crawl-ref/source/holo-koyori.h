#pragma once
#include "spell-type.h"
#include "beam-type.h"
#include "ouch.h"
#include <string>
class monster;
class actor;
struct coord_def;
namespace holo_koyori {
bool enabled();
bool direct_cast();
void initialise();
bool attack_spell(spell_type spell);
bool range_bonus(spell_type spell,int maxrange);
int next_type();
int action();
void tick(int at);
int movement(const monster &mon, int base);
int mark(const coord_def &p);
std::string status();
void damage(monster &mon,const actor *source,int amount,beam_type flavour,kill_method_type kind);
int reaction_damage(int raw,int pair,bool critical);
class spell_scope {
public: struct context;
private: context *previous,*cast;
public: spell_scope(spell_type spell,bool ordinary,const coord_def &aim);~spell_scope();
};
}
