const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const output=path.resolve(__dirname,'../preview/city-random82');
(async()=>{
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1050}}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`${previewURL}/city-random82/`);await page.waitForFunction(()=>window.ready);
  const native=JSON.parse(fs.readFileSync(path.join(output,'map.json'),'utf8'));
  assert.deepEqual(await page.evaluate(()=>window.wallMapReview82.map),native);
  assert.equal(native.facility,null);assert.equal(native.depth,1);
  const image=await page.evaluate(()=>window.wallMapReview82.fullImage());
  fs.writeFileSync(path.join(output,'full-map.png'),Buffer.from(image.split(',')[1],'base64'));
  await page.locator('#actual').click();assert.equal(await page.evaluate(()=>window.wallMapReview82.getView().scale),1);
  await page.locator('#double').click();assert.equal(await page.evaluate(()=>window.wallMapReview82.getView().scale),2);
  await page.locator('#fit').click();
  await page.screenshot({path:path.join(output,'overview.png'),fullPage:true});
  if(JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8')).wallArtRevision>=84){
   await page.goto(`${previewURL}/city-random82/?cx=46&cy=25&zoom=2`);await page.waitForFunction(()=>window.ready);
   assert.equal(await page.evaluate(()=>window.wallMapReview82.getView().scale),2);
   await page.screenshot({path:path.join(output,'corner-focus84.png'),fullPage:true});
  }
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify({status:'passed',seed:native.seed,nativeSnapshotMatches:true,facility:false,fullMapPixels:[native.width*32,native.height*32],zoom1and2:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log(`Verified native random floor ${native.seed}; full map, both zoom levels and mobile layout.`);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
