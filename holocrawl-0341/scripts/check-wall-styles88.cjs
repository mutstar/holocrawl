const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'preview/wall-styles88');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.equal(v.ownBaselineMatchesRelief87,true);assert.equal(v.checks.length,4);
 assert.ok(v.checks.every(c=>c.nonWallPixelsChanged===0&&c.alphaUnchanged));
 assert.equal(sha(path.join(root,'preview/wall-audit85/assets/wall.png')),v.auditedWallAtlasSha256);
 assert.equal(sha(path.join(root,'preview/wall-audit85/maps/map-802302584-1.json')),v.sourceMapSha256);
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/wall-styles88/`);
  const loaded=()=>page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));await loaded();
  assert.equal(await page.locator('.card').count(),4);
  await page.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  const tested=[];
  for(const view of Object.keys(manifest.views)){
   await page.locator(`[data-view="${view}"]`).click();await loaded();
   const widths=await page.locator('img[data-style]').evaluateAll(imgs=>imgs.map(i=>i.naturalWidth));assert.ok(widths.every(w=>w===manifest.views[view].width));
   for(const zoom of [2,1]){
    await page.locator(`[data-zoom="${zoom}"]`).click();
    const sizes=await page.locator('img[data-style]').evaluateAll(imgs=>imgs.map(i=>i.getBoundingClientRect().width));assert.ok(sizes.every(w=>w===widths[0]*zoom));
   }
   tested.push(view);
  }
  await page.locator('[data-view="scene"]').click();await loaded();
  await page.locator('.view').first().evaluate(v=>{v.scrollLeft=120;v.scrollTop=20;v.dispatchEvent(new Event('scroll'))});
  await page.waitForFunction(()=>[...document.querySelectorAll('.view')].every(v=>v.scrollLeft===120&&v.scrollTop===20));
  await page.locator('[data-view="shapes"]').click();await loaded();await page.screenshot({path:path.join(out,'shapes-overview.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'passed',views:tested,styles:4,allImagesLoaded:true,zoom1and2:true,synchronizedScrolling:true,mobileOverflow:false,auditedInputsUnchanged:true,pageErrors:errors},null,2)+'\n');
  console.log('Passed four styles, four views, zoom, synchronized scrolling, mobile and immutable audited inputs.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
