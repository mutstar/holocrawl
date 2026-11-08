(function(root){
 'use strict';
 const native=typeof module!=='undefined'&&module.exports,base=native?require('../city-street122/ambient118.js'):root.Ambient118,key=(x,y)=>`${x},${y}`;
 const profiles={1:{windows:['acrylic-window'],stands:0,units:['air','vent']},2:{windows:['shirt-window'],stands:0,units:['vent','cabinet']},3:{windows:['acrylic-window','shirt-window'],stands:1,units:['air','vent','cabinet']}};
 function generate(m){
  const a=base.generate(m),p=profiles[m.depth];if(!p)throw Error('Clean street profile requires1-3F');
  const oldBlocked=new Set(a.blocked),stands=a.floor.filter(f=>!['delivery-boxes','trash-bags'].includes(f.type));
  a.walls=a.walls.filter(f=>p.windows.includes(f.type));
  a.floor=[...stands.slice(0,p.stands),...a.floor.filter(f=>f.type==='delivery-boxes')];
  a.infra=p.units.map(type=>a.infra.find(f=>f.type===type)).filter(Boolean);
  const blocked=new Set();for(const f of [...a.floor,...a.fences])for(let dy=0;dy<(f.footH||1);dy++)for(let dx=0;dx<(f.footW||1);dx++)blocked.add(key(f.x+dx,f.y+dy));
  const baseline=base.reach(m,a.start),walk=base.reach(m,a.start,blocked),stairs=[];for(let y=0;y<m.height;y++)for(let x=0;x<m.width;x++)if('<>'.includes(m.rows[y][x]))stairs.push(key(x,y));
  const subset=[...blocked].every(k=>oldBlocked.has(k));
  a.blocked=[...blocked];a.validation={...a.validation,connected:walk.seen.size===baseline.seen.size-blocked.size,stairsConnected:stairs.every(k=>walk.seen.has(k)),mainRoutesClear:a.validation.mainRoutesClear&&subset,blocked:blocked.size,shops:a.walls.length,crates:a.floor.filter(f=>f.type==='delivery-boxes').length};
  if(!a.validation.connected||!a.validation.stairsConnected||!a.validation.mainRoutesClear)throw Error('Clean street connectivity failed');
  a.district123={theme:'clean-street',windows:a.walls.length,stands:stands.slice(0,p.stands).length,serviceUnits:a.infra.length,shutters:0,looseTrash:0,pipes:0,onlyRemovedFloorObstacles:subset};return a;
 }
 const api={...base,generate,profiles};root.Ambient118=api;root.CleanStreet123=api;if(native)module.exports=api;
})(globalThis);
