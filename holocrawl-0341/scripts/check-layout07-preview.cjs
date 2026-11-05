const fs=require('fs'),path=require('path'),assert=require('assert');
const G=require('../preview/city-layout07/market-generator.js'),old=require('../preview/city-layout06/market-generator.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/city-layout07'),totals={},shares={};let overlap=0;
 for(let i=0;i<60;i++){
  const maps={};
  for(const kind of ['rooms','balanced','connected']){
   const m=maps[kind]=G.generate('QUARTER-CHECK-'+i,4+i%4,'floor',kind);
   assert(m.validation.ok);assert.strictEqual(m.layoutKey,kind);assert.strictEqual(m.enemies.length+m.items.length,0);
   totals[kind]=(totals[kind]||0)+m.flowMetrics.singleFileCells;shares[kind]=(shares[kind]||0)+m.flowMetrics.wideCoreConnectedFraction;
   if(kind==='balanced'){
    assert(m.quarterCount>=3&&m.quarterCount<=4);assert(m.annexCount>=9&&m.annexCount<=14);
    assert(m.reservedRoute.length>24);assert.strictEqual(m.cells[m.focus.y*m.w+m.focus.x],1);
    for(const p of m.reservedRoute)for(let y=p.y-1;y<=p.y+1;y++)for(let x=p.x-1;x<=p.x+1;x++)assert.strictEqual(m.cells[y*m.w+x],1,'Reserved route narrowed after props');
   }else if(i<5)assert.deepStrictEqual(m.cells,old.generate('QUARTER-CHECK-'+i,4+i%4,'floor',kind).cells,'Endpoint changed');
  }
  let same=0,union=0;for(let n=0;n<maps.rooms.cells.length;n++){const a=maps.rooms.cells[n]!==0,b=maps.balanced.cells[n]!==0;if(a&&b)same++;if(a||b)union++;}overlap+=same/union;
 }
 assert(overlap/60<.75,'New mixed map still reuses original footprint');assert(totals.balanced<totals.rooms);
 const a=G.generate('LAYOUT-001',4,'floor','balanced'),b=G.generate('LAYOUT-001',4,'floor','balanced');assert.deepStrictEqual(a.cells,b.cells);assert.deepStrictEqual(a.marketProps,b.marketProps);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto('http://127.0.0.1:8797/city-layout07/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert.strictEqual(await p.locator('#examples article').count(),3);await p.locator('body').screenshot({path:path.join(out,'comparison.png')});
  await p.goto('http://127.0.0.1:8797/city-layout07/index.html?layout=balanced&seed=LAYOUT-001&view=focus');await p.waitForFunction(()=>window.previewReady);assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,'balanced');await p.locator('#map').screenshot({path:path.join(out,'balanced-field.png')});await p.evaluate(()=>previewApp.setOverview(true));await p.locator('#map').screenshot({path:path.join(out,'balanced-overview.png')});
  const plain=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#wideRoute').click();assert.notStrictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),plain);await p.locator('#map').screenshot({path:path.join(out,'balanced-route.png')});
  for(const kind of ['rooms','connected','balanced']){await p.selectOption('#layoutMode',kind);assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,kind);}
  const steps=await p.evaluate(()=>{previewApp.showStart();const m=previewApp.getMap();let n=0;for(let i=1;i<Math.min(50,m.path.length);i++){if(!previewApp.move(m.path[i].x-m.path[i-1].x,m.path[i].y-m.path[i-1].y))throw Error('Route not walkable');n++;}return n;});assert.strictEqual(steps,49);
  await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.goto('http://127.0.0.1:8797/city-layout07/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
  const result={status:'passed',casesPerLayout:60,totalMapCases:180,connectedAndReachable:true,independentMiddleGenerator:true,meanFloorJaccardWithA:overlap/60,originalEndpointsPreserved:true,balancedMainRouteWidth3Preserved:true,meanSingleFileCells:Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,v/60])),meanWideCoreConnectedFraction:Object.fromEntries(Object.entries(shares).map(([k,v])=>[k,v/60])),deterministicBySeed:true,walkedRouteSteps:steps,responsiveNoOverflow:true,nativeGameLaunched:false,errors};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
