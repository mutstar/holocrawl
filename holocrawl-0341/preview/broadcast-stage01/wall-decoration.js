function createWallDecorationPlan(map, choices, reserved) {
  const {w, h, cells, seed, upstairs, exit, start} = map;
  const anchors = [start, upstairs, exit];
  const variants = choices.map(({id, name, sprite, weight}) => ({id, name, sprite, weight, width: sprite.width / 32}));
  const plainWallWeight = 900;
  const decorationWeight = variants.reduce((total, variant) => total + variant.weight, 0);
  const decorations = [];

  function fitsWall(variant, x, y) {
    const index = y * w + x;
    const right = x + variant.width;
    return right < w - 1
      && cells.subarray(index - 1, index + variant.width + 1).every(tile => tile === StreetGen.WALL)
      && cells.subarray(index + w, index + w + variant.width).every(tile => tile === StreetGen.FLOOR)
      && !anchors.some(p => Math.abs(p.y - y) <= 1 && p.x >= x - 1 && p.x <= right)
      && !reserved.some(p => y + 1 >= p.y && y < p.y + p.height && x < p.x + p.width && right > p.x);
  }

  const positions = [];
  for (let y = 2; y < h - 2; y++) for (let x = 2; x < w - 2; x++) {
    const index = y * w + x;
    if (cells[index] !== StreetGen.WALL || cells[index + w] !== StreetGen.FLOOR) continue;
    positions.push({x, y});
    const roll = Math.floor(StreetGen.random(`${seed}:wall-decoration:${x},${y}`)()
      * (plainWallWeight + decorationWeight)) - plainWallWeight;
    if (roll < 0) continue;
    const variant = weightedWallDecoration(variants, roll);
    if (fitsWall(variant, x, y) && !decorations.some(p => y === p.y && x <= p.x + p.width)) {
      decorations.push({...variant, x, y});
    }
  }

  function fill(doors) {
    const random = StreetGen.random(`${seed}:wall-decoration-density`);
    const target = 10 + Math.floor(random() * 6);
    const minSpacing = 4;
    // The preliminary placements help reserve door sites. Rebuild the final set around the doors.
    decorations.length = 0;
    const candidates = [];
    for (const {x, y} of positions) {
      const fits = variants.filter(variant => fitsWall(variant, x, y)
        && !doors.some(door => Math.abs(door.y - y) <= 1 && x <= door.x + 1 && x + variant.width > door.x - 1));
      if (!fits.length) continue;
      const total = fits.reduce((sum, variant) => sum + variant.weight, 0);
      const prop = {...weightedWallDecoration(fits, Math.floor(random() * total)), x, y};
      candidates.push({prop, rank: random(), distance: Infinity});
    }

    while (decorations.length < target) {
      let best;
      for (const candidate of candidates) {
        if (candidate.distance < minSpacing) continue;
        if (!best || candidate.distance > best.distance
            || (candidate.distance === best.distance && candidate.rank < best.rank)) best = candidate;
      }
      if (!best) break;
      decorations.push(best.prop);
      for (const candidate of candidates) {
        candidate.distance = Math.min(candidate.distance, wallDecorationDistance(candidate.prop, best.prop));
      }
    }
  }

  return {decorations, fill};
}

function wallDecorationDistance(a, b) {
  const horizontal = Math.max(0, a.x - (b.x + b.width - 1), b.x - (a.x + a.width - 1));
  return Math.max(horizontal, Math.abs(a.y - b.y));
}

function weightedWallDecoration(variants, roll) {
  for (const variant of variants) {
    roll -= variant.weight;
    if (roll < 0) return variant;
  }
}
