(function(root){
'use strict';
const legacy=typeof module!=='undefined'&&module.exports?require('./legacy-generator.js'):root.StreetGen;
const {WALL,FLOOR,BARRIER,random,distances,route}=legacy;
const info={plaza:['큰 광장·건물 덩어리','큰 열린 공간에 건물 덩어리와 작은 샛방이 불규칙하게 끼어듭니다.'],rooms:['비정형 방·통로 연결','작고 큰 방,ㄱ·ㄴ·십자 모양 공간과 길이가 다른 통로가 얽힙니다.'],alleys:['구불구불한 골목망','굴곡 많은 긴 골목에 작은 마당·막다른 길·순환 경로가 섞입니다.']};
function validate(m){const b=distances(m,m.start);let walkable=0,border=true;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){if(m.cells[y*m.w+x]===FLOOR)walkable++;if((!x||!y||x===m.w-1||y===m.h-1)&&m.cells[y*m.w+x]!==WALL)border=false;}return{ok:walkable===b.count&&b.dist[m.exit.y*m.w+m.exit.x]>18&&border,walkable,reached:b.count,exitDistance:b.dist[m.exit.y*m.w+m.exit.x],border,prefab:Boolean(m.prefab)};}
function generate(seed,w=80,h=70,exitMode='auto',profile={}){
 if(profile.layout==='previous'){const m=legacy.generate(seed,w,h,exitMode,profile);m.layoutKey='previous';m.layoutName='이전 사각 구획';m.layoutDetail='사각 구획과 직각 통로가 반복되던 이전 시안';m.focus=m.start;return m;}
 if(w<64||h<56)throw Error('Layout comparison needs at least64x56 cells');
 for(let attempt=0;attempt<24;attempt++){
 const rng=random(`${seed}:layout04:${attempt}`),int=(a,b)=>a+Math.floor(rng()*(b-a+1));
 const requested=profile.layout||'auto',key=requested==='auto'?['plaza','rooms','alleys'][int(0,2)]:requested;if(!info[key])throw Error('Unknown layout');
 const m={seed:String(seed),w,h,cells:new Uint8Array(w*h),rooms:[],partitions:[],edges:[],props:[],enemies:[],items:[],attempt,layoutKey:key,layoutName:info[key][0],layoutDetail:info[key][1]};
 const {cells,rooms}=m;
 const inside=(x,y)=>x>1&&y>1&&x<w-2&&y<h-2;
 function carve(x,y,width=1){for(let yy=y-Math.floor((width-1)/2);yy<=y+Math.floor(width/2);yy++)for(let xx=x-Math.floor((width-1)/2);xx<=x+Math.floor(width/2);xx++)if(inside(xx,yy))cells[yy*w+xx]=FLOOR;}
 function rect(x,y,rw,rh){for(let yy=y;yy<y+rh;yy++)for(let xx=x;xx<x+rw;xx++)carve(xx,yy);}
 function addRoom(x,y,rw,rh,shape='rect'){
   const r={x,y,w:rw,h:rh,cx:x+Math.floor(rw/2),cy:y+Math.floor(rh/2),shape};
   if(shape==='cross'){rect(x,y+Math.floor(rh/3),rw,Math.max(3,Math.floor(rh/3)));rect(x+Math.floor(rw/3),y,Math.max(3,Math.floor(rw/3)),rh);}
   else if(shape==='elbow'){rect(x,y,Math.max(3,Math.floor(rw*.6)),rh);rect(x,y+Math.floor(rh*.5),rw,Math.max(3,Math.ceil(rh*.5)));}
   else if(shape==='chamfer'){rect(x+1,y,rw-2,rh);rect(x,y+1,rw,rh-2);}
   else rect(x,y,rw,rh);
   carve(r.cx,r.cy,2);rooms.push(r);m.partitions.push({...r,depth:2});return r;
 }
 function stroke(a,b,width){let x=a.x,y=a.y,first=rng()<.5;while(x!==b.x||y!==b.y){carve(x,y,width);if(first&&x!==b.x||y===b.y)x+=Math.sign(b.x-x);else y+=Math.sign(b.y-y);}carve(x,y,width);}
 function corridor(a,b,winding=false){
   const width=rng()<.65?1:rng()<.7?2:3;
   if(winding){let x=a.x,y=a.y,steps=0,heading=null,remaining=0;while((x!==b.x||y!==b.y)&&steps++<1200){carve(x,y,width);if(remaining--<=0){const dx=b.x-x,dy=b.y-y;if(rng()<.18)heading=[[1,0],[-1,0],[0,1],[0,-1]][int(0,3)];else if(dx&&(!dy||rng()<.5))heading=[Math.sign(dx),0];else heading=[0,Math.sign(dy)];remaining=int(1,4);}let nx=x+heading[0],ny=y+heading[1];if(!inside(nx,ny)){remaining=0;continue;}x=nx;y=ny;}stroke({x,y},b,width);}
   else if(rng()<.6){const middle={x:Math.max(3,Math.min(w-4,Math.round((a.x+b.x)/2)+int(-7,7))),y:Math.max(3,Math.min(h-4,Math.round((a.y+b.y)/2)+int(-7,7)))};stroke(a,middle,width);stroke(middle,b,rng()<.6?width:int(1,3));}
   else stroke(a,b,width);
   m.edges.push({a:{...a},b:{...b},winding});
 }
 function connectRooms(winding){const joined=[0],waiting=rooms.map((_,i)=>i).slice(1);while(waiting.length){let choice=null;for(const a of joined)for(let n=0;n<waiting.length;n++){const b=waiting[n],distance=Math.abs(rooms[a].cx-rooms[b].cx)+Math.abs(rooms[a].cy-rooms[b].cy);if(!choice||distance<choice.distance)choice={a,b,n,distance};}const a=rooms[choice.a],b=rooms[choice.b];corridor({x:a.cx,y:a.cy},{x:b.cx,y:b.cy},winding);joined.push(choice.b);waiting.splice(choice.n,1);}}
 let focus;
 if(key==='plaza'){
   const cx=int(29,w-29),cy=int(25,h-25);
   addRoom(cx-int(16,22),cy-int(10,17),int(32,43),int(23,32),'chamfer');
   for(let i=0;i<3;i++)rect(cx+int(-22,10),cy+int(-18,8),int(12,24),int(10,20));
   for(let i=0;i<int(6,10);i++){const bx=cx+int(-16,13),by=cy+int(-12,10),bw=int(3,7),bh=int(3,8);for(let y=by;y<by+bh;y++)for(let x=bx;x<bx+bw;x++)if(inside(x,y))cells[y*w+x]=WALL;}
   for(let i=0;i<18;i++){const rw=int(5,12),rh=int(4,11);addRoom(int(3,w-rw-4),int(3,h-rh-4),rw,rh,['rect','elbow','chamfer'][int(0,2)]);}
   focus={x:cx,y:cy};
 }else if(key==='rooms'){
   const target=int(28,39);for(let tries=0;tries<1400&&rooms.length<target;tries++){
     const large=rooms.length<3,rw=large?int(13,20):int(4,12),rh=large?int(10,17):int(4,11),x=int(3,w-rw-4),y=int(3,h-rh-4);
     let overlap=0;for(let yy=y-1;yy<=y+rh;yy++)for(let xx=x-1;xx<=x+rw;xx++)if(cells[yy*w+xx]===FLOOR)overlap++;
     if(overlap>rw*rh*.13)continue;addRoom(x,y,rw,rh,['rect','elbow','cross','chamfer'][int(0,3)]);
   }
   const r=rooms[0];focus={x:r.cx,y:r.cy};
 }else{
   for(let i=0;i<20;i++){const rw=int(4,10),rh=int(4,9);addRoom(int(3,w-rw-4),int(3,h-rh-4),rw,rh,['elbow','chamfer','rect'][int(0,2)]);}
   focus={x:rooms[8].cx,y:rooms[8].cy};
 }
 m.roomCells=cells.slice();connectRooms(key==='alleys');
 const loops=key==='plaza'?int(4,7):key==='rooms'?int(5,10):int(7,12);
 for(let i=0;i<loops;i++){const a=rooms[int(0,rooms.length-1)],near=rooms.filter(b=>b!==a).sort((b,c)=>(Math.abs(a.cx-b.cx)+Math.abs(a.cy-b.cy))-(Math.abs(a.cx-c.cx)+Math.abs(a.cy-c.cy))),b=near[int(0,Math.min(5,near.length-1))];corridor({x:a.cx,y:a.cy},{x:b.cx,y:b.cy},key==='alleys'||rng()<.3);}
 // Extra branches make dead ends and short side passages, rather than filling every gap.
 if(key==='alleys')for(let i=0;i<18;i++){const r=rooms[int(0,rooms.length-1)];let x=r.cx,y=r.cy,dx=rng()<.5?1:-1,dy=0;for(let j=0;j<int(6,18);j++){carve(x,y,rng()<.85?1:2);if(rng()<.22){[dx,dy]=[dy,-dx];}if(!inside(x+dx,y+dy))break;x+=dx;y+=dy;}}
 // Repair any pockets left around building islands; retain only genuinely connected geometry.
 const first=Array.from(cells).findIndex(c=>c===FLOOR),origin={x:first%w,y:Math.floor(first/w)};
 for(let tries=0;tries<60;tries++){
   const b=distances(m,origin),isolated=[];for(let i=0;i<cells.length;i++)if(cells[i]===FLOOR&&b.dist[i]<0)isolated.push(i);if(!isolated.length)break;
   const target=isolated[int(0,isolated.length-1)],p={x:target%w,y:Math.floor(target/w)};let best=null;
   for(let i=0;i<cells.length;i++)if(b.dist[i]>=0){const q={x:i%w,y:Math.floor(i/w)},d=Math.abs(q.x-p.x)+Math.abs(q.y-p.y);if(!best||d<best.d)best={q,d};}corridor(best.q,p,false);
 }
 m.corridorCells=cells.slice();
 const arrivals=[];for(let y=3;y<h-3;y++)for(let x=3;x<w-3;x++){let clear=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(cells[yy*w+xx]!==FLOOR)clear=false;if(clear)arrivals.push({x,y});}
 if(arrivals.length<2)continue;m.upstairs=arrivals[int(0,arrivals.length-1)];m.start={x:m.upstairs.x,y:m.upstairs.y+1};
 const b=distances(m,m.start),floors=arrivals.filter(p=>b.dist[p.y*w+p.x]>25).map(p=>({...p,distance:b.dist[p.y*w+p.x]})).sort((a,b)=>b.distance-a.distance);
 if(!floors.length)continue;
 const doors=[];for(let y=3;y<h-4;y++)for(let x=3;x<w-5;x++){
   let valid=true;for(let yy=y;yy<y+2;yy++)for(let xx=x;xx<x+3;xx++)if(cells[yy*w+xx]!==WALL)valid=false;
   for(let xx=x;xx<x+3;xx++)if(cells[(y+2)*w+xx]!==FLOOR)valid=false;
   if(valid&&b.dist[(y+2)*w+x+1]>25)doors.push({x,y,w:3,h:2,distance:b.dist[(y+2)*w+x+1]});
 }
 doors.sort((a,b)=>b.distance-a.distance);
 const wallExit=exitMode==='wall'&&doors.length||exitMode==='auto'&&doors.length&&rng()<.3;
 if(wallExit){m.exitDoor=doors[int(0,Math.min(8,doors.length-1))];m.exit={x:m.exitDoor.x+1,y:m.exitDoor.y+2};m.exitType='wall';}else{const p=floors[int(0,Math.min(10,floors.length-1))];m.exit={x:p.x,y:p.y};m.exitType='floor';m.exitDoor=null;}
 const landmark=doors[0]||{x:3,y:3,w:2,h:2};m.prefab={...landmark,room:rooms[0]};
 m.focus=arrivals.reduce((best,p)=>!best||Math.abs(p.x-focus.x)+Math.abs(p.y-focus.y)<Math.abs(best.x-focus.x)+Math.abs(best.y-focus.y)?p:best,null);
 if(key==='alleys'){
   const bends=[];for(let y=7;y<h-7;y++)for(let x=7;x<w-7;x++)if(cells[y*w+x]===FLOOR){let local=0,neighbors=0;for(let yy=y-2;yy<=y+2;yy++)for(let xx=x-2;xx<=x+2;xx++)if(cells[yy*w+xx]===FLOOR)local++;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]])if(cells[(y+dy)*w+x+dx]===FLOOR)neighbors++;if(local>=7&&local<=14&&neighbors>=2)bends.push({x,y,score:Math.abs(x-w/2)+Math.abs(y-h/2)});}
   bends.sort((a,b)=>a.score-b.score);if(bends.length)m.focus={x:bends[0].x,y:bends[0].y};
 }
 m.decoratedCells=cells.slice();m.path=route(m,m.start,m.exit);m.validation=validate(m);
 if(!m.validation.ok)continue;
 let openNine=0,deadEnds=0;for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++)if(cells[y*w+x]===FLOOR){let count=0;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]])if(cells[(y+dy)*w+x+dx]===FLOOR)count++;if(count===1)deadEnds++;let full=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(cells[yy*w+xx]!==FLOOR)full=false;if(full)openNine++;}
 m.metrics={walkable:m.validation.walkable,openNine,deadEnds,roomCount:rooms.length,connections:m.edges.length};return m;
 }
 throw Error('Could not construct connected layout');
}
const api={WALL,FLOOR,BARRIER,random,distances,route,validate,generate,layoutInfo:info};root.StreetGen=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
