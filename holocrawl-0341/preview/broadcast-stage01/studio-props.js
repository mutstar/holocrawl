function createStudioProps() {
  function prop(name, width, height, draw) {
    const tile = document.createElement('canvas');
    tile.width = width * 32;
    tile.height = height * 32;
    const ctx = tile.getContext('2d');
    const paint = (color, x, y, w, h) => {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, w, h);
    };
    draw(paint);
    return {name, width, height, tile};
  }

  function recess(paint, width) {
    paint('#172028', 1, 5, width - 2, 26);
    paint('#63767d', 2, 5, width - 4, 2);
    paint('#34454e', 2, 7, 4, 22);
    paint('#34454e', width - 6, 7, 4, 22);
    paint('#59656b', 3, 29, width - 6, 2);
  }

  const wall = [
    prop('매립형 믹싱 콘솔', 4, 1, p => {
      recess(p, 128);
      p('#384550', 8, 9, 112, 17);
      p('#53616b', 9, 24, 110, 3);
      for (let x = 12; x < 114; x += 7) {
        p('#172229', x, 12, 2, 10);
        p('#8b9c9d', x - 1, 15 + (x % 5), 4, 2);
        p(x % 3 ? '#77a999' : '#c38d56', x, 10, 2, 1);
      }
      p('#282e33', 51, 7, 27, 7);
      for (const x of [55, 60, 65, 70]) p('#8bbdaa', x, 9, 2, 3);
    }),
    prop('패치 패널과 연결선', 3, 1, p => {
      recess(p, 96);
      p('#42515a', 8, 9, 80, 16);
      for (let x = 11; x < 87; x += 6) {
        p('#17222a', x, 12, 3, 2);
        p('#17222a', x, 19, 3, 2);
      }
      for (const [x, end, color] of [[18, 37, '#ae7760'], [30, 58, '#7faaa5'], [48, 73, '#b89a5e']]) {
        p(color, x, 13, 2, 10);
        p(color, x + 1, 22, end - x, 2);
        p(color, end, 19, 2, 5);
      }
    }),
    prop('인이어·무선 마이크 충전 선반', 3, 1, p => {
      recess(p, 96);
      p('#38434b', 8, 9, 80, 16);
      p('#77756a', 8, 25, 80, 2);
      for (const x of [13, 23, 33, 43, 53]) {
        p('#20252b', x, 13, 7, 11);
        p('#78868b', x + 2, 10, 3, 4);
        p('#899893', x + 1, 11, 5, 2);
        p('#7caf92', x + 2, 22, 3, 1);
      }
      for (const x of [67, 77]) {
        p('#252c33', x, 13, 8, 11);
        p('#a4a097', x + 1, 15, 6, 2);
        p('#b48254', x + 3, 21, 2, 1);
      }
    }),
    prop('리허설 카운트다운 패널', 2, 1, p => {
      recess(p, 64);
      p('#362829', 9, 9, 46, 15);
      const segments = [[0,0,5,1],[4,1,1,4],[4,6,1,4],[0,10,5,1],[0,6,1,4],[0,1,1,4],[0,5,5,1]];
      for (const [i, digit] of [[0, '012345'], [1, '012345'], [2, '02356'], [3, '01346']]) {
        const x = 15 + i * 8 + (i >= 2 ? 4 : 0);
        for (const segment of digit) {
          const [dx, dy, w, h] = segments[Number(segment)];
          p('#d37e69', x + dx, 11 + dy, w, h);
        }
      }
      for (const y of [14, 18]) p('#d37e69', 31, y, 1, 1);
    }),
  ];

  const ground = [
    prop('붐 마이크와 바닥 모니터', 2, 1, p => {
      p('#202529', 3, 27, 55, 3);
      p('#252b31', 8, 25, 19, 3);
      p('#778388', 17, 11, 2, 15);
      p('#a1a69d', 19, 9, 11, 2);
      p('#6a787d', 29, 7, 5, 2);
      p('#202831', 33, 6, 6, 4);
      p('#778287', 35, 6, 4, 1);
      p('#262d34', 39, 20, 19, 8);
      p('#505f67', 42, 17, 13, 3);
      p('#405059', 40, 20, 17, 4);
      p('#1c262d', 42, 21, 13, 2);
    }),
    prop('대본 보면대', 1, 1, p => {
      p('#22282c', 6, 28, 20, 2);
      p('#303941', 8, 26, 16, 2);
      p('#889195', 15, 14, 2, 13);
      p('#303c45', 6, 6, 21, 10);
      p('#b9b5a2', 9, 6, 15, 8);
      p('#918a79', 16, 7, 1, 6);
      for (const y of [8, 10, 12]) {
        p('#686d66', 10, y, 5, 1);
        p('#79796c', 18, y, 5, 1);
      }
      p('#77838a', 7, 15, 19, 1);
    }),
    prop('보컬 흡음 파티션', 2, 1, p => {
      p('#25292e', 4, 26, 56, 3);
      for (const [x, y] of [[5, 6], [23, 3], [41, 6]]) {
        p('#29323b', x, y, 17, 20);
        p('#67657d', x + 1, y, 15, 2);
        p('#454459', x + 2, y + 3, 13, 14);
        for (let row = y + 5; row < y + 17; row += 3) p('#5c5970', x + 3, row, 11, 1);
        p('#777a80', x + 3, y + 18, 11, 1);
      }
    }),
    prop('출연자 위치 테이프', 1, 1, p => {
      p('#c7a46f', 8, 9, 7, 2);
      p('#c7a46f', 8, 9, 2, 7);
      p('#95b3a5', 19, 22, 7, 2);
      p('#95b3a5', 24, 17, 2, 7);
      p('#e5c99e', 8, 9, 5, 1);
      p('#bed0bd', 22, 22, 4, 1);
    }),
  ];
  return {wall, ground};
}
