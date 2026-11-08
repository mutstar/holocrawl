const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-doors102');
(async()=>{const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));assert.equal(v.status,'passed');assert.equal(v.maps,9);assert.equal(v.ordinaryDoorCells,82);
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1380,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`${previewURL}/city-doors102/`);await p.waitForFunction(()=>window.ready);
  assert.equal(await p.locator('#sample').inputValue(),'2');
  await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await p.locator('#basicDoor').click();assert.equal(await p.evaluate(()=>cityDoors102.getView().scale),2);
  await p.screenshot({path:path.join(out,'door-detail.png'),fullPage:true});
  for(let i=0;i<9;i++){
   await p.locator('#sample').selectOption(String(i));await p.waitForFunction(()=>window.ready);
   const m=await p.evaluate(()=>cityDoors102.manifest.maps[cityDoors102.getView().sample]);
   if(m.doors.length){await p.locator('#doors').click();assert.ok((await p.evaluate(()=>cityDoors102.getImage())).endsWith(m.openImage));await p.locator('#doors').click()}
   else assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="previous95"]').click();assert.equal(await p.locator('#doors').isEnabled(),false);
   await p.locator('[data-style="new102"]').click();await p.locator('#facility').click();await p.locator('#entrance').click();
  }
  await p.locator('#sample').selectOption('2');await p.waitForFunction(()=>window.ready);await p.locator('[data-mode="fit"]').click();
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',maps:9,doorCells:82,defaultFacility:'dev',closedOpen:true,comparison:true,focus:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log('Verified9 full facility maps,82 existing basic doors, open/closed, comparison, focus and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
