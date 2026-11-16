function placeEquipmentFloorBays(map) {
  const {w, h, cells, seed, start, upstairs, exit} = map;
  const random = StreetGen.random(`${seed}:equipment-bays`);
  const anchors = [start, upstairs, exit];
  const bays = {};
  const specs = [['lighting', 6, 4], ['cable', 6, 4], ['loading', 8, 5], ['service', 6, 4]];
  for (const [kind, width, depth] of specs) {
    const reserved = Object.values(bays);
    let best;
    for (let y = 3; y < h - depth - 1; y++) for (let x = 2; x < w - width - 1; x++) {
      if (anchors.some(p => p.x >= x - 1 && p.x <= x + width && p.y >= y - 1 && p.y <= y + depth)) continue;
      if (reserved.some(p => x < p.x + p.width + 2 && x + width + 2 > p.x
          && y < p.y + p.depth + 2 && y + depth + 2 > p.y)) continue;
      let clear = true;
      for (let dx = 0; dx < width && clear; dx++) {
        if (cells[(y - 1) * w + x + dx] !== StreetGen.WALL) { clear = false; break; }
        for (let dy = 0; dy < depth; dy++) {
          if (cells[(y + dy) * w + x + dx] !== StreetGen.FLOOR) { clear = false; break; }
        }
      }
      if (!clear) continue;
      const rank = random();
      if (!best || rank < best.rank) best = {x, y, width, depth, rank};
    }
    if (best) bays[kind] = best;
  }
  if (bays.loading) bays.loading.cartColumn = random() < .5 ? 1 : 5;
  return bays;
}

function blockEquipmentFloorBays(map, bays) {
  const occupied = {
    lighting: [[1, 0], [2, 0], [3, 0], [4, 0]],
    loading: [[1, 0], [2, 0], [3, 0], [4, 0]],
    service: [[2, 1], [3, 1], [4, 1]],
  };
  for (const [kind, tiles] of Object.entries(occupied)) {
    const bay = bays[kind];
    if (!bay) continue;
    for (const [dx, dy] of tiles) map.cells[(bay.y + dy) * map.w + bay.x + dx] = StreetGen.BARRIER;
  }
  if (bays.loading) {
    const {x, y, cartColumn} = bays.loading;
    const leftWheelTile = (y + 2) * map.w + x + cartColumn;
    map.cells.fill(StreetGen.BARRIER, leftWheelTile, leftWheelTile + 2);
  }
}

function createEquipmentFloorArt(art, atlas, rects, planes) {
  const floors = new Map();
  const walls = new Map();

  function floorTile(x, y) {
    const variant = Math.floor(StreetGen.random(`equipment-tile:${x},${y}`)() * 19);
    if (!floors.has(variant)) floors.set(variant, art.sprite(32, 32, ctx => {
      const random = StreetGen.random(`equipment-concrete:${variant}`);
      const stains = Array.from({length: 4}, () => ({x: random() * 32, y: random() * 32, r: 3 + random() * 11}));
      const base = [65, 66, 62];
      const pixels = ctx.createImageData(32, 32);
      for (let py = 0; py < 32; py++) for (let px = 0; px < 32; px++) {
        const blotch = stains.reduce((tone, stain) => {
          const distance = Math.abs(px - stain.x) + Math.abs(py - stain.y);
          return tone + Math.max(0, 1 - distance / stain.r) * 7;
        }, 0);
        const seam = (px === 0 || py === 0) ? 6 : 0;
        const tone = Math.floor(random() * 7) - 3 - blotch - seam;
        pixels.data.set([base[0] + tone, base[1] + tone, base[2] + tone, 255], (py * 32 + px) * 4);
      }
      ctx.putImageData(pixels, 0, 0);
      if (variant % 4 === 0) {
        ctx.fillStyle = '#4d4841';
        ctx.fillRect(10, 22, 8, 1);
        ctx.fillRect(17, 21, 5, 1);
        ctx.fillRect(21, 20, 3, 1);
      }
    }));
    return floors.get(variant);
  }

  function wallTile(mask, x, y) {
    const variant = (x * 3 + y * 5) % 7;
    const key = mask * 7 + variant;
    if (!walls.has(key)) walls.set(key, art.sprite(32, 32, ctx => {
      ctx.drawImage(atlas, ...rects[`${mask}:0`], 0, 0, 32, 32);
      const pixels = ctx.getImageData(0, 0, 32, 32);
      const front = planes[String(mask)];
      for (let i = 0; i < 1024; i++) {
        const offset = 4 * i;
        if (!pixels.data[offset + 3]) continue;
        const original = pixels.data[offset + 1];
        const row = Math.floor(i / 32);
        const facing = front[i] === '1';
        const lip = row === 6 ? 14 : row >= 25 ? -12 : 0;
        const tone = facing ? 66 + original * .3 + lip + variant : 12 + original * .5;
        pixels.data.set([tone, tone - 4, tone - 8], offset);
      }
      ctx.putImageData(pixels, 0, 0);
    }));
    return walls.get(key);
  }

  function baySprite(kind) {
    return art.sprite(192, 96, ctx => {
      const paint = (color, x, y, w, h) => {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, w, h);
      };

      if (kind === 'lighting') {
        paint('#202629', 14, 9, 164, 22);
        paint('#828986', 15, 8, 162, 2);
        paint('#536163', 15, 10, 162, 2);
        for (let x = 20; x < 171; x += 33) {
          paint('#424c50', x, 13, 24, 15);
          paint('#252d31', x + 3, 16, 18, 8);
          paint('#5c7171', x + 4, 17, 16, 1);
          if (x < 110) {
            paint('#8bae90', x + 5, 20, 5, 2);
            paint('#b59561', x + 12, 21, 2, 1);
          }
          paint('#30363b', x + 18, 25, 3, 1);
        }
        paint('#333b3c', 37, 32, 119, 17);
        paint('#50595a', 39, 33, 114, 8);
        paint('#92918a', 39, 33, 114, 1);
        for (let x = 46; x < 147; x += 7) {
          paint('#272e32', x, 35, 2, 5);
          paint('#b8b19b', x - 1, 36 + x % 3, 4, 1);
        }
        for (const x of [38, 150]) paint('#242c2e', x, 48, 4, 8);
        paint('#333837', 32, 60, 128, 23);
        paint('#626661', 34, 61, 124, 1);
        paint('#252a29', 34, 80, 124, 2);
        for (let x = 37; x < 157; x += 5) {
          paint('#474d48', x, 64, 1, 14);
          paint('#444840', x, 77, 3, 1);
        }
      } else {
        paint('#282c2b', 5, 16, 182, 12);
        for (const y of [18, 23]) {
          paint('#8a7960', 6, y, 180, 2);
          paint('#534a40', 6, y + 2, 180, 1);
        }
        for (const x of [12, 43, 149, 177]) paint('#5a6667', x, 16, 4, 12);
        paint('#252d30', 68, 7, 55, 23);
        paint('#636e70', 69, 7, 53, 2);
        paint('#444f50', 70, 9, 51, 18);
        paint('#9c8559', 75, 13, 10, 4);
        paint('#232d2e', 74, 20, 13, 3);
        for (let x = 91; x < 117; x += 5) paint('#232929', x, 13, 2, 10);

        // Covered cable channel is flush with the floor. The warning stripes mark the transition.
        const channelX = 81;
        paint('#302e28', channelX, 31, 30, 65);
        paint('#555d5c', channelX + 2, 31, 26, 65);
        for (let y = 34; y < 95; y += 5) {
          paint('#282d2f', channelX + 6, y, 18, 2);
          paint('#767c75', channelX + 6, y + 2, 18, 1);
        }
        for (const x of [channelX, channelX + 27]) {
          for (let y = 37; y < 94; y += 8) paint('#a58e5c', x, y, 3, 4);
        }
        paint('#1e2528', channelX + 6, 59, 18, 18);
        paint('#825b47', channelX + 11, 59, 2, 18);
        paint('#7a7653', channelX + 17, 59, 2, 18);
      }
    });
  }

  const loading = art.sprite(256, 64, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};

    // The upper casing sits on the wall, with the recessed lift and tracks below.
    p('#22282b', 40, 8, 112, 56);
    p('#605951', 43, 9, 106, 52);
    p('#191d21', 48, 11, 96, 47);
    p('#343c40', 53, 27, 86, 29);
    for (const x of [53, 135]) {
      p('#848983', x, 22, 4, 35);
      p('#454c4d', x + 1, 22, 2, 35);
    }
    for (const y of [38, 46, 55]) p('#252d30', 57, y, 78, 1);
    for (const x of [72, 117]) for (let y = 26; y < 51; y += 4) p('#96907c', x, y, 2, 2);
    p('#576066', 48, 12, 96, 19);
    p('#8b8f88', 48, 12, 96, 2);
    for (let y = 16; y < 30; y += 4) {
      p('#353d41', 50, y, 92, 1);
      p('#656d70', 50, y + 1, 92, 1);
    }
    p('#252c2e', 49, 30, 94, 3);
    p('#575c57', 56, 55, 80, 3);
    p('#221f1c', 43, 58, 106, 4);
    for (let x = 46; x < 144; x += 10) p('#a18755', x, 58, 5, 2);
    p('#212729', 155, 15, 10, 15);
    p('#829473', 158, 18, 4, 3);
    p('#9b6651', 159, 24, 2, 2);
  });

  const cart = art.sprite(64, 32, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};
    p('#302d2b', 0, 23, 64, 7);
    p('#242a2e', 6, 18, 55, 8);
    p('#777e7a', 7, 18, 53, 2);
    for (const x of [8, 50]) {
      p('#262a2d', x, 24, 8, 6);
      p('#5c625f', x + 2, 25, 4, 3);
    }
    p('#777a70', 4, 12, 2, 8);
    p('#888b80', 1, 11, 5, 2);
    p('#5d6567', 7, 8, 51, 11);
    p('#343e42', 8, 10, 49, 7);
    for (let x = 8; x + 11 < 58; x += 12) {
      for (let step = 0; step < 6; step++) {
        p('#999d95', x + step, 16 - step, 1, 1);
        p('#757f81', x + step + 6, 11 + step, 1, 1);
      }
    }
    p('#a2a49c', 7, 8, 51, 1);
    p('#87908e', 7, 17, 51, 1);
    for (const x of [17, 41]) {
      p('#262e36', x, 1, 12, 9);
      p('#626d71', x + 1, 1, 10, 2);
      p('#38464d', x + 2, 4, 10, 5);
      p('#ae9e7b', x + 10, 3, 2, 5);
    }
  });

  const fan = art.sprite(64, 32, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};
    const disk = (color, cx, cy, radius) => {
      for (let y = -radius; y <= radius; y++) {
        const half = Math.floor(Math.sqrt(radius * radius - y * y));
        p(color, cx - half, cy + y, half * 2 + 1, 1);
      }
    };
    p('#242b2e', 8, 4, 48, 25);
    p('#59625f', 9, 4, 46, 23);
    p('#93998f', 10, 4, 44, 1);
    p('#373f3e', 11, 6, 42, 20);
    p('#787c70', 12, 26, 40, 1);
    for (const x of [13, 49]) for (const y of [9, 23]) p('#aaa28f', x, y, 2, 1);
    for (const x of [16, 44]) for (const y of [13, 16, 19]) {
      p('#283232', x, y, 4, 1);
      p('#5d6660', x, y + 1, 4, 1);
    }
    disk('#1b2428', 32, 16, 9);
    disk('#87958f', 32, 16, 8);
    disk('#182225', 32, 16, 7);

    ctx.save();
    ctx.translate(32, 16);
    for (let blade = 0; blade < 4; blade++) {
      p('#758b84', 1, -1, 4, 2);
      p('#a7bbb1', 2, -2, 5, 2);
      p('#b5c4b7', 3, -3, 4, 1);
      p('#ced7c9', 4, -4, 2, 1);
      ctx.rotate(Math.PI / 2);
    }
    ctx.restore();
    disk('#293a3c', 32, 16, 2);
    disk('#a7ac9d', 32, 16, 1);
    p('#57534a', 22, 29, 8, 1);
    p('#4d4b43', 29, 30, 7, 1);
  });

  const curtainRoll = art.sprite(96, 32, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};
    p('#2b2729', 10, 8, 76, 20);
    p('#5f5e56', 10, 7, 76, 5);
    p('#909184', 12, 7, 72, 1);
    for (const x of [12, 80]) {
      p('#79766e', x, 9, 4, 17);
      p('#454746', x + 3, 10, 2, 16);
    }
    p('#553540', 17, 10, 62, 14);
    p('#79505a', 18, 11, 60, 8);
    p('#a16b73', 19, 11, 58, 1);
    p('#50313a', 18, 20, 60, 3);
    p('#65404b', 20, 24, 56, 5);
    for (const x of [24, 34, 45, 55, 67]) {
      p('#8a5760', x, 24, 2, 4);
      p('#4b303b', x + 3, 25, 2, 4);
    }
    p('#9c7171', 21, 28, 54, 1);
    for (const x of [31, 64]) {
      p('#897557', x, 10, 3, 14);
      p('#b09a74', x, 11, 1, 12);
      p('#4a3b3a', x - 1, 22, 5, 3);
      p('#a89471', x, 22, 3, 1);
    }
  });

  const powerLever = art.sprite(64, 32, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};
    p('#272a2b', 13, 6, 30, 24);
    p('#666960', 14, 6, 28, 22);
    p('#a09e8d', 15, 6, 26, 1);
    p('#3c4141', 18, 9, 20, 16);
    p('#6b6a59', 19, 10, 18, 14);
    p('#292f30', 26, 11, 5, 12);
    p('#a6a28e', 27, 15, 2, 7);
    p('#442e30', 22, 13, 13, 6);
    p('#a85f50', 22, 12, 13, 5);
    p('#cb8874', 23, 12, 11, 1);
    p('#292825', 18, 25, 20, 3);
    for (const x of [19, 25, 31]) p('#b3975e', x, 25, 3, 1);
    p('#313839', 42, 13, 11, 7);
    p('#69716a', 44, 13, 8, 1);
    p('#a38b62', 47, 15, 3, 2);
  });

  const service = art.sprite(192, 96, ctx => {
    const p = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};

    // The folded ladder hangs from two wall catches above the floor.
    p('#2b2d2c', 16, 7, 53, 24);
    p('#464b49', 17, 8, 51, 20);
    for (const x of [25, 56]) {
      p('#333637', x, 7, 6, 22);
      p('#a19477', x + 1, 7, 4, 20);
      p('#b9ac8d', x + 1, 7, 1, 20);
      p('#5a5c52', x, 28, 6, 2);
    }
    for (const y of [9, 14, 19, 24]) {
      p('#656e69', 31, y, 25, 2);
      p('#a1a497', 31, y, 25, 1);
    }
    for (const x of [21, 59]) {
      p('#353c3c', x, 14, 5, 5);
      p('#bc9e67', x + 1, 14, 4, 2);
    }

    p('#32302c', 65, 86, 93, 5);
    for (const x of [68, 150]) {
      p('#2a3234', x, 73, 6, 15);
      p('#73756b', x, 73, 2, 14);
    }
    p('#3d4748', 73, 82, 77, 3);
    p('#2d3335', 65, 66, 92, 12);
    p('#626765', 65, 66, 92, 9);
    p('#97978b', 66, 67, 90, 1);
    p('#4d5656', 66, 73, 90, 3);

    // Lamp body, removed lens, and tools lie across the worktop.
    p('#2b3338', 73, 64, 24, 8);
    p('#6c7777', 75, 64, 17, 4);
    p('#9f8b64', 92, 65, 5, 6);
    p('#c5b286', 93, 65, 4, 1);
    p('#343d3d', 101, 64, 10, 8);
    p('#8b9b91', 103, 65, 6, 6);
    p('#566b68', 104, 66, 4, 4);
    p('#363d3e', 118, 65, 15, 7);
    p('#a8aaa0', 119, 66, 9, 2);
    p('#a58060', 127, 69, 6, 2);
    p('#3c4341', 138, 65, 13, 8);
    p('#8b7b62', 140, 66, 9, 6);
    p('#3c4341', 142, 67, 5, 3);
  });

  return {
    floorTile, wallTile, bays: {lighting: baySprite('lighting'), cable: baySprite('cable'), loading, service}, cart,
    fixtures: {fan, 'curtain-roll': curtainRoll, 'power-lever': powerLever},
  };
}
