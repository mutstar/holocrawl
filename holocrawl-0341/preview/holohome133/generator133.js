(function(root){'use strict';const native=typeof module!=='undefined'&&module.exports,Base=native?require('../holohome132/generator132.js'):root.HoloHomeGen132;
 function cellsFor(m,p){const out=[];for(const r of p.collisionRects||[{x:0,y:0,w:p.w,h:p.h}])for(let y=p.y+r.y;y<p.y+r.y+r.h;y++)for(let x=p.x+r.x;x<p.x+r.x+r.w;x++)out.push(y*m.w+x);return out;}
 function generate(seed,floor=1){const m=Base.generate(seed,floor);m.generation='browser HoloHome133 reference-lobby revision; native integration pending';if(!m.home)return m;const h=m.home;
  // Only the interior is rebuilt; the random street, shell position and ordinary stairs remain.
  for(let y=1;y<h.h-1;y++)for(let x=1;x<h.w-1;x++)m.cells[(h.y+y)*m.w+h.x+x]=1;
  m.doors=m.doors.filter(d=>!d.home||d.entrance);
  const prop=(type,x,y,w,hgt,extra={})=>({type,x:h.x+x,y:h.y+y,w,h:hgt,...extra});
  m.props=[prop('balcony',3,0,11,4,{architecture:true,collisionRects:[{x:0,y:1,w:4,h:3},{x:7,y:1,w:4,h:3},{x:4,y:0,w:3,h:2}]}),prop('sofa',6,5,3,1),prop('coffee',7,7,2,1),prop('sofa',6,9,3,1),prop('bookcase',1,5,2,1),prop('kotatsu',2,8,3,2),prop('tv',12,7,3,2),prop('notice',14,4,1,1),prop('planter',1,10,2,1),prop('planter',13,10,2,1)];
  m.homeStair.x=h.x+8;m.homeStair.y=h.y+3;m.homeFocus={x:h.x+9,y:h.y+10};
  m.open=Uint8Array.from(m.cells,c=>c===1?1:0);const occupied=new Set();for(const p of m.props)for(const i of cellsFor(m,p)){if(occupied.has(i))throw Error('HoloHome133 overlapping scenery');occupied.add(i);m.open[i]=0;}
  if(!m.open[m.homeStair.y*m.w+m.homeStair.x])throw Error('HoloHome stair obstructed');const d=Base.distances(m,m.start);m.walkable=m.open.reduce((a,b)=>a+b,0);if(d.filter(n=>n>=0).length!==m.walkable)throw Error('HoloHome133 path disconnected');m.homeDistance=d[m.homeStair.y*m.w+m.homeStair.x];m.validation={...m.validation,referenceLobby:true,connected:true,oldInternalPartitionsRemoved:true};return m;
 }
 const api={generate,distances:Base.distances,isHome:Base.isHome,cellsFor};root.HoloHomeGen133=api;if(native)module.exports=api;
})(globalThis);
