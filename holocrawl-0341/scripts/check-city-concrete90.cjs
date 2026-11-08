const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'preview/city-concrete90');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'))),v=JSON.parse(fs.readFileSync(path.join(out,'validation.json')));
 assert.equal(v.status,'passed');assert.ok(v.checks.every(c=>c.nonWallPixelsChanged===0&&c.prior89Unchanged&&c.convexSideTaperChecked));
 for(const map of m.maps){assert.equal(sha(path.join(root,map.sourceMap)),map.sourceMapSha256);const src=path.join(root,'preview/city-concrete89',map.images.concrete89);assert.equal(sha(path.join(out,map.images.concrete89)),sha(src));const atlas=map.seed===802302584?'wall-audit85':'city-random82';assert.equal(sha(path.join(root,`preview/${atlas}/assets/wall.png`)),map.auditedWallAtlasSha256)}
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:980}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/city-concrete90/?cx=33&cy=39&zoom=2`);await page.waitForFunction(()=>window.ready);
  assert.equal(await page.evaluate(()=>window.cityConcrete90.getView().style),'concrete90');
  for(let sample=0;sample<2;sample++){
   if(sample){await page.locator('#sample').selectOption('1');await page.waitForFunction(()=>window.ready);await page.locator('#corner').click()}
   const position=await page.evaluate(()=>window.cityConcrete90.getView().center);
   for(const style of m.styles){await page.locator(`[data-style="${style.id}"]`).click();assert.deepEqual(await page.evaluate(()=>window.cityConcrete90.getView().center),position)}
   await page.locator('[data-style="concrete90"]').click();await page.screenshot({path:path.join(out,`detail-${sample+1}.png`),fullPage:true});
   await page.locator('[data-mode="actual"]').click();assert.equal(await page.evaluate(()=>window.cityConcrete90.getView().scale),1);
   await page.locator('[data-mode="fit"]').click();assert.equal(await page.evaluate(()=>window.cityConcrete90.getView().mode),'fit');await page.screenshot({path:path.join(out,`full-map-${sample+1}.png`),fullPage:true});
  }
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',maps:2,styles:3,zoom:true,positionPreserved:true,mobileOverflow:false,prior89AndNative84Unchanged:true,pageErrors:errors},null,2)+'\n');console.log('Verified90 corners, two maps, preserved89, material switching, zoom and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
