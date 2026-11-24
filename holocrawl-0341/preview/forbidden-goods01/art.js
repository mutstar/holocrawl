function createWarehouseWallArt() {
  const kinds = [
    { id: 'inventory', name: '재고 표시기', weight: 4, lights: '#84ada0' },
    { id: 'seal', name: '봉인 확인함', weight: 3, lights: '#c18d6d' },
    { id: 'intercom', name: '검수 호출기', weight: 3, lights: '#9286a9' },
  ];
  return kinds.map(({ lights, ...kind }) => {
    const sprite = document.createElement('canvas');
    sprite.width = sprite.height = 32;
    const context = sprite.getContext('2d');
    const paint = (color, x, y, w, h) => {
      context.fillStyle = color;
      context.fillRect(x, y, w, h);
    };
    paint('#323036', 5, 10, 22, 13);
    paint('#80727e', 6, 10, 20, 2);
    paint('#504750', 7, 12, 18, 9);
    paint('#292b31', 9, 13, 13, 6);
    for (const x of [10, 14, 18]) paint(lights, x, 15, 2, 2);
    if (kind.id === 'seal') paint('#b58762', 22, 16, 2, 4);
    return { ...kind, sprite };
  });
}

function drawWarehouse(context, map, zones, wallDecorations) {
  const size = 32;
  const { w, h, cells } = map;
  const floor = (x, y) => x >= 0 && y >= 0 && x < w && y < h && cells[y * w + x] !== StreetGen.WALL;
  const paint = (color, x, y, width, height) => {
    context.fillStyle = color;
    context.fillRect(x, y, width, height);
  };
  context.imageSmoothingEnabled = false;
  paint('#161719', 0, 0, w * size, h * size);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const left = x * size;
    const top = y * size;
    if (floor(x, y)) {
      const shade = 57 + ((x * 19 + y * 11 + x * y) % 6);
      paint(`rgb(${shade + 3},${shade},${shade - 2})`, left, top, size, size);
      paint('#2e2c30', left, top, size, 1);
      paint('#2e2c30', left, top + 1, 1, 31);
      paint('#464047', left + 2, top + 1, 29, 1);
      if ((x * 7 + y) % 4 === 0) {
        paint('#363338', left + 8, top + 23, 7, 1);
        paint('#4c474a', left + 10, top + 22, 3, 1);
      }
      FloorOvergrowth.draw(context, 'tile', map.seed, x, y);
    } else if (floor(x, y + 1)) {
      paint('#514a54', left, top + 6, size, 25);
      paint('#74656d', left, top + 6, size, 2);
      paint('#3c353e', left, top + 23, size, 8);
      paint('#8c6b55', left, top + 25, size, 2);
      paint('#27262a', left, top + 30, size, 2);
      paint('#443e46', left + 1, top + 8, 1, 15);
      paint('#5c525d', left + 2, top + 9, 1, 13);
      for (const bolt of [4, 27]) paint('#80767d', left + bolt, top + 18, 1, 1);
    } else if (floor(x - 1, y) || floor(x + 1, y)) {
      if (floor(x - 1, y)) paint('#4a444b', left, top, 3, size);
      if (floor(x + 1, y)) paint('#4a444b', left + 29, top, 3, size);
    }
  }

  for (const { sprite, x, y } of wallDecorations) context.drawImage(sprite, x * size, y * size);
  for (const zone of zones) drawWarehouseZone(paint, zone);
  const { upstairs, start, exitDoor } = map;
  paint('#28272a', upstairs.x * 32 + 2, upstairs.y * 32 + 3, 28, 26);
  paint('#84786a', upstairs.x * 32 + 4, upstairs.y * 32 + 5, 24, 20);
  for (let step = 0; step < 4; step++) {
    paint('#493f3d', upstairs.x * 32 + 6, upstairs.y * 32 + 7 + step * 4, 20, 2);
    paint('#a48e78', upstairs.x * 32 + 6, upstairs.y * 32 + 9 + step * 4, 20, 1);
  }
  paint('#8a7049', start.x * 32 + 6, start.y * 32 + 4, 20, 2);

  const left = (exitDoor.x + 1) * 32;
  const top = (exitDoor.y + 1) * 32;
  paint('#2b2b2c', left, top + 2, 64, 29);
  paint('#817077', left + 2, top + 4, 60, 26);
  paint('#534a53', left + 5, top + 7, 54, 21);
  for (const offset of [10, 15, 20, 25]) paint('#746370', left + 6, top + offset, 52, 1);
  paint('#c1935d', left + 10, top + 12, 8, 3);
  paint('#c1935d', left + 46, top + 12, 8, 3);
  paint('#b77161', left + 30, top + 3, 4, 2);
}

function drawWarehouseZone(paint, zone) {
  const { x, y, band, width, height, props } = zone;
  const left = x * 32;
  const top = y * 32;
  paint(`${band}2b`, left + 2, top + 2, width * 32 - 4, height * 32 - 4);
  for (let tile = 0; tile < width; tile++) {
    paint(`${band}aa`, left + tile * 32 + 6, top + 5, 20, 2);
    paint(`${band}aa`, left + tile * 32 + 6, top + height * 32 - 7, 20, 2);
  }
  for (const [kind, dx, dy, span] of props) {
    drawWarehouseProp(paint, kind, left + dx * 32, top + dy * 32, span * 32, band);
  }
}

function drawWarehouseProp(paint, kind, left, top, width, band) {
  const put = (color, x, y, w, h) => paint(color, left + x, top + y, w, h);
  put('#2222249f', 3, 24, width - 5, 6);
  put('#2b292d', 4, 12, width - 8, 15);
  if (kind === 'counter') {
    put('#6e756e', 5, 8, width - 10, 14);
    put('#899187', 6, 8, width - 12, 2);
    put('#403b40', 7, 20, width - 14, 4);
    put('#252c2e', 12, 10, 15, 9);
    put('#759c89', 14, 10, 11, 5);
    put('#bca487', width - 25, 12, 12, 7);
    put('#827061', width - 23, 14, 8, 1);
  } else if (kind === 'cage' || kind === 'shelf') {
    put('#6e5e6d', 5, 3, width - 10, 23);
    put('#322d37', 8, 6, width - 16, 17);
    for (let bay = 0; bay < 3; bay++) {
      const x = 11 + bay * 26;
      put(kind === 'cage' ? '#8d6d52' : '#715f73', x, 11, 19, 10);
      put(band, x + 1, 10, 17, 2);
      put('#c1a988', x + 7, 15, 5, 2);
    }
    if (kind === 'cage') {
      for (let wire = 9; wire < width - 8; wire += 4) put('#b39f735c', wire, 7, 1, 17);
      put('#b48453', 8, 24, width - 16, 2);
    }
  } else {
    put(kind === 'cart' ? '#626d67' : '#786352', 5, 10, width - 10, 13);
    put(band, 6, 10, width - 12, 2);
    put('#302c30', 10, 17, width - 20, 4);
    put('#bd9c68', width / 2 - 3, 15, 6, 4);
    for (const x of [9, width - 14]) put('#252527', x, 24, 5, 4);
  }
}
