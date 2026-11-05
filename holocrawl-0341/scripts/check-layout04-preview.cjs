const fs=require('fs'),path=require('path'),assert=require('assert'),G=require('../preview/city-layout04/market-generator.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/city-layout04'),stats=[],automatic=new Set();
 for(const kind of ['plaza','rooms','alleys']){let walk=0,open=0,dead=0;for(let i=0;i<60;i++){
   const m=G.generate('LAYOUT-CHECK-'+i,4+i%4,'floor',kind);assert(m.validation.ok);assert(m.path.length>18);assert.strictEqual(m.cells[m.focus.y*m.w+m.focus.x],1);assert.strictEqual(m.enemies.length+m.items.length,0);assert.strictEqual(m.layoutKey,kind);walk+=m.validation.walkable;open+=m.metrics.openNine;dead+=m.metrics.deadEnds;
 }stats.push({layout:kind,cases:60,meanWalkable:walk/60,meanOpenNine:open/60,meanDeadEnds:dead/60});}
 for(let i=0;i<30;i++)automatic.add(G.generate('AUTO-CHECK-'+i,4,'floor','auto').layoutKey);assert.strictEqual(automatic.size,3);
 for(const kind of ['plaza','rooms','alleys']){const a=G.generate('LAYOUT-001',4,'floor',kind),b=G.generate('LAYOUT-001',4,'floor',kind);assert.deepStrictEqual(a.cells,b.cells);assert.deepStrictEqual(a.marketProps,b.marketProps);}
 assert(stats[0].meanOpenNine>stats[2].meanOpenNine);assert(stats[2].meanDeadEnds>stats[0].meanDeadEnds);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8797/city-layout04/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert.strictEqual(await p.locator('#examples article').count(),3);await p.locator('body').screenshot({path:path.join(out,'layouts-comparison.png')});
 for(const kind of ['plaza','rooms','alleys','previous']){
   await p.goto('http://127.0.0.1:8797/city-layout04/index.html?layout='+kind+'&seed=LAYOUT-001&view=focus');await p.waitForFunction(()=>window.previewReady);
   const s=await p.evaluate(()=>previewApp.getState());assert.strictEqual(s.layoutKey,kind);assert(s.validation.ok);assert(await p.evaluate(()=>previewApp.getMap().cells[previewApp.getState().player.y*80+previewApp.getState().player.x]===1));
   await p.locator('#map').screenshot({path:path.join(out,kind+'-field.png')});await p.evaluate(()=>previewApp.setOverview(true));await p.locator('#map').screenshot({path:path.join(out,kind+'-overview.png')});
 }
 await p.selectOption('#layoutMode','rooms');assert.strictEqual((await p.evaluate(()=>previewApp.getState())).layoutKey,'rooms');const before=await p.evaluate(()=>JSON.stringify({cells:Array.from(previewApp.getMap().cells),props:previewApp.getMap().marketProps}));await p.locator('#shuffleStock').click();assert.strictEqual(await p.evaluate(()=>JSON.stringify({cells:Array.from(previewApp.getMap().cells),props:previewApp.getMap().marketProps})),before);
 await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.goto('http://127.0.0.1:8797/city-layout04/layouts.html');await p.waitForFunction(()=>window.layoutExamplesReady);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',mapCases:180,autoLayoutCases:30,threeLayoutFamilies:true,connectedWalkableAndStairs:true,deterministicBySeed:true,differentGeometryMetrics:stats,allFamiliesSelectedByAuto:true,playerFocusOnWalkableTile:true,stockShufflePreservesLayout:true,noMonstersOrRewards:true,nativeGameLaunched:false,officialDCSSGeneratorExecuted:false,responsiveNoOverflow:true,errors};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
