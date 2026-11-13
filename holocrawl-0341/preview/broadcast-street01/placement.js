function placeBroadcastProps(map, station, wallSites, doors, inEntrance, stageSite) {
  const {w, h, cells, seed, floor} = map;
  const stairs = [map.upstairs, map.exit];
  const distance = (a, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));
  const location = (x, y) => y * w + x;
  const random = StreetGen.random(`${seed}:broadcast-props`);
  const wallProps = [{...station, type: 'onAir'}];
  const windowOffsets = [-2, -1, 1, 2];
  const stationWalls = wallSites.filter(({x, y}) => !inEntrance(x, y));
  const wallKeys = new Set(stationWalls.map(({x, y}) => `${x},${y}`));
  for (const dx of windowOffsets) {
    const x = station.x + dx;
    if (wallKeys.has(`${x},${station.y}`)) wallProps.push({x, y: station.y, type: 'window'});
  }
  const frontFixtures = [
    {type: 'stationEmblem', dx: -3}, {type: 'scheduleBoard', dx: 3},
    {type: 'speaker', dx: -5}, {type: 'securityCamera', dx: 5},
  ];
  for (const {type, dx} of frontFixtures) {
    const x = station.x + dx;
    if (wallKeys.has(`${x},${station.y}`)) wallProps.push({x, y: station.y, type});
  }
  if (floor >= 13) {
    const occupied = new Set(wallProps.map(({x, y}) => location(x, y)));
    const bays = stationWalls.filter(({x, y}) =>
      wallKeys.has(`${x + 1},${y}`) &&
      !occupied.has(location(x, y)) && !occupied.has(location(x + 1, y)));
    const screen = bays.sort((a, b) => distance(a, station) - distance(b, station))[0];
    if (screen) {
      wallProps.push({...screen, type: 'noiseScreen', footW: 2});
    } else if (windowOffsets.slice(0, 2).every(dx => wallKeys.has(`${station.x + dx},${station.y}`))) {
      // Use a window bay if the station has no other pair of exposed wall tiles.
      wallProps.splice(1, 2, {x: station.x - 2, y: station.y, type: 'noiseScreen', footW: 2});
    }
  }
  const wallOrder = stationWalls.map(site => ({site, rank: random()})).sort((a, b) => a.rank - b.rank);
  const wallObstacles = [...stairs, ...doors];
  const equipment = ['stationEmblem', 'scheduleBoard', 'speaker', 'securityCamera',
    'signalBox', 'programPoster', 'conduit', 'vent', 'vent', 'speaker', 'programPoster', 'conduit'];
  for (const type of equipment) {
    const candidate = wallOrder.find(({site}) =>
      wallProps.every(prop => distance(site, prop) >= 4 &&
        (prop.footW !== 2 || distance(site, {x: prop.x + 1, y: prop.y}) >= 4)) &&
      wallObstacles.every(feature => distance(site, feature) >= 2));
    if (candidate) wallProps.push({...candidate.site, type});
  }

  const open = Uint8Array.from(cells, cell => Number(cell === StreetGen.FLOOR));
  const front = {x: station.x, y: station.y + 2};
  const safety = Passage124.create({
    w, h, open, seed,
    specials: [
      ...stairs.map(stair => ({...stair, radius: 2})),
      ...doors.map(door => ({...door, radius: 1})),
      ...(stageSite ? [{...stageSite, radius: 1}] : []),
      {...front, radius: 1},
    ],
  });
  const sites = [];
  for (let y = 2; y < h - 2; y++) for (let x = 2; x < w - 2; x++) {
    const i = location(x, y);
    if (open[i] && !safety.protectedCells[i]) sites.push({x, y, rank: random()});
  }
  const groundSpecs = [
    {type: 'van', footW: 3, footH: 2, dx: -8, dy: 3},
    {type: 'queueBarrier', footW: 2, dx: 3, dy: 2},
    {type: 'camera', dx: -3, dy: 3},
    {type: 'studioLight', dx: 2, dy: 4},
    {type: 'equipmentCases', dx: -7, dy: 0},
    {type: 'cable', dx: -4, dy: 5},
    {type: 'clapperboard', dx: 5, dy: 5},
    {type: 'monitorRack', dx: 14, dy: -4},
    {type: 'equipmentCart', dx: -16, dy: 10},
    {type: 'satelliteDish', dx: 7, dy: -13},
  ];
  const requested = [];
  for (const {type, footW = 1, footH = 1, dx, dy} of groundSpecs) {
    const target = {x: front.x + dx, y: front.y + dy};
    const candidates = sites.filter(({x, y}) => {
      for (let py = y; py < y + footH; py++) for (let px = x; px < x + footW; px++) {
        const i = location(px, py);
        if (!open[i] || safety.protectedCells[i]) return false;
      }
      return true;
    }).sort((a, b) => distance(a, target) - distance(b, target) || a.rank - b.rank);
    if (candidates.length) requested.push({x: candidates[0].x, y: candidates[0].y, footW, footH, type});
  }
  const ground = safety.place(requested);
  return {front, wallProps, groundProps: ground.placed, blocked: ground.blocked};
}
