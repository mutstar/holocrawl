(async function () {
  const byId = id => document.getElementById(id);
  const status = byId('status');
  const wallRoot = '../wall-height121/';
  const stairsRoot = '../city-random15/assets/';
  const load = async url => {
    const image = new Image();
    image.src = url;
    await image.decode();
    return image;
  };
  const json = async url => {
    const response = await fetch(url);
    if (!response.ok) throw Error(url);
    return response.json();
  };
  const [atlas, rects, planes, up, down] = await Promise.all([
    load(wallRoot + 'wall22.png'), json(wallRoot + 'rects121.json'), json(wallRoot + 'planes121.json'),
    load(stairsRoot + 'crawl-stairs-up-mirrored32.png'), load(stairsRoot + 'crawl-stairs-down-mirrored32.png'),
  ]);
  const art = createStudioArt(atlas, rects, planes);
  const bayArt = ['window', 'rack', 'shutter'].map(art.wallBay);
  const equipment = createStudioProps();
  const glassStudio = createGlassStudioArt(art, equipment.wall[0], equipment.ground[0]);
  const vaultArt = createStudioVaultArt(art, equipment);
  const neighbors = [[0,-1], [1,-1], [1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1]];
  const field = byId('map');
  const ctx = field.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  const seedInput = byId('seed');
  const floorSelect = byId('floor');
  const query = new URLSearchParams(location.search);
  seedInput.value = (query.get('seed') || seedInput.value).slice(0, seedInput.maxLength);
  floorSelect.value = query.get('floor') === '2' ? '2' : '1';
  const views = ['overview', 'studio', 'booth', 'rehearsal', 'storage'];
  let map, rendered, points, focus = views.includes(query.get('view')) ? query.get('view') : 'studio';

  function buildLayout(seed) {
    const profile = {courts: 4, wideChance: .75, extraLinks: .85, avenues: 2, minRoomWidth: 7, minRoomHeight: 5};
    const next = StreetGen.generate(seed, 80, 70, 'floor', profile);
    const {w, h, cells} = next;
    for (const {x, y} of next.props) cells[y * w + x] = StreetGen.FLOOR;
    const wall = (x, y) => x >= 0 && y >= 0 && x < w && y < h && cells[y * w + x] === StreetGen.WALL;
    const stages = next.rooms.map(room => ({x: room.cx - 2, y: room.y, cx: room.cx, cy: room.cy, width: 5}))
      .filter(({x, y}) => [0, 1, 2, 3, 4].every(dx =>
        wall(x + dx, y - 1) && [0, 1, 2, 3].every(dy => !wall(x + dx, y + dy))))
      .sort((a, b) => Math.hypot(a.cx - w / 2, a.cy - h / 2) - Math.hypot(b.cx - w / 2, b.cy - h / 2))
      .slice(0, 5);
    if (!stages.length) {
      const room = next.prefab.room;
      stages.push({x: next.prefab.x, y: room.y, cx: next.prefab.x + 1, cy: room.cy, width: 4});
    }
    const bays = [];
    for (const stage of stages) {
      const bay = {x: stage.x + 1, y: stage.y - 1};
      if (bays.some(other => other.y === bay.y && Math.abs(other.x - bay.x) < 4)) continue;
      bays.push({...bay, stage});
    }
    const booth = placeGlassStudio(next, stages);
    const reserved = stages.map(stage => ({x: stage.x, y: stage.y - 1, width: stage.width, height: 5}));
    if (booth) reserved.push({...booth, ...glassStudioSize});
    const vaults = {};
    for (const kind of Object.keys(vaultArt)) {
      const site = placeStudioVault(next, kind, reserved);
      if (!site) continue;
      vaults[kind] = site;
      reserved.push(site);
    }
    return {next, wall, stages, bays, booth, vaults};
  }

  function render(seed, floor) {
    const floorSeed = `${seed}:rehearsal:${floor}`;
    const count = layout => Number(Boolean(layout.booth)) + Object.keys(layout.vaults).length;
    let layout = buildLayout(floorSeed);
    for (let attempt = 1; attempt <= 4 && count(layout) < 3; attempt++) {
      const candidate = buildLayout(`${floorSeed}:vaults:${attempt}`);
      if (count(candidate) > count(layout)) layout = candidate;
    }
    const {next, wall, stages, bays, booth, vaults} = layout;
    const {w, h, cells} = next;
    const source = art.sprite(w * 32, h * 32, layer => {
      layer.fillStyle = '#14191e';
      layer.fillRect(0, 0, w * 32, h * 32);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        let tile;
        if (wall(x, y)) {
          const mask = neighbors.reduce((bits, [dx, dy], bit) =>
            wall(x + dx, y + dy) ? bits | (1 << bit) : bits, 0);
          tile = art.wallTile(mask, x, y);
        } else {
          const platform = stages.some(stage => x >= stage.x && x < stage.x + stage.width
            && y >= stage.y && y < stage.y + 4);
          tile = art.floorTile(x, y, platform);
        }
        layer.drawImage(tile, x * 32, y * 32);
      }
      for (const [index, bay] of bays.entries()) {
        layer.drawImage(bayArt[index % bayArt.length], bay.x * 32, bay.y * 32);
        layer.fillStyle = '#bf9c70';
        for (const dx of [6, 82]) layer.fillRect(bay.x * 32 + dx, bay.stage.y * 32 + 103, 6, 2);
      }
      if (booth) layer.drawImage(glassStudio, booth.x * 32, booth.y * 32);
      for (const [kind, site] of Object.entries(vaults)) {
        layer.drawImage(vaultArt[kind], site.x * 32, site.y * 32);
      }
      layer.drawImage(up, next.upstairs.x * 32, next.upstairs.y * 32);
      layer.drawImage(down, next.exit.x * 32, next.exit.y * 32);
    });
    if (booth) for (const {x, y} of booth.glass) cells[y * w + x] = StreetGen.WALL;
    for (const {blocked} of Object.values(vaults)) {
      for (const {x, y, tile} of blocked) cells[y * w + x] = tile;
    }
    const center = ({x, y, width, height}) => ({x: x + (width - 1) / 2, y: y + (height - 1) / 2});
    const points = {studio: {x: stages[0].cx, y: stages[0].y + 1}};
    if (booth) points.booth = center({...booth, ...glassStudioSize});
    for (const [kind, site] of Object.entries(vaults)) points[kind] = center(site);
    return {map: next, source, points};
  }

  function draw() {
    const overview = focus === 'overview';
    const point = points[focus] || points.studio;
    const scale = overview ? .25 : 1.5;
    const width = map.w * 32 * scale;
    const height = map.h * 32 * scale;
    const offset = (coordinate, screen, extent) => overview
      ? Math.floor((screen - extent) / 2)
      : -Math.max(0, Math.min(extent - screen, Math.floor((coordinate + .5) * 32 * scale - screen / 2)));
    ctx.fillStyle = '#101419';
    ctx.fillRect(0, 0, field.width, field.height);
    ctx.drawImage(rendered, offset(point.x, field.width, width), offset(point.y, field.height, height), width, height);
    for (const id of views) byId(id).setAttribute('aria-pressed', String(focus === id));
  }

  function generate() {
    const floor = Number(floorSelect.value);
    const seed = seedInput.value.trim() || 'rehearsal-01';
    const result = render(seed, floor);
    ({map, source: rendered, points} = result);
    for (const id of ['booth', 'rehearsal', 'storage']) byId(id).hidden = !points[id];
    if (focus !== 'overview' && !points[focus]) focus = 'studio';
    seedInput.value = seed;
    const title = `방송 지하무대 ${floor}층 · 리허설 스튜디오`;
    byId('title').textContent = document.title = title;
    field.setAttribute('aria-label', title + ' 지도');
    history.replaceState(null, '', '?' + new URLSearchParams({seed, floor, view: focus}));
    status.textContent = '80×70칸 · 목재 리허설 바닥과 흡음 패널 벽';
    draw();
  }

  function refresh() {
    try { generate(); }
    catch (error) {
      status.textContent = '지도를 생성하지 못했습니다. 다른 시드로 다시 시도하세요.';
      console.error(error);
    }
  }
  document.querySelector('form').onsubmit = event => { event.preventDefault(); refresh(); };
  floorSelect.onchange = refresh;
  byId('random').onclick = () => {
    seedInput.value = 'rehearsal-' + Math.floor(Math.random() * 1e9);
    refresh();
  };
  for (const id of views) byId(id).onclick = () => {
    focus = id;
    const params = new URLSearchParams(location.search);
    params.set('view', id);
    history.replaceState(null, '', '?' + params);
    draw();
  };
  refresh();
})().catch(error => {
  document.getElementById('status').textContent = '미리보기를 불러오지 못했습니다.';
  console.error(error);
});
