const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const G=require('../preview/festival130/generator130.js');
const stallCatalog=require('../preview/festival214/stalls214.json');
const{chromium,executablePath}=require('./portable-browser-tools.cjs');
const D=path.resolve(__dirname,'../preview/festival130'),url=process.env.HOLOCRAWL_PREVIEW_URL||'http://127.0.0.1:8798';
const hash=m=>crypto.createHash('sha256').update(Buffer.from(m.cells)).update(JSON.stringify([m.structures,m.loose,m.lanterns,m.doors,m.stairs])).digest('hex');
const results=[],fingerprints=new Set(),geometryHashes=new Set(),stallIds=new Set(stallCatalog.map(s=>s.id)),seenStalls=new Set();
for(const seed of ['20261109-8',...Array.from({length:23},(_,i)=>'festival-audit-'+i)]){
 const m=G.generate(seed),occupied=new Set(),h=hash(m);fingerprints.add(h);geometryHashes.add(crypto.createHash('sha256').update(Buffer.from(m.cells)).digest('hex'));
 const reachable=G.distances(m,m.open,m.start);assert.equal(reachable.filter(d=>d>=0).length,m.floorTiles,seed+' disconnected');
 for(const p of [...m.structures,...m.loose])for(const i of G.rectCells(m,p)){assert.equal(m.cells[i],1);assert.equal(m.open[i],0);assert.ok(!occupied.has(i),'object overlap');occupied.add(i);if(m.loose.includes(p))assert.equal(m.protectedCells[i],0,'protected corridor occupied');}
 const stalls=m.structures.filter(p=>p.kind==='stall').map(p=>p.type);
 assert.ok(stalls.length>=5&&stalls.length<=7);
 assert.equal(new Set(stalls).size,stalls.length);
 for(const type of stalls){assert.ok(stallIds.has(type),type);seenStalls.add(type);}
 for(const type of ['yagura','lantern-string','festival-cart','mask-rack','bench','nobori','taiko'])assert.ok([...m.structures,...m.loose,...m.lanterns].some(p=>p.type===type));
 assert.equal(m.stairs.filter(p=>p.kind==='up').length,3);assert.equal(m.stairs.filter(p=>p.kind==='down').length,3);
 for(const a of m.stairs){assert.ok(reachable[a.y*m.w+a.x]>=0);for(const b of m.stairs)if(a!==b)assert.ok(Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y))>=9);}
 for(let x=0;x<m.w;x++){assert.equal(m.cells[x],0);assert.equal(m.cells[(m.h-1)*m.w+x],0);}for(let y=0;y<m.h;y++){assert.equal(m.cells[y*m.w],0);assert.equal(m.cells[y*m.w+m.w-1],0);}
 const wallcells=new Set();for(const p of m.lanterns)for(let dx=0;dx<4;dx++){const i=p.y*m.w+p.x+dx;assert.equal(m.cells[i],0);assert.ok(!wallcells.has(i));wallcells.add(i);}
 assert.ok(m.placementAudit.maxAnchorDetour<=2);assert.ok(m.placementAudit.maxLocalDetour<=2);assert.equal(m.items.length+m.enemies.length,0);
 assert.equal(hash(G.generate(seed)),h,'seed not deterministic');results.push({seed,hash:h,attempts:m.generatorAttempts,stalls:m.structures.length-1,loose:m.loose.length,lanterns:m.lanterns.length,doors:m.doors.length,floor:m.floorTiles,stairDistance:m.stairDistance,detour:m.placementAudit.maxAnchorDetour});
}
assert.equal(fingerprints.size,results.length);assert.equal(geometryHashes.size,results.length);
assert.equal(stallIds.size,10);
assert.deepEqual(seenStalls,stallIds);
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1}),errors=[],failed=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failed.push([r.status(),r.url()]);});
 await p.goto(url+'/festival130/');await p.waitForFunction(()=>window.festivalReady);
 assert.ok(await p.evaluate(()=>festival130.getOverview()));
 const first=await p.evaluate(()=>JSON.stringify(festival130.getMap().structures));await p.click('#generate');await p.waitForFunction(()=>festivalReady);assert.equal(await p.evaluate(()=>JSON.stringify(festival130.getMap().structures)),first);
 await p.click('#random');assert.notEqual(await p.inputValue('#seed'),'20261109-8');await p.fill('#seed','20261109-8');await p.click('#generate');await p.waitForFunction(()=>festivalReady);
 const save=async(name)=>{const data=await p.evaluate(()=>document.getElementById('map').toDataURL());fs.writeFileSync(path.join(D,name),Buffer.from(data.split(',')[1],'base64'));};
 // Export the entire generated floor at its native 32px grid, with no manual geometry edits.
 await p.evaluate(()=>{const c=document.getElementById('map');c.width=2560;c.height=2240;festival130.setOverview(true);});await save('floor8-full130.png');
 await p.evaluate(()=>{const c=document.getElementById('map');c.width=640;c.height=448;festival130.setOverview(true);});await save('overview130.png');
 await p.selectOption('#focus','4');await p.click('#visit');await p.evaluate(()=>festival130.focusAt({x:44,y:23},'구라·아키로제 노점 거리 검토'));await save('stalls130.png');
 const original=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.uncheck('#objects');assert.notEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),original);await p.check('#objects');assert.equal(await p.evaluate(()=>document.getElementById('map').toDataURL()),original);
 await p.check('#fog');assert.notEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),original);await p.uncheck('#fog');assert.equal(await p.evaluate(()=>document.getElementById('map').toDataURL()),original);
 await p.click('#plaza');await save('plaza130.png');
 const actions=await p.evaluate(()=>{const a=festival130,m=a.getMap(),s=a.getState(),d=m.doors[0];if(!d)throw Error('No door in default seed');const neighbours=[[1,0],[-1,0],[0,1],[0,-1]],q=neighbours.map(([dx,dy])=>({x:d.x+dx,y:d.y+dy})).find(p=>m.open[p.y*m.w+p.x]);a.focusAt(q,'door test');const before=s.turns;a.move(d.x-q.x,d.y-q.y);if(s.player.x!==q.x||s.player.y!==q.y||!s.opened.has(d.id)||s.turns!==before+1)throw Error('door opening turn');document.getElementById('close').click();if(s.opened.has(d.id))throw Error('door close');a.move(d.x-q.x,d.y-q.y);a.move(d.x-q.x,d.y-q.y);if(s.player.x!==d.x||s.player.y!==d.y)throw Error('door entry');
  const block=m.structures[0],edge={x:block.x+1,y:block.y+block.footH};a.focusAt(edge,'collision test');const beforeBlock=s.turns;if(a.move(0,-1)||s.turns!==beforeBlock)throw Error('stage collision');if(a.route(m.exit).length<1)throw Error('exit route');const explored=s.explored.reduce((n,v)=>n+v,0);if(explored>=m.floorTiles)throw Error('fog explored whole map');return{doorOpenClose:true,stageCollision:true,exitPath:true,explored};});
 const visits=await p.evaluate(()=>{const a=festival130,m=a.getMap();for(const q of m.focusOptions){a.focusAt(a.approach(q),'asset focus');if(!m.open[a.getState().player.y*m.w+a.getState().player.x])throw Error('bad focus');}return m.focusOptions.length;});
 for(const seed of ['festival-browser-1','festival-browser-2']){await p.fill('#seed',seed);await p.click('#generate');await p.waitForFunction(()=>festivalReady);}
 await p.fill('#seed','20261109-8');await p.click('#generate');await p.waitForFunction(()=>festivalReady);await p.screenshot({path:path.join(D,'page130.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile overflow');assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const report={status:'passed',revision:130,generatedSeeds:results,deterministic:true,distinctGeometryHashes:fingerprints.size,stallTypesSeen:seenStalls.size,allSevenPropTypes:true,nonOverlapping:true,connected:true,stairsPerFloor:6,minStairChebyshev:9,maxLooseDetour:2,actions,focusVisits:visits,mobileOverflow:false,pageErrors:errors,failedRequests:failed,nativeIntegrated:false};fs.writeFileSync(path.join(D,'validation.json'),JSON.stringify(report,null,2)+'\n');
 const m=G.generate('20261109-8');fs.writeFileSync(path.join(D,'map130.json'),JSON.stringify({...m,cells:Array.from(m.cells),open:Array.from(m.open),baselineOpen:Array.from(m.baselineOpen),protectedCells:Array.from(m.protectedCells)},null,2)+'\n');console.log(JSON.stringify({status:report.status,seeds:results.length,default:results[0],actions,focusVisits:visits,pageErrors:errors,failedRequests:failed}));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
