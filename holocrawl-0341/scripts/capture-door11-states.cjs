const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/native-door11'),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1150}}),errors=[],bad=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)bad.push(r.url());});
  await p.goto('http://127.0.0.1:8797/native-door11/');await p.waitForFunction(()=>window.doorPreviewReady);await p.evaluate(()=>doorPreview.setDoorMode('fit'));
  const original=await p.evaluate(()=>JSON.stringify(doorPreview.getState().map.rows)),closed=await p.evaluate(()=>({horizontal:document.getElementById('fithorizontal').toDataURL(),vertical:document.getElementById('fitvertical').toDataURL()}));
  for(const axis of ['horizontal','vertical'])await p.locator('#fit'+axis).screenshot({path:path.join(out,axis+'-closed-state.png')});
  const views=[];
  for(const axis of ['horizontal','vertical']){
   await p.evaluate(axis=>{doorPreview.focusAxis(axis);doorPreview.toggleFocused();},axis);const state=await p.evaluate(()=>doorPreview.getState());assert.strictEqual(state.doorAxis,axis);assert.notStrictEqual(await p.evaluate(axis=>document.getElementById('fit'+axis).toDataURL(),axis),closed[axis]);assert.strictEqual(await p.evaluate(()=>JSON.stringify(doorPreview.getState().map.rows)),original);
   await p.locator('#fit'+axis).screenshot({path:path.join(out,axis+'-open-state.png')});await p.locator('#field').screenshot({path:path.join(out,axis+'-open-field.png')});views.push({axis,width:state.doorDisplayWidth,height:state.doorDisplayHeight,position:state.center});
  }
  await p.goto('http://127.0.0.1:8797/native-door11/states.html');await p.locator('img').last().waitFor();await p.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth===320));await p.locator('#allStates').screenshot({path:path.join(out,'all-open-closed-states.png')});await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);assert.deepStrictEqual(bad,[]);
  const result={status:'passed',views,openedBothOrientations:true,closedAndOpenVisuallyDifferent:true,nativeTerrainUnchanged:true,newRasterArtCreated:false,errors,bad,mobileNoOverflow:true};fs.writeFileSync(path.join(out,'states-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
