(() => {
  const sites = {
    mountain: { title: '0기생 페이스 마운틴', hint: '북쪽 암벽에 새겨진 다섯 부조를 보러 올라가세요.', floor: ['#4a5340', '#4e5844', '#505945', '#48523f'], wall: ['#343631', '#555449', '#7c7563'] },
    dining: { title: '1기생 타라후쿠 저니', hint: '식탁 사이를 지나 배식대 가운데 주방문을 여세요.', floor: ['#5b4942', '#4d403b', '#594740', '#4b3f3a'], wall: ['#342c2c', '#68473e', '#9e7255'], door: [4, 3], doorLabel: '주방문' },
    market: { title: '5기생 네포라보 마트', hint: '계산대 옆으로 들어가 진열대 뒤편을 둘러보세요.', floor: ['#47524d', '#515d54', '#4b5650', '#546057'], wall: ['#2d3534', '#465b50', '#7a9180'] },
    dev: { title: 'DEV_IS 쵸베리바 출장소', hint: '출입 게이트를 열고 라이브 스테이지와 양옆 설비를 둘러보세요.', floor: ['#333541', '#393b49', '#353748', '#3c3b4a'], wall: ['#20232f', '#40374e', '#8c6792'], door: [5, 6], doorLabel: '출입 게이트' },
  };
  const requested = new URLSearchParams(location.search).get('site');
  const key = Object.hasOwn(sites, requested) ? requested : 'mountain';
  const site = sites[key];
  document.title = site.title + ' · 잔향도시';
  document.getElementById('siteTitle').textContent = site.title;
  document.getElementById('siteHint').textContent = site.hint;
  document.querySelector(`[data-site="${key}"]`).setAttribute('aria-current', 'page');
  const dataLink = document.getElementById('dataLink');
  dataLink.href = `${key}.json`;

  window.vaultTheme = {
    name: site.title,
    vaultFile: `./${key}.json`,
    defaultReward: 'weapon',
    assets: { weapon: '../theater-vault36/assets/reward-weapon.png' },
    startMessage: site.hint,
    walkMessage: site.title + '을 둘러보는 중입니다.',
    stairsMessage: '시작 계단에서 시설까지 탐험합니다.',
    showLabels: '구역 표시',
    hideLabels: '구역 숨기기',
    doorMessage: (x, y) => x === site.door?.[0] && y === site.door?.[1] ? site.doorLabel + '을 열었습니다.' : undefined,
    blockedMessage: tile => tile === 'G' ? '난간이 길을 막고 있습니다.' : undefined,
    inventory: ({ weapon = 0, scroll = 0, potion = 0 }) =>
      `획득  +2 숏소드 ${weapon}개 / 스크롤 ${scroll}장 / 포션 ${potion}개`,
  };

  const tile = 32;
  const mountainWallRow = 4;
  const art = document.createElement('canvas');
  const canvas = art.getContext('2d');
  const rect = (color, x, y, w, h = 1, context = canvas) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };
  const hash = (x, y) => {
    const seed = Math.imul(x + 41, 0x27d4eb2d) ^ Math.imul(y + 71, 0x165667b1);
    return Math.imul(seed ^ (seed >>> 16), 0x45d9f3b) >>> 0;
  };
  function texture(x, y, w, h, colors, count) {
    for (let i = 0; i < count; i++) {
      const seed = hash(x + i * 5, y + i);
      rect(colors[seed >>> 30], x + seed % w, y + ((seed >>> 8) % h), 1);
    }
  }

  function pavement(rows) {
    for (const [y, row] of rows.entries()) {
      for (const [x, cell] of [...row].entries()) {
        const px = x * tile;
        const py = y * tile;
        const [shadow, face, rim] = site.wall;
        const stoneBarrier = key === 'mountain' && y === mountainWallRow && x > 0 && x < row.length - 1;
        if (cell === '#' && !stoneBarrier) {
          rect(shadow, px, py, tile, tile);
          texture(px, py, tile, tile, [shadow, face, shadow, shadow], 35);
          if (y === 0 || y === 8 || rows[y + 1]?.[x] === '.') {
            rect(face, px, py + 17, 32, 11);
            rect(rim, px, py + 17, 32);
            rect(shadow, px, py + 28, 32, 4);
            rect(shadow, px + 25, py + 18, 1, 10);
          } else if (x === 0 || x === 8) {
            rect(face, px + (x === 0 ? 28 : 0), py, 4, 32);
          }
          continue;
        }
        rect(site.floor[hash(x, y) >>> 30], px, py, tile, tile);
        if (key === 'mountain') {
          texture(px, py, 32, 32, ['#444d3b', '#54604a', '#5b6149', '#3f4837'], 120);
          continue;
        }
        const stride = key === 'dining' ? 16 : key === 'market' ? 8 : 16;
        for (let dy = 0; dy < 32; dy += stride) {
          for (let dx = 0; dx < 32; dx += stride) {
            const tone = key === 'dev' ? hash(px + dx, py + dy) >>> 30 : ((x + y + (dx + dy) / stride) & 1);
            rect(site.floor[tone], px + dx, py + dy, stride, stride);
            rect(shadow, px + dx, py + dy, stride);
            rect(shadow, px + dx, py + dy, 1, stride);
          }
        }
      }
    }
  }

  function plaque(x, y, w, color, light) {
    rect('#28262b', x - 1, y - 1, w + 2, 11);
    rect(color, x, y, w, 9);
    rect(light, x + 2, y + 1, w - 4);
    for (let dx = 4; dx < w - 3; dx += 6) rect(light, x + dx, y + 4, 3, 2);
  }

  // Left to right as on the HoloDreams exhibit. Each relief has its own
  // silhouette, bangs and face, with a little mineral color in the stone.
  const mountainReliefs = [
    { // Sora: long side locks, star clips and a blouse with a blue tie.
      stone: ['#705344', '#9b735c', '#cbb090', '#74858b', '#e4ca87'],
      clothes: ['#8e8c82', '#b4ac98', '#d3c6ac', '#637884'],
      neck: '#aa8e72',
      pixels: [
        '.............b..',
        '.....hhhh...bb..',
        '...hhhhhhhhbb...',
        '..hhhllllhb.bb..',
        '..hhllhlhhbbbh..',
        '..hlhlhlahlhhh..',
        '..hlhfhahahllh..',
        '..hlffaffffllh..',
        '..hlfeffefhlhh..',
        '..hlffffffhlhh..',
        '..hlffffsfhlhh..',
        '..hlhfsfsfhlhh..',
        '..hlhffffhllhh..',
        '..hllhnfnhllhh..',
        '.shlhsnfnhhlhh..',
        '.shlhttntthlhhs.',
        '.chlvtmmtkvhlhs.',
        'chlhvvtmvvvhlhs.',
        'cshlvkvmvkkhlhss',
        'csllvkvmmvkhhcss',
        'cshvvkvmmvkvscsd',
        'csskvkvmmvkvkcsd',
        'cscskvkvvkvkcsdd',
        'sscsskkvvkkcssdd',
        'dsscsssssscssddd',
        'rddsssssssssdddr',
        'rrdddsssssdddrrr'
      ]
    },
    { // Roboco: short bob, round glasses and a hoodie with drawstrings.
      stone: ['#70535a', '#ad7e88', '#cfb7a7', '#a87581', '#c6aaa0'],
      clothes: ['#80646b', '#a77d86', '#bb989b', '#d1b6a2'],
      neck: '#ac9084',
      glasses: true,
      pixels: [
        '................',
        '.....hhhhhh.....',
        '....hllhllhh....',
        '..aaalhllhhaa...',
        '..ahallhllhahaa.',
        '...ahhhlhhlaha..',
        '..hlhlhfhfhhlh..',
        '..hlfffffffhlh..',
        '..hlffffffflhh..',
        '..hlffffffflhh..',
        '..hlfffffffflh..',
        '..hlhfffffhlhh..',
        '...llhffnhlhh...',
        '....hlnfnbhh....',
        '....rtnfntrr....',
        '...rtkknkktrr...',
        '..rtvkkkkkvtrs..',
        '.rtvvtttttvvkss.',
        '.rvkvvmvmvvkvss.',
        'rvvkvvmvmvvkvssd',
        'rvvkvvmvmvvkvssd',
        'svvkvvmvmvvksrdd',
        'ssvkvvvvvvvkrsdd',
        'dsskkvvvvkkssddd',
        'ddsccrrsrrsssddd',
        'rddssssssssddrrr',
        'rrdddssssdddrrrr'
      ]
    },
    { // AZKi: long straight strands and a high collar with rose trim.
      stone: ['#554b4d', '#766666', '#c5af9d', '#af7479', '#cc8b8e'],
      clothes: ['#534b4e', '#6c5d60', '#ad8589', '#c59da1'],
      neck: '#a68d7e',
      pixels: [
        '.....hhhhhh.....',
        '....hhlllbhh....',
        '...hhlllhbahh...',
        '...hlhlhlbahl...',
        '..hlhlhhfhahlh..',
        '..hlhhffflahlh..',
        '..hlfeffefahlh..',
        '..hlffffffahlh..',
        '..hlffffslahlh..',
        '..hlhfsfsbahhh..',
        '..hlhffffbahhh..',
        '..hlhhnfnbhlhh..',
        '..hlhtnfnthlhh..',
        '.shlhvtntrhlhs..',
        '.shhhvkmkvhhhs..',
        '.shlhvktkvhlhhs.',
        '.chlvktmkvhlhhs.',
        'chllvkvtkvhlhsss',
        'chlhvvktvvhlhssd',
        'chlhvvktvvhhsssd',
        'csllkvktvkhssrdd',
        'csllkvkvvksssrdd',
        'ssslkkvvkksrdddd',
        'dsssrskksssddddd',
        'ddssssssssddrrrr',
        'rddssssssddrrrrr',
        'rrdddssdddrrrrrr'
      ]
    },
    { // Miko: looped ahoge, side blossom and a crossed shrine-maiden collar.
      stone: ['#856966', '#b38b86', '#d3b9a6', '#ad7779', '#d6a4a0'],
      clothes: ['#906562', '#b1a292', '#d3c2a9', '#a7736f'],
      neck: '#b39485',
      pixels: [
        '......aaa.......',
        '.....a...a......',
        '.....a..a.......',
        '....hhhhhhh.....',
        '...hllhlllhha...',
        '..hllhlhlhhabaa.',
        '..hlhlhflhlabaa.',
        '..hlhffflhhaah..',
        '..hlfeffefhlhh..',
        '..hlffffsfhlhh..',
        '...hlfffshlhh...',
        '...hlfsssflhh...',
        '...hllffslhh....',
        '..sbhhnfnhhbss..',
        '.sssbtnfntbssss.',
        '.ssbvtntvvbssrs.',
        'cssbvktkvvbcsrs.',
        'csskvvktkvvvcrsd',
        'crskvvvktkvvsrsd',
        'csskvvvvktkvssdd',
        'cssmvvvvvkkmsddd',
        'cssmvvvvvvvmsddd',
        'ssskmmmmmmksdddd',
        'dsssskkkksssdddd',
        'ddssssssssddrrrr',
        'rddssssssddrrrrr',
        'rrdddssdddrrrrrr'
      ]
    },
    { // Suisei: tilted beret, blue side ponytail and a uniform with gold buttons.
      stone: ['#61686b', '#849699', '#c7b6a0', '#78818b', '#d2bb84'],
      clothes: ['#596167', '#78858b', '#b1b8ad', '#c5ac7c'],
      neck: '#a3917d',
      pixels: [
        '........bbbb.h..',
        '......bbbbbblbh.',
        '.....bhhhhhhb...',
        '....hlllhlhlhb..',
        '...hlllhlhlhlh..',
        '...hlhhlhhfhlah.',
        '...hhfffhffhaah.',
        '...hfeffeffflh..',
        '...hlffffsflhh..',
        '...hlfffsffl.hh.',
        '....hlsssfh..lh.',
        '.....hffsh...lh.',
        '....ssnfnh...lh.',
        '..ssstnfntshlh..',
        '.ssssvtntvshhss.',
        '.rcsvvtktvhlhss.',
        '.rckvvtvtvhlhsss',
        'crrkvvktvvhlhssd',
        'crkvvvmvmvvhhssd',
        'crkvvvkvkvvsvsdd',
        'crskvvmvmvvkvsdd',
        'crsskvkvkvkssddd',
        'sssskvvvvksssddd',
        'dsssskkkkssddddd',
        'ddssssssssddrrrr',
        'rddssssssddrrrrr',
        'rrdddssdddrrrrrr'
      ]
    }
  ];

  function carveRelief(x, y, { stone, clothes, neck, pixels, glasses }) {
    const [hair, light, face, accent, gleam] = stone;
    const [clothShadow, cloth, seam, ornament] = clothes;
    const palette = {
      h: hair, l: light, f: face, b: accent, a: gleam,
      e: face, n: neck, s: '#95846e',
      c: '#b29d83', r: '#887761', d: '#766956',
      k: clothShadow, v: cloth, t: seam, m: ornament
    };
    for (const [row, line] of pixels.entries()) {
      for (const [col, mark] of [...line].entries()) {
        if (mark !== '.') rect('#51483c', x + col * 2 + 1, y + row * 2 + 1, 2, 2);
      }
    }
    for (const [row, line] of pixels.entries()) {
      for (const [col, mark] of [...line].entries()) {
        if (mark === '.') continue;
        const px = x + col * 2;
        const py = y + row * 2;
        rect(palette[mark], px, py, 2, 2);
        if (mark === 'f' && !'fen'.includes(line[col - 1])) rect('#d8c2a2', px, py, 1);
      }
    }
    // Incised lids read as narrow marks on the stone, with no bright pupils.
    for (const [row, line] of pixels.entries()) {
      for (const [col, mark] of [...line].entries()) {
        if (mark !== 'e') continue;
        const px = x + col * 2;
        const py = y + row * 2;
        rect('#75614f', px, py, 3);
        rect('#594b3e', px + 1, py + 1, 2);
      }
    }
    if (glasses) {
      const frame = '#735760';
      rect(frame, x + 14, y + 16, 3);
      for (const left of [8, 16]) {
        rect(frame, x + left + 1, y + 14, 5, 6);
        rect(frame, x + left, y + 15, 7, 4);
        rect(face, x + left + 1, y + 15, 5, 4);
        rect('#59473f', x + left + 2, y + 16, 3);
        rect('#59473f', x + left + 3, y + 17, 2);
      }
    }
  }

  function mountainTrail(rows) {
    // [row, centre, half-width] from the overlook to the south entrance.
    const bends = [
      [66, 141, 2], [76, 139, 17], [96, 154, 15],
      [126, 208, 14], [155, 208, 14], [189, 142, 15],
      [220, 141, 14], [253, 208, 14], [288, 208, 13]
    ];
    for (let i = 1; i < bends.length; i++) {
      const [top, from, narrow] = bends[i - 1];
      const [bottom, to, wide] = bends[i];
      for (let y = top; y < bottom; y++) {
        const t = (y - top) / (bottom - top);
        const centre = from + (to - from) * t * t * (3 - 2 * t);
        const radius = narrow + (wide - narrow) * t;
        for (let x = Math.floor(centre - radius - 5); x <= centre + radius + 5; x++) {
          if (rows[Math.floor(y / tile)][Math.floor(x / tile)] !== '.') continue;
          const side = x < centre ? -1 : 1;
          const roughness = (hash(side * 71, Math.floor(y / 3)) % 5) - 2;
          const edge = radius + roughness - Math.abs(x - centre);
          const grain = hash(x, y) % 100;
          if (edge < 0 && (edge < -3 || grain > 23)) continue;
          const earth = edge < 2 ? '#666047' : edge < 5 ? '#706148' : '#7c6a50';
          const speck = grain < 7 ? '#8c795b' : grain < 16 ? '#6a5b45' : earth;
          rect(speck, x, y, 1);
        }
      }
    }
  }

  function mountainBarrier(row) {
    const y = mountainWallRow * tile;
    const gap = row.indexOf('.');
    for (const [start, end] of [[tile, gap * tile], [(gap + 1) * tile, (row.length - 1) * tile]]) {
      for (let x = start; x < end; x++) {
        const segment = Math.floor((x - start) / 13);
        const tip = Math.min(x - start, end - 1 - x);
        const crest = 4 + [0, 3, 1, 4, 2, 0, 2][segment % 7] + Math.max(0, 3 - tip);
        const toe = 26 + [0, 2, 1, 0, 3][Math.floor((x - start) / 7) % 5];
        const face = ['#7a6e5b', '#837661', '#786f60', '#726755'][segment % 4];
        rect('#414536', x, y + crest + 1, 1, toe - crest + 2);
        rect('#585044', x, y + crest, 1, toe - crest);
        rect(face, x, y + crest + 1, 1, toe - crest - 5);
        rect('#958671', x, y + crest + 1, 1, 2);
        if (hash(x, y) % 3 === 0) rect('#a09077', x, y + crest + 4 + hash(x, 1) % 5, 1);
      }
      texture(start + 1, y + 13, end - start - 2, 10, ['#6b6050', '#897b65', '#7a6e5b', '#998970'], Math.floor((end - start) * 0.9));
      for (let x = start + 11; x < end - 5; x += 19 + hash(x, y) % 13) {
        const split = y + 12 + hash(x, 2) % 4;
        rect('#665948', x, split, 2, 4);
        rect('#615747', x + 2, split + 3, 2, 4);
        rect('#514a3d', x + 3, split + 6, 1, 3);
      }
    }
  }

  function faceMountain(rows) {
    mountainTrail(rows);
    mountainBarrier(rows[mountainWallRow]);
    // The upper ridge spans the wall. The five busts share a second row of
    // rock, with a walkable path to either side and in front of their feet.
    rect('#3c3e36', 0, 0, 288, 32);
    for (let x = 0; x < 288; x++) {
      const ridge = 6 + [0, 1, 2, 1, 0, -1, -2, -1][Math.floor(x / 9) % 8];
      const foot = 29 + [0, 1, 1, 0, -1, -1][Math.floor(x / 11) % 6];
      const tone = ['#746a58', '#796f5d', '#766c59', '#716756'][Math.floor(x / 17) % 4];
      rect('#91836a', x, ridge, 1, 2);
      rect(tone, x, ridge + 2, 1, foot - ridge - 2);
      rect('#4b473d', x, foot, 1, 2);
    }
    texture(2, 9, 284, 18, ['#817661', '#796e5b', '#685e4f', '#766e5c'], 510);
    for (const [x, y, length] of [[14, 17, 19], [36, 23, 21], [105, 10, 8], [171, 25, 9], [230, 14, 21], [253, 23, 17]]) {
      rect('#62594b', x, y, length);
      rect('#82745e', x + 2, y + 1, length - 4);
    }

    for (let x = 2 * tile; x < 7 * tile; x++) {
      const left = x - 2 * tile;
      const foot = 58 + [0, 1, 3, 2, 2, 0, 1, 3][Math.floor(left / 5) % 8];
      const tone = ['#766956', '#7e705c', '#82745e', '#796c59'][Math.floor(left / 11) % 4];
      rect('#4b473d', x, 31, 1, tile + 1);
      rect(tone, x, 29, 1, foot - 29);
      rect('#665b4b', x, foot, 1, 2);
    }
    mountainReliefs.forEach((relief, i) => carveRelief((i + 2) * tile, 1, relief));
    texture(2 * tile + 2, 46, 5 * tile - 4, 10, ['#84735e', '#9b886f', '#786956', '#93806a'], 150);
    for (const [x, y, w] of [[68, 55, 16], [83, 56, 19], [109, 57, 16], [133, 54, 10], [144, 55, 15], [175, 56, 23], [205, 55, 15]]) {
      rect('#97846d', x, y, w);
      rect('#746754', x + 1, y + 1, w);
    }
    rect('#6a533d', 109, 233, 3, 19);
    plaque(100, 229, 22, '#6c5141', '#b89b75');
  }

  function table(x, y) {
    rect('#332b2a', x + 2, y + 4, 28, 55);
    rect('#976e53', x + 3, y + 4, 26, 49);
    rect('#b18865', x + 3, y + 4, 26, 2);
    rect('#824b46', x + 10, y + 6, 12, 48);
    rect('#b1665d', x + 10, y + 6, 2, 48);
    for (const [dx, dy] of [[6, 11], [20, 39]]) {
      rect('#665448', x + dx, y + dy, 7, 6);
      rect('#d9ccb3', x + dx + 1, y + dy + 1, 5, 4);
      rect('#a68b74', x + dx + 2, y + dy + 2, 3, 2);
    }
    rect('#513934', x + 5, y + 53, 22, 4);
  }

  function diningKeepsakes() {
    const props = [
      { // Akirose's vase of red roses.
        x: 71, y: 174,
        colors: { k: '#3e3d36', v: '#608279', g: '#9cb29b', d: '#45615a', r: '#b74456', h: '#f0888b', b: '#873e48', l: '#809252', s: '#536e48' },
        pixels: [
          '.......rr........',
          '......rhhrr......',
          '..rr..rhbrb......',
          '.rhrr..rrb..rr...',
          '.rhrb..sb..rhrr..',
          '..rb..ls...rrrb..',
          '..sl..ss..lsrb...',
          '...sll.s.lss.....',
          '....sslslss......',
          '.....slsss.......',
          '......gggd.......',
          '......gvvd.......',
          '......gvvd.......',
          '.....gvvvvd......',
          '....gvvvvvvd.....',
          '...ggvvvvvvvd....',
          '...gvvvvvvvdd....',
          '...gvvvvvvddd....',
          '....vvvvvddd.....',
          '.....dddddd......',
          '.....kkkkkk......'
        ]
      },
      { // Haachama's ramen with a spider on top.
        x: 100, y: 91,
        colors: { k: '#593735', p: '#a95c50', w: '#e3bda1', n: '#edc07c', s: '#a96d40', d: '#37292c', c: '#725149', r: '#a94746', h: '#d37665', v: '#b3977d' },
        pixels: [
          '.......v.....v........',
          '........v...v.........',
          '....wwwwwwwwwwww......',
          '..wwssssssssssssww....',
          '.wssndnnnnnnndnsssw...',
          'wsnnndsdnsndsdnnsnsw..',
          'wsnsnnddnsnddnnsnnsw..',
          'wsnndnsddcddnndnsnsw..',
          'wsnsndddcdddddnsnnsw..',
          'wsnsdnnndddnsndnsnsw..',
          '.wwnnndnsdndnsnnnww...',
          '.rwwwwwwwwwwwwwwwr....',
          '..rhhrrrrrrrrrrrr.....',
          '...rhhrrrrrrrrrr......',
          '....prrrrrrrrpp.......',
          '.....ppppppppp........',
          '......kkkkkkk.........'
        ]
      },
      { // Fubuki's white fox teapot, blue lid and a curved handle.
        x: 165, y: 178,
        colors: { k: '#53433b', w: '#eee0c9', f: '#c4c4b6', b: '#769f9e', c: '#a4c3bc', d: '#3c525a' },
        pixels: [
          '.....w......w.........',
          '....wwf....fww........',
          '....wwf....fww........',
          '....wwwccccwww........',
          '.....cbbbbbbcf.kkk....',
          '...wfffffffffkkfwfk...',
          '..wwwwwwwwwwwwk...k...',
          '.wwwwdwwwwdwwwk...k...',
          'wwfwwdwwwwdwwwk..fk...',
          '.ffwwwwddwwwwwkkkf....',
          '...fwcwwwwcwwf........',
          '....ffccccfff.........',
          '.....fbbbbbf..........',
          '......kkkkk...........'
        ]
      },
      { // Matsuri's Ebifrion serving plate.
        x: 196, y: 93,
        colors: { k: '#694737', p: '#c5a58b', w: '#e6cbb0', o: '#b96431', g: '#e89f48', f: '#f2c374', d: '#694439', r: '#b94c3d' },
        pixels: [
          '.....gg..gg.......r.r.',
          '....ggg..ggg.....rrrr.',
          '....ooggggoo.....rrr..',
          '...oogffffgoog...rr...',
          '...ogffffffgoggggr....',
          '..wogfddfdfgoggggo....',
          '.wwogffffffgogggoow...',
          'pwwogffddffgoggooowp..',
          'pwwwooggggoooggoowwp..',
          'pwwwwwooooogggoowwwp..',
          '.ppwwwwwoooooowwwpp...',
          '..ppppwwwwwwwwpppp....',
          '.....pppppppppp.......',
          '......kkkkkkkk........'
        ]
      }
    ];
    for (const { x, y, colors, pixels } of props) {
      for (const [dy, line] of pixels.entries()) {
        for (const [dx, ink] of [...line].entries()) {
          if (ink !== '.') rect(colors[ink], x + dx, y + dy, 1);
        }
      }
    }
  }

  function diningRoom(rows) {
    plaque(112, 18, 64, '#7f4743', '#e0b58f');
    for (let x = 1; x <= 7; x++) {
      if (rows[3][x] === '+') continue;
      const left = x * tile;
      rect('#553b36', left, 107, 32, 21);
      rect('#ba8b64', left, 107, 32, 3);
      rect('#7c5048', left + 2, 111, 28, 12);
      rect('#a56459', left + 3, 111, 26);
      rect('#603e39', left + 15, 112, 1, 10);
    }
    for (const x of [41, 68, 178, 238]) {
      rect('#624c42', x, 101, 16, 7);
      rect('#c8b49b', x + 1, 100, 14, 4);
      rect('#ad795c', x + 5, 100, 6, 2);
    }
    for (const [x, y] of [[1, 1], [1, 2], [4, 1], [5, 1]]) {
      const left = x * tile;
      const top = y * tile;
      rect('#423936', left + 2, top + 5, 29, 24);
      rect('#8c8170', left + 3, top + 6, 26, 20);
      rect('#afa594', left + 3, top + 6, 26, 2);
      rect('#4d4540', left + 7, top + 10, 18, 9);
      rect('#6c6960', left + 8, top + 11, 16, 2);
      rect('#cfa181', left + 10, top + 22, 10);
    }
    table(64, 160);
    table(160, 160);
    diningKeepsakes();
  }

  const marketProducts = {
    lamy(paint) {
      paint('#2b393d', 3, 3, 26, 56);
      paint('#506b70', 4, 3, 24, 52);
      paint('#8ba8a9', 4, 3, 24, 2);
      paint('#344d59', 7, 7, 18, 30);
      paint('#51727e', 8, 8, 2, 25);
      paint('#adc8c6', 24, 19, 2, 8);
      paint('#7d9896', 7, 36, 18, 2);
      for (const y of [45, 48, 51]) paint('#354a4a', 9, y, 14);

      paint('#a5c9d8', 13, 8, 6, 3);
      paint('#467c99', 13, 11, 6, 6);
      paint('#689db5', 12, 16, 8, 2);
      paint('#467c99', 11, 18, 10, 13);
      paint('#8fbdcc', 12, 18, 2, 11);
      paint('#d5e5df', 12, 21, 8, 7);
      paint('#5788a0', 13, 24, 6);
      paint('#5788a0', 15, 22, 2, 5);
      paint('#2b5366', 12, 31, 8);
    },

    nene(paint) {
      paint('#3f342c', 4, 5, 55, 23);
      paint('#99744e', 5, 5, 53, 19);
      paint('#584635', 8, 7, 47, 14);
      paint('#746044', 9, 8, 23, 12);
      paint('#866f50', 11, 9, 18);
      paint('#b08a5d', 5, 23, 53, 3);
      paint('#d1aa78', 6, 23, 51);
      paint('#e2c095', 17, 24, 10);

      paint('#edc193', 35, 7, 17, 2);
      paint('#c96d4f', 35, 9, 17, 3);
      paint('#e68d58', 36, 12, 15, 7);
      paint('#b55f45', 37, 19, 13, 2);
      paint('#ffe0ab', 38, 13, 11, 5);
      paint('#e88d73', 41, 14, 5, 3);
      paint('#f2aa86', 41, 14, 2);
      paint('#8a995e', 44, 12, 3, 2);
    },

    botan(paint) {
      paint('#303b34', 3, 4, 26, 54);
      paint('#6c7d68', 4, 4, 24, 48);
      paint('#9fa78e', 4, 4, 24, 2);
      paint('#39493f', 6, 7, 20, 25);
      paint('#546458', 6, 34, 20, 16);
      paint('#899785', 6, 32, 20, 2);
      paint('#37473d', 8, 39, 16, 7);
      paint('#a3a28a', 13, 40, 6);

      paint('#d2ccb4', 8, 10, 16, 3);
      paint('#ede1c3', 9, 9, 14, 2);
      paint('#526d52', 9, 13, 14, 9);
      paint('#3b503f', 10, 22, 12, 4);
      paint('#8b9f73', 10, 14, 12, 8);
      paint('#dddccd', 12, 15, 8, 6);
      paint('#eee6d0', 11, 14, 3, 3);
      paint('#eee6d0', 18, 14, 3, 3);
      paint('#4c5349', 13, 17, 1);
      paint('#4c5349', 18, 17, 1);
      paint('#646357', 15, 19, 2);
      paint('#c9ba8b', 12, 23, 8);
    },

    polka(paint) {
      paint('#49363c', 3, 5, 26, 24);
      paint('#80565e', 4, 5, 24, 21);
      paint('#aa7373', 4, 5, 24, 2);
      paint('#594c55', 6, 8, 20, 13);
      paint('#bb935c', 4, 24, 24, 2);
      paint('#c0a473', 11, 26, 10);
      paint('#9b4f55', 9, 11, 14, 7);
      paint('#9b4f55', 11, 18, 10, 5);
      paint('#ddaa7e', 11, 12, 2, 6);
      paint('#e7b17f', 15, 12, 2, 10);
      paint('#d0a276', 19, 12, 2, 6);
      paint('#d8af73', 9, 10, 14, 2);
      for (const [x, y] of [[10, 8], [13, 6], [16, 7], [19, 6], [21, 8]]) {
        paint('#f0d6a4', x, y, 3, 3);
        paint('#fff0c8', x + 1, y, 2);
      }
    },
  };

  function marketCheckout(x, y) {
    const paint = (color, dx, dy, width, height = 1) => {
      rect(color, x + dx, y + dy, width, height);
    };
    paint('#2e3935', 1, 7, 94, 24);
    paint('#2e3935', 64, 28, 31, 32);
    paint('#43564e', 3, 5, 89, 22);
    paint('#43564e', 67, 26, 25, 30);
    paint('#9ba590', 3, 5, 89, 2);
    paint('#829484', 3, 7, 2, 19);
    paint('#829484', 67, 27, 2, 28);
    paint('#35453f', 90, 7, 2, 49);
    paint('#65796b', 5, 26, 62, 3);
    paint('#65796b', 69, 54, 21, 3);

    paint('#929787', 7, 9, 60, 14);
    paint('#3a4544', 8, 10, 58, 12);
    for (let dx = 10; dx < 66; dx += 4) paint('#53605b', dx, 11, 1, 10);
    paint('#b3b6a0', 8, 9, 58);

    paint('#31423e', 69, 12, 9, 9);
    paint('#84958b', 70, 12, 7, 6);
    paint('#38464a', 71, 13, 5, 4);
    paint('#d58572', 72, 14, 3);
    paint('#263637', 79, 8, 10, 15);
    paint('#465b58', 80, 9, 8, 8);
    paint('#90b5a5', 81, 10, 6, 4);
    paint('#b2c9b5', 81, 10, 4);
    for (const dx of [81, 84, 86]) paint('#a9a38f', dx, 19, 1, 2);

    paint('#35453f', 71, 29, 16, 21);
    paint('#758575', 72, 30, 14, 18);
    paint('#a6af99', 72, 30, 14);
    paint('#bbb08b', 76, 36, 7, 9);
    paint('#ddd0a4', 77, 36, 5);
    paint('#615f4c', 78, 37, 3);

    // Storage and a stool fill the enclosed staff nook.
    paint('#35443c', 6, 35, 24, 19);
    paint('#5b6c5e', 7, 35, 22, 14);
    paint('#879481', 7, 35, 22, 2);
    paint('#3f5147', 9, 44, 18, 4);
    paint('#b5ac8d', 15, 45, 6);
    paint('#303932', 45, 46, 12, 6);
    paint('#695747', 46, 44, 10, 6);
    paint('#ad8965', 47, 43, 8, 3);
    paint('#c4a17a', 48, 43, 6);
    for (const dx of [102, 109, 116]) paint('#a99f7d', dx, 50, 4, 2);
  }

  function market(_rows, stations) {
    plaque(105, 18, 78, '#4a6a5c', '#d4bf8e');
    rect('#303e38', 131, 36, 26, 92);
    rect('#61776a', 132, 36, 24, 88);
    rect('#8c9d87', 132, 36, 24, 2);
    rect('#41564b', 135, 40, 18, 81);
    for (const y of [58, 78, 99, 120]) {
      rect('#a6aa90', 134, y, 20);
      rect('#5a6959', 135, y + 1, 18, 2);
    }
    for (const [x, y, width, height, color] of [
      [136, 47, 6, 11, '#7d8c7a'], [144, 49, 7, 9, '#a09174'],
      [137, 69, 13, 9, '#8a8172'], [140, 89, 10, 10, '#718980'],
      [136, 111, 7, 9, '#8f9b82'], [145, 115, 6, 5, '#9e896f'],
    ]) {
      rect(color, x, y, width, height);
      rect('#b5b09b', x + 1, y + 1, width - 2);
    }
    for (const { id, x, y } of stations) {
      if (id === 'register') {
        marketCheckout(x * tile, y * tile);
        continue;
      }
      const product = marketProducts[id];
      if (product) product((color, dx, dy, width, height = 1) => {
        rect(color, x * tile + dx, y * tile + dy, width, height);
      });
    }
  }

  function liveStage(x, y) {
    const paint = (color, dx, dy, w, h = 1) => rect(color, x + dx, y + dy, w, h);
    paint('#20222d', 0, 1, 128, 63);
    paint('#373242', 3, 5, 122, 52);
    paint('#494052', 3, 32, 122, 23);
    for (const offset of [10, 34, 58, 82, 106]) {
      paint('#403747', offset, 34, 1, 20);
    }
    paint('#242732', 3, 54, 122, 8);
    paint('#716078', 3, 54, 122);
    paint('#aa5786', 12, 57, 104, 2);
    paint('#de91ba', 15, 57, 98);

    paint('#70617b', 5, 5, 118, 2);
    for (const offset of [20, 46, 75, 101]) {
      paint('#24242f', offset, 7, 7, 5);
      paint(offset < 64 ? '#ce83ac' : '#88bac5', offset + 1, 9, 5, 2);
    }
    paint('#161d29', 19, 13, 90, 24);
    paint('#6d5374', 20, 13, 88);
    paint('#262e42', 21, 15, 86, 19);
    paint('#43415a', 24, 24, 80);
    const signal = [2, 3, 2, 6, 11, 7, 3, 8, 5, 10, 6, 3, 6, 4, 2, 3];
    for (const [index, height] of signal.entries()) {
      const color = index < 8 ? '#bb648f' : '#6ba4b7';
      paint(color, 26 + index * 5, 25 - Math.floor(height / 2), 3, height);
    }

    for (const offset of [5, 110]) {
      paint('#20222e', offset, 24, 13, 27);
      paint('#5d586c', offset + 1, 25, 11, 2);
      paint('#3d3c50', offset + 2, 29, 9, 18);
      paint('#1d212d', offset + 3, 30, 7, 6);
      paint('#1d212d', offset + 3, 39, 7, 6);
      paint('#716a83', offset + 5, 32, 3, 2);
      paint('#716a83', offset + 5, 41, 3, 2);
    }
    for (const offset of [52, 74]) {
      paint('#25252f', offset - 4, 48, 9, 2);
      paint('#b7a5b6', offset, 40, 1, 9);
      paint('#cbbcce', offset - 1, 39, 3, 2);
    }
  }

  function recordingDesk(x, y) {
    const paint = (color, dx, dy, w, h = 1) => rect(color, x + dx, y + dy, w, h);
    paint('#20232e', 1, 4, 62, 27);
    paint('#545267', 3, 5, 58, 20);
    paint('#7c7790', 3, 5, 58);
    for (const offset of [7, 25]) {
      paint('#202734', offset, 2, 14, 11);
      paint('#426071', offset + 2, 4, 10, 6);
      paint('#94bec9', offset + 3, 7, 8);
    }
    paint('#292b38', 6, 15, 35, 8);
    for (const offset of [9, 15, 21, 27, 33]) {
      paint('#77778a', offset, 16, 1, 6);
      paint('#d5bfce', offset - 1, 17 + (offset % 4), 3);
    }
    paint('#2a2c3a', 45, 8, 12, 15);
    paint('#87af9f', 47, 14, 2, 6);
    paint('#c18aa7', 51, 11, 2, 9);
    paint('#353645', 4, 25, 56, 3);
  }

  function ventRig(x, y) {
    const paint = (color, dx, dy, w, h = 1) => rect(color, x + dx, y + dy, w, h);
    paint('#20232f', 2, 4, 60, 26);
    paint('#36374b', 4, 5, 56, 22);
    paint('#61546f', 4, 5, 56);
    paint('#1f2230', 39, 8, 17, 15);
    for (const row of [10, 13, 16, 19]) paint('#665c77', 41, row, 13);
    for (const offset of [6, 20]) {
      paint('#282739', offset, 7, 8, 17);
      paint('#4e4667', offset + 1, 7, 6, 16);
      paint('#71618d', offset + 2, 8, 1, 13);
      paint('#4e4667', offset + 5, 19, 11, 5);
      paint('#847397', offset, 11, 8, 2);
      paint('#686282', offset + 7, 19, 8);
    }
    paint('#be779e', 35, 11, 2, 2);
    paint('#7daab9', 35, 17, 2, 2);
  }

  const reglossProps = {
    kanade(paint) {
      paint('#252631', 3, 23, 26, 4);
      paint('#646474', 7, 17, 3, 8);
      paint('#646474', 22, 17, 3, 8);
      paint('#38343c', 2, 9, 28, 13);
      paint('#b99747', 3, 10, 26, 10);
      paint('#e1c778', 3, 10, 26);
      paint('#f0e4ce', 4, 13, 24, 6);
      for (const x of [7, 11, 15, 19, 23, 27]) paint('#8b8276', x, 14, 1, 5);
      for (const x of [6, 10, 14, 18, 22, 26]) paint('#343039', x, 13, 2, 3);
      paint('#4d463f', 11, 4, 10, 6);
      paint('#e4d7b5', 12, 4, 8, 5);
      paint('#a39476', 16, 4, 1, 5);
      paint('#fae4a2', 25, 5, 3);
      paint('#fae4a2', 26, 4, 1, 3);
    },

    ririka(paint) {
      paint('#29202d', 2, 11, 28, 20);
      paint('#713a57', 3, 15, 26, 14);
      paint('#bd6388', 3, 13, 26, 5);
      paint('#f2adca', 4, 13, 24);
      paint('#4b314d', 5, 2, 22, 11);
      paint('#92608c', 6, 3, 20);
      paint('#322743', 7, 4, 18, 8);
      for (const [x, y, width] of [[8, 8, 4], [13, 6, 5], [19, 7, 4]]) {
        paint('#64446d', x, y, width, 12 - y);
        paint('#f0bfac', x + 1, y + 1, 2);
      }
      paint('#dc96c0', 21, 5, 2);
      paint('#f7dbbd', 6, 14, 7, 3);
      paint('#5a2d48', 22, 14, 4, 3);
      paint('#2b2130', 4, 18, 24, 11);
      paint('#eb96bc', 4, 18, 24);
      const letters = ['111/100/100/100/111', '111/100/110/100/111', '111/101/101/101/111'];
      for (const [index, letter] of letters.entries()) {
        for (const [y, row] of letter.split('/').entries()) {
          for (const [x, pixel] of [...row].entries()) {
            if (pixel === '1') paint('#ffdf9e', 5 + index * 8 + x * 2, 19 + y * 2, 2, 2);
          }
        }
      }
    },

    raden(paint) {
      paint('#192926', 3, 8, 26, 22);
      paint('#356f5e', 4, 6, 24, 20);
      paint('#5da78e', 6, 5, 20, 2);
      paint('#24483e', 6, 8, 20, 16);
      paint('#234035', 5, 25, 22, 4);
      paint('#79b6a1', 6, 25, 20);
      paint('#a7d1b5', 7, 10, 2, 2);
      paint('#b894bd', 23, 14, 2, 2);
      paint('#d1c493', 7, 21, 2, 2);

      // Raden's mask as shown on the official hololive friends to Go product.
      const hair = '#292933';
      const porcelain = '#e7e0d4';
      paint(hair, 12, 1, 8, 1);
      paint(hair, 9, 2, 14, 2);
      paint(hair, 7, 4, 18, 3);
      paint(hair, 6, 7, 20, 13);
      paint('#d1c6b9', 8, 18, 16, 4);
      paint('#d1c6b9', 10, 22, 12, 2);
      paint('#d1c6b9', 12, 24, 8, 1);
      paint('#bdb2a9', 14, 25, 4, 1);

      // A center part and two curved hair lines hug the high forehead.
      paint('#676571', 10, 3, 5, 1);
      paint('#676571', 17, 3, 5, 1);
      paint('#676571', 8, 5, 3, 2);
      paint('#676571', 21, 5, 3, 2);
      paint('#676571', 7, 7, 1, 8);
      paint('#676571', 24, 7, 1, 8);
      paint(porcelain, 15, 3, 2, 1);
      paint(porcelain, 12, 4, 8, 1);
      paint(porcelain, 10, 5, 12, 2);
      paint(porcelain, 8, 7, 16, 12);
      paint(porcelain, 9, 19, 14, 2);
      paint(porcelain, 11, 21, 10, 2);
      paint('#d9cfc3', 13, 23, 6, 1);

      // Small high brows, curved upper lids, and fastening cords at eye level.
      paint('#96938c', 10, 7, 4, 1);
      paint('#96938c', 11, 6, 3, 1);
      paint('#96938c', 18, 7, 4, 1);
      paint('#96938c', 18, 6, 3, 1);
      for (const x of [10, 18]) {
        paint('#5d5760', x + 1, 12, 3, 1);
        paint(hair, x, 13, 5, 1);
        paint(hair, x + 2, 14, 1, 1);
      }
      paint(hair, 4, 14, 4, 1);
      paint(hair, 24, 14, 4, 1);
      paint('#b1a699', 14, 17, 1, 1);
      paint('#b1a699', 17, 17, 1, 1);
      paint('#963f48', 13, 19, 6, 1);
      paint('#582d38', 14, 20, 4, 1);
      paint('#963f48', 15, 21, 2, 1);
    },

    hajime(paint) {
      paint('#282736', 3, 16, 26, 13);
      paint('#514769', 4, 17, 24, 10);
      paint('#9380b5', 4, 17, 24);
      paint('#c4b1e4', 8, 21, 4, 2);
      paint('#c4b1e4', 7, 23, 4, 2);
      paint('#d7b777', 22, 19, 3, 2);
      paint('#d7b777', 21, 21, 4, 2);
      paint('#d7b777', 22, 23, 1, 2);

      paint('#242531', 12, 6, 9, 2);
      paint('#242531', 10, 8, 13, 11);
      paint('#242531', 8, 13, 17, 3);
      paint('#4d455c', 12, 7, 8, 2);
      paint('#e7dfd4', 12, 11, 9, 8);
      paint('#e7dfd4', 12, 10, 3, 1);
      paint('#e7dfd4', 18, 10, 3, 1);
      paint('#302c38', 13, 12, 1, 2);
      paint('#302c38', 19, 12, 1, 2);
      paint('#d39cae', 12, 15, 2);
      paint('#d39cae', 19, 15, 2);
      paint('#dfb273', 15, 14, 3, 2);
      paint('#bc9369', 11, 19, 4, 2);
      paint('#bc9369', 18, 19, 4, 2);
    },
  };

  function broadcast(rows, stations) {
    const furniture = { stage: liveStage, desk: recordingDesk, pipes: ventRig };
    for (const { id, x, y } of stations) {
      if (furniture[id]) {
        furniture[id](x * tile, y * tile);
      } else {
        reglossProps[id]?.((color, dx, dy, width, height = 1) => {
          rect(color, x * tile + dx, y * tile + dy, width, height);
        });
      }
    }

    for (const [column, cell] of [...rows[6]].entries()) {
      if (cell !== 'G') continue;
      const x = column * tile;
      rect('#262832', x, 206, 32, 7);
      rect('#645971', x, 206, 32, 2);
      rect('#4c4459', x + 6, 203, 3, 10);
      rect('#ab849f', x + 6, 203, 3, 2);
    }
  }

  const drawSites = { mountain: faceMountain, dining: diningRoom, market, dev: broadcast };
  window.holoxSecurityDoor = {
    source: '../holox-floor55/',
    install(layout, vault) {
      const { x, y } = layout.origin;
      for (const [dy, row] of vault.rows.entries()) {
        const original = layout.map.rows[y + dy];
        layout.map.rows[y + dy] = original.slice(0, x) + row + original.slice(x + vault.width);
      }
      art.width = vault.width * tile;
      art.height = vault.height * tile;
      pavement(vault.rows);
      drawSites[key](vault.rows, vault.stations);
      window.drawFacilityEntrance(canvas, vault.rows, key);
      return null;
    },
    drawInterior(context, origin, opened) {
      if (!site.door) return;
      const [dx, dy] = site.door;
      const x = (origin.x + dx) * tile;
      const y = (origin.y + dy) * tile;
      const open = opened.has(`${origin.x + dx},${origin.y + dy}`);
      const [shadow, face, rim] = site.wall;
      for (const left of [2, 27]) {
        rect(shadow, x + left, y + 7, 4, 22, context);
        rect(rim, x + left + 1, y + 7, 2, 2, context);
      }
      if (open) return;
      rect(shadow, x + 5, y + 8, 23, 20, context);
      rect(face, x + 6, y + 9, 21, 18, context);
      rect(rim, x + 7, y + 10, 19, 2, context);
      rect(shadow, x + 16, y + 10, 1, 17, context);
      rect('#cbb48b', x + 13, y + 18, 2, 2, context);
      rect('#cbb48b', x + 18, y + 18, 2, 2, context);
    },
  };
  window.LabMaterials = {
    draw(target, origin) {
      target.drawImage(art, origin.x * tile, origin.y * tile);
    },
  };
})();
