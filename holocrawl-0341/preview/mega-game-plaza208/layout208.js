(function () {
  'use strict';
  const footprint = [25,16], offset = 3, [width,height] = footprint;
  const w = width + offset*2, h = height + offset*2;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y*w+x;
  const absolute = p => ({...p,x:p.x+offset,y:p.y+offset});

  function generate(mode) {
    const cells = Array(w*h).fill(1), inner = cells.map(()=>false), building = inner.slice();
    for (const [x,y,cols,rows] of [[4,1,17,1],[2,2,21,2],[1,4,23,9],[3,13,19,1],[5,14,15,1]]) {
      for(let dy=0;dy<rows;dy++) for(let dx=0;dx<cols;dx++) inner[index(x+dx+offset,y+dy+offset)]=true;
    }
    if (mode === 'attached') cells.fill(0,0,(offset+1)*w);
    inner.forEach((inside,i)=>{
      if(!inside)return;
      cells[i]=1;
      for(const [dx,dy] of dirs) {
        const n=i+dy*w+dx;
        if(!inner[n]){cells[n]=0;building[n]=true;}
      }
    });
    const entry=absolute({x:11,y:15,w:3,h:1});
    for(let dx=0;dx<entry.w;dx++) cells[index(entry.x+dx,entry.y)]=1;
    const props = [
      {id:'capsule',label:'카엘라 · 캡슐 콩',x:3,y:3,w:6,h:4},
      {id:'crane',label:'로보코 · 로보로보 크레인',x:17,y:2,w:5,h:5},
      {id:'bench',label:'벤치',x:6,y:11,w:2,h:1},
      {id:'bench',label:'벤치',x:17,y:11,w:2,h:1},
    ].map(absolute);
    const open=cells.slice();
    for(const p of props) {
      for(let dy=0;dy<p.h;dy++)for(let dx=0;dx<p.w;dx++)open[index(p.x+dx,p.y+dy)]=0;
    }
    const points=[
      {id:'입구',x:12,y:15},
      {id:'중앙 광장',x:12,y:9},
      {id:'캡슐 뽑기',x:6,y:7},
      {id:'인형 뽑기',x:19,y:7},
      {id:'뒤쪽 통로',x:12,y:2},
    ].map(absolute);
    return {w,h,cells,inner,building,entry,props,open,points,start:absolute({x:12,y:16}),
      origin:{x:offset,y:offset}};
  }

  function reachable(map) {
    const seen=new Set([index(map.start.x,map.start.y)]), queue=[map.start];
    for(const {x,y} of queue) {
      for(const [dx,dy] of dirs) {
        if(dx&&dy)continue;
        const nx=x+dx,ny=y+dy,i=index(nx,ny);
        if(nx<0||nx>=w||ny<0||ny>=h||!map.open[i]||seen.has(i))continue;
        seen.add(i);queue.push({x:nx,y:ny});
      }
    }
    return seen;
  }
  window.GamePlazaLayout208={generate,reachable,dirs,index,footprint};
})();
