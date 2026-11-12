(async function () {
  'use strict';
  const tileSize = 32;
  const byId = id => document.getElementById(id);
  const images = {}, maps = {}, canvases = {};
  const theme = {material:'plaster',face:[83,108,121],top:[34,44,52],accent:[161,179,178]};
  let opened = false;

  async function load(id,url) {
    const image = new Image();
    image.src = url;
    await image.decode();
    images[id] = image;
  }
  await Promise.all([
    WallHeight121.load(),
    load('floor','../native-play107/assets/floor.png'),
    ...['track','ticket-counter','carrot-trophy'].map(id => load(id,'assets/' + id + '-native.png'))
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
    for (const [index,[dx,dy]] of DerbyLayout204.dirs.entries()) {
      const nx = x + dx, ny = y + dy;
      if (nx >= 0 && ny >= 0 && nx < map.w && ny < map.h && !map.cells[ny * map.w + nx]) {
        mask |= 1 << index;
      }
    }
    return mask;
  }

  function drawFloor(context,x,y) {
    const variant = RandomFloor.index('PEKORA-DERBY204',0,x,y) % floors.length;
    context.drawImage(floors[variant],x * tileSize,y * tileSize);
  }

  function drawBench(context,bench) {
    const x = bench.x * tileSize, y = bench.y * tileSize;
    context.fillStyle = '#293137';
    context.fillRect(x + 3,y + 25,58,5);
    context.fillStyle = '#55626a';
    context.fillRect(x + 5,y + 20,4,9);
    context.fillRect(x + 55,y + 20,4,9);
    context.fillStyle = '#688c9b';
    context.fillRect(x + 3,y + 8,58,6);
    context.fillRect(x + 3,y + 17,58,7);
    context.fillStyle = '#a4bcc0';
    context.fillRect(x + 3,y + 8,58,2);
    context.fillRect(x + 3,y + 17,58,2);
  }

  function drawDoor(context,entry) {
    const x = entry.x * tileSize, y = entry.y * tileSize;
    const fill = (color,dx,dy,w,h) => {
      context.fillStyle = color;
      context.fillRect(x + dx,y + dy,w,h);
    };
    fill('#303e49',0,0,64,9);
    fill('#9db1b7',0,0,64,1);
    for (let i = 0; i < 12; i++) {
      fill(i % 2 ? '#587580' : '#d4ccaf',8 + i * 4,3,4,3);
    }
    fill('#9db1b7',0,8,64,1);
    fill('#a9b7b7',0,9,3,21);
    fill('#a9b7b7',61,9,3,21);
    if (!opened) {
      for (const start of [3,32]) {
        fill('#567683',start,9,29,21);
        fill('#91aab1',start + 2,11,25,2);
        fill('#354b58',start + 4,14,21,12);
        fill('#748f98',start + 4,14,21,1);
        fill('#c5a778',start + 12,20,4,2);
      }
      fill('#293741',31,9,2,21);
    } else {
      fill('#557582',3,9,3,21);
      fill('#557582',58,9,3,21);
    }
    fill('#a9b7b7',0,30,64,1);
    fill('#4d5d64',0,31,64,1);
  }

  function draw(mode) {
    const map = maps[mode], context = canvases[mode].getContext('2d');
    context.imageSmoothingEnabled = false;
    for (let y = 0; y < map.h; y++) {
      for (let x = 0; x < map.w; x++) {
        const i = y * map.w + x;
        drawFloor(context,x,y);
        if (map.inner[i]) {
          context.fillStyle = 'rgba(68,105,117,.20)';
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
    for (const bench of map.benches) drawBench(context,bench);
    for (const prop of map.props) {
      const image = images[prop.id];
      const x = prop.x * tileSize + (prop.w * tileSize - image.width) / 2;
      const y = (prop.y + prop.h) * tileSize - image.height;
      context.fillStyle = 'rgba(0,0,0,.25)';
      context.fillRect(x + 6,y + image.height - 4,image.width - 12,4);
      context.drawImage(image,x,y);
    }
    drawDoor(context,map.entry);
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
    byId('status').textContent = '17×13칸 · ' + (opened ? '문 열림' : '문 닫힘');
  }
  for (const mode of ['attached','standalone']) {
    const map = maps[mode] = DerbyLayout204.generate(mode);
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
      byId('title').textContent = '페코람블 더비 · ' + (mode === 'attached' ? '벽붙임' : '독립 배치');
      byId('detail').showModal();
    };
  }
  byId('door').onclick = () => { opened = !opened; redraw(); };
  byId('grid').onchange = byId('labels').onchange = redraw;
  byId('close').onclick = () => byId('detail').close();
  redraw();
  window.DerbyArt204 = {maps,canvases,images,getOpened:() => opened};
  window.derby204Ready = true;
})().catch(error => {
  console.error(error);
  document.getElementById('status').textContent = '불러오기 실패: ' + error.message;
});
