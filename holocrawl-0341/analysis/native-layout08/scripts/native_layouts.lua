-- Read-only terrain export through the unchanged upstream level builder.
-- No renderer, play session, or HoloCrawl terrain import is involved.
local cases = {
  {seed='2026110401', place='D:5'},
  {seed='2026110402', place='D:5'},
  {seed='2026110403', place='D:5'},
  {seed='2026110404', place='D:10'},
  {seed='2026110405', place='D:10'},
  {seed='2026110406', place='D:10'}
}
for _, case in ipairs(cases) do
  debug.reset_rng(case.seed)
  test.regenerate_level(case.place)
  local w,h=dgn.max_bounds()
  local palette, ids, rows = {}, {}, {}
  for y=0,h-1 do
    local row={}
    for x=0,w-1 do
      local name=dgn.feature_name(dgn.grid(x,y))
      if not ids[name] then
        palette[#palette+1]='"'..name..'"'
        ids[name]=#palette-1
      end
      row[#row+1]=ids[name]
    end
    rows[#rows+1]='['..table.concat(row,',')..']'
  end
  local vaults=debug.vault_names()
  crawl.stderr('HOLO_TERRAIN_JSON '..'{"seed":"'..case.seed..'","place":"'..case.place..'","w":'..w..',"h":'..h..',"vaults":"'..vaults..'","palette":['..table.concat(palette,',')..'],"rows":['..table.concat(rows,',')..']}')
end
