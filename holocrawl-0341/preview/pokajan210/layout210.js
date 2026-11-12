(function () {
  'use strict';
  const w = 24, h = 21, offset = 3;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y * w + x;
  const absolute = item => ({...item,x:item.x + offset,y:item.y + offset});
  function generate(mode) {
    const cells = Array(w * h).fill(1), inner = cells.map(() => false), building = inner.slice();
    for (const [x,y,width,height] of [[3,1,12,2],[1,3,16,7],[3,10,12,3]]) {
      for (let dy = 0; dy < height; dy++) for (let dx = 0; dx < width; dx++)
        inner[index(x + offset + dx,y + offset + dy)] = true;
    }
    if (mode === 'attached') cells.fill(0,0,(offset + 1) * w);
    for (let i = 0; i < inner.length; i++) {
      if (!inner[i]) continue;
      cells[i] = 1;
      for (const [dx,dy] of dirs) {
        const n = index(i % w + dx,Math.floor(i / w) + dy);
        if (!inner[n]) { cells[n] = 0; building[n] = true; }
      }
    }
    const entry = absolute({x:8,y:13,w:2,h:1});
    const doorway = [index(entry.x,entry.y),index(entry.x + 1,entry.y)];
    for (const i of doorway) cells[i] = 1;
    const props = [
      {id:'cards',label:'카드 보관장',x:4,y:1,w:3,h:2},
      {id:'board',label:'대국 안내판',x:10,y:1,w:3,h:2},
      {id:'table',label:'4인 포카쟝 테이블',x:7,y:5,w:3,h:3},
      {id:'chair',label:'대국 좌석',x:8,y:4,w:1,h:1,facing:'south'},
      {id:'chair',label:'대국 좌석',x:8,y:8,w:1,h:1,facing:'north'},
      {id:'chair',label:'대국 좌석',x:6,y:6,w:1,h:1,facing:'east'},
      {id:'chair',label:'대국 좌석',x:10,y:6,w:1,h:1,facing:'west'},
      {id:'reception',label:'접수대 · 카드 배부',x:2,y:7,w:3,h:2},
      {id:'bench',label:'관전석',x:13,y:6,w:3,h:1},
      {id:'bench',label:'대기석',x:12,y:10,w:3,h:1},
      {id:'drinks',label:'음료 선반',x:14,y:8,w:2,h:2},
      {id:'plant',label:'장식 화분',x:3,y:11,w:1,h:1},
      {id:'plant',label:'장식 화분',x:14,y:3,w:1,h:1}
    ].map(absolute);
    const open = cells.slice();
    for (const p of props) for (let dy = 0; dy < p.h; dy++) for (let dx = 0; dx < p.w; dx++)
      open[index(p.x + dx,p.y + dy)] = 0;
    const servicePoints = [[5,3],[11,3],[8,3],[8,9],[5,6],[11,6],[3,9],[14,7],[13,11],[13,9]]
      .map(([x,y]) => absolute({x,y}));
    return {w,h,offset,cells,inner,building,props,entry,doorway,open,servicePoints,
      start:{x:entry.x,y:entry.y + 2},rug:absolute({x:6,y:4,w:5,h:5})};
  }
  function distances(map,doorOpen) {
    const seen = new Set([index(map.start.x,map.start.y)]), queue = [map.start];
    for (const {x,y} of queue) for (const [dx,dy] of dirs) {
      if (dx && dy) continue;
      const nx = x + dx, ny = y + dy, i = index(nx,ny);
      if (nx < 0 || nx >= w || ny < 0 || ny >= h || !map.open[i] || seen.has(i) ||
          (!doorOpen && map.doorway.includes(i))) continue;
      seen.add(i); queue.push({x:nx,y:ny});
    }
    return seen;
  }
  window.PokajanLayout210 = {generate,distances,dirs,index};
})();
