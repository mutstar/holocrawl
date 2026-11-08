const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'preview/city-facilities95'),previous=path.join(root,'preview/city-facilities94');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'))),v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));
 assert.equal(v.status,'passed');assert.equal(v.facilities,9);assert.equal(m.normalWallRevision,92);
 assert.ok(v.checks.every(c=>c.normal92OutsideFacilityUnchanged&&c.interiorSceneryUnchanged&&c.geometryUnchanged&&c.doorStateChangesOnlyDoorCells));
 for(const map of m.maps){assert.equal(sha(path.join(out,map.map)),sha(path.join(previous,map.map)));assert.equal(sha(path.join(out,map.images.previous94)),sha(path.join(previous,`${map.facility}-integrated92.png`)))}
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1320,height:1060}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/city-facilities95/?focus=facility`);await page.waitForFunction(()=>window.ready);
  const checks=[];
  for(let i=0;i<m.maps.length;i++){
   if(i){await page.locator('#sample').selectOption(String(i));await page.waitForFunction(()=>window.ready)}
   await page.locator('#facility').click();const initial=await page.evaluate(()=>window.cityFacilities95.getView());assert.equal(initial.scale,2);assert.equal(initial.style,'new95');
   if(i<3)await page.screenshot({path:path.join(out,`${m.maps[i].facility}-detail.png`),fullPage:true});
   if(m.maps[i].doors.length){
    assert.equal(await page.locator('#doors').isEnabled(),true);await page.locator('#doors').click();assert.equal(await page.evaluate(()=>window.cityFacilities95.getView().doorsOpen),true);
    assert.ok((await page.evaluate(()=>window.cityFacilities95.getImage())).endsWith(m.maps[i].openImage));
    assert.deepEqual(await page.evaluate(()=>window.cityFacilities95.getView().center),initial.center);
    if(i===0)await page.screenshot({path:path.join(out,'holox-open.png'),fullPage:true});
    await page.locator('#doors').click();assert.equal(await page.evaluate(()=>window.cityFacilities95.getView().doorsOpen),false);
   }else assert.equal(await page.locator('#doors').isEnabled(),false);
   await page.locator('[data-style="previous94"]').click();assert.equal(await page.locator('#doors').isEnabled(),false);assert.deepEqual(await page.evaluate(()=>window.cityFacilities95.getView().center),initial.center);
   await page.locator('[data-style="new95"]').click();await page.locator('#entrance').click();const entrance=m.maps[i].entrances[0];assert.deepEqual(await page.evaluate(()=>window.cityFacilities95.getView().center),{x:entrance.x+.5,y:entrance.y+.5});
   await page.locator('[data-mode="fit"]').click();assert.equal(await page.evaluate(()=>window.cityFacilities95.getView().mode),'fit');
   if(i===0)await page.screenshot({path:path.join(out,'overview.png'),fullPage:true});
   checks.push({facility:m.maps[i].facility,wallComparison:true,doorStates:m.maps[i].doors.length?'opened-and-closed':'open-portal',entranceFocus:true,fullMap:true});
  }
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',checks,mobileOverflow:false,pageErrors:errors,native94GeometryUnchanged:true},null,2)+'\n');
  console.log('Verified nine facilities, protected normal92 walls, new closed/open doors, portals, comparison and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
