(function(root){
 'use strict';
 const native=typeof module!=='undefined'&&module.exports,base=native?require('../wall-structures122/market122.js'):root.MarketGen;
 const key=(x,y)=>`${x},${y}`,policies={
  4:{coverage:.78,weights:[4,3,1.5,1,.5]},5:{coverage:.88,weights:[3,3,2,2,.4]},
  6:{coverage:.82,weights:[1.2,.8,4,3,.5]},7:{coverage:.92,weights:[.6,.5,7,4,.4]}
 },types=['acrylic-window','shirt-window','closed-shutter','half-shutter','poster-wall'];
 function random(text){let h=2166136261;for(const c of text)h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h+=0x6D2B79F5;let t=Math.imul(h^(h>>>15),h|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
 function choose(weights,r){let n=r()*weights.reduce((a,b)=>a+b,0);for(let i=0;i<weights.length;i++){n-=weights[i];if(n<0)return types[i];}return types.at(-1);}
 function generate(...args){
  const m=base.generate(...args),floor=m.floorNumber,p=policies[floor];if(!p)throw Error('Shopping district requires4-7F');
  const r=random(`${m.seed}:${floor}:shopfront123`),old=m.marketWalls.map(f=>({...f})),used=new Set();
  for(const f of old)for(let dx=0;dx<2;dx++)used.add(key(f.x+dx,f.y));
  const specials=[m.start,m.upstairs,m.exit].filter(Boolean),eligible=new Set(),serviceReserved=new Set();
  for(const f of m.marketInfra||[])for(let dx=-1;dx<=f.length;dx++)serviceReserved.add(key(f.x+dx,f.y));
  function outside(x,y){const a=m.prefab;if(a&&x>=a.x-2&&x<a.x+a.w+2&&y>=a.y-2&&y<a.y+a.h+2)return false;const d=m.exitDoor;if(d&&x>=d.x-3&&x<d.x+d.w+3&&y>=d.y-3&&y<d.y+d.h+3)return false;return specials.every(a=>Math.max(Math.abs(a.x-x),Math.abs(a.y-y))>3);}
  for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++)if(m.cells[y*m.w+x]===0&&m.cells[(y+1)*m.w+x]!==0&&outside(x,y)&&!serviceReserved.has(key(x,y)))eligible.add(key(x,y));
  const candidates=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-3;x++)if(eligible.has(key(x,y))&&eligible.has(key(x+1,y))){const row=old.filter(a=>a.y===y),distance=row.length?Math.min(...row.map(a=>Math.abs(a.x-x))):999;candidates.push({x,y,distance,rank:r()});}
  candidates.sort((a,b)=>(a.distance<6?0:1)-(b.distance<6?0:1)||a.distance-b.distance||a.rank-b.rank);
  const covered=()=>[...eligible].filter(k=>used.has(k)).length,target=Math.ceil(eligible.size*p.coverage),added=[];
  for(const a of candidates){if(covered()>=target)break;if(used.has(key(a.x,a.y))||used.has(key(a.x+1,a.y)))continue;added.push({x:a.x,y:a.y});used.add(key(a.x,a.y));used.add(key(a.x+1,a.y));}
  m.marketWalls=[...old.map(f=>({...f,added123:false})),...added.map(f=>({...f,added123:true}))].map(f=>{const type=choose(p.weights,r);return{...f,type,closed:type==='closed-shutter'};}).sort((a,b)=>a.y-b.y||a.x-b.x);
  m.district123={theme:'shopping-street',oldFacades:old.length,addedFacades:added.length,facades:m.marketWalls.length,eligibleFrontCells:eligible.size,coveredFrontCells:covered(),targetCoverage:p.coverage,actualCoverage:eligible.size?covered()/eligible.size:0,openDisplays:m.marketWalls.filter(f=>f.type.endsWith('window')).length,shutters:m.marketWalls.filter(f=>f.type.includes('shutter')).length};
  return m;
 }
 const api={...base,generate,policies};root.MarketGen=api;root.ShoppingDistrict123=api;if(native)module.exports=api;
})(globalThis);
