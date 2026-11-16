function drawEndingFixture(paint, id, placement, accent) {
  const palette = {
    flood: ['#68828a', '#455f65'], street: ['#a58765', '#645547'],
    factory: ['#9c8e63', '#5c6058'], horror: ['#9d7685', '#654957'],
    tower: ['#8e9eac', '#525f70'], garden: ['#8d9d73', '#526854'],
    archive: ['#a6977d', '#645a50'], mirror: ['#ac91a4', '#66566a'],
    rail: ['#9a8667', '#615344'], power: ['#ad995d', '#6e6250'],
  };
  const [metal, body] = palette[id];
  const shadow = '#252a2b';
  if (placement === 'wall') {
    paint('#161a1c90', 5, 9, 54, 17);
    paint(body, 6, 10, 52, 13);
    paint(`${metal}bf`, 7, 10, 50, 1);
    paint(shadow, 8, 12, 48, 9);
    drawEndingWallEquipment(paint, id, metal, body, accent);
    return;
  }

  for (const x of [3, 51]) {
    paint(`${accent}75`, x, 4, 10, 1);
    paint(`${accent}75`, x === 3 ? x : x + 9, 4, 1, 5);
  }
  paint('#171a1b8c', 4, 24, 56, 5);
  paint(shadow, 7, 17, 50, 9);
  paint(body, 8, 18, 48, 6);
  paint(metal, 8, 18, 48, 1);
  for (const x of [9, 50]) paint(shadow, x, 23, 4, 6);
  drawEndingFloorEquipment(paint, id, metal, body, accent);
}

function drawEndingWallEquipment(p, id, metal, body, accent) {
  if (id === 'flood') {
    p(metal, 10, 16, 44, 3);
    p('#8ba3a3', 11, 16, 42, 1);
    for (const x of [17, 41]) {
      p('#39474c', x, 12, 5, 9);
      p(accent, x - 2, 12, 9, 2);
      p('#23363b', x + 1, 14, 2, 4);
    }
  } else if (id === 'street') {
    p('#735849', 10, 12, 44, 8);
    for (const [x, width] of [[12,10],[24,11],[37,14]]) {
      p('#bf9470', x, 13, width, 4);
      for (let stroke = x + 2; stroke < x + width - 1; stroke += 3) p('#765d4e', stroke, 14, 1, 2);
    }
  } else if (id === 'factory') {
    p('#596060', 10, 12, 44, 8);
    for (const [x, y] of [[13,13],[20,15],[27,13],[34,15],[44,13]]) {
      p(metal, x, y, 2, 5);
      p(accent, x - 1, y, 4, 1);
    }
  } else if (id === 'horror') {
    for (const x of [11, 27, 43]) {
      p('#614752', x, 12, 10, 8);
      p('#c28c86', x + 2, 13, 6, 2);
      p('#241f28', x + 2, 16, 6, 3);
      p(metal, x + 7, 17, 2, 1);
    }
  } else if (id === 'tower') {
    p('#344856', 10, 12, 44, 8);
    for (const [x, h] of [[13,3],[19,5],[25,2],[31,6],[37,4],[43,2]]) p('#86acb0', x, 19 - h, 2, h);
    p(accent, 50, 14, 3, 3);
  } else if (id === 'garden') {
    p('#365346', 10, 14, 44, 5);
    p('#76a59a', 12, 13, 40, 1);
    for (const x of [14, 24, 36, 47]) {
      p(metal, x, 15, 2, 4);
      p('#a0b7a5', x - 1, 19, 4, 1);
    }
  } else if (id === 'archive') {
    for (const x of [12, 23, 35, 46]) {
      p('#4e5552', x, 12, 7, 8);
      p(metal, x + 1, 12, 5, 1);
      p('#a9aaa0', x + 2, 15, 3, 3);
      p('#404643', x + 3, 16, 1, 1);
    }
  } else if (id === 'mirror') {
    p('#526574', 12, 12, 40, 8);
    p('#b6ccd1', 16, 14, 13, 1);
    p('#8da8b0', 19, 15, 5, 1);
    for (const x of [12, 20, 28, 36, 44, 51]) p('#e2c3a2', x, 12, 2, 1);
    p(metal, 12, 20, 40, 1);
  } else if (id === 'rail') {
    p('#a58e72', 12, 17, 39, 1);
    p('#a58e72', 28, 14, 23, 1);
    p('#a58e72', 27, 15, 2, 2);
    for (const x of [18, 47]) p('#a2ad7e', x, 14, 2, 3);
    p('#c18468', 51, 15, 2, 2);
  } else {
    for (const x of [12, 22, 32, 42]) {
      p(body, x, 12, 8, 8);
      p(metal, x + 2, 14, 4, 2);
      p('#222a2b', x + 3, 16, 2, 3);
    }
    p('#9aa475', 52, 13, 2, 2);
  }
}

function drawEndingFloorEquipment(p, id, metal, body, accent) {
  const dark = '#2a3134';
  if (id === 'flood') {
    p('#465e65', 10, 10, 35, 8);
    p('#72a09d', 11, 10, 31, 1);
    p(body, 38, 6, 12, 13);
    p(metal, 40, 5, 7, 2);
    p('#2f4148', 16, 8, 12, 13);
    p('#6e8d90', 17, 8, 10, 4);
    p(accent, 18, 7, 7, 2);
    p('#869b91', 51, 12, 5, 2);
  } else if (id === 'street') {
    p('#514131', 11, 7, 41, 13);
    p('#a77e56', 13, 7, 37, 6);
    p('#c19c76', 14, 7, 34, 1);
    p('#785941', 15, 14, 33, 3);
    for (const x of [14, 45]) {
      p('#757e76', x, 15, 3, 9);
      p('#99988b', x - 2, 23, 7, 1);
    }
    p('#626e65', 20, 19, 13, 4);
  } else if (id === 'factory') {
    p('#4e5756', 11, 12, 42, 7);
    p('#888b75', 12, 12, 39, 2);
    p('#a5824d', 25, 7, 18, 5);
    p('#c3a76d', 26, 7, 16, 1);
    p('#a5824d', 23, 9, 5, 10);
    p(dark, 40, 10, 5, 8);
    p('#a2b7aa', 43, 16, 3, 2);
    p('#8e9384', 13, 15, 8, 2);
  } else if (id === 'horror') {
    p('#4c3845', 10, 7, 23, 12);
    p('#8e6476', 11, 7, 21, 2);
    p('#2e2532', 12, 11, 18, 6);
    p('#6f5165', 35, 12, 16, 7);
    p('#9f7988', 37, 13, 11, 2);
    for (const x of [39, 46]) {
      p('#b4a4a0', x, 10, 4, 4);
      p('#524854', x + 1, 11, 2, 1);
    }
  } else if (id === 'tower') {
    p('#405261', 10, 5, 19, 15);
    p(metal, 11, 5, 17, 2);
    for (const y of [8, 12, 16]) {
      p('#252e3b', 12, y, 12, 2);
      p('#9cbead', 25, y, 2, 1);
    }
    p('#607985', 34, 10, 16, 6);
    p('#9aa8a8', 36, 9, 12, 2);
    p(accent, 44, 13, 3, 1);
    p('#465462', 40, 15, 3, 5);
  } else if (id === 'garden') {
    p('#685942', 10, 10, 44, 9);
    p('#a28f6a', 11, 10, 42, 1);
    for (const [x, y] of [[14,8],[23,5],[34,7],[44,5]]) {
      p('#5a7956', x, y, 8, 9);
      p('#81a273', x + 2, y, 5, 3);
      p('#b0a774', x + 2, y + 1, 2, 2);
      p('#524537', x + 1, 14, 7, 3);
    }
  } else if (id === 'archive') {
    p('#7d6954', 10, 11, 43, 8);
    p('#ad9675', 11, 11, 39, 1);
    for (const x of [16, 33]) {
      p('#363b3c', x, 7, 11, 8);
      p('#92928a', x + 1, 8, 9, 6);
      p('#555e5b', x + 4, 9, 3, 4);
      p('#d1b87a', x + 5, 10, 1, 2);
    }
    p('#817963', 40, 15, 10, 2);
  } else if (id === 'mirror') {
    p('#594659', 13, 4, 32, 12);
    p('#778692', 15, 5, 28, 9);
    p('#a8bdc4', 18, 7, 12, 1);
    for (const x of [15,23,32,41]) p('#e1ba98', x, 5, 2, 2);
    p('#876d79', 10, 15, 43, 5);
    p('#c18f96', 17, 13, 4, 3);
    p('#747e83', 46, 12, 4, 5);
  } else if (id === 'rail') {
    p('#393e3e', 8, 18, 49, 5);
    p('#655b47', 10, 9, 44, 10);
    p('#a17a54', 11, 8, 42, 4);
    p('#bc9870', 13, 8, 38, 1);
    for (const x of [15, 25, 35, 45]) {
      p('#2a3539', x, 12, 6, 6);
      p('#718882', x + 1, 13, 4, 3);
    }
    for (const x of [13, 48]) p('#262b2c', x, 21, 6, 4);
  } else {
    p('#504a38', 10, 9, 40, 11);
    p(metal, 11, 9, 38, 2);
    p('#262b2b', 15, 12, 22, 6);
    for (const x of [17, 21, 25, 29, 33]) p('#676f64', x, 13, 2, 4);
    p('#74765c', 40, 12, 7, 6);
    p('#a4a76d', 42, 13, 3, 2);
    p('#5f5644', 51, 11, 5, 9);
  }
}
