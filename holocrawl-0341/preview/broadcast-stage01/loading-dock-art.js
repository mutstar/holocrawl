function createLoadingDockArt(art, atlas, rects, planes) {
  const floors = new Map();
  const walls = new Map();

  function floorTile(x, y) {
    const variant = Math.floor(StreetGen.random(`dock-tile:${x},${y}`)() * 24);
    if (!floors.has(variant)) floors.set(variant, art.sprite(32, 32, ctx => {
      const random = StreetGen.random(`dock-concrete:${variant}`);
      const image = ctx.createImageData(32, 32);
      const smudgeX = random() * 26 + 3;
      const smudgeY = random() * 26 + 3;
      const slab = variant % 5 - 2;
      for (let py = 0; py < 32; py++) for (let px = 0; px < 32; px++) {
        const distance = Math.abs(px - smudgeX) + Math.abs(py - smudgeY);
        const smudge = Math.max(0, 11 - distance) * (variant % 3 === 0 ? .8 : .4);
        const seam = px === 0 || py === 0 ? -9 : py === 1 ? 2 : 0;
        const tone = slab + Math.floor(random() * 7) - 3 + seam - smudge;
        image.data.set([76 + tone, 73 + tone, 68 + tone, 255], (py * 32 + px) * 4);
      }
      ctx.putImageData(image, 0, 0);
      if (variant % 6 === 0) {
        ctx.fillStyle = '#56504a';
        ctx.fillRect(7, 23, 8, 1);
        ctx.fillRect(14, 22, 4, 1);
        ctx.fillRect(17, 21, 3, 1);
      }
    }));
    return floors.get(variant);
  }

  function wallTile(mask, x, y) {
    const variant = (x * 11 + y * 7) % 5;
    const key = mask * 5 + variant;
    if (!walls.has(key)) walls.set(key, art.sprite(32, 32, ctx => {
      ctx.drawImage(atlas, ...rects[`${mask}:0`], 0, 0, 32, 32);
      const image = ctx.getImageData(0, 0, 32, 32);
      const front = planes[String(mask)];
      for (let i = 0; i < 1024; i++) {
        const offset = 4 * i;
        if (!image.data[offset + 3]) continue;
        const original = image.data[offset + 1];
        const row = Math.floor(i / 32);
        const rail = row === 20 ? 12 : row > 20 ? -19 : 0;
        const tone = front[i] === '1' ? 64 + original * .34 + rail + variant : 9 + original * .47;
        image.data.set(front[i] === '1' && row > 20
          ? [tone - 8, tone, tone + 2] : [tone + 4, tone, tone - 5], offset);
      }
      ctx.putImageData(image, 0, 0);
    }));
    return walls.get(key);
  }

  function prop(width, height, draw) {
    return art.sprite(width, height, ctx => {
      const paint = (color, x, y, w, h) => {ctx.fillStyle = color; ctx.fillRect(x, y, w, h);};
      const caution = (x, y, width) => {
        paint('#292825', x, y, width, 3);
        for (let dx = 0; dx <= width - 5; dx += 9) {
          paint('#a88a50', x + dx, y, 5, 1);
          paint('#8d7345', x + dx + 1, y + 1, 5, 1);
        }
      };
      draw(paint, caution);
    });
  }

  const freightLift = prop(160, 64, (p, caution) => {
    p('#282a2b', 3, 9, 154, 48);
    p('#61635f', 6, 8, 148, 39);
    p('#929083', 7, 8, 146, 2);
    p('#1d2226', 16, 15, 128, 35);
    p('#303940', 23, 19, 114, 25);
    for (const x of [10, 142]) {
      p('#545854', x, 13, 8, 37);
      p('#9a998e', x, 14, 2, 33);
    }
    for (const x of [28, 123]) {
      p('#66716e', x, 24, 5, 27);
      p('#a09b86', x + 1, 24, 1, 27);
    }
    p('#4d5458', 43, 21, 74, 7);
    p('#22282b', 43, 28, 74, 2);
    for (const x of [46, 109]) for (let y = 28; y < 44; y += 3) p('#858679', x, y, 2, 2);
    p('#383d3d', 18, 42, 124, 13);
    for (let y = 44; y < 54; y += 3) p('#4d5653', 21, y, 118, 1);
    caution(9, 54, 142);
    p('#313639', 147, 21, 9, 13);
    p('#93a68b', 150, 23, 3, 2);
    p('#a46350', 150, 28, 3, 2);
  });

  const warehouseShutter = prop(128, 48, (p, caution) => {
    p('#242728', 3, 7, 122, 39);
    p('#535856', 6, 7, 116, 32);
    p('#7a8079', 6, 7, 116, 2);
    p('#343d42', 14, 15, 100, 24);
    for (let y = 17; y < 38; y += 4) {
      p('#252e32', 15, y, 98, 1);
      p('#596269', 15, y + 1, 98, 1);
    }
    for (const x of [8, 114]) {
      p('#414645', x, 12, 6, 28);
      p('#77776e', x + 1, 12, 1, 28);
    }
    p('#242529', 48, 10, 32, 7);
    p('#513837', 50, 11, 28, 4);
    p('#b2755f', 59, 12, 10, 2);
    p('#515451', 57, 30, 14, 7);
    p('#25292a', 60, 32, 8, 2);
    caution(9, 39, 110);
  });

  const hoistControls = prop(96, 32, p => {
    p('#2b2b29', 9, 14, 79, 8);
    p('#797360', 10, 15, 76, 2);
    for (const x of [12, 73]) p('#545651', x, 14, 3, 8);
    p('#262a2b', 34, 7, 30, 23);
    p('#545c60', 36, 8, 26, 19);
    p('#89918b', 36, 8, 26, 1);
    p('#252b2c', 39, 11, 12, 6);
    p('#9eaf87', 41, 13, 7, 2);
    p('#573d31', 54, 11, 6, 6);
    p('#d18b70', 55, 12, 4, 4);
    for (const x of [40, 46, 52]) p('#a8a38d', x, 21, 3, 2);
  });

  const wallBumpers = prop(96, 32, (p, caution) => {
    p('#252a2a', 6, 14, 84, 17);
    p('#454948', 8, 15, 80, 13);
    p('#676c63', 9, 15, 78, 1);
    for (const x of [11, 44, 77]) {
      p('#303434', x, 13, 8, 17);
      caution(x + 1, 19, 6);
      p('#8e8c7a', x + 3, 14, 2, 1);
    }
  });

  const rails = prop(128, 64, p => {
    for (const y of [14, 45]) {
      p('#49423a', 0, y - 3, 128, 10);
      p('#272b2c', 0, y, 128, 4);
      p('#7b7e72', 0, y, 128, 1);
      p('#565b56', 0, y + 2, 128, 1);
      for (let x = 5; x < 128; x += 16) {
        p('#626057', x, y - 3, 4, 2);
        p('#626057', x, y + 4, 4, 2);
      }
    }
  });

  const stagingMark = prop(96, 64, p => {
    for (const x of [7, 72]) for (const y of [7, 54]) {
      p('#a18a53', x, y, 17, 3);
      p('#8d784c', x + (x === 7 ? 0 : 14), y === 7 ? y : y - 12, 3, 15);
      p('#605744', x + 5, y + 1, 3, 1);
      p('#605744', x + 11, y + 2, 2, 1);
    }
  });

  const sceneryPallet = prop(96, 64, p => {
    p('#322d27', 10, 56, 78, 4);
    p('#4e3e30', 11, 42, 75, 9);
    for (let x = 13; x < 83; x += 10) {
      p('#96764e', x, 42, 8, 8);
      p('#a5875e', x, 44, 8, 1);
      p('#765d42', x + 1, 47, 4, 1);
    }
    for (const x of [13, 43, 73]) {
      p('#4e3c2d', x, 51, 10, 7);
      p('#76593b', x + 1, 52, 7, 5);
    }
    p('#73573c', 11, 50, 75, 4);
    p('#9a7a50', 12, 50, 73, 1);
    p('#49382c', 12, 57, 73, 2);

    // Painted stage flats, with wooden legs resting on the deck.
    p('#493c32', 22, 14, 41, 34);
    p('#63767b', 24, 14, 37, 29);
    p('#7b8b8b', 25, 14, 35, 1);
    p('#9bada8', 29, 23, 17, 3);
    p('#9bada8', 33, 21, 9, 2);
    p('#4f6669', 25, 34, 35, 9);
    p('#594a3a', 24, 43, 4, 5);
    p('#594a3a', 56, 43, 4, 5);

    p('#4b3b31', 43, 25, 34, 25);
    p('#96785b', 43, 25, 33, 20);
    p('#a98b69', 44, 25, 31, 1);
    p('#6d5747', 52, 33, 16, 12);
    p('#6d5747', 55, 30, 10, 4);
    p('#3d3b3b', 55, 34, 10, 11);
    p('#3d3b3b', 57, 32, 6, 2);
    p('#634b36', 44, 44, 4, 6);
    p('#634b36', 72, 44, 4, 6);
    p('#473b31', 18, 44, 7, 3);
  });

  const cargoCrate = prop(64, 32, p => {
    p('#342d26', 3, 24, 59, 6);
    p('#55432f', 5, 7, 53, 20);
    p('#8c7250', 6, 4, 51, 11);
    p('#a68a62', 7, 4, 49, 1);
    p('#6c553c', 8, 15, 46, 9);
    for (const x of [7, 52]) p('#9c7b54', x, 13, 4, 12);
    for (const x of [18, 43]) {
      p('#666a5c', x, 5, 3, 11);
      p('#434744', x, 15, 3, 11);
      p('#a59a78', x, 17, 3, 2);
    }
    p('#bab099', 27, 17, 10, 5);
    p('#6e695c', 29, 18, 6, 1);
  });

  const forklift = prop(64, 32, p => {
    p('#302c28', 4, 26, 57, 4);
    p('#282b2c', 5, 18, 21, 4);
    p('#949689', 5, 18, 21, 1);
    p('#25282a', 2, 24, 24, 3);
    p('#888f86', 2, 24, 24, 1);
    p('#252c31', 23, 5, 7, 23);
    p('#818983', 24, 5, 2, 22);
    p('#424749', 28, 12, 2, 14);
    p('#694d2e', 29, 15, 31, 12);
    p('#a47b40', 31, 14, 28, 8);
    p('#c29a58', 47, 14, 11, 3);
    p('#504c45', 35, 11, 13, 6);
    p('#252a2f', 36, 10, 8, 7);
    p('#252b30', 33, 3, 17, 2);
    p('#6d736e', 34, 3, 15, 1);
    p('#383e40', 33, 5, 2, 13);
    p('#383e40', 48, 5, 2, 10);
    p('#c29452', 47, 1, 3, 3);
    for (const [x, width] of [[28, 12], [50, 9]]) {
      p('#23272a', x, 22, width, 7);
      p('#23272a', x + 1, 21, width - 2, 9);
      p('#474b4a', x + 3, 23, width - 6, 4);
    }
  });

  const railsTowardLift = art.sprite(64, 128, ctx => {
    ctx.translate(64, 0);
    ctx.rotate(Math.PI / 2);
    ctx.drawImage(rails, 0, 0);
  });

  const warehouseOpening = prop(96, 32, (p, caution) => {
    p('#393b39', 0, 21, 96, 5);
    p('#68685c', 0, 20, 96, 2);
    p('#424843', 0, 23, 96, 2);
    caution(0, 19, 12);
    caution(84, 19, 12);
  });

  const inspectionWindow = prop(96, 32, p => {
    p('#242728', 5, 7, 86, 24);
    p('#686d66', 6, 7, 84, 21);
    p('#9b9a88', 7, 7, 82, 1);
    p('#242f34', 10, 10, 76, 15);
    p('#3f5053', 12, 11, 46, 9);
    p('#677c7d', 13, 11, 44, 1);
    p('#303e42', 37, 11, 2, 9);
    p('#758985', 16, 14, 17, 1);
    p('#567071', 14, 15, 9, 1);

    p('#363632', 17, 19, 25, 7);
    p('#75766b', 17, 20, 25, 1);
    p('#b6af96', 21, 19, 15, 4);
    p('#d2c5a5', 24, 18, 12, 3);
    for (const x of [26, 29, 31]) p('#7b7867', x, 19, 1, 2);

    p('#374247', 64, 15, 13, 5);
    p('#829093', 64, 15, 12, 1);
    p('#a46a54', 63, 17, 3, 2);
    p('#5d6969', 69, 19, 3, 5);
    p('#303638', 65, 23, 12, 2);
    p('#272d2e', 77, 10, 7, 5);
    p('#91a784', 79, 11, 3, 2);
    p('#7e7b6c', 7, 25, 82, 3);
    p('#a39a85', 7, 25, 82, 1);
    p('#454643', 8, 28, 80, 2);
  });

  const forkliftCharger = prop(64, 32, p => {
    p('#292d2f', 8, 7, 25, 23);
    p('#58615d', 9, 7, 23, 19);
    p('#8a9385', 10, 7, 21, 1);
    p('#283336', 13, 10, 14, 6);
    p('#8aa986', 15, 12, 7, 2);
    p('#4b524b', 12, 19, 17, 5);
    p('#7f8574', 13, 19, 15, 1);
    p('#b59a61', 15, 21, 5, 1);
    p('#2d3535', 38, 9, 13, 3);
    p('#7c8376', 39, 9, 11, 1);

    // Two offset runs leave a hole in the middle of the hanging cable coil.
    p('#222729', 28, 22, 12, 3);
    p('#1a2023', 35, 15, 4, 10);
    p('#1a2023', 39, 12, 13, 3);
    p('#1a2023', 50, 15, 4, 11);
    p('#1a2023', 39, 25, 13, 3);
    p('#58615f', 39, 12, 12, 1);
    p('#535b59', 35, 16, 1, 7);
    p('#59615f', 50, 15, 1, 8);
    p('#444a47', 40, 25, 10, 1);
    p('#26292a', 48, 20, 11, 4);
    p('#b68352', 53, 19, 7, 5);
    p('#d8a36a', 54, 19, 5, 1);
    p('#72756e', 59, 20, 2, 3);
  });

  const strapRack = prop(96, 32, p => {
    p('#2a2e2d', 13, 8, 70, 9);
    p('#626960', 14, 8, 68, 6);
    p('#9a998b', 15, 8, 66, 1);
    for (const [x, length] of [[23, 11], [43, 15], [64, 9]]) {
      p('#333633', x, 10, 9, length + 4);
      p('#94774d', x + 1, 11, 6, length);
      p('#bb9a60', x + 2, 12, 2, length - 2);
      p('#5a4e3c', x + 2, 15, 5, 2);
      p('#8f9890', x + 2, 10 + length, 5, 4);
      p('#4b5553', x + 3, 11 + length, 3, 2);
    }
  });

  const palletScale = prop(64, 64, (p, caution) => {
    p('#36342e', 8, 13, 48, 38);
    p('#525753', 10, 14, 44, 34);
    p('#818479', 12, 15, 40, 2);
    p('#656a62', 12, 18, 40, 27);
    for (const y of [21, 27, 33, 39]) {
      for (let x = 16; x < 50; x += 7) p('#85867a', x + (y % 2) * 2, y, 3, 1);
    }
    p('#414b48', 12, 44, 40, 3);
    caution(14, 44, 36);
    p('#273032', 24, 8, 16, 7);
    p('#56605b', 25, 8, 14, 6);
    p('#252f31', 27, 9, 10, 4);
    p('#9cba95', 29, 10, 6, 1);
  });

  return {
    floorTile, wallTile, freightLift, warehouseShutter, hoistControls, wallBumpers,
    railsTowardLift, stagingMark, sceneryPallet, cargoCrate, forklift, warehouseOpening, inspectionWindow, forkliftCharger,
    strapRack, palletScale,
  };
}
