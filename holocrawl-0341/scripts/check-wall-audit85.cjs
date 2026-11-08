const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),output=path.join(root,'preview/wall-audit85');
(async()=>{
 const m=JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8'));
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1050}}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`${previewURL}/wall-audit85/`);await page.waitForFunction(()=>window.ready);
  assert.equal(await page.locator('#sample option').count(),128);
  assert.equal(await page.evaluate(()=>window.wallMapReview82.map.seed),m.maps[0].seed);
  for(const index of [1,63,127]){
   await page.locator('#sample').selectOption(String(index));
   await page.waitForFunction(seed=>window.ready&&window.wallMapReview82.map.seed===seed,m.maps[index].seed);
   assert.deepEqual(await page.evaluate(()=>window.wallMapReview82.map),JSON.parse(fs.readFileSync(path.join(output,m.maps[index].file),'utf8')));
  }
  await page.locator('#actual').click();assert.equal(await page.evaluate(()=>window.wallMapReview82.getView().scale),1);
  await page.locator('#double').click();assert.equal(await page.evaluate(()=>window.wallMapReview82.getView().scale),2);
  await page.locator('#fit').click();
  await page.locator('#sample').selectOption('0');await page.waitForFunction(seed=>window.ready&&window.wallMapReview82.map.seed===seed,m.maps[0].seed);
  await page.screenshot({path:path.join(output,'overview.png')});
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify({status:'passed',mapOptions:128,samplesChecked:[0,1,63,127],nativeSnapshotsMatch:true,zoom1and2:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log('Verified 128-map selector, native samples, zoom and mobile layout.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
