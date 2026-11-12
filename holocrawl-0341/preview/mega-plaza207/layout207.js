(function () {
  'use strict';
  const footprint = [29,19], offset = 3, [width,height] = footprint;
  const w = width + offset*2, h = height + offset*2;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y*w+x;
  const absolute = p => ({...p,x:p.x+offset,y:p.y+offset});

  function generate(mode) {
    const cells = Array(w*h).fill(1), inner = cells.map(()=>false), building = inner.slice();
    for (const [x,y,cols,rows] of [[4,1,21,1],[2,2,25,3],[1,5,27,11],[2,16,25,1],[5,17,19,1]]) {
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
    const entry=absolute({x:13,y:18,w:3,h:1});
    for(let dx=0;dx<entry.w;dx++) cells[index(entry.x+dx,entry.y)]=1;
    const props = [
      {id:'coaster',label:'메가코스터',x:5,y:2,w:16,h:7},
      {id:'platform',label:'탑승장',x:12,y:9,w:8,h:2},
      {id:'maintenance',label:'정비함',x:22,y:5,w:2,h:2},
      {id:'console',label:'운행 제어기',x:20,y:9,w:1,h:2},
      {id:'capsule',label:'카엘라 · 캡슐 콩',x:2,y:11,w:6,h:4},
      {id:'crane',label:'로보코 · 로보로보 크레인',x:22,y:10,w:5,h:5},
      {id:'bench',label:'벤치',x:10,y:15,w:2,h:1},
      {id:'bench',label:'벤치',x:17,y:15,w:2,h:1},
    ].map(absolute);
    const open=cells.slice();
    for(const p of props) {
      for(let dy=0;dy<p.h;dy++)for(let dx=0;dx<p.w;dx++)open[index(p.x+dx,p.y+dy)]=0;
    }
    const points=[
      {id:'입구',x:14,y:18},{id:'중앙 광장',x:14,y:13},{id:'탑승장',x:16,y:11},
      {id:'캡슐 뽑기',x:5,y:15},{id:'인형 뽑기',x:24,y:15},
      {id:'정비 통로',x:21,y:6},{id:'코스터 뒤편',x:10,y:1},
    ].map(absolute);
    return {w,h,cells,inner,building,entry,props,open,points,start:absolute({x:14,y:19}),
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
  window.PlazaLayout207={generate,reachable,dirs,index,footprint};
})();
