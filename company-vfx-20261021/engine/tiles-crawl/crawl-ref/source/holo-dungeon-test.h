#pragma once
#include "ouch.h"
namespace holo_dungeon {
bool requested();
bool active();
bool finished();
bool record_death(kill_method_type cause,const char *aux,mid_t source);
int run();
}
// Test drivers reuse the actual startup and level serializer.
void holo_dungeon_post_init(bool new_character);
void holo_dungeon_save_level();
void holo_dungeon_prep_input();
