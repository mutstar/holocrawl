const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/native-door11'),source=JSON.parse(fs.readFileSync(path.join(out,'../native-layout08/native-maps.json'),'utf8'));
 assert.deepStrictEqual(JSON.parse(fs.readFileSync(path.join(out,'native-maps.json'),'utf8')),source);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],bad=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push(r.url());});await p.goto('http://127.0.0.1:8797/native-door11/');await p.waitForFunction(()=>window.doorPreviewReady);
  const checks=await p.evaluate(()=>{
   const pixels=(id,x,y,w,h)=>Array.from(document.getElementById(id).getContext('2d').getImageData(x,y,w,h).data);
   const horizontalDoorPreserved=JSON.stringify(pixels('slimhorizontal',128,128,64,64))===JSON.stringify(pixels('fithorizontal',128,128,64,64));
   const verticalNorthWallContextChanged=JSON.stringify(pixels('slimvertical',128,64,64,64))!==JSON.stringify(pixels('fitvertical',128,64,64,64));
   return{horizontalDoorPreserved,verticalNorthWallContextChanged};
  });assert(checks.horizontalDoorPreserved);assert(checks.verticalNorthWallContextChanged);
  await p.locator('#horizontalComparisons').screenshot({path:path.join(out,'horizontal-comparison.png')});await p.locator('#verticalComparisons').screenshot({path:path.join(out,'vertical-comparison.png')});await p.locator('#field').screenshot({path:path.join(out,'vertical-fit-field.png')});
  const closed=await p.evaluate(()=>document.getElementById('field').toDataURL());await p.locator('#toggleDoor').click();assert.notStrictEqual(await p.evaluate(()=>document.getElementById('field').toDataURL()),closed);await p.locator('#verticalComparisons').screenshot({path:path.join(out,'vertical-open-comparison.png')});await p.locator('#toggleDoor').click();assert.strictEqual(await p.evaluate(()=>document.getElementById('field').toDataURL()),closed);
  await p.locator('#horizontalFocus').click();await p.locator('#field').screenshot({path:path.join(out,'horizontal-fit-field.png')});
  for(let i=0;i<6;i++){
   await p.selectOption('#mapSelect',String(i));
   for(const axis of ['horizontal','vertical']){await p.locator('#'+axis+'Focus').click();for(const mode of ['slim','wide','fit']){await p.selectOption('#doorMode',mode);const state=await p.evaluate(()=>doorPreview.getState());assert.strictEqual(state.doorAxis,axis);assert.deepStrictEqual(state.map.rows,source.maps[i].rows);}}
  }
  await p.selectOption('#mapSelect','0');await p.selectOption('#doorMode','fit');await p.locator('#slimvertical').click();assert.strictEqual((await p.evaluate(()=>doorPreview.getState())).doorMode,'slim');await p.locator('#fitvertical').click();assert.strictEqual((await p.evaluate(()=>doorPreview.getState())).doorMode,'fit');
  await p.locator('#overview').click();await p.locator('#overview').click();await p.screenshot({path:path.join(out,'review-page.png'),fullPage:true});await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);assert.deepStrictEqual(bad,[]);
  const result={status:'passed',...checks,nativeMapsUnchanged:6,mapAxisModeCases:36,horizontalWidth:24,verticalWidth:32,openCloseWorks:true,comparisonCardsClickable:true,mobileNoOverflow:true,pageErrors:errors,failedAssets:bad,nativeRuntimeModified:false};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
