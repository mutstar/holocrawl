function createBroadcastPropArt(sprite) {
  const ink = '#22282b';
  const steel = '#52636a';
  const edge = '#89979a';
  const dark = '#353f45';
  const glass = '#4b717a';
  const red = '#c47868';
  const tape = '#b19a65';
  const rect = (ctx, color, x, y, width, height) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
  };

  function wallSpeaker(ctx) {
    rect(ctx, ink, 10, 7, 13, 17);
    rect(ctx, steel, 11, 8, 11, 15);
    rect(ctx, dark, 12, 11, 9, 10);
    rect(ctx, edge, 12, 8, 9, 1);
    for (let y = 12; y < 21; y += 2) rect(ctx, '#6a7779', 13, y, 7, 1);
    rect(ctx, red, 19, 9, 2, 1);
  }

  function signalBox(ctx) {
    rect(ctx, ink, 8, 9, 17, 15);
    rect(ctx, steel, 9, 10, 15, 12);
    rect(ctx, edge, 10, 10, 13, 1);
    rect(ctx, ink, 11, 12, 10, 4);
    rect(ctx, glass, 12, 13, 3, 2);
    rect(ctx, red, 18, 13, 2, 2);
    rect(ctx, dark, 13, 19, 6, 1);
    rect(ctx, dark, 11, 24, 2, 4);
    rect(ctx, dark, 20, 24, 2, 4);
  }

  function securityCamera(ctx) {
    rect(ctx, ink, 5, 9, 6, 13);
    rect(ctx, steel, 6, 10, 3, 11);
    rect(ctx, dark, 9, 13, 8, 4);
    rect(ctx, ink, 13, 9, 12, 8);
    rect(ctx, edge, 14, 10, 9, 2);
    rect(ctx, steel, 14, 12, 9, 4);
    rect(ctx, ink, 23, 12, 4, 6);
    rect(ctx, glass, 25, 13, 2, 4);
    rect(ctx, red, 16, 13, 1, 1);
  }

  function stationEmblem(ctx) {
    rect(ctx, ink, 8, 6, 16, 19);
    rect(ctx, '#42636b', 9, 7, 14, 16);
    rect(ctx, edge, 9, 7, 14, 1);
    rect(ctx, '#93b9b7', 15, 12, 2, 8);
    for (const [x, y, width] of [[13,10,6],[12,12,1],[19,12,1],[11,9,1],[20,9,1],[10,11,1],[21,11,1],[14,20,4]]) {
      rect(ctx, '#93b9b7', x, y, width, 1);
    }
  }

  function scheduleBoard(ctx) {
    rect(ctx, ink, 5, 8, 22, 17);
    rect(ctx, '#657475', 6, 9, 20, 14);
    rect(ctx, '#283d43', 7, 10, 18, 11);
    for (const [y, color, width] of [[12, red, 8], [15, '#7d9d9c', 11], [18, tape, 6]]) {
      rect(ctx, color, 9, y, 2, 1);
      rect(ctx, color, 13, y, width, 1);
    }
  }

  function noiseScreen(floor) {
    const heavy = floor === 14;
    return sprite(64, 32, ctx => {
      rect(ctx, ink, 4, 6, 56, 21);
      rect(ctx, steel, 5, 7, 54, 17);
      rect(ctx, edge, 7, 7, 50, 1);
      rect(ctx, dark, 6, 24, 52, 2);
      rect(ctx, '#222e35', 8, 9, 48, 13);
      const random = StreetGen.random('broadcast-noise-screen:' + floor);
      const colors = ['#344952', '#4e606a', '#6c7c82', '#a4b1ac'];
      for (let y = 10; y < 21; y++) {
        for (let x = 9; x < 55; x++) {
          if (random() < (heavy ? .76 : .41)) {
            const tone = Math.floor(random() * colors.length);
            rect(ctx, colors[tone], x, y, 1, 1);
          }
        }
      }
      const bands = heavy
        ? [[10, 11, 35, '#465262'], [21, 14, 34, '#748088'], [9, 17, 45, '#202a30'], [28, 19, 25, '#776471']]
        : [[11, 12, 39, '#66828a'], [21, 16, 32, '#9baaa8'], [9, 19, 20, '#536e77']];
      for (const [x, y, width, color] of bands) rect(ctx, color, x, y, width, 1);
      rect(ctx, heavy ? red : '#83a39c', 51, 24, 3, 1);
    });
  }

  function programPoster(ctx) {
    rect(ctx, ink, 9, 6, 15, 21);
    rect(ctx, '#7b626c', 10, 7, 13, 18);
    rect(ctx, '#a47e82', 10, 7, 13, 3);
    rect(ctx, '#4d4c60', 12, 12, 9, 8);
    rect(ctx, '#c2a78d', 16, 12, 3, 5);
    rect(ctx, '#c2a78d', 15, 17, 3, 1);
    rect(ctx, '#bda69d', 12, 22, 9, 1);
    rect(ctx, '#615963', 22, 23, 1, 2);
  }

  function conduit(ctx) {
    rect(ctx, ink, 2, 12, 28, 9);
    rect(ctx, '#777a72', 3, 13, 26, 2);
    rect(ctx, steel, 3, 17, 26, 2);
    for (const x of [4, 24]) {
      rect(ctx, dark, x, 11, 4, 11);
      rect(ctx, edge, x + 1, 12, 2, 7);
    }
    rect(ctx, tape, 18, 13, 3, 1);
  }

  function van(ctx) {
    rect(ctx, '#282e30', 4, 46, 88, 12);
    rect(ctx, ink, 3, 29, 88, 22);
    rect(ctx, ink, 8, 19, 68, 13);
    rect(ctx, ink, 72, 23, 15, 9);
    rect(ctx, '#747e7d', 9, 21, 63, 24);
    rect(ctx, '#939995', 10, 21, 61, 5);
    rect(ctx, '#c0c0af', 11, 21, 58, 1);
    rect(ctx, '#7d8a89', 72, 25, 11, 22);
    rect(ctx, '#7d8a89', 82, 31, 7, 16);
    rect(ctx, ink, 74, 27, 8, 9);
    rect(ctx, glass, 75, 28, 6, 7);
    rect(ctx, glass, 83, 32, 4, 4);
    rect(ctx, '#4d6c77', 7, 38, 82, 5);
    rect(ctx, '#809295', 8, 38, 65, 1);
    rect(ctx, dark, 46, 27, 21, 11);
    rect(ctx, '#9ca39a', 47, 27, 18, 1);
    for (let y = 30; y <= 35; y += 2) rect(ctx, steel, 49, y, 14, 1);
    rect(ctx, red, 5, 40, 4, 3);
    rect(ctx, '#d5c995', 86, 42, 4, 2);
    for (const x of [16, 72]) {
      rect(ctx, ink, x, 45, 12, 9);
      rect(ctx, '#171b1d', x + 2, 47, 8, 8);
      rect(ctx, '#616a6b', x + 4, 48, 4, 4);
    }
    rect(ctx, dark, 34, 17, 15, 4);
    rect(ctx, steel, 40, 10, 3, 8);
    rect(ctx, dark, 34, 8, 11, 4);
    rect(ctx, edge, 33, 6, 10, 3);
    rect(ctx, '#a8aaa0', 32, 5, 7, 1);
    rect(ctx, edge, 42, 4, 2, 2);
  }

  function camera(ctx) {
    rect(ctx, ink, 15, 15, 3, 13);
    rect(ctx, steel, 16, 16, 1, 12);
    for (let step = 0; step < 7; step++) {
      rect(ctx, ink, 14 - step, 19 + step, 3, 2);
      rect(ctx, ink, 18 + step, 19 + step, 2, 2);
      rect(ctx, steel, 15 - step, 19 + step, 1, 1);
      rect(ctx, steel, 18 + step, 19 + step, 1, 1);
    }
    rect(ctx, ink, 8, 7, 15, 10);
    rect(ctx, steel, 9, 8, 12, 8);
    rect(ctx, edge, 10, 8, 10, 1);
    rect(ctx, ink, 20, 9, 7, 6);
    rect(ctx, glass, 24, 10, 2, 4);
    rect(ctx, ink, 12, 5, 8, 2);
    rect(ctx, red, 10, 10, 2, 2);
  }

  function monitor(ctx, x, y, broken) {
    rect(ctx, ink, x, y, 17, 13);
    rect(ctx, steel, x + 1, y + 1, 15, 11);
    rect(ctx, '#26383e', x + 3, y + 3, 10, 7);
    rect(ctx, broken ? '#7a6479' : glass, x + 4, y + 4, 8, 5);
    if (broken) {
      rect(ctx, '#b598ac', x + 9, y + 4, 1, 2);
      rect(ctx, '#342f3a', x + 8, y + 6, 1, 1);
      rect(ctx, '#342f3a', x + 7, y + 7, 1, 2);
    } else {
      rect(ctx, '#83aaa3', x + 5, y + 6, 6, 1);
      rect(ctx, '#6e938b', x + 5, y + 8, 4, 1);
    }
    rect(ctx, red, x + 14, y + 8, 1, 1);
  }

  function monitorRack(ctx) {
    rect(ctx, ink, 6, 7, 22, 22);
    rect(ctx, dark, 7, 8, 20, 18);
    monitor(ctx, 8, 15, false);
    monitor(ctx, 7, 4, true);
    rect(ctx, edge, 7, 28, 2, 2);
    rect(ctx, edge, 25, 28, 2, 2);
  }

  function equipmentCases(ctx) {
    function box(x, y, width, height) {
      rect(ctx, ink, x, y, width, height);
      rect(ctx, steel, x + 1, y + 1, width - 2, height - 2);
      rect(ctx, dark, x + 2, y + 4, width - 4, height - 6);
      rect(ctx, edge, x + 2, y + 1, width - 4, 1);
      rect(ctx, edge, x + 2, y + height - 3, 2, 2);
      rect(ctx, edge, x + width - 4, y + height - 3, 2, 2);
      rect(ctx, tape, x + width - 6, y + 5, 3, 2);
      rect(ctx, '#818c8e', x + 4, y + 6, 4, 1);
    }
    box(8, 14, 22, 13);
    box(3, 7, 20, 12);
  }

  function cable(ctx) {
    const rows = [
      '..........########......',
      '........###......###....',
      '.......##..######..##...',
      '.......#..##....##..#...',
      '.......#..#..##..#..#...',
      '.......#..##.###.#..#...',
      '........#..####.##.##...',
      '........##......#.##....',
      '.###......###..###......',
      '.#.##.......####........',
      '##..##########..........',
    ];
    rows.forEach((row, y) => Array.from(row).forEach((pixel, x) => {
      if (pixel === '#') rect(ctx, ink, x + 4, y + 12, 1, 2);
    }));
    rows.forEach((row, y) => Array.from(row).forEach((pixel, x) => {
      if (pixel === '#') rect(ctx, '#697476', x + 4, y + 12, 1, 1);
    }));
    rect(ctx, tape, 4, 22, 3, 2);
  }

  function studioLight(ctx) {
    rect(ctx, ink, 15, 15, 3, 14);
    rect(ctx, steel, 16, 16, 1, 12);
    rect(ctx, ink, 11, 26, 11, 3);
    rect(ctx, steel, 12, 26, 8, 1);
    rect(ctx, ink, 9, 7, 15, 11);
    rect(ctx, steel, 10, 8, 13, 8);
    rect(ctx, '#9d9271', 11, 9, 9, 6);
    rect(ctx, '#dbc99b', 12, 9, 7, 1);
    rect(ctx, dark, 7, 7, 3, 8);
    rect(ctx, dark, 23, 6, 3, 9);
  }

  function equipmentCart(ctx) {
    rect(ctx, ink, 5, 10, 24, 16);
    rect(ctx, steel, 6, 11, 2, 13);
    rect(ctx, dark, 8, 19, 20, 6);
    rect(ctx, edge, 8, 20, 19, 1);
    rect(ctx, '#777663', 10, 14, 9, 5);
    rect(ctx, '#a39c7a', 10, 13, 9, 1);
    rect(ctx, '#596968', 20, 16, 6, 3);
    for (const x of [9, 23]) {
      rect(ctx, ink, x, 25, 4, 4);
      rect(ctx, '#758084', x + 1, 26, 2, 2);
    }
  }

  function satelliteDish(ctx) {
    rect(ctx, ink, 8, 25, 17, 5);
    rect(ctx, steel, 9, 25, 15, 2);
    rect(ctx, dark, 14, 17, 6, 8);
    rect(ctx, edge, 15, 18, 2, 7);
    for (const [y, x, width] of [[8,7,4],[9,7,6],[10,8,8],[11,8,10],[12,9,11],[13,10,12],[14,11,13],[15,12,13],[16,13,12],[17,15,11],[18,17,8]]) {
      rect(ctx, ink, x, y, width + 1, 2);
      rect(ctx, y < 15 ? '#a3a9a1' : '#687779', x, y, width, 1);
    }
    rect(ctx, dark, 19, 11, 3, 2);
    rect(ctx, steel, 21, 8, 2, 4);
    rect(ctx, edge, 21, 7, 5, 2);
  }

  function clapperboard(ctx) {
    rect(ctx, ink, 7, 15, 18, 12);
    rect(ctx, dark, 8, 16, 16, 9);
    rect(ctx, '#6d7b7b', 10, 19, 12, 1);
    rect(ctx, '#6d7b7b', 10, 22, 8, 1);
    for (let i = 0; i < 6; i++) {
      rect(ctx, ink, 7 + i * 3, 14 - i, 3, 3);
      if (i % 2 === 0) rect(ctx, '#b3afa1', 7 + i * 3, 14 - i, 2, 2);
    }
    rect(ctx, red, 8, 16, 1, 1);
  }

  function queueBarrier(ctx) {
    for (const x of [11, 49]) {
      rect(ctx, ink, x - 4, 25, 10, 3);
      rect(ctx, ink, x, 9, 3, 17);
      rect(ctx, edge, x + 1, 10, 1, 14);
      rect(ctx, steel, x - 1, 8, 5, 2);
    }
    rect(ctx, '#542f36', 14, 11, 35, 3);
    rect(ctx, '#9c615e', 14, 11, 35, 1);
    rect(ctx, tape, 28, 11, 8, 2);
  }

  return {
    noiseScreen,
    wall: {
      speaker: sprite(32, 32, wallSpeaker),
      signalBox: sprite(32, 32, signalBox),
      securityCamera: sprite(32, 32, securityCamera),
      stationEmblem: sprite(32, 32, stationEmblem),
      scheduleBoard: sprite(32, 32, scheduleBoard),
      programPoster: sprite(32, 32, programPoster),
      conduit: sprite(32, 32, conduit),
    },
    ground: {
      van: sprite(96, 64, van),
      camera: sprite(32, 32, camera),
      monitorRack: sprite(32, 32, monitorRack),
      equipmentCases: sprite(32, 32, equipmentCases),
      cable: sprite(32, 32, cable),
      studioLight: sprite(32, 32, studioLight),
      equipmentCart: sprite(32, 32, equipmentCart),
      satelliteDish: sprite(32, 32, satelliteDish),
      clapperboard: sprite(32, 32, clapperboard),
      queueBarrier: sprite(64, 32, queueBarrier),
    },
  };
}
