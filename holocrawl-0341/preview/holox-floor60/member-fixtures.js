const fixturePlans = {
  laplus: {
    x: 1, y: 1, w: 2, h: 1,
    name: '라플라스 봉인 격납고',
    motif: '밝은 보라색 핵을 가둔 캡슐. 양쪽 고정쇠와 황동 사슬로 봉인되어 있다.',
  },
  chloe: {
    x: 1, y: 5, w: 1, h: 2,
    name: '클로에 잠수 장비 거치대',
    motif: '은색 산소통 두 개와 검은 호스, 붉은 리본을 건 세로형 거치대.',
  },
  iroha: {
    x: 5, y: 7, w: 1, h: 1,
    name: '이로하 출입 검문기',
    motif: '연녹색 검사등이 달린 검문기 옆에 카타나를 세워두었다.',
  },
};

const installSecurityDoor = LabSecurityDoor.install;
LabSecurityDoor.install = function (layout, vault) {
  // The same footprint drives movement, vision and station highlights.
  const rows = vault.rows.map(row => [...row]);
  const paintFootprint = (station, tile) => {
    for (let y = station.y; y < station.y + station.h; y++) {
      for (let x = station.x; x < station.x + station.w; x++) rows[y][x] = tile;
    }
  };
  const stations = vault.stations.filter(station => fixturePlans[station.id]);
  for (const station of stations) paintFootprint(station, '.');
  for (const station of stations) {
    Object.assign(station, fixturePlans[station.id]);
    paintFootprint(station, 'F');
  }
  vault.rows = rows.map(row => row.join(''));
  const { x, y } = layout.origin;
  vault.rows.forEach((row, offset) => {
    const mapRow = layout.map.rows[y + offset];
    layout.map.rows[y + offset] = mapRow.slice(0, x) + row + mapRow.slice(x + vault.width);
  });
  return installSecurityDoor.call(this, layout, vault);
};

function drawSeal(rect, polygon) {
  rect('#24232c', 3, 25, 58, 4);
  rect('#585367', 7, 23, 50, 4);
  rect('#3f3a4d', 9, 25, 46, 2);
  polygon('#211d2d', [[8,11],[15,5],[49,5],[56,11],[56,21],[49,25],[15,25],[8,21]]);
  polygon('#5c4d78', [[10,12],[16,7],[48,7],[54,12],[54,20],[48,23],[16,23],[10,20]]);
  polygon('#3a2d57', [[15,11],[20,8],[44,8],[49,11],[49,20],[15,20]]);
  rect('#9c88b7', 18, 8, 28, 1);
  rect('#766591', 17, 19, 30, 1);
  rect('#685683', 20, 11, 24, 6);
  polygon('#a66cdc', [[32,8],[39,14],[32,20],[25,14]]);
  polygon('#d6a5f5', [[32,10],[36,14],[32,18],[28,14]]);
  rect('#f4dcff', 31, 12, 2, 3);
  for (const x of [7, 50]) {
    rect('#2d2938', x, 10, 7, 13);
    rect('#878097', x + 1, 10, 5, 2);
    rect('#656076', x + 2, 12, 3, 8);
    rect('#b58ade', x + 2, 15, 3, 2);
    rect('#b39a64', x + 1, 21, 5, 2);
  }
  for (const x of [15, 20, 25, 34, 39, 44]) {
    rect('#967d50', x, 23, 4, 2);
    rect('#d4b676', x, 23, 2, 1);
  }
}

function drawDivingRack(rect, polygon) {
  rect('#22232c', 3, 52, 27, 6);
  rect('#312e3d', 4, 5, 24, 49);
  rect('#504d60', 5, 7, 22, 44);
  rect('#3d3b49', 8, 10, 16, 40);
  rect('#aaa1b7', 5, 7, 22, 2);
  rect('#777184', 5, 9, 2, 43);
  rect('#777184', 25, 9, 2, 43);
  rect('#9b93a8', 5, 50, 22, 2);
  for (const x of [9, 17]) {
    rect('#22252f', x, 15, 7, 26);
    rect('#a2a4ae', x + 1, 18, 5, 19);
    rect('#dedee2', x + 1, 19, 2, 16);
    rect('#5f6573', x + 4, 19, 2, 16);
    rect('#373a47', x, 27, 7, 3);
    rect('#b8a582', x + 2, 15, 3, 3);
    rect('#7b7684', x + 1, 37, 5, 2);
  }
  polygon('#21222d', [[9,41],[22,41],[24,44],[24,48],[20,50],[10,50],[7,47],[7,44]]);
  rect('#888597', 10, 42, 11, 1);
  rect('#545363', 8, 44, 2, 3);
  rect('#545363', 22, 44, 1, 3);
  rect('#5e5c6e', 11, 48, 9, 1);
  polygon('#b85061', [[17,12],[22,10],[24,12],[25,16],[21,15],[19,18],[18,15],[15,15]]);
  rect('#e99ba4', 20, 12, 3, 1);
}

function drawCheckpoint(rect, polygon) {
  rect('#23252c', 3, 26, 27, 4);
  polygon('#232732', [[3,10],[8,6],[19,6],[22,10],[22,27],[3,27]]);
  polygon('#858894', [[5,10],[9,7],[18,7],[21,10],[17,13],[7,13]]);
  rect('#555866', 5, 13, 15, 12);
  rect('#767982', 5, 14, 2, 10);
  rect('#3d424d', 8, 17, 9, 6);
  rect('#abceb0', 9, 9, 8, 2);
  rect('#d3efb3', 10, 9, 5, 1);
  rect('#8db989', 8, 14, 10, 1);
  rect('#acbf8b', 16, 19, 2, 2);
  rect('#77697b', 6, 25, 13, 1);
  // A freestanding scabbard with its grip and guard at the top.
  rect('#575163', 23, 23, 7, 4);
  rect('#2a2c39', 25, 7, 4, 18);
  rect('#8ca187', 25, 11, 1, 13);
  rect('#d0b781', 23, 8, 7, 2);
  rect('#b6a4a0', 26, 3, 2, 5);
  rect('#77976e', 26, 4, 2, 1);
  rect('#77976e', 26, 6, 2, 1);
}

const fixtureDrawings = { laplus: drawSeal, chloe: drawDivingRack, iroha: drawCheckpoint };
const fixtureSprites = new Map();
LabMaterials.memberSprite = function (_original, id) {
  const draw = fixtureDrawings[id];
  if (!draw) return null;
  if (fixtureSprites.has(id)) return fixtureSprites.get(id);
  const canvas = document.createElement('canvas');
  canvas.width = fixturePlans[id].w * 32;
  canvas.height = fixturePlans[id].h * 32;
  const context = canvas.getContext('2d');
  const rect = (color, x, y, w, h) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };
  const polygon = (color, points) => {
    context.fillStyle = color;
    // Draw polygon edges as whole pixels to match the native tile scale.
    for (let y = 0; y < canvas.height; y++) {
      const intersections = [];
      let previous = points.at(-1);
      for (const point of points) {
        if ((point[1] > y + 0.5) !== (previous[1] > y + 0.5)) {
          intersections.push(previous[0] + (y + 0.5 - previous[1]) * (point[0] - previous[0]) / (point[1] - previous[1]));
        }
        previous = point;
      }
      intersections.sort((a, b) => a - b);
      for (let i = 0; i < intersections.length; i += 2) {
        const left = Math.ceil(intersections[i] - 0.5);
        const right = Math.ceil(intersections[i + 1] - 0.5);
        context.fillRect(left, y, right - left, 1);
      }
    }
  };
  draw(rect, polygon);
  fixtureSprites.set(id, canvas);
  return canvas;
};
