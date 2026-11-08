const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-random93');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.ok(v.connected&&v.newGeometry&&v.reviewed92RendererPixelMatch&&v.frozenInputsUnchanged);assert.equal(v.nonWallPixelsChanged,0);
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1320,height:1060}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/city-random93/`);await page.waitForFunction(()=>window.ready);
  assert.equal(await page.locator('#sample option').count(),1);
  const fit=await page.evaluate(()=>({v:window.cityRandom93.getView(),w:document.getElementById('map').width,h:document.getElementById('map').height}));
  assert.equal(fit.v.mode,'fit');assert.equal(fit.v.style,'concrete92');assert.ok(fit.v.ox>=0&&fit.v.oy>=0&&fit.v.scale*2560<=fit.w+.01&&fit.v.scale*2240<=fit.h+.01);
  await page.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await page.locator('#corner').click();assert.deepEqual(await page.evaluate(()=>window.cityRandom93.getView().center),m.maps[0].focus);assert.equal(await page.evaluate(()=>window.cityRandom93.getView().scale),2);
  await page.screenshot({path:path.join(out,'detail.png'),fullPage:true});
  await page.locator('[data-style="original84"]').click();assert.deepEqual(await page.evaluate(()=>window.cityRandom93.getView().center),m.maps[0].focus);
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',seed:m.maps[0].seed,fullMapFits:true,repaired92Default:true,focusAndZoom:true,materialSwitch:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');console.log('Verified fresh native floor, full repaired92 map, focus, comparison and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
