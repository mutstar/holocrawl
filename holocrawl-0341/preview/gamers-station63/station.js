(() => {
  const art = window.gamersStationArt ?? {};
  const doors = {
    '6,8': { kind: 'entry', message: '미닫이 출입문을 열었습니다.' },
    '6,6': { kind: 'gate', message: '개찰구가 열렸습니다.' },
    '5,3': { kind: 'staff', message: '역무실 문을 열었습니다.' },
  };
  window.vaultTheme = {
    name: '게이머즈 폐역',
    vaultFile: './vault.json',
    defaultReward: 'weapon',
    assets: { weapon: '../theater-vault36/assets/reward-weapon.png' },
    startMessage: '미닫이문으로 들어가 개찰구를 지나면 옛 승강장이 나옵니다.',
    walkMessage: '게이머즈 폐역을 둘러보는 중입니다.',
    stairsMessage: '기존 시작 계단에서 게이머즈 폐역까지 탐험합니다.',
    showLabels: '구역 표시',
    hideLabels: '구역 숨기기',
    blockedMessage: tile => tile === 'T' ? '승강장 아래 선로에는 내려갈 수 없습니다.' : undefined,
    doorMessage: (x, y) => doors[x + ',' + y]?.message,
    inventory: ({ weapon = 0, scroll = 0, potion = 0 }) =>
      `획득: +2 숏소드 ${weapon}개 / 스크롤 ${scroll}장 / 포션 ${potion}개`,
  };

  const paint = (g, draw) => draw((color, x, y, w, h = 1) => {
    g.fillStyle = color;
    g.fillRect(x, y, w, h);
  });
  const tile = (g, x, y, draw) => {
    g.save();
    g.translate(x * 32, y * 32);
    paint(g, draw);
    g.restore();
  };
  const noise = (x, y, salt) =>
    (Math.imul(x + salt * 17, 0x45d9f3b) ^ Math.imul(y + salt * 7, 0x119de1f3)) >>> 0;
  const dust = (px, seed, colors, count, y0 = 0, h = 32) => {
    for (let i = 0; i < count; i++) {
      const n = noise(i, seed, 17);
      px(colors[(n >>> 21) % colors.length], n % 31, y0 + ((n >>> 10) % h), 1 + (n >>> 30) % 2);
    }
  };

  const stationTiles = document.createElement('canvas');
  stationTiles.width = stationTiles.height = 9 * 32;
  const surface = stationTiles.getContext('2d');
  const wall = (px, at, x, y) => {
    const solid = (tx, ty) => ['#', '+'].includes(at(tx, ty));
    const west = x > 0 && !solid(x - 1, y);
    const east = x < 8 && !solid(x + 1, y);
    const south = y < 8 && !solid(x, y + 1);
    const face = south || y === 8;
    px('#2d3030', 0, 0, 32, 32);
    dust(px, x + y * 9, ['#333434', '#383838', '#292d2d'], 42);
    if (y === 0) px('#5b574c', 0, 0, 32);
    if (x === 0) px('#58554b', 0, 0, 1, 32);
    if (x === 8) px('#202322', 31, 0, 1, 32);
    if (west) {
      px('#303a37', 0, 0, 4, 32);
      px('#69746a', 0, 0, 1, 32);
    }
    if (east) {
      px('#222726', 28, 0, 4, 32);
      px('#505a50', 28, 0, 1, 32);
    }
    if (!face) return;
    const left = west ? 4 : 0;
    const right = east ? 28 : 32;
    px('#514f46', left, 17, right - left, 11);
    px('#767467', left, 17, right - left);
    px('#626155', left, 18, right - left, 7);
    px('#3d5c55', left, 25, right - left, 4);
    px('#729388', left, 25, right - left);
    px('#252827', left, 29, right - left, 3);
    if (!east && x < 8) px('#45483f', 31, 18, 1, 7);
    const chip = left + (noise(x,y,4) % (right - left - 3));
    px('#454a41', chip, 22, 3);
    px('#55574c', chip + 1, 23, 2);
  };

  const floor = (px, x, y) => {
    const shades = ['#494740','#4b4942','#4d4b45','#4a4841'];
    px(shades[noise(x, y, 11) % shades.length], 0, 0, 32, 32);
    dust(px, x + y * 9, ['#4f4d46', '#45433e', '#545148', '#43413a'], 64);
    // Battered tiles, with staggered seams so the grid isn't overly uniform.
    const seam = y % 2 === 0 ? 21 : 8;
    px('#403f3a', 0, 17, 32);
    px('#4e4b44', 0, 18, 32);
    px('#403f3a', seam, 0, 1, 17);
    px('#403f3a', 31 - seam, 18, 1, 14);
    if (x <= 4 && y === 3) {
      px('#34352f', 0, 0, 32, 2);
      px('#af9859', 0, 2, 32, 2);
      for (let i = 2; i < 32; i += 4) px('#675c41', i, 3, 2);
    }
  };

  const track = (px, x, y) => {
    px('#2f302b', 0, 0, 32, 32);
    dust(px, x + y * 9, ['#414138','#3a3b33','#272924','#474439'], 100);
    const upper = y === 1;
    for (const left of [5, 19]) {
      const top = upper ? 16 : 0;
      px('#282824', left, top, 8, 16);
      px('#544738', left + 1, top, 6, 16);
      px('#695a45', left + 2, top, 1, 16);
      px('#3e372d', left + 6, top, 1, 16);
    }
    const rail = upper ? 22 : 9;
    px('#242624', 0, rail, 32, 5);
    px('#7b7e75', 0, rail + 1, 32, 2);
    px('#b1ada0', 0, rail + 1, 32);
    for (const left of [5, 19]) px('#767262', left + 1, rail + 3, 5);
    if (x === 4) {
      px('#292522', 27, rail - 2, 5, 9);
      px('#886044', 28, rail - 1, 4, 6);
      px('#b9925a', 29, rail - 1, 2, 5);
    }
  };

  const drawDoor = (px, kind, open) => {
    if (kind === 'entry') {
      if (art.entry) return art.entry(px, open);
      px('#222927', 0, 0, 32, 5);
      px('#45645b', 0, 1, 32, 2);
      px('#9bb4a1', 4, 3, 24);
      for (const x of [0, 27]) {
        px('#283733', x, 5, 5, 24);
        px('#81988c', x + 1, 6, 2, 22);
      }
      px('#69695a', 3, 29, 26, 2);
      px('#303a35', 3, 30, 26);
      if (open) return;
      px('#262d2a', 5, 5, 22, 24);
      for (const x of [6, 17]) {
        px('#576e63', x, 6, 9, 22);
        px('#293e39', x + 1, 8, 7, 10);
        px('#5f8b81', x + 1, 9, 7, 6);
        px('#96b7a8', x + 2, 9, 5);
        px('#8da497', x + 1, 23, 7);
      }
      return;
    }
    if (kind === 'staff') {
      px('#272b28', 8, 0, 16, 5);
      px('#272b28', 8, 27, 16, 5);
      px('#a0957b', 11, 4, 10);
      px('#786d5a', 11, 27, 10);
      if (open) {
        px('#5e5b51', 14, 5, 4, 22);
        px('#343832', 15, 6, 2, 20);
        return;
      }
      px('#272825', 10, 5, 13, 22);
      px('#766953', 11, 6, 10, 20);
      px('#9b8a70', 11, 7, 2, 18);
      px('#384540', 14, 8, 6, 6);
      px('#6b8373', 14, 9, 6);
      px('#c0ac86', 15, 18, 4, 2);
      return;
    }
    for (const x of [1, 25]) {
      px('#252e2a', x, 9, 6, 17);
      px('#61786e', x, 9, 6, 3);
      px('#76958a', x + 1, 12, 2, 12);
      px(open ? '#a6ca96' : '#be8063', x + 2, 10, 3);
    }
    if (open) {
      px('#8fa696', 7, 10, 1, 8);
      px('#8fa696', 24, 10, 1, 8);
      return;
    }
    px('#28312c', 7, 15, 18, 5);
    px('#68897e', 7, 15, 18, 2);
    for (let x = 9; x < 24; x += 4) px('#aac0ae', x, 15, 2);
  };

  const departures = px => {
    px('#212926', 4, 17, 56, 12);
    px('#648477', 4, 17, 56);
    px('#3f5a4f', 4, 27, 56, 2);
    for (const [i, color] of ['#9ab9b2', '#bf817f', '#ada0c6', '#c7a66e'].entries()) {
      const x = 9 + i * 13;
      px(color, x, 20, 2);
      px(color, x + 4, 20, 2);
      px(color, x + 1, 22, 4, 2);
      px('#7d8067', x, 25, 7);
    }
  };

  const sign = (px, word, glyphs, x, y, color) => {
    for (const [i, letter] of [...word].entries()) {
      for (const [row, bits] of glyphs[letter].entries()) {
        for (const [col, bit] of [...bits].entries()) {
          if (bit === '1') px(color, x + i * 4 + col, y + row, 1);
        }
      }
    }
  };

  const objects = g => {
    tile(g, 1, 4, art.bench ?? (px => {
      px('#292720', 3, 24, 27, 5);
      px('#33332b', 5, 10, 22, 14);
      px('#846c52', 5, 10, 22, 2);
      px('#695541', 5, 13, 22, 2);
      px('#524736', 5, 16, 22, 2);
      px('#99815c', 4, 20, 24, 3);
      px('#61503b', 4, 23, 24, 2);
      for (const x of [5, 24]) px('#606254', x, 24, 2, 4);
    }));
    tile(g, 7, 5, art.kiosk ?? (px => {
      px('#272923', 6, 28, 23, 3);
      px('#252f2d', 7, 4, 19, 25);
      px('#52746a', 8, 5, 17, 23);
      px('#85a497', 8, 5, 16, 2);
      px('#364d44', 22, 7, 3, 20);
      px('#253f3a', 10, 9, 11, 8);
      px('#78aa96', 11, 10, 9, 4);
      px('#c1cfad', 12, 11, 4);
      px('#cdb784', 12, 20, 2, 2);
      px('#273731', 15, 21, 6, 2);
      px('#a39169', 10, 26, 7);
    }));
    tile(g, 6, 0, art.staffBoard ?? (px => {
      // Staff-room key hooks and the old noticeboard are painted inside the wall.
      px('#2e2e28', 5, 17, 22, 12);
      px('#79684e', 6, 18, 20, 10);
      px('#a89876', 8, 19, 6, 7);
      px('#b7a17b', 17, 20, 2, 4);
      px('#b7a17b', 21, 21, 2, 4);
      px('#625747', 9, 21, 4);
    }));
    if (!art.facade) tile(g, 7, 8, px => {
      px('#2a3530', 2, 16, 28, 11);
      px('#6f8b7c', 2, 16, 28);
      px('#455b50', 2, 26, 28);
      sign(px, 'GAMERS', {
        G: ['111','100','101','101','111'],
        A: ['010','101','111','101','101'],
        M: ['101','111','101','101','101'],
        E: ['111','100','110','100','111'],
        R: ['110','101','110','101','101'],
        S: ['111','100','111','001','111'],
      }, 4, 19, '#b9c7ae');
    });
    tile(g, 1, 3, px => {
      px('#554d3b', 9, 7, 8, 9);
      sign(px, '1', { 1: ['010','110','010','010','111'] }, 11, 9, '#b19a65');
    });
    g.save();
    g.translate(64, 0);
    paint(g, departures);
    g.restore();
    art.facade?.(g, tile);
    if (art.signal) tile(g, 1, 0, art.signal);
  };

  window.holoxSecurityDoor = {
    source: '../holox-floor55/',
    install(layout, vault) {
      const { x, y } = layout.origin;
      const at = (tx, ty) => vault.rows[ty]?.[tx];
      layout.blockedChars.push('T');
      for (const [dy, row] of vault.rows.entries()) {
        const mapRow = layout.map.rows[y + dy];
        layout.map.rows[y + dy] = mapRow.slice(0, x) + row + mapRow.slice(x + vault.width);
        for (const [dx, cell] of [...row].entries()) {
          tile(surface, dx, dy, px => {
            if (cell === '#') wall(px, at, dx, dy);
            else if (cell === 'T') track(px, dx, dy);
            else floor(px, dx, dy);
          });
        }
      }
      objects(surface);
      return { x: x + 6, y: y + 8 };
    },
    draw() {}, // All three doors share the overlay below.
    drawInterior(g, origin, opened) {
      for (const [key, door] of Object.entries(doors)) {
        const [x,y] = key.split(',').map(Number);
        const worldX = origin.x + x;
        const worldY = origin.y + y;
        tile(g, worldX, worldY, px => drawDoor(px, door.kind, opened.has(worldX + ',' + worldY)));
      }
    },
  };
  const LabMaterials = {
    draw(g, origin) { g.drawImage(stationTiles, origin.x * 32, origin.y * 32); },
  };
  window.LabMaterials = LabMaterials;
})();
