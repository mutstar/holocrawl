"""Install full altar feature tiles while retaining deity emblems in menus."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = root / 'engine/campaign-crawl/crawl-ref/source'

def replace(path, old, new):
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

replace(src/'holo-visual.h', 'int god_tile(const std::string &god);',
        'int god_tile(const std::string &god);\nint altar_tile(const std::string &god);')
replace(src/'holo-visual.cc', 'int effect_tile(effect kind,int frame) {',
        '''int altar_tile(const std::string &g) {
    const auto ids=holo_worship::gods();const auto it=std::find(ids.begin(),ids.end(),g);
    return it==ids.end()?0:TILE_HOLO_ALTAR_SUISEI+int(it-ids.begin());
}
int effect_tile(effect kind,int frame) {''')
replace(src/'holo-visual.cc', 'require(TILE_HOLO_GOD_MELA-TILE_HOLO_GOD_SUISEI==21);',
        '''require(TILE_HOLO_GOD_MELA-TILE_HOLO_GOD_SUISEI==21);
    require(TILE_HOLO_ALTAR_MELA-TILE_HOLO_ALTAR_SUISEI==21);
    require(altar_tile("unknown")==0);
    int altar_index=0;
    for(const auto &g:holo_worship::gods())
        require(altar_tile(g)==TILE_HOLO_ALTAR_SUISEI+altar_index++);''')
replace(src/'tilepick.cc', 'dungeon_feature_type feat = env.map_knowledge(gc).feat();\n\n    tileidx_t override',
        '''dungeon_feature_type feat = env.map_knowledge(gc).feat();

    // Saved deity identity selects the entire structure, replacing native altar art.
    const auto holo_altar = holo_visual::altar(gc);
    if (!holo_altar.empty())
        if (const int tile = holo_visual::altar_tile(holo_altar))
            return tile;

    tileidx_t override''')
path=src/'tilecell.cc'
text=path.read_text(encoding='utf-8')
old='    const auto god=holo_visual::altar(world);\n    if(!god.empty() && cell.num_dngn_overlay<packed_cell::MAX_DNGN_OVERLAY)_add_overlay(holo_visual::god_tile(god),cell);\n'
if old in text:path.write_text(text.replace(old,''),encoding='utf-8')

# Keep the feature registry in the existing synchronized include.
gods='suisei miko aki fubuki ayame choco korone okayu pekora noel watame towa lamy polka koyori lui raden hajime su vivi sopia mela'.split()
path=src/'rltiles/dc-holo-feat.txt'
text=path.read_text(encoding='utf-8')
if 'HOLO_ALTAR_SUISEI' not in text:
    path.write_text(text+'\n'+''.join(f'altar_{g} HOLO_ALTAR_{g.upper()}\n' for g in gods),encoding='utf-8')
print('Full altar lookup installed; saved deity identities and menu emblems retained.')
