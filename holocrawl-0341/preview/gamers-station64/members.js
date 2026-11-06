(() => {
  const face = (px, x, y, shape, colors) => {
    for (const [dy, row] of shape.entries()) {
      for (const [dx, color] of [...row].entries()) {
        if (color !== '.') px(colors[color], x + dx, y + dy, 1);
      }
    }
  };
  const roof = (px, outerSide) => {
    const bands = [
      ['#34475e', 3, 8], ['#506a84', 4, 7], ['#34475e', 5, 6],
      ['#293b56', 6, 5], ['#677486', 7, 4], ['#26262a', 8, 4],
      ['#26262a', 9, 5],
    ];
    for (const [color, y, inset] of bands) {
      const left = outerSide === 'left' ? inset : 0;
      const right = outerSide === 'right' ? 32 - inset : 32;
      px(color, left, y, right - left);
    }
  };
  const wall = (px, outerSide) => {
    const courses = [
      // Begin at the height and color of the adjoining station wall.
      [0, 3, 17, '#767467', '#626155'],
      [3, 3, 15, '#817c6b', '#6c675c'],
      [6, 3, 12, '#918777', '#7b7164'],
      [9, 23, 10, '#a09886', '#8d8171'],
    ];
    for (const [offset, width, top, rim, plaster] of courses) {
      const left = outerSide === 'left' ? offset : 32 - offset - width;
      px(rim, left, top, width);
      px(plaster, left, top + 1, width, 25 - top - 1);
    }
    // Run the same base trim through the facade and the adjoining wall.
    px('#729388', 0, 25, 32);
    px('#3d5c55', 0, 26, 32, 3);
    px('#252827', 0, 29, 32, 3);
  };
  const sconce = (px, x) => {
    px('#584f45', x - 1, 11, 7, 7);
    px('#b8a27d', x, 11, 5, 5);
    px('#e9dbac', x + 1, 12, 3, 3);
    px('#f7ead0', x + 2, 12, 1, 2);
    px('#6f604e', x + 1, 16, 3);
  };

  window.gamersStationArt = {
    facade(g, tile) {
      for (const side of [5, 7]) tile(g, side, 8, px => {
        const outerSide = side === 5 ? 'left' : 'right';
        wall(px, outerSide);
        roof(px, outerSide);
        sconce(px, side === 5 ? 23 : 4);
        if (side === 5) {
          // Recessed old station board under the canopy.
          px('#544e47', 8, 14, 13, 11);
          px('#b4a88e', 9, 14, 11);
          px('#434a46', 9, 15, 11, 8);
          px('#778f88', 10, 17, 8);
          px('#b8bb9e', 10, 19, 5);
          px('#a68c61', 16, 21, 2);
        } else {
          // Cyan round window, kept inside the frontage rather than floating.
          face(px, 14, 12, [
            '...####...', '..######..', '.##aaaa##.', '##abbbaa##',
            '#abccbbba#', '#abccbbba#', '#aabbbbba#', '##aabbaa##',
            '.##aaaa##.', '..######..', '...####...',
          ], { '#':'#4a514b', a:'#558b8e', b:'#74b9ba', c:'#bce0d4' });
          px('#777366', 22, 23, 3);
        }
      });
    },

    entry(px, open) {
      roof(px);
      // Rounded stone frame and blue lettering, like the station counter front.
      px('#554d44', 0, 10, 32, 6);
      px('#9e927c', 1, 10, 30, 4);
      px('#bbb098', 5, 10, 22, 2);
      px('#c0b498', 9, 10, 14);
      px('#7c7160', 3, 13, 26, 2);
      for (const x of [0, 30]) {
        px('#8d8171', x, 16, 2, 9);
        px('#729388', x, 25, 2);
        px('#3d5c55', x, 26, 2, 3);
        px('#252827', x, 29, 2, 3);
      }
      px('#5d554b', 1, 15, 5, 15);
      px('#5d554b', 26, 15, 5, 15);
      px('#aa9b80', 2, 15, 2, 13);
      px('#aa9b80', 28, 15, 2, 13);
      px('#252b2b', 5, 15, 2, 14);
      px('#252b2b', 25, 15, 2, 14);
      px('#756e60', 5, 29, 22, 2);
      px('#a1947a', 7, 29, 18);
      px('#506b8c', 8, 11, 4);
      px('#506b8c', 12, 10, 8);
      px('#506b8c', 20, 11, 4);
      px('#6e88a4', 14, 12, 4);
      if (open) return;
      px('#273633', 7, 15, 18, 14);
      for (const x of [8, 17]) {
        px('#4c6c65', x, 16, 7, 12);
        px('#6e9d98', x + 1, 17, 5, 6);
        px('#9cbeb4', x + 1, 17, 4);
        px('#344c45', x, 23, 7, 2);
        px('#6b7e70', x + 1, 26, 5);
      }
    },

    signal(px) {
      // Fubuki: a white fox signal lamp in an enamel railway case.
      px('#343632', 3, 16, 26, 14);
      px('#5d6a65', 4, 16, 24, 2);
      px('#253733', 6, 18, 20, 10);
      face(px, 10, 17, [
        'w.........w', 'ww.......ww', 'wmw.....wmw', 'wmmwwwwwmmw',
        'wwwwwwwwwww', '.wkwwwwkw.', '..wwwwwww..', '...wwkww...',
        '....www....',
      ], { w:'#dddcd2', m:'#8fb5af', k:'#304344' });
      px('#75a39c', 6, 28, 20);
    },

    staffBoard(px) {
      // Mio: a dark lacquered card case with red lining, mounted on the wall.
      px('#302727', 2, 16, 28, 14);
      px('#6f4c49', 3, 16, 26);
      px('#483032', 4, 18, 24, 10);
      px('#8e4d50', 5, 19, 22, 7);
      for (const [x,y] of [[8,19],[13,18],[18,19]]) {
        px('#28242a', x, y, 5, 8);
        px('#c3a683', x + 1, y + 1, 3, 6);
        px('#6f4d61', x + 1, y + 3, 3, 2);
      }
      px('#eed2a0', 15, 21, 1);
      px('#b17c66', 13, 28, 6);
    },

    kiosk(px) {
      // Okayu: the rice-and-nori sign belongs to the purple vending machine.
      px('#302732', 5, 28, 24, 3);
      px('#302733', 6, 4, 21, 25);
      px('#7a6082', 7, 5, 18, 23);
      px('#9b81a7', 8, 5, 16, 2);
      px('#514059', 23, 7, 3, 21);
      px('#48384c', 9, 8, 13, 12);
      face(px, 11, 9, [
        '....w....', '...www...', '..wwwww..', '.wwwwwww.',
        'wwwwwwwww', 'wwwnnnwww', 'wwwnnnwww', '.wwnnnww.',
      ], { w:'#ded0db', n:'#34343b' });
      px('#b9a2c2', 9, 21, 5);
      px('#b896ae', 21, 22, 2, 2);
      px('#423545', 11, 24, 10, 3);
      px('#9c829f', 10, 24, 11);
    },

    bench(px) {
      // Side profile: one closed eye, the round ear at the back and a
      // see-through mouth opening. The lower lip doubles as the seat.
      px('#34302a', 8, 29, 17, 2);
      px('#3e3831', 14, 24, 7, 6);
      px('#7b6c54', 15, 26, 3, 3);
      px('#9e8968', 15, 28, 3);
      const profile = [
        [11,18],[9,20],[7,22],[6,23],[5,24],[5,24],[4,24],
        [3,24],[4,24],[4,24],[3,25],[3,27],[4,28],
        [14,28],[16,28],[17,27],[17,26],[16,24],[15,24],
        [7,23],[5,23],[5,22],[6,21],[9,19],
      ];
      for (const [row, [left,right]] of profile.entries()) {
        const y = row + 3;
        px('#453a2d', left, y, right - left + 1);
        if (row === 0 || row === profile.length - 1) continue;
        // Keep the eye and mouth readable at native scale, with a darker far edge.
        const start = Math.max(left + 1, profile[row - 1][0]);
        const end = Math.min(right - 1, profile[row - 1][1]);
        if (start <= end) {
          px(row < 6 ? '#e0ca93' : row < 17 ? '#d0b67f' : '#b29a68',
            start, y, end - start + 1);
          if (end - start > 6) px('#e2cc97', start, y, end - start - 3);
        }
      }
      px('#ead7a5', 11, 5, 8);
      px('#ead7a5', 8, 6, 5);
      px('#66503a', 12, 9, 4);
      px('#66503a', 11, 10, 1, 2);
      px('#66503a', 16, 10, 1, 2);
      px('#bc9e69', 24, 15, 2, 4);
      px('#d0b985', 25, 16, 2, 2);
      px('#e7cf97', 7, 23, 11);
      px('#d0b37c', 6, 24, 13);
      px('#a38859', 8, 25, 12);
    },
  };
})();
