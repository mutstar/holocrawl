(function () {
  'use strict';
  const w = 27, h = 22, offset = 4;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y * w + x;
  const absolute = item => ({...item,x:item.x + offset,y:item.y + offset});

  function generate(mode) {
    const cells = Array(w * h).fill(1);
    const inner = cells.map(() => false), building = inner.slice();
    for (const [x,y,width,height] of [[3,1,13,2],[1,3,17,6],[2,9,15,3],[5,12,9,1]]) {
      for (let dy = 0; dy < height; dy++) {
        for (let dx = 0; dx < width; dx++) inner[index(x + offset + dx,y + offset + dy)] = true;
      }
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
    const entry = absolute({x:9,y:13,w:2,h:1});
    const doorway = [index(entry.x,entry.y),index(entry.x + 1,entry.y)];
    for (const i of doorway) cells[i] = 1;
    const props = [
      {id:'coaster',label:'급강하 레일 · 정차 차량',x:4,y:2,w:12,h:5},
      {id:'platform',label:'탑승장',x:9,y:7,w:6,h:2},
      {id:'maintenance',label:'정비함',x:3,y:8,w:2,h:2},
      {id:'console',label:'운행 제어기',x:15,y:7,w:1,h:2},
      {id:'queue',label:'대기열 난간',x:10,y:10,w:4,h:1}
    ].map(absolute);
    const open = cells.slice();
    for (const p of props) {
      for (let dy = 0; dy < p.h; dy++) {
        for (let dx = 0; dx < p.w; dx++) open[index(p.x + dx,p.y + dy)] = 0;
      }
    }
    const servicePoints = [[6,7],[2,8],[5,9],[9,9],[14,9],[16,8],[10,11]]
      .map(([x,y]) => absolute({x,y}));
    return {w,h,cells,inner,building,props,entry,doorway,open,servicePoints,
      start:{x:entry.x,y:entry.y + 2}};
  }

  function distances(map,doorOpen) {
    const seen = new Set(), queue = [map.start];
    seen.add(index(map.start.x,map.start.y));
    for (const {x,y} of queue) {
      for (const [dx,dy] of dirs) {
        if (dx && dy) continue;
        const nx = x + dx, ny = y + dy, i = index(nx,ny);
        if (nx < 0 || nx >= w || ny < 0 || ny >= h || !map.open[i] || seen.has(i) ||
            (!doorOpen && map.doorway.includes(i))) continue;
        seen.add(i);
        queue.push({x:nx,y:ny});
      }
    }
    return seen;
  }

  window.CoasterLayout206 = {generate,distances,dirs,index};
})();
