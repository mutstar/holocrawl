(async function () {
  const byId = id => document.getElementById(id);
  const loadImage = async url => {
    const image = new Image();
    image.src = url;
    await image.decode();
    return image;
  };
  const readJson = async url => {
    const response = await fetch(url);
    if (!response.ok) throw Error(url);
    return response.json();
  };
  const [atlas, rects, planes, up, down] = await Promise.all([
    loadImage('../wall-height121/wall22.png'),
    readJson('../wall-height121/rects121.json'),
    readJson('../wall-height121/planes121.json'),
    loadImage('../city-random15/assets/crawl-stairs-up-mirrored32.png'),
    loadImage('../city-random15/assets/crawl-stairs-down-mirrored32.png'),
  ]);
  const art = createBroadcastArt(atlas, rects, planes);
  const propArt = createBroadcastPropArt(art.sprite);
  const wallArt = {...art.fixtures, ...propArt.wall};
  const wear = createBroadcastWear(art, wallArt, propArt.ground);
  const curtainEntrance = createCurtainEntrance(art);
  const stageEntrance = createStageEntrance(art);
  const tileSize = 32;
  const neighbors = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const seedInput = byId('seed');
  const floorSelect = byId('floor');
  const field = byId('map');
  const ctx = field.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  const doorFocus = byId('door-focus');
  const curtainFocus = byId('curtain-focus');
  const stageFocus = byId('stage-focus');
  let map, rendered, front, nearestDoor, stage, overview, view;
  const query = new URLSearchParams(location.search);
  seedInput.value = (query.get('seed') || seedInput.value).slice(0, seedInput.maxLength);
  if (['11', '12', '13', '14'].includes(query.get('floor'))) floorSelect.value = query.get('floor');

  function generateMap(seed, floor) {
    const map = StreetGen.generate(`${seed}:broadcast${floor}`, 80, 70, floor === 14 ? 'wall' : 'floor', {
      courts: 5, wideChance: .65, extraLinks: 1.1, avenues: 3,
      minRoomWidth: 6, minRoomHeight: 5,
      wallExitWidth: 2,
    });
    // StreetGen's entrance fence belongs to the early-city layout.
    for (const prop of map.props) map.cells[prop.y * map.w + prop.x] = StreetGen.FLOOR;
    map.seed = seed;
    map.floor = floor;
    return map;
  }

  function renderMap(next) {
    const {w, h, cells, seed, floor} = next;
    const age = floor - 11;
    const equipment = wear.equipment(age);
    if (age >= 2) equipment.walls.noiseScreen = propArt.noiseScreen(floor);
    const wall = (x, y) => x >= 0 && y >= 0 && x < w && y < h && cells[y * w + x] === StreetGen.WALL;
    const paving = (x, y) => x > 0 && y > 0 && x < w - 1 && y < h - 1 && !wall(x, y);
    const stations = [];
    const wallSites = [];
    const doors = [];
    const entrance = next.exitDoor;
    const inCurtain = (x, y) => entrance &&
      x >= entrance.x && x < entrance.x + entrance.w && y >= entrance.y && y < entrance.y + entrance.h;
    for (let y = 2; y < h - 3; y++) for (let x = 2; x < w - 2; x++) {
      if (wall(x, y) && paving(x, y + 1)) {
        wallSites.push({x, y});
        if ([-2,-1,0,1,2].every(dx => wall(x + dx, y) && !inCurtain(x + dx, y) &&
          paving(x + dx, y + 1) && paving(x + dx, y + 2))) {
          stations.push({x, y, distance: Math.hypot(x - w / 2, y - h / 2)});
        }
      } else if (paving(x, y)) {
        const horizontal = wall(x - 1, y) && wall(x + 1, y) && paving(x, y - 1) && paving(x, y + 1);
        const vertical = wall(x, y - 1) && wall(x, y + 1) && paving(x - 1, y) && paving(x + 1, y);
        if (horizontal || vertical) doors.push({x, y, horizontal});
      }
    }
    const center = stations.sort((a, b) => a.distance - b.distance)[0] || {
      x: next.prefab.x + 1, y: next.prefab.y + 1,
    };
    const stairSites = [next.upstairs, next.exit];
    const distance = (a,b) => Math.max(Math.abs(a.x-b.x), Math.abs(a.y-b.y));
    const stageFloor = 11 + Math.floor(StreetGen.random(`${seed}:broadcast-stage-floor`)() * 2);
    let stageSite = null;
    if (floor === stageFloor) {
      const candidates = [];
      for (let y = 2; y < h - 2; y++) for (let x = 2; x < w - 2; x++) {
        const site = {x, y};
        if (distance(site, center) < 5 ||
            stairSites.some(stair => distance(site, stair) < 5)) continue;
        const clear = [-1, 0, 1].every(dy =>
          [-1, 0, 1].every(dx => paving(x + dx, y + dy)));
        if (clear) candidates.push(site);
      }
      const pick = StreetGen.random(`${seed}:broadcast-stage-location`)();
      stageSite = candidates[Math.floor(pick * candidates.length)];
      if (!stageSite) throw Error('No open paving available for the broadcast stage entrance');
    }
    const doorOrder = StreetGen.random(`${seed}:doors`);
    const placedDoors = [];
    for (const {door} of doors.map(door => ({door, order:doorOrder()})).sort((a,b) => a.order-b.order)) {
      if (stairSites.some(stair => distance(door, stair) < 3)) continue;
      if (stageSite && distance(door, stageSite) < 2) continue;
      if (placedDoors.some(placed => distance(door, placed) < 5)) continue;
      placedDoors.push(door);
      if (placedDoors.length === 16) break;
    }
    const layout = placeBroadcastProps(next, center, wallSites, placedDoors, inCurtain, stageSite);
    const doorMap = {...next, doors: placedDoors};
    const sprite = art.sprite(w * tileSize, h * tileSize, layer => {
      layer.fillStyle = '#171c20';
      layer.fillRect(0, 0, w * tileSize, h * tileSize);
      function stamp(tile, x, y) {
        layer.drawImage(tile, x * tileSize, y * tileSize);
      }
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        if (wall(x, y)) {
          const walls = DoorFit159.wallCells(doorMap, x, y);
          const mask = neighbors.reduce((value, [dx,dy], bit) => {
            const nx = x + dx, ny = y + dy;
            const solid = nx >= 0 && ny >= 0 && nx < w && ny < h && walls[ny * w + nx] === 0;
            return solid ? value | (1 << bit) : value;
          }, 0);
          stamp(art.wallTile(mask, x, y), x, y);
          if (age && paving(x, y + 1)) {
            const random = StreetGen.random(`${seed}:${floor}:wall-wear:${x},${y}`);
            if (random() < age * .25) {
              layer.save();
              layer.translate(x * tileSize, y * tileSize);
              wear.wall(layer, random, age, planes[String(mask)]);
              layer.restore();
            }
          }
        } else {
          stamp(art.floorTile(seed, x, y), x, y);
          if (age) {
            const random = StreetGen.random(`${seed}:${floor}:paving-wear:${x},${y}`);
            if (random() < age * .16) {
              layer.save();
              layer.translate(x * tileSize, y * tileSize);
              wear.paving(layer, random, age);
              layer.restore();
            }
          }
        }
      }
      const {canvasW, w: doorWidth} = DoorFit159.frame;
      const inset = (canvasW - doorWidth) / 2;
      for (const door of placedDoors) {
        DoorFit159.drawWallReturns(layer, doorMap, door, layer.canvas, inset);
        stamp(equipment.door, door.x, door.y);
      }
      for (const {x, y, type} of layout.wallProps) {
        let sprite = equipment.walls[type];
        if (type === 'window' && age >= 2) {
          const random = StreetGen.random(`${seed}:${floor}:window-wear:${x},${y}`);
          if (random() < (age === 2 ? .40 : .67)) {
            sprite = equipment.windows[1 + Math.floor(random() * 3)];
          }
        }
        stamp(sprite, x, y);
      }
      for (const {x, y, type} of layout.groundProps) {
        stamp(equipment.ground[type], x, y);
      }
      stamp(up, next.upstairs.x, next.upstairs.y);
      if (entrance) stamp(curtainEntrance, entrance.x, entrance.y);
      else stamp(down, next.exit.x, next.exit.y);
      if (stageSite) stamp(stageEntrance, stageSite.x, stageSite.y);
    });
    const nearestDoor = placedDoors.reduce((nearest, door) =>
      !nearest || distance(door, layout.front) < distance(nearest, layout.front) ? door : nearest, null);
    return {sprite, front: layout.front, nearestDoor, stage: stageSite};
  }

  function draw(at) {
    overview = !at;
    const scale = overview ? .25 : 1.5;
    const width = map.w * tileSize * scale;
    const height = map.h * tileSize * scale;
    const offset = (coordinate, screen, extent) => overview
      ? Math.floor((screen - extent) / 2)
      : -Math.max(0, Math.min(extent - screen, Math.floor((coordinate + .5) * tileSize * scale - screen / 2)));
    view = {scale, x:offset(at?.x, field.width, width), y:offset(at?.y, field.height, height)};
    ctx.fillStyle = '#111619';
    ctx.fillRect(0, 0, field.width, field.height);
    ctx.drawImage(rendered, view.x, view.y, width, height);
    byId('overview').setAttribute('aria-pressed', String(overview));
    const entranceView = map.exitDoor && at === map.exit;
    byId('hint').textContent = overview ? '지도에서 보고 싶은 곳을 누르면 확대됩니다.'
      : entranceView ? '커튼콜 1층 · 끝없는 대기실 입구'
      : at === stage ? '방송 지하무대 1층 · 리허설 스튜디오 입구'
      : '확대 보기 · 다른 위치를 보려면 전체 지도를 선택하세요.';
  }

  function generate() {
    const showCurtain = location.hash === '#curtain';
    const showStage = location.hash === '#stage';
    const seed = seedInput.value.trim() || 'studio-11';
    const floor = Number(floorSelect.value);
    const next = generateMap(seed, floor);
    const layout = renderMap(next);
    map = next;
    rendered = layout.sprite;
    front = layout.front;
    nearestDoor = layout.nearestDoor;
    stage = layout.stage;
    doorFocus.disabled = !nearestDoor;
    curtainFocus.hidden = !map.exitDoor;
    stageFocus.hidden = !stage;
    seedInput.value = seed;
    const title = `잔향도시 ${floor}층 · 뒤틀린 방송 거리`;
    byId('floor-title').textContent = document.title = title;
    field.setAttribute('aria-label', title + ' 지도');
    const query = '?' + new URLSearchParams({seed, floor});
    const focus = (showStage && stage) || (showCurtain && map.exitDoor && map.exit) || front;
    const hash = focus === stage ? '#stage' : focus === map.exit ? '#curtain' : '';
    history.replaceState(null, '', query + hash);
    draw(focus);
  }

  const samples = [
    ['회청색 패널 외벽', q => { for (let x = 0; x < 2; x++) q.drawImage(art.wallTile(68,x,0),x*32,0); }],
    ['콘크리트 보도', q => { for (let x = 0; x < 2; x++) q.drawImage(art.floorTile('sample',x,0),x*32,0); }],
    ['아치형 방음문 · 닫힘과 열림', q => {
      art.doors.forEach((door, i) => {
        q.drawImage(art.floorTile('sample', i, 0), i * 32, 0);
        q.drawImage(door, i * 32, 0);
      });
    }],
    ['방송 표시등과 방음창', q => {
      q.drawImage(art.wallTile(68,0,0),0,0);
      q.drawImage(art.wallTile(68,1,0),32,0);
      q.drawImage(art.fixtures.onAir,0,0);
      q.drawImage(art.fixtures.window,32,0);
    }],
  ];
  function addSample(section, label, sprite) {
    const figure = document.createElement('figure');
    const caption = document.createElement('figcaption');
    caption.textContent = label;
    figure.append(sprite, caption);
    byId(section).append(figure);
  }
  for (const [label, paint] of samples) {
    addSample('samples', label, art.sprite(64,32,paint));
  }
  const wallSamples = [
    ['ON AIR 표시등', art.fixtures.onAir],
    ['방음창', art.fixtures.window, true],
    ['환기구', art.fixtures.vent],
    ['안내 방송 스피커', propArt.wall.speaker],
    ['송출 단자함', propArt.wall.signalBox],
    ['벽걸이 CCTV', propArt.wall.securityCamera],
    ['방송국 로고', propArt.wall.stationEmblem],
    ['편성표 전광판', propArt.wall.scheduleBoard],
    ['프로그램 포스터', propArt.wall.programPoster],
    ['벽면 케이블 덕트', propArt.wall.conduit],
  ];
  const groundSamples = [
    ['중계차 · 3×2칸', propArt.ground.van],
    ['삼각대 카메라 · 1칸', propArt.ground.camera],
    ['모니터 랙 · 1칸', propArt.ground.monitorRack],
    ['장비 케이스 · 1칸', propArt.ground.equipmentCases],
    ['말린 케이블 · 1칸', propArt.ground.cable],
    ['스튜디오 조명 · 1칸', propArt.ground.studioLight],
    ['장비 운반 카트 · 1칸', propArt.ground.equipmentCart],
    ['위성 안테나 · 1칸', propArt.ground.satelliteDish],
    ['슬레이트 · 1칸', propArt.ground.clapperboard],
    ['대기줄 차단봉 · 2×1칸', propArt.ground.queueBarrier],
  ];
  function propSample(prop, onWall, repeat) {
    return art.sprite(96, 64, ctx => {
      ctx.fillStyle = '#171c20';
      ctx.fillRect(0, 0, 96, 64);
      for (let x = 0; x < 3; x++) {
        const tile = onWall ? art.wallTile(68, x, 0) : art.floorTile('sample', x, 0);
        ctx.drawImage(tile, x * 32, 0);
        ctx.drawImage(art.floorTile('sample', x, 1), x * 32, 32);
        if (repeat) ctx.drawImage(prop, x * 32, 0);
      }
      if (!repeat) ctx.drawImage(prop, (96 - prop.width) / 2, onWall || prop.height === 64 ? 0 : 16);
    });
  }
  for (const [label, prop, repeat] of wallSamples) {
    addSample('wall-props', label, propSample(prop, true, repeat));
  }
  for (const floor of [13, 14]) {
    addSample('wall-props', `${floor}층 방송 스크린 · 2칸`, propSample(propArt.noiseScreen(floor), true, false));
  }
  for (const [label, prop] of groundSamples) {
    addSample('ground-props', label, propSample(prop, false));
  }
  byId('generator').onsubmit = event => { event.preventDefault(); generate(); };
  floorSelect.onchange = generate;
  byId('random').onclick = () => { seedInput.value = 'studio-' + Math.floor(Math.random() * 1e9); generate(); };
  byId('front').onclick = () => draw(front);
  doorFocus.onclick = () => draw(nearestDoor);
  stageFocus.onclick = () => {
    history.replaceState(null, '', '#stage');
    draw(stage);
  };
  curtainFocus.onclick = () => {
    history.replaceState(null, '', '#curtain');
    draw(map.exit);
  };
  byId('overview').onclick = () => draw(overview ? front : null);
  field.onclick = event => {
    if (!overview) return;
    const rect = field.getBoundingClientRect();
    const x = Math.floor(((event.clientX - rect.left) * field.width / rect.width - view.x) / (tileSize * view.scale));
    const y = Math.floor(((event.clientY - rect.top) * field.height / rect.height - view.y) / (tileSize * view.scale));
    if (x >= 0 && y >= 0 && x < map.w && y < map.h) draw({x,y});
  };
  generate();
})().catch(error => {
  document.getElementById('hint').textContent = '미리보기를 불러오지 못했습니다.';
  console.error(error);
});
