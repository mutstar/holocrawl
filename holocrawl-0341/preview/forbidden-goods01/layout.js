const warehouseZones = [
  { id: 'inspection', name: '반입 검수실', width: 10, height: 6, distance: 24, band: '#5d8379',
    props: [['counter', 2, 1, 3], ['counter', 6, 1, 3], ['cart', 1, 4, 2], ['case', 7, 4, 2]] },
  { id: 'quarantine', name: '격리 적재장', width: 12, height: 7, distance: 55, band: '#a88851',
    props: [['cage', 1, 1, 3], ['cage', 8, 1, 3], ['case', 1, 4, 2], ['case', 9, 4, 2]] },
  { id: 'returns', name: '반송 분류실', width: 9, height: 6, distance: 76, band: '#887197',
    props: [['shelf', 1, 1, 3], ['shelf', 5, 1, 3], ['cart', 2, 4, 2], ['case', 5, 4, 2]] },
];

function buildForbiddenWarehouse(seed) {
  const profile = { courts: 7, wideChance: .67, extraLinks: .82, avenues: 2,
    minRoomWidth: 8, minRoomHeight: 6, wallExitWidth: 2 };
  for (let attempt = 0; attempt < 12; attempt++) {
    const map = StreetGen.generate(`${seed}:forbidden-warehouse:${attempt}`, 80, 70, 'wall', profile);
    for (const { x, y } of map.props) map.cells[y * map.w + x] = StreetGen.FLOOR;
    const placed = [];
    for (const zone of warehouseZones) {
      const area = placeWarehouseZone(map, zone, placed);
      if (!area) break;
      placed.push(area);
    }
    if (placed.length === warehouseZones.length) {
      map.validation = StreetGen.validate(map);
      map.path = StreetGen.route(map, map.start, map.exit);
      return { map, zones: placed };
    }
  }
  throw Error('Could not fit connected warehouse zones');
}

function placeWarehouseZone(map, zone, placed) {
  const { w, h, cells, start, upstairs, exit, exitDoor } = map;
  const { width, height, distance } = zone;
  const random = StreetGen.random(`${map.seed}:${zone.id}`);
  const { dist } = StreetGen.distances(map, start);
  const anchors = [start, upstairs, exit];
  const candidates = [];
  for (let y = 2; y + height < h - 2; y++) for (let x = 2; x + width < w - 2; x++) {
    if (anchors.some(p => p.x >= x - 2 && p.x < x + width + 2 && p.y >= y - 2 && p.y < y + height + 2)) continue;
    if (x < exitDoor.x + exitDoor.w + 1 && x + width + 1 > exitDoor.x
        && y < exitDoor.y + exitDoor.h + 2 && y + height + 1 > exitDoor.y) continue;
    if (placed.some(p => x < p.x + p.width + 3 && x + width + 3 > p.x
        && y < p.y + p.height + 3 && y + height + 3 > p.y)) continue;
    let fits = true;
    for (let row = y; row < y + height && fits; row++) {
      fits = cells.subarray(row * w + x, row * w + x + width).every(tile => tile === StreetGen.FLOOR);
    }
    if (!fits) continue;
    const center = (y + Math.floor(height / 2)) * w + x + Math.floor(width / 2);
    candidates.push({ x, y, priority: Math.abs(dist[center] - distance) + random() * 16 });
  }
  candidates.sort((a, b) => a.priority - b.priority);
  for (const { x, y } of candidates) {
    for (const [, dx, dy, span] of zone.props) {
      const index = (y + dy) * w + x + dx;
      cells.fill(StreetGen.BARRIER, index, index + span);
    }
    if (StreetGen.validate(map).ok) return { ...zone, x, y };
    for (const [, dx, dy, span] of zone.props) {
      const index = (y + dy) * w + x + dx;
      cells.fill(StreetGen.FLOOR, index, index + span);
    }
  }
  return null;
}
