const fs=require('fs'),path=require('path'),assert=require('assert'),G=require('../preview/city-layout06/market-generator.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const out=path.resolve(__dirname,'../preview/city-layout06');const totals={rooms:0,balanced:0,connected:0},shares={rooms:0,balanced:0,connected:0};
for(let i=0;i<60;i++)for(const kind of ['rooms','balanced','connected']){
 const map=G.generate('MIDDLE-CHECK-'+i,4+i%4,'floor',kind);assert(map.validation.ok);assert.strictEqual(map.layoutKey,kind);totals[kind]+=map.flowMetrics.singleFileCells;shares[kind]+=map.flowMetrics.wideCoreConnectedFraction;
 if(kind==='balanced'){for(const p of map.reservedRoute)for(let y=p.y-1;y<=p.y+1;y++)for(let x=p.x-1;x<=p.x+1;x++)assert.strictEqual(map.cells[y*map.w+x],1);assert.strictEqual(map.cells[map.focus.y*map.w+map.focus.x],1);}
}
assert(totals.connected<totals.balanced&&totals.balanced<totals.rooms);assert(shares.rooms<shares.balanced&&shares.balanced<shares.connected);
const a=G.generate('LAYOUT-001',4,'floor','balanced'),b=G.generate('LAYOUT-001',4,'floor','balanced');assert.deepStrictEqual(a.cells,b.cells);assert.deepStrictEqual(a.marketProps,b.marketProps);
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:8797/city-layout06/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert.strictEqual(await p.locator('#examples article').count(),3);await p.locator('body').screenshot({path:path.join(out,'comparison.png')});
 await p.goto('http://127.0.0.1:8797/city-layout06/index.html?layout=balanced&seed=LAYOUT-001&view=focus');await p.waitForFunction(()=>window.previewReady);assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,'balanced');await p.locator('#map').screenshot({path:path.join(out,'balanced-field.png')});await p.evaluate(()=>previewApp.setOverview(true));await p.locator('#map').screenshot({path:path.join(out,'balanced-overview.png')});
 await p.locator('#wideRoute').click();await p.locator('#map').screenshot({path:path.join(out,'balanced-route.png')});
 for(const kind of ['rooms','connected','balanced']){await p.selectOption('#layoutMode',kind);assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,kind);}
 const steps=await p.evaluate(()=>{previewApp.showStart();const m=previewApp.getMap();let n=0;for(let i=1;i<Math.min(50,m.path.length);i++){if(!previewApp.move(m.path[i].x-m.path[i-1].x,m.path[i].y-m.path[i-1].y))throw Error('Route not walkable');n++;}return n;});assert.strictEqual(steps,49);
 await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.goto('http://127.0.0.1:8797/city-layout06/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',casesPerLayout:60,totalMapCases:180,connectedAndReachable:true,balancedMainRouteWidth3Preserved:true,meanSingleFileCells:Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,v/60])),meanWideCoreConnectedFraction:Object.fromEntries(Object.entries(shares).map(([k,v])=>[k,v/60])),balancedMetricsBetweenEndpoints:true,deterministicBySeed:true,walkedRouteSteps:steps,responsiveNoOverflow:true,nativeGameLaunched:false,errors};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
