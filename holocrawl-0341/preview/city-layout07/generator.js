(function(root){
'use strict';
const base=typeof module!=='undefined'&&module.exports?require('./layout06-generator.js'):root.StreetGen;
const {FLOOR,WALL,random,route,distances}=base;
function generate(seed,w=80,h=70,exitMode='auto',profile={}){
 const mode=profile.layout||'balanced';if(!['balanced','auto'].includes(mode))return base.generate(seed,w,h,exitMode,profile);
 for(let attempt=0;attempt<24;attempt++){
 const rng=random(`${seed}:quarters07:${attempt}`),int=(a,b)=>a+Math.floor(rng()*(b-a+1)),cells=new Uint8Array(w*h),rooms=[],edges=[],quarters=[];
 function rect(cx,cy,rw,rh,kind){const x=Math.max(2,Math.min(w-rw-2,cx-Math.floor(rw/2))),y=Math.max(2,Math.min(h-rh-2,cy-Math.floor(rh/2)));for(let yy=y;yy<y+rh;yy++)for(let xx=x;xx<x+rw;xx++){if((xx===x&&yy===y||xx===x+rw-1&&yy===y+rh-1)&&rw>6&&rh>6)continue;cells[yy*w+xx]=FLOOR;}const room={x,y,w:rw,h:rh,cx:x+Math.floor(rw/2),cy:y+Math.floor(rh/2),kind,depth:2};rooms.push(room);return room;}
 function paint(x,y,width){for(let yy=y-Math.floor((width-1)/2);yy<=y+Math.floor(width/2);yy++)for(let xx=x-Math.floor((width-1)/2);xx<=x+Math.floor(width/2);xx++)if(xx>0&&yy>0&&xx<w-1&&yy<h-1)cells[yy*w+xx]=FLOOR;}
 function link(a,b,width){let x=a.x,y=a.y,first=rng()<.5;while(x!==b.x||y!==b.y){paint(x,y,width);if(first&&x!==b.x||y===b.y)x+=Math.sign(b.x-x);else y+=Math.sign(b.y-y);}paint(x,y,width);edges.push({a:{...a},b:{...b},width});}
 const count=int(3,4);
 for(let i=0;i<count;i++){
   let center=null;for(let n=0;n<200;n++){const p={x:int(14,w-15),y:int(12,h-13)};if(quarters.every(q=>Math.hypot(q.cx-p.x,q.cy-p.y)>20)){center=p;break;}}
   if(!center)break;
   const q=rect(center.x,center.y,int(15,22),int(11,18),'quarter');quarters.push(q);
   for(let n=0;n<int(1,2);n++)rect(q.cx+int(-6,6),q.cy+int(-5,5),int(8,14),int(7,12),'quarter-lobe');
 }
 if(quarters.length<3)continue;
 const regionCells=cells.slice(),joined=[0],waiting=quarters.map((_,i)=>i).slice(1),connectedPairs=new Set();
 while(waiting.length){let best=null;for(const a of joined)for(let n=0;n<waiting.length;n++){const b=waiting[n],d=Math.hypot(quarters[a].cx-quarters[b].cx,quarters[a].cy-quarters[b].cy);if(!best||d<best.d)best={a,b,n,d};}const a=quarters[best.a],b=quarters[best.b];link({x:a.cx,y:a.cy},{x:b.cx,y:b.cy},rng()<.6?3:5);connectedPairs.add([best.a,best.b].sort().join(','));joined.push(best.b);waiting.splice(best.n,1);}
 const extra=[];for(let a=0;a<quarters.length;a++)for(let b=a+1;b<quarters.length;b++)if(!connectedPairs.has([a,b].join(',')))extra.push({a,b});
 if(extra.length){const p=extra[int(0,extra.length-1)],a=quarters[p.a],b=quarters[p.b];link({x:a.cx,y:a.cy},{x:b.cx,y:b.cy},3);}
 let islands=0;
 for(const q of quarters)for(let n=0;n<2;n++){
   const bw=int(3,5),bh=int(3,5),x=q.cx+int(-4,1),y=q.cy+int(-3,1);let open=true;for(let yy=y-3;yy<y+bh+3;yy++)for(let xx=x-3;xx<x+bw+3;xx++)if(xx<1||yy<1||xx>=w-1||yy>=h-1||cells[yy*w+xx]!==FLOOR)open=false;
   if(open){for(let yy=y;yy<y+bh;yy++)for(let xx=x;xx<x+bw;xx++)if(!(xx===x&&yy===y))cells[yy*w+xx]=WALL;islands++;}
 }
 const annexCount=int(9,14);
 for(let i=0;i<annexCount;i++){
   const q=quarters[int(0,quarters.length-1)],rw=int(5,10),rh=int(4,9),angle=rng()*Math.PI*2,gap=int(2,6),cx=q.cx+Math.round(Math.cos(angle)*(q.w/2+rw/2+gap)),cy=q.cy+Math.round(Math.sin(angle)*(q.h/2+rh/2+gap));
   const room=rect(cx,cy,rw,rh,'annex');link({x:q.cx,y:q.cy},{x:room.cx,y:room.cy},rng()<.5?1:2);
 }
 const m={seed:String(seed),w,h,cells,rooms,partitions:rooms,edges,props:[],enemies:[],items:[],attempt,layoutKey:'balanced',layoutName:'큰 구역과 짧은 골목',layoutDetail:'3~4개의 넓은 구역 사이를 연결하고, 주변에 작은 공간과 짧은 샛길을 섞습니다.',roomCells:regionCells,corridorCells:cells.slice(),quarterCount:quarters.length,quarters,annexCount,islands};
 const clear=base.core(cells,w,h),groups=base.components(clear,w,h);if(!groups.length||groups[0].length<150)continue;const main=groups[0],upIndex=main[int(0,main.length-1)];m.upstairs={x:upIndex%w,y:Math.floor(upIndex/w)};m.start={x:m.upstairs.x,y:m.upstairs.y+1};
 const wideMap={w,h,cells:clear},wideDistances=distances(wideMap,m.upstairs),targets=main.filter(i=>wideDistances.dist[i]>24);
 targets.sort((left,right)=>wideDistances.dist[right]-wideDistances.dist[left]);if(!targets.length)continue;const down=targets[int(0,Math.min(10,targets.length-1))];m.exit={x:down%w,y:Math.floor(down/w)};m.exitType='floor';m.exitDoor=null;
 m.reservedRoute=route(wideMap,m.upstairs,m.exit);m.reservedWalk=new Uint8Array(w*h);for(const p of m.reservedRoute)for(let y=p.y-1;y<=p.y+1;y++)for(let x=p.x-1;x<=p.x+1;x++)m.reservedWalk[y*w+x]=1;
 const central=quarters[0];m.focus=main.map(i=>({x:i%w,y:Math.floor(i/w)})).sort((a,b)=>(Math.abs(a.x-central.cx)+Math.abs(a.y-central.cy))-(Math.abs(b.x-central.cx)+Math.abs(b.y-central.cy)))[0];
 m.prefab={x:2,y:2,w:2,h:2,room:quarters[0]};m.decoratedCells=cells.slice();m.path=route(m,m.start,m.exit);m.validation=base.validate(m);if(!m.validation.ok)continue;
 m.flowMetrics=base.flowMetrics(m);m.metrics={walkable:m.validation.walkable,mainQuarters:quarters.length,sideSpaces:annexCount,mainRouteWidth:3};return m;
 }
 throw Error('Could not create independently mixed quarters');
}
root.StreetGen={...base,generate};if(typeof module!=='undefined'&&module.exports)module.exports=root.StreetGen;
})(typeof globalThis!=='undefined'?globalThis:this);
