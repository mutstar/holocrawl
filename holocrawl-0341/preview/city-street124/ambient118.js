(function(root){
 'use strict';
 const dirs=[[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]],key=(x,y)=>`${x},${y}`;
 function random(seed){let h=2166136261;for(const c of String(seed))h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h+=0x6D2B79F5;let t=Math.imul(h^(h>>>15),h|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
 function shuffle(a,r){a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
 function reach(m,start,blocked=new Set()){
  const q=[start],seen=new Set([key(start.x,start.y)]),prev=new Map([[key(start.x,start.y),null]]);
  for(let i=0;i<q.length;i++)for(const[dx,dy]of dirs){const x=q[i].x+dx,y=q[i].y+dy,k=key(x,y);if(x<=0||y<=0||x>=m.width-1||y>=m.height-1||seen.has(k)||blocked.has(k)||!(m.passable[y*m.width+x]||m.rows[y][x]==='+'))continue;seen.add(k);prev.set(k,q[i]);q.push({x,y});}return{seen,prev};
 }
 function generate(m){
  const w=m.width,h=m.height,r=random(`${m.seed}:${m.depth}:street118`),walls=[],floor=[],fences=[],infra=[],blocked=new Set(),usedWall=new Set();
  const specials=[];for(let y=0;y<h;y++)for(let x=0;x<w;x++)if('<>+'.includes(m.rows[y][x]))specials.push({x,y,c:m.rows[y][x]});
  const start=specials.find(p=>p.c==='<'),baseline=reach(m,start),protectedPath=new Set();
  for(const end of specials.filter(p=>p.c==='<'||p.c==='>'))for(let p=end;p;p=baseline.prev.get(key(p.x,p.y)))protectedPath.add(key(p.x,p.y));
  const outside=(x,y,margin=2)=>!m.origin||x<m.origin.x-margin||y<m.origin.y-margin||x>=m.origin.x+m.origin.width+margin||y>=m.origin.y+m.origin.height+margin;
  const clear=(x,y,n=3)=>specials.every(p=>Math.max(Math.abs(p.x-x),Math.abs(p.y-y))>n);
  const plain=(x,y)=>x>1&&y>1&&x<w-2&&y<h-2&&m.rows[y][x]==='.'&&m.passable[y*w+x]&&m.features[y*w+x]===m.floors[y*w+x]&&outside(x,y)&&clear(x,y)&&!blocked.has(key(x,y));
  function accept(x,y,fw=1,fh=1){const points=[];for(let dy=0;dy<fh;dy++)for(let dx=0;dx<fw;dx++){const xx=x+dx,yy=y+dy;if(!plain(xx,yy)||protectedPath.has(key(xx,yy)))return false;points.push(key(xx,yy));}
   const test=new Set([...blocked,...points]),walk=reach(m,start,test);if(walk.seen.size!==baseline.seen.size-test.size)return false;for(const k of points)blocked.add(k);return true;
  }
  function wallFree(x,y,length=2){for(let dx=-1;dx<=length;dx++)if(usedWall.has(key(x+dx,y)))return false;return true;}
  function markWall(x,y,length){for(let dx=0;dx<length;dx++)usedWall.add(key(x+dx,y));}
  const slots=[];for(let y=2;y<h-2;y++)for(let x=2;x<w-3;x++)if(m.rows[y][x]==='#'&&m.rows[y][x+1]==='#'&&plain(x,y+1)&&plain(x+1,y+1)&&outside(x,y)&&outside(x+1,y)&&clear(x,y)&&clear(x+1,y))slots.push({x,y});
  let pool=shuffle(slots,r);pool.sort((a,b)=>Math.hypot(a.x-start.x,a.y-start.y)-Math.hypot(b.x-start.x,b.y-start.y));
  for(const[type,index]of[['acrylic-window',0],['shirt-window',1]]){
   for(const p of pool){if(!wallFree(p.x,p.y)||walls.some(q=>Math.hypot(q.x-p.x,q.y-p.y)<8))continue;
    const frontType=index===0?'shirt-stack':['acrylic-rack','hoodie-rack','plush-basket','badge-trays'][Math.floor(r()*4)];let f=null;
    for(const fw of[2,1])for(const[dx,dy]of[[0,1],[0,2],[1,1],[-1,2]])if(!f&&accept(p.x+dx,p.y+dy,fw,1))f={type:frontType,x:p.x+dx,y:p.y+dy,footW:fw,footH:1};
    if(!f)continue;floor.push(f);walls.push({...p,type});markWall(p.x,p.y,2);break;
   }
  }
  for(const type of['closed-shutter','half-shutter']){const p=pool.filter(p=>wallFree(p.x,p.y)).sort((a,b)=>Math.min(...walls.map(q=>Math.hypot(a.x-q.x,a.y-q.y)))-Math.min(...walls.map(q=>Math.hypot(b.x-q.x,b.y-q.y))))[0];if(p){walls.push({...p,type});markWall(p.x,p.y,2);}}
  const edge=[];for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++)if(plain(x,y)&&dirs.some(([dx,dy])=>m.rows[y+dy]?.[x+dx]==='#'))edge.push({x,y});
  const crates=2+Math.floor(r()*2);for(let i=0;i<crates;i++){const p=shuffle(edge,r).find(p=>floor.every(q=>Math.max(Math.abs(q.x-p.x),Math.abs(q.y-p.y))>=3)&&accept(p.x,p.y));if(p)floor.push({...p,type:'delivery-boxes',footW:1,footH:1});}
  const trash=shuffle(edge,r).find(p=>floor.every(q=>Math.max(Math.abs(q.x-p.x),Math.abs(q.y-p.y))>=2)&&accept(p.x,p.y));if(trash)floor.push({...trash,type:'trash-bags',footW:1,footH:1});
  const fence=shuffle(edge,r).filter(p=>Math.hypot(p.x-start.x,p.y-start.y)<22).find(p=>accept(p.x,p.y,2,1));if(fence)for(let dx=0;dx<2;dx++)fences.push({x:fence.x+dx,y:fence.y});
  // Old infrastructure designs return on long exposed walls. Keep them away
  // from windows, doors, facility shells and their immediate entrance buffers.
  const mounts=[];for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++)if(m.rows[y][x]==='#'&&m.rows[y+1][x]==='.'&&outside(x,y)&&clear(x,y))mounts.push({x,y});
  const mountFree=(x,y)=>mounts.some(p=>p.x===x&&p.y===y)&&wallFree(x,y,1);
  for(const type of['pipe','air','vent','cabinet','air','vent','cabinet','air','vent']){
   for(const p of shuffle(mounts,r)){
    if(!mountFree(p.x,p.y))continue;const length=type==='pipe'?3+Math.floor(r()*3):1;
    if(!Array.from({length},(_,dx)=>mountFree(p.x+dx,p.y)).every(Boolean))continue;
    infra.push({...p,type,length});markWall(p.x,p.y,length);break;
   }
  }
  const reached=reach(m,start,blocked),stairs=specials.filter(p=>p.c==='<'||p.c==='>');
  return{walls,floor,fences,infra,start,blocked:[...blocked],validation:{connected:reached.seen.size===baseline.seen.size-blocked.size,stairsConnected:stairs.every(p=>reached.seen.has(key(p.x,p.y))),mainRoutesClear:[...protectedPath].every(k=>!blocked.has(k)),baseline:baseline.seen.size,blocked:blocked.size,crateTarget:crates,crates:floor.filter(p=>p.type==='delivery-boxes').length,shops:walls.filter(p=>p.type.endsWith('window')).length}};
 }
 const api={generate,reach};root.Ambient118=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
