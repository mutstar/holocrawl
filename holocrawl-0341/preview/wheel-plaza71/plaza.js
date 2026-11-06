(() => {
  window.vaultTheme = {
    name: '4기생 관람차',
    vaultFile: './vault.json',
    defaultReward: 'weapon',
    assets: {
      weapon: '../theater-vault36/assets/reward-weapon.png',
      wheel: '../generation-structures29/assets/wheel-native.png',
    },
    startMessage: '매표소 옆 탑승구를 열고 관람차 뒤편으로 가 보세요.',
    walkMessage: '관람차 광장을 둘러보는 중입니다.',
    stairsMessage: '기존 시작 계단에서 관람차 광장까지 탐험합니다.',
    showLabels: '구역 표시',
    hideLabels: '구역 숨기기',
    doorMessage: (x, y) => x === gate.x && y === gate.y ? '탑승구를 열었습니다.' : undefined,
    blockedMessage: tile => tile === 'G' ? '안전 펜스가 길을 막고 있습니다.' : undefined,
    inventory: ({ weapon = 0, scroll = 0, potion = 0 }) =>
      `획득  +2 숏소드 ${weapon}개 / 스크롤 ${scroll}장 / 포션 ${potion}개`,
  };

  const size = 32;
  const art = document.createElement('canvas');
  const canvas = art.getContext('2d');
  let wheel;
  const gate = { x: 6, y: 5 };
  const stone = ['#45474b', '#48494d', '#494a4d', '#46474b'];
  const paint = (g, color, x, y, w, h = 1) => {
    g.fillStyle = color;
    g.fillRect(x, y, w, h);
  };
  const rect = (color, x, y, w, h = 1) => paint(canvas, color, x, y, w, h);
  const grain = (x, y) => {
    const seed = Math.imul(x + 37, 0x27d4eb2d) ^ Math.imul(y + 79, 0x165667b1);
    return Math.imul(seed ^ (seed >>> 16), 0x45d9f3b) >>> 0;
  };

  function pavement() {
    for (let y = 0; y < art.height; y++) {
      for (let x = 0; x < art.width; x++) {
        const stagger = (y >> 3) % 2 * 7;
        const brickX = Math.floor((x + stagger) / 14);
        const brickY = y >> 3;
        const joint = y % 8 === 0 || (x + stagger) % 14 === 0;
        const color = joint ? '#3d3f44' : stone[grain(brickX, brickY) >>> 30];
        rect(color, x, y, 1);
      }
    }
  }

  function walls(rows) {
    for (const [y, row] of rows.entries()) {
      for (const [x, cell] of [...row].entries()) {
        if (cell !== '#') continue;
        const px = x * size;
        const py = y * size;
        rect('#2c2c2d', px, py, size, size);
        for (let i = 0; i < 52; i++) {
          const value = grain(i, x + y * 9);
          rect(value % 2 ? '#303033' : '#292a2b', px + value % 32, py + ((value >>> 10) % 31), 1);
        }
        if (y === 0 || y === 8) {
          rect('#3a373b', px, py + 18, size, 11);
          rect('#646063', px, py + 18, size);
          rect('#4b464a', px, py + 19, size, 7);
          rect('#594452', px, py + 26, size, 2);
          rect('#222326', px, py + 29, size, 3);
          rect('#3c353a', px + 15, py + 19, 1, 7);
        }
        if (x === 0 || x === 8) {
          const inside = px + (x === 0 ? 28 : 0);
          rect('#413c42', inside, py, 4, 32);
          rect('#635962', inside + (x === 0 ? 3 : 0), py, 1, 32);
        }
      }
    }
  }

  function wheelYard() {
    // Keep the same paving beneath the wheel. Only the machinery casts a shadow.
    for (let dy = -25; dy <= 25; dy++) {
      const halfWidth = Math.floor(58 * Math.sqrt(1 - (dy / 26) ** 2));
      const center = 134 + Math.floor(dy / 5);
      rect('rgba(25,23,29,.16)', center - halfWidth, 158 + dy, halfWidth * 2 + 1);
    }

    // Low bollards mark the machinery area without framing the whole sprite.
    for (const [x, y] of [[66,82],[66,128],[66,175],[88,187],[168,187],[189,175],[189,128],[189,82]]) {
      rect('rgba(25,23,29,.26)', x - 2, y + 2, 7, 2);
      rect('#363238', x - 1, y - 3, 4, 6);
      rect('#82747c', x - 1, y - 3, 3);
      rect('#61565f', x, y - 2, 2, 4);
    }
    // The concrete footings sit directly beneath the legs.
    for (const x of [101, 139]) {
      rect('#302d34', x, 186, 17, 5);
      rect('#6d6269', x + 2, 186, 13, 2);
      rect('#514a53', x + 1, 188, 15, 2);
    }
  }

  function rail(x, y) {
    rect('#2b3034', x, y + 14, size, 5);
    rect('#808083', x, y + 14, size);
    rect('#45484e', x, y + 18, size);
    for (const offset of [2, 28]) {
      rect('#353439', x + offset, y + 10, 3, 14);
      rect('#8d8582', x + offset, y + 10, 3, 2);
    }
  }

  function ticketBooth() {
    const x = 224;
    const y = 224;
    rect('rgba(19,19,22,.48)', x + 2, y + 27, 30, 3);
    rect('#392c39', x + 5, y + 6, 24, 23);
    rect('#827171', x + 7, y + 10, 20, 17);
    rect('#b8a297', x + 7, y + 10, 20, 2);
    rect('#574956', x + 24, y + 11, 3, 16);
    rect('#644e62', x + 3, y + 5, 27, 7);
    rect('#9e7892', x + 5, y + 4, 23, 3);
    rect('#c095ad', x + 6, y + 5, 20);
    rect('#3a2d3b', x + 3, y + 10, 27, 2);
    rect('#383038', x + 10, y + 13, 13, 8);
    rect('#726578', x + 11, y + 14, 11, 4);
    rect('#cabbad', x + 9, y + 20, 15, 2);
    rect('#b89b71', x + 18, y + 18, 3, 2);
    rect('#544350', x + 10, y + 24, 11, 3);
    rect('#383237', x + 2, y + 20, 5, 7);
    rect('#b7aa89', x + 3, y + 20, 3, 4);
  }

  function waitingBench(x, y, planter) {
    rect('rgba(21,21,23,.36)', x + 4, y + 26, 56, 4);
    rect('#392d30', x + 4, y + 12, 48, 12);
    for (const offset of [13, 16, 19]) {
      rect('#87654f', x + 5, y + offset, 46, 2);
      rect('#a78364', x + 5, y + offset, 44);
      for (const bolt of [8, 27, 48]) rect('#6a534a', x + bolt, y + offset, 1);
    }
    rect('#a38666', x + 4, y + 22, 49, 2);
    rect('#654d43', x + 5, y + 24, 47, 2);
    for (const offset of [7, 27, 48]) {
      rect('#3a363a', x + offset, y + 24, 3, 5);
      rect('#817472', x + offset, y + 25, 1, 3);
    }
    if (planter) {
      rect('#55413b', x + 56, y + 22, 7, 6);
      rect('#aa775c', x + 57, y + 22, 5, 2);
      rect('#755444', x + 57, y + 24, 5, 3);
      rect('#414a3d', x + 55, y + 16, 7, 6);
      rect('#707b57', x + 56, y + 16, 3, 4);
      rect('#879367', x + 59, y + 17, 2, 4);
    }
  }

  function controlPanel(x, y) {
    rect('rgba(21,21,23,.36)', x + 6, y + 26, 23, 4);
    rect('#333035', x + 8, y + 9, 21, 19);
    rect('#5d575e', x + 9, y + 15, 18, 12);
    rect('#746c70', x + 9, y + 16, 2, 10);
    rect('#46414a', x + 22, y + 16, 5, 10);
    rect('#8e8384', x + 6, y + 9, 22, 7);
    rect('#a09591', x + 7, y + 9, 20);
    rect('#3e4146', x + 8, y + 11, 18, 4);
    rect('#75a39c', x + 9, y + 11, 7, 2);
    rect('#b97a68', x + 18, y + 12, 2);
    rect('#c6ab7e', x + 21, y + 12, 2);
    rect('#393941', x + 12, y + 20, 8, 4);
    rect('#aba087', x + 14, y + 20, 4);
    rect('#5e4e4b', x + 25, y + 5, 2, 7);
    rect('#c28a73', x + 24, y + 4, 4, 2);
  }

  function plazaDetails(vault) {
    for (const station of vault.stations) {
      const x = station.x * size;
      const y = station.y * size;
      if (station.id.startsWith('bench-')) waitingBench(x, y, station.id === 'bench-east');
      if (station.id === 'control') controlPanel(x, y);
    }

    // A wall poster and paired amber lamps use the existing masonry face.
    rect('#302a32', 185, 17, 25, 13);
    rect('#8b706d', 186, 17, 23);
    rect('#62526a', 187, 19, 21, 9);
    rect('#c6a879', 193, 20, 8, 1);
    rect('#c6a879', 191, 22, 2, 3);
    rect('#c6a879', 201, 22, 2, 3);
    rect('#bc90a9', 195, 23, 4, 2);
    rect('#aa8a75', 191, 26, 12);
    for (const x of [80, 225]) {
      rect('#3d3434', x, 17, 8, 11);
      rect('#ae8866', x + 1, 18, 6, 6);
      rect('#e2c097', x + 2, 19, 4, 3);
      rect('#725444', x + 2, 24, 4, 2);
    }

    // Small floor arrows lead from the queue toward the gate.
    for (const x of [160, 178]) {
      const y = 218;
      rect('#776a6e', x, y, 6);
      rect('#9a8382', x + 4, y - 2, 1);
      rect('#9a8382', x + 5, y - 1, 1);
      rect('#9a8382', x + 5, y + 1, 1);
      rect('#9a8382', x + 4, y + 2, 1);
    }
    rect('#776a6e', 207, 199, 1, 8);
    rect('#9a8382', 207, 199, 1);
    rect('#9a8382', 206, 200, 1);
    rect('#9a8382', 208, 200, 1);
    rect('#9a8382', 205, 201, 1);
    rect('#9a8382', 209, 201, 1);
  }

  function buildWheel(source) {
    const sprite = document.createElement('canvas');
    sprite.width = sprite.height = 128;
    const g = sprite.getContext('2d');
    g.imageSmoothingEnabled = false;
    const pixel = (color, x, y, w = 1, h = 1) => paint(g, color, x, y, w, h);
    const hubX = 64;
    const hubY = 58;
    const cabins = [
      { anchor: [35, 29], shift: [9, -24], pieces: [[17, 38, 18, 8], [5, 46, 41, 23]] },
      { anchor: [93, 29], shift: [28, 12], pieces: [[51, 0, 28, 35]] },
      { anchor: [35, 87], shift: [0, -11], pieces: [[32, 83, 12, 7], [17, 90, 37, 23]] },
      { anchor: [93, 87], shift: [-3, -11], pieces: [[86, 84, 21, 7], [75, 91, 43, 23]] },
    ];
    // A new evenly spaced rim keeps the four cabin anchors on the same circle.
    for (let y = 12; y <= 103; y++) {
      for (let x = 18; x <= 110; x++) {
        const distance = Math.hypot(x - hubX, y - hubY);
        if (distance >= 39 && distance <= 44) {
          const color = distance < 40 || distance > 43 ? '#342d35'
            : distance >= 42 ? '#bca074' : '#967d65';
          pixel(color, x, y);
        }
      }
    }
    for (const [x, y] of cabins.map(cabin => cabin.anchor)) {
      for (let i = 0; i <= 29; i++) {
        const px = hubX + Math.round((x - hubX) * i / 29);
        const py = hubY + Math.round((y - hubY) * i / 29);
        pixel('#332b40', px - 2, py - 2, 5, 5);
      }
      for (let i = 0; i <= 29; i++) {
        const px = hubX + Math.round((x - hubX) * i / 29);
        const py = hubY + Math.round((y - hubY) * i / 29);
        pixel('#70608b', px - 1, py - 1, 3, 3);
      }
    }
    // The rear struts flare into the existing pair of concrete footings.
    for (let y = 62; y < 125; y++) {
      const spread = 3 + Math.floor((y - 62) * 16 / 62);
      for (const x of [hubX - spread, hubX + spread]) {
        pixel('#372d3d', x - 4, y, 9);
        pixel('#726087', x - 2, y, 5);
        pixel('#9b7d9e', x - 2, y, 1);
      }
    }
    pixel('#5c4658', 48, 118, 32, 3);
    for (const x of [41, 77]) {
      pixel('#493740', x, 124, 11, 4);
      pixel('#c2a17a', x + 1, 124, 9, 2);
    }
    g.drawImage(source, 52, 51, 25, 25, hubX - 12, hubY - 12, 25, 25);
    for (const { shift: [dx, dy], pieces } of cabins) {
      for (const [x, y, w, h] of pieces) g.drawImage(source, x, y, w, h, x + dx, y + dy, w, h);
    }
    return sprite;
  }

  window.holoxSecurityDoor = {
    source: '../holox-floor55/',
    install(layout, vault) {
      const { x, y } = layout.origin;
      for (const [dy, row] of vault.rows.entries()) {
        const outside = layout.map.rows[y + dy];
        layout.map.rows[y + dy] = outside.slice(0, x) + row + outside.slice(x + vault.width);
      }
      art.width = vault.width * size;
      art.height = vault.height * size;
      pavement();
      walls(vault.rows);
      wheelYard();
      for (const column of [1, 7]) rail(column * size, gate.y * size);
      ticketBooth();
      plazaDetails(vault);
      window.drawFacilityEntrance(canvas, vault.rows, 'wheel');
      return null;
    },
    drawInterior(g, origin, opened) {
      const x = (origin.x + gate.x) * size;
      const y = (origin.y + gate.y) * size;
      const isOpen = opened.has(`${origin.x + gate.x},${origin.y + gate.y}`);
      for (const left of [1, 26]) {
        paint(g, '#36363e', x + left, y + 9, 5, 15);
        paint(g, '#9c8794', x + left + 1, y + 9, 3, 2);
        paint(g, isOpen ? '#a1bf9d' : '#d28374', x + left + 1, y + 12, 3);
      }
      if (!isOpen) {
        paint(g, '#4d404b', x + 6, y + 14, 20, 6);
        paint(g, '#bfa28c', x + 6, y + 14, 20);
        for (const left of [8, 13, 18, 23]) paint(g, '#8e7884', x + left, y + 16, 1, 4);
      }
    },
  };
  window.LabMaterials = {
    draw(target, origin, vault, images) {
      const x = origin.x * size;
      const y = origin.y * size;
      target.drawImage(art, x, y);
      wheel ??= buildWheel(images.wheel);
      target.drawImage(wheel, x + 64, y + 64);
    },
  };
})();
