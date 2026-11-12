(function () {
  const width = 43, height = 25;
  const entry = [5,21], exit = [35,7];
  const steps = [[0,-1],[1,0],[0,1],[-1,0]];
  const islands = [[6,19,5.5,4.5],[19,15,8,5.9],[30,6,7.6,4.7],[37,21,5.1,3.2],[12,6,4.4,3.2]];
  const channels = [
    [[9,19],[14,17]],
    [[22,12],[26,9]],
    [[26,16],[29,19]],
    [[29,19],[35,21]],
    [[13,8],[16,12]]
  ];
  const landmarks = [
    {name:'피시 블루',type:'fish',x:4,y:16,w:3,h:2,approach:[5,18]},
    {name:'라군 스테이지',type:'stage',x:27,y:4,w:6,h:3,approach:[29,7]},
    {name:'프린세스 마린호',type:'ship',x:32,y:14,w:8,h:4,approach:[36,17]}
  ];
  function hash(x,y) {
    const value = Math.imul(x+17,374761393) ^ Math.imul(y+39,668265263);
    return (value ^ (value >>> 13)) >>> 0;
  }
  function distanceToLine(x,y,[ax,ay],[bx,by]) {
    const dx = bx-ax, dy = by-ay;
    const t = Math.max(0,Math.min(1,((x-ax)*dx + (y-ay)*dy)/(dx*dx+dy*dy)));
    return Math.hypot(x-ax-t*dx,y-ay-t*dy);
  }
  function coastDistance(x,y) {
    return Math.min(...islands.map(([cx,cy,rx,ry],i) => {
      const angle = Math.atan2((y-cy)/ry,(x-cx)/rx);
      return Math.hypot((x-cx)/rx,(y-cy)/ry)
        - .085*Math.sin(5*angle+i) - .045*Math.cos(9*angle-i);
    }));
  }
  function generate(high) {
    const tiles = Array.from({length:height},(_,y) => Array.from({length:width},(_,x) => {
      const distance = coastDistance(x,y);
      if (distance < 1) return 'sand';
      if (channels.some(([a,b]) => distanceToLine(x,y,a,b) < 1.02)) return 'shallow';
      if (!high && distanceToLine(x,y,[15,6],[23,7]) < 1.15) return 'shallow';
      return distance < (high ? 1.16 : 1.36) ? 'shallow' : 'deep';
    }));
    const paint = (x,y,w,h,tile) => {
      for (let dy=0;dy<h;dy++) for (let dx=0;dx<w;dx++) tiles[y+dy][x+dx] = tile;
    };
    // Piers and stage floors remain above the water at either tide.
    paint(7,12,1,6,'deck');
    paint(6,12,3,1,'deck');
    paint(23,4,12,5,'deck');
    paint(36,17,1,5,'deck');
    paint(33,15,6,2,'ship');
    paint(32,16,1,1,'ship');
    paint(39,16,1,1,'ship');
    for (const [x,y,w,h] of [[17,13,3,2],[18,12,2,1],[21,16,2,2],[9,4,3,2],[3,20,1,2],[37,22,2,1]]) {
      paint(x,y,w,h,'rock');
    }
    for (const landmark of landmarks.filter(p => p.type !== 'ship')) {
      paint(landmark.x,landmark.y,landmark.w,landmark.h,'fixture');
    }
    return tiles;
  }
  function walkable(tiles,x,y) {
    return ['sand','shallow','deck','ship'].includes(tiles[y]?.[x]);
  }
  function reachable(tiles) {
    const queue = [entry], seen = new Set([entry.join(',')]);
    for (const [x,y] of queue) for (const [dx,dy] of steps) {
      const next = [x+dx,y+dy], key = next.join(',');
      if (seen.has(key) || !walkable(tiles,...next)) continue;
      seen.add(key);
      queue.push(next);
    }
    return seen;
  }
  window.LagoonMap213 = {width,height,entry,exit,steps,landmarks,hash,generate,walkable,reachable};
})();
