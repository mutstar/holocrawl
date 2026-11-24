function endingTile(ending, x, y) {
  return ending.layout[y]?.[x] || ' ';
}

function endingWalkable(tile) {
  return '.=ers'.includes(tile);
}

function pickStageEnding(seed) {
  const random = StreetGen.random(`${seed}:stage-ending`);
  return stageEndings[Math.floor(random() * stageEndings.length)];
}

function endingFootprint(ending) {
  const footprint = [];
  for (let y = 0; y < ending.depth; y++) for (let x = 0; x < ending.width; x++) {
    const tile = endingTile(ending, x, y);
    if (tile !== ' ') footprint.push({x, y, tile});
  }
  return footprint;
}

function placeStageEnding(map, ending, sites) {
  const {w, h, cells, start, upstairs, exit} = map;
  const random = StreetGen.random(`${map.seed}:ending-placement`);
  const {dist} = StreetGen.distances(map, start);
  const footprint = endingFootprint(ending);
  const candidates = [];
  for (let y = 2; y + ending.depth < h - 2; y++) for (let x = 2; x + ending.width < w - 2; x++) {
    const entryX = x + ending.entry.x;
    const entryY = y + ending.depth;
    if (dist[entryY * w + entryX] < 24) continue;
    if (cells[(entryY + 1) * w + entryX] !== StreetGen.FLOOR) continue;
    if ([start, upstairs, exit].some(p => p.x >= x - 2 && p.x < x + ending.width + 2
        && p.y >= y - 2 && p.y < entryY + 2)) continue;
    if (sites.some(p => x < p.x + p.width + 2 && x + ending.width + 2 > p.x
        && y < p.y + p.depth + 2 && entryY + 2 > p.y)) continue;
    let replaced = 0;
    for (const tile of footprint) {
      if (!endingWalkable(tile.tile) && cells[(y + tile.y) * w + x + tile.x] === StreetGen.FLOOR) replaced++;
    }
    const openFront = Number(cells[entryY * w + entryX - 1] === StreetGen.FLOOR)
      + Number(cells[entryY * w + entryX + 1] === StreetGen.FLOOR);
    candidates.push({x, y, rank: replaced - openFront * 3 + random() * 16});
  }

  for (const {x, y} of candidates.sort((a, b) => a.rank - b.rank).slice(0, 64)) {
    map.cells = cells.slice();
    const vault = stampStageEnding(map, ending, footprint, x, y);
    if (StreetGen.validate(map).ok) return vault;
    if (sealCutOffStageFloor(map, vault)) return vault;
  }
  map.cells = cells;
  return null;
}

function sealCutOffStageFloor(map, vault) {
  const {w, cells, start, exit, upstairs} = map;
  const {dist} = StreetGen.distances(map, start);
  if ([exit, upstairs, vault.entry, vault.reward].some(p => dist[p.y * w + p.x] < 0)) return false;
  const pockets = [];
  for (let i = 0; i < cells.length; i++) {
    if (cells[i] === StreetGen.FLOOR && dist[i] < 0) pockets.push(i);
    if (pockets.length > 40) return false;
  }
  for (const i of pockets) cells[i] = StreetGen.WALL;
  return StreetGen.validate(map).ok;
}

function stampStageEnding(map, ending, footprint, x, y) {
  const {w, cells} = map;
  const entry = {x: x + ending.entry.x, y: y + ending.entry.y};
  let reward;
  let guard;
  let exitDoor;
  for (const {x: dx, y: dy, tile} of footprint) {
    const point = {x: x + dx, y: y + dy};
    const index = point.y * w + point.x;
    cells[index] = endingWalkable(tile) ? StreetGen.FLOOR : '~opPvkbfd'.includes(tile) ? StreetGen.BARRIER : StreetGen.WALL;
    if (tile === 'r') reward = point;
    if (tile === 's') guard = point;
    if (tile === 'd') exitDoor = point;
  }
  return {ending, x, y, entry, reward, guard, exitDoor, width: ending.width, depth: ending.depth};
}

function endingFloorMaterial(ending, tile, path, x, y) {
  if (tile === '~') return 'deep';
  if (path && ['tower','rail','flood'].includes(ending.id)) return 'metal';
  if (ending.id === 'office' && y < 13 && (x >= 8 || y >= 10)) {
    return x >= 10 && x <= 17 && y >= 7 && y <= 10 ? 'carpet' : 'wood';
  }
  if (ending.liveShow) {
    const {stage, lobby} = ending.liveShow;
    const within = box => x >= box.x && x < box.x+box.width && y >= box.y && y < box.y+box.depth;
    if (within(stage)) return 'wood';
    if (within(lobby) && x>lobby.x && x<lobby.x+lobby.width-1) return 'carpet';
  }
  return ending.road ? 'stone' : 'tile';
}

function drawStageEnding(layer, ending, originX, originY, deepWater, seed = ending.id, gardenSprites, archiveConcrete) {
  const {id, width, depth, palette: [floor, trim, wall, accent]} = ending;
  const plantedCracks = new Map((ending.floorCracks ?? []).map(crack => [crack.y * width + crack.x, crack]));
  const paint = (color, x, y, w, h) => {
    layer.fillStyle = color;
    layer.fillRect(x, y, w, h);
  };
  for (let y = 0; y < depth; y++) for (let x = 0; x < width; x++) {
    const tile = endingTile(ending, x, y);
    if (tile === ' ') continue;
    const atEntrance = y >= depth - 3 && Math.abs(x - ending.entry.x) <= 2;
    layer.save();
    layer.translate((originX + x) * 32, (originY + y) * 32);
    if (tile === '#') {
      const inside = endingTile(ending, x, y + 1);
      if (id !== 'mirror' && !atEntrance && inside !== '#' && inside !== ' ' && (x + y * 3) % 4 < 2) {
        // Recess details into the existing dock wall face and retain its coping and lower trim.
        paint(`${trim}38`, 3, 11, 26, 11);
        drawEndingWallDetail(paint, id, wall, accent, x, y);
      }
    } else {
      if (tile === '~') {
        const patch = Math.floor(StreetGen.random(`flood-water:${x}:${y}`)() * 16);
        layer.drawImage(deepWater, (patch % 4) * 32, Math.floor(patch / 4) * 32, 32, 32, 0, 0, 32, 32);
      } else if (id === 'rail') {
        drawServerGround(layer, ending, x, y);
      } else if (!atEntrance) {
        paint(`${floor}${y < depth - 4 ? '5c' : '29'}`, 0, 0, 32, 32);
        if (id === 'archive' && archiveConcrete) {
          layer.imageSmoothingEnabled = false;
          layer.globalAlpha = 0.86;
          layer.drawImage(archiveConcrete, (x%8)*16, (y%8)*16, 16, 16, 0, 0, 32, 32);
          layer.globalAlpha = 1;
          if (x%2 === 0) paint('#29272040',0,0,1,32);
          if (y%2 === 0) paint('#29272040',0,0,32,1);
        }
        if (id === 'office') drawOfficeFloor(paint, x, y);
        if (ending.road) drawStreetSetGround(paint, ending, x, y);
        if (ending.liveShow) drawLiveShowGround(paint, ending.liveShow, x, y);
      }
      const path = tile === '=' || (['flood','tower','rail'].includes(id) && ending.pathUnderMarks.has(y * width + x));
      if (path && (!atEntrance || id === 'tower')) drawEndingPath(paint, ending, trim, accent, x, y);
      if (ending.dollyTrack) drawGardenTrack(paint, ending.dollyTrack, x, y);
      const crack = tile === '.' && plantedCracks.get(y * width + x);
      if (crack) drawTowerFloorCrack(paint, crack);
      else if (id !== 'rail') FloorOvergrowth.draw(layer, endingFloorMaterial(ending, tile, path, x, y), seed, originX+x, originY+y, 0, 0);
      if (tile === 'o') drawEndingProp(paint, id, trim, accent, id === 'mirror' ? x % 3 : (x + y) % 2);
      if (id === 'flood' && 'vkb'.includes(tile)) drawFloodPlatformProp(paint, tile);
      if (tile === 'e') {
        paint('#2e302e', 0, 28, 32, 2);
        paint('#777266', 0, 28, 32, 1);
        for (const x of [2, 25]) paint('#a18a53', x, 25, 5, 1);
      }
      if (tile === 'r') drawEndingReward(paint);
    }
    layer.restore();
  }
  for (const {kind, x, y} of ending.floodedEquipment ?? []) {
    layer.save();
    layer.translate((originX + x) * 32, (originY + y) * 32);
    drawFloodedEquipment(paint, kind);
    layer.restore();
  }
  if (id === 'garden') {
    layer.save();
    layer.translate(originX*32,originY*32);
    drawGardenYard(layer,ending);
    layer.restore();
  }
  const drawScenery = {live: drawLiveShowScenery, street: drawStreetSetScenery, office: drawOfficeScenery, tower: drawTowerScenery, archive: drawFilmArchiveScenery, mirror: drawDressingRoomScenery, rail: drawModelRailScenery, power: drawPowerScenery}[id];
  if (id === 'rail') {
    layer.save();
    layer.translate(originX * 32, originY * 32);
    drawServerShadows(layer, ending.scenery);
    layer.restore();
  }
  for (const scenery of ending.scenery ?? []) {
    layer.save();
    layer.translate((originX + scenery.x) * 32, (originY + scenery.y) * 32);
    if (id === 'garden') drawGardenScenery(layer, gardenSprites, scenery);
    else drawScenery(paint, scenery);
    layer.restore();
  }
  for (const {x, y} of ending.wallFixtures) {
    layer.save();
    layer.translate((originX + x) * 32, (originY + y) * 32);
    drawEndingFixture(paint, id, 'wall', accent);
    layer.restore();
  }
  for (let y = 0; y < depth; y++) for (let x = 0; x < width; x++) {
    if (endingTile(ending, x, y) !== 'p') continue;
    layer.save();
    layer.translate((originX + x) * 32, (originY + y) * 32);
    drawEndingFixture(paint, id, 'floor', accent, x % 2 === 1);
    layer.restore();
  }
}

function drawFloodPlatformProp(paint, tile) {
  paint('#20252ac0', 4, 22, 24, 6);
  if (tile === 'v') {
    paint('#343938', 6, 19, 21, 8);
    paint('#73776a', 7, 20, 19, 2);
    paint('#344748', 12, 10, 9, 12);
    paint('#687978', 13, 11, 2, 9);
    paint('#513d35', 10, 5, 13, 12);
    paint('#ab785b', 11, 6, 11, 10);
    paint('#503e36', 14, 8, 5, 6);
    paint('#cf9b72', 11, 6, 11, 2);
    paint('#9b7457', 16, 7, 1, 8);
    paint('#9b7457', 12, 10, 9, 1);
    paint('#c6a972', 8, 24, 4, 1);
    paint('#c6a972', 21, 24, 4, 1);
  } else if (tile === 'k') {
    paint('#292e30', 9, 8, 13, 17);
    paint('#705844', 10, 9, 11, 14);
    paint('#957c5d', 11, 9, 9, 2);
    for (const x of [9, 21]) {
      paint('#424b4a', x - 2, 10, 4, 14);
      paint('#7a8377', x - 2, 10, 1, 12);
    }
    for (const y of [12, 15, 18]) paint('#353b3b', 11, y, 9, 2);
    paint('#353b3b', 18, 21, 2, 5);
    paint('#353b3b', 19, 25, 9, 2);
    paint('#9b8055', 26, 25, 3, 2);
  } else {
    paint('#303b40', 4, 9, 24, 15);
    paint('#56666a', 5, 9, 22, 12);
    paint('#87908a', 6, 9, 20, 1);
    paint('#405158', 6, 16, 20, 6);
    paint('#616962', 6, 22, 20, 2);
    for (const x of [8, 22]) paint('#a9936e', x, 15, 2, 5);
    paint('#252d32', 12, 12, 8, 2);
  }
}

function drawFloodedEquipment(paint, kind) {
  if (kind === 'rack') {
    paint('#041d27c0', 7, 25, 112, 27);
    paint('#203a40', 11, 15, 106, 27);
    paint('#334950', 10, 12, 108, 23);
    paint('#62736d', 13, 12, 102, 2);
    paint('#26383d', 13, 16, 102, 16);
    for (const x of [14, 47, 80]) {
      paint('#495a5d', x, 17, 29, 13);
      paint('#687872', x, 17, 29, 1);
      paint('#253841', x + 3, 20, 18, 7);
      paint('#396067', x + 4, 21, 16, 4);
      paint(x === 47 ? '#a98459' : '#699a92', x + 24, 21, 2, 2);
      paint('#253841', x + 24, 25, 2, 2);
    }
    for (const x of [15, 51, 105]) {
      paint('#40534e', x, 35, 5, 9);
      paint('#51706b', x, 36, 2, 4);
      paint('#476b6e8f', x - 3, 43, 12, 1);
    }
    paint('#0c3440a3', 11, 38, 106, 6);
    paint('#65919080', 6, 38, 16, 1);
    paint('#65919080', 74, 40, 24, 1);
    paint('#3b656b90', 108, 47, 15, 1);
  } else if (kind === 'pump') {
    paint('#051e29bd', 8, 16, 48, 35);
    paint('#273d3d', 9, 30, 45, 17);
    paint('#4f625c', 10, 31, 43, 2);
    paint('#354a4c', 15, 13, 28, 28);
    paint('#63766e', 16, 13, 26, 2);
    paint('#485e60', 17, 16, 24, 18);
    paint('#2f474b', 19, 18, 7, 12);
    for (const y of [19, 23, 27]) paint('#29393b', 29, y, 9, 2);
    paint('#624d3b', 41, 21, 11, 10);
    paint('#8f7356', 41, 21, 10, 2);
    paint('#493c34', 46, 26, 7, 12);
    paint('#507476a6', 7, 39, 24, 1);
    paint('#32808a70', 35, 43, 23, 1);
  } else if (kind === 'footing') {
    paint('#071e29ac', 4, 14, 51, 12);
    for (const [x, y, w] of [[7, 9, 22], [29, 13, 15], [46, 16, 8]]) {
      paint('#37484a', x, y, w, 9);
      paint('#59615a', x, y, w, 3);
      paint('#71776a', x, y, 7, 1);
    }
    paint('#786a50', 13, 5, 2, 6);
    paint('#566863', 35, 9, 2, 6);
    paint('#2c64727d', 7, 19, 24, 2);
    paint('#76908b63', 28, 21, 16, 1);
  } else {
    paint('#041e29ae', 6, 18, 111, 12);
    paint('#041e29ae', 98, 21, 20, 28);
    paint('#384e50', 11, 14, 99, 9);
    paint('#384e50', 102, 19, 9, 26);
    paint('#6b7362', 12, 14, 96, 2);
    paint('#526560', 102, 20, 2, 23);
    for (const x of [19, 48, 79]) {
      paint('#31413e', x, 12, 7, 13);
      paint('#748076', x, 12, 3, 9);
    }
    paint('#162f37', 101, 39, 12, 8);
    paint('#5e77776c', 95, 44, 23, 1);
  }
}

function drawEndingWallDetail(paint, id, shadow, accent, x, y) {
  if (id === 'garden') {
    paint(shadow, 5, 11, 22, 10);
    paint('#416a63', 6, 12, 20, 7);
    paint('#c1dcd56d', 8, 14, 9, 1);
    paint('#c1dcd56d', 9, 15, 4, 1);
  } else if (id === 'street' || id === 'rail') {
    paint('#241a1a4a', 0, 17, 32, 1);
    paint('#241a1a4a', 0, 22, 32, 1);
    paint('#241a1a4a', 13 + (x + y) % 4, 12, 1, 5);
    paint('#241a1a4a', 5 + (x + y) % 3, 18, 1, 4);
  } else if (id === 'office') {
    paint('#848579', 0, 12, 32, 9);
    paint('#a69f88', 0, 12, 32, 1);
    paint('#575f59', 0, 20, 32, 2);
  } else if (id === 'flood') {
    paint('#567e7b', 0, 23, 32, 1);
    paint('#304d4f', 0, 24, 32, 2);
  } else if (id === 'tower' || id === 'live' || id === 'power') {
    paint(shadow, 1, 12, 2, 8);
    paint('#bcc3bd65', 5, 14, 2, 2);
    paint('#bcc3bd65', 26, 14, 2, 2);
    if (x % 4 === 2) paint(accent, 12, 18, 7, 2);
  } else if (x % 2 === 0) {
    paint(shadow, 5, 12, 22, 8);
    paint(accent, 11, 17, 10, 3);
  }
}

function drawEndingPath(paint, ending, trim, accent, x, y) {
  const {id} = ending;
  if (id === 'flood') {
    const bridge=floodServiceBridge;
    if (x===bridge.x && y>=bridge.y && y<bridge.y+bridge.length) {
      // A continuous span with open seams and flush end plates on the landings.
      paint('#454843',0,0,32,32);
      paint('#848372',0,0,3,32);
      paint('#62665e',29,0,3,32);
      for (let row=1; row<32; row+=4) {
        paint('#858579',4,row,24,2);
        paint('#60655d',4,row+2,24,1);
      }
      if (y===bridge.y || y===bridge.y+bridge.length-1) {
        const at=y===bridge.y?0:28;
        paint('#695f46',0,at,32,4);
        for (const col of [2,8,21,27]) paint('#baa276',col,at+1,3,2);
      }
      return;
    }
    paint((x * 5 + y * 3) % 4 === 0 ? '#77736a' : '#706d64', 0, 0, 32, 32);
    paint('#504e47', 0, 0, 32, 1);
    paint('#504e47', 0, 0, 1, 32);
    for (const row of [6, 13, 20, 27]) {
      paint('#58564e', 3, row, 26, 2);
      paint('#878278', 3, row + 2, 26, 1);
    }
    if (endingTile(ending, x, y - 1) === '~') paint('#aaa18d', 1, 0, 31, 2);
    if (endingTile(ending, x - 1, y) === '~') paint('#a49b89', 0, 1, 2, 30);
    if (endingTile(ending, x + 1, y) === '~') paint('#a49b89', 30, 1, 2, 30);
    if (endingTile(ending, x, y + 1) === '~') {
      paint('#978d77', 0, 27, 32, 2);
      paint('#3e3c35', 0, 29, 32, 3);
    }
    if (endingTile(ending, x, y - 1) === '.') {
      paint('#4b4841', 0, 0, 32, 2);
      paint('#766f60', 0, 2, 32, 4);
      paint('#928878', 0, 3, 32, 1);
      paint('#5b574e', 0, 6, 32, 1);
    }
  } else if (id === 'rail') {
    const trackAt = (col, row) => endingTile(ending, col, row) === '=' || ending.pathUnderMarks.has(row * ending.width + col);
    const west = trackAt(x - 1, y);
    const east = trackAt(x + 1, y);
    const north = trackAt(x, y - 1);
    const south = trackAt(x, y + 1);
    if (west !== east && north !== south) {
      drawModelTrackBend(paint, east, north);
      return;
    }
    const horizontal = west || east;
    const vertical = north || south;
    if (horizontal) {
      paint('#362e27', 0, 5, 32, 22);
      for (const slot of [2, 11, 21, 29]) paint('#74624d', slot, 5, 2, 22);
    }
    if (vertical) {
      paint('#362e27', 5, 0, 22, 32);
      for (const slot of [2, 11, 21, 29]) paint('#74624d', 5, slot, 22, 2);
    }
    for (const rail of [9, 22]) {
      if (horizontal) {
        paint('#272d2c', 0, rail, 32, 3);
        paint('#b0a493', 0, rail, 32, 1);
      }
      if (vertical) {
        paint('#272d2c', rail, 0, 3, 32);
        paint('#b0a493', rail, 0, 1, 32);
      }
    }
    if (y === 22 && ((x >= 20 && x <= 22) || (x >= 31 && x <= 32))) {
      for (const row of [3, 12, 17, 25]) {
        paint('#847464', 0, row, 32, 4);
        paint('#a38f76', 0, row, 32, 1);
      }
    }
  } else if (id === 'tower') {
    drawTowerWalkway(paint, ending, x, y);
  } else {
    paint(`${trim}50`, 1, 1, 30, 30);
    if ((x + y) % 3 === 0) paint(`${accent}8c`, 4 + (x * 3 + y * 7) % 9, 5, 8, 1);
    paint('#11192339', 2, 28, 28, 2);
  }
}

function drawModelTrackBend(paint, east, north) {
  for (let y = 0; y < 32; y++) for (let x = 0; x < 32; x++) {
    const dx = east ? 31-x : x;
    const dy = north ? y : 31-y;
    const radius = Math.round(Math.hypot(dx, dy));
    if (radius < 5 || radius > 26) continue;
    let color = '#362e27';
    if (Math.cos(12 * Math.atan2(dy, dx)) > 0.82) color = '#74624d';
    if ((radius >= 9 && radius < 12) || (radius >= 22 && radius < 25)) color = '#272d2c';
    if (radius === 9 || radius === 22) color = '#b0a493';
    paint(color, x, y, 1, 1);
  }
}

function drawEndingProp(p, id, trim, accent, alternate) {
  if (id !== 'mirror') p('#10131aa0', 3, 23, 27, 6);
  if (id === 'flood') {
    p('#202f3a', 4, 5, 24, 20);
    p('#526c79', 5, 5, 22, 9);
    p('#2d3f4b', 7, 8, 19, 15);
    p('#1e2b35', 8, 10, 13, 8);
    p('#539b9f', 9, 11, 11, 5);
    p('#79b5b1', 10, alternate ? 12 : 14, 8, 1);
    p(accent, 23, 11, 2, 2);
    for (const x of [7, 24]) p(trim, x, 23, 2, 5);
  } else if (id === 'street') {
    if (alternate) {
      p('#3d352d', 5, 4, 22, 20);
      p('#846a50', 6, 5, 20, 17);
      p('#ab8761', 8, 7, 16, 2);
      p('#594b3b', 8, 10, 16, 9);
      for (const x of [8, 24]) {
        p('#656f6a', x, 19, 2, 9);
        p('#90988a', x - 2, 27, 6, 1);
      }
    } else {
      p('#3a2e28', 2, 18, 28, 8);
      p('#725943', 4, 12, 26, 9);
      p('#4a6b68', 6, 5, 20, 12);
      p('#7d9794', 8, 5, 16, 2);
      for (const x of [6, 25]) p(accent, x, 25, 3, 2);
    }
  } else if (id === 'tower') {
    p('#343e53', 7, 23, 19, 4);
    p('#8391a3', 15, 4, 3, 22);
    p('#a1a9b5', 10, 8, 14, 2);
    p('#66788e', 7, 13, 19, 2);
    p('#66788e', 10, 18, 14, 1);
    for (const x of [8, 22]) p('#536478', x, 11, 2, 12);
    p(accent, 15, 3, 3, 3);
  } else if (id === 'garden') {
    p('#473b32', 2, 14, 28, 13);
    p('#927657', 4, 15, 24, 3);
    p('#69543a', 4, 22, 24, 4);
    p('#304f3b', 6, 9, 20, 12);
    p('#46765a', 9, 6, 15, 12);
    p('#608866', 6, 10, 21, 5);
    p('#6e9a72', 12, 5, 9, 5);
    p(alternate ? '#d49783' : '#cbbe77', 11, 8, 3, 3);
    p('#9daf67', 20, 11, 3, 3);
  } else if (id === 'archive') {
    p('#3b3835', 4, 4, 24, 22);
    p('#82715a', 5, 4, 22, 2);
    p('#5a5246', 6, 6, 20, 17);
    for (const y of [7, 16]) {
      p('#292e34', 7, y, 18, 7);
      for (const x of [8, 13, 19]) {
        p('#819089', x, y + 1, 4, 3);
        p(accent, x, y + 4, 2, 1);
      }
    }
  } else if (id === 'mirror') {
    const [width, height] = [[14, 18], [14, 26], [22, 21]][alternate];
    const left = Math.floor((32 - width) / 2);
    p('#28272b70', left - 1, 27, width + 3, 2);
    for (const leg of [left + 1, left + width - 3]) {
      p('#8e7f75', leg, 24, 2, 4);
      p('#5b5053', leg - 1, 27, 4, 1);
    }
    drawSmallDressingMirror(p, left, 26 - height, width, height);
  } else if (id === 'rail') {
    p('#4a4537', 4, 12, 24, 12);
    p('#a18d65', 6, 11, 20, 5);
    p('#49352b', 5, 3, 22, 10);
    p('#9e6f4f', 8, 3, 16, 7);
    p('#bd8865', 11, 2, 10, 2);
    p('#30373a', 10, 14, 12, 7);
    p('#6b8983', 11, 15, 10, 5);
  } else if (id === 'power') {
    p('#282b2c', 3, 9, 26, 18);
    p('#827150', 4, 8, 24, 8);
    p('#b09b68', 5, 8, 22, 1);
    p('#4e4f48', 6, 15, 18, 10);
    for (const x of [8, 12, 16, 20]) p('#303633', x, 16, 2, 7);
    p(alternate ? '#b98759' : '#8d9d72', 24, 17, 3, 3);
    p('#b5aa8c', 7, 25, 2, 3);
    p('#b5aa8c', 24, 25, 2, 3);
  }
}

function drawEndingReward(paint) {
  paint('#252b30', 3, 9, 26, 19);
  paint('#77755e', 4, 10, 24, 16);
  paint('#c5af73', 5, 10, 22, 2);
  paint('#343b3a', 6, 13, 20, 8);
  paint('#a5a58d', 6, 22, 20, 2);
  for (const clasp of [9, 21]) paint('#e3c888', clasp, 19, 2, 5);
}
