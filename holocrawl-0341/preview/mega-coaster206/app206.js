(async function () {
  'use strict';
  const tileSize = 32;
  const byId = id => document.getElementById(id);
  const images = {}, maps = {}, canvases = {};
  const theme = {material:'plaster',face:[72,93,110],top:[36,43,54],accent:[142,170,172]};
  let opened = false;

  async function load(id,url) {
    const image = new Image();
    image.src = url;
    await image.decode();
    images[id] = image;
  }
  await Promise.all([
    WallHeight121.load(),
    load('floor','../native-play107/assets/floor.png')
  ]);
  while (!window.material171Ready) {
    if (window.material171Error) throw Error(window.material171Error);
    await new Promise(resolve => setTimeout(resolve,25));
  }
  const response = await fetch('../native-play107/maps/map-10786001-1.json');
  if (!response.ok) throw Error('바닥 타일 자료를 불러올 수 없습니다.');
  const source = await response.json();
  const counts = new Map();
  for (const id of source.floors) counts.set(id,(counts.get(id) || 0) + 1);
  const floorIds = [...counts].sort((a,b) => b[1] - a[1]).map(([id]) => id)
    .filter(id => source.palette[id].atlas === 'floor').slice(0,4);
  const floors = [];
  for (const id of floorIds) {
    const tile = source.palette[id];
    for (let turn = 0; turn < 4; turn++) {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = tileSize;
      const context = canvas.getContext('2d');
      context.translate(16,16);
      context.rotate(turn * Math.PI / 2);
      context.drawImage(images.floor,tile.sx,tile.sy,32,32,-16,-16,32,32);
      floors.push(canvas);
    }
  }

  function wallMask(map,x,y) {
    let mask = 0;
    for (const [index,[dx,dy]] of CoasterLayout206.dirs.entries()) {
      const nx = x + dx, ny = y + dy;
      if (nx >= 0 && ny >= 0 && nx < map.w && ny < map.h && !map.cells[ny * map.w + nx]) {
        mask |= 1 << index;
      }
    }
    return mask;
  }

  function drawFloor(context,x,y) {
    const variant = RandomFloor.index('MEGA-COASTER206',0,x,y) % floors.length;
    context.drawImage(floors[variant],x * tileSize,y * tileSize);
  }

  function draw(mode) {
    const map = maps[mode], context = canvases[mode].getContext('2d');
    context.imageSmoothingEnabled = false;
    for (let y = 0; y < map.h; y++) {
      for (let x = 0; x < map.w; x++) {
        const i = y * map.w + x;
        drawFloor(context,x,y);
        if (map.inner[i]) {
          context.fillStyle = 'rgba(68,83,112,.22)';
          context.fillRect(x * tileSize,y * tileSize,tileSize,tileSize);
        }
        if (map.cells[i]) continue;
        if (map.building[i]) {
          context.drawImage(FacilityMaterial171.tile(wallMask(map,x,y),x,y,theme),x * tileSize,y * tileSize);
        } else {
          WallHeight121.wall(context,map.cells,map.w,map.h,x,y,tileSize);
        }
      }
    }
    for (const prop of map.props) CoasterSprites206.draw(context,prop);
    CoasterSprites206.door(context,map.entry,opened);
    if (byId('grid').checked) {
      context.strokeStyle = 'rgba(192,211,215,.22)';
      for (let y = 0; y < map.h; y++) {
        for (let x = 0; x < map.w; x++) context.strokeRect(x * 32 + .5,y * 32 + .5,31,31);
      }
    }
    if (byId('labels').checked) {
      context.font = '11px system-ui';
      context.textAlign = 'center';
      for (const p of map.props) {
        const x = (p.x + p.w / 2) * 32, y = p.y * 32;
        const width = context.measureText(p.label).width + 12;
        context.fillStyle = '#253945';
        context.fillRect(x - width / 2,y - 16,width,15);
        context.fillStyle = '#e1e9e9';
        context.fillText(p.label,x,y - 5);
      }
    }
  }

  function redraw() {
    for (const mode of ['attached','standalone']) draw(mode);
    byId('door').textContent = opened ? '문 닫기' : '문 열기';
    byId('status').textContent = '19×14칸 · ' + (opened ? '문 열림' : '문 닫힘');
  }
  for (const mode of ['attached','standalone']) {
    const map = maps[mode] = CoasterLayout206.generate(mode);
    const canvas = canvases[mode] = byId(mode);
    canvas.width = map.w * tileSize;
    canvas.height = map.h * tileSize;
    document.querySelector('[data-mode=' + mode + ']').onclick = () => {
      const zoom = byId('zoom');
      zoom.width = canvas.width * 2;
      zoom.height = canvas.height * 2;
      const context = zoom.getContext('2d');
      context.imageSmoothingEnabled = false;
      context.drawImage(canvas,0,0,zoom.width,zoom.height);
      byId('title').textContent = '메가코스터 · ' + (mode === 'attached' ? '벽붙임' : '독립 배치');
      byId('detail').showModal();
    };
  }
  byId('door').onclick = () => { opened = !opened; redraw(); };
  byId('grid').onchange = byId('labels').onchange = redraw;
  byId('close').onclick = () => byId('detail').close();
  redraw();
  window.CoasterArt206 = {maps,canvases,images,getOpened:() => opened};
  window.coaster206Ready = true;
})().catch(error => {
  console.error(error);
  document.getElementById('status').textContent = '불러오기 실패: ' + error.message;
});
