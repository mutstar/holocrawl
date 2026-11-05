(function(root){
'use strict';
const G=typeof module!=='undefined'&&module.exports?require('./generator.js'):root.StreetGen;
const profiles=typeof module!=='undefined'&&module.exports?require('./market-profiles.js'):root.MarketProfiles;
function generate(seed,floor,exitMode='auto'){
 const profile=profiles.find(p=>p.floor===floor);if(!profile)throw Error('Floor is outside market district');
 const map=G.generate(String(seed)+':market:'+floor,80,70,exitMode,profile);
 map.seed=String(seed);map.floorNumber=floor;map.profile=profile;map.enemies=[];map.items=[];map.marketWalls=[];map.marketProps=[];
 const rng=G.random(String(seed)+':market-props:'+floor),used=new Set();
 const open=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.FLOOR;
 const wall=(x,y)=>x>0&&y>0&&x<map.w-1&&y<map.h-1&&map.cells[y*map.w+x]===G.WALL;
 for(let y=1;y<map.h-2;y++)for(let x=1;x<map.w-3;x++){
   if(!wall(x,y)||!wall(x+1,y)||!open(x,y+1)||!open(x+1,y+1)||used.has(y*map.w+x)||rng()>profile.shops)continue;
   map.marketWalls.push({x,y,closed:rng()<profile.closedChance});used.add(y*map.w+x);used.add(y*map.w+x+1);x++;
 }
 // Position solid low props along walls, preserving the entire reachable floor graph.
 const candidates=[];
 for(let y=2;y<map.h-2;y++)for(let x=2;x<map.w-2;x++){
   if(!open(x,y)||!wall(x,y-1)||!open(x,y+1))continue;
   if([map.start,map.upstairs,map.exit].some(p=>Math.max(Math.abs(x-p.x),Math.abs(y-p.y))<3))continue;
   candidates.push({x,y});
 }
 for(let i=candidates.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[candidates[i],candidates[j]]=[candidates[j],candidates[i]];}
 for(const p of candidates){
   const roll=rng();if(roll>=profile.rackRate+profile.boxRate)continue;
   const type=roll<profile.rackRate?'rack':'boxes';
   if(map.marketProps.some(q=>Math.max(Math.abs(q.x-p.x),Math.abs(q.y-p.y))<(type==='rack'?3:2)))continue;
   const i=p.y*map.w+p.x;map.cells[i]=G.BARRIER;
   if(!G.validate(map).ok){map.cells[i]=G.FLOOR;continue;}
   map.marketProps.push({...p,type});
 }
 map.decoratedCells=map.cells.slice();map.validation=G.validate(map);map.path=G.route(map,map.start,map.exit);
 if(!map.validation.ok)throw Error('Market props disconnected the map');
 return map;
}
root.MarketGen={generate,profiles};if(typeof module!=='undefined'&&module.exports)module.exports=root.MarketGen;
})(typeof globalThis!=='undefined'?globalThis:this);
