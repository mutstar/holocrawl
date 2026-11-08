const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),output=path.join(root,'preview/wall-relief87');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(output,'validation.json'),'utf8'));
 assert.equal(v.outsideSelectionChangedPixels,0);assert.equal(v.selectedWallCells,12);assert.ok(v.baseFrontAndEastSidePreserved);
 const base=fs.readFileSync(path.join(root,'preview/wall-audit85/assets/wall.png'));
 assert.equal(crypto.createHash('sha256').update(base).digest('hex'),v.baseWallAtlasSha256);
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1240,height:950}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${previewURL}/wall-relief87/`);await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth));
  await page.locator('[data-zoom="1"]').click();assert.equal(await page.locator('.viewport img').first().evaluate(i=>i.getBoundingClientRect().width),224);
  await page.locator('[data-zoom="2"]').click();assert.equal(await page.locator('.viewport img').first().evaluate(i=>i.getBoundingClientRect().width),448);
  await page.screenshot({path:path.join(output,'overview.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify({status:'passed',bothImagesLoaded:true,zoom1and2:true,mobileOverflow:false,auditedAtlasUnchanged:true,pageErrors:errors},null,2)+'\n');
  console.log('Verified local natural stone-light proposal, zoom, unchanged audited atlas and mobile layout.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
