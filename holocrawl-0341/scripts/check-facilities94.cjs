const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'preview/city-facilities94'),run=path.join(root,'analysis/native-facilities94');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'))),v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),plan=JSON.parse(fs.readFileSync(path.join(run,'plan.json')));
 assert.equal(v.status,'passed');assert.equal(v.facilitiesCovered,9);assert.equal(new Set(m.maps.map(e=>e.facility)).size,9);assert.equal(v.uniqueGeometries,9);
 assert.ok(v.checks.every(c=>c.nativeConnected&&c.entrancePreserved&&c.interiorPreservedOutsideContactBand&&c.nonWallPixelsChanged===0&&c.normal92RetainedOutsideFacility));
 assert.equal(sha(path.join(root,'engine/upstream/crawl-ref/source/crawl.exe')),plan.inputSha256.originalExecutable);
 assert.equal(sha(path.join(root,'engine/upstream/crawl-ref/source/holo34-city.cc')),plan.inputSha256.originalSource);
 for(const e of m.maps){const d=JSON.parse(fs.readFileSync(path.join(out,e.map)));assert.equal(d.facility,e.facility);assert.equal(sha(path.join(out,e.map)),e.mapSha256);assert.ok(e.entrances.length)}
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1320,height:1060}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/city-facilities94/`);await page.waitForFunction(()=>window.ready);
  assert.equal(await page.locator('#sample option').count(),9);
  const checks=[];
  for(let i=0;i<m.maps.length;i++){
   if(i){await page.locator('#sample').selectOption(String(i));await page.waitForFunction(()=>window.ready)}
   const fit=await page.evaluate(()=>({v:window.cityFacilities94.getView(),w:document.getElementById('map').width,h:document.getElementById('map').height}));
   assert.equal(fit.v.mode,'fit');assert.equal(fit.v.style,'integrated92');assert.ok(fit.v.ox>=0&&fit.v.oy>=0&&fit.v.scale*2560<=fit.w+.01&&fit.v.scale*2240<=fit.h+.01);
   if(i===0)await page.screenshot({path:path.join(out,'overview.png'),fullPage:true});
   await page.locator('#corner').click();assert.deepEqual(await page.evaluate(()=>window.cityFacilities94.getView().center),m.maps[i].focus);
   assert.equal(await page.evaluate(()=>window.cityFacilities94.getView().scale),2);
   await page.screenshot({path:path.join(out,`${m.maps[i].facility}-detail.png`),fullPage:true});
   await page.locator('[data-style="original84"]').click();assert.deepEqual(await page.evaluate(()=>window.cityFacilities94.getView().center),m.maps[i].focus);
   await page.locator('[data-style="integrated92"]').click();
   const imageURL=await page.evaluate(()=>window.cityFacilities94.getImage());assert.ok(imageURL.endsWith(m.maps[i].images.integrated92));
   checks.push({facility:m.maps[i].facility,seed:m.maps[i].seed,fullMapFits:true,facilityFocus:true,samePositionComparison:true});
  }
  await page.locator('[data-mode="actual"]').click();assert.equal(await page.evaluate(()=>window.cityFacilities94.getView().scale),1);
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',checks,mobileOverflow:false,pageErrors:errors,originalEnginePreserved:true},null,2)+'\n');
  console.log('Verified all9 facility maps, complete floor views, entrance focus, comparison, original engine and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
