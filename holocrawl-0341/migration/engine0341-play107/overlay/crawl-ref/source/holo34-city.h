#pragma once

#include <string>
#include "coord-def.h"
#include "dungeon-feature-type.h"
#include "rltiles/tiledef_defines.h"

namespace holo34 {
bool city_floor_enabled();
bool city_run_enabled();
void place_city_facility();
void decorate_city_floor();
tileidx_t city_door_tile(const coord_def &position, dungeon_feature_type feature);
tileidx_t city_wall_decal_tile(const coord_def &position);
std::string city_native_test(const std::string &output_directory);
}
