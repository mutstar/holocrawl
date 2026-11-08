const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-facilities104'),src=path.resolve(__dirname,'../preview/city-facilities103');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.equal(v.facilities,9);assert.equal(v.checks.find(c=>c.facility==='theater').members.length,3);assert.equal(v.checks.find(c=>c.facility==='gamers').members.length,4);assert.equal(m.maps.length,9);
 assert.ok(v.checks.every(c=>c.newArtOnlyOnExistingWallCells&&c.outsideDecorationAndFacilityDoorCellsUnchanged&&c.normalWallsAndBasicDoorsUnchanged&&c.geometryUnchanged&&c.doorFacing.every(d=>d.spriteFacing==='front'&&!d.rotationApplied)));
 for(const map of m.maps){assert.equal(sha(path.join(out,map.map)),sha(path.join(src,map.map)));assert.equal(sha(path.join(out,map.images.previous103)),sha(path.join(src,`${map.facility}-closed103.png`)))}
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1380,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`${previewURL}/city-facilities104/?focus=facility`);await p.waitForFunction(()=>window.ready);
  assert.equal(await p.locator('#sample').inputValue(),'1');
  await p.screenshot({path:path.join(out,'theater-overview.png'),fullPage:true});
  await p.locator('[data-style="previous103"]').click();await p.screenshot({path:path.join(out,'theater-before.png'),fullPage:true});
  await p.locator('[data-style="new104"]').click();
  const checks=[];
  for(let i=0;i<9;i++){
   await p.locator('#sample').selectOption(String(i));await p.waitForFunction(()=>window.ready);await p.locator('#facility').click();
   assert.equal(await p.evaluate(()=>cityFacilities104.getView().style),'new104');
   await p.screenshot({path:path.join(out,`${m.maps[i].facility}-browser-detail.png`),fullPage:true});
   if(m.maps[i].doors.length){await p.locator('#doors').click();assert.ok((await p.evaluate(()=>cityFacilities104.getImage())).endsWith(m.maps[i].openImage));await p.locator('#doors').click()}
   else assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="previous103"]').click();assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="new104"]').click();await p.locator('#entrance').click();
   const entry=m.maps[i].entrances[0];assert.deepEqual(await p.evaluate(()=>cityFacilities104.getView().center),{x:entry.x+.5,y:entry.y+.5});
   await p.locator('[data-mode="fit"]').click();assert.equal(await p.evaluate(()=>cityFacilities104.getView().mode),'fit');
   checks.push({facility:m.maps[i].facility,fullMap:true,detail:true,entrance:true,beforeAfter:true,doorState:true});
  }
  await p.locator('#sample').selectOption('4');await p.waitForFunction(()=>window.ready);await p.locator('[data-mode="fit"]').click();
  await p.screenshot({path:path.join(out,'fullmap.png'),fullPage:true});await p.locator('#facility').click();await p.screenshot({path:path.join(out,'gamers-overview.png'),fullPage:true});await p.locator('#doors').click();await p.screenshot({path:path.join(out,'gamers-open.png'),fullPage:true});
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',checks,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log('Verified restored member panels and front-facing facility doors on9 maps, source hashes, all views, comparisons and ordinary door states.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
