#include "AppHdr.h"
#include "holo34-street.h"

#include <cstdlib>
#include <fstream>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <vector>

#include "branch.h"
#include "act-iter.h"
#include "coordit.h"
#include "dungeon.h"
#include "env.h"
#include "feature.h"
#include "items.h"
#include "los.h"
#include "mapdef.h"
#include "mon-util.h"
#include "player.h"
#include "terrain.h"
#include "tile-env.h"
#include "rltiles/tiledef-dngn.h"

namespace holo34 {
namespace {
const char *const key = "holocrawl_street01";
void check(bool value, const char *message) { if (!value) throw std::runtime_error(message); }
struct street_model {
    std::string seed;
    std::vector<std::string> rows;
    std::vector<int> floors, walls;
    coord_def up, down;
    int walkable = 0;
};
street_model read_model(const char *path)
{
    std::ifstream in(path);
    check(bool(in), "Cannot open street map export");
    std::string magic; std::getline(in, magic);
    check(magic == "HCSTREET1", "Unknown street map format");
    street_model m; std::getline(in, m.seed);
    check(!m.seed.empty() && m.seed.size() <= 80, "Invalid street seed");
    int width = 0, height = 0; in >> width >> height;
    check(width == GXM && height == GYM, "Street map dimensions must match engine");
    int ups = 0, downs = 0;
    for (int y = 0; y < GYM; ++y) {
        std::string row; in >> row;
        check(row.size() == GXM, "Invalid street map row");
        for (int x = 0; x < GXM; ++x) {
            const char c = row[x];
            check(c == '#' || c == '.' || c == '|' || c == '<' || c == '>', "Unknown street terrain");
            if (!in_bounds(coord_def(x,y))) check(c == '#', "Street boundary must be solid");
            if (c == '<') { m.up = coord_def(x,y); ++ups; }
            if (c == '>') { m.down = coord_def(x,y); ++downs; }
            if (c != '#' && c != '|') ++m.walkable;
        }
        m.rows.push_back(row);
    }
    check(ups == 1 && downs == 1, "Street requires exactly one stair in each direction");
    for (int n = 0; n < 2; ++n) for (int i = 0; i < GXM*GYM; ++i) {
        int value = -1; in >> value;
        check(bool(in) && value >= 0 && value < (n == 0 ? 4 : 88), "Invalid street tile index");
        (n == 0 ? m.floors : m.walls).push_back(value);
    }
    std::string extra; check(!(in >> extra), "Unexpected trailing street map data");
    std::queue<coord_def> queue; std::vector<bool> visited(GXM*GYM, false);
    queue.push(m.up); visited[m.up.y*GXM+m.up.x] = true; int count = 0;
    const coord_def steps[] = {coord_def(1,0),coord_def(-1,0),coord_def(0,1),coord_def(0,-1)};
    while (!queue.empty()) {
        const auto p = queue.front(); queue.pop(); ++count;
        for (const auto &d : steps) {
            const auto q = p+d;
            if (!in_bounds(q)) continue;
            const int i=q.y*GXM+q.x; const char c=m.rows[q.y][q.x];
            if (!visited[i] && c!='#' && c!='|') {visited[i]=true;queue.push(q);}
        }
    }
    check(count == m.walkable && visited[m.down.y*GXM+m.down.x], "Street floor disconnected");
    return m;
}
void set_tile(unsigned short &tile, unsigned short &saved_name, const std::string &name)
{
    tileidx_t index = 0;
    check(tile_dngn_index(name.c_str(), &index), "Street atlas tile is missing");
    tile = index;
    saved_name = store_tilename_get_index(name);
}
void apply(const street_model &m)
{
    for (int y=0; y<GYM; ++y) for (int x=0; x<GXM; ++x) {
        const coord_def p(x,y); const int i=y*GXM+x; const char c=m.rows[y][x];
        env.grid(p) = c=='#' ? DNGN_ROCK_WALL : c=='|' ? DNGN_GRATE
                    : c=='<' ? DNGN_STONE_STAIRS_UP_I : c=='>' ? DNGN_STONE_STAIRS_DOWN_I : DNGN_FLOOR;
        auto &flv=tile_env.flv(p);
        set_tile(flv.floor,flv.floor_idx,"holo_street_floor"+std::to_string(m.floors[i]));
        set_tile(flv.wall,flv.wall_idx,"holo_street_wall"+std::to_string(m.walls[i]));
        if (c=='<' || c=='>' || c=='|')
            set_tile(flv.feat,flv.feat_idx,c=='<' ? "holo_street_up12" : c=='>' ? "holo_street_down06" : "holo_street_fence");
        // Keep the prototype floor empty even if a later generic allocator runs.
        env.level_map_mask(p) |= MMT_NO_MONS | MMT_NO_ITEM | MMT_NO_TRAP;
    }
    env.properties[key]=1;
    env.properties["holocrawl_street_seed"]=m.seed;
    env.level_build_method="HoloCrawl approved street generator / "+m.seed;
}
class map_opacity : public opacity_func {
public:
    CLONE(map_opacity)
    opacity_type operator()(const coord_def &p) const override
    { return !in_bounds(p) || feat_is_opaque(env.grid(p)) ? OPC_OPAQUE : OPC_CLEAR; }
};
}
bool build_street_floor()
{
    const char *path=std::getenv("HOLOCRAWL_STREET01_MAP");
    if (!path || !*path || you.where_are_you!=BRANCH_DUNGEON || you.depth!=1) return false;
    apply(read_model(path));
    return true;
}
bool is_street_floor() { return env.properties.exists(key); }
std::string street_native_test()
{
    const char *path=std::getenv("HOLOCRAWL_STREET01_MAP");
    check(path && *path, "Native street test requires exported map path");
    const auto m=read_model(path);
    dgn_reset_level(); apply(m);
    int checked=0, fences=0, stairs=0;
    for (int y=0;y<GYM;++y)for(int x=0;x<GXM;++x) {
        const coord_def p(x,y);const char c=m.rows[y][x];const auto feature=env.grid(p);
        check(feat_is_solid(feature)==(c=='#'||c=='|'),"Native collision differs from exported map");
        check(feat_is_opaque(feature)==(c=='#'),"Native opacity differs from exported map");
        if(c=='|')++fences;
        if(c=='<'||c=='>')++stairs;
        check(tile_env.flv(p).floor_idx && tile_env.flv(p).wall_idx,"Tile names not registered for native saves");
        ++checked;
    }
    check(stairs==2 && fences>0,"Expected stair pair and transparent fences");
    check(!monster_iterator(),"Street must contain no monsters");
    for (int i=0;i<MAX_ITEMS;++i)check(!env.item[i].defined(),"Street must contain no ground items");
    map_opacity opacity;
    los_grid visible; losight(visible,m.up,opacity,circle_def(7,C_SQUARE));
    check(visible(coord_def(0,0)),"Native sight failed at arrival");
    std::ostringstream out;
    out<<"{\"status\":\"passed\",\"terrainCells\":"<<checked<<",\"walkable\":"<<m.walkable
       <<",\"fences\":"<<fences<<",\"stairs\":2,\"monsters\":0,\"groundItems\":0,\"nativeCollisionMatches\":true,\"nativeOpacityMatches\":true,\"saveTileNamesRegistered\":true}";
    return out.str();
}
}
