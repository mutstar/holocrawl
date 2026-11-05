(function(root){
'use strict';
const base=typeof module!=='undefined'&&module.exports?require('./layout04-generator.js'):root.StreetGen;
const {FLOOR,WALL,random,distances,route,validate}=base;
function components(cells,w,h){const seen=new Uint8Array(w*h),result=[];for(let i=0;i<cells.length;i++)if(cells[i]===FLOOR&&!seen[i]){const q=[i];seen[i]=1;for(let n=0;n<q.length;n++){const p=q[n],x=p%w,y=Math.floor(p/w);for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,yy=y+dy,j=yy*w+xx;if(xx>0&&yy>0&&xx<w-1&&yy<h-1&&!seen[j]&&cells[j]===FLOOR){seen[j]=1;q.push(j);}}}result.push(q);}return result.sort((a,b)=>b.length-a.length);}
function core(cells,w,h){const result=new Uint8Array(w*h);for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){let good=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(cells[yy*w+xx]!==FLOOR)good=false;if(good)result[y*w+x]=FLOOR;}return result;}
function flowMetrics(m){let narrow=0,walk=0;const {cells,w,h}=m;for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++)if(cells[y*w+x]===FLOOR){walk++;if((cells[y*w+x-1]!==FLOOR&&cells[y*w+x+1]!==FLOOR)||(cells[(y-1)*w+x]!==FLOOR&&cells[(y+1)*w+x]!==FLOOR))narrow++;}const groups=components(core(cells,w,h),w,h),total=groups.reduce((n,g)=>n+g.length,0);return{walkable:walk,singleFileCells:narrow,wideCoreCells:total,largestWideCore:groups[0]?.length||0,wideCoreConnectedFraction:total?(groups[0]?.length||0)/total:0};}
function generate(seed,w=80,h=70,exitMode='auto',profile={}){
 if(profile.layout&&!['auto','connected'].includes(profile.layout)){const m=base.generate(seed,w,h,exitMode,profile);m.flowMetrics=flowMetrics(m);return m;}
 for(let attempt=0;attempt<30;attempt++){
 const rng=random(`${seed}:connected05:${attempt}`),int=(a,b)=>a+Math.floor(rng()*(b-a+1)),cells=new Uint8Array(w*h),patches=[],edges=[];
 const inside=(x,y)=>x>=3&&y>=3&&x<w-3&&y<h-3;
 function paint(x,y,width=5){for(let yy=y-Math.floor(width/2);yy<=y+Math.floor(width/2);yy++)for(let xx=x-Math.floor(width/2);xx<=x+Math.floor(width/2);xx++)if(inside(xx,yy))cells[yy*w+xx]=FLOOR;}
 function patch(cx,cy,rw,rh){const x=Math.max(3,Math.min(w-rw-3,cx-Math.floor(rw/2))),y=Math.max(3,Math.min(h-rh-3,cy-Math.floor(rh/2)));for(let yy=y;yy<y+rh;yy++)for(let xx=x;xx<x+rw;xx++)cells[yy*w+xx]=FLOOR;const p={x,y,w:rw,h:rh,cx:x+Math.floor(rw/2),cy:y+Math.floor(rh/2),depth:2};patches.push(p);return p;}
 function broadLink(a,b,width=5){let x=a.x,y=a.y;const first=rng()<.5;while(x!==b.x||y!==b.y){paint(x,y,width);if(first&&x!==b.x||y===b.y)x+=Math.sign(b.x-x);else y+=Math.sign(b.y-y);}paint(x,y,width);edges.push({a:{...a},b:{...b},width});}
 patch(Math.floor(w/2)+int(-5,5),Math.floor(h/2)+int(-5,5),int(12,19),int(10,16));
 for(let n=1;n<int(35,44);n++){
   const rw=int(9,19),rh=int(8,16),angle=rng()*Math.PI*2;
   const parent=n%3===0?patches.reduce((best,p)=>!best||(p.cx-w/2)*Math.cos(angle)+(p.cy-h/2)*Math.sin(angle)>(best.cx-w/2)*Math.cos(angle)+(best.cy-h/2)*Math.sin(angle)?p:best,null):patches[int(0,patches.length-1)];
   const dx=Math.round(Math.cos(angle)*(parent.w+rw)*.30),dy=Math.round(Math.sin(angle)*(parent.h+rh)*.30);
   const child=patch(parent.cx+dx,parent.cy+dy,rw,rh);
   // Wide overlap/join rather than a separate room connected by a thin corridor.
   broadLink({x:parent.cx,y:parent.cy},{x:child.cx,y:child.cy},int(5,7));
 }
 // Fill small seams between overlapping spaces; this merges almost-touching lobes.
 const expanded=new Uint8Array(cells.length),closed=new Uint8Array(cells.length);
 for(let y=3;y<h-3;y++)for(let x=3;x<w-3;x++)if(cells[y*w+x]===FLOOR)for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)expanded[yy*w+xx]=1;
 for(let y=3;y<h-3;y++)for(let x=3;x<w-3;x++){let all=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(!expanded[yy*w+xx])all=false;if(all)closed[y*w+x]=1;}
 cells.set(closed);const growthCells=cells.slice();
 const footprint=[];for(let i=0;i<cells.length;i++)if(cells[i]===FLOOR)footprint.push(i);
 const xs=footprint.map(i=>i%w),ys=footprint.map(i=>Math.floor(i/w));if(Math.max(...xs)-Math.min(...xs)<w*.68||Math.max(...ys)-Math.min(...ys)<h*.65)continue;
 const desiredIslands=int(10,17);let islands=0;
 for(let tries=0;tries<1100&&islands<desiredIslands;tries++){
   const bw=int(4,11),bh=int(4,10),x=int(6,w-bw-6),y=int(6,h-bh-6),shape=int(0,3);let good=true;
   // Irregular wall masses, with air between them, rather than equal building boxes.
   for(let yy=y-2;yy<y+bh+2;yy++)for(let xx=x-2;xx<x+bw+2;xx++)if(cells[yy*w+xx]!==FLOOR)good=false;
   if(!good)continue;
   for(let yy=y;yy<y+bh;yy++)for(let xx=x;xx<x+bw;xx++){
     const dx=xx-x,dy=yy-y;
     if(shape===1&&dx>=Math.ceil(bw*.55)&&dy<Math.floor(bh*.55))continue;
     if(shape===2&&(dx<Math.floor(bw*.25)||dx>=Math.ceil(bw*.75))&&(dy<Math.floor(bh*.3)||dy>=Math.ceil(bh*.7)))continue;
     if(shape===3&&(dy<Math.floor(bh*.45)&&dx<Math.floor(bw*.35)||dy>=Math.floor(bh*.45)&&dx>=Math.ceil(bw*.8)))continue;
     cells[yy*w+xx]=WALL;
   }islands++;
 }
 if(islands<5)continue;
 // Short wall peninsulas break up the outer outline without sealing routes.
 let peninsulas=0;
 for(let n=0;n<100&&peninsulas<5;n++){
   const x=int(6,w-12),y=int(6,h-12),bw=int(4,8),bh=int(3,6);let floor=0,wall=0;
   for(let yy=y;yy<y+bh;yy++)for(let xx=x;xx<x+bw;xx++)cells[yy*w+xx]===FLOOR?floor++:wall++;
   if(!wall||floor<bw*bh*.55||floor>bw*bh*.9)continue;
   const saved=cells.slice();for(let yy=y;yy<y+bh;yy++)for(let xx=x;xx<x+bw;xx++)if(yy<y+bh-1||xx<x+bw-2)cells[yy*w+xx]=WALL;
   const floorGroups=components(cells,w,h),wideGroups=components(core(cells,w,h),w,h),total=wideGroups.reduce((sum,g)=>sum+g.length,0);
   if(floorGroups.length!==1||!total||wideGroups[0].length/total<.96){cells.set(saved);continue;}peninsulas++;
 }
 // Open a few short detours, rather than forcing repeated long trips around walls.
 const working={w,h,cells};
 for(let n=0;n<5;n++){
   const clear=core(cells,w,h),points=[];for(let i=0;i<clear.length;i++)if(clear[i]===1)points.push(i);if(!points.length)break;
   const i=points[int(0,points.length-1)],a={x:i%w,y:Math.floor(i/w)},dist=distances(working,a),candidates=points.filter(j=>{const direct=Math.abs(j%w-a.x)+Math.abs(Math.floor(j/w)-a.y);return direct>=5&&direct<=13&&dist.dist[j]>direct*2+8;});
   if(candidates.length){const j=candidates[int(0,candidates.length-1)];broadLink(a,{x:j%w,y:Math.floor(j/w)},5);}
 }
 let clear=core(cells,w,h),groups=components(clear,w,h),sum=groups.reduce((n,g)=>n+g.length,0);
 if(!groups.length||groups[0].length/sum<.94)continue;
 const m={seed:String(seed),w,h,cells,rooms:patches,partitions:patches,edges,props:[],enemies:[],items:[],attempt,layoutKey:'connected',layoutName:'불규칙하게 이어진 거리',layoutDetail:'공간이 겹쳐 이어지고, 벽 덩어리 사이로 넓은 순환 길이 남습니다.',roomCells:growthCells,corridorCells:cells.slice(),islands,peninsulas};
 const main=groups[0],upIndex=main[int(0,main.length-1)];m.upstairs={x:upIndex%w,y:Math.floor(upIndex/w)};m.start={x:m.upstairs.x,y:m.upstairs.y+1};
 const wideMap={w,h,cells:clear},wideDistance=distances(wideMap,m.upstairs),targets=main.filter(i=>wideDistance.dist[i]>24).sort((a,b)=>wideDistance.dist[b]-wideDistance.dist[a]);if(!targets.length)continue;
 const downIndex=targets[int(0,Math.min(10,targets.length-1))];m.exit={x:downIndex%w,y:Math.floor(downIndex/w)};m.exitType='floor';m.exitDoor=null;
 const protectedRoute=route(wideMap,m.upstairs,m.exit);if(!protectedRoute.length)continue;m.reservedWalk=new Uint8Array(w*h);m.reservedRoute=protectedRoute;
 for(const p of protectedRoute)for(let yy=p.y-1;yy<=p.y+1;yy++)for(let xx=p.x-1;xx<=p.x+1;xx++)m.reservedWalk[yy*w+xx]=1;
 m.focus=main.map(i=>({x:i%w,y:Math.floor(i/w)})).sort((a,b)=>(Math.abs(a.x-w/2)+Math.abs(a.y-h/2))-(Math.abs(b.x-w/2)+Math.abs(b.y-h/2)))[0];
 // Keep the legacy decoration exclusion marker at a real solid wall patch.
 let marker=null;for(let y=3;y<h-5&&!marker;y++)for(let x=3;x<w-5;x++)if(cells[y*w+x]===0&&cells[y*w+x+1]===0&&cells[(y+1)*w+x]===0&&cells[(y+1)*w+x+1]===0&&cells[(y+2)*w+x]===1) {marker={x,y,w:2,h:2,room:patches[0]};break;}
 m.prefab=marker||{x:3,y:3,w:2,h:2,room:patches[0]};m.decoratedCells=cells.slice();m.path=route(m,m.start,m.exit);m.validation=validate(m);if(!m.validation.ok)continue;
 m.flowMetrics=flowMetrics(m);m.metrics={walkable:m.validation.walkable,openNine:sum,roomCount:patches.length,connections:edges.length,internalBuildings:islands,mainRouteWidth:3};return m;
 }
 throw Error('Could not create a connected comfortable street');
}
function validateComfort(m){const result=base.validate(m);if(result.ok&&m.layoutKey==='connected'){const groups=components(core(m.cells,m.w,m.h),m.w,m.h),total=groups.reduce((n,g)=>n+g.length,0);result.wideConnectedShare=total?groups[0].length/total:0;result.ok=result.ok&&result.wideConnectedShare>=.92;}return result;}
root.StreetGen={...base,validate:validateComfort,generate,flowMetrics,core,components};if(typeof module!=='undefined'&&module.exports)module.exports=root.StreetGen;
})(typeof globalThis!=='undefined'?globalThis:this);
