const fs=require('fs'),path=require('path'),assert=require('assert'),G=require('../preview/city-layout05/market-generator.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const out=path.resolve(__dirname,'../preview/city-layout05');let oldNarrow=0,newNarrow=0,coreShare=0,minShare=1;
for(let i=0;i<80;i++){
 const seed='FLOW-CHECK-'+i,floor=4+i%4,m=G.generate(seed,floor,'floor','connected'),old=G.generate(seed,floor,'floor','rooms');assert(m.validation.ok);assert.strictEqual(m.layoutKey,'connected');assert(m.reservedRoute.length>24);assert.strictEqual(m.enemies.length+m.items.length,0);
 for(const p of m.reservedRoute)for(let y=p.y-1;y<=p.y+1;y++)for(let x=p.x-1;x<=p.x+1;x++)assert.strictEqual(m.cells[y*m.w+x],1,'Prop narrowed a reserved3-wide route');
 assert(m.flowMetrics.wideCoreConnectedFraction>=.92);assert.strictEqual(m.cells[m.focus.y*m.w+m.focus.x],1);
 oldNarrow+=old.flowMetrics.singleFileCells;newNarrow+=m.flowMetrics.singleFileCells;coreShare+=m.flowMetrics.wideCoreConnectedFraction;minShare=Math.min(minShare,m.flowMetrics.wideCoreConnectedFraction);
}
assert(newNarrow<oldNarrow*.5);
const repeatA=G.generate('LAYOUT-001',4,'floor','connected'),repeatB=G.generate('LAYOUT-001',4,'floor','connected');assert.deepStrictEqual(repeatA.cells,repeatB.cells);assert.deepStrictEqual(repeatA.marketProps,repeatB.marketProps);
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8797/city-layout05/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert.strictEqual(await p.locator('#examples article').count(),2);await p.locator('body').screenshot({path:path.join(out,'comparison.png')});
 for(const kind of ['rooms','connected']){
   await p.goto('http://127.0.0.1:8797/city-layout05/index.html?layout='+kind+'&seed=LAYOUT-001&view=focus');await p.waitForFunction(()=>window.previewReady);assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,kind);
   await p.locator('#map').screenshot({path:path.join(out,kind+'-field.png')});await p.evaluate(()=>previewApp.setOverview(true));await p.locator('#map').screenshot({path:path.join(out,kind+'-overview.png')});
 }
 const normal=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#wideRoute').click();const marked=await p.evaluate(()=>document.getElementById('map').toDataURL());assert.notStrictEqual(normal,marked);await p.locator('#map').screenshot({path:path.join(out,'wide-route-overview.png')});await p.locator('#wideRoute').click();assert.strictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),normal);
 await p.selectOption('#layoutMode','rooms');assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,'rooms');await p.selectOption('#layoutMode','connected');assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,'connected');
 const start=await p.evaluate(()=>{previewApp.showStart();const m=previewApp.getMap();let steps=0;for(let i=1;i<Math.min(m.path.length,50);i++){if(!previewApp.move(m.path[i].x-m.path[i-1].x,m.path[i].y-m.path[i-1].y))throw Error('Movement failed on generated route');steps++;}return steps;});assert.strictEqual(start,49);
 await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.goto('http://127.0.0.1:8797/city-layout05/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',newMapsChecked:80,oldComparisonMapsChecked:80,allFloorsAndStairsConnected:true,reservedStairRoute3WideAfterProps:true,minimumWideCoreConnectedFraction:minShare,meanWideCoreConnectedFraction:coreShare/80,oldMeanSingleFileCells:oldNarrow/80,newMeanSingleFileCells:newNarrow/80,singleFileCellsReducedMoreThanHalf:true,deterministicBySeed:true,walkedRouteSteps:start,wideRouteOverlayWorks:true,responsiveNoOverflow:true,nativeGameLaunched:false,errors};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
