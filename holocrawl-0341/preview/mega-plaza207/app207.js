(async function () {
  'use strict';
  const tileSize = 32;
  const byId = id => document.getElementById(id);
  const images = {}, maps = {}, canvases = {};
  const theme = {material:'plaster',face:[72,93,110],top:[36,43,54],accent:[142,170,172]};

  async function load(id,url) {
    const image = new Image();
    image.src = url;
    await image.decode();
    images[id] = image;
  }
  await Promise.all([
    WallHeight121.load(),
    PlazaSprites207.load(),
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
    for (const [index,[dx,dy]] of PlazaLayout207.dirs.entries()) {
      const nx = x + dx, ny = y + dy;
      if (nx >= 0 && ny >= 0 && nx < map.w && ny < map.h && !map.cells[ny * map.w + nx]) {
        mask |= 1 << index;
      }
    }
    return mask;
  }

  function drawFloor(context,x,y) {
    const variant = RandomFloor.index('MEGA-PLAZA207',0,x,y) % floors.length;
    context.drawImage(floors[variant],x * tileSize,y * tileSize);
  }

  function paving(context,map) {
    const {x,y}=map.origin, at=dx=>(x*32+dx), top=y*32;
    context.fillStyle='rgba(151,130,139,.13)';
    context.fillRect(at(13*32),top+11*32,96,7*32);
    context.fillRect(at(4*32),top+15*32,21*32,32);
    const cx=at(14*32+16),cy=top+13*32+17;
    const steps=[[146,0],[138,26],[114,48],[78,63],[42,69],[0,72]];
    for(let dy=-72;dy<=72;dy++){
      const yy=Math.abs(dy);
      for(let i=1;i<steps.length;i++){
        const [a,y0]=steps[i-1],[b,y1]=steps[i];
        if(yy>y1)continue;
        const reach=Math.round(a+(b-a)*(yy-y0)/(y1-y0));
        context.fillStyle='rgba(153,142,151,.22)';
        context.fillRect(cx-reach,cy+dy,reach*2+1,1);
        if(yy%9<4 && reach>12){
          context.fillStyle='rgba(176,161,147,.33)';
          context.fillRect(cx-reach+4,cy+dy,3,1);
          context.fillRect(cx+reach-6,cy+dy,3,1);
        }
        break;
      }
    }
    context.fillStyle='rgba(177,158,136,.40)';
    context.fillRect(cx-23,cy-2,47,5);
    context.fillRect(cx-2,cy-15,5,31);
    context.fillStyle='rgba(182,160,170,.43)';
    for(let i=0;i<10;i++) {
      const q=Math.floor(i/2);
      context.fillRect(cx-10+q,cy-10+i,3,1);
      context.fillRect(cx+8-q,cy-10+i,3,1);
      context.fillRect(cx-10+q,cy+10-i,3,1);
      context.fillRect(cx+8-q,cy+10-i,3,1);
    }
  }

  function draw(mode) {
    const map=maps[mode],context=canvases[mode].getContext('2d');
    context.imageSmoothingEnabled=false;
    for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){
      const i=y*map.w+x;
      drawFloor(context,x,y);
      if(map.inner[i]){
        context.fillStyle='rgba(71,77,108,.22)';
        context.fillRect(x*32,y*32,32,32);
      }
      if(!map.cells[i]){
        if(map.building[i])context.drawImage(FacilityMaterial171.tile(wallMask(map,x,y),x,y,theme),x*32,y*32);
        else WallHeight121.wall(context,map.cells,map.w,map.h,x,y,32);
      }
    }
    paving(context,map);
    for(const p of map.props)PlazaSprites207.draw(context,p);
    PlazaSprites207.gate(context,map.entry);
    if(byId('grid').checked) {
      context.strokeStyle='rgba(192,211,215,.23)';
      for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++)context.strokeRect(x*32+.5,y*32+.5,31,31);
    }
    if(byId('paths').checked) {
      const seen=PlazaLayout207.reachable(map);
      context.fillStyle='rgba(123,198,169,.14)';
      for(const i of seen)if(map.inner[i])context.fillRect(i%map.w*32,Math.floor(i/map.w)*32,32,32);
      context.fillStyle='#b9e5ca';
      for(const p of map.points)context.fillRect(p.x*32+13,p.y*32+13,6,6);
    }
    if(byId('labels').checked) {
      context.font='15px system-ui';
      context.textAlign='center';
      for(const p of map.props) {
        const x=(p.x+p.w/2)*32,y=p.y*32,width=context.measureText(p.label).width+14;
        context.fillStyle='#293545';context.fillRect(x-width/2,y-13,width,21);
        context.fillStyle='#e1e9e9';context.fillText(p.label,x,y+3);
      }
    }
  }

  function redraw() {
    const mode=byId('mode').value;
    draw(mode);
    for(const item of document.querySelectorAll('figure'))item.hidden=item.dataset.layout!==mode;
  }
  for (const mode of ['attached','standalone']) {
    const map = maps[mode] = PlazaLayout207.generate(mode);
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
      byId('title').textContent = '메가코스터 광장 · ' + (mode === 'attached' ? '벽붙임' : '독립 배치');
      byId('detail').showModal();
    };
  }
  byId('mode').onchange = byId('paths').onchange = redraw;
  byId('grid').onchange = byId('labels').onchange = redraw;
  byId('close').onclick = () => byId('detail').close();
  redraw();
  window.PlazaArt207 = {maps,canvases};
  window.plaza207Ready = true;
})().catch(error => {
  console.error(error);
  document.getElementById('status').textContent = '불러오기 실패: ' + error.message;
});
