#pragma once

#include "skill-type.h"

// Hooks are inert outside the explicit engine benchmark for now.
// No unimplemented god is substituted by a flat damage multiplier.
bool holo_engine_benchmark_requested();
int holo_run_engine_benchmark();
bool holo_benchmark_active();
bool holo_benchmark_finished();
bool holo_record_benchmark_death();
bool holo_record_benchmark_banishment();
int holo_armour_bonus();
int holo_shield_bonus();
int holo_skill_bonus(skill_type skill, int scale);
int holo_fighting_skill(int scale);
int holo_melee_damage(int damage);
bool holo_force_immune();
void holo_reset_validation_fixture();
void holo_validation_spend_time(int aut);
void holo_reduce_poison_time(int percent);
bool holo_spell_target(class dist &target,struct bolt &beam,int range);
