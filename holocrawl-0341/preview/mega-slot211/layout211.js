(function () {
  'use strict';
  const w = 26, h = 21, offset = 3;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y * w + x;
  const absolute = item => ({...item,x:item.x + offset,y:item.y + offset});
  function generate(mode) {
    const cells = Array(w * h).fill(1), inner = cells.map(() => false), building = inner.slice();
    for (const [x,y,width,height] of [[4,1,12,2],[2,3,16,1],[1,4,18,7],[3,11,14,2]]) {
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
    const entry = absolute({x:9,y:13,w:2,h:1});
    const doorway = [index(entry.x,entry.y),index(entry.x + 1,entry.y)];
    for (const i of doorway) cells[i] = 1;
    const props = [
      {id:'mega',label:'대형 3릴 메가슬롯',x:8,y:1,w:4,h:2},
      {id:'sign',label:'코인 안내판',x:5,y:1,w:2,h:2},
      {id:'coinCabinet',label:'코인 보관함',x:13,y:1,w:2,h:2},
      ...[[3,4,0],[6,4,1],[12,4,2],[15,4,0],[3,8,2],[15,8,1]].map(([x,y,variant],n)=>
        ({id:'slot',label:'슬롯머신 '+(n+1),x,y,w:2,h:2,variant,worn:n===4})),
      ...[[3,6],[6,6],[12,6],[15,6],[3,10],[15,10]].map(([x,y])=>
        ({id:'stool',label:'회전 의자',x,y,w:2,h:1})),
      {id:'counter',label:'코인 교환 카운터',x:5,y:11,w:3,h:1},
      {id:'bench',label:'대기 벤치',x:12,y:11,w:3,h:1},
      {id:'bin',label:'소형 휴지통',x:17,y:7,w:1,h:1}
    ].map(absolute);
    const open = cells.slice();
    for (const p of props) for (let dy = 0; dy < p.h; dy++) for (let dx = 0; dx < p.w; dx++)
      open[index(p.x + dx,p.y + dy)] = 0;
    const servicePoints = [[9,3],[6,3],[14,3],[3,7],[6,7],[12,7],[15,7],[3,11],[15,11],[6,12],[13,12]]
      .map(([x,y]) => absolute({x,y}));
    return {w,h,offset,cells,inner,building,props,entry,doorway,open,servicePoints,
      start:{x:entry.x,y:entry.y + 2},runner:absolute({x:9,y:4,w:2,h:9})};
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
  window.MegaSlotLayout211 = {generate,distances,dirs,index};
})();
