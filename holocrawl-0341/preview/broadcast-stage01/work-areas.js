const workAreaWidth = 6;
const workAreaDepth = 4;

function placeStageWorkAreas(map, sites, templates, extraReserved = []) {
  const {w, h, cells, seed, start, upstairs, exit} = map;
  const anchors = [start, upstairs, exit];
  const fixed = [...Object.values(sites), ...extraReserved];
  const random = StreetGen.random(`${seed}:work-areas`);
  const areas = [];

  for (const [kind, site] of Object.entries(sites)) {
    const frontage = {x: site.x + Math.floor(site.width / 2), y: site.y + site.depth - 1};
    const {dist} = StreetGen.distances(map, frontage);
    const occupied = [...fixed, ...areas];
    let best;
    for (let y = 2; y < h - workAreaDepth - 1; y++) {
      for (let x = 2; x < w - workAreaWidth - 1; x++) {
        const distance = dist[(y + 2) * w + x + 3];
        if (distance < 6 || distance > 34) continue;
        if (anchors.some(p => p.x >= x - 1 && p.x <= x + workAreaWidth
            && p.y >= y - 1 && p.y <= y + workAreaDepth)) continue;
        if (occupied.some(p => x < p.x + p.width + 2 && x + workAreaWidth + 2 > p.x
            && y < p.y + p.depth + 2 && y + workAreaDepth + 2 > p.y)) continue;

        // Keep a walkable tile on all four sides of the work area.
        let clear = true;
        for (let row = y - 1; row <= y + workAreaDepth && clear; row++) {
          const left = row * w + x - 1;
          clear = cells.subarray(left, left + workAreaWidth + 2).every(tile => tile === StreetGen.FLOOR);
        }
        if (!clear) continue;
        const rank = Math.abs(distance - 15) + random() * 6;
        if (!best || rank < best.rank) best = {kind, x, y, width: workAreaWidth, depth: workAreaDepth, rank};
      }
    }
    if (!best) continue;

    areas.push(best);
    for (const {sprite, dx, dy, walkable} of templates[kind].props) {
      if (walkable) continue;
      const columns = Math.ceil(sprite.width / 32);
      const rows = Math.ceil(sprite.height / 32);
      for (let row = 0; row < rows; row++) {
        const left = (best.y + dy + row) * w + best.x + dx;
        cells.fill(StreetGen.BARRIER, left, left + columns);
      }
    }
  }
  map.validation = StreetGen.validate(map);
  map.path = StreetGen.route(map, start, exit);
  return areas;
}

function drawStageWorkAreas(layer, areas, templates) {
  for (const {kind, x, y} of areas) {
    const {ground, props} = templates[kind];
    layer.drawImage(ground, x * 32, y * 32);
    for (const {sprite, dx, dy} of props) layer.drawImage(sprite, (x + dx) * 32, (y + dy) * 32);
  }
}

function createStageWorkAreaArt(art, equipment, dock) {
  const sprite = (width, height, draw) => art.sprite(width, height, ctx => draw((color, x, y, w, h) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
  }));
  const mat = (base, edge, mark) => sprite(workAreaWidth * 32, workAreaDepth * 32, p => {
    p(base, 4, 5, 184, 118);
    p(edge, 4, 122, 184, 2);
    p(edge, 4, 5, 184, 2);
    for (const x of [4, 167]) for (const y of [5, 121]) {
      p(mark, x, y, 21, 2);
      p(mark, x === 4 ? x : x + 19, y === 5 ? y : y - 13, 2, 15);
    }
    for (const x of [8, 55, 110, 158]) {
      p('#332e2a70', x + 7, 6, 4, 2);
      p('#332e2a70', x, 121, 6, 2);
    }
  });
  const blue = mat('#53626a68', '#737e8290', '#9a9f92');
  const green = mat('#61684f70', '#80816b90', '#a29d75');
  const amber = mat('#7b644357', '#89755690', '#ad925b');

  const casePair = sprite(64, 32, p => {
    for (const [x, y, w] of [[4, 10, 29], [33, 5, 27]]) {
      p('#302c29', x - 1, y + 15, w + 3, 5);
      p('#242a2c', x, y, w, 18);
      p('#4c5659', x + 2, y, w - 4, 6);
      p('#7c8684', x, y + 6, w, 2);
      p('#3e494c', x + 1, y + 12, w - 2, 4);
      p('#a19e88', x + 5, y + 7, 3, 5);
      p('#a19e88', x + w - 8, y + 7, 3, 5);
      p('#272e30', x + 11, y + 9, 7, 3);
    }
  });
  const spool = sprite(32, 32, p => {
    p('#302b27', 4, 25, 24, 4);
    p('#514536', 6, 8, 20, 18);
    p('#937f60', 7, 7, 18, 6);
    p('#af9970', 10, 6, 12, 2);
    p('#29343a', 9, 13, 14, 11);
    for (const x of [10, 14, 18, 22]) p('#526267', x, 13, 1, 9);
    p('#866b4d', 7, 24, 18, 3);
    p('#b08d55', 20, 22, 6, 2);
    p('#b08d55', 25, 22, 2, 5);
  });
  const lamp = sprite(32, 32, p => {
    p('#302c29', 4, 26, 24, 3);
    p('#282f33', 7, 18, 21, 8);
    p('#666d69', 11, 15, 11, 9);
    p('#272e33', 5, 7, 22, 12);
    p('#687277', 6, 7, 20, 5);
    p('#a9aa85', 7, 9, 6, 8);
    p('#d1be8d', 7, 10, 2, 6);
    p('#3f494e', 16, 12, 9, 5);
  });
  const prop = (sprite, dx, dy, walkable = false) => ({sprite, dx, dy, walkable});

  return {
    lighting: {ground: blue, props: [prop(lamp, 1, 1), prop(lamp, 2, 1), prop(casePair, 3, 2)]},
    cable: {ground: green, props: [prop(spool, 1, 1), prop(spool, 2, 2), prop(casePair, 3, 1)]},
    loading: {ground: amber, props: [prop(equipment.cart, 1, 1), prop(casePair, 3, 2)]},
    service: {ground: blue, props: [prop(casePair, 1, 1), prop(lamp, 4, 1), prop(spool, 4, 2)]},
    lift: {ground: amber, props: [prop(dock.stagingMark, 2, 1, true), prop(dock.cargoCrate, 1, 1), prop(dock.cargoCrate, 3, 2)]},
    warehouse: {ground: green, props: [prop(dock.sceneryPallet, 1, 1), prop(dock.cargoCrate, 4, 1)]},
    shutter: {ground: amber, props: [prop(dock.palletScale, 1, 1, true), prop(dock.cargoCrate, 3, 1), prop(dock.cargoCrate, 3, 2)]},
  };
}
