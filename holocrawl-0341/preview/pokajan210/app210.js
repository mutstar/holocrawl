(async function () {
  'use strict';
  const tileSize = 32;
  const byId = id => document.getElementById(id);
  const images = {}, maps = {}, canvases = {};
  const theme = {material:'plaster',face:[82,77,86],top:[40,39,48],accent:[157,145,113]};
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
    for (const [index,[dx,dy]] of PokajanLayout210.dirs.entries()) {
      const nx = x + dx, ny = y + dy;
      if (nx >= 0 && ny >= 0 && nx < map.w && ny < map.h && !map.cells[ny * map.w + nx]) {
        mask |= 1 << index;
      }
    }
    return mask;
  }

  function drawFloor(context,x,y) {
    const variant = RandomFloor.index('POKAJAN210',0,x,y) % floors.length;
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
          context.fillStyle = (x + y) % 2 ? '#394749' : '#3c494a';
          context.fillRect(x * tileSize,y * tileSize,tileSize,tileSize);
          context.fillStyle = '#303b3e';
          context.fillRect(x * 32,y * 32,32,1);
          context.fillRect(x * 32,y * 32,1,32);
          // Sparse wear keeps the floor quiet at native tile size.
          context.fillStyle = '#4b5553';
          if ((x * 7 + y * 11) % 5 === 0) context.fillRect(x * 32 + 7,y * 32 + 19,3,1);
        }
        if (map.cells[i]) continue;
        if (map.building[i]) {
          context.drawImage(FacilityMaterial171.tile(wallMask(map,x,y),x,y,theme),x * tileSize,y * tileSize);
        } else {
          WallHeight121.wall(context,map.cells,map.w,map.h,x,y,tileSize);
        }
      }
    }
    const r = map.rug;
    context.fillStyle = '#756751'; context.fillRect(r.x * 32-4,r.y * 32-4,r.w * 32+8,r.h * 32+8);
    context.fillStyle = '#413e49'; context.fillRect(r.x * 32-2,r.y * 32-2,r.w * 32+4,r.h * 32+4);
    context.fillStyle = '#645863'; context.fillRect(r.x * 32+2,r.y * 32+2,r.w * 32-4,r.h * 32-4);
    context.fillStyle = '#49434f'; context.fillRect(r.x * 32+5,r.y * 32+5,r.w * 32-10,r.h * 32-10);
    for (const prop of map.props) PokajanSprites210.draw(context,prop);
    PokajanSprites210.door(context,map.entry,opened);
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
    byId('status').textContent = '18×14칸 · ' + (opened ? '문 열림' : '문 닫힘');
  }
  for (const mode of ['attached','standalone']) {
    const map = maps[mode] = PokajanLayout210.generate(mode);
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
      byId('title').textContent = '포카쟝 게임실 · ' + (mode === 'attached' ? '벽붙임' : '독립 배치');
      byId('detail').showModal();
    };
  }
  byId('door').onclick = () => { opened = !opened; redraw(); };
  byId('grid').onchange = byId('labels').onchange = redraw;
  byId('close').onclick = () => byId('detail').close();
  redraw();
  window.PokajanArt210 = {maps,canvases,images,getOpened:() => opened};
  window.pokajan210Ready = true;
})().catch(error => {
  console.error(error);
  document.getElementById('status').textContent = '불러오기 실패: ' + error.message;
});
