const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-facilities103'),src=path.resolve(__dirname,'../preview/city-doors102');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.equal(v.facilities,9);assert.equal(m.maps.length,9);
 assert.ok(v.checks.every(c=>c.wallMaterial92ExactOutsideInsets&&c.interiorSceneryUnchanged&&c.normalWallsAndBasicDoorsUnchanged&&c.geometryUnchanged&&c.outsideAllowedPixelsUnchanged));
 for(const map of m.maps){assert.equal(sha(path.join(out,map.map)),sha(path.join(src,map.map)));assert.equal(sha(path.join(out,map.images.previous102)),sha(path.join(src,`${map.facility}-closed102.png`)))}
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1380,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`${previewURL}/city-facilities103/?focus=facility`);await p.waitForFunction(()=>window.ready);
  assert.equal(await p.locator('#sample').inputValue(),'2');
  await p.screenshot({path:path.join(out,'dev-overview.png'),fullPage:true});
  await p.locator('[data-style="previous102"]').click();await p.screenshot({path:path.join(out,'dev-before.png'),fullPage:true});
  await p.locator('[data-style="new103"]').click();
  const checks=[];
  for(let i=0;i<9;i++){
   await p.locator('#sample').selectOption(String(i));await p.waitForFunction(()=>window.ready);await p.locator('#facility').click();
   assert.equal(await p.evaluate(()=>cityFacilities103.getView().style),'new103');
   await p.screenshot({path:path.join(out,`${m.maps[i].facility}-browser-detail.png`),fullPage:true});
   if(m.maps[i].doors.length){await p.locator('#doors').click();assert.ok((await p.evaluate(()=>cityFacilities103.getImage())).endsWith(m.maps[i].openImage));await p.locator('#doors').click()}
   else assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="previous102"]').click();assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="new103"]').click();await p.locator('#entrance').click();
   const entry=m.maps[i].entrances[0];assert.deepEqual(await p.evaluate(()=>cityFacilities103.getView().center),{x:entry.x+.5,y:entry.y+.5});
   await p.locator('[data-mode="fit"]').click();assert.equal(await p.evaluate(()=>cityFacilities103.getView().mode),'fit');
   checks.push({facility:m.maps[i].facility,fullMap:true,detail:true,entrance:true,beforeAfter:true,doorState:true});
  }
  await p.locator('#sample').selectOption('2');await p.waitForFunction(()=>window.ready);await p.locator('[data-mode="fit"]').click();
  await p.screenshot({path:path.join(out,'fullmap.png'),fullPage:true});
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',checks,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log('Verified9 repaired facility perimeters, source hashes, all views, comparisons and ordinary door states.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
