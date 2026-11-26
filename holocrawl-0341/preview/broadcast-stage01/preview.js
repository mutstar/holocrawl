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
  const query = new URLSearchParams(location.search);
  const useArchiveConcrete = query.get('material') === 'concrete';
  const [atlas, rects, planes, up, down, deepWater, gardenSprites, archiveConcrete] = await Promise.all([
    load(wallRoot + 'wall22.png'), json(wallRoot + 'rects121.json'), json(wallRoot + 'planes121.json'),
    load(stairsRoot + 'crawl-stairs-up-mirrored32.png'), load(stairsRoot + 'crawl-stairs-down-mirrored32.png'),
    load('../native-water02/assets/water-deep128.png'), load('garden-scenery.png?v=4'),
    useArchiveConcrete ? load('archive-concrete.png') : null,
  ]);
  const art = createStudioArt(atlas, rects, planes);
  const bayArt = ['window', 'rack', 'shutter'].map(art.wallBay);
  const equipment = createStudioProps();
  const glassStudio = createGlassStudioArt(art, equipment.wall[0], equipment.ground[0]);
  const vaultArt = createStudioVaultArt(art, equipment);
  const equipmentArt = createEquipmentFloorArt(art, atlas, rects, planes);
  const dockArt = createLoadingDockArt(art, atlas, rects, planes);
  const endingWallTile = createEndingWallArt(art.sprite, planes);
  const workAreaArt = createStageWorkAreaArt(art, equipmentArt, dockArt);
  const doors = {studio: art.doors[0], ...createStageDoorArt(art.sprite)};
  const studioWallChoices = [
    {id: 'window', name: '매립형 조정실 창', sprite: bayArt[0], weight: 5},
    {id: 'rack', name: '매립형 장비 랙', sprite: bayArt[1], weight: 4},
    {id: 'shutter', name: '매립형 셔터', sprite: bayArt[2], weight: 4},
    {id: 'patch-panel', name: equipment.wall[1].name, sprite: equipment.wall[1].tile, weight: 4},
    {id: 'charging-shelf', name: equipment.wall[2].name, sprite: equipment.wall[2].tile, weight: 3},
  ];
  const equipmentWallChoices = [
    {id: 'fan', name: '매립 환기팬', sprite: equipmentArt.fixtures.fan, weight: 8},
    {id: 'curtain-roll', name: '무대막 보관 롤', sprite: equipmentArt.fixtures['curtain-roll'], weight: 7},
    {id: 'power-lever', name: '전원 차단 레버', sprite: equipmentArt.fixtures['power-lever'], weight: 5},
  ];
  const dockWallChoices = [
    {id: 'strap-rack', name: '화물 고정 스트랩 걸이', sprite: dockArt.strapRack, weight: 12},
    {id: 'wall-bumpers', name: '벽면 충격 방지대', sprite: dockArt.wallBumpers, weight: 8},
  ];
  const neighbors = [[0,-1], [1,-1], [1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1]];
  const field = byId('map');
  const ctx = field.getContext('2d');
  ctx.imageSmoothingEnabled = false;
  const seedInput = byId('seed');
  const floorSelect = byId('floor');
  const endingExample = byId('ending-example');
  const routeToggle = byId('routes');
  routeToggle.checked = query.get('routes') === '1';
  let reviewPaths = [];
  // These seeds draw each vault through the regular floor generator.
  const exampleSeeds = ['dock-review-5', 'dock-review-18', 'dock-review-10', 'dock-review-6',
    'dock-review-8', 'dock-review-3', 'dock-review-1', 'dock-review-19', 'dock-review-2', 'dock-review-4',
    'dock-large-6', 'dock-large-22', 'dock-large-4', 'dock-large-1'];
  // Previously shared links have no pool parameter. Keep their original seed reproducible.
  let originalSeed = !query.has('pool') && !exampleSeeds.slice(10).includes(query.get('seed'))
    ? query.get('seed') : null;
  for (const seed of exampleSeeds) {
    const ending = pickStageEnding(seed);
    endingExample.add(new Option((stageEndings.indexOf(ending) + 1) + '. ' + ending.name, seed));
  }
  seedInput.value = (query.get('seed') || seedInput.value).slice(0, seedInput.maxLength);
  const requestedFloor = query.get('floor');
  if (['1', '2', '3', '4', '5'].includes(requestedFloor)) floorSelect.value = requestedFloor;
  const views = ['overview', 'studio', 'booth', 'rehearsal', 'storage', 'lighting', 'cable', 'loading',
    'fan', 'curtain-roll', 'power-lever', 'service', 'freight', 'warehouse', 'goods-gate', 'wall-decor', 'work-area', 'door', 'ending', 'ward-doors'];
  let map, rendered, points, decorations;
  let setOfficeExit, exitOpen;
  let wardControls = [];
  const wardButtons = Array.from(document.querySelectorAll('[data-ward]'));
  let focus = views.includes(query.get('view')) ? query.get('view') : 'studio';

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
    const stageMarks = [];
    for (const stage of stages) {
      const mark = {x: stage.x + 1, y: stage.y};
      if (stageMarks.some(other => other.y === mark.y && Math.abs(other.x - mark.x) < 4)) continue;
      stageMarks.push(mark);
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
    return {next, stages, stageMarks, booth, vaults};
  }

  function placeDoors(map, reserved, decorations) {
    const {w, h, cells, seed, start, upstairs, exit} = map;
    const random = StreetGen.random(`${seed}:doors`);
    const anchors = [start, upstairs, exit];
    const unavailable = [...reserved, ...decorations.map(prop => ({...prop, height: 1}))];
    const tile = (x, y) => cells[y * w + x];
    const clear = (x, y) => !anchors.some(p => Math.max(Math.abs(p.x - x), Math.abs(p.y - y)) < 3)
      && !unavailable.some(p => x + 1 >= p.x && x - 1 < p.x + p.width
        && y + 1 >= p.y && y - 1 < p.y + p.height);
    const candidates = [];
    for (let y = 2; y < h - 2; y++) for (let x = 2; x < w - 2; x++) {
      if (tile(x, y) !== StreetGen.FLOOR || !clear(x, y)) continue;
      const horizontal = tile(x - 1, y) === StreetGen.WALL && tile(x + 1, y) === StreetGen.WALL
        && tile(x, y - 1) === StreetGen.FLOOR && tile(x, y + 1) === StreetGen.FLOOR;
      const vertical = tile(x, y - 1) === StreetGen.WALL && tile(x, y + 1) === StreetGen.WALL
        && tile(x - 1, y) === StreetGen.FLOOR && tile(x + 1, y) === StreetGen.FLOOR;
      if (horizontal || vertical) candidates.push({x, y, horizontal, order: random()});
    }
    const doors = [];
    for (const {x, y, horizontal} of candidates.sort((a, b) => a.order - b.order)) {
      if (doors.some(p => Math.max(Math.abs(p.x - x), Math.abs(p.y - y)) < 5)) continue;
      doors.push({x, y, horizontal});
      if (doors.length === 16) break;
    }
    return doors;
  }

  // The vault renderer chooses the material after painting its water, paths and room floors.
  function endingWalkableSurface(vault, x, y) {
    const tile = endingTile(vault.ending, x - vault.x, y - vault.y);
    return tile !== ' ' && tile !== '#';
  }

  function renderBase(map, surface, doorSprite, isPlatform, wallDecorations, reserved, decorate, endingVault) {
    const {w, h, cells} = map;
    const {decorations} = wallDecorations;
    map.doors = placeDoors(map, reserved, decorations);
    const wallMap = endingVault?.wardDoors.length
      ? {...map, doors:[...map.doors, ...endingVault.wardDoors]} : map;
    wallDecorations.fill(map.doors);
    const wall = (x, y, tiles = cells) => x >= 0 && y >= 0 && x < w && y < h && tiles[y * w + x] === StreetGen.WALL;
    return art.sprite(w * 32, h * 32, layer => {
      layer.fillStyle = '#14191e';
      layer.fillRect(0, 0, w * 32, h * 32);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        let tile;
        if (wall(x, y)) {
          const walls = DoorFit159.wallCells(wallMap, x, y);
          const mask = neighbors.reduce((bits, [dx, dy], bit) =>
            wall(x + dx, y + dy, walls) ? bits | (1 << bit) : bits, 0);
          tile = surface.wallTile(mask, x, y);
          if (endingVault) {
            const dx = x - endingVault.x, dy = y - endingVault.y;
            const {ending} = endingVault;
            const doorway = dy === ending.depth-1 && Math.abs(dx-ending.entry.x) <= 1;
            if (!doorway && endingTile(ending,dx,dy) === '#') tile = endingWallTile(ending.id,tile,mask,dx);
          }
        } else {
          const platform = isPlatform(x, y);
          tile = surface.floorTile(x, y, platform);
          layer.drawImage(tile, x * 32, y * 32);
          const inVault = endingVault && endingWalkableSurface(endingVault, x, y);
          if (!inVault) FloorOvergrowth.draw(layer, platform ? 'wood' : 'tile', map.seed, x, y);
          continue;
        }
        layer.drawImage(tile, x * 32, y * 32);
      }
      for (const door of map.doors) {
        DoorFit159.drawFitted(layer,map,door,doorSprite,layer.canvas,(DoorFit159.frame.canvasW-DoorFit159.frame.w)/2);
      }
      decorate(layer);
      for (const {sprite, x, y} of decorations) layer.drawImage(sprite, x * 32, y * 32);
      layer.drawImage(up, map.upstairs.x * 32, map.upstairs.y * 32);
      if (map.exitType !== 'wall') layer.drawImage(down, map.exit.x * 32, map.exit.y * 32);
    });
  }

  function render(seed, floor) {
    const floorSeed = `${seed}:rehearsal:${floor}`;
    const count = layout => Number(Boolean(layout.booth)) + Object.keys(layout.vaults).length;
    let layout = buildLayout(floorSeed);
    for (let attempt = 1; attempt <= 4 && count(layout) < 3; attempt++) {
      const candidate = buildLayout(`${floorSeed}:vaults:${attempt}`);
      if (count(candidate) > count(layout)) layout = candidate;
    }
    const {next, stages, stageMarks, booth, vaults} = layout;
    const {w, cells} = next;
    const reserved = Object.values(vaults);
    if (booth) reserved.push({...booth, ...glassStudioSize});
    const wallDecorations = createWallDecorationPlan(next, studioWallChoices, reserved);
    const isPlatform = (x, y) => stages.some(stage => x >= stage.x && x < stage.x + stage.width
      && y >= stage.y && y < stage.y + 4);
    const source = renderBase(next, art, doors.studio, isPlatform, wallDecorations, reserved, layer => {
      layer.fillStyle = '#bf9c70';
      for (const {x, y} of stageMarks) {
        for (const dx of [6, 82]) layer.fillRect(x * 32 + dx, y * 32 + 103, 6, 2);
      }
      if (booth) layer.drawImage(glassStudio, booth.x * 32, booth.y * 32);
      for (const [kind, site] of Object.entries(vaults)) {
        layer.drawImage(vaultArt[kind], site.x * 32, site.y * 32);
      }
    });
    if (booth) for (const {x, y} of booth.glass) cells[y * w + x] = StreetGen.WALL;
    for (const {blocked} of Object.values(vaults)) {
      for (const {x, y, tile} of blocked) cells[y * w + x] = tile;
    }
    const center = ({x, y, width, height}) => ({x: x + (width - 1) / 2, y: y + (height - 1) / 2});
    const points = {studio: {x: stages[0].cx, y: stages[0].y + 1}};
    if (booth) points.booth = center({...booth, ...glassStudioSize});
    for (const [kind, site] of Object.entries(vaults)) points[kind] = center(site);
    return {map: next, source, points, decorations: wallDecorations.decorations};
  }

  function buildEquipmentLayout(seed, floor) {
    const profile = {courts: 3, wideChance: .9, extraLinks: .65, avenues: 2, minRoomWidth: 8, minRoomHeight: 5};
    const floorSeed = `${seed}:equipment:${floor}`;
    let best;
    for (let attempt = 0; attempt <= 4; attempt++) {
      const variant = attempt === 0 ? floorSeed : `${floorSeed}:bays:${attempt}`;
      const map = StreetGen.generate(variant, 80, 70, 'floor', profile);
      for (const {x, y} of map.props) map.cells[y * map.w + x] = StreetGen.FLOOR;
      const bays = placeEquipmentFloorBays(map);
      const count = Object.keys(bays).length;
      if (!best || count > best.count) best = {map, bays, count};
      if (count === Object.keys(equipmentArt.bays).length) break;
    }
    return best;
  }

  function renderEquipment(seed, floor) {
    const {map, bays} = buildEquipmentLayout(seed, floor);
    const reserved = Object.values(bays).map(({x, y, width, depth}) => ({x, y: y - 1, width, height: depth + 1}));
    const wallDecorations = createWallDecorationPlan(map, equipmentWallChoices, reserved);
    blockEquipmentFloorBays(map, bays);
    const workAreas = placeStageWorkAreas(map, bays, workAreaArt);
    const points = {};
    const source = renderBase(map, equipmentArt, doors.equipment, () => false, wallDecorations, reserved, layer => {
      for (const [kind, {x, y, width}] of Object.entries(bays)) {
        layer.drawImage(equipmentArt.bays[kind], x * 32, (y - 1) * 32);
        points[kind] = {x: x + (width - 1) / 2, y: y + (kind === 'loading' || kind === 'service' ? 1 : 0)};
      }
      if (bays.loading) {
        const {x, y, cartColumn} = bays.loading;
        layer.drawImage(equipmentArt.cart, (x + cartColumn) * 32, (y + 2) * 32);
      }
      drawStageWorkAreas(layer, workAreas, workAreaArt);
    });
    const {decorations} = wallDecorations;
    for (const {id, x, y, width} of decorations) points[id] ??= {x: x + (width - 1) / 2, y};
    return {map, source, points, decorations, workAreas};
  }

  function renderDock(seed, ending) {
    const layout = buildLoadingDock(seed, ending);
    const {map, lift, warehouse, shutter, vault} = layout;
    const inspectionWidth = 6 + dockArt.inspectionWindow.width / 32;
    const shutterArea = {...shutter, width: Math.max(shutter.width, inspectionWidth)};
    const reserved = [lift, warehouse, shutterArea, vault]
      .map(({x, y, width, depth}) => ({x: x - 1, y: y - 1, width: width + 2, height: depth + 1}));
    const wallDecorations = createWallDecorationPlan(map, dockWallChoices, reserved);
    const workAreas = placeStageWorkAreas(map, {lift, warehouse, shutter: shutterArea}, workAreaArt, [vault]);
    const source = renderBase(map, dockArt, doors.dock, () => false, wallDecorations, reserved, layer => {
      drawLoadingDock(layer, dockArt, layout, deepWater, gardenSprites, archiveConcrete);
      drawStageWorkAreas(layer, workAreas, workAreaArt);
    }, vault);
    const points = {
      freight: {x: lift.x + (lift.width - 1) / 2, y: lift.y + 1},
      warehouse: {x: warehouse.x + 3.5, y: warehouse.y + 2},
      'goods-gate': {x: shutter.x + (shutter.width - 1) / 2, y: shutter.y},
      ending: {x: vault.x + (vault.width - 1) / 2, y: vault.y + (vault.depth - 1) / 2,
        width: vault.width, depth: vault.depth},
    };
    const officeExit = vault.exitDoor && officeExitControl(source, map, vault.exitDoor);
    if (vault.wardDoors.length) {
      const first = vault.wardDoors[0], last = vault.wardDoors[vault.wardDoors.length - 1];
      points['ward-doors'] = {x:first.x, y:(first.y + last.y)/2};
    }
    const wardControls = vault.wardDoors.map(door => {
      const layer = source.getContext('2d'), px = door.x * 32, py = door.y * 32;
      const {frame} = DoorFit159;
      const spriteInset = (frame.canvasW-frame.w)/2;
      DoorFit159.prepareDoorway(layer,map,door,source);
      const threshold = layer.getImageData(px,py,frame.canvasW,frame.h);
      const control = {open:false, setOpen(open) {
        this.open = open;
        map.cells[door.y*map.w+door.x] = open ? StreetGen.FLOOR : StreetGen.BARRIER;
        layer.putImageData(threshold,px,py);
        DoorFit159.drawLeaf(layer,map,door,open ? doors.wardOpen : doors.ward,spriteInset);
      }};
      control.setOpen(false);
      return control;
    });
    return {map, source, points, decorations: wallDecorations.decorations, workAreas, vault, officeExit, wardControls};
  }

  function draw() {
    const latch = byId('office-latch');
    latch.hidden = !(setOfficeExit && focus === 'ending');
    latch.textContent = exitOpen ? '사무실 문 닫기' : '사무실 안쪽 빗장 열기';
    wardButtons.forEach((button,i) => {
      const control = wardControls[i];
      button.hidden = !control || (focus !== 'ending' && focus !== 'ward-doors');
      button.textContent = button.dataset.ward + ' 병실 문 ' + (control?.open ? '닫기' : '열기');
    });
    const overview = focus === 'overview';
    const point = points[focus] || map.start;
    const endingScale = points.ending && Math.min(1, field.width / ((points.ending.width + 4) * 32),
      field.height / ((points.ending.depth + 4) * 32));
    const scale = overview ? .25 : focus === 'ending' ? endingScale : focus === 'ward-doors' ? 2 : 1.5;
    const width = map.w * 32 * scale;
    const height = map.h * 32 * scale;
    const offset = (coordinate, screen, extent) => {
      if (overview) return Math.floor((screen - extent) / 2);
      const centered = Math.round(screen / 2 - (coordinate + .5) * 32 * scale);
      if (focus === 'ending') return centered;
      return -Math.max(0, Math.min(extent - screen, -centered));
    };
    ctx.fillStyle = '#101419';
    ctx.fillRect(0, 0, field.width, field.height);
    const left = offset(point.x, field.width, width);
    const top = offset(point.y, field.height, height);
    ctx.drawImage(rendered, left, top, width, height);
    const canShowRoutes = reviewPaths.length > 0 && (focus === 'ending' || overview);
    byId('routes-label').hidden = !canShowRoutes;
    if (canShowRoutes && routeToggle.checked) {
      ctx.save();
      ctx.translate(left, top);
      ctx.scale(scale, scale);
      for (const [i, path] of reviewPaths.entries()) {
        ctx.beginPath();
        for (const [step, tile] of path.entries()) {
          const x = (tile.x + .5) * 32, y = (tile.y + .5) * 32;
          if (step === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.lineJoin = 'round';
        ctx.setLineDash([]);
        ctx.strokeStyle = '#28252d';
        ctx.lineWidth = 5;
        ctx.stroke();
        ctx.strokeStyle = ['#ede3c9', '#84d8cf', '#f0bb78'][i];
        ctx.setLineDash(i === 2 ? [8, 5] : []);
        ctx.lineWidth = 3;
        ctx.stroke();
      }
      ctx.restore();
    }
    for (const id of views) byId(id).setAttribute('aria-pressed', String(focus === id));
  }

  function renderFloor(seed, floor) {
    const ending = floor === 5 ? pickStageEnding(seed, seed === originalSeed) : null;
    const renderLayout = ending ? (variant => renderDock(variant, ending)) : floor >= 3 ? renderEquipment : render;
    const first = renderLayout(seed, floor);
    if (first.map.doors.length) return first;
    for (let attempt = 1; attempt <= 6; attempt++) {
      const candidate = renderLayout(`${seed}:door-layout:${attempt}`, floor);
      if (candidate.map.doors.length) return candidate;
    }
    return first;
  }

  function generate() {
    const floor = Number(floorSelect.value);
    const seed = seedInput.value.trim() || 'rehearsal-01';
    const isDock = floor === 5;
    const isEquipment = floor === 3 || floor === 4;
    const result = renderFloor(seed, floor);
    const {workAreas = [], vault} = result;
    setOfficeExit = result.officeExit;
    wardControls = result.wardControls || [];
    exitOpen = false;
    ({map, source: rendered, points, decorations} = result);
    reviewPaths = [];
    if (vault?.ending.reviewRoutes) {
      const branches = vault.ending.reviewRoutes.map(stops => stops.map(([x,y]) => ({x:vault.x+x, y:vault.y+y})));
      const routes = [[vault.entry, branches[0][0]], ...branches.map(branch => [...branch, vault.reward])];
      reviewPaths = routes.map(stops => {
        const path = [stops[0]];
        for (const stop of stops.slice(1)) {
          const segment = StreetGen.route(map, path[path.length - 1], stop);
          if (!segment.length) return [];
          path.push(...segment.slice(1));
        }
        return path;
      });
      if (reviewPaths.some(path => !path.length)) reviewPaths = [];
    }
    if (decorations.length) {
      const {x, y, width} = decorations[0];
      points['wall-decor'] = {x: x + (width - 1) / 2, y};
    }
    if (workAreas.length) {
      const {x, y, width, depth} = workAreas[0];
      points['work-area'] = {x: x + (width - 1) / 2, y: y + (depth - 1) / 2};
    }
    if (map.doors.length) points.door = map.doors[0];
    if (vault) byId('ending').textContent = vault.ending.name;
    byId('ending-examples').hidden = !isDock;
    endingExample.value = exampleSeeds.includes(seed) ? seed : '';
    const goodsEntry = byId('goods-entry');
    goodsEntry.hidden = !isDock;
    if (isDock) goodsEntry.href = '../forbidden-goods01/?' + new URLSearchParams({ seed, view: 'arrival' });
    for (const id of views.slice(1)) byId(id).hidden = !points[id];
    if (focus !== 'overview' && !points[focus]) focus = Object.keys(points)[0] || 'overview';
    seedInput.value = seed;
    const theme = isDock ? '지하 세트 하역장' : isEquipment ? '무대 설비층' : '리허설 스튜디오';
    const title = `방송 지하무대 ${floor}층 · ${theme}`;
    byId('title').textContent = document.title = title;
    field.setAttribute('aria-label', title + ' 지도');
    const params = new URLSearchParams({seed, floor, view: focus});
    if (seed !== originalSeed) params.set('pool','14');
    if (reviewPaths.length && routeToggle.checked) params.set('routes', '1');
    if (useArchiveConcrete) params.set('material','concrete');
    history.replaceState(null, '', '?' + params);
    const props = isDock ? '화물 리프트, 세트 보관창고, 금지된 굿즈 창고 셔터'
      : isEquipment ? '조명 제어, 매립 덕트, 승강기, 조명 정비 구역' : '목재 리허설 바닥과 흡음 패널 벽';
    const workAreaStatus = isDock || isEquipment ? ` · 보조 작업 구역 ${workAreas.length}곳` : '';
    const doorName = isDock ? '하역장 문' : isEquipment ? '철제 설비문' : '방음문';
    byId('door').textContent = `${doorName} 확대`;
    const endingStatus = vault ? ` · 보상 고정지형 ${vault.ending.width}×${vault.ending.depth}칸` : '';
    status.textContent = `80×70칸 · ${props} · 랜덤 벽 장식 ${decorations.length}개${workAreaStatus} · ${doorName} ${map.doors.length}개${endingStatus}`;
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
  routeToggle.onchange = () => {
    const params = new URLSearchParams(location.search);
    if (routeToggle.checked) params.set('routes', '1');
    else params.delete('routes');
    history.replaceState(null, '', '?' + params);
    draw();
  };
  endingExample.onchange = () => {
    originalSeed = null;
    seedInput.value = endingExample.value;
    focus = 'ending';
    refresh();
  };
  byId('office-latch').onclick = () => {
    if (!setOfficeExit) return;
    exitOpen = !exitOpen;
    setOfficeExit(exitOpen);
    draw();
  };
  wardButtons.forEach((button,i) => {
    button.onclick = () => {
      const control = wardControls[i];
      if (control) { control.setOpen(!control.open); draw(); }
    };
  });
  byId('random').onclick = () => {
    originalSeed = null;
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
