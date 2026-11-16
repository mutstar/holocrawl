function buildEndingLayout({width, depth, entrance, design, ...info}) {
  const rows = Array.from({length: depth}, () => Array(width).fill(' '));
  const rectangle = (x, y, w, h, tile = '.') => {
    for (let dy = 0; dy < h; dy++) rows[y + dy].fill(tile, x, x + w);
  };
  const marks = (tile, coordinates) => {
    for (const [x, y] of coordinates) {
      if (tile === 'p') {
        if (!'.='.includes(rows[y][x]) || !'.='.includes(rows[y][x + 1])) {
          throw Error(`${info.id}: fixture does not fit at ${x},${y}`);
        }
        rows[y][x + 1] = 'P';
      }
      rows[y][x] = tile;
    }
  };
  design(rectangle, marks);
  const layout = rows.map((row, y) => row.map((tile, x) => {
    if (tile !== ' ') return tile;
    return [-1, 0, 1].some(dy => [-1, 0, 1].some(dx => {
      const near = rows[y + dy]?.[x + dx];
      return near && near !== ' ' && near !== '#';
    })) ? '#' : ' ';
  }).join(''));
  const entry = {x: entrance, y: depth - 1};
  layout[entry.y] = layout[entry.y].slice(0, entrance) + 'e' + layout[entry.y].slice(entrance + 1);
  return {...info, layout, width, depth, entry, wallFixtures: endingWallFixtures(layout)};
}

function endingWallFixtures(layout) {
  const stations = [];
  const positions = [];
  for (const [y, row] of layout.entries()) for (let x = 0; x < row.length - 1; x++) {
    if (row[x] === 'p') stations.push({x, y});
    if (y < layout.length - 4 && row.slice(x, x + 2) === '##'
        && !/[^.=]/.test(layout[y + 1].slice(x, x + 2))) positions.push({x, y});
  }
  const distance = (a, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));
  const pieces = [];
  while (pieces.length < Math.min(7, stations.length + 2)) {
    let best;
    for (const position of positions) {
      const gap = pieces.length ? Math.min(...pieces.map(piece => distance(position, piece))) : 8;
      if (gap < 6) continue;
      const nearestStation = Math.min(...stations.map(station => distance(position, station)));
      const rank = Math.min(gap, 12) * 2 - Math.abs(nearestStation - 3) * 2;
      if (!best || rank > best.rank) best = {...position, rank};
    }
    if (!best) break;
    pieces.push(best);
  }
  return pieces;
}

const stageEndings = [
  {
    id: 'flood', name: '침수된 송출 설비실', width: 36, depth: 26, entrance: 18,
    feature: '방수 전실 → 끊어진 점검 발판 → 송출 제어실',
    palette: ['#314655', '#547280', '#253946', '#50a4a9'],
    design(rect, mark) {
      rect(9, 1, 18, 6);
      rect(1, 7, 34, 13, '~');
      rect(3, 6, 3, 14, '=');
      rect(29, 6, 4, 14, '=');
      rect(4, 9, 28, 2, '=');
      rect(5, 16, 27, 2, '=');
      rect(14, 17, 8, 6, '=');
      rect(11, 21, 14, 4);
      rect(12, 6, 3, 4, '=');
      rect(22, 5, 3, 6, '=');
      rect(14, 3, 7, 1, '#');
      rect(7, 12, 4, 2, '~');
      mark('o', [[10,2],[25,2],[10,5],[25,5],[12,22],[23,22]]);
      mark('p', [[11,3],[22,3],[3,13],[30,11],[14,22]]);
      mark('s', [[16,9]]);
      mark('r', [[18,2]]);
    },
  },
  {
    id: 'street', name: '철거 중인 거리 세트', width: 42, depth: 24, entrance: 21,
    feature: '촬영 장비 반입로 → 가짜 상가 골목 → 간판 창고',
    palette: ['#5d4c3f', '#866e57', '#42352d', '#c38b59'],
    design(rect, mark) {
      rect(4, 2, 12, 7);
      rect(26, 1, 12, 7);
      rect(18, 5, 6, 8);
      rect(1, 9, 40, 5);
      rect(5, 14, 8, 6, '=');
      rect(16, 14, 14, 6);
      rect(33, 13, 7, 7);
      rect(8, 19, 29, 2, '=');
      rect(18, 20, 7, 3);
      rect(6, 6, 3, 4);
      rect(30, 7, 4, 4);
      rect(18, 15, 3, 3, '#');
      rect(25, 16, 3, 1, '#');
      rect(6, 10, 28, 1, '=');
      mark('o', [[6,3],[10,4],[14,7],[28,3],[35,4],[18,9],[13,12],[36,12],[8,16],[23,17],[32,19],[37,16]]);
      mark('p', [[7,6],[31,3],[19,6],[3,11],[23,12],[34,18],[18,21]]);
      mark('s', [[27,11]]);
      mark('r', [[36,2]]);
    },
  },
  {
    id: 'factory', name: '무대 세트 조립실', width: 25, depth: 45, entrance: 13,
    feature: '긴 반입로를 따라 가공실·조립실·검수실을 차례로 통과',
    palette: ['#414b4a', '#617071', '#333b3e', '#b29b54'],
    design(rect, mark) {
      rect(5, 1, 16, 7);
      rect(16, 7, 4, 5, '=');
      rect(1, 11, 22, 9);
      rect(3, 13, 16, 2, '=');
      rect(4, 18, 5, 8, '=');
      rect(3, 24, 21, 9);
      rect(8, 26, 13, 2, '=');
      rect(11, 30, 11, 1, '#');
      rect(16, 32, 5, 5, '=');
      rect(6, 36, 16, 8);
      rect(11, 39, 5, 5, '=');
      mark('o', [[7,2],[19,2],[4,13],[11,13],[17,13],[5,17],[20,18],[7,26],[12,26],[18,26],[7,37],[20,39]]);
      mark('p', [[8,5],[16,4],[7,16],[17,16],[8,25],[18,28],[7,40],[17,41]]);
      mark('s', [[6,22]]);
      mark('r', [[13,2]]);
    },
  },
  {
    id: 'horror', name: '공포 특수촬영실', width: 34, depth: 26, entrance: 28,
    feature: '분장 대기실 → 암전 복도 → 특수촬영 메인 세트',
    palette: ['#493745', '#74526a', '#332836', '#af5c6e'],
    design(rect, mark) {
      rect(12, 1, 18, 7);
      rect(14, 6, 5, 4);
      rect(1, 9, 22, 4, '=');
      rect(1, 12, 5, 7);
      rect(5, 15, 19, 4);
      rect(9, 18, 6, 5);
      rect(21, 17, 12, 5, '=');
      rect(24, 21, 9, 4);
      rect(16, 4, 9, 1, '=');
      rect(21, 15, 3, 2, '#');
      rect(10, 20, 3, 1, '#');
      mark('o', [[13,2],[28,2],[16,6],[25,5],[3,10],[9,10],[4,15],[8,16],[12,22],[17,16],[26,18],[31,20],[25,23],[31,23]]);
      mark('p', [[15,3],[23,3],[4,11],[3,17],[16,17],[25,19],[27,23]]);
      mark('s', [[14,9]]);
      mark('r', [[22,2]]);
    },
  },
  {
    id: 'tower', name: '송신 안테나 정비실', width: 21, depth: 45, entrance: 14,
    feature: '세로로 긴 정비 발판과 중간 중계실을 지나 송신부로',
    palette: ['#383f57', '#5e688b', '#262d3f', '#c16c86'],
    design(rect, mark) {
      rect(4, 1, 15, 7);
      rect(13, 7, 4, 8, '=');
      rect(1, 13, 12, 6);
      rect(8, 13, 9, 3, '=');
      rect(5, 18, 4, 8, '=');
      rect(5, 24, 11, 3, '=');
      rect(12, 26, 8, 6);
      rect(15, 31, 3, 7, '=');
      rect(7, 36, 12, 8);
      rect(12, 39, 4, 5, '=');
      rect(7, 5, 5, 1, '#');
      mark('o', [[5,2],[17,2],[8,4],[10,15],[2,14],[19,30],[18,28],[9,38],[17,40]]);
      mark('p', [[13,4],[5,6],[2,16],[16,27],[8,41],[16,37]]);
      mark('s', [[6,22]]);
      mark('r', [[11,2]]);
    },
  },
  {
    id: 'garden', name: '식생 촬영실', width: 38, depth: 28, entrance: 19,
    feature: '화단 반입 구간 → 두 온실 사이 순환로 → 종자 보관실',
    palette: ['#3b4d3d', '#61836e', '#263e35', '#9aaa64'],
    design(rect, mark) {
      rect(11, 1, 16, 6);
      rect(1, 7, 36, 15);
      rect(6, 21, 12, 4);
      rect(20, 21, 12, 4);
      rect(15, 23, 9, 4);
      rect(15, 6, 8, 3, '=');
      rect(3, 9, 32, 2, '=');
      rect(3, 19, 32, 2, '=');
      rect(3, 10, 2, 10, '=');
      rect(33, 10, 2, 10, '=');
      rect(17, 10, 4, 11, '=');
      rect(8, 13, 6, 2, '#');
      rect(24, 13, 6, 2, '#');
      for (const x of [7,10,13,24,27,30]) mark('o', [[x,11],[x,16],[x,17]]);
      mark('o', [[13,2],[25,2],[9,23],[28,23]]);
      mark('p', [[12,5],[22,4],[6,12],[27,12],[10,18],[28,18],[10,22],[25,23]]);
      mark('s', [[18,14]]);
      mark('r', [[19,2]]);
    },
  },
  {
    id: 'archive', name: '필름 보존고', width: 18, depth: 36, entrance: 9,
    feature: '좁고 긴 선반 열을 돌아 검수실과 보존실을 연결',
    palette: ['#584a43', '#857059', '#3f3934', '#d29a61'],
    design(rect, mark) {
      rect(3, 1, 12, 6);
      rect(7, 6, 4, 3);
      rect(1, 8, 16, 20);
      rect(5, 27, 9, 8);
      rect(7, 31, 4, 4, '=');
      for (const y of [11, 16, 21, 26]) {
        const start = y === 11 || y === 21 ? 1 : 5;
        rect(start, y, 12, 1, '#');
        for (let x = start + 1; x < start + 12; x += 3) mark('o', [[x, y - 1]]);
      }
      mark('o', [[4,2],[13,2],[6,29],[12,32]]);
      mark('p', [[6,3],[11,4],[2,12],[13,17],[3,22],[10,29]]);
      mark('s', [[13,13]]);
      mark('r', [[9,2]]);
    },
  },
  {
    id: 'mirror', name: '거울 분장실', width: 26, depth: 25, entrance: 18,
    feature: '대기실 → 서로 어긋난 분장실 두 곳 → 의상실',
    palette: ['#534961', '#806982', '#3c344d', '#bc9bba'],
    design(rect, mark) {
      rect(3, 1, 13, 6);
      rect(10, 6, 6, 4, '=');
      rect(13, 8, 12, 7);
      rect(11, 11, 4, 6, '=');
      rect(1, 15, 15, 6);
      rect(12, 19, 9, 2, '=');
      rect(15, 21, 9, 3);
      rect(17, 11, 5, 1, '#');
      rect(5, 17, 6, 1, '#');
      mark('o', [[4,2],[14,2],[6,4],[4,16],[9,16],[2,19],[23,9],[18,9],[23,13],[17,14],[16,22],[22,22]]);
      mark('p', [[7,3],[12,4],[20,9],[17,13],[4,19],[7,16],[18,22]]);
      mark('s', [[14,13]]);
      mark('r', [[9,2]]);
    },
  },
  {
    id: 'rail', name: '모형 철도 촬영장', width: 44, depth: 30, entrance: 22,
    feature: '정비 측선 → 대형 순환 선로 → 중앙 촬영 역사',
    palette: ['#504e39', '#776e55', '#35362d', '#b4875b'],
    design(rect, mark) {
      rect(6, 1, 32, 4);
      rect(3, 4, 38, 4);
      rect(1, 7, 42, 15);
      rect(3, 21, 38, 4);
      rect(8, 24, 28, 3);
      rect(17, 26, 11, 3);
      rect(5, 4, 34, 1, '=');
      rect(5, 5, 1, 17, '=');
      rect(38, 5, 1, 17, '=');
      rect(5, 22, 34, 1, '=');
      rect(10, 8, 24, 1, '#');
      rect(10, 9, 1, 11, '#');
      rect(33, 9, 1, 11, '#');
      rect(10, 19, 24, 1, '#');
      rect(20, 8, 4, 1);
      rect(31, 19, 2, 1);
      rect(15, 12, 14, 1, '=');
      rect(11, 25, 6, 1, '=');
      mark('o', [[8,10],[35,10],[8,17],[35,17],[13,11],[30,11],[13,17],[30,17],[13,24],[15,24],[26,26]]);
      mark('p', [[7,7],[34,7],[15,10],[25,10],[14,16],[26,17],[18,25],[26,24],[35,20]]);
      mark('s', [[23,15]]);
      mark('r', [[18,15]]);
    },
  },
  {
    id: 'power', name: '비상 발전실', width: 33, depth: 21, entrance: 16,
    feature: '차단기 전실 → 두 발전기 열 → 비상 전력 제어실',
    palette: ['#514940', '#77674e', '#38332f', '#bea05d'],
    design(rect, mark) {
      rect(8, 1, 17, 5);
      rect(13, 5, 7, 3);
      rect(1, 8, 31, 8);
      rect(5, 15, 8, 3);
      rect(20, 15, 8, 3);
      rect(12, 16, 9, 4);
      rect(3, 10, 9, 3, '=');
      rect(21, 10, 9, 3, '=');
      rect(13, 10, 7, 1, '#');
      rect(14, 15, 5, 3, '=');
      for (const x of [4,7,10,22,25,28]) mark('o', [[x,10],[x,12]]);
      mark('o', [[9,2],[23,2],[6,16],[26,16],[13,18],[19,18]]);
      mark('p', [[10,3],[21,4],[5,11],[24,11],[8,15],[21,16],[14,17]]);
      mark('s', [[16,13]]);
      mark('r', [[16,2]]);
    },
  },
].map(buildEndingLayout);
