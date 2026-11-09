(function(root){
'use strict';
const WALL=0,FLOOR=1,BARRIER=2;
function random(seed){let h=2166136261;for(const c of String(seed)){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return()=>{h+=0x6D2B79F5;let t=h;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
function distances(map,from){const {w,h,cells}=map;const dist=new Int32Array(w*h).fill(-1),prev=new Int32Array(w*h).fill(-1),queue=[];const first=from.y*w+from.x;if(cells[first]!==FLOOR)return{dist,prev,count:0};dist[first]=0;queue.push(first);for(let head=0;head<queue.length;head++){const i=queue[head],x=i%w,y=Math.floor(i/w);for(const [dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy,j=ny*w+nx;if(nx<0||ny<0||nx>=w||ny>=h||cells[j]!==FLOOR||dist[j]>=0)continue;dist[j]=dist[i]+1;prev[j]=i;queue.push(j);}}return{dist,prev,count:queue.length};}
function route(map,from,to){const b=distances(map,from),target=to.y*map.w+to.x;if(b.dist[target]<0)return[];const path=[];for(let i=target;i>=0;i=b.prev[i])path.push({x:i%map.w,y:Math.floor(i/map.w)});return path.reverse();}
function validate(map){const {w,h,cells,start,exit}=map;const b=distances(map,start);let walk=0,border=true;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const c=cells[y*w+x];if(c===FLOOR)walk++;if((x===0||y===0||x===w-1||y===h-1)&&c!==WALL)border=false;}return{ok:walk===b.count&&b.dist[exit.y*w+exit.x]>0&&border&&Boolean(map.prefab),walkable:walk,reached:b.count,exitDistance:b.dist[exit.y*w+exit.x],border,prefab:Boolean(map.prefab)};}
function generate(seed,w=80,h=70){
 if(w<32||h<22)throw new Error('Preview map must be at least32x22');
 for(let attempt=0;attempt<32;attempt++){
 const rng=random(`${seed}:expanded:${attempt}`),int=(a,b)=>a+Math.floor(rng()*(b-a+1));
 const map={seed:String(seed),w,h,cells:new Uint8Array(w*h),rooms:[],partitions:[],edges:[],props:[],enemies:[],items:[],attempt};
 const {cells,rooms}=map;
 function carve(x,y){if(x>0&&y>0&&x<w-1&&y<h-1)cells[y*w+x]=FLOOR;}
 function split(rect,depth){map.partitions.push({...rect,depth});const canX=rect.w>=18,canY=rect.h>=16;if(depth>=6||(!canX&&!canY)){const rw=int(5,rect.w-2),rh=int(4,rect.h-2),x=rect.x+int(1,rect.w-rw-1),y=rect.y+int(1,rect.h-rh-1);const room={x,y,w:rw,h:rh,cx:x+Math.floor(rw/2),cy:y+Math.floor(rh/2)};rooms.push(room);for(let yy=y;yy<y+rh;yy++)for(let xx=x;xx<x+rw;xx++)carve(xx,yy);return{room};}const vertical=canX&&(!canY||rect.w/rect.h>1.25||(rect.w/rect.h>.85&&rng()<.5));let left,right;if(vertical){const cut=int(8,rect.w-8);left={x:rect.x,y:rect.y,w:cut,h:rect.h};right={x:rect.x+cut,y:rect.y,w:rect.w-cut,h:rect.h};}else{const cut=int(7,rect.h-7);left={x:rect.x,y:rect.y,w:rect.w,h:cut};right={x:rect.x,y:rect.y+cut,w:rect.w,h:rect.h-cut};}return{left:split(left,depth+1),right:split(right,depth+1)};}
 const tree=split({x:2,y:2,w:w-4,h:h-4},0);
 map.layout=['広場','路地','街区'][Math.floor(rng()*3)];
 // Overlapping open courts break up the separated rectangular room pattern.
 for(let n=0;n<3;n++){const a=rooms[int(0,rooms.length-1)],rw=int(9,15),rh=int(7,12);for(let y=a.cy-Math.floor(rh/2);y<a.cy+Math.ceil(rh/2);y++)for(let x=a.cx-Math.floor(rw/2);x<a.cx+Math.ceil(rw/2);x++)carve(x,y);}
 map.roomCells=cells.slice();
 function corridor(a,b){const wide=rng()<.55?3:1;let x=a.cx,y=a.cy;const horizontal=rng()<.5;function stepTo(tx,ty){while(x!==tx||y!==ty){carve(x,y);if(wide===3){carve(x+1,y);carve(x,y+1);carve(x+1,y+1);carve(x-1,y);carve(x,y-1);}if(x!==tx)x+=Math.sign(tx-x);else y+=Math.sign(ty-y);}carve(x,y);}if(horizontal){stepTo(b.cx,a.cy);stepTo(b.cx,b.cy);}else{stepTo(a.cx,b.cy);stepTo(b.cx,b.cy);}map.edges.push({a:{x:a.cx,y:a.cy},b:{x:b.cx,y:b.cy}});}
 function connect(node){if(node.room)return node.room;const a=connect(node.left),b=connect(node.right);corridor(a,b);return rng()<.5?a:b;}
 connect(tree);
 for(let n=0;n<Math.max(1,Math.floor(rooms.length*.85));n++){const a=rooms[int(0,rooms.length-1)],others=rooms.filter(b=>b!==a).sort((b,c)=>(Math.abs(a.cx-b.cx)+Math.abs(a.cy-b.cy))-(Math.abs(a.cx-c.cx)+Math.abs(a.cy-c.cy)));corridor(a,others[int(0,Math.min(2,others.length-1))]);}
 // Wide routes link distant courts; buildings form islands with routes on both sides.
 const avenueCount=map.layout==='広場'?3:map.layout==='路地'?1:2;
 for(let n=0;n<avenueCount;n++){const a=rooms[int(0,rooms.length-1)],b=rooms[int(0,rooms.length-1)];corridor(a,b);}
 map.corridorCells=cells.slice();
 const candidates=[];for(const room of rooms){if(room.y<3||room.w<4)continue;for(let x=room.x;x<=room.x+room.w-4;x++){let valid=true;for(let yy=room.y-2;yy<room.y;yy++)for(let xx=x;xx<x+4;xx++)if(cells[yy*w+xx]!==WALL)valid=false;if(valid)candidates.push({x,y:room.y-2,w:4,h:2,room});}}
 if(!candidates.length)continue;map.prefab=candidates[int(0,candidates.length-1)];
 const anchor=rooms[0];let first=Array.from(cells).findIndex(c=>c===FLOOR);const any={x:first%w,y:Math.floor(first/w)};
 function placeProp(x,y,type){const i=y*w+x;if(cells[i]!==FLOOR)return false;cells[i]=BARRIER;const remaining=Array.from(cells).filter(c=>c===FLOOR).length;if(distances(map,any).count!==remaining){cells[i]=FLOOR;return false;}map.props.push({x,y,type});return true;}
 for(const room of rooms){if(rng()<.7)placeProp(room.x,room.y,'ticket');}
 const front=map.prefab.room;for(let dx=0;dx<3;dx++)placeProp(front.x+1+dx,Math.min(front.y+2,front.y+front.h-2),'fence');
 map.decoratedCells=cells.slice();
 let sx=anchor.cx,sy=anchor.cy;if(cells[sy*w+sx]!==FLOOR){first=Array.from(cells).findIndex(c=>c===FLOOR);sx=first%w;sy=Math.floor(first/w);}map.start={x:sx,y:sy};
 const b=distances(map,map.start);let far=0;for(let i=0;i<b.dist.length;i++)if(b.dist[i]>b.dist[far])far=i;map.exit={x:far%w,y:Math.floor(far/w)};
 const safe=[];for(let i=0;i<cells.length;i++)if(cells[i]===FLOOR&&b.dist[i]>=8&&i!==far)safe.push(i);
 for(let i=safe.length-1;i>0;i--){const j=int(0,i);[safe[i],safe[j]]=[safe[j],safe[i]];}
 for(const i of safe.slice(0,Math.min(28,safe.length)))map.enemies.push({x:i%w,y:Math.floor(i/w)});
 for(const i of safe.slice(28,46))map.items.push({x:i%w,y:Math.floor(i/w)});
 map.path=route(map,map.start,map.exit);map.validation=validate(map);if(!map.validation.ok||map.validation.exitDistance<18)continue;
 return map;
 }
 throw new Error('Could not construct a connected preview map');
}
const api={WALL,FLOOR,BARRIER,generate,distances,route,validate,random};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.StreetGen=api;
})(typeof globalThis!=='undefined'?globalThis:this);
