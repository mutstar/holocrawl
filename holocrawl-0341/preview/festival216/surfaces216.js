globalThis.createFestivalSurfaces216 = function ({canvas, g, atlas, wall, rects, planes}) {
  const size = 32;
  const sample = canvas(256, 256);
  g(sample).drawImage(atlas, 0, 0);
  const pixels = g(sample).getImageData(0, 0, 256, 256).data;
  const floorCache = new Map();
  const wallCache = new Map();
  const rows = [0, 13, 32, 49, 64];
  const stagger = [3, 22, 9, 32];
  const stoneTone = [84, 78, 69];
  const reflect = n => {
    const i = n % 256;
    return i < 128 ? i : 255 - i;
  };
  const sampleIndex = (column, row, x, y) =>
    ((row * 128 + reflect(y)) * 256 + column * 128 + reflect(x)) * 4;

  function floorTile(worldX, worldY) {
    // Paving joints run in world space across the edges of dungeon tiles.
    const tx = worldX % 24;
    const ty = worldY % 8;
    const key = ty * 24 + tx;
    if (floorCache.has(key)) return floorCache.get(key);
    const tile = canvas(size, size);
    const ctx = g(tile);
    const image = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) {
      const py = ty * size + y;
      const localY = py % 64;
      const row = rows.findIndex(end => localY < end) - 1;
      const rowY = localY - rows[row];
      const band = Math.floor(py / 64) * 4 + row;
      for (let x = 0; x < size; x++) {
        const px = tx * size + x;
        const shifted = px + stagger[row];
        const slab = Math.floor(shifted / 48) % 16;
        const slabX = shifted % 48;
        const variance = ((slab * 7 + band * 13 + slab * band * 3) % 11) - 5;
        const alternate = (slab + band * 2) % 5 === 1;
        const from = sampleIndex(alternate ? 1 : 0, alternate ? 1 : 0, px, py);
        const to = (y * size + x) * 4;
        const joint = rowY === 0 || slabX === 0;
        const bevel = rowY === 1 || slabX === 1;
        const edge = joint ? -15 : bevel ? 5 : 0;
        for (let channel = 0; channel < 3; channel++) {
          image.data[to + channel] = pixels[from + channel] * .63 + stoneTone[channel] * .37 + variance + edge;
        }
        image.data[to + 3] = 255;
      }
    }
    ctx.putImageData(image, 0, 0);
    floorCache.set(key, tile);
    return tile;
  }

  function wearWallFace(image, front, random) {
    const surface = (x, y) => x >= 0 && y >= 0 && x < size && y < size
      && front[y * size + x] === '1' && image.data[(y * size + x) * 4 + 3];
    function shade(x, y, amount) {
      if (!surface(x, y)) return;
      const i = (y * size + x) * 4;
      for (let c = 0; c < 3; c++) image.data[i + c] += amount;
    }

    // Missing plaster reveals staggered, darker brick beneath the surface.
    if (random() < .56) {
      const atBrickBase = random() < .45;
      const start = atBrickBase ? 22 : 10 + Math.floor(random() * 7);
      const depth = 5 + Math.floor(random() * (atBrickBase ? 6 : 4));
      const center = 7 + Math.floor(random() * 18);
      const radius = 3 + Math.floor(random() * 5);
      let offset = 0;
      for (let row = 0; row < depth && start + row <= 30; row++) {
        const y = start + row;
        offset += Math.floor(random() * 3) - 1;
        const spread = Math.max(1, Math.round(radius * Math.sin((row + 1) / (depth + 1) * Math.PI)));
        const left = Math.max(2, center + offset - spread);
        const right = Math.min(29, center + offset + spread + Math.floor(random() * 3));
        for (let x = left; x <= right; x++) {
          if (!surface(x, y)) continue;
          const i = (y * size + x) * 4;
          const edge = row === 0 || x === left;
          const mortar = (y - start) % 4 === 3 || (x + Math.floor(row / 4) * 3) % 7 === 0;
          const light = (edge ? -17 : mortar ? -12 : 0) + Math.floor(random() * 9);
          const brick = atBrickBase ? [69, 53, 43] : [102, 75, 57];
          for (let c = 0; c < 3; c++) image.data[i + c] = image.data[i + c] * .27 + brick[c] * .73 + light;
        }
        shade(right + 1, y, 12);
      }
    }

    // Break up the angle and weight, so the cracks do not repeat across a wall.
    let x = 6 + Math.floor(random() * 20);
    const y = 10 + Math.floor(random() * 8);
    const length = 8 + Math.floor(random() * 10);
    let drift = random() < .5 ? -1 : 1;
    for (let step = 0; step < length && y + step < 31; step++) {
      const row = y + step;
      const strength = step < 2 || step >= length - 2 ? 24 : 46;
      shade(x + 1, row, 11);
      shade(x, row, -strength);
      if (step > 3 && step < 8 && step % 2 === 0) shade(x - 1, row, -22);
      if (step === 4 && random() < .65) {
        for (let branch = 1; branch <= 5; branch++) {
          shade(x - drift * branch, row + Math.floor(branch / 2), -36 + branch * 4);
        }
      }
      if (random() < .22) drift = -drift;
      if (random() < .68 && x + drift > 2 && x + drift < 29) {
        shade(x + drift, row, -strength / 2);
        x += drift;
      }
    }
  }

  function wallTile(mask, worldX, worldY, wearRandom) {
    const tx = worldX % 8;
    const ty = worldY % 8;
    const key = mask * 64 + ty * 8 + tx;
    if (!wearRandom && wallCache.has(key)) return wallCache.get(key);
    const tile = canvas(size, size);
    const ctx = g(tile);
    ctx.drawImage(wall, ...rects[`${mask}:0`], 0, 0, size, size);
    const image = ctx.getImageData(0, 0, size, size);
    const front = planes[String(mask)];
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const i = (y * size + x) * 4;
      if (!image.data[i + 3]) continue;
      if (front[y * size + x] !== '1') {
        const light = image.data[i] * .2126 + image.data[i + 1] * .7152 + image.data[i + 2] * .0722;
        image.data[i] = light * .93;
        image.data[i + 1] = light * .84;
        image.data[i + 2] = light * .74;
        continue;
      }
      const brick = y >= 23;
      const from = brick
        ? sampleIndex(0, 1, tx * size + x, (y - 23) * 2 + 29)
        : sampleIndex(1, 0, tx * size + x, ty * size + y);
      const shade = brick ? .93 : .85 - (y - 10) * .003;
      const ledge = y === 23 ? 8 : y === 24 ? -6 : y === 31 ? -6 : 0;
      for (let channel = 0; channel < 3; channel++) {
        image.data[i + channel] = pixels[from + channel] * shade + ledge;
      }
    }
    if (wearRandom) wearWallFace(image, front, wearRandom);
    ctx.putImageData(image, 0, 0);
    if (!wearRandom) wallCache.set(key, tile);
    return tile;
  }

  return {floorTile, wallTile};
};
