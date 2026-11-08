(async () => {
  const names = {
    mountain: '페이스 마운틴', dining: '타라후쿠 저니', theater: '2기생 극장',
    gamers: '게이머즈 폐역', fantasy: '도타바타 그라운드', wheel: '관람차 광장',
    market: '네포라보 마트', holox: 'holoX 연구소', dev: 'DEV_IS 출장소',
  };
  const manifest = await (await fetch('manifest.json')).json();
  const wallSelection = await (await fetch('wall-selection81.json')).json();
  const selectedWalls = new Set(wallSelection.cells.map(([x, y]) => `${x},${y}`));
  let wallPreviewEnabled = true;
  const atlas = {};
  await Promise.all(['floor', 'wall', 'feat', 'wall-depth81'].map(name => new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => { atlas[name] = image; resolve(); };
    image.onerror = reject;
    image.src = `assets/${name}.png?v=${manifest.artRevision || 77}`;
  })));
  const field = document.getElementById('field');
  const context = field.getContext('2d');
  const floorSelect = document.getElementById('floor');
  for (let depth = 1; depth <= 14; depth++) floorSelect.add(new Option(`${depth}층`, depth));
  const parameters = new URLSearchParams(location.search);
  const requestedSeed = parameters.get('seed');
  document.getElementById('seed').value = manifest.seeds.includes(Number(requestedSeed)) ? requestedSeed : '77001';
  floorSelect.value = String(Math.max(1, Math.min(14, Number(parameters.get('floor')) || 1)));
  const directions = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]];
  let maps, map, state, seed, overview = true, fog = false, center, transform, timer;
  let request = 0;
  const coordinate = (x, y) => `${x},${y}`;
  const terrain = (x, y) => map.rows[y]?.[x] || '#';
  const pass = (x, y) => !'#G~'.includes(terrain(x, y));
  const canStep = (x, y, nx, ny) => pass(nx, ny) &&
    !(nx !== x && ny !== y && !pass(nx, y) && !pass(x, ny));
  const stop = () => { clearTimeout(timer); timer = null; };
  const storageKey = () => `holocrawl-native-city77:${seed}:${map.depth}`;
  function save() {
    try { localStorage.setItem(storageKey(), JSON.stringify(state)); } catch {}
  }
  function vision() {
    const visible = CrawlVisibility.compute(map.width, map.height, state.player, (x, y) =>
      terrain(x, y) === '#' || terrain(x, y) === '+' && !state.opened.includes(coordinate(x, y)) ? 2 : 0, 7);
    for (let index = 0; index < visible.length; index++) if (visible[index]) state.explored[index] = 1;
    return visible;
  }
  function drawTile(index, x, y, scale, selectedWall = false) {
    const tile = map.palette[index];
    const image = selectedWall && tile.atlas === 'wall' ? atlas['wall-depth81'] : atlas[tile.atlas];
    context.drawImage(image, tile.sx, tile.sy, tile.width, tile.height,
      x + tile.dx * scale, y + tile.dy * scale, tile.width * scale, tile.height * scale);
  }
  function draw() {
    const visible = vision();
    context.imageSmoothingEnabled = false;
    context.fillStyle = '#080b10';
    context.fillRect(0, 0, field.width, field.height);
    const scale = overview ? Math.min(field.width / (map.width * 32), field.height / (map.height * 32)) : 1;
    const startX = overview ? 0 : Math.max(0, Math.min(map.width * 32 - field.width, center.x * 32 - field.width / 2));
    const startY = overview ? 0 : Math.max(0, Math.min(map.height * 32 - field.height, center.y * 32 - field.height / 2));
    const offsetX = overview ? (field.width - map.width * 32 * scale) / 2 : 0;
    const offsetY = overview ? (field.height - map.height * 32 * scale) / 2 : 0;
    transform = { scale, startX, startY, offsetX, offsetY };
    const opened = new Set(state.opened);
    const doors = new Map(map.doors.map(door => [coordinate(door.x, door.y), door]));
    for (let y = 0; y < map.height; y++) {
      for (let x = 0; x < map.width; x++) {
        const index = y * map.width + x;
        const dx = (x * 32 - startX) * scale + offsetX;
        const dy = (y * 32 - startY) * scale + offsetY;
        if (dx < -32 || dy < -32 || dx > field.width || dy > field.height) continue;
        const door = doors.get(coordinate(x, y));
        drawTile(map.floors[index], dx, dy, scale);
        const selectedWall = wallPreviewEnabled && seed === wallSelection.seed &&
          map.depth === wallSelection.depth && selectedWalls.has(coordinate(x, y));
        drawTile(door && opened.has(coordinate(x, y)) ? door.opened : map.features[index], dx, dy, scale, selectedWall);
        if (fog && !visible[index]) {
          context.fillStyle = state.explored[index] ? 'rgba(0,0,0,.73)' : '#080b10';
          context.fillRect(dx, dy, 32 * scale + .5, 32 * scale + .5);
        }
      }
    }
    context.fillStyle = '#ffdb7f';
    context.beginPath();
    context.arc((state.player.x * 32 + 16 - startX) * scale + offsetX,
      (state.player.y * 32 + 16 - startY) * scale + offsetY, Math.max(3, 6 * scale), 0, Math.PI * 2);
    context.fill();
    document.getElementById('info').textContent = `${map.depth}층 · ${state.turns}턴 · ${state.player.x},${state.player.y} · ${state.message}`;
    document.getElementById('overview').textContent = overview ? '주변 확대 보기' : '전체 층 보기';
    document.getElementById('fog').textContent = fog ? '탐험 안개 끄기' : '탐험 안개 켜기';
    save();
  }
  function move(dx, dy, automatic = false) {
    if (!automatic) stop();
    const nx = state.player.x + dx, ny = state.player.y + dy;
    if (!canStep(state.player.x, state.player.y, nx, ny)) return false;
    const key = coordinate(nx, ny);
    if (terrain(nx, ny) === '+' && !state.opened.includes(key)) {
      state.opened.push(key);
      state.message = '문을 열었습니다. 다음 이동에 통과합니다.';
    } else {
      state.player = { x: nx, y: ny };
      state.message = '실제 생성된 지형을 둘러보는 중입니다.';
      if (!overview) center = { ...state.player };
    }
    state.turns++;
    draw();
    return true;
  }
  function route(target) {
    const queue = [{ ...state.player }];
    const previous = new Map([[coordinate(state.player.x, state.player.y), null]]);
    const end = coordinate(target.x, target.y);
    for (let index = 0; index < queue.length && !previous.has(end); index++) {
      const point = queue[index];
      for (const [dx, dy] of directions) {
        const x = point.x + dx, y = point.y + dy, key = coordinate(x, y);
        if (!previous.has(key) && canStep(point.x, point.y, x, y) &&
            (!fog || state.explored[y * map.width + x])) {
          previous.set(key, point);
          queue.push({ x, y });
        }
      }
    }
    if (!previous.has(end)) return [];
    const path = [];
    for (let point = target; point; point = previous.get(coordinate(point.x, point.y))) path.push(point);
    return path.reverse();
  }
  async function load() {
    stop();
    const pending = ++request;
    const selectedSeed = Number(document.getElementById('seed').value);
    const selectedFloor = Number(floorSelect.value);
    const loaded = await Promise.all(Array.from({ length: 14 }, async (_, index) =>
      (await fetch(`maps/map-${selectedSeed}-${index + 1}.json`)).json()));
    if (pending !== request) return;
    maps = loaded;
    seed = selectedSeed;
    map = maps[selectedFloor - 1];
    const stairs = map.rows.flatMap((row, y) => [...row].flatMap((cell, x) => cell === '<' ? [{ x, y }] : []));
    state = { player: stairs[0], turns: 0, opened: [], explored: Array(map.width * map.height).fill(0), message: '실제 엔진에서 생성한 층입니다.' };
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey()));
      if (saved && pass(saved.player.x, saved.player.y) && saved.explored.length === map.width * map.height) state = saved;
    } catch {}
    center = map.origin ? { x: map.origin.x + map.origin.width / 2, y: map.origin.y + map.origin.height / 2 } : { ...state.player };
    document.getElementById('current').textContent = map.facility ? names[map.facility] : '이번 층은 시설 없음';
    document.getElementById('facility').disabled = !map.facility;
    document.getElementById('schedule').replaceChildren(...maps.map(floor => {
      const row = document.createElement('li');
      row.textContent = `${floor.depth}층 · ${names[floor.facility] || '시설 없음'}`;
      row.setAttribute('aria-current', floor.depth === map.depth);
      return row;
    }));
    history.replaceState(null, '', `?seed=${seed}&floor=${map.depth}`);
    draw();
  }
  document.getElementById('seed').onchange = load;
  floorSelect.onchange = load;
  document.getElementById('overview').onclick = () => { stop(); overview = !overview; draw(); };
  document.getElementById('facility').onclick = () => {
    stop(); overview = false;
    center = { x: map.origin.x + map.origin.width / 2, y: map.origin.y + map.origin.height / 2 };
    draw();
  };
  document.getElementById('player').onclick = () => { stop(); overview = false; center = { ...state.player }; draw(); };
  document.getElementById('fog').onclick = () => { fog = !fog; draw(); };
  document.querySelectorAll('[data-d]').forEach(button => button.onclick = () => move(...button.dataset.d.split(',').map(Number)));
  const keys = { ArrowLeft: [-1,0], ArrowRight: [1,0], ArrowUp: [0,-1], ArrowDown: [0,1], a: [-1,0], d: [1,0], w: [0,-1], s: [0,1], q: [-1,-1], e: [1,-1], z: [-1,1], c: [1,1] };
  addEventListener('keydown', event => {
    if (keys[event.key] && !['SELECT', 'INPUT'].includes(document.activeElement.tagName)) {
      event.preventDefault(); move(...keys[event.key]);
    } else if (event.key === 'Escape') stop();
  });
  field.onclick = event => {
    stop();
    const rectangle = field.getBoundingClientRect();
    const { scale, startX, startY, offsetX, offsetY } = transform;
    const target = {
      x: Math.floor(((event.clientX - rectangle.left) * field.width / rectangle.width - offsetX) / scale / 32 + startX / 32),
      y: Math.floor(((event.clientY - rectangle.top) * field.height / rectangle.height - offsetY) / scale / 32 + startY / 32),
    };
    const tick = () => {
      const next = route(target)[1];
      if (!next) return;
      move(next.x - state.player.x, next.y - state.player.y, true);
      timer = setTimeout(tick, 100);
    };
    tick(); field.focus();
  };
  await load();
  window.cityReview = { move, route, pass, draw, getMap: () => map, getMaps: () => maps, getState: () => structuredClone(state),
    getWallSelection: () => structuredClone(wallSelection), getView: () => ({ ...transform }),
    setWallPreviewEnabled: enabled => { wallPreviewEnabled = Boolean(enabled); draw(); } };
  window.ready = true;
})().catch(error => { document.getElementById('info').textContent = `불러오기 실패 · ${error.message}`; throw error; });
