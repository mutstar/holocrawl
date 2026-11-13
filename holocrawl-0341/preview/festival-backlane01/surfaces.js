function createBacklaneSurfaces(atlas, rects, planes) {
  const size = 32;
  const palettes = [
    {floor: [80, 74, 63], wall: [119, 100, 77], cap: [88, 76, 61], brick: [91, 71, 53]},
    {floor: [70, 67, 59], wall: [108, 95, 75], cap: [79, 71, 58], brick: [84, 67, 52]},
  ];

  function grain(x, y) {
    let value = Math.imul(x + 71, 0x1f123bb5) ^ Math.imul(y + 113, 0x5f356495);
    value = Math.imul(value ^ (value >>> 16), 0x45d9f3b);
    return ((value ^ (value >>> 16)) >>> 0) / 0x100000000;
  }

  function texture(x, y) {
    const broad = grain(Math.floor((x + 2) / 6), Math.floor((y + 4) / 4));
    const grit = grain(x, y);
    return Math.floor(broad * 7) + Math.floor(grit * 8) - 7;
  }

  function tile(paint) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    paint(ctx);
    return canvas;
  }

  function shade(image, index, color, light) {
    for (let channel = 0; channel < 3; channel++) image.data[index + channel] = color[channel] + light;
  }

  function floorTile(floor, tileX, tileY) {
    const material = palettes[floor - 1];
    return tile(ctx => {
      const image = ctx.createImageData(size, size);
      for (let py = 0; py < size; py++) {
        const y = tileY * size + py;
        const row = Math.floor((y + 9) / 29);
        const rowY = (y + 9) % 29;
        for (let px = 0; px < size; px++) {
          const x = tileX * size + px;
          const staggeredX = x + (row % 3) * 23 + 13;
          const slab = Math.floor(staggeredX / 63);
          const slabX = staggeredX % 63;
          const joint = rowY === 0 || slabX === 0;
          const bevel = rowY === 1 || slabX === 1;
          const wear = grain(Math.floor(x / 12), Math.floor(y / 7)) < .19 ? -5 : 0;
          const variation = Math.floor(grain(slab, row + 14) * 10) - 5;
          const light = texture(x, y) + variation + wear + (joint ? -10 : bevel ? 3 : 0);
          const index = (py * size + px) * 4;
          shade(image, index, material.floor, light);
          image.data[index + 3] = 255;
        }
      }
      ctx.putImageData(image, 0, 0);
    });
  }

  function wallTile(floor, mask, tileX, tileY) {
    const material = palettes[floor - 1];
    return tile(ctx => {
      ctx.drawImage(atlas, ...rects[`${mask}:0`], 0, 0, size, size);
      const image = ctx.getImageData(0, 0, size, size);
      const front = planes[String(mask)];
      const variant = Math.floor(grain(tileX + 90, tileY) * 9) - 4;
      for (let py = 0; py < size; py++) {
        const y = tileY * size + py;
        for (let px = 0; px < size; px++) {
          const pixel = py * size + px;
          const index = pixel * 4;
          if (!image.data[index + 3]) continue;
          const x = tileX * size + px;
          const sourceTone = image.data[index] * .21 + image.data[index + 1] * .72 + image.data[index + 2] * .07;
          const relief = (sourceTone - 75) * .43;
          let light = texture(x, y) + relief + variant;
          let color = material.cap;
          if (front[pixel] === '1') {
            color = material.wall;
            if (py >= 24) {
              const brickJoint = py === 27 || (x + (py > 27 ? 6 : 0)) % 16 === 0;
              color = material.brick;
              light += brickJoint ? -12 : py === 24 ? 7 : 0;
            } else if (py > 17 && grain(Math.floor(x / 7), Math.floor(y / 4)) < .25) {
              light -= 8;
            }
          }
          shade(image, index, color, light);
        }
      }
      ctx.putImageData(image, 0, 0);
    });
  }

  return {size, floorTile, wallTile};
}
