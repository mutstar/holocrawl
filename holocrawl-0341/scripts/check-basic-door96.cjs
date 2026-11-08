const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath,headless:true});
 try{const page=await browser.newPage({viewport:{width:1200,height:950}}),errors=[];page.on('pageerror',e=>errors.push(e.message));const checks=[];
  for(const folder of ['basic-door96','holox-door97']){
   await page.setViewportSize({width:1200,height:950});await page.goto(`${previewURL}/${folder}/`);await page.waitForFunction(()=>window.ready);
   const m=await page.evaluate(()=>window.doorReview96.manifest);
   for(let i=0;i<m.scenes.length;i++){
    await page.locator(`[data-scene="${i}"]`).click();
    for(const s of m.styles){await page.locator(`[data-style="${s.id}"]`).click();await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
     for(const state of ['closed','open'])assert.ok((await page.locator(`[data-state="${state}"]`).getAttribute('src')).endsWith(m.scenes[i].images[s.id][state]));
    }
   }
   await page.locator(`[data-scene="0"]`).click();await page.locator(`[data-style="${m.styles[0].id}"]`).click();
   for(const zoom of [1,2,3]){await page.locator(`[data-zoom="${zoom}"]`).click();assert.equal(await page.locator('[data-state="closed"]').evaluate(i=>i.getBoundingClientRect().width),m.scenes[0].width*zoom)}
   await page.locator(`[data-zoom="${m.defaultZoom}"]`).click();await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
   await page.screenshot({path:path.join(root,`preview/${folder}/overview.png`),fullPage:true});
   await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   if(folder==='holox-door97'){assert.equal(m.scenes.length,2);assert.ok(m.scenes.every(s=>s.images.new.closed.startsWith('holox-')))}
   checks.push({page:folder,scenes:m.scenes.length,styles:m.styles.length,statesLoaded:true,zoom123:true,mobileOverflow:false});
  }
  assert.deepEqual(errors,[]);const result={status:'passed',checks,pageErrors:errors};for(const folder of ['basic-door96','holox-door97'])fs.writeFileSync(path.join(root,`preview/${folder}/browser-validation.json`),JSON.stringify(result,null,2)+'\n');console.log('Verified new normal door and isolated holoX review: orientations, states, old/new, zoom and mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
