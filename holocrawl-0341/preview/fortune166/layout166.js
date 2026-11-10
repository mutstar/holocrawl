(function(root){'use strict';const native=typeof module!=='undefined'&&module.exports,Base=native?require('../fortune165/layout165.js'):root.FortuneLayout165;
function generate(){const m=Base.generate();m.props=[{id:'hub',label:'공용 · 라이브 중계 데스크',x:7,y:2,w:3,h:2},{id:'calli',label:'칼리오페 · 사신 레코드',x:4,y:2,w:2,h:2},{id:'kiara',label:'키아라 · 피닉스 송신기',x:11,y:2,w:2,h:2},{id:'ina',label:'이나 · 고서 중계대',x:3,y:5,w:2,h:2},{id:'ame',label:'아메 · 탐정 통신대',x:5,y:5,w:2,h:2},{id:'gura',label:'구라 · 상어 신호기',x:12,y:5,w:2,h:2}];
m.fixtures=[{id:'stage',role:'shared-performance-stage',x:3,y:2,w:11,h:2,blocking:false,members:['calli','hub','kiara']},{id:'workbench',role:'wall-attached-shared-workbench',x:3,y:5,w:4,h:2,blocking:true,members:['ina','ame']},{id:'reception',role:'wall-attached-reception-counter',x:11,y:5,w:3,h:2,blocking:true,members:['gura']}];
m.open=Uint8Array.from(m.cells);for(const p of [...m.props,...m.fixtures.filter(f=>f.blocking)])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)m.open[y*m.w+x]=0;
m.ports=[{id:'calli',x:4,y:4,color:'#ae6978'},{id:'kiara',x:12,y:4,color:'#bd875b'},{id:'ina',x:4,y:7,color:'#9477ac'},{id:'ame',x:6,y:7,color:'#baa671'},{id:'gura',x:12,y:7,color:'#6599bc'}];
m.mainAisle=Array.from({length:9},(_,i)=>({x:8,y:12-i}));m.policy={...m.policy,revision:166,stageAndWorkZones:true,fiveDetachedTerminals:false,floorLinkDiagram:false};return m;}
const api={generate,distances:Base.distances,route:Base.route};root.FortuneLayout166=api;if(native)module.exports=api;
})(globalThis);
