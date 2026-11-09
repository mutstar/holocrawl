const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const{generate,floors}=require('../preview/facility-pool131/planner131.js'),{chromium,executablePath}=require('./portable-browser-tools.cjs');
const D=path.resolve(__dirname,'../preview/facility-pool131'),registry=JSON.parse(fs.readFileSync(path.join(D,'registry.json'),'utf8')),regions=['JP','ID','EN'];
assert.equal(registry.facilities.length,42);assert.equal(new Set(registry.facilities.map(f=>f.id)).size,42);assert.equal(registry.facilities.filter(f=>f.status==='built').length,9);assert.equal(floors().length,34);
const appeared=new Map(registry.facilities.map(f=>[f.id,new Set()])),selected={JP:0,ID:0,EN:0},available={JP:0,ID:0,EN:0};let realSelections=0;
for(let n=0;n<1000;n++){
 const seed='pool131-'+n,p=generate(registry,seed,{includePlanned:true});assert.deepEqual(generate(registry,seed,{includePlanned:true}),p);
 assert.deepEqual(p.guaranteed,[{floorId:'JP-main-1',facilityId:'holohome',chance:1}]);assert.ok(!p.poolSnapshot.includes('holohome'));
 assert.equal(new Set(p.slots.map(s=>s.id)).size,34);const used=new Set();
 for(const s of p.slots){assert.ok(regions.includes(s.region));available[s.region]++;if(!s.facilityId)continue;assert.ok(!used.has(s.facilityId));used.add(s.facilityId);appeared.get(s.facilityId).add(s.region);selected[s.region]++;}
 // Affiliation is narrative metadata, not a regional eligibility filter.
 const changed={...registry,facilities:registry.facilities.map(f=>({...f,affiliation:'JP'}))};assert.deepEqual(generate(changed,seed,{includePlanned:true}),p);
 const ready=generate(registry,seed);const readyUsed=new Set();for(const s of ready.slots)if(s.facilityId){assert.equal(registry.facilities.find(f=>f.id===s.facilityId).status,'built');assert.ok(!readyUsed.has(s.facilityId));readyUsed.add(s.facilityId);realSelections++;}
}
for(const[id,seen]of appeared)assert.deepEqual([...seen].sort(),['EN','ID','JP'],id+' did not appear in every region');
for(const r of regions)assert.ok(selected[r]/available[r]>.47&&selected[r]/available[r]<.53);
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{const p=await b.newPage({viewport:{width:1440,height:1100}}),errors=[],failed=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
 await p.goto((process.env.HOLOCRAWL_PREVIEW_URL||'http://127.0.0.1:8798')+'/facility-pool131/');await p.waitForFunction(()=>window.facilityPoolReady);assert.equal(await p.locator('#built .card').count(),9);assert.equal(await p.locator('#planned .card').count(),33);assert.equal(await p.locator('#regions .slot').count(),34);
 await p.selectOption('#mode','future');const first=await p.evaluate(()=>JSON.stringify(facilityPool131.getPlan()));await p.click('#roll');assert.equal(await p.evaluate(()=>JSON.stringify(facilityPool131.getPlan())),first);assert.ok((await p.innerText('#saveState')).includes('복원'));
 await p.reload();await p.waitForFunction(()=>facilityPoolReady);await p.selectOption('#mode','future');assert.equal(await p.evaluate(()=>JSON.stringify(facilityPool131.getPlan())),first);assert.ok((await p.innerText('#saveState')).includes('복원'));
 await p.click('#random');assert.notEqual(await p.evaluate(()=>JSON.stringify(facilityPool131.getPlan())),first);await p.fill('#seed','SHARED-20261109');await p.click('#roll');await p.screenshot({path:path.join(D,'pool131.png'),fullPage:false});
 await p.selectOption('#mode','built');const images=await p.locator('#built img').evaluateAll(es=>es.map(e=>({ok:e.complete&&e.naturalWidth>0,src:e.src})));assert.ok(images.every(i=>i.ok));
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const report={status:'passed',revision:131,total:42,built:9,planned:33,campaignSeeds:1000,eligibleFloors:34,allFacilitiesAppearInAllRegions:true,affiliationNeverFilters:true,noRunDuplicates:true,deterministic:true,builtModeNeverUsesPlanned:true,selected,available,persistedBrowserPlan:true,imagesLoaded:images.length,mobileOverflow:false,pageErrors:errors,failedRequests:failed,nativeIntegrated:false,geometricPlacementTested:false};fs.writeFileSync(path.join(D,'validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
