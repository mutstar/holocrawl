const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/basic-doors99');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));assert.equal(v.status,'passed');assert.equal(v.doorDesigns,10);assert.ok(v.spritesIdenticalAcrossOrientations&&v.openCentersTransparent&&v.closedCentersOpaque);assert.ok(v.checks.every(c=>c.outsideDoorPixelsChanged===0));
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1360,height:950}}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(`${previewURL}/basic-doors99/`);await p.waitForFunction(()=>window.ready);
  assert.equal(await p.locator('#gallery img').count(),10);
  const loaded=()=>p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const direction of ['horizontal','vertical']){await p.locator(`[data-direction="${direction}"]`).click();for(const state of ['closed','open']){
   await p.locator(`[data-state="${state}"]`).click();await loaded();const names=await p.locator('#gallery img').evaluateAll(imgs=>imgs.map(i=>i.getAttribute('src')));assert.ok(names.every(n=>n.includes(`-${direction}-${state}.png`)));
  }}
  await p.locator('[data-direction="horizontal"]').click();await p.locator('[data-state="closed"]').click();await p.locator('[data-zoom="2"]').click();await loaded();await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await p.locator('[data-state="open"]').click();await loaded();await p.screenshot({path:path.join(out,'overview-open.png'),fullPage:true});
  await p.locator('[data-detail="glass"]').click();await loaded();assert.equal(await p.locator('#detailGrid img').count(),4);assert.equal(await p.evaluate(()=>window.basicDoors99.getView().detail),'glass');
  await p.locator('#closeDetail').click();assert.equal(await p.locator('#detail').isVisible(),false);
  for(const zoom of [1,2,3]){await p.locator(`[data-zoom="${zoom}"]`).click();assert.equal(await p.locator('#gallery img').first().evaluate(i=>i.getBoundingClientRect().width),64*zoom)}
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',galleryDoors:10,orientations:2,states:2,zoom123:true,detailStates:4,mobileOverflow:false,pageErrors:errors},null,2)+'\n');console.log('Verified10 door variants, both wall axes/states, enlargement, detail panel and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
