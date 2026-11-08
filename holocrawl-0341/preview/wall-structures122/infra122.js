(function(root){
 'use strict';
 const key=(x,y)=>`${x},${y}`;
 function random(text){let h=2166136261;for(const c of text)h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h+=0x6D2B79F5;let t=Math.imul(h^(h>>>15),h|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
 function place(m){
  const r=random(`${m.seed}:${m.floorNumber}:wall-infra122`),used=new Set(),result=[],floor=m.floorNumber,points=[m.start,m.upstairs,m.exit].filter(Boolean);
  for(const p of m.marketWalls||[])for(let dx=-1;dx<=2;dx++)used.add(key(p.x+dx,p.y));
  const wall=(x,y)=>x>1&&y>1&&x<m.w-2&&y<m.h-2&&m.cells[y*m.w+x]===0&&m.cells[(y+1)*m.w+x]===1;
  const outside=(x,y)=>{const p=m.prefab;if(p&&x>=p.x-2&&x<p.x+p.w+2&&y>=p.y-2&&y<p.y+p.h+2)return false;return points.every(p=>Math.max(Math.abs(p.x-x),Math.abs(p.y-y))>3)&&(!m.exitDoor||x<m.exitDoor.x-3||y<m.exitDoor.y-3||x>m.exitDoor.x+m.exitDoor.w+3||y>m.exitDoor.y+m.exitDoor.h+3);};
  const slots=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++)if(wall(x,y)&&outside(x,y))slots.push({x,y,rank:r()});
  const types={4:['air','vent','cabinet'],5:['vent','cabinet','air','vent'],6:['pipe','cabinet','vent','air','cabinet','vent'],7:['pipe','vent','cabinet','air','vent','cabinet']}[floor]||[];
  const anchors=floor===6?m.marketProps:m.marketWalls;
  const distance=p=>anchors.length?Math.min(...anchors.map(q=>Math.hypot(p.x-q.x,p.y-q.y))):0;
  slots.sort((a,b)=>distance(a)-distance(b)||a.rank-b.rank);
  for(const type of types){
   const length=type==='pipe'?3+Math.floor(r()*2):1,pool=slots.map(p=>({...p,order:r()}));pool.sort((a,b)=>distance(a)-distance(b)||a.order-b.order);
   const p=pool.find(p=>Array.from({length},(_,i)=>p.x+i).every(x=>wall(x,p.y)&&outside(x,p.y)&&[-1,0,1].every(dx=>!used.has(key(x+dx,p.y)))));
   if(!p)continue;result.push({x:p.x,y:p.y,type,length});for(let dx=-1;dx<=length;dx++)used.add(key(p.x+dx,p.y));
  }return result;
 }
 const api={place};root.WallInfra122=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
