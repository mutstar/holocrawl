const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-facilities106'),src=path.resolve(__dirname,'../preview/city-facilities105');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.equal(v.facilities,9);assert.equal(m.maps.find(c=>c.facility==='theater').memberDetails.length,3);assert.equal(m.maps.find(c=>c.facility==='gamers').memberDetails.length,4);assert.equal(m.maps.length,9);
 assert.ok(v.checks.every(c=>c.editsOnlyOnExistingInteriorBlockedCells&&c.outsideFourDetailBoxesUnchanged&&c.walls105AndDoors105Unchanged&&c.geometryUnchanged));
 for(const map of m.maps){assert.equal(sha(path.join(out,map.map)),sha(path.join(src,map.map)));assert.equal(sha(path.join(out,map.images.previous105)),sha(path.join(src,`${map.facility}-closed105.png`)))}
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1380,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`${previewURL}/city-facilities106/?focus=facility`);await p.waitForFunction(()=>window.ready);
  assert.equal(await p.locator('#sample').inputValue(),'3');
  await p.screenshot({path:path.join(out,'dining-overview.png'),fullPage:true});
  await p.locator('[data-style="previous105"]').click();await p.screenshot({path:path.join(out,'dining-before.png'),fullPage:true});
  await p.locator('[data-style="new106"]').click();
  const checks=[];
  for(let i=0;i<9;i++){
   await p.locator('#sample').selectOption(String(i));await p.waitForFunction(()=>window.ready);await p.locator('#facility').click();
   assert.equal(await p.evaluate(()=>cityFacilities106.getView().style),'new106');
   await p.screenshot({path:path.join(out,`${m.maps[i].facility}-browser-detail.png`),fullPage:true});
   if(m.maps[i].doors.length){await p.locator('#doors').click();assert.ok((await p.evaluate(()=>cityFacilities106.getImage())).endsWith(m.maps[i].openImage));await p.locator('#doors').click()}
   else assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="previous105"]').click();assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="new106"]').click();await p.locator('#entrance').click();
   const entry=m.maps[i].entrances[0];assert.deepEqual(await p.evaluate(()=>cityFacilities106.getView().center),{x:entry.x+.5,y:entry.y+.5});
   await p.locator('[data-mode="fit"]').click();assert.equal(await p.evaluate(()=>cityFacilities106.getView().mode),'fit');
   checks.push({facility:m.maps[i].facility,fullMap:true,detail:true,entrance:true,beforeAfter:true,doorState:true});
  }
  await p.locator('#sample').selectOption('4');await p.waitForFunction(()=>window.ready);await p.locator('[data-mode="fit"]').click();
  await p.screenshot({path:path.join(out,'fullmap.png'),fullPage:true});await p.locator('#facility').click();await p.screenshot({path:path.join(out,'gamers-overview.png'),fullPage:true});await p.locator('#doors').click();await p.screenshot({path:path.join(out,'gamers-open.png'),fullPage:true});
  await p.goto(`${previewURL}/city-facilities106/audit.html`);await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));assert.equal(await p.locator('article').count(),30);assert.equal(await p.locator('strong.visibility-improved').count(),4);for(const [facility,count] of [['mountain',5],['dining',4],['fantasy',4],['wheel',4],['market',4],['holox',5],['dev',4]]){await p.locator('#filter').selectOption(facility);assert.equal(await p.locator('section:not([hidden]) article').count(),count)}await p.locator('#filter').selectOption('market');await p.screenshot({path:path.join(out,'market-audit.png'),fullPage:true});await p.locator('#filter').selectOption('all');await p.screenshot({path:path.join(out,'audit-overview.png'),fullPage:true});await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',auditedMembers:30,auditedFacilities:7,improved:4,checks,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log('Verified30 member audit cards,7 filters,4 repairs and9 preserved maps, sources, states and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
