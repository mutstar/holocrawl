const contestantPodiums = [
  {column: 2, front: '#3f626c', trim: '#83a7ae'},
  {column: 4, front: '#574869', trim: '#a592b5'},
  {column: 6, front: '#725239', trim: '#bf9b69'},
];

const studioVaults = {
  rehearsal: {
    width: 8, height: 6,
    wall: (x, y) => y === 0 || (y < 5 && (x === 0 || x === 7)),
    equipment: [[1, 3], ...contestantPodiums.map(({column}) => [column, 2])],
  },
  storage: {
    width: 6, height: 6,
    wall: (x, y) => y === 0 || x === 0 || x === 5 || (y === 5 && (x === 1 || x === 4)),
    equipment: [[1, 1], [4, 1], [1, 2], [4, 2], [1, 3], [4, 3], [4, 4]],
  },
};

function placeStudioVault(map, kind, avoid) {
  const {w, h, cells, seed} = map;
  const {width, height, wall, equipment} = studioVaults[kind];
  const random = StreetGen.random(`${seed}:${kind}-vault`);
  const anchors = [map.start, map.upstairs, map.exit];
  let site = null;
  for (let y = 2; y < h - height - 1; y++) for (let x = 2; x < w - width - 1; x++) {
    if (anchors.some(p => p.x >= x - 1 && p.x <= x + width && p.y >= y - 1 && p.y <= y + height)) continue;
    if (avoid.some(p => x <= p.x + p.width && x + width >= p.x && y <= p.y + p.height && y + height >= p.y)) continue;
    let clear = true;
    for (let dy = -1; dy <= height && clear; dy++) for (let dx = -1; dx <= width; dx++) {
      if (cells[(y + dy) * w + x + dx] !== StreetGen.FLOOR) { clear = false; break; }
    }
    if (!clear) continue;
    const rank = random();
    if (!site || rank < site.rank) site = {x, y, width, height, rank};
  }
  if (!site) return null;

  const blocked = equipment.map(([x, y]) => ({x: site.x + x, y: site.y + y, tile: StreetGen.BARRIER}));
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    if (wall(x, y)) blocked.push({x: site.x + x, y: site.y + y, tile: StreetGen.WALL});
  }
  return {...site, blocked};
}

function createStudioVaultArt(art, props) {
  function paintWith(ctx) {
    return (color, x, y, w, h) => {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, w, h);
    };
  }

  function flightCase(paint, x, y, width, wheels = false) {
    const handle = x + Math.floor(width / 2) - 3;
    paint('#121518', x + 1, y + 2, width + 1, 21);
    paint('#33383c', x, y, width, 7);
    paint('#191d21', x, y + 7, width, 13);
    paint('#a3aaa8', x + 1, y, width - 2, 1);
    paint('#828c8d', x, y + 1, 2, 18);
    paint('#667376', x + width - 2, y + 1, 2, 18);
    paint('#a4adae', x + 1, y + 7, width - 2, 1);
    paint('#606a6c', x + 1, y + 19, width - 2, 1);
    for (const corner of [x, x + width - 3]) {
      paint('#c2c7be', corner, y + 1, 3, 3);
      paint('#a4acac', corner, y + 17, 3, 3);
    }
    paint('#9a9e96', x + 4, y + 6, 3, 4);
    paint('#9a9e96', x + width - 7, y + 6, 3, 4);
    paint('#6a7375', handle, y + 12, 6, 4);
    paint('#111518', handle + 1, y + 13, 4, 2);
    if (wheels) {
      for (const axle of [x + 3, x + width - 7]) {
        paint('#181c20', axle, y + 20, 4, 4);
        paint('#697476', axle + 1, y + 21, 2, 1);
      }
    }
  }

  const rehearsal = art.sprite(256, 192, ctx => {
    const p = paintWith(ctx);
    for (let y = 0; y < 5; y++) for (let x = 0; x < 8; x++) {
      ctx.drawImage(art.floorTile(x + 5, y + 4, true), x * 32, y * 32);
    }
    p('#191a20', 0, 0, 256, 32);
    p('#282a34', 0, 8, 256, 24);
    p('#1d2028', 0, 29, 256, 3);
    for (let x = 5; x < 253; x += 16) {
      p('#3d3b48', x, 11, 13, 15);
      p('#4d4858', x, 11, 13, 2);
      p('#31323e', x + 11, 13, 2, 13);
    }
    for (const x of [0, 224]) {
      p('#1d2027', x, 0, 32, 161);
      p('#373845', x + 3, 9, 26, 146);
      p('#5c5262', x + 3, 9, 26, 2);
      for (let y = 32; y < 152; y += 24) p('#292b35', x + 3, y, 26, 2);
      p('#131820', x + 3, 154, 26, 6);
      p('#756476', x + 4, 153, 24, 2);
    }

    // A framed cloth backdrop and the countdown are centered on the set wall.
    p('#1b1d25', 63, 12, 131, 36);
    p('#5d4b63', 67, 12, 122, 32);
    p('#746179', 69, 12, 118, 3);
    for (const x of [75, 94, 157, 176]) p('#68536d', x, 16, 4, 27);
    p('#43394c', 68, 41, 120, 3);
    ctx.drawImage(props.wall[3].tile, 96, 12);

    for (const {column, front, trim} of contestantPodiums) {
      const x = column * 32 + 3;
      p('#332821', x + 2, 90, 26, 5);
      p('#25252c', x + 2, 72, 22, 21);
      p(front, x + 4, 74, 18, 17);
      p(trim, x + 5, 75, 16, 1);
      p('#282d35', x + 7, 78, 12, 7);
      p(trim, x + 9, 80, 8, 3);
      p('#454149', x + 1, 66, 24, 7);
      p('#716773', x + 2, 66, 22, 2);
      p('#29282f', x, 72, 26, 2);
      p('#883f43', x + 9, 67, 8, 4);
      p('#d47868', x + 10, 66, 6, 2);
      p('#eeaa92', x + 11, 66, 4, 1);
    }

    // Short dolly rails sit to the left of the clear approach.
    for (let y = 78; y < 145; y += 10) p('#393331', 35, y, 22, 2);
    for (const x of [37, 53]) {
      p('#292a2e', x, 76, 3, 72);
      p('#8b8478', x, 76, 1, 71);
    }
    p('#22262c', 34, 115, 24, 7);
    p('#56616a', 36, 113, 20, 4);
    p('#252d34', 42, 100, 9, 15);
    p('#20262d', 37, 99, 19, 10);
    p('#6b7276', 38, 99, 17, 2);
    p('#2a333c', 44, 95, 9, 4);
    p('#7b969c', 46, 95, 5, 2);
    p('#303c48', 55, 101, 8, 6);
    p('#71919c', 61, 102, 2, 4);
    p('#c3735e', 38, 102, 2, 2);
    p('#302724', 32, 156, 192, 4);
    p('#9a7957', 33, 156, 190, 1);
  });

  const storage = art.sprite(192, 192, ctx => {
    const p = paintWith(ctx);
    for (let y = 0; y < 6; y++) for (let x = 0; x < 6; x++) {
      ctx.drawImage(art.floorTile(x + 8, y + 2, false), x * 32, y * 32);
    }
    p('#1b2227', 0, 0, 192, 32);
    p('#363f43', 3, 8, 186, 21);
    p('#596263', 3, 8, 186, 2);
    for (const x of [0, 160]) {
      p('#21272c', x, 0, 32, 191);
      p('#3c4547', x + 4, 9, 24, 175);
      p('#59615f', x + 4, 9, 24, 2);
      for (let y = 34; y < 180; y += 28) p('#30383c', x + 4, y, 24, 2);
      p('#181e23', x, 184, 32, 7);
    }

    // A rack of painted set flats reads differently from the flight cases.
    p('#232a31', 55, 11, 82, 23);
    p('#656e6c', 56, 11, 80, 2);
    for (const [x, color] of [[59, '#766453'], [77, '#536971'], [95, '#6d5a68'], [113, '#5e6959']]) {
      p(color, x, 16, 15, 13);
      p('#a0947c', x, 16, 15, 1);
      p('#292e33', x + 2, 27, 11, 2);
    }
    p('#4f5b5e', 55, 30, 82, 3);

    for (const [x, height, shelves] of [[33, 60, [61, 93]], [129, 92, [61, 93, 125]]]) {
      p('#272e33', x, 35, 30, height);
      p('#495458', x, 36, 30, 2);
      p('#4d585b', x, 36, 1, height - 1);
      p('#4d585b', x + 29, 36, 1, height - 1);
      for (const y of shelves) p('#495458', x, y, 30, 2);
    }
    flightCase(p, 35, 40, 25);
    flightCase(p, 130, 133, 28, true);

    // Folded backdrop cloths and a portable lamp on a folded stand.
    p('#3d3e4d', 36, 82, 24, 10);
    p('#777084', 36, 83, 24, 5);
    p('#514b5b', 38, 89, 20, 1);
    p('#52605c', 39, 78, 20, 6);
    p('#7f9287', 39, 78, 20, 2);
    p('#8a7362', 41, 75, 16, 4);
    p('#20252b', 35, 122, 27, 3);
    p('#768183', 46, 107, 2, 15);
    p('#657174', 43, 115, 2, 6);
    p('#657174', 50, 115, 2, 6);
    p('#657174', 40, 121, 5, 2);
    p('#657174', 50, 121, 5, 2);
    p('#343c46', 39, 100, 18, 10);
    p('#7e888a', 40, 100, 16, 2);
    p('#c0ac84', 43, 103, 10, 4);
    p('#555963', 55, 102, 3, 6);

    // A wood crate, stacked color bins, and a coiled cable on the right rack.
    p('#47392e', 132, 44, 25, 17);
    p('#84654b', 133, 44, 23, 13);
    p('#a18763', 134, 44, 21, 2);
    p('#5c4938', 135, 48, 19, 2);
    p('#5c4938', 135, 54, 19, 1);
    p('#b0936c', 134, 46, 2, 13);
    p('#9a7b56', 153, 46, 2, 13);
    p('#515b5d', 131, 82, 26, 10);
    p('#859f99', 132, 82, 24, 2);
    p('#344748', 133, 86, 22, 5);
    p('#7d5d43', 136, 74, 19, 8);
    p('#b08b65', 135, 74, 21, 2);
    p('#21272e', 136, 105, 16, 17);
    p('#737775', 139, 104, 10, 19);
    p('#737775', 135, 108, 18, 11);
    p('#2b3033', 138, 107, 12, 13);
    p('#96978c', 141, 110, 6, 6);
    p('#333a40', 143, 112, 2, 2);
    p('#555c5d', 150, 116, 2, 7);
    p('#555c5d', 151, 122, 6, 2);

    for (const x of [28, 128]) {
      p('#252d32', x, 160, 36, 32);
      p('#424a4e', x + 3, 163, 30, 24);
      p('#737b77', x + 3, 163, 30, 2);
      p('#171e23', x, 187, 36, 5);
    }
    for (const x of [64, 125]) for (let y = 165; y < 189; y += 6) p('#aa8b52', x, y, 3, 3);
    p('#4b5659', 67, 183, 58, 3);
    p('#666d66', 67, 183, 58, 1);
  });

  return {rehearsal, storage};
}
