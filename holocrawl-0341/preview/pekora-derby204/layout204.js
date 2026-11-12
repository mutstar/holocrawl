(function () {
  'use strict';
  const width = 25, height = 21, offset = 4;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const cardinal = dirs.filter(([dx,dy]) => dx === 0 || dy === 0);
  const index = (x,y) => y * width + x;
  const absolute = item => ({...item, x:item.x + offset, y:item.y + offset});

  function generate(mode) {
    const cells = Array(width * height).fill(1);
    const building = cells.map(() => false);
    const inner = cells.map(() => false);
    for (const [x,y,w,h] of [[3,1,11,2],[1,3,15,7],[3,10,11,2]]) {
      for (let row = y; row < y + h; row++) {
        for (let col = x; col < x + w; col++) inner[index(col + offset,row + offset)] = true;
      }
    }
    if (mode === 'attached') cells.fill(0,0,(offset + 1) * width);
    for (let i = 0; i < inner.length; i++) {
      if (!inner[i]) continue;
      cells[i] = 1;
      for (const [dx,dy] of dirs) {
        const neighbor = index(i % width + dx,Math.floor(i / width) + dy);
        if (inner[neighbor]) continue;
        cells[neighbor] = 0;
        building[neighbor] = true;
      }
    }
    const entry = absolute({x:8,y:12,w:2,h:1});
    const doorway = [index(entry.x,entry.y),index(entry.x + 1,entry.y)];
    for (const i of doorway) cells[i] = 1;
    const props = [
      {id:'track',label:'노우사기 경주로',x:5,y:3,w:7,h:5},
      {id:'ticket-counter',label:'발권대',x:3,y:1,w:3,h:2},
      {id:'carrot-trophy',label:'당근 트로피',x:13,y:1,w:1,h:2}
    ].map(absolute);
    const benches = [{x:3,y:9,w:2,h:1},{x:12,y:9,w:2,h:1}].map(absolute);
    const servicePoints = [
      {id:'ticket-counter',x:4,y:3},{id:'carrot-trophy',x:13,y:3},
      {id:'track',x:8,y:8},{id:'track',x:4,y:5},{id:'track',x:12,y:5}
    ].map(absolute);
    const open = cells.slice();
    for (const p of [...props,...benches]) {
      for (let y = p.y; y < p.y + p.h; y++) {
        for (let x = p.x; x < p.x + p.w; x++) open[index(x,y)] = 0;
      }
    }
    return {w:width,h:height,mode,cells,building,inner,open,props,benches,servicePoints,entry,doorway,
      start:{x:entry.x,y:entry.y + 2},origin:{x:offset,y:offset,w:17,h:13}};
  }

  function distances(map, opened = true, diagonal = false) {
    const open = map.open.slice();
    if (!opened) for (const i of map.doorway) open[i] = 0;
    const distance = open.map(() => -1);
    const queue = [map.start];
    distance[index(map.start.x,map.start.y)] = 0;
    for (const point of queue) {
      for (const [dx,dy] of diagonal ? dirs : cardinal) {
        const x = point.x + dx, y = point.y + dy;
        const i = index(x,y);
        if (x < 0 || x >= width || y < 0 || y >= height || !open[i] || distance[i] >= 0) continue;
        distance[i] = distance[index(point.x,point.y)] + 1;
        queue.push({x,y});
      }
    }
    return distance;
  }

  window.DerbyLayout204 = {generate,distances,dirs};
})();
