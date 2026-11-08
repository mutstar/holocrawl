#include "AppHdr.h"
#include "holo34-city.h"

#include <cstdlib>
#include <fstream>
#include <set>
#include <queue>
#include "unwind.h"
#include "los.h"
#include "movement.h"
#include "initfile.h"
#include "view.h"
#include "tile-flags.h"
#include "monster.h"
#include "mon-place.h"
#include "mon-info.h"
#include "mgen-data.h"
#include "tiledoll.h"
#include "tilepick-p.h"
#include "rltiles/tiledef-player.h"
#include "rltiles/tiledef-main.h"
#include <sstream>
#include <stdexcept>

#include "act-iter.h"
#include "branch.h"
#include "coordit.h"
#include "dungeon.h"
#include "env.h"
#include "feature.h"
#include "items.h"
#include "mapdef.h"
#include "player.h"
#include "random.h"
#include "state.h"
#include "tags.h"
#include "terrain.h"
#include "tile-env.h"
#include "tilepick.h"
#include "rltiles/tiledef-dngn.h"

namespace holo34 {
namespace {
const char *const mode_key = "holocrawl_city77_enabled";
const char *const plan_key = "holocrawl_city77_plan";
const char *const facility_key = "holocrawl_city77_facility";
const char *const origin_key = "holocrawl_city77_origin";
const int city_floors = 14;

struct facility_spec {
    const char *id;
    int width, height;
    std::vector<std::string> rows;
};
const facility_spec facilities[] = {
#include "holo34-facilities.inc"
};
const int facility_count = sizeof(facilities) / sizeof(facilities[0]);

void check(bool value, const char *message)
{
    if (!value)
        throw std::runtime_error(message);
}

std::string make_plan(uint64_t seed)
{
    // A private RNG leaves layout RNG untouched and reserves the same facility
    // for a depth even when floors are generated out of order or vetoed.
    rng::subgenerator random(seed, 0x484f4c4f43495459ULL);
    std::vector<int> remaining;
    for (int i = 0; i < facility_count; ++i)
        remaining.push_back(i);
    std::string plan(city_floors, '-');
    for (int depth = 0; depth < city_floors; ++depth) {
        if (!coinflip() || remaining.empty())
            continue;
        const int index = random2(remaining.size());
        plan[depth] = 'A' + remaining[index];
        remaining.erase(remaining.begin() + index);
    }
    return plan;
}

const std::string &saved_plan()
{
    if (!you.props.exists(plan_key)) {
        you.props[plan_key] = make_plan(you.game_seed);
        you.props[mode_key] = true;
    }
    const auto &plan = you.props[plan_key].get_string();
    check(plan.size() == city_floors, "Invalid saved city facility plan");
    std::set<char> seen;
    for (char entry : plan) {
        check(entry == '-' || (entry >= 'A' && entry < 'A' + facility_count),
              "Unknown saved city facility");
        check(entry == '-' || seen.insert(entry).second,
              "Duplicate facility in saved city plan");
    }
    return plan;
}

bool fits(const facility_spec &facility, const coord_def &origin)
{
    for (int y = 0; y < facility.height; ++y)
        for (int x = 0; x < facility.width; ++x)
            if (env.grid(origin + coord_def(x, y)) != DNGN_ROCK_WALL)
                return false;
    // Preserve every existing corridor and stair. Connect only through the
    // reviewed south entrance, directly onto an existing ordinary floor.
    for (int x = 0; x < facility.width; ++x) {
        const char cell = facility.rows.back()[x];
        if ((cell == '.' || cell == '+')
            && env.grid(origin + coord_def(x, facility.height)) == DNGN_FLOOR)
            return true;
    }
    return false;
}

dungeon_feature_type native_feature(char cell)
{
    switch (cell) {
    case '#': return DNGN_ROCK_WALL;
    case 'F': return DNGN_GRANITE_STATUE;
    case 'G': return DNGN_CLEAR_ROCK_WALL;
    case '+': return DNGN_CLOSED_DOOR;
    default: return DNGN_FLOOR;
    }
}

void named_tile(unsigned short &tile, unsigned short &saved_name,
                const std::string &name)
{
    tileidx_t index = 0;
    check(tile_dngn_index(name.c_str(), &index), "Missing native city atlas tile");
    tile = index;
    saved_name = store_tilename_get_index(name);
}

std::string facility_tile_name(int selected, int index)
{
    return std::string("holo_facility_") + facilities[selected].id
           + "_" + std::to_string(index);
}


#include "holo34-art107.inc"
bool city_perimeter107(const coord_def &p)
{
    if (!env.properties.exists(facility_key)) return false;
    const int selected=env.properties[facility_key].get_int();
    if (selected<0) return false;
    const auto q=p-env.properties[origin_key].get_coord();
    const auto &f=facilities[selected];
    return q.x>=0 && q.y>=0 && q.x<f.width && q.y<f.height
        && f.rows[q.y][q.x]=='#'
        && (q.x==0 || q.y==0 || q.x==f.width-1 || q.y==f.height-1);
}
bool city_solid107(const coord_def &p)
{
    if (p.x<0 || p.y<0 || p.x>=GXM || p.y>=GYM) return false;
    const int selected=env.properties.exists(facility_key)?env.properties[facility_key].get_int():-1;
    if (selected>=0) {
        const auto q=p-env.properties[origin_key].get_coord();const auto &f=facilities[selected];
        if (q.x>0 && q.y>0 && q.x<f.width-1 && q.y<f.height-1
            && (f.rows[q.y][q.x]=='#' || f.rows[q.y][q.x]=='G')) return false;
    }
    return feat_is_wall(env.grid(p)) || feat_is_door(env.grid(p))
        || env.grid(p)==DNGN_GRANITE_STATUE || env.grid(p)==DNGN_TREE;
}
std::string city_wall_name107(const coord_def &p)
{
    const coord_def dirs[]={ {0,-1},{1,-1},{1,0},{1,1},{0,1},{-1,1},{-1,0},{-1,-1} };
    int mask=0;for(int i=0;i<8;++i) if(city_solid107(p+dirs[i]))mask|=1<<i;
    const auto variant=(you.game_seed ^ uint64_t(p.x*374761393u) ^ uint64_t(p.y*668265263u))%8;
    return "holo_city_wall78_"+std::to_string(mask)+"_"+std::to_string(variant);
}

void export_native_floor(const std::string &directory, uint64_t seed, int depth)
{
    unwind_var<time_t> export_birth(you.birth_time, time_t(107));
    unwind_var<unsigned int> export_frame(you.frame_no, 0);
    std::vector<tileidx_t> palette;
    const auto palette_index = [&palette](tileidx_t tile) {
        const auto found = std::find(palette.begin(), palette.end(), tile);
        if (found != palette.end())
            return int(found - palette.begin());
        palette.push_back(tile);
        return int(palette.size()) - 1;
    };
    std::vector<int> floors, features, overlays, passability, opacity;
    std::vector<std::string> rows;
    struct preview_door { int x, y, opened; };
    std::vector<preview_door> doors;
    for (int y = 0; y < GYM; ++y) {
        std::string row;
        for (int x = 0; x < GXM; ++x) {
            const coord_def position(x, y);
            const auto feature = env.grid(position);
            char cell = '.';
            if (feature == DNGN_CLOSED_DOOR)
                cell = '+';
            else if (feat_is_stone_stair(feature) || feature == DNGN_EXIT_DUNGEON)
                cell = feat_stair_direction(feature) == CMD_GO_UPSTAIRS ? '<' : '>';
            else if (feat_is_solid(feature))
                cell = feat_is_opaque(feature) ? '#' : 'G';
            else if (feature == DNGN_DEEP_WATER || feature == DNGN_LAVA)
                cell = '~';
            row += cell;
            env.map_knowledge(position).set_feature(feature);
            tileidx_t tile = tileidx_feature(position);
            floors.push_back(palette_index(tile_env.flv(position).floor));
            features.push_back(palette_index(tile));
            const auto decal=city_wall_decal_tile(position);
            overlays.push_back(decal?palette_index(decal):-1);
            passability.push_back(you.can_pass_through_feat(feature)?1:0);
            opacity.push_back(int(opc_default(position)));
            if (cell == '+') {
                tileidx_t opened = city_door_tile(position, DNGN_OPEN_DOOR);
                if (!opened)
                    opened = tileidx_feature_base(DNGN_OPEN_DOOR);
                doors.push_back({x, y, palette_index(opened)});
            }
        }
        rows.push_back(row);
    }
    std::ofstream out(directory + "/map-" + std::to_string(seed) + "-"
                      + std::to_string(depth) + ".json");
    check(bool(out), "Cannot write native floor browser export");
    const int selected = env.properties[facility_key].get_int();
    out << "{\"seed\":" << seed << ",\"depth\":" << depth
        << ",\"width\":" << GXM << ",\"height\":" << GYM
        << ",\"facility\":";
    if (selected < 0)
        out << "null,\"origin\":null";
    else {
        const auto origin = env.properties[origin_key].get_coord();
        out << '\"' << facilities[selected].id << "\",\"origin\":{\"x\":"
            << origin.x << ",\"y\":" << origin.y << ",\"width\":"
            << facilities[selected].width << ",\"height\":"
            << facilities[selected].height << '}';
    }
    out << ",\"rows\":[";
    for (int y = 0; y < GYM; ++y) {
        if (y) out << ',';
        out << '\"' << rows[y] << '\"';
    }
    out << "],\"palette\":[";
    for (size_t index = 0; index < palette.size(); ++index) {
        if (index) out << ',';
        const auto tile = palette[index];
        const auto &info = tile_dngn_info(tile);
        const char *atlas = tile < TILE_FLOOR_MAX ? "floor" : tile < TILE_WALL_MAX ? "wall" : "feat";
        out << "{\"atlas\":\"" << atlas << "\",\"sx\":" << info.sx
            << ",\"sy\":" << info.sy << ",\"width\":" << info.ex - info.sx
            << ",\"height\":" << info.ey - info.sy << ",\"dx\":" << int(info.offset_x)
            << ",\"dy\":" << int(info.offset_y) << '}';
    }
    const auto write_indices = [&out](const char *key, const std::vector<int> &indices) {
        out << "],\"" << key << "\":[";
        for (size_t index = 0; index < indices.size(); ++index) {
            if (index) out << ',';
            out << indices[index];
        }
    };
    write_indices("floors", floors);
    write_indices("features", features);
    write_indices("overlays", overlays);
    write_indices("passable", passability);
    write_indices("opacity", opacity);
    out << "],\"doors\":[";
    for (size_t index = 0; index < doors.size(); ++index) {
        if (index) out << ',';
        const auto &door = doors[index];
        out << "{\"x\":" << door.x << ",\"y\":" << door.y
            << ",\"opened\":" << door.opened << ",\"linked\":[";
        std::set<coord_def> linked;find_connected_identical(coord_def(door.x,door.y),linked);
        bool first_link=true;for(const auto &p:linked){if(!first_link)out<<',';first_link=false;out<<'['<<p.x<<','<<p.y<<']';}
        out << "]}";
    }
    out << "]}\n";
}
}

bool city_run_enabled()
{
    if (you.props.exists(mode_key))
        return you.props[mode_key].get_bool();
    const char *mode = std::getenv("HOLOCRAWL_CITY77");
    return mode && std::string(mode) == "1";
}

bool city_floor_enabled()
{
    return city_run_enabled() && you.where_are_you == BRANCH_DUNGEON
           && you.depth >= 1 && you.depth <= city_floors;
}

void place_city_facility()
{
    const char entry = saved_plan()[you.depth - 1];
    env.properties[facility_key] = -1;
    env.properties["holocrawl_city77"] = true;
    if (entry == '-')
        return;
    const int selected = entry - 'A';
    const auto &facility = facilities[selected];
    std::vector<coord_def> candidates;
    for (int y = 2; y < GYM - facility.height - 2; ++y)
        for (int x = 2; x < GXM - facility.width - 2; ++x) {
            const coord_def origin(x, y);
            if (fits(facility, origin))
                candidates.push_back(origin);
        }
    if (candidates.empty())
        throw dgn_veto_exception("No connected space for reserved city facility");
    const auto origin = candidates[random2(candidates.size())];
    for (int y = 0; y < facility.height; ++y)
        for (int x = 0; x < facility.width; ++x) {
            const coord_def position = origin + coord_def(x, y);
            env.grid(position) = native_feature(facility.rows[y][x]);
            env.level_map_mask(position) |= MMT_VAULT | MMT_NO_MONS
                                           | MMT_NO_ITEM | MMT_NO_TRAP;
        }
    env.properties[facility_key] = selected;
    env.properties[origin_key] = origin;
    env.level_build_method += " / city facility " + std::string(facility.id);
}

void decorate_city_floor()
{
    for (rectangle_iterator it(0); it; ++it) {
        const auto p = *it;
        auto &flavour = tile_env.flv(p);
        const auto floor = (p.x * 17 + p.y * 31 + you.game_seed) % 4;
        named_tile(flavour.floor, flavour.floor_idx,
                   "holo_street_floor" + std::to_string(floor));
        const coord_def neighbours[] = {
            coord_def(0,-1), coord_def(1,-1), coord_def(1,0), coord_def(1,1),
            coord_def(0,1), coord_def(-1,1), coord_def(-1,0), coord_def(-1,-1)
        };
        int mask = 0;
        for (int direction = 0; direction < 8; ++direction) {
            const auto next = p + neighbours[direction];
            if (!in_bounds(next) || feat_is_wall(env.grid(next))
                || feat_is_door(env.grid(next)) || env.grid(next) == DNGN_GRANITE_STATUE
                || env.grid(next) == DNGN_TREE)
                mask |= 1 << direction;
        }
        const uint64_t texture = (you.game_seed ^ uint64_t(p.x * 374761393u)
                                  ^ uint64_t(p.y * 668265263u)) % 8;
        const auto wall_name = city_wall_name107(p);
        (void)mask; (void)texture;
        named_tile(flavour.wall, flavour.wall_idx, wall_name);
        if (feat_is_wall(env.grid(p)) && feat_is_opaque(env.grid(p)))
            named_tile(flavour.feat, flavour.feat_idx, wall_name);
        if (feat_is_stone_stair(env.grid(p)) || env.grid(p) == DNGN_EXIT_DUNGEON) {
            const bool up = feat_stair_direction(env.grid(p)) == CMD_GO_UPSTAIRS;
            named_tile(flavour.feat, flavour.feat_idx,
                       up ? "holo_street_up12" : "holo_street_down06");
        }
        env.level_map_mask(p) |= MMT_NO_MONS | MMT_NO_ITEM | MMT_NO_TRAP;
    }
    const int selected = env.properties[facility_key].get_int();
    if (selected < 0)
        return;
    const auto origin = env.properties[origin_key].get_coord();
    const auto &facility = facilities[selected];
    for (int y = 0; y < facility.height; ++y)
        for (int x = 0; x < facility.width; ++x) {
            auto &flavour = tile_env.flv(origin + coord_def(x, y));
            const auto name = facility_tile_name(selected, y * facility.width + x);
            if (city_perimeter107(origin+coord_def(x,y))) {
                const auto wall=city_wall_name107(origin+coord_def(x,y));
                named_tile(flavour.floor,flavour.floor_idx,wall);
                named_tile(flavour.wall,flavour.wall_idx,wall);
                named_tile(flavour.feat,flavour.feat_idx,wall);
                continue;
            }
            named_tile(flavour.floor, flavour.floor_idx, name);
            named_tile(flavour.wall, flavour.wall_idx, name);
            if (facility.rows[y][x] != '.')
                named_tile(flavour.feat, flavour.feat_idx, name);
        }
}


tileidx_t city_wall_decal_tile(const coord_def &position)
{
    if (!city_perimeter107(position)) return 0;
    const int selected=env.properties[facility_key].get_int();
    const auto p=position-env.properties[origin_key].get_coord();
    const int index=p.y*facilities[selected].width+p.x;
    if(!city_decals107[selected].count(index))return 0;
    tileidx_t tile=0;check(tile_dngn_index(facility_tile_name(selected,index).c_str(),&tile),"Missing107 decal");return tile;
}
tileidx_t city_door_tile(const coord_def &position, dungeon_feature_type feature)
{
    if(!env.properties.exists("holocrawl_city77") || (feature!=DNGN_CLOSED_DOOR && feature!=DNGN_OPEN_DOOR))return 0;
    std::string name=feature==DNGN_OPEN_DOOR?"holo_city107_door_open":"holo_city107_door_closed";
    const int selected=env.properties[facility_key].get_int();
    if(selected>=0){
        const auto p=position-env.properties[origin_key].get_coord();const auto &f=facilities[selected];
        if(p.x>=0&&p.y>=0&&p.x<f.width&&p.y<f.height&&f.rows[p.y][p.x]=='+'){
            name=facility_tile_name(selected,p.y*f.width+p.x);if(feature==DNGN_OPEN_DOOR)name+="_open";
        }
    }
    tileidx_t tile=0;check(tile_dngn_index(name.c_str(),&tile),"Missing107 door tile");return tile;
}
namespace {
#include "holo34-play107.inc"
}

std::string city_native_test(const std::string &output_directory)
{
    check(city_run_enabled(), "Native city test requires HOLOCRAWL_CITY77=1");
    // Freeze visual-only animation during scripted replay comparisons.
    Options.tile_water_anim=false;Options.tile_misc_anim=false;
    unwind_var<time_t> test_birth(you.birth_time, time_t(107));
    unwind_var<unsigned int> test_frame(you.frame_no, 0);
    // Explicit, isolated art-review export. Ordinary runs and the regression
    // cohort below retain their normal facility plan and layout distribution.
    if (const char *preview_seed = std::getenv("HOLOCRAWL_CITY_REVIEW_SEED")) {
        const std::string value(preview_seed);
        check(!value.empty() && value.find_first_not_of("0123456789") == std::string::npos,
              "Review seed must be an unsigned decimal integer");
        const uint64_t seed = std::stoull(value);
        rng::seed(seed);
        init_level_connectivity();
        you.game_seed = seed;
        you.where_are_you = BRANCH_DUNGEON;
        you.depth = 1;
        you.props[plan_key] = std::string(city_floors, '-');
        check(builder(true), "Native review floor generation failed");
        check(env.properties[facility_key].get_int() == -1,
              "Facility found in facility-free wall review");
        check(dgn_count_disconnected_zones(false) == 1,
              "Native review floor is disconnected");
        export_native_floor(output_directory, seed, 1);
        std::ostringstream report;
        report << "{\"status\":\"passed\",\"seed\":" << seed
               << ",\"nativeFloors\":1,\"depth\":1,\"facility\":false,\"connected\":true}";
        std::ofstream file(output_directory + "/validation.json");
        check(bool(file), "Cannot write native review report");
        file << report.str() << '\n';
        return report.str();
    }

    if(const char *chosen=std::getenv("HOLOCRAWL_FACILITY107")) {
        const char *text=std::getenv("HOLOCRAWL_SEED107");check(text,"Need107 seed");
        const uint64_t seed=std::stoull(text);int selected=-1;
        for(int i=0;i<facility_count;++i)if(std::string(chosen)==facilities[i].id)selected=i;
        check(selected>=0,"Unknown107 facility");rng::seed(seed);init_level_connectivity();
        you.game_seed=seed;you.where_are_you=BRANCH_DUNGEON;you.depth=1;
        std::string plan(city_floors,'-');plan[0]='A'+selected;you.props[plan_key]=plan;
        check(builder(true),"Forced107 generation failed");
        check(env.properties[facility_key].get_int()==selected,"Forced107 facility missing");
        check(dgn_count_disconnected_zones(false)==1,"Forced107 disconnected");
        export_native_floor(output_directory,seed,1);
        city_probe107(output_directory,seed,1);
        std::ofstream out(output_directory+"/validation.json");out<<"{\"status\":\"passed\",\"nativeFloors\":1,\"forcedReview\":true}";
        return "forced107 passed";
    }

    int rolls = 0, placements = 0, first_floor_placements = 0;
    for (uint64_t seed = 0; seed < 20000; ++seed) {
        const auto before = rng::peek_uint64();
        const auto plan = make_plan(seed);
        check(before == rng::peek_uint64(), "Facility plan changed the layout RNG");
        check(plan == make_plan(seed), "Facility plan is not reproducible");
        std::set<char> unique;
        for (char entry : plan)
            check(entry == '-' || unique.insert(entry).second, "Duplicate facility");
        rolls += city_floors;
        placements += unique.size();
        first_floor_placements += plan[0] != '-';
    }
    check(first_floor_placements > 9600 && first_floor_placements < 10400,
          "Observed facility frequency differs from 50 percent");
    you.where_are_you = BRANCH_DUNGEON;
    you.game_seed = 77001;
    you.props.erase(plan_key);
    const auto failure_plan = saved_plan();
    const auto reserved_depth = failure_plan.find_first_not_of('-');
    check(reserved_depth != std::string::npos, "Failure test needs a reserved facility");
    you.depth = reserved_depth + 1;
    dgn_reset_level();
    env.grid.init(DNGN_FLOOR);
    bool vetoed = false;
    try {
        place_city_facility();
    } catch (const dgn_veto_exception &) {
        vetoed = true;
    }
    check(vetoed && saved_plan() == failure_plan,
          "Failed placement must veto the floor without rerolling the facility");
    std::set<int> covered;
    int floors = 0, doors = 0;
    for (uint64_t seed = 10786001; seed < 10786013; ++seed) {
        rng::seed(seed);
        init_level_connectivity();
        you.game_seed = seed;
        you.where_are_you = BRANCH_DUNGEON;
        you.props.erase(plan_key);
        const auto plan = saved_plan();
        std::vector<unsigned char> bytes;
        writer output(&bytes);
        you.props.write(output);
        CrawlHashTable restored;
        reader input(bytes, TAG_MINOR_VERSION);
        restored.read(input);
        check(restored[plan_key].get_string() == plan, "Saved facility plan changed");
        you.props = restored;
        // Both ordinary and reverse floor order must obey the persisted plan.
        for (int index = 0; index < city_floors; ++index) {
            const int depth = seed % 2 ? index + 1 : city_floors - index;
            you.depth = depth;
            check(builder(true), "Native city floor generation failed");
            std::printf("City seed %s floor %d: %s\n", std::to_string(seed).c_str(),
                        depth, env.level_build_method.c_str());
            std::fflush(stdout);
            const int selected = env.properties[facility_key].get_int();
            check(selected == (plan[depth - 1] == '-' ? -1 : plan[depth - 1] - 'A'),
                  "Actual placement differs from saved facility plan");
            if (selected >= 0) {
                covered.insert(selected);
                const auto &facility = facilities[selected];
                const auto origin = env.properties[origin_key].get_coord();
                for (int y = 0; y < facility.height; ++y)
                    for (int x = 0; x < facility.width; ++x) {
                        const auto position = origin + coord_def(x, y);
                        check(env.grid(position) == native_feature(facility.rows[y][x]),
                              "Native collision differs from reviewed facility");
                        check(tile_env.flv(position).floor_idx != 0,
                              "Facility tile name missing from save data");
                        if (facility.rows[y][x] == '+') {
                            check(city_door_tile(position, DNGN_CLOSED_DOOR)
                                  != city_door_tile(position, DNGN_OPEN_DOOR),
                                  "Facility door does not change artwork");
                            ++doors;
                        }
                    }
            }
            check(!monster_iterator(), "City test floor contains monsters");
            for (int item_index = 0; item_index < MAX_ITEMS; ++item_index)
                check(!env.item[item_index].defined(), "City test floor contains loot");
            check(dgn_count_disconnected_zones(false) == 1,
                  "City floor or facility entrance is disconnected");
            city_probe107(output_directory,seed,depth);
            std::vector<dungeon_feature_type> saved_terrain;
            for (int y = 0; y < GYM; ++y)
                for (int x = 0; x < GXM; ++x)
                    saved_terrain.push_back(env.grid(coord_def(x, y)));
            std::vector<unsigned char> level_bytes;
            writer level_output(&level_bytes);
            tag_write(TAG_LEVEL, level_output);
            dgn_reset_level();
            reader level_input(level_bytes, TAG_MINOR_VERSION);
            tag_read(level_input, TAG_LEVEL);
            check(env.properties[facility_key].get_int() == selected,
                  "Facility identity changed after native level save/load");
            check(dgn_count_disconnected_zones(false) == 1,
                  "Native level save/load changed connectivity");
            for (int y = 0; y < GYM; ++y)
                for (int x = 0; x < GXM; ++x)
                    check(env.grid(coord_def(x, y)) == saved_terrain[y * GXM + x],
                          "Native save/load changed a terrain cell");
            ++floors;
            export_native_floor(output_directory, seed, depth);
        }
    }
    check(covered.size() == facility_count, "Native tests did not cover all nine facilities");
    std::ostringstream report;
    report << "{\"status\":\"passed\",\"nativeFloors\":" << floors
           << ",\"facilitiesCovered\":" << covered.size()
           << ",\"doorChecks\":" << doors << ",\"scheduleSeeds\":20000"
           << ",\"scheduledFloors\":" << rolls << ",\"scheduledFacilities\":" << placements
           << ",\"firstFloorPlacements\":" << first_floor_placements
           << ",\"savePlanRoundtrip\":true,\"nativeLevelSaveRoundtrip\":true"
           << ",\"forwardAndReverseGeneration\":true,\"placementFailureKeepsPlan\":true"
           << ",\"layoutRngUnchanged\":true}";
    std::ofstream file(output_directory + "/validation.json");
    check(bool(file), "Cannot write city validation report");
    file << report.str() << '\n';
    return report.str();
}
}
