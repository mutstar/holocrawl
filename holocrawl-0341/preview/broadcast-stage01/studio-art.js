function createStudioArt(atlas, rects, planes) {
  const {sprite} = createBroadcastArt(atlas, rects, planes);
  const paving = new Map();
  const walls = new Map();

  function floorTile(x, y, platform) {
    const variant = (x * 13 + y * 19 + x * y * 7) % 13;
    const key = `${platform}:${variant}:${y % 3}`;
    if (!paving.has(key)) paving.set(key, sprite(32, 32, ctx => {
      const image = ctx.createImageData(32, 32);
      const random = StreetGen.random(`rehearsal-floor-${key}`);
      const base = platform ? [99, 75, 56] : [48, 53, 58];
      for (let py = 0; py < 32; py++) for (let px = 0; px < 32; px++) {
        const row = py + (y % 3) * 32;
        const seam = platform ? row % 6 === 0 : px === 0 || py === 0;
        const plankTone = platform ? (Math.floor(row / 6) % 4) * 2 - 3 : 0;
        const grit = Math.floor(random() * 8) - 4;
        const tone = (variant % 5) - 2 + plankTone + grit - (seam ? 9 : 0);
        const index = (py * 32 + px) * 4;
        image.data.set([base[0] + tone, base[1] + tone, base[2] + tone, 255], index);
      }
      ctx.putImageData(image, 0, 0);
    }));
    return paving.get(key);
  }

  function wallTile(mask, x, y) {
    const variant = (x * 5 + y * 7) % 6;
    const key = mask * 6 + variant;
    if (!walls.has(key)) walls.set(key, sprite(32, 32, ctx => {
      ctx.drawImage(atlas, ...rects[`${mask}:0`], 0, 0, 32, 32);
      const image = ctx.getImageData(0, 0, 32, 32);
      const front = planes[String(mask)];
      for (let py = 0; py < 32; py++) for (let px = 0; px < 32; px++) {
        const pixel = py * 32 + px;
        const index = pixel * 4;
        if (!image.data[index + 3]) continue;
        const original = image.data[index + 1];
        if (front[pixel] === '1') {
          const rail = py === 23 ? 16 : py > 23 ? -9 : 0;
          const groove = py < 23 && px % 8 === 0 ? -9 : 0;
          const tone = 57 + original * .27 + rail + groove + variant;
          image.data.set([tone - 7, tone + 1, tone + 4], index);
        } else {
          const tone = original * .48 + 6;
          image.data.set([tone - 4, tone, tone + 6], index);
        }
      }
      ctx.putImageData(image, 0, 0);
    }));
    return walls.get(key);
  }

  function wallBay(kind) {
    return sprite(96, 32, ctx => {
      const paint = (color, x, y, w, h) => {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, w, h);
      };
      paint('#28343c', 1, 5, 94, 26);
      paint('#6e8188', 2, 5, 92, 2);
      paint('#192127', 5, 8, 86, 20);
      paint('#52636c', 3, 9, 2, 19);
      paint('#44525c', 91, 9, 2, 19);
      paint('#7b8785', 5, 28, 86, 1);
      if (kind === 'window') {
        for (const x of [8, 36, 64]) {
          paint('#314954', x, 10, 24, 16);
          paint('#58757e', x, 10, 24, 2);
          paint('#42626a', x + 2, 13, 20, 10);
          paint('#739297', x + 3, 13, 9, 1);
          paint('#688991', x + 2, 14, 8, 1);
          paint('#243742', x + 2, 23, 20, 2);
        }
      } else if (kind === 'rack') {
        for (const x of [10, 36, 62]) {
          paint('#4d575d', x, 10, 24, 16);
          for (const y of [12, 17, 22]) {
            paint('#212a30', x + 1, y, 22, 3);
            paint(y === 17 ? '#c38555' : '#87baaa', x + 3, y + 1, 2, 1);
            paint('#839196', x + 9, y + 1, 10, 1);
          }
        }
      } else {
        paint('#434c55', 7, 9, 82, 18);
        for (let y = 11; y <= 25; y += 4) {
          paint('#252d35', 7, y, 82, 1);
          paint('#5d6973', 9, y + 1, 78, 1);
        }
        paint('#a6824b', 40, 23, 16, 3);
        paint('#23282a', 47, 23, 2, 3);
      }
    });
  }

  return {sprite, floorTile, wallTile, wallBay};
}
