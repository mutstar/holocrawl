"""Install city77 into the restored 0.34.1 engine without touching old snapshots."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root / 'engine/upstream/crawl-ref/source'
overlay = root / 'migration/engine0341-city77/overlay/crawl-ref/source'

for item in overlay.rglob('*'):
    if item.is_file():
        target = source / item.relative_to(overlay)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def replace(filename, before, after, marker=None):
    target = source / filename
    text = target.read_text(encoding='utf-8')
    if after in text or (marker is not None and marker in text):
        return
    if text.count(before) != 1:
        raise ValueError(f'Unexpected engine source around {filename}: {before[:60]}')
    target.write_text(text.replace(before, after), encoding='utf-8', newline='\n')


replace('Makefile.obj', 'holo34-street.o \\\n', 'holo34-street.o \\\nholo34-city.o \\\n')
replace('dungeon.cc', '#include "holo34-street.h"',
        '#include "holo34-street.h"\n#include "holo34-city.h"')
replace('dungeon.cc', 'static void _build_dungeon_level()\n{\n', '''static void _build_dungeon_level()
{
    if (holo34::city_floor_enabled()) {
        const map_def *layout = random_map_for_tag("layout", true, true);
        if (!layout)
            throw dgn_veto_exception("No native layout for HoloCrawl city");
        _dgn_ensure_vault_placed(_build_primary_vault(layout), false, layout->name);
        dgn_check_connectivity = true;
        holo34::place_city_facility();
        _check_doors();
        _dgn_verify_connectivity(env.level_vaults.size());
        holo34::decorate_city_floor();
        env.level_build_method += " / HoloCrawl city77";
        return;
    }
''', marker='env.level_build_method += " / HoloCrawl city77";')
replace('dungeon.cc', '''        _check_doors();
        _dgn_verify_connectivity(env.level_vaults.size());''', '''        _check_doors();
        if (dgn_count_disconnected_zones(false) != 1)
            throw dgn_veto_exception("HoloCrawl city must form one connected floor");
        _dgn_verify_connectivity(env.level_vaults.size());''')
replace('dungeon.cc', '''        holo34::decorate_city_floor();''', '''        _fixup_branch_stairs();
        holo34::decorate_city_floor();''')
replace('dungeon.cc', '''        const map_def *layout = random_map_for_tag("layout", true, true);''', '''        // Use the five native layout families approved in the city previews.
        const char *layout_name = random_choose_weighted(
            35, "layout_basic", 15, "layout_loops_ring", 5, "layout_loops_cross",
            5, "layout_loops_corners", 15, "layout_rooms");
        const map_def *layout = find_map_by_name(layout_name);''')
replace('tags.cc', 'static void _add_missing_branches()\n{\n', '''static void _add_missing_branches()
{
    // Branch entrances are intentionally deferred in the isolated city prototype.
    if (env.properties.exists("holocrawl_city77"))
        return;
''')
replace('tilepick.cc', '#include "tilepick.h"',
        '#include "tilepick.h"\n#include "holo34-city.h"')
replace('tilepick.cc', '''    dungeon_feature_type feat = env.map_knowledge(gc).feat();

    tileidx_t override = tile_env.flv(gc).feat;''', '''    dungeon_feature_type feat = env.map_knowledge(gc).feat();
    if (const auto city_door = holo34::city_door_tile(gc, feat))
        return city_door;

    tileidx_t override = tile_env.flv(gc).feat;''')
replace('stairs.cc', '#include "holo34-street.h"',
        '#include "holo34-street.h"\n#include "holo34-city.h"')
replace('stairs.cc', '''    if (holo34::is_street_floor()) {''', '''    if (holo34::city_floor_enabled() && you.depth == 14 && !going_up) {
        mpr("HoloCrawl city prototype ends at floor 14. Use Ctrl-S to save.");
        return;
    }
    if (holo34::is_street_floor()) {''')
replace('ctest.cc', '#include "holo34-street.h"',
        '#include "holo34-street.h"\n#include "holo34-city.h"')
replace('ctest.cc', 'static const struct luaL_Reg crawl_test_lib[] =', '''static int crawl_holo_city_test(lua_State *ls)
{
    try {
        const auto report = holo34::city_native_test(luaL_checkstring(ls, 1));
        std::puts(report.c_str());
        lua_pushstring(ls, report.c_str());
        return 1;
    } catch (const std::exception &error) {
        return luaL_error(ls, "Native city test: %s", error.what());
    }
}
static const struct luaL_Reg crawl_test_lib[] =''')
replace('ctest.cc', '    { "holo_street_test", crawl_holo_street_test },',
        '    { "holo_street_test", crawl_holo_street_test },\n'
        '    { "holo_city_test", crawl_holo_city_test },')
atlas = source / 'rltiles/dc-floor.txt'
atlas_text = atlas.read_text(encoding='utf-8')
marker = '\n# HOLOCRAWL CITY77\n'
if marker in atlas_text:
    atlas_text = atlas_text.split(marker)[0]
updated_atlas = atlas_text + (overlay / 'rltiles/holo-city77.txt').read_text(encoding='utf-8')
if atlas.read_text(encoding='utf-8') != updated_atlas:
    atlas.write_text(updated_atlas, encoding='utf-8', newline='\n')
wall_atlas = source / 'rltiles/dc-wall.txt'
wall_marker = '\n# HOLOCRAWL WALL78\n'
wall_text = wall_atlas.read_text(encoding='utf-8').split(wall_marker)[0]
updated_walls = wall_text + (overlay / 'rltiles/holo-wall78.txt').read_text(encoding='utf-8')
if wall_atlas.read_text(encoding='utf-8') != updated_walls:
    wall_atlas.write_text(updated_walls, encoding='utf-8', newline='\n')
print('Installed native city77 source, nine facility layouts, and reviewed tiles.')
