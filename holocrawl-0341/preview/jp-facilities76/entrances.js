(() => {
  function posts(paint, dark, face, edge) {
    for (const x of [24, 64]) {
      paint(dark, x, 10, 8, 21);
      paint(face, x + 1, 12, 6, 16);
      paint(edge, x + 1, 13, 2, 14);
      paint(dark, x - 1, 28, 10, 3);
    }
  }

  function lantern(paint, x, color, light) {
    paint('#3a3030', x, 15, 8, 10);
    paint(color, x + 1, 16, 6, 6);
    paint(light, x + 2, 17, 4, 3);
    paint('#6a4e41', x + 2, 23, 4, 2);
  }

  const fronts = {
    wheel(paint) {
      posts(paint, '#3c323e', '#715a6f', '#ac819b');
      paint('#3b303a', 9, 9, 78, 8);
      paint('#67485e', 11, 10, 74, 5);
      paint('#a77589', 13, 10, 70);
      paint('#433542', 32, 4, 32, 9);
      paint('#78576e', 35, 2, 26, 11);
      paint('#a68288', 39, 1, 18, 2);
      paint('#d9b27b', 44, 4, 8);
      paint('#d9b27b', 43, 5, 1, 6);
      paint('#d9b27b', 52, 5, 1, 6);
      paint('#d9b27b', 45, 11, 6);
      paint('#e4c18b', 47, 6, 2, 3);
      paint('#c09384', 46, 9, 4);
      for (const x of [14, 20, 26, 33, 39, 55, 61, 68, 74, 80]) {
        paint('#d2a26f', x, 13, 2, 2);
      }
      lantern(paint, 16, '#af8061', '#e5c191');
      lantern(paint, 72, '#af8061', '#e5c191');
    },

    mountain(paint) {
      for (const x of [15, 64]) {
        paint('#3b3d34', x + 1, 11, 16, 18);
        paint('#635f4d', x, 17, 17, 10);
        paint('#827862', x + 2, 12, 14, 9);
        paint('#9b8e72', x + 4, 12, 10, 2);
        paint('#4c4a3c', x - 3, 27, 22, 4);
        paint('#79705a', x - 2, 25, 20, 3);
        paint('#727956', x + 2, 19, 6, 2);
        paint('#687252', x + 10, 26, 7, 2);
      }
      paint('#45392e', 20, 7, 56, 8);
      paint('#785d42', 21, 7, 54, 5);
      paint('#aa8960', 23, 7, 50, 2);
      paint('#574333', 28, 11, 39, 2);
      paint('#554737', 39, 4, 18, 9);
      paint('#a18156', 41, 4, 14, 6);
      paint('#d2b584', 44, 6, 8);
      lantern(paint, 21, '#a98962', '#dbc499');
      lantern(paint, 67, '#a98962', '#dbc499');
    },

    dining(paint) {
      posts(paint, '#482f2a', '#835849', '#b38467');
      paint('#492c29', 9, 8, 78, 7);
      paint('#874739', 13, 6, 70, 7);
      paint('#b06b51', 20, 4, 56, 3);
      paint('#c89b72', 10, 12, 76);
      for (const x of [27, 38, 49, 60]) {
        paint('#693639', x, 15, 10, 5);
        paint('#a35f53', x + 1, 15, 8, 4);
        paint('#c59173', x + 2, 19, 6);
      }
      paint('#533632', 40, 4, 16, 10);
      paint('#d1aa7c', 43, 9, 10);
      paint('#c08d69', 45, 10, 6, 2);
      paint('#d8b58e', 46, 6, 1, 2);
      paint('#d8b58e', 49, 5, 1, 3);
      lantern(paint, 14, '#b96757', '#f1c28f');
      lantern(paint, 74, '#b96757', '#f1c28f');
    },

    market(paint) {
      posts(paint, '#304640', '#5d8170', '#9eb39c');
      paint('#334741', 15, 4, 66, 14);
      paint('#4e7364', 21, 4, 54, 7);
      paint('#7d9a7e', 22, 4, 52);
      for (const [x, color] of [[38, '#8bb4ca'], [44, '#d7a763'], [50, '#aab5a3'], [56, '#bd7f8b']]) {
        paint(color, x, 6, 3, 3);
      }
      for (let x = 12; x < 84; x += 6) {
        const pale = (x - 12) % 12 === 0;
        paint(pale ? '#bdb59b' : '#779181', x, 11, 6, 6);
        paint(pale ? '#a29b82' : '#5e776b', x, 17, 6, 2);
      }
      for (const x of [12, 73]) {
        paint('#355249', x, 21, 11, 6);
        paint('#8caa9b', x + 1, 21, 9);
        paint('#6d9385', x + 2, 23, 7, 2);
      }
    },

    dev(paint) {
      posts(paint, '#34303e', '#625570', '#aa84ad');
      paint('#393242', 10, 9, 76, 8);
      paint('#5e4a68', 14, 6, 68, 8);
      paint('#987298', 15, 6, 66, 2);
      paint('#2b2534', 28, 3, 40, 12);
      paint('#805f86', 30, 4, 36, 9);
      paint('#352d41', 32, 6, 32, 5);
      for (const [x, color] of [[35, '#a7b3d0'], [41, '#d7af87'], [47, '#bc89a6'], [53, '#8ab3a1'], [59, '#d69aa0']]) {
        paint(color, x, 7, 3, 3);
      }
      for (const x of [13, 75]) {
        paint('#373240', x, 18, 8, 9);
        paint('#997492', x + 1, 18, 6, 2);
        paint('#c590a6', x + 2, 22, 4, 2);
      }
      paint('#a87f9e', 18, 13, 10);
      paint('#a87f9e', 68, 13, 10);
    },
  };

  window.drawFacilityEntrance = (context, rows, theme) => {
    const tile = 32;
    const row = rows.at(-1);
    const opening = row.indexOf('.');
    const left = (opening - 1) * tile;
    const top = (rows.length - 1) * tile;
    const paint = (color, x, y, width, height = 1) => {
      context.fillStyle = color;
      context.fillRect(left + x, top + y, width, height);
    };

    paint('#62574d', 32, 25, 32, 5);
    paint('#9a8b74', 33, 25, 30);
    paint('#746758', 34, 27, 28, 2);
    fronts[theme](paint);
  };
})();
