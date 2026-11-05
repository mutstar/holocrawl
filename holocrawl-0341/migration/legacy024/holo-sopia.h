#pragma once
#include "coord.h"
#include <string>
#include "holo-visual.h"

namespace holo_sopia {
struct metrics {
    int ring_casts=0, ring_ticks=0, ring_hits=0;
    int field_casts=0, field_ticks=0, field_hits=0;
    int pull_attempts=0, pulls=0, big_casts=0, detonations=0, damage=0;
};
void reset(bool enabled, int invocation, bool ring_only=false);
int choose_action(const coord_def *preferred=nullptr); // Mutates ability state/resources; caller spends returned aut.
void advance(int now); // Native post-monster phase; drains due logical aut events.
const metrics &get_metrics();
std::string save_campaign();
void load_campaign(const std::string &blob);
int manual_action(int tier,const coord_def &aim,int option=0);
void leave_level();
int cooldown();
coord_def field_centre(); // Read-only saved field centre for VFX.
bool five_active(); // Read-only visual state of the large gravity field.
std::string status();
holo_visual::effect visual_at(const coord_def &pos);
void restore_cooldown(int ready);
void validate(); // Controlled native-monster fixture checks, not win-rate trials.
}
