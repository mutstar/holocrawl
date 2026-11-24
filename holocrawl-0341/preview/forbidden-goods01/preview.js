(() => {
  const canvas = document.getElementById('map');
  const context = canvas.getContext('2d');
  const seedInput = document.getElementById('seed');
  const back = document.getElementById('return');
  const status = document.getElementById('status');
  const controls = [...document.querySelectorAll('[data-view]')];
  const wallArt = createWarehouseWallArt();
  const query = new URLSearchParams(location.search);
  seedInput.value = (query.get('seed') || seedInput.value).slice(0, seedInput.maxLength);
  let view = controls.some(button => button.dataset.view === query.get('view')) ? query.get('view') : 'inspection';
  let rendered, points, currentSeed;

  function draw() {
    const overview = view === 'overview';
    const scale = overview ? .28125 : 1.375;
    const width = rendered.width * scale;
    const height = rendered.height * scale;
    const { x, y } = points[view] || points.arrival;
    const offset = (coordinate, screen, extent) => overview
      ? Math.floor((screen - extent) / 2)
      : -Math.max(0, Math.min(extent - screen, Math.floor((coordinate + .5) * 32 * scale - screen / 2)));
    context.imageSmoothingEnabled = false;
    context.fillStyle = '#111114';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(rendered, offset(x, canvas.width, width), offset(y, canvas.height, height), width, height);
    for (const button of controls) button.setAttribute('aria-pressed', String(button.dataset.view === view));
    history.replaceState(null, '', '?' + new URLSearchParams({ seed: currentSeed, view }));
  }

  function generate() {
    const seed = seedInput.value.trim() || 'rehearsal-01';
    try {
      const { map, zones } = buildForbiddenWarehouse(seed);
      const image = document.createElement('canvas');
      image.width = map.w * 32;
      image.height = map.h * 32;
      const shutter = { ...map.exitDoor, width: map.exitDoor.w, height: map.exitDoor.h };
      const wallPlan = createWallDecorationPlan(map, wallArt, [...zones, shutter]);
      wallPlan.fill([]);
      drawWarehouse(image.getContext('2d'), map, zones, wallPlan.decorations);
      rendered = image;
      points = { arrival: map.upstairs, shutter: map.exit };
      for (const { id, x, y, width, height } of zones) {
        points[id] = { x: x + (width - 1) / 2, y: y + (height - 1) / 2 };
      }
      currentSeed = seedInput.value = seed;
      back.href = '../broadcast-stage01/?' + new URLSearchParams({ floor: 5, view: 'goods-gate', seed });
      draw();
      status.textContent = `80×70칸 · 벽 장식 ${wallPlan.decorations.length}개 · 하행 셔터까지 ${map.path.length - 1}칸`;
    } catch (error) {
      status.textContent = '이 시드에서 창고 지도를 만들지 못했어. 다른 시드를 입력해 줘.';
      console.error(error);
    }
  }

  document.querySelector('form').onsubmit = event => { event.preventDefault(); generate(); };
  for (const button of controls) button.onclick = () => {
    if (!rendered) return;
    view = button.dataset.view;
    draw();
  };
  generate();
})();
