const fs=require('fs'),path=require('path'),assert=require('assert');
const G=require('../preview/city-market01/market-generator.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/city-market01'),stats=[];
 for(const floor of [4,5,6,7]){let shops=0,boxes=0,racks=0;for(let i=0;i<30;i++){
   const map=G.generate('MARKET-CHECK-'+i,floor,'floor');assert(map.validation.ok);assert(map.path.length>0);assert.strictEqual(map.enemies.length,0);assert.strictEqual(map.items.length,0);
   for(const p of map.marketProps)assert.strictEqual(map.cells[p.y*map.w+p.x],2);
   for(const p of map.marketWalls){assert.strictEqual(map.cells[p.y*map.w+p.x],0);assert.strictEqual(map.cells[p.y*map.w+p.x+1],0);}
   shops+=map.marketWalls.length;boxes+=map.marketProps.filter(p=>p.type==='boxes').length;racks+=map.marketProps.filter(p=>p.type==='rack').length;
 }stats.push({floor,maps:30,meanShops:shops/30,meanBoxes:boxes/30,meanRacks:racks/30});}
 assert(stats[2].meanBoxes>stats[0].meanBoxes);assert(stats[1].meanRacks>stats[2].meanRacks);
 const a=G.generate('MARKET-CHECK-0',4),b=G.generate('MARKET-CHECK-0',4);assert.deepStrictEqual(a.cells,b.cells);assert.deepStrictEqual(a.marketProps,b.marketProps);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8797/city-market01/');await p.waitForFunction(()=>window.previewReady===true);
 for(const floor of [4,5,6,7]){
   await p.locator(`[data-floor="${floor}"]`).click();await p.locator('#marketView').click();
   const state=await p.evaluate(()=>previewApp.getState());assert.strictEqual(state.marketFloor,floor);assert(state.marketWalls.length>0);assert(state.validation.ok);
   await p.locator('#map').screenshot({path:path.join(out,`floor${floor}-field.png`)});
   await p.evaluate(()=>previewApp.setOverview(true));await p.locator('#map').screenshot({path:path.join(out,`floor${floor}-overview.png`)});await p.evaluate(()=>previewApp.setOverview(false));
 }
 await p.locator('[data-floor="4"]').click();await p.locator('#marketView').click();await p.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 const before=await p.evaluate(()=>JSON.stringify({cells:Array.from(previewApp.getMap().cells),props:previewApp.getMap().marketProps}));await p.locator('#shuffleFloor').click();assert.strictEqual(await p.evaluate(()=>JSON.stringify({cells:Array.from(previewApp.getMap().cells),props:previewApp.getMap().marketProps})),before);
 await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(out,'mobile.png'),fullPage:true});assert.deepStrictEqual(errors,[]);
 const result={status:'passed',mapCases:120,connectedWithSolidProps:true,deterministicSeed:true,floorProfiles:stats,nativeGameLaunched:false,noMonstersOrRewards:true,floorShufflePreservesLayout:true,responsiveNoOverflow:true,errors};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
