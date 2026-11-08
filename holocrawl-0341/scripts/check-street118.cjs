const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),O=path.join(R,'preview/city-street118'),{generate,reach}=require('../preview/city-street118/ambient118.js');
const manifest=JSON.parse(fs.readFileSync(path.join(O,'manifest.json'))),plans=[];
assert.equal(manifest.maps.length,36);
for(const entry of manifest.maps){
 const raw=fs.readFileSync(path.resolve(O,entry.file)),m=JSON.parse(raw),a=generate(m);
 assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),entry.sha256);
 assert.deepEqual(a,generate(m));assert.ok(a.validation.connected&&a.validation.stairsConnected&&a.validation.mainRoutesClear);
 assert.equal(new Set(a.blocked).size,a.blocked.length);assert.equal(a.validation.shops,2);assert.equal(a.validation.crates,a.validation.crateTarget);
 assert.equal(a.walls.length,4);assert.equal(a.fences.length,2);assert.equal(a.floor.filter(p=>p.type==='trash-bags').length,1);
 const special=[];for(let y=0;y<m.height;y++)for(let x=0;x<m.width;x++)if('<>+'.includes(m.rows[y][x]))special.push({x,y});
 for(const k of a.blocked){const[x,y]=k.split(',').map(Number),i=y*m.width+x;assert.equal(m.rows[y][x],'.');assert.equal(m.features[i],m.floors[i]);assert.ok(m.passable[i]);assert.ok(special.every(p=>Math.max(Math.abs(x-p.x),Math.abs(y-p.y))>3));if(m.origin){const o=m.origin;assert.ok(x<o.x-2||y<o.y-2||x>=o.x+o.width+2||y>=o.y+o.height+2);}}
 const used=new Set();for(const p of [...a.walls.map(p=>({...p,length:2})),...a.infra])for(let dx=0;dx<p.length;dx++){const x=p.x+dx,y=p.y,k=`${x},${y}`;assert.ok(!used.has(k));used.add(k);assert.equal(m.rows[y][x],'#');assert.ok(special.every(q=>Math.max(Math.abs(x-q.x),Math.abs(y-q.y))>3));if(m.origin){const o=m.origin;assert.ok(x<o.x-2||y<o.y-2||x>=o.x+o.width+2||y>=o.y+o.height+2);}}
 plans.push({seed:m.seed,depth:m.depth,...a.validation,utilities:a.infra.map(p=>p.type)});
}
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1280,height:1000}}),errors=[],failed=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
 await p.goto(`${previewURL}/city-street118/`);await p.waitForFunction(()=>window.ready,{},{timeout:60000});
 let frames=0,blocked=0,doorPairs=0;
 for(let i=0;i<manifest.maps.length;i++){
  if(i){await p.locator('#sample').selectOption(String(i));await p.waitForFunction(i=>window.ready&&play118.getMap().seed===play118.manifest.maps[i].seed&&play118.getMap().depth===play118.manifest.maps[i].depth,i);}
  const checks=await p.evaluate(()=>{
   const api=play118,m=api.getMap(),a=api.getAmbience();let frames=0;for(let i=0;i<api.getProbe().frames.length;i++){if(api.oracleFrame(i)!==0)throw Error('Native LOS mismatch');frames++;}
   for(const k of a.blocked){const[x,y]=k.split(',').map(Number);if(api.pass(x,y))throw Error('Prop passable');}
   let doorPairs=0;for(const d of m.doors){const pts=[[0,1],[1,0],[0,-1],[-1,0]].map(([dx,dy])=>({x:d.x+dx,y:d.y+dy})).filter(p=>api.pass(p.x,p.y)&&m.rows[p.y][p.x]!=='+');if(!pts[0])continue;const q=pts[0];api.reset(q,'door test');if(!api.move(d.x-q.x,d.y-q.y))throw Error('Open failed');if(d.linked.some(([x,y])=>!api.getState().opened.includes(`${x},${y}`)))throw Error('Group failed');api.move(d.x-q.x,d.y-q.y);if(api.getState().player.x!==d.x||api.getState().player.y!==d.y)throw Error('Step failed');doorPairs++;}
   document.getElementById('stairStart').click();return{frames,blocked:a.blocked.length,doorPairs};
  });frames+=checks.frames;blocked+=checks.blocked;doorPairs+=checks.doorPairs;
 }
 // Actual code-rendered scene captures, one floor per panel, with no manual art compositing.
 const scenes=[];
 for(const[i,kind]of [[0,'shops'],[1,'utilities'],[2,'crate']]){
  await p.locator('#sample').selectOption(String(i));await p.waitForFunction(i=>window.ready&&play118.getMap().depth===play118.manifest.maps[i].depth,i);
  await p.locator('#fog').uncheck();await p.locator('[data-zoom="2"]').click();await p.evaluate(kind=>play118.focusAmbient(kind),kind);
  await p.locator('#field').screenshot({path:path.join(O,`floor${i+1}.png`)});
  scenes.push({i,kind,seed:await p.evaluate(()=>play118.getMap().seed)});
 }
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={status:'passed',revision:118,nativeAmbientIntegrated:false,nativeBackgroundSource:107,maps:36,deterministic:true,sourceHashesPreserved:true,stairRoutesProtected:true,nativeLOSFrames:frames,blockedCells:blocked,openedAndTraversedDoorGroups:doorPairs,plans,scenes,errors,failed};
 fs.writeFileSync(path.join(O,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:'passed',maps:36,frames,blocked,doorPairs,scenes}));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
