function createBroadcastWear(art, wallArt, groundArt) {
  function marks(ctx, random, count, color, width, top, height) {
    ctx.fillStyle = color;
    for (let i = 0; i < count; i++) {
      const x = 2 + Math.floor(random() * (width - 7));
      const y = top + Math.floor(random() * height);
      ctx.fillRect(x, y, 2 + Math.floor(random() * 4), 1);
    }
  }

  function fracture(ctx, random, x, y, length, dx, dy, opacity) {
    function trace(x, y, steps, dx, dy, branch) {
      let drift = random() < .5 ? -1 : 1;
      for (let step = 0; step < steps; step++) {
        const weight = step >= steps - 2 ? .48 : 1;
        ctx.fillStyle = 'rgba(22,25,26,' + opacity * weight + ')';
        ctx.fillRect(x, y, 1, 1);
        if (branch && step === Math.floor(steps * .45) && random() < .45) {
          trace(x, y, 3 + Math.floor(random() * 4), -dy * drift, dx * drift, false);
        }
        x += dx;
        y += dy;
        if (random() < .20) drift *= -1;
        if (random() < .65) {
          x -= dy * drift;
          y += dx * drift;
        }
      }
    }
    trace(x, y, length, dx, dy, true);
  }

  function paving(ctx, random, level) {
    if (level >= 2 && random() < (level === 2 ? .15 : .24)) {
      const fromUpperJoint = random() < .65;
      const startX = 9 + Math.floor(random() * 14);
      const joint = fromUpperJoint ? 11 : 27;
      fracture(ctx, random, startX, joint, 4 + Math.floor(random() * 9), 0, fromUpperJoint ? 1 : -1, .48);
    }
    marks(ctx, random, level * 2, 'rgba(27,29,25,.28)', 32, 4, 23);
    if (level === 3) marks(ctx, random, 5, 'rgba(142,130,100,.24)', 32, 6, 21);
  }

  function wall(ctx, random, level, face) {
    ctx.save();
    ctx.beginPath();
    for (let y = 10; y < 31; y++) {
      for (let x = 0; x < 32; x++) if (face[y * 32 + x] === '1') ctx.rect(x, y, 1, 1);
    }
    ctx.clip();
    if (level >= 2 && random() < (level === 2 ? .24 : .37)) {
      const left = random() < .5;
      fracture(ctx, random, left ? 1 : 30, 15 + Math.floor(random() * 10),
        5 + Math.floor(random() * 12), left ? 1 : -1, 0, .55);
    }
    marks(ctx, random, level * 3, 'rgba(31,36,31,.38)', 32, 12, 17);
    if (level >= 2) {
      marks(ctx, random, level, 'rgba(159,151,119,.36)', 32, 18, 11);
    }
    ctx.restore();
  }

  function weathered(source, type, level, variant = 0) {
    if (!level) return source;
    const {width, height} = source;
    return art.sprite(width, height, ctx => {
      ctx.drawImage(source, 0, 0);
      ctx.globalCompositeOperation = 'source-atop';
      ctx.fillStyle = 'rgba(23,24,22,' + (level * .1) + ')';
      ctx.fillRect(0, 0, width, height);
      const random = StreetGen.random('broadcast-equipment:' + type + ':' + variant);
      marks(ctx, random, level * (width > 32 ? 13 : 5), 'rgba(126,106,80,.40)', width, 7, height - 12);
      if (level >= 2 && type === 'window' && variant > 0) {
        const starts = [[8, 10, 0, 1], [24, 19, 0, -1], [5, 16, 1, 0]];
        const [x, y, dx, dy] = starts[variant - 1];
        ctx.save();
        ctx.beginPath();
        ctx.rect(2, 10, 28, 10);
        ctx.clip();
        fracture(ctx, random, x, y, 4 + variant * 2, dx, dy, .64);
        ctx.restore();
      }
      if (level >= 2 && type === 'monitorRack') {
        ctx.fillStyle = '#292d31';
        ctx.fillRect(12, 19, 8, 5);
        fracture(ctx, random, 16, 8, 5, 0, 1, .62);
      }
      if (level >= 2 && type === 'scheduleBoard') {
        ctx.fillStyle = '#2d3335';
        ctx.fillRect(12, 14, 11, 6);
      }
      if (level === 3 && type === 'onAir') {
        ctx.fillStyle = '#473638';
        ctx.fillRect(5, 13, 22, 9);
        ctx.fillStyle = '#655051';
        ctx.fillRect(7, 16, 17, 1);
      }
      if (level === 3 && type === 'studioLight') {
        ctx.fillStyle = '#42413a';
        ctx.fillRect(11, 9, 9, 6);
      }
    });
  }

  function equipment(level) {
    const age = sprites => Object.fromEntries(Object.entries(sprites).map(([type, source]) =>
      [type, weathered(source, type, level)]));
    const walls = age(wallArt);
    const windows = [walls.window];
    if (level >= 2) {
      for (let variant = 1; variant <= 3; variant++) windows.push(weathered(wallArt.window, 'window', level, variant));
    }
    return {walls, windows, ground: age(groundArt), door: weathered(art.doors[0], 'door', level)};
  }

  return {paving, wall, equipment};
}
