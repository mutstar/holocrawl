// Native facade details stay within the reviewed entrance and its two side walls.
window.drawNativeEntrance78 = (context, id, rows) => {
  const last = rows.at(-1);
  const openings = [...last].flatMap((cell, x) => cell === '.' || cell === '+' ? [x] : []);
  if (!openings.length) throw Error(`Missing entrance for ${id}`);
  const first = openings[0], final = openings.at(-1);
  const left = (first - 1) * 32, top = (rows.length - 1) * 32;
  const span = (final - first + 3) * 32;
  const paint = (color, x, y, width, height = 1) => {
    context.fillStyle = color;
    context.fillRect(left + x, top + y, width, height);
  };
  const palettes = {
    mountain: ['#34392f', '#817860', '#c0af89'], dining: ['#422b29', '#8c5142', '#d5a77a'],
    theater: ['#2c1c26', '#713e4c', '#cda86d'], gamers: ['#303e3c', '#78938b', '#bbd2bd'],
    fantasy: ['#443b30', '#8b7850', '#cebd89'], wheel: ['#3a2e3b', '#8c6480', '#d5ad82'],
    market: ['#2b4238', '#61826b', '#b9c5a0'], holox: ['#20202e', '#69527e', '#c095df'],
    dev: ['#232430', '#6a537b', '#db9ec8'],
  };
  const [dark, face, light] = palettes[id];
  for (const x of [24, span - 32]) {
    paint(dark, x - 2, 5, 10, 27);
    paint(face, x, 7, 6, 24);
    paint(light, x, 8, 1, 20);
    paint(dark, x - 3, 29, 12, 3);
  }
  if (id === 'theater') {
    // Keep the approved HOLO CINEMAS lettering above the two door leaves.
    for (const x of [9, span - 32]) {
      paint(dark, x, 0, 23, 7);
      paint(face, x + 1, 1, 21, 4);
      paint(light, x + 2, 1, 19);
    }
  } else {
    paint(dark, 9, 0, span - 18, 7);
    paint(face, 10, 1, span - 20, 4);
    paint(light, 12, 1, span - 24);
  }

  if (id === 'holox') {
    // Round violet windows are recessed into connected caution-striped plating.
    for (const center of [15, span - 15]) {
      paint('#171721', center - 9, 12, 18, 16);
      for (const [y, half] of [[13,4],[14,5],[15,6],[16,6],[17,6],[18,6],[19,6],[20,5],[21,4]]) {
        paint('#684096', center - half, y, half * 2);
      }
      paint('#b983dc', center - 3, 14, 6, 5);
      paint('#dfb4f1', center - 2, 14, 3, 2);
    }
    for (const start of [0, span - 32]) {
      paint('#242126', start, 29, 32, 3);
      for (let x = start + 1; x < start + 31; x += 6) {
        paint('#bc9c32', x, 29, 3);
        paint('#bc9c32', x - 1, 30, 3);
      }
    }
    return;
  }
  if (id === 'gamers') {
    paint('#3b5351', 6, 0, span - 12, 4);
    paint('#abc1ab', 6, 0, span - 12);
    for (const center of [15, span - 15]) {
      paint('#263f3e', center - 5, 12, 10, 10);
      paint('#759f96', center - 4, 13, 8, 8);
      paint('#b4d0b7', center - 2, 13, 4, 2);
      paint('#304c47', center, 14, 1, 6);
    }
  } else if (id === 'dining') {
    for (let x = 12; x < span - 12; x += 11) {
      if (x >= 32 && x < span - 32) continue;
      paint('#6f3434', x, 8, 9, 7);
      paint('#b87759', x + 1, 8, 7, 2);
    }
    for (const x of [12, span - 20]) {
      paint('#d0a36d', x + 3, 8, 2, 4);
      paint('#613a32', x, 12, 8, 11);
      paint('#c67d56', x + 1, 13, 6, 8);
      paint('#f0c18b', x + 2, 14, 3, 4);
    }
  } else if (id === 'market') {
    for (let x = 10; x < span - 10; x += 6) {
      paint((x - 10) % 12 ? '#637f6b' : '#b9b59a', x, 5, 6, 4);
    }
    for (const [x, color] of [[37,'#8bb4ca'],[43,'#d7a763'],[49,'#aab5a3'],[55,'#bd7f8b']]) paint(color, x, 2, 3, 2);
  } else if (id === 'wheel') {
    const center = span / 2;
    for (const [y, half] of [[0,6],[1,8],[2,9],[3,9],[4,9],[5,8],[6,6]]) paint('#c7a17c', center - half, y, half * 2);
    paint('#5e425b', center - 5, 1, 10, 5);
    paint('#e0b77f', center - 1, 1, 2, 5);
  } else if (id === 'fantasy') {
    for (const [x, color] of [[12,'#b87b64'],[span - 21,'#bbb590']]) {
      paint('#c2af7f', x, 7, 1, 16);
      paint(color, x + 1, 8, 8, 5);
      paint(light, x + 1, 8, 6);
    }
  } else if (id === 'theater') {
    for (const x of [11, span - 21]) {
      paint('#bc925f', x, 10, 9, 16);
      paint('#4a2c35', x + 1, 11, 7, 14);
      paint('#b66867', x + 2, 13, 5, 4);
      paint('#d6b77c', x + 3, 19, 3, 2);
    }
  } else if (id === 'dev') {
    paint('#d287b1', 12, 2, 25, 2);
    paint('#7fb7c4', span - 37, 2, 25, 2);
    for (const x of [13, span - 20]) {
      paint('#2d273e', x, 12, 7, 12);
      paint('#8e6c9f', x + 1, 13, 5, 2);
      paint('#7ab2c1', x + 1, 19, 5, 2);
    }
  }
};
