const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'preview/city-concrete89');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'))),v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));
 assert.equal(v.status,'passed');assert.equal(v.priorGungeon88PixelMatch,true);assert.equal(v.checks.length,6);assert.ok(v.checks.every(c=>c.nonWallPixelsChanged===0&&c.alphaUnchanged));
 for(const map of manifest.maps){assert.equal(sha(path.join(root,map.sourceMap)),map.sourceMapSha256);const atlas=map.seed===802302584?'wall-audit85':'city-random82';assert.equal(sha(path.join(root,`preview/${atlas}/assets/wall.png`)),map.auditedWallAtlasSha256)}
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1380,height:1050}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/city-concrete89/`);await page.waitForFunction(()=>window.ready);
  const checks=[];
  for(let sample=0;sample<2;sample++){
   if(sample){await page.locator('#sample').selectOption(String(sample));await page.waitForFunction(()=>window.ready)}
   for(const style of manifest.styles){
    await page.locator(`[data-style="${style.id}"]`).click();
    assert.equal(await page.evaluate(()=>window.cityConcrete89.getView().style),style.id);
    assert.ok((await page.evaluate(()=>window.cityConcrete89.getImage())).endsWith(manifest.maps[sample].images[style.id]));
   }
   await page.locator('[data-style="concrete89"]').click();await page.locator('[data-mode="fit"]').click();
   const fit=await page.evaluate(()=>({view:window.cityConcrete89.getView(),w:document.getElementById('map').width,h:document.getElementById('map').height}));
   assert.ok(fit.view.ox>=0&&fit.view.oy>=0&&fit.view.scale*2560<=fit.w+.01&&fit.view.scale*2240<=fit.h+.01);
   await page.screenshot({path:path.join(out,`full-map-${sample+1}.png`),fullPage:true});
   await page.locator('#corner').click();assert.equal(await page.evaluate(()=>window.cityConcrete89.getView().scale),2);
   await page.screenshot({path:path.join(out,`detail-${sample+1}.png`),fullPage:true});
   const center=await page.evaluate(()=>window.cityConcrete89.getView().center);
   await page.locator('[data-style="original84"]').click();assert.deepEqual(await page.evaluate(()=>window.cityConcrete89.getView().center),center);
   await page.locator('[data-mode="actual"]').click();assert.equal(await page.evaluate(()=>window.cityConcrete89.getView().scale),1);
   await page.locator('#map').press('ArrowRight');assert.equal(await page.evaluate(()=>window.cityConcrete89.getView().center.x),center.x+2);
   checks.push({seed:manifest.maps[sample].seed,styles:3,fullMapFits:true,zoomAndPan:true,positionPreservedOnStyleChange:true});
  }
  await page.locator('[data-mode="fit"]').click();const r=await page.locator('#map').boundingBox();await page.locator('#map').click({position:{x:r.width/2,y:r.height/2}});assert.equal(await page.evaluate(()=>window.cityConcrete89.getView().mode),'actual');
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',checks,clickToZoom:true,mobileOverflow:false,auditedInputsUnchanged:true,pageErrors:errors},null,2)+'\n');
  console.log('Passed two complete native maps, three materials, fit, zoom, navigation, mobile and preserved inputs.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
