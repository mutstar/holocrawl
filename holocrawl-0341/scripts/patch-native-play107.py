"""Install art107 integration and native runtime probes in the isolated copy."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'analysis/native-play107-01';S=RUN/'engine/crawl-ref/source'
p=S/'holo34-city.h';s=p.read_text();s=s.replace('std::string city_native_test', 'tileidx_t city_wall_decal_tile(const coord_def &position);\nstd::string city_native_test');p.write_text(s)
p=S/'holo34-city.cc';s=p.read_text();assert 'city_decals107' not in s
s=s.replace('#include <set>','#include <set>\n#include <queue>\n#include "unwind.h"\n#include "los.h"\n#include "movement.h"\n#include "initfile.h"\n#include "view.h"\n#include "tile-flags.h"\n#include "monster.h"\n#include "mon-place.h"\n#include "mon-info.h"\n#include "mgen-data.h"\n#include "tiledoll.h"\n#include "tilepick-p.h"\n#include "rltiles/tiledef-player.h"\n#include "rltiles/tiledef-main.h"')
anchor='void export_native_floor('
helper=r'''
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
'''
s=s.replace(anchor,helper+'\n'+anchor,1)
s=s.replace('std::vector<int> floors, features;','std::vector<int> floors, features, overlays, passability, opacity;')
s=s.replace('features.push_back(palette_index(tile));','''features.push_back(palette_index(tile));
            const auto decal=city_wall_decal_tile(position);
            overlays.push_back(decal?palette_index(decal):-1);
            passability.push_back(you.can_pass_through_feat(feature)?1:0);
            opacity.push_back(int(opc_default(position)));''')
s=s.replace('write_indices("features", features);','write_indices("features", features);\n    write_indices("overlays", overlays);\n    write_indices("passable", passability);\n    write_indices("opacity", opacity);')
# Use an adjacency-dependent base at every perimeter; decals are rendered in
# the engine's dungeon overlay layer before actors and items.
s=s.replace('const auto wall_name = "holo_city_wall78_" + std::to_string(mask)\n                               + "_" + std::to_string(texture);','const auto wall_name = city_wall_name107(p);\n        (void)mask; (void)texture;')
anchor='''            const auto name = facility_tile_name(selected, y * facility.width + x);
            named_tile(flavour.floor, flavour.floor_idx, name);'''
s=s.replace(anchor,'''            const auto name = facility_tile_name(selected, y * facility.width + x);
            if (city_perimeter107(origin+coord_def(x,y))) {
                const auto wall=city_wall_name107(origin+coord_def(x,y));
                named_tile(flavour.floor,flavour.floor_idx,wall);
                named_tile(flavour.wall,flavour.wall_idx,wall);
                named_tile(flavour.feat,flavour.feat_idx,wall);
                continue;
            }
            named_tile(flavour.floor, flavour.floor_idx, name);''')
start=s.index('tileidx_t city_door_tile(');end=s.index('\nstd::string city_native_test',start)
s=s[:start]+r'''
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
''' +s[end:]
anchor='''    int rolls = 0, placements = 0, first_floor_placements = 0;'''
branch=r'''
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
'''
s=s.replace(anchor,branch+'\n'+anchor)
s=s.replace('for (uint64_t seed = 77001; seed < 77013; ++seed)', 'for (uint64_t seed = 10786001; seed < 10786013; ++seed)')
s=s.replace('''            std::vector<dungeon_feature_type> saved_terrain;''','''            city_probe107(output_directory,seed,depth);
            std::vector<dungeon_feature_type> saved_terrain;''')
s=s.replace('''            if (seed < 77004)
                export_native_floor(output_directory, seed, depth);''','''            export_native_floor(output_directory, seed, depth);''')
p.write_text(s)
p=S/'tilecell.cc';s=p.read_text();s=s.replace('#include "AppHdr.h"','#include "AppHdr.h"\n#include "holo34-city.h"',1)
anchor='''    if (player_in_branch(BRANCH_SHOALS))'''
s=s.replace(anchor,'''    if (const auto decal=holo34::city_wall_decal_tile(gc)) cell.add_overlay(decal);

'''+anchor,1);p.write_text(s)
plan=json.loads((RUN/'plan.json').read_text());plan['status']='native-source-patched';(RUN/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Patched isolated engine: dynamic wall107/decal integration, basic doors and native probe hook.')

# Floor-atlas facility decals need a separate local-renderer pass after walls.
p=S/'tiledgnbuf.h';text=p.read_text().replace('    TileBuffer m_buf_wall;','    TileBuffer m_buf_wall;\n    TileBuffer m_buf_city_decal;');p.write_text(text)
p=S/'tiledgnbuf.cc';text=p.read_text().replace('m_buf_wall(&im->get_texture(TEX_WALL)),','m_buf_wall(&im->get_texture(TEX_WALL)),\n    m_buf_city_decal(&im->get_texture(TEX_FLOOR)),')
text=text.replace('    m_buf_wall.clear();','    m_buf_wall.clear();\n    m_buf_city_decal.clear();').replace('    m_buf_wall.draw();','    m_buf_wall.draw();\n    m_buf_city_decal.draw();')
needle='            if (tile < TILE_DNGN_MAX)\n                add_dngn_tile(tile, x, y);'
replace='            if (tile < TILE_FLOOR_MAX && std::string(tile_floor_name(tile)).find("holo_facility_")==0)\n                m_buf_city_decal.add(tile,x,y);\n            else if (tile < TILE_DNGN_MAX)\n                add_dngn_tile(tile, x, y);'
assert needle in text;text=text.replace(needle,replace);p.write_text(text)

# Export native connected-door groups for matching browser interactions.
p=S/'holo34-city.cc';text=p.read_text()
needle='        out << "{\\"x\\":" << door.x << ",\\"y\\":" << door.y\n            << ",\\"opened\\":" << door.opened << \'}\';'
replace='        out << "{\\"x\\":" << door.x << ",\\"y\\":" << door.y\n            << ",\\"opened\\":" << door.opened << ",\\"linked\\":[";\n        std::set<coord_def> linked;find_connected_identical(coord_def(door.x,door.y),linked);\n        bool first_link=true;for(const auto &p:linked){if(!first_link)out<<\',\';first_link=false;out<<\'[\'<<p.x<<\',\'<<p.y<<\']\';}\n        out << "]}";'
assert needle in text;p.write_text(text.replace(needle,replace))

# Freeze only test-script animation, leaving real game animation unchanged.
p=S/'holo34-city.cc';text=p.read_text();needle='    check(city_run_enabled(), "Native city test requires HOLOCRAWL_CITY77=1");'
assert needle in text;p.write_text(text.replace(needle,needle+'\n    Options.tile_water_anim=false;Options.tile_misc_anim=false;\n    unwind_var<time_t> test_birth(you.birth_time, time_t(107));\n    unwind_var<unsigned int> test_frame(you.frame_no, 0);',1))

# Export fixed cosmetic clock; colour.cc hashes birth_time/frame_no even with animation disabled.
p=S/"holo34-city.cc";text=p.read_text();text=text.replace("    std::vector<tileidx_t> palette;", "    unwind_var<time_t> export_birth(you.birth_time, time_t(107));\n    unwind_var<unsigned int> export_frame(you.frame_no, 0);\n    std::vector<tileidx_t> palette;",1);text=text.replace("            apply_variations(tile_env.flv(position), &tile, position);\n", "",1);p.write_text(text)
import shutil
shutil.copy2(ROOT/"scripts/native-play107-probe.inc",S/"holo34-play107.inc")
