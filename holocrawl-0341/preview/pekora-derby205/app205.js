(async function () {
  'use strict';
  const tileSize = 32;
  const byId = id => document.getElementById(id);
  const images = {}, maps = {}, canvases = {};
  const theme = {material:'plaster',face:[161,144,119],top:[54,47,43],accent:[219,201,166]};
  const wallTiles = new Map();
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
    ...['track','ticket-counter','carrot-trophy'].map(id => load(id,'../pekora-derby204/assets/' + id + '-native.png'))
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

  function derbyWall(mask,x,y) {
    const key = [mask,x % 4,y % 2].join(':');
    if (wallTiles.has(key)) return wallTiles.get(key);
    const tile = document.createElement('canvas');
    tile.width = tile.height = tileSize;
    const context = tile.getContext('2d');
    context.drawImage(FacilityMaterial171.tile(mask,x,y,theme),0,0);
    const pixels = context.getImageData(0,0,32,32);
    const plane = FacilityMaterial171.planes[String(mask)];
    for (let py = 23; py < 31; py++) {
      for (let px = 0; px < 32; px++) {
        if (plane[py * 32 + px] !== '1') continue;
        const i = (py * 32 + px) * 4;
        const shade = py === 23 ? [180,151,104] : py === 24 ? [120,96,69] : [94,75,61];
        pixels.data.set(shade,i);
      }
    }
    context.putImageData(pixels,0,0);
    wallTiles.set(key,tile);
    return tile;
  }

  function drawDoor(context,entry) {
    const x = entry.x * tileSize, y = entry.y * tileSize;
    const fill = (color,dx,dy,w,h) => {
      context.fillStyle = color;
      context.fillRect(x + dx,y + dy,w,h);
    };
    fill('#5e4b3d',0,0,64,11);
    fill('#c3aa80',0,0,64,1);
    fill('#a88b61',0,10,64,1);
    for (const side of [8,40]) {
      for (let col = 0; col < 4; col++) {
        for (let row = 0; row < 2; row++) {
          const light = (col + row) % 2 === 0;
          fill(light ? '#e1d5b8' : '#51413a',side + col * 4,2 + row * 4,4,4);
        }
      }
    }
    // Small rabbit emblem cut into the frame above the doorway.
    fill('#e1d5b8',27,4,10,5);
    fill('#e1d5b8',28,1,2,5);
    fill('#e1d5b8',34,1,2,5);
    fill('#51413a',29,6,1,1);
    fill('#51413a',34,6,1,1);
    fill('#cfb78f',0,11,4,19);
    fill('#cfb78f',60,11,4,19);
    fill('#8e7050',3,11,1,19);
    fill('#8e7050',60,11,1,19);
    if (opened) {
      fill('#8e7050',4,11,3,19);
      fill('#8e7050',57,11,3,19);
    } else {
      for (const start of [4,32]) {
        fill('#80664f',start,11,28,19);
        fill('#b4976d',start + 2,12,24,2);
        fill('#414c44',start + 4,15,20,11);
        fill('#697060',start + 4,15,20,1);
        const handle = start === 4 ? start + 23 : start + 3;
        fill('#d0b47f',handle,21,2,4);
      }
      fill('#433630',31,11,2,19);
    }
    fill('#b49b75',0,30,64,1);
    fill('#625142',0,31,64,1);
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
          context.drawImage(derbyWall(wallMask(map,x,y),x,y),x * tileSize,y * tileSize);
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
  window.DerbyArt205 = {maps,canvases,images,getOpened:() => opened};
  window.derby205Ready = true;
})().catch(error => {
  console.error(error);
  document.getElementById('status').textContent = '불러오기 실패: ' + error.message;
});
