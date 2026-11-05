const fs=require('fs'),path=require('path'),assert=require('assert');const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{const root=path.resolve(__dirname,'../preview/holox-floor52'),results=[];
for(let n=0;n<3;n++){
 const p=await b.newPage({viewport:{width:1280,height:1080}}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
 await p.goto(previewURL+'/holox-floor52/?map='+n);await p.waitForFunction(()=>window.ready);
 assert(await p.locator('#placementInfo').innerText());
 const decor=await p.evaluate(()=>{const f=vaultReview,v=f.vault,d=v.entranceDecor,o=f.layout.origin;return {kind:d.kind,onWalls:d.wallCells.every(([x,y])=>v.rows[y][x]==='#'),openThreshold:f.pass(o.x+d.opening.x,o.y+d.opening.y),unchangedRows:JSON.stringify(v.rows),unchangedScenario:JSON.stringify(f.layout.map.rows)}});
 const previous=JSON.parse(fs.readFileSync(path.join(root,'../holox-floor48/vault.json'))),scenario=JSON.parse(fs.readFileSync(path.join(root,'../holox-floor48/scenario-'+n+'.json')));
 assert.strictEqual(decor.kind,'holodori-armored-entry');assert(decor.onWalls&&decor.openThreshold);
 assert.strictEqual(decor.unchangedRows,JSON.stringify(previous.rows));assert.strictEqual(decor.unchangedScenario,JSON.stringify(scenario.map.rows));
 await p.locator('#closeup').screenshot({path:path.join(root,'lab-'+n+'.png')});
 await p.locator('#field').screenshot({path:path.join(root,'approach-'+n+'.png')});
 await p.locator('#overview').click();await p.locator('#field').screenshot({path:path.join(root,'floor-'+n+'.png')});
 await p.locator('#labView').click();await p.locator('#stairsStart').click();
 const reach=await p.evaluate(()=>{const f=vaultReview,o=f.layout.origin,v=f.vault;return{atStairs:JSON.stringify(f.getState().player)===JSON.stringify(f.layout.stairsStart),allMembers:v.stations.every(s=>{for(let y=s.y;y<s.y+s.h;y++)for(let x=s.x;x<s.x+s.w;x++)for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]])if(f.route({x:o.x+x+dx,y:o.y+y+dy}).length>0)return true;return false}),allRewards:Object.values(v.rewardOptions).flat().every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0),stairs:f.layout.placement.stairsPreserved.every(a=>f.route(a).length>0),size:[f.layout.map.w,f.layout.map.h],labDoors:v.rows.some(r=>r.includes('+'))}});
 assert(reach.atStairs&&reach.allMembers&&reach.allRewards&&reach.stairs&&!reach.labDoors);assert.deepStrictEqual(reach.size,[80,70]);
 await p.locator('#reset').click();await p.evaluate(()=>vaultReview.walkTo(vaultReview.rewards()[0]));await p.waitForFunction(()=>vaultReview.getState().taken.length===1,{timeout:20000});
 await p.locator('#fog').click();assert(await p.evaluate(()=>vaultReview.getState().fog));
 await p.locator('#stairsStart').click();assert(await p.evaluate(()=>vaultReview.getState().explored.reduce((a,b)=>a+b,0)<250));
 await p.setViewportSize({width:390,height:850});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 results.push({case:n,status:'passed',...reach,integratedEntry:true,unchangedCollision:true,autoEnterAndPickup:true,fogAtStairs:true,mobileNoOverflow:true,errors});await p.close();
}
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify({status:'passed',scope:'Three static native-floor snapshots with browser vault insertion; not native generator integration',cases:results},null,2));console.log(JSON.stringify(results));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
