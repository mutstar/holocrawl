(function(root){'use strict';const native=typeof module!=='undefined'&&module.exports,Base=native?require('../holohome132/generator132.js'):root.HoloHomeGen132;
function cellsFor(m,p){const a=[];for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)a.push(y*m.w+x);return a;}
function generate(seed,floor=1){const m=Base.generate(seed,floor);m.generation='browser HoloHome139 distinct facade with modest lounge; native integration pending';if(!m.home)return m;const old={...m.home};m.reservedHomeBounds=old;
for(let y=old.y;y<old.y+old.h;y++)for(let x=old.x;x<old.x+old.w;x++)m.cells[y*m.w+x]=1;
const h=m.home={...old,x:old.x+2,y:old.y+1,w:13,h:11};
for(let y=0;y<h.h;y++)for(let x=0;x<h.w;x++)m.cells[(h.y+y)*m.w+h.x+x]=x===0||y===0||x===h.w-1||y===h.h-1?0:1;
m.entrance={x:h.x+6,y:h.y+10};m.cells[m.entrance.y*m.w+m.entrance.x]=1;m.doors=m.doors.filter(d=>!d.home);m.doors.push({id:'home-6-10',...m.entrance,home:true,entrance:true});
const prop=(type,x,y,w,hh,extra={})=>({type,x:h.x+x,y:h.y+y,w,h:hh,...extra});
m.props=[prop('sofa',3,4,3,1),prop('coffee',4,6,2,1),prop('sofa',3,8,3,1),prop('bookcase',1,3,2,1),prop('tv',9,4,2,2),prop('planter',1,8,2,1),prop('planter',10,8,2,1)];
m.homeStair.x=h.x+6;m.homeStair.y=h.y+2;m.homeFocus={x:h.x+7,y:h.y+7};
m.open=Uint8Array.from(m.cells,c=>c===1?1:0);const used=new Set();for(const p of m.props)for(const i of cellsFor(m,p)){if(used.has(i))throw Error('HoloHome furniture overlaps');used.add(i);m.open[i]=0;}
const d=Base.distances(m,m.start);m.walkable=m.open.reduce((a,b)=>a+b,0);if(d.filter(x=>x>=0).length!==m.walkable)throw Error('HoloHome disconnected');if(!m.open[m.homeStair.y*m.w+m.homeStair.x])throw Error('Stair blocked');m.homeDistance=d[m.homeStair.y*m.w+m.homeStair.x];m.validation={...m.validation,restrainedLounge:true,connected:true};return m;}
const api={generate,cellsFor,distances:Base.distances,isHome:Base.isHome};root.HoloHomeGen139=api;if(native)module.exports=api;
})(globalThis);