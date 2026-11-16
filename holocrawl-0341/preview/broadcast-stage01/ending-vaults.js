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
  for (const {x: dx, y: dy, tile} of footprint) {
    const point = {x: x + dx, y: y + dy};
    const index = point.y * w + point.x;
    cells[index] = endingWalkable(tile) ? StreetGen.FLOOR : '~opP'.includes(tile) ? StreetGen.BARRIER : StreetGen.WALL;
    if (tile === 'r') reward = point;
    if (tile === 's') guard = point;
  }
  return {ending, x, y, entry, reward, guard, width: ending.width, depth: ending.depth};
}

function drawStageEnding(layer, ending, originX = 0, originY = 0) {
  const {id, width, depth, palette: [floor, trim, wall, accent]} = ending;
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
      if (!atEntrance && inside !== '#' && inside !== ' ' && (x + y * 3) % 4 < 2) {
        // Recess details into the existing dock wall face and retain its coping and lower trim.
        paint(`${trim}38`, 3, 11, 26, 11);
        drawEndingWallDetail(paint, id, wall, accent, x, y);
      }
    } else {
      if (tile === '~') {
        paint('#233b498e', 0, 0, 32, 32);
        for (const py of [6, 15, 26]) {
          const rippleX = 2 + (py + x * 7 + y * 9) % 18;
          paint('#38616b', rippleX, py, 10, 1);
          paint('#557d81', rippleX + 3, py + 1, 4, 1);
        }
      } else if (!atEntrance) {
        paint(`${floor}${y < depth - 4 ? '5c' : '29'}`, 0, 0, 32, 32);
      }
      if (tile === '=' && !atEntrance) drawEndingPath(paint, ending, trim, accent, x, y);
      if (tile === 'o') drawEndingProp(paint, id, trim, accent, (x + y) % 2);
      if (tile === 'e') {
        paint('#2e302e', 0, 28, 32, 2);
        paint('#777266', 0, 28, 32, 1);
        for (const x of [2, 25]) paint('#a18a53', x, 25, 5, 1);
      }
      if (tile === 'r') drawEndingReward(paint);
    }
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
    drawEndingFixture(paint, id, 'floor', accent);
    layer.restore();
  }
}

function drawEndingWallDetail(paint, id, shadow, accent, x, y) {
  if (id === 'garden' || id === 'mirror') {
    paint(shadow, 5, 11, 22, 10);
    paint(id === 'garden' ? '#416a63' : '#646c84', 6, 12, 20, 7);
    paint('#c1dcd56d', 8, 14, 9, 1);
    paint('#c1dcd56d', 9, 15, 4, 1);
    if (id === 'mirror') for (const n of [7, 15, 23]) paint(accent, n, 11, 2, 2);
  } else if (id === 'street' || id === 'rail') {
    paint('#241a1a4a', 0, 17, 32, 1);
    paint('#241a1a4a', 0, 22, 32, 1);
    paint('#241a1a4a', 13 + (x + y) % 4, 12, 1, 5);
    paint('#241a1a4a', 5 + (x + y) % 3, 18, 1, 4);
  } else if (id === 'horror') {
    for (const x of [2, 10, 18, 26]) paint('#2f192c7d', x, 12, 3, 8);
  } else if (id === 'flood') {
    paint('#567e7b', 0, 23, 32, 1);
    paint('#304d4f', 0, 24, 32, 2);
  } else if (id === 'tower' || id === 'factory' || id === 'power') {
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
  if (id === 'rail') {
    const horizontal = endingTile(ending, x - 1, y) === '=' || endingTile(ending, x + 1, y) === '=';
    const vertical = endingTile(ending, x, y - 1) === '=' || endingTile(ending, x, y + 1) === '=';
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
  } else if (id === 'tower' || id === 'flood' || id === 'factory') {
    paint('#282d3290', 1, 1, 30, 30);
    for (const stripe of [4, 12, 20, 28]) paint(`${trim}9c`, 3, stripe, 26, 1);
    if ((x + y) % 2 === 0) for (const side of [2, 28]) paint(`${accent}93`, side, 3, 2, 5);
  } else if (id === 'street') {
    paint('#78664f35', 0, 6, 32, 20);
    for (const y of [5, 26]) paint('#a68b5e8a', 4, y, 13, 1);
    paint('#473d3450', 1, 6, 30, 1);
  } else {
    paint(`${trim}${id === 'horror' ? '78' : '50'}`, 1, 1, 30, 30);
    if ((x + y) % 3 === 0) paint(`${accent}8c`, 4 + (x * 3 + y * 7) % 9, 5, 8, 1);
    paint('#11192339', 2, 28, 28, 2);
  }
}

function drawEndingProp(p, id, trim, accent, alternate) {
  p('#10131aa0', 3, 23, 27, 6);
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
  } else if (id === 'factory') {
    p('#485459', 3, 20, 26, 7);
    p('#92a29b', 5, 20, 22, 2);
    p('#776340', 11, 12, 10, 10);
    p('#b79355', 12, 11, 8, 9);
    p('#a48148', 7, 8, 12, 6);
    p('#d1a861', 7, 7, 11, 2);
    p('#987e50', 6, 5, 4, 8);
    p('#6f8580', 6, 3, 7, 3);
    p('#272f32', 5, 3, 2, 4);
  } else if (id === 'horror') {
    p('#171622', 5, 22, 22, 5);
    p('#3c3545', 7, 4, 18, 21);
    p('#8d7584', 9, 5, 14, 17);
    p(alternate ? '#51415b' : '#762e4c', 11, 7, 10, 13);
    p('#c6b4b0', 13, 9, 6, 6);
    p('#544153', 14, 11, 1, 2);
    p('#544153', 17, 11, 1, 2);
    p('#2a2430', 8, 24, 2, 5);
    p('#2a2430', 22, 24, 2, 5);
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
    p('#292e3b', 7, 3, 19, 21);
    p('#9a8499', 8, 3, 17, 16);
    p('#54687b', 10, 5, 13, 11);
    p('#aac4cd', 11, 7, 7, 1);
    p('#7897a4', 12, 8, 3, 1);
    p('#685568', 5, 18, 23, 8);
    p('#977c8d', 6, 18, 21, 2);
    for (const x of [9, 22]) p('#dac6ac', x, 6, 2, 2);
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
