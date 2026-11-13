function createBroadcastArt(atlas, rects, planes) {
  const size = 32;
  const walls = new Map();
  const floors = new Map();

  function sprite(width, height, paint) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    paint(ctx);
    return canvas;
  }

  function floorTile(seed, worldX, worldY) {
    const variant = Math.floor(StreetGen.random(`${seed}:paving:${worldX},${worldY}`)() * 24);
    const column = worldX % 2;
    const key = variant * 2 + column;
    if (!floors.has(key)) floors.set(key, sprite(size, size, ctx => {
      const noise = StreetGen.random(`broadcast-paving-${key}`);
      const image = ctx.createImageData(size, size);
      for (let y = 0; y < size; y++) {
        const jointY = (y + 5) % 16;
        for (let x = 0; x < size; x++) {
          const jointX = (x + column * 32 + (y >= 11 && y < 27 ? 15 : 3)) % 64;
          const joint = jointX === 0 || jointY === 0;
          const bevel = jointX === 1 || jointY === 1;
          const tone = (joint ? -11 : bevel ? 4 : 0) + (variant % 7) - 3 + Math.floor(noise() * 7);
          image.data.set([62 + tone, 65 + tone, 67 + tone, 255], (y * size + x) * 4);
        }
      }
      ctx.putImageData(image, 0, 0);
      ctx.fillStyle = 'rgba(20,28,32,.12)';
      ctx.fillRect(8 + variant % 5, 16, 4, 2);
      ctx.fillRect(21, 28 - variant % 3, 6, 2);
    }));
    return floors.get(key);
  }

  function wallTile(mask, x, y) {
    const variant = (x * 7 + y * 11) % 8;
    const key = mask * 8 + variant;
    if (!walls.has(key)) walls.set(key, sprite(size, size, ctx => {
      ctx.drawImage(atlas, ...rects[`${mask}:0`], 0, 0, size, size);
      const image = ctx.getImageData(0, 0, size, size);
      const front = planes[String(mask)];
      const noise = StreetGen.random(`broadcast-facade-${variant}`);
      for (let py = 0; py < size; py++) for (let px = 0; px < size; px++) {
        const i = (py * size + px) * 4;
        const grain = Math.floor(noise() * 7) - 3;
        if (!image.data[i + 3]) continue;
        const original = image.data[i] * .21 + image.data[i + 1] * .72 + image.data[i + 2] * .07;
        let tone = original * .47 + 9;
        if (front[py * size + px] === '1') {
          const seam = px === 1 || px === 30;
          const skirt = py >= 25 ? -13 : py === 24 ? 8 : 0;
          tone = 80 + original * .17 + skirt + (seam ? -9 : 0) + variant % 4 + grain;
          image.data.set([tone - 13, tone, tone + 9], i);
        } else {
          image.data.set([tone - 4, tone + 1, tone + 5], i);
        }
      }
      ctx.putImageData(image, 0, 0);
    }));
    return walls.get(key);
  }

  function door(open) {
    const {frame, archTop, openingTop} = DoorFit159;
    const inset = (frame.canvasW - frame.w) / 2;
    const right = inset + frame.w;
    return sprite(frame.canvasW, frame.h, ctx => {
      const paint = (color, x, y, width, height) => {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, width, height);
      };
      const jamb = 4;
      const panelLeft = inset + jamb;
      const panelRight = right - jamb;
      const seam = frame.canvasW / 2;
      for (let column = 0; column < frame.w; column++) {
        const x = inset + column;
        const top = archTop(column);
        const opening = openingTop(column);
        paint('#86979b', x, top, 1, 1);
        paint('#4a6068', x, top + 1, 1, opening - top - 1);
        if (x < panelLeft || x >= panelRight) {
          const highlight = x === inset + 1 || x === right - 2;
          paint(highlight ? '#6c7e83' : '#303c42', x, opening, 1, frame.h - opening);
        } else if (!open) {
          const color = x === seam - 1 || x === seam ? '#26343a' : '#51646b';
          paint(color, x, opening, 1, frame.h - opening);
        } else if (x < panelLeft + 2 || x >= panelRight - 2) {
          paint('#38494f', x, opening, 1, frame.h - opening);
        }
      }
      paint('#403639', 10, 2, 12, 4);
      paint('#a0544b', 11, 3, 10, 2);
      paint('#ec9f88', 12, 3, 8, 1);
      if (!open) {
        for (const x of [8, 19]) {
          paint('#293e48', x, 10, 5, 11);
          paint('#4e7884', x + 1, 11, 3, 8);
          paint('#8da9ab', x + 1, 11, 3, 1);
        }
        for (const x of [13, 18]) paint('#a2afad', x, 23, 1, 3);
        paint('#35474e', panelLeft, 28, 9, 3);
        paint('#35474e', panelRight - 9, 28, 9, 3);
      }
      paint('#778b8f', panelLeft, frame.h - 1, panelRight - panelLeft, 1);
      paint('#1d272d', 26, 17, 4, 7);
      paint('#a0aaa0', 27, 18, 2, 1);
      paint('#79b5a8', 27, 20, 2, 1);
    });
  }

  function fixture(type) {
    return sprite(size, size, ctx => {
      if (type === 'onAir') {
        ctx.fillStyle = '#22292e';
        ctx.fillRect(3, 12, 26, 12);
        ctx.fillStyle = '#7b4b49';
        ctx.fillRect(5, 13, 22, 9);
        ctx.fillStyle = '#a34c48';
        ctx.fillRect(6, 14, 20, 7);
        ctx.fillStyle = '#ffb29a';
        const lettering = [
          '111101101101111',
          '110111111111101',
          '010101111101101',
          '111010010010111',
          '110101110101101',
        ];
        lettering.forEach((glyph, index) => {
          const left = 6 + index * 4 + (index >= 2 ? 1 : 0);
          for (let i = 0; i < glyph.length; i++) {
            if (glyph[i] === '1') ctx.fillRect(left + i % 3, 15 + Math.floor(i / 3), 1, 1);
          }
        });
      } else if (type === 'window') {
        ctx.fillStyle = '#282f33';
        ctx.fillRect(0, 8, 32, 15);
        ctx.fillStyle = '#3b515c';
        ctx.fillRect(2, 10, 28, 10);
        ctx.fillStyle = '#596e75';
        ctx.fillRect(3, 11, 26, 1);
        ctx.fillRect(5, 13, 6, 1);
        ctx.fillRect(4, 14, 6, 1);
        ctx.fillStyle = '#6d7c81';
        ctx.fillRect(0, 21, 32, 1);
      } else {
        ctx.fillStyle = '#2b3439';
        ctx.fillRect(7, 10, 18, 14);
        ctx.fillStyle = '#576365';
        ctx.fillRect(8, 11, 16, 11);
        ctx.fillStyle = '#343e42';
        for (let y = 13; y <= 19; y += 2) ctx.fillRect(10, y, 12, 1);
      }
    });
  }

  return {
    floorTile, wallTile, sprite,
    doors: [door(false), door(true)],
    fixtures: {onAir: fixture('onAir'), window: fixture('window'), vent: fixture('vent')},
  };
}
