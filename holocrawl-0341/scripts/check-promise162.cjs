const fs=require('fs'),path=require('path'),assert=require('assert/strict'),G=require('../preview/promise162/layout162.js');
const m=G.generate(),d=G.distances(m,m.start),occupied=new Set();
assert.equal(d.filter(v=>v>=0).length,Array.from(m.open).filter(Boolean).length);
for(const p of m.props)for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const i=y*m.w+x;assert.equal(m.cells[i],1,'prop embedded in wall');assert.equal(m.open[i],0);assert(!occupied.has(i),'overlapping props');occupied.add(i);}
assert(d[m.entry.y*m.w+m.entry.x]>=0);assert(d[m.rewardReserve.y*m.w+m.rewardReserve.x]>=0);
// All four cardinal approaches to the central mechanism remain reachable.
for(const [x,y]of [[5,6],[9,6],[7,4],[7,8]])assert(d[y*m.w+x]>=0,'ring route blocked');
assert.deepEqual(Array.from(G.generate().cells),Array.from(m.cells));
const report={revision:162,status:'passed',scope:'Local facility structure, not campaign insertion',footprint:[11,11],shape:'chamfered clock-tower chamber',walkable:d.filter(v=>v>=0).length,connected:true,entranceReachable:true,rewardReserveReachable:true,centralMechanismFourSidesReachable:true,nonOverlappingProps:true,props:m.props.map(p=>p.id),deterministic:true,artStatus:'Existing clock33 mural plus editable code-native structure markers; bespoke assets pending',nativeIntegrated:false};
fs.writeFileSync(path.resolve(__dirname,'../preview/promise162/validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
