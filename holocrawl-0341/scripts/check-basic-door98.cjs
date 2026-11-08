const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/basic-door98');
(async()=>{const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));assert.equal(v.status,'passed');assert.ok(v.checks.every(c=>c.outsideDoorPixelsChanged===0));assert.ok(v.original96Unchanged&&v.openCenterTransparent);
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1200,height:920}}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(`${previewURL}/basic-door98/`);await p.waitForFunction(()=>window.ready);
  for(const direction of ['horizontal','vertical']){await p.locator(`[data-direction="${direction}"]`).click();for(const state of ['closed','open']){await p.locator(`[data-state="${state}"]`).click();await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth===96));for(const id of ['a','b'])assert.equal(await p.locator(`[data-variant="${id}"]`).getAttribute('src'),`${id}-${direction}-${state}.png`)}}
  await p.locator('[data-direction="horizontal"]').click();await p.locator('[data-state="closed"]').click();
  for(const zoom of [1,2,4]){await p.locator(`[data-zoom="${zoom}"]`).click();assert.equal(await p.locator('[data-variant="b"]').evaluate(i=>i.getBoundingClientRect().width),96*zoom)}
  await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth===96));await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await p.locator('[data-state="open"]').click();await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth===96));await p.screenshot({path:path.join(out,'overview-open.png'),fullPage:true});
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',variants:2,orientations:2,states:2,zoom124:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');console.log('VerifiedA/B door variation98, both orientations/states, zoom and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
