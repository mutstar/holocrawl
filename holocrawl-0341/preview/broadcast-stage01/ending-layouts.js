function buildEndingLayout({width, depth, entrance, design, ...info}) {
  const rows = Array.from({length: depth}, () => Array(width).fill(' '));
  const pathUnderMarks = new Set();
  const rectangle = (x, y, w, h, tile = '.') => {
    for (let dy = 0; dy < h; dy++) rows[y + dy].fill(tile, x, x + w);
  };
  const marks = (tile, coordinates) => {
    for (const [x, y] of coordinates) {
      if (tile === 'p') {
        if (!'.='.includes(rows[y][x]) || !'.='.includes(rows[y][x + 1])) {
          throw Error(`${info.id}: fixture does not fit at ${x},${y}`);
        }
        if (rows[y][x + 1] === '=') pathUnderMarks.add(y * width + x + 1);
        rows[y][x + 1] = 'P';
      }
      if (rows[y][x] === '=') pathUnderMarks.add(y * width + x);
      rows[y][x] = tile;
    }
  };
  design(rectangle, marks);
  for (const {x, y, width, depth} of info.scenery ?? []) {
    for (let row = y; row < y + depth; row++) {
      if (rows[row]?.slice(x, x + width).filter(tile => '.='.includes(tile)).length !== width) {
        throw Error(`${info.id}: scenery does not fit at ${x},${y}`);
      }
      if (info.id === 'rail') {
        for (let col = x; col < x + width; col++) {
          if (rows[row][col] === '=') pathUnderMarks.add(row * rows[row].length + col);
        }
      }
    }
    rectangle(x, y, width, depth, 'f');
  }
  const layout = rows.map((row, y) => row.map((tile, x) => {
    if (tile !== ' ') return tile;
    return [-1, 0, 1].some(dy => [-1, 0, 1].some(dx => {
      const near = rows[y + dy]?.[x + dx];
      return near && near !== ' ' && near !== '#';
    })) ? '#' : ' ';
  }).join(''));
  const entry = {x: entrance, y: depth - 1};
  layout[entry.y] = layout[entry.y].slice(0, entrance) + 'e' + layout[entry.y].slice(entrance + 1);
  return {...info, layout, width, depth, entry, pathUnderMarks, wallFixtures: endingWallFixtures(layout)};
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

const liveShowGateBanks = [
  {x: 5, y: 28, width: 3, depth: 1, turnstiles: [1]},
  {x: 11, y: 28, width: 4, depth: 1, turnstiles: [1, 3]},
  {x: 18, y: 28, width: 3, depth: 1, turnstiles: [0, 2]},
];
const liveSeatRows = [12, 14, 17, 19];
const liveHouseEntry = {x:12, y:20, width:2, depth:4};

// The two open ends of the cable trench line up with the grating on the main walk.
const towerCrossing = {x:10, y:9, width:9, depth:2, bridgeX:13, bridgeWidth:4};
const floodServiceBridge = {x:13, y:11, length:3};
// The plywood starts at the bakery's east jamb (x16) and ends at the store's west jamb (x26).
const streetBacklot = [
  {x:16,y:4,width:10,depth:3},
  {x:16,y:7,width:8,depth:2},
];

const stageEndings = [
  {
    id: 'flood', name: '침수된 송출 설비실', width: 36, depth: 26, entrance: 18,
    feature: '배수 밸브 옆 한 칸 점검교 또는 동쪽 케이블 정비로를 거쳐 송출 제어실로',
    palette: ['#314655', '#547280', '#253946', '#50a4a9'],
    floodedEquipment: [
      {kind: 'pump', x: 7, y: 7},
      {kind: 'rack', x: 16, y: 12},
      {kind: 'footing', x: 18, y: 7},
      {kind: 'footing', x: 21, y: 14},
      {kind: 'pipe', x: 8, y: 18},
      {kind: 'pump', x: 25, y: 18},
    ],
    design(rect, mark) {
      rect(9, 1, 18, 6);
      rect(1, 7, 34, 13, '~');
      rect(21, 5, 5, 2, '~');
      rect(3, 6, 3, 14, '=');
      rect(29, 6, 4, 14, '=');
      rect(4, 9, 28, 2, '=');
      rect(5, 16, 27, 2, '=');
      rect(14, 17, 8, 6, '=');
      rect(11, 21, 14, 4);
      rect(12, 7, 3, 3, '=');
      rect(22, 5, 3, 6, '=');
      rect(14, 3, 7, 1, '#');
      rect(8, 13, 4, 1, '=');
      rect(7, 14, 7, 2, '=');
      rect(floodServiceBridge.x, floodServiceBridge.y, 1, floodServiceBridge.length, '=');
      rect(25, 11, 3, 2, '=');
      rect(23, 12, 2, 2, '=');
      rect(25, 13, 2, 1, '=');
      // Join the cable landing to the east gallery at a second point.
      rect(26, 13, 5, 2, '=');
      mark('o', [[10,2],[25,2],[10,5],[25,4],[12,22],[23,22]]);
      mark('p', [[11,3],[22,3],[3,13],[8,13],[30,11],[14,22]]);
      mark('v', [[11,14]]);
      mark('k', [[24,13]]);
      mark('b', [[27,11],[13,23]]);
      mark('s', [[16,9]]);
      mark('r', [[18,2]]);
    },
  },
  {
    id: 'street', name: '철거 중인 거리 세트', width: 42, depth: 24, entrance: 21,
    feature: '카페 앞 큰길 또는 빵집 뒤 작업 골목을 지나 간판 창고로',
    palette: ['#5d4c3f', '#866e57', '#42352d', '#c38b59'],
    road: {x: 2, y: 10, width: 38, depth: 3, backlot:streetBacklot},
    scenery: [
      {kind: 'bakery', x: 5, y: 7, width: 8, depth: 2},
      {kind: 'stripped', x: 18, y: 7, width: 5, depth: 2},
      {kind: 'cafe', x: 31, y: 7, width: 6, depth: 2},
      {kind: 'signs', x: 28, y: 2, width: 4, depth: 2},
      {kind: 'lumber', x: 6, y: 15, width: 3, depth: 2},
      {kind: 'lift', x: 10, y: 16, width: 2, depth: 3},
      {kind: 'cases', x: 35, y: 15, width: 3, depth: 2},
      {kind: 'broken-camera', x: 19, y: 10, width: 2, depth: 1},
      {kind: 'fallen-light', x: 35, y: 17, width: 2, depth: 1},
      {kind: 'cable-reel', x: 7, y: 17, width: 1, depth: 1},
    ],
    design(rect, mark) {
      rect(4, 2, 12, 7);
      rect(26, 1, 12, 7);
      rect(18, 5, 6, 8);
      rect(1, 9, 40, 5);
      rect(5, 14, 8, 6);
      rect(16, 14, 14, 6);
      rect(33, 13, 7, 7);
      rect(8, 19, 29, 2);
      rect(18, 20, 7, 3);
      rect(6, 6, 3, 4);
      rect(27, 8, 11, 2);
      for (const lane of streetBacklot) rect(lane.x,lane.y,lane.width,lane.depth);
      rect(18, 15, 3, 3, '#');
      rect(25, 16, 3, 1, '#');
      mark('o', [[6,4],[14,7],[35,4],[23,17],[32,19]]);
      mark('p', [[7,4],[33,2],[34,18],[18,21]]);
      mark('s', [[27,11]]);
      mark('r', [[36,2]]);
    },
  },
  {
    id: 'live', name: '폐쇄된 공개방송 스튜디오', width: 25, depth: 45, entrance: 13,
    feature: '개찰구에서 무대로 이어지는 중앙 객석 통로와 왼쪽 측면 통로',
    palette: ['#484456', '#686273', '#352f3c', '#8ca9a5'],
    liveShow: {
      stage: {x: 6, y: 2, width: 14, depth: 4},
      steps: {x: 11, y: 6, width: 5, depth: 2},
      frontAisle: {x: 5, y: 8, width: 16, depth: 3},
      audience: {x: 1, y: 11, width: 22, depth: 10},
      houseEntry: liveHouseEntry, seatRows: liveSeatRows,
      lobby: {x: 6, y: 36, width: 16, depth: 8},
      aisles: [{x: 2, width: 1}, {x: 10, width: 4}, {x: 21, width: 1}],
      gateBanks: liveShowGateBanks,
    },
    scenery: [
      {kind: 'screen', x: 7, y: 1, width: 12, depth: 2},
      {kind: 'speakers', x: 6, y: 4, width: 2, depth: 1},
      {kind: 'speakers', x: 18, y: 4, width: 2, depth: 1},
      {kind: 'floor-light', x: 6, y: 9, width: 1, depth: 1},
      {kind: 'floor-light', x: 19, y: 9, width: 1, depth: 1},
      ...liveSeatRows.flatMap(y => [3, 14].map(x => ({kind: 'seats', x, y, width: 7, depth: 1}))),
      ...liveShowGateBanks.flatMap(({x, y, turnstiles}) => turnstiles.map(offset => (
        {kind: 'turnstile', x: x + offset, y, width: 1, depth: 1}
      ))),
      {kind: 'ticket-booth', x: 4, y: 26, width: 2, depth: 2},
      {kind: 'ticket-booth', x: 21, y: 27, width: 2, depth: 2},
      {kind: 'bench', x: 7, y: 37, width: 2, depth: 1},
      {kind: 'belt', x: 8, y: 42, width: 5, depth: 1},
      {kind: 'belt', x: 15, y: 42, width: 2, depth: 1},
      {kind: 'belt', x: 9, y: 40, width: 4, depth: 1},
      {kind: 'belt', x: 18, y: 40, width: 3, depth: 1},
      {kind: 'belt', x: 7, y: 38, width: 6, depth: 1},
      {kind: 'belt', x: 16, y: 38, width: 2, depth: 1},
    ],
    design(rect, mark) {
      rect(3, 1, 19, 7);
      rect(5, 8, 16, 4);
      rect(1, 11, 22, 10);
      rect(4, 18, 5, 8);
      rect(liveHouseEntry.x, liveHouseEntry.y, liveHouseEntry.width, liveHouseEntry.depth);
      rect(3, 24, 21, 9);
      rect(13, 32, 8, 5);
      rect(6, 36, 16, 8);
      mark('p', [[20,2],[19,18],[20,26]]);
      mark('s', [[6,22]]);
      mark('r', [[13,4]]);
    },
  },
  {
    id: 'office', name: '홀로그라 사무실', width: 24, depth: 18, entrance: 13,
    feature: '깨진 로고 창문에서 응접실로 직행하거나 회의실 옆 복도를 돌아 업무석으로',
    palette: ['#73695b', '#8d8977', '#484d49', '#73b8b7'],
    scenery: [
      {kind: 'window-left', x: 10, y: 12, width: 3, depth: 1},
      {kind: 'window-right', x: 15, y: 12, width: 2, depth: 1},
      {kind: 'sofa-left', x: 11, y: 8, width: 1, depth: 2},
      {kind: 'sofa-right', x: 16, y: 8, width: 1, depth: 2},
      {kind: 'tea-table', x: 14, y: 8, width: 1, depth: 1},
      {kind: 'fallen-chair', x: 16, y: 11, width: 1, depth: 1},
      {kind: 'conference', x: 3, y: 5, width: 2, depth: 3},
      {kind: 'whiteboard', x: 2, y: 2, width: 4, depth: 1},
      {kind: 'workstations', x: 10, y: 3, width: 4, depth: 2, snappedDesk: true},
      {kind: 'workstations', x: 16, y: 3, width: 4, depth: 2},
      {kind: 'yagoo-display', x: 14, y: 1, width: 2, depth: 1},
      {kind: 'files', x: 21, y: 7, width: 1, depth: 2},
      {kind: 'plant', x: 20, y: 3, width: 1, depth: 1},
      {kind: 'plant', x: 2, y: 9, width: 1, depth: 1},
    ],
    design(rect, mark) {
      rect(8, 2, 14, 10);
      rect(10, 1, 10, 1);
      rect(1, 2, 6, 8);
      rect(7, 5, 1, 2);
      // A second internal approach starts behind the sofa, enters the meeting
      // room at its foot and rejoins the office on the open side of the desks.
      rect(4, 10, 2, 1);
      rect(8, 12, 14, 1, '#');
      rect(10, 12, 7, 1);
      rect(9, 13, 12, 2);
      rect(4, 11, 6, 2);
      rect(9, 13, 1, 1, '#');
      rect(11, 15, 6, 2);
      mark('d', [[19,12]]);
      mark('s', [[13,9]]);
      mark('r', [[13,7]]);
    },
  },
  {
    id: 'tower', name: '송신 안테나 정비실', width: 21, depth: 45, entrance: 14,
    grates: [
      {x:towerCrossing.bridgeX, y:towerCrossing.y, width:towerCrossing.bridgeWidth, depth:towerCrossing.depth},
      {x:5, y:20, width:4, depth:2},
      {x:13, y:20, width:4, depth:2},
      {x:10, y:24, width:2, depth:3, across:true},
      {x:15, y:33, width:3, depth:1},
    ],
    feature: '비상 전원실에서 동쪽 케이블 점검로나 서쪽 중계실을 거쳐 접시 안테나로',
    palette: ['#383f57', '#5e688b', '#262d3f', '#c16c86'],
    floorCracks: [
      {x:8, y:39, kind:'corner'}, {x:10, y:41, kind:'seam', flip:true},
      {x:17, y:37, kind:'split'},
      {x:18, y:28, kind:'corner', flip:true}, {x:13, y:30, kind:'split'},
      {x:1, y:16, kind:'split'}, {x:6, y:16, kind:'corner'}, {x:10, y:17, kind:'seam'},
      {x:4, y:4, kind:'corner'}, {x:9, y:6, kind:'seam', flip:true},
      {x:17, y:4, kind:'split', flip:true},
    ],
    scenery: [
      {kind: 'bench', x: 8, y: 37, width: 3, depth: 2},
      {kind: 'reel', x: 8, y: 41, width: 2, depth: 1},
      {kind: 'tool-cart', x: 11, y: 38, width: 1, depth: 1},
      {kind: 'transformer', x: 17, y: 26, width: 3, depth: 2},
      {kind: 'breakers', x: 12, y: 29, width: 1, depth: 2},
      {kind: 'scope', x: 2, y: 13, width: 3, depth: 2},
      {kind: 'relay-racks', x: 2, y: 17, width: 3, depth: 1},
      {kind: 'dish', x: 5, y: 2, width: 5, depth: 3},
      {kind: 'feeder', x: 16, y: 2, width: 2, depth: 2},
      {kind: 'inspection-hatch', x: 2, y: 20, width: 3, depth: 2},
      {kind: 'feeder-trench', x:1, y:20, width:1, depth:2, wallEnd:'left'},
      {kind: 'feeder-trench', x:17, y:20, width:2, depth:2, wallEnd:'right'},
      {kind: 'feeder-trench', x: towerCrossing.x, y: towerCrossing.y,
        width: towerCrossing.bridgeX - towerCrossing.x, depth: towerCrossing.depth},
      {kind: 'feeder-trench', x: towerCrossing.bridgeX + towerCrossing.bridgeWidth, y: towerCrossing.y,
        width: towerCrossing.x + towerCrossing.width - towerCrossing.bridgeX - towerCrossing.bridgeWidth, depth: towerCrossing.depth},
    ],
    design(rect, mark) {
      rect(4, 1, 15, 7);
      rect(13, 7, 4, 8, '=');
      rect(towerCrossing.x, towerCrossing.y, towerCrossing.width, towerCrossing.depth, '=');
      rect(1, 13, 12, 6);
      rect(8, 13, 9, 3, '=');
      rect(5, 18, 4, 8, '=');
      rect(1, 18, 2, 4);
      rect(1, 20, 5, 4);
      rect(5, 20, 4, 2, '=');
      rect(2, 24, 4, 1);
      rect(5, 24, 11, 3, '=');
      rect(12, 26, 8, 6);
      // A two-tile service walk follows the transformer feed around the east
      // side of the relay room. The open cable bay ends flush with its mesh.
      rect(13, 21, 2, 4, '=');
      rect(13, 20, 6, 2, '=');
      rect(15, 15, 2, 6, '=');
      rect(15, 31, 3, 7, '=');
      rect(7, 36, 12, 8);
      rect(12, 39, 4, 5, '=');
      rect(7, 5, 5, 1, '#');
      mark('p', [[13,4]]);
      mark('s', [[6,22]]);
      mark('r', [[11,2]]);
    },
  },
  {
    id: 'garden', name: '식생 촬영실', width: 38, depth: 28, entrance: 19,
    feature: '온실 관수로와 이랑 사이 수레길을 잇는 횡단로 → 종자 보관실',
    palette: ['#3b4d3d', '#61836e', '#263e35', '#9aaa64'],
    dollyTrack: {x:18, y:11, width:2, depth:8, crossingY:13},
    scenery: [
      {kind:'glasshouse', x:6, y:10, width:8, depth:3},
      {kind:'glasshouse', x:8, y:14, width:8, depth:3},
      {kind:'glasshouse', x:5, y:18, width:8, depth:3},
      {kind:'water-tank', x:15, y:10, width:2, depth:2},
      {kind:'potting-bench', x:8, y:22, width:4, depth:2},
      {kind:'planting-rows', x:23, y:10, width:9, depth:3},
      {kind:'planting-rows', x:24, y:16, width:8, depth:3, flowering:true},
      {kind:'dolly-camera', x:18, y:16, width:2, depth:2},
      {kind:'wheelbarrow-spade', x:22, y:16, width:2, depth:2},
      {kind:'seed-drawers', x:12, y:2, width:4, depth:2},
      {kind:'seed-cabinet', x:23, y:2, width:3, depth:2},
      {kind:'plant-cart', x:13, y:22, width:3, depth:2},
    ],
    design(rect, mark) {
      rect(11, 1, 16, 6);
      rect(1, 7, 36, 15);
      rect(6, 21, 12, 4);
      rect(20, 21, 12, 4);
      rect(15, 23, 9, 4);
      // Open the receiving apron between the potting bench and the flower beds.
      rect(18, 21, 2, 3);
      // A delivery cart can reach the east side of the seed store from the
      // beds, even when the central camera aisle is occupied.
      rect(26, 3, 8, 2, '=');
      rect(32, 5, 2, 5, '=');
      rect(15, 6, 8, 3, '=');
      rect(3, 9, 32, 2, '=');
      rect(3, 19, 32, 2, '=');
      rect(3, 10, 2, 10, '=');
      rect(33, 10, 2, 10, '=');
      rect(17, 10, 4, 11, '=');
      // The west walk threads the existing gaps between the three houses.
      rect(6, 17, 12, 1, '=');
      rect(6, 13, 2, 4, '=');
      rect(4, 13, 30, 1, '=');
      rect(14, 10, 1, 3, '=');
      // Two walkable tiles between the beds, meeting the cart ramp outside.
      rect(21, 14, 13, 1, '=');
      rect(32, 10, 2, 5, '=');
      mark('p', [[12,5],[22,4],[25,23]]);
      mark('s', [[18,14]]);
      mark('r', [[19,2]]);
    },
  },
  {
    id: 'archive', name: '필름 보존고', width: 18, depth: 36, entrance: 9,
    feature: '쌍릴 검수대에서 선반 사이 점검 통로나 동쪽 필름 반입구를 거쳐 보존실로',
    palette: ['#584a43', '#857059', '#3f3934', '#d29a61'],
    scenery: [
      {kind:'film-rack', x:1, y:10, width:8, depth:2},
      {kind:'film-rack', x:10, y:10, width:4, depth:2},
      {kind:'film-cart', x:12, y:16, width:2, depth:1},
      {kind:'film-cabinets', x:2, y:15, width:7, depth:2},
      {kind:'film-rack', x:1, y:20, width:4, depth:2},
      {kind:'packing-table', x:5, y:21, width:4, depth:2},
      {kind:'reel-bin', x:4, y:25, width:4, depth:2, bank:0},
      {kind:'reel-bin', x:11, y:25, width:4, depth:2, bank:1},
      {kind:'inspection-bench', x:6, y:29, width:4, depth:2},
      {kind:'inspection-bench', x:4, y:2, width:4, depth:2},
      {kind:'film-rack', x:11, y:1, width:4, depth:2},
    ],
    design(rect, mark) {
      rect(3, 1, 12, 6);
      rect(7, 6, 4, 3);
      // A two-wide receiving passage turns into the store below its fixed rack.
      rect(13, 4, 4, 2);
      rect(15, 6, 2, 3);
      rect(1, 8, 16, 20);
      rect(5, 27, 9, 8);
      rect(7, 31, 4, 4, '=');
      mark('s', [[13,13]]);
      mark('r', [[9,2]]);
    },
  },
  {
    id: 'mirror', name: '거울 분장실', width: 26, depth: 25, entrance: 18,
    feature: '대기실 → 전구 거울 앞길 또는 의상 행거 통로 → 안쪽 의상실',
    palette: ['#534961', '#806982', '#3c344d', '#bc9bba'],
    scenery: [
      {kind:'costume-rail', x:2, y:9, width:3, depth:1},
      {kind:'broken-mannequin', x:6, y:10, width:1, depth:1},
      {kind:'broken-mannequin', pose:'reaching', x:22, y:13, width:1, depth:1},
      {kind:'broken-mannequin', pose:'seated', x:6, y:15, width:1, depth:1},
      {kind:'broken-mannequin', pose:'fallen', x:13, y:3, width:2, depth:1},
      {kind:'bulb-vanity', x:17, y:11, width:5, depth:2},
      {kind:'standing-mirror', x:2, y:15, width:2, depth:2},
    ],
    design(rect, mark) {
      rect(3, 1, 13, 6);
      rect(10, 6, 6, 4, '=');
      rect(13, 8, 12, 7);
      rect(11, 11, 4, 6, '=');
      rect(1, 15, 15, 6);
      rect(12, 19, 9, 2, '=');
      rect(15, 21, 9, 3);
      rect(18, 14, 2, 6);
      rect(4, 6, 2, 10);
      rect(2, 9, 6, 4);
      rect(17, 10, 5, 1, '#');
      rect(5, 17, 6, 1, '#');
      mark('o', [[4,2],[14,2],[6,4],[2,19],[23,9],[23,13],[16,22],[22,22]]);
      mark('p', [[7,3],[12,4],[20,9],[4,19],[7,16],[20,22]]);
      mark('s', [[14,13]]);
      mark('r', [[9,2]]);
    },
  },
  {
    id: 'rail', name: '홀로섭 공동 건설 현장', width: 44, depth: 30, entrance: 22,
    feature: '소라 트레인 순환선 · 홀로섭 랜드마크 여덟 곳과 다이아 장비고',
    palette: ['#504e39', '#776e55', '#35362d', '#b4875b'],
    scenery: [
      {kind:'minecart', x:18, y:12, width:1, depth:1},
      {kind:'ore-cart', x:22, y:12, width:1, depth:1},
      {kind:'rabbit-office', x:17, y:9, width:4, depth:2},
      {kind:'moon-workbench', x:24, y:9, width:3, depth:2},
      {kind:'carrot-beds', x:13, y:9, width:3, depth:2},
      {kind:'supply-chests', x:34, y:15, width:2, depth:1},
      {kind:'sora-station', x:16, y:23, width:4, depth:2},
      {kind:'diamond-rack', x:23, y:23, width:4, depth:2},
      {kind:'pekodam', x:28, y:10, width:3, depth:4},
      {kind:'aquamarine', x:7, y:1, width:7, depth:3},
      {kind:'sakura-tree', x:29, y:1, width:5, depth:3},
      {kind:'menya-botan', x:11, y:16, width:3, depth:2},
      {kind:'babel', x:6, y:12, width:3, depth:4},
      {kind:'pekoland', x:6, y:6, width:4, depth:3},
      {kind:'creeper', x:15, y:11, width:1, depth:1},
      {kind:'creeper', x:34, y:5, width:1, depth:1},
      {kind:'creeper', x:9, y:18, width:1, depth:1},
    ],
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
      rect(20, 19, 3, 1);
      rect(33, 14, 1, 2);
      rect(10, 13, 1, 2);
      rect(14, 12, 14, 1, '=');
      rect(10, 23, 1, 3, '=');
      rect(11, 25, 6, 1, '=');
      mark('o', [[8,10],[35,10],[8,17],[35,17],[13,11],[30,17],[13,24],[15,24],[26,26]]);
      mark('p', [[34,7],[14,16],[26,17],[18,25],[35,20]]);
      mark('s', [[23,15]]);
      mark('r', [[18,15]]);
    },
  },
  {
    id: 'power', name: '비상 발전실', width: 33, depth: 21, entrance: 16,
    feature: '차단기 전실 → 발전기 사이 중앙 통로 또는 서쪽 정비 통로 → 전력 제어실',
    palette: ['#514940', '#77674e', '#38332f', '#bea05d'],
    scenery: [
      {kind:'diesel', x:5, y:10, width:6, depth:2},
      {kind:'alternator', x:22, y:10, width:6, depth:2},
      {kind:'switchboard', x:13, y:1, width:6, depth:1},
    ],
    design(rect, mark) {
      rect(8, 1, 17, 5);
      rect(13, 5, 7, 3);
      rect(1, 8, 31, 8);
      rect(5, 15, 8, 3);
      rect(20, 15, 8, 3);
      rect(12, 16, 9, 4);
      rect(3, 10, 9, 3, '=');
      rect(21, 10, 9, 3, '=');
      rect(7, 5, 3, 4);
      rect(7, 5, 6, 2);
      rect(15, 7, 3, 9);
      rect(14, 15, 5, 3, '=');
      mark('o', [[9,2],[23,2],[6,16],[26,16],[13,18],[19,18]]);
      mark('p', [[10,3],[21,4],[8,15],[21,16]]);
      mark('s', [[16,13]]);
      mark('r', [[16,2]]);
    },
  },
].map(buildEndingLayout);
