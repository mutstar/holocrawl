(function(root){
'use strict';
const base=typeof module!=='undefined'&&module.exports?require('./layout05-generator.js'):root.StreetGen;
const {FLOOR,random,distances,route}=base;
function generate(seed,w=80,h=70,exitMode='auto',profile={}){
 const mode=profile.layout||'balanced';
 if(!['balanced','auto'].includes(mode))return base.generate(seed,w,h,exitMode,profile);
 const m=base.generate(seed,w,h,'floor',{...profile,layout:'rooms'}),rng=random(`${seed}:balanced06`),int=(a,b)=>a+Math.floor(rng()*(b-a+1)),oldCells=m.cells.slice();
 function paint(x,y,width){for(let yy=y-Math.floor(width/2);yy<=y+Math.floor(width/2);yy++)for(let xx=x-Math.floor(width/2);xx<=x+Math.floor(width/2);xx++)if(xx>0&&yy>0&&xx<w-1&&yy<h-1)m.cells[yy*w+xx]=FLOOR;}
 function link(a,b,width){let x=a.x,y=a.y,first=rng()<.5;while(x!==b.x||y!==b.y){paint(x,y,width);if(first&&x!==b.x||y===b.y)x+=Math.sign(b.x-x);else y+=Math.sign(b.y-y);}paint(x,y,width);}
 // Merge selected neighbouring spaces into local quarters; preserve other small pockets.
 const centers=[];
 for(let n=0;n<3;n++){
   let candidate=m.rooms[int(0,m.rooms.length-1)];for(let tries=0;tries<25&&centers.some(c=>Math.abs(c.cx-candidate.cx)+Math.abs(c.cy-candidate.cy)<17);tries++)candidate=m.rooms[int(0,m.rooms.length-1)];centers.push(candidate);
 }
 const merges=[];
 for(const center of centers){const near=m.rooms.filter(r=>r!==center).sort((a,b)=>(Math.abs(a.cx-center.cx)+Math.abs(a.cy-center.cy))-(Math.abs(b.cx-center.cx)+Math.abs(b.cy-center.cy))).slice(0,2);
   for(const r of near){const a={x:center.cx,y:center.cy},b={x:r.cx,y:r.cy};if(Math.abs(a.x-b.x)+Math.abs(a.y-b.y)>23)continue;link(a,b,5);merges.push({a,b,width:5});}
 }
 m.roomCells=m.cells.slice();let widerLinks=0;
 for(const edge of m.edges)if(rng()<.3){const path=route({w,h,cells:oldCells},edge.a,edge.b);for(const p of path)paint(p.x,p.y,3);widerLinks++;}
 // The stair-to-stair route stays broad, even while some side passages remain small.
 const primary=route(m,m.upstairs,m.exit);if(!primary.length)throw Error('Missing balanced primary path');
 for(const p of primary)paint(p.x,p.y,3);
 m.reservedRoute=primary;m.reservedWalk=new Uint8Array(w*h);
 for(const p of primary)for(let y=p.y-1;y<=p.y+1;y++)for(let x=p.x-1;x<=p.x+1;x++)m.reservedWalk[y*w+x]=1;
 m.layoutKey='balanced';m.layoutName='이어진 구역과 짧은 골목';m.layoutDetail='일부 공간은 넓게 합치고, 사이에는 짧은 골목과 작은 옆 공간을 남깁니다.';
 m.mergedQuarters=centers.map(r=>({x:r.cx,y:r.cy}));m.mergedLinks=merges;m.widerLinks=widerLinks;m.edges.push(...merges);
 m.corridorCells=m.cells.slice();m.decoratedCells=m.cells.slice();m.focus={x:centers[1].cx,y:centers[1].cy};m.path=route(m,m.start,m.exit);m.validation=base.validate(m);if(!m.validation.ok)throw Error('Invalid balanced map');
 m.flowMetrics=base.flowMetrics(m);m.metrics={walkable:m.validation.walkable,mergedQuarters:centers.length,widenedLinks:widerLinks,mainRouteWidth:3};return m;
}
root.StreetGen={...base,generate};if(typeof module!=='undefined'&&module.exports)module.exports=root.StreetGen;
})(typeof globalThis!=='undefined'?globalThis:this);
