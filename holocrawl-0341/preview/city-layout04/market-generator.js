(function(root){
'use strict';
const native=typeof module!=='undefined'&&module.exports,G=native?require('./generator.js'):root.StreetGen,profiles=native?require('./market-profiles.js'):root.MarketProfiles,catalog=native?require('./merch-catalog.js'):root.MerchCatalog;
function choose(items,weights,random){let value=random()*weights.reduce((a,b)=>a+b,0);for(let i=0;i<items.length;i++){value-=weights[i];if(value<0)return items[i];}return items[items.length-1];}
function generate(seed,floor,exitMode='auto',layoutMode='auto'){
 const profile=profiles.find(p=>p.floor===floor);if(!profile)throw Error('Unknown market floor');
 const map=G.generate(String(seed)+':market:'+floor,80,70,exitMode,{...profile,layout:layoutMode});
 Object.assign(map,{seed:String(seed),floorNumber:floor,profile,enemies:[],items:[],marketWalls:[],marketProps:[],placementZones:[]});
 const random=G.random(`${seed}:layout04-props:${floor}:${map.layoutKey}`),int=(a,b)=>a+Math.floor(random()*(b-a+1)),used=new Set(),walls=catalog.filter(p=>p.kind==='wall'),props=catalog.filter(p=>p.kind==='floor');
 const open=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.FLOOR;
 const solid=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.WALL;
 const allFloor=[];for(let y=2;y<map.h-2;y++)for(let x=2;x<map.w-2;x++)if(open(x,y))allFloor.push({x,y});
 const zoneKinds=floor===6?['stock','stock','trash','shop','empty']:floor===7?['trash','closed','empty','shop','empty']:['shop','shop','stock','trash','empty'];
 for(const kind of zoneKinds){let point=allFloor[int(0,allFloor.length-1)];for(let n=0;n<40&&map.placementZones.some(z=>Math.abs(z.x-point.x)+Math.abs(z.y-point.y)<15);n++)point=allFloor[int(0,allFloor.length-1)];map.placementZones.push({...point,kind,radius:int(9,17)});}
 function influence(x,y,kind){let strength=0;for(const zone of map.placementZones)if(zone.kind===kind){const distance=Math.hypot(x-zone.x,(y-zone.y)*1.12);strength=Math.max(strength,Math.max(0,1-distance/zone.radius));}return strength;}
 for(let y=1;y<map.h-2;y++)for(let x=1;x<map.w-3;x++){
   if(!solid(x,y)||!solid(x+1,y)||!open(x,y+1)||!open(x+1,y+1)||used.has(y*map.w+x))continue;
   const empty=influence(x,y,'empty'),shop=influence(x,y,'shop'),closed=influence(x,y,'closed');
   const density=(.035+.78*shop+.65*closed)*(1-.9*empty);if(random()>density)continue;
   const weights=walls.map(p=>p.id==='closed-shutter'?(floor===7?5:1)+closed*8:p.id==='half-shutter'?(floor===6?3:1):p.id==='acrylic-window'?2+shop*4:p.id==='shirt-window'?2+shop*3:1);
   const type=choose(walls,weights,random).id;map.marketWalls.push({x,y,type,closed:type==='closed-shutter'});used.add(y*map.w+x);used.add(y*map.w+x+1);x++;
 }
 const candidates=[];
 for(const p of allFloor){
   if([map.start,map.upstairs,map.exit,map.focus||map.start].some(q=>Math.max(Math.abs(p.x-q.x),Math.abs(p.y-q.y))<2))continue;
   const adjacentWall=[[1,0],[-1,0],[0,1],[0,-1]].some(([dx,dy])=>solid(p.x+dx,p.y+dy));
   const stock=influence(p.x,p.y,'stock'),trash=influence(p.x,p.y,'trash'),shop=influence(p.x,p.y,'shop'),empty=influence(p.x,p.y,'empty');
   const density=((adjacentWall?.025:.003)+.21*stock+.16*trash+.08*shop)*(1-.95*empty);
   if(random()<density)candidates.push({...p,stock,trash,shop});
 }
 for(let i=candidates.length-1;i>0;i--){const j=int(0,i);[candidates[i],candidates[j]]=[candidates[j],candidates[i]];}
 for(const p of candidates){
   const weights=props.map(type=>type.content==='stock'?1+p.stock*15:type.content==='trash'?1+p.trash*16:1+p.shop*10),type=choose(props,weights,random).id;
   // Clusters can touch locally; limit overfilling so a pile does not become a second wall.
   if(map.marketProps.filter(q=>Math.max(Math.abs(q.x-p.x),Math.abs(q.y-p.y))<3).length>4)continue;
   const i=p.y*map.w+p.x;map.cells[i]=G.BARRIER;if(!G.validate(map).ok){map.cells[i]=G.FLOOR;continue;}map.marketProps.push({x:p.x,y:p.y,type});
 }
 map.decoratedCells=map.cells.slice();map.validation=G.validate(map);map.path=G.route(map,map.start,map.exit);if(map.metrics)map.metrics.walkable=map.validation.walkable;
 if(!map.validation.ok)throw Error('Props disconnected the map');return map;
}
root.MarketGen={generate,profiles};if(native)module.exports=root.MarketGen;
})(typeof globalThis!=='undefined'?globalThis:this);
