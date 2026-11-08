const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/basic-doors101');
(async()=>{const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));assert.equal(v.status,'passed');assert.ok(v.jambsEqualWidth&&v.doubleSpriteMirrorExact&&v.spritesIdenticalAcrossOrientations);assert.deepEqual(v.doubleLeafWidths,[13,13]);assert.equal(v.openingCenterX,15.5);assert.equal(v.doubleLeafHeight,26);assert.ok(v.single100PixelIdentical);assert.ok(v.checks.every(c=>c.outsideDoorPixelsChanged===0));
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1280,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(`${previewURL}/basic-doors101/`);await p.waitForFunction(()=>window.ready);assert.equal(await p.locator('#rows img').count(),20);
  const loaded=()=>p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth===64));
  for(const state of ['closed','open']){await p.locator(`[data-state="${state}"]`).click();await loaded();const names=await p.locator('#rows img').evaluateAll(imgs=>imgs.map(i=>i.getAttribute('src')));assert.ok(names.every(n=>n.endsWith(`-${state}.png`)));await p.screenshot({path:path.join(out,`overview-${state}.png`),fullPage:true})}
  for(const version of ['before','after']){await p.locator(`[data-version="${version}"]`).click();await loaded();assert.equal(await p.evaluate(()=>basicDoors101.getView().version),version)}await p.locator('[data-state="closed"]').click();await loaded();await p.locator('#centerLines').check();assert.ok(await p.locator('#tablewrap').evaluate(e=>e.classList.contains('centers')));await p.locator('#centerLines').uncheck();
  for(const zoom of [1,2,3]){await p.locator(`[data-zoom="${zoom}"]`).click();assert.equal(await p.locator('#rows img').first().evaluate(i=>i.getBoundingClientRect().width),64*zoom)}
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',simultaneousViews:20,states:2,beforeAfter:true,singleUnchanged:true,centerLines:true,zoom123:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');console.log('Verified centered doors and20 simultaneous axis/leaf views, states, centerline, zoom and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
