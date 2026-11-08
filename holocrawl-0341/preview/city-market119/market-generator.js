(function(root){
'use strict';
const native=typeof module!=='undefined'&&module.exports;
const G=native?require('./generator.js'):root.StreetGen;
const profiles=native?require('./market-profiles.js'):root.MarketProfiles;
const catalog=native?require('./merch-catalog.js'):root.MerchCatalog;
function choose(items,weights,random){let total=weights.reduce((a,b)=>a+b,0),roll=random()*total;for(let i=0;i<items.length;i++){roll-=weights[i];if(roll<0)return items[i];}return items[items.length-1];}
function generate(seed,floor,exitMode='auto'){
 const profile=profiles.find(p=>p.floor===floor);if(!profile)throw Error('Unknown market floor');
 const map=G.generate(String(seed)+':market:'+floor,80,70,exitMode,profile);
 Object.assign(map,{seed:String(seed),floorNumber:floor,profile,enemies:[],items:[],marketWalls:[],marketProps:[]});
 const random=G.random(`${seed}:market02:${floor}`),used=new Set(),walls=catalog.filter(p=>p.kind==='wall'),props=catalog.filter(p=>p.kind==='floor');
 const open=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.FLOOR;
 const wall=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.WALL;
 let last=null;
 for(let y=1;y<map.h-2;y++)for(let x=1;x<map.w-3;x++){
   if(!wall(x,y)||!wall(x+1,y)||!open(x,y+1)||!open(x+1,y+1)||used.has(y*map.w+x)||random()>profile.shops)continue;
   if(last&&last.y===y&&x-last.x<4&&random()>.35)continue;
   const weights=walls.map(p=>p.id==='closed-shutter'?(floor===7?7:floor===6?3:1):p.id==='half-shutter'?(floor===7?3:1):p.id==='acrylic-window'?(floor<6?3:1):p.id==='shirt-window'?(floor<6?2:1):1);
   const type=choose(walls,weights,random).id;
   const fixture={x,y,type,closed:type==='closed-shutter'};map.marketWalls.push(fixture);last=fixture;used.add(y*map.w+x);used.add(y*map.w+x+1);x++;
 }
 const candidates=[];
 for(let y=2;y<map.h-2;y++)for(let x=2;x<map.w-2;x++){
   if(!open(x,y)||!wall(x,y-1)||!open(x,y+1))continue;
   if([map.start,map.upstairs,map.exit].some(p=>Math.max(Math.abs(x-p.x),Math.abs(y-p.y))<3))continue;candidates.push({x,y});
 }
 for(let i=candidates.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[candidates[i],candidates[j]]=[candidates[j],candidates[i]];}
 const weights=props.map(p=>{if(p.content==='stock')return floor===6?6:floor===7?2:1;if(p.content==='trash')return floor===7?4:floor===6?2:.7;return floor<6?3:1;});
 for(const p of candidates){
   if(random()>=Math.max(.16,profile.rackRate+profile.boxRate))continue;
   const type=choose(props,weights,random).id;
   if(map.marketProps.some(q=>Math.max(Math.abs(q.x-p.x),Math.abs(q.y-p.y))<2))continue;
   const i=p.y*map.w+p.x;map.cells[i]=G.BARRIER;
   if(!G.validate(map).ok){map.cells[i]=G.FLOOR;continue;}
   map.marketProps.push({...p,type});
 }
 map.decoratedCells=map.cells.slice();map.validation=G.validate(map);map.path=G.route(map,map.start,map.exit);
 if(!map.validation.ok)throw Error('Market props disconnected the map');return map;
}
root.MarketGen={generate,profiles};if(native)module.exports=root.MarketGen;
})(typeof globalThis!=='undefined'?globalThis:this);
