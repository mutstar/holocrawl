function buildLoadingDock(seed, ending) {
  const profile = {courts: 6, wideChance: .9, extraLinks: .7, avenues: 3, minRoomWidth: 9, minRoomHeight: 6, wallExitWidth: 7};
  for (let attempt = 0; attempt < 16; attempt++) {
    const map = StreetGen.generate(`${seed}:loading-dock:${attempt}`, 80, 70, 'wall', profile);
    const {w, start, upstairs, exitDoor} = map;
    for (const {x, y} of map.props) map.cells[y * w + x] = StreetGen.FLOOR;

    const shutter = {x: exitDoor.x, y: exitDoor.y + 2, width: exitDoor.w, depth: 3};
    if (!dockClear(map, shutter)) continue;
    map.exit = {x: shutter.x + 3, y: shutter.y};
    const shutterArea = {...shutter, width: shutter.width + 2};
    const vault = placeStageEnding(map, ending, [shutterArea]);
    if (!vault) continue;

    const {cells} = map;
    const anchors = [start, upstairs, map.exit];
    const vaultMouth = {x: vault.entry.x - 1, y: vault.entry.y + 1, width: 3, depth: 2};
    const reserved = [shutterArea, vault, vaultMouth];
    const random = StreetGen.random(`${map.seed}:dock-sites`);
    const lift = findDockSite(map, 11, 5, reserved, anchors, random);
    if (!lift) continue;
    const warehouse = findDockSite(map, 8, 5, [...reserved, lift], anchors, random);
    if (!warehouse) continue;

    const liftEquipment = [[1, 0, 5], [8, 2, 2]];
    const storedCargo = [[1, 1, 3], [5, 1, 2], [1, 3, 2]];
    const goodsCargo = [[4, 1, 2]];
    const blockRow = (zone, dx, dy, span, tile) => {
      const i = (zone.y + dy) * w + zone.x + dx;
      cells.fill(tile, i, i + span);
    };
    for (let dy = 0; dy < warehouse.depth; dy++) {
      blockRow(warehouse, 0, dy, 1, StreetGen.WALL);
      blockRow(warehouse, 7, dy, 1, StreetGen.WALL);
    }
    blockRow(warehouse, 1, 4, 2, StreetGen.WALL);
    blockRow(warehouse, 6, 4, 1, StreetGen.WALL);
    for (const [zone, occupied] of [[lift, liftEquipment], [warehouse, storedCargo], [shutter, goodsCargo]]) {
      for (const [dx, dy, span] of occupied) blockRow(zone, dx, dy, span, StreetGen.BARRIER);
    }
    const validation = StreetGen.validate(map);
    if (!validation.ok || !StreetGen.route(map, start, vault.reward).length) continue;
    map.validation = validation;
    map.path = StreetGen.route(map, start, map.exit);
    return {map, lift, warehouse, shutter, vault};
  }
  throw Error('Could not fit the loading dock and warehouse on a connected floor');
}

function dockClear({w, h, cells}, {x, y, width, depth}) {
  if (x < 1 || y < 1 || x + width >= w || y + depth >= h) return false;
  for (let yy = y; yy < y + depth; yy++) for (let xx = x; xx < x + width; xx++) {
    if (cells[yy * w + xx] !== StreetGen.FLOOR) return false;
  }
  return true;
}

function findDockSite(map, width, depth, reserved, anchors, random) {
  const {w, h, cells} = map;
  let best;
  for (let y = 3; y < h - depth - 1; y++) for (let x = 2; x < w - width - 1; x++) {
    if (anchors.some(p => p.x >= x - 1 && p.x <= x + width && p.y >= y - 1 && p.y <= y + depth)) continue;
    if (reserved.some(p => x < p.x + p.width + 2 && x + width + 2 > p.x
        && y < p.y + p.depth + 2 && y + depth + 2 > p.y)) continue;
    const north = (y - 1) * w + x;
    if (cells.subarray(north, north + width).some(tile => tile !== StreetGen.WALL)) continue;
    if (!dockClear(map, {x: x - 1, y, width: width + 2, depth: depth + 1})) continue;
    const rank = random();
    if (!best || rank < best.rank) best = {x, y, width, depth, rank};
  }
  return best;
}

function drawLoadingDock(layer, art, {lift, warehouse, shutter, vault}) {
  const draw = (sprite, zone, dx, dy) => layer.drawImage(art[sprite], zone.x * 32 + dx, zone.y * 32 + dy);
  draw('railsTowardLift', lift, 80, 24);
  draw('freightLift', lift, 32, -32);
  draw('hoistControls', lift, 192, -32);
  draw('forkliftCharger', lift, 288, -32);
  draw('stagingMark', lift, 240, 56);
  draw('forklift', lift, 256, 64);

  draw('warehouseOpening', warehouse, 96, 128);
  draw('sceneryPallet', warehouse, 32, 0);
  draw('cargoCrate', warehouse, 160, 32);
  draw('cargoCrate', warehouse, 32, 96);

  draw('stagingMark', shutter, 96, 28);
  draw('warehouseShutter', shutter, 32, -32);
  draw('inspectionWindow', shutter, 192, -32);
  draw('palletScale', shutter, 224, 22);
  draw('cargoCrate', shutter, 128, 32);
  drawStageEnding(layer, vault.ending, vault.x, vault.y);
}
