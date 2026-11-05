const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const dir=path.resolve(__dirname,'../preview/native-layout08'),source=JSON.parse(fs.readFileSync(path.join(dir,'native-maps.json'),'utf8'));
 assert.strictEqual(source.version,'0.34.1');assert.strictEqual(source.nativeBinarySha256,'df553d04a4c89f7b1043d1e17a68f3a26559a3bed7832be6769d58b40a559102');assert.strictEqual(source.maps.length,6);
 for(const m of source.maps){assert.strictEqual(m.w,80);assert.strictEqual(m.h,70);assert.strictEqual(m.rows.length,70);assert(m.rows.every(r=>r.length===80&&r.every(v=>v>=0&&v<m.palette.length)));assert(m.palette.some(f=>f.startsWith('stone_stairs_up')));assert(m.palette.some(f=>f.startsWith('stone_stairs_down')));}
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],bad=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push([r.status(),r.url()]);});
  await p.goto('http://127.0.0.1:8797/native-layout08/');await p.waitForFunction(()=>window.nativePreviewReady);assert.strictEqual(await p.locator('.map-card').count(),6);await p.locator('header').evaluate(e=>e.id='heading');
  await p.screenshot({path:path.join(dir,'comparison.png'),fullPage:true});
  await p.locator('#gallery').screenshot({path:path.join(dir,'native-gallery.png')});
  await p.locator('#field').screenshot({path:path.join(dir,'native-city-field.png')});
  for(let i=0;i<6;i++){
   await p.locator('.map-card').nth(i).click();const m=await p.evaluate(()=>nativePreview.getState().map);assert.deepStrictEqual(m.rows,source.maps[i].rows);assert.strictEqual(m.layout,source.maps[i].layout);
   await p.evaluate(()=>nativePreview.setOverview(true));await p.locator('#field').screenshot({path:path.join(dir,`city-overview-${i+1}.png`)});
  }
  await p.evaluate(()=>nativePreview.select(1));await p.locator('#stairs').click();await p.locator('#field').screenshot({path:path.join(dir,'native-stairs-field.png')});await p.evaluate(()=>nativePreview.setOverview(true));await p.locator('#field').click({position:{x:480,y:280}});assert.strictEqual((await p.evaluate(()=>nativePreview.getState())).overview,false);
  const initial=await p.evaluate(()=>JSON.stringify(nativePreview.getState().map.rows));await p.locator('#skin').click();await p.locator('#skin').click();assert.strictEqual(await p.evaluate(()=>JSON.stringify(nativePreview.getState().map.rows)),initial);
  await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);assert.deepStrictEqual(bad,[]);
  const result={status:'passed',nativeVersion:source.version,maps:6,terrainCells:33600,browserRowsMatchNativeExport:true,allSixMapsRender:true,modeSwitchAndClickZoom:true,mobileNoOverflow:true,pageErrors:errors,failedAssets:bad,nativeGameWindowOpened:false,headlessNativeBuilderUsed:true};fs.writeFileSync(path.join(dir,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
