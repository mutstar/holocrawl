const TheaterCinema = {
  source: '../theater-vault36/',

  drawWalls(context, origin, vault) {
    const wallAt = (x, y) => vault.rows[y]?.[x] === '#';
    for (let y = 0; y < vault.height; y++) {
      for (let x = 0; x < vault.width; x++) {
        if (!wallAt(x, y)) continue;
        const left = (origin.x + x) * 32;
        const top = (origin.y + y) * 32;
        const paint = (color, dx, dy, width, height) => {
          context.fillStyle = color;
          context.fillRect(left + dx, top + dy, width, height);
        };
        paint('#302228', 0, 0, 32, 32);
        paint('#412c33', 2, 2, 28, 28);
        if (!wallAt(x, y - 1)) {
          paint('#241a20', 0, 0, 32, 1);
          paint('#85674d', 0, 1, 32, 1);
        }
        if (!wallAt(x - 1, y)) paint('#6f5543', 1, 2, 1, 28);
        if (!wallAt(x + 1, y)) paint('#6f5543', 30, 2, 1, 28);

        if (!wallAt(x, y + 1)) {
          // Horizontal brass rails join across neighboring tiles.
          paint('#a28159', 0, 12, 32, 1);
          paint('#4c3431', 0, 13, 32, 2);
          paint('#4c2935', 0, 15, 32, 14);
          paint('#652f41', 4, 17, 24, 9);
          paint('#7e4652', 4, 17, 24, 1);
          paint('#42252f', 4, 25, 24, 1);
          paint('#957551', 0, 29, 32, 1);
          paint('#1c171c', 0, 31, 32, 1);
        } else {
          const side = x === 0 ? 27 : 0;
          paint('#542c38', side, 0, 5, 32);
          paint('#a18058', side + (x === 0 ? 3 : 1), 0, 1, 32);
        }
      }
    }
  },

  drawEntrance(context, origin, vault, terrain, isOpen) {
    const [leftDoor, rightDoor] = vault.connectors;
    const x = (origin.x + leftDoor.x) * 32;
    const y = (origin.y + leftDoor.y) * 32;
    const paint = (color, dx, dy, width, height) => {
      context.fillStyle = color;
      context.fillRect(x + dx, y + dy, width, height);
    };
    for (const [index, door] of [leftDoor, rightDoor].entries()) {
      const dx = index * 32;
      if (isOpen(origin.x + door.x, origin.y + door.y)) {
        context.drawImage(terrain, x + dx, y - 32, 32, 32, x + dx, y, 32, 32);
        paint('#422833', dx + (index ? 28 : 0), 8, 4, 22);
      } else {
        paint('#25181f', dx, 8, 32, 24);
        paint('#59303c', dx + 2, 9, 28, 20);
        paint('#a27a53', dx + 3, 10, 26, 1);
        paint('#824a51', dx + 6, 12, 20, 6);
        paint('#6b373f', dx + 6, 20, 20, 6);
        paint('#ba985f', dx + (index ? 6 : 24), 19, 2, 4);
      }
      paint('#9c7954', dx, 30, 32, 1);
      paint('#493635', dx, 31, 32, 1);
    }

    paint('#2a1a24', -4, 0, 72, 8);
    paint('#ac8a60', -4, 0, 72, 1);
    paint('#956647', -4, 7, 72, 1);
    paint('#d4aa6b', 1, 3, 2, 2);
    paint('#d4aa6b', 61, 3, 2, 2);
    const glyphs = {
      H: ['101', '101', '111', '101', '101'], O: ['111', '101', '101', '101', '111'],
      L: ['100', '100', '100', '100', '111'], C: ['111', '100', '100', '100', '111'],
      I: ['111', '010', '010', '010', '111'], N: ['101', '111', '111', '111', '101'],
      E: ['111', '100', '110', '100', '111'], M: ['101', '111', '101', '101', '101'],
      A: ['010', '101', '111', '101', '101'], S: ['111', '100', '111', '001', '111'],
    };
    [...'HOLO CINEMAS'].forEach((letter, index) => {
      glyphs[letter]?.forEach((row, dy) => {
        [...row].forEach((pixel, dx) => {
          if (pixel === '1') paint('#edc88b', 8 + index * 4 + dx, 2 + dy, 1, 1);
        });
      });
    });
  },
};

window.theaterTheme = TheaterCinema;
