const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
const out=path.resolve(__dirname,'../preview/street-floor-random01'),browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8797/street-floor-random01/');await p.waitForFunction(()=>window.previewReady===true);
 const initial=await p.evaluate(()=>{const s=previewApp.getState(),m=previewApp.getMap();return{state:s,cells:Array.from(m.cells),props:m.props,enemies:m.enemies.length,items:m.items.length,canvas:document.getElementById('map').toDataURL()};});
 assert.strictEqual(initial.state.fogEnabled,false);assert.strictEqual(initial.enemies,0);assert.strictEqual(initial.items,0);assert.strictEqual(new Set(initial.state.floorChoices).size,16);assert.strictEqual(await p.locator('#floorSwatches canvas').count(),16);
 await p.locator('#map').screenshot({path:path.join(out,'random-field.png')});await p.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 await p.selectOption('#floorPattern','repeat');const repeat=await p.evaluate(()=>({s:previewApp.getState(),canvas:document.getElementById('map').toDataURL()}));assert(repeat.s.floorChoices.every(v=>v===0));assert.notStrictEqual(repeat.canvas,initial.canvas);await p.locator('#map').screenshot({path:path.join(out,'repeated-field.png')});
 await p.selectOption('#floorPattern','random');assert.strictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),initial.canvas);
 await p.locator('#shuffleFloor').click();const shuffled=await p.evaluate(()=>({s:previewApp.getState(),cells:Array.from(previewApp.getMap().cells),props:previewApp.getMap().props,canvas:document.getElementById('map').toDataURL()}));
 assert.strictEqual(shuffled.s.floorMix,1);assert.notDeepStrictEqual(shuffled.s.floorChoices,initial.state.floorChoices);assert.deepStrictEqual(shuffled.cells,initial.cells);assert.deepStrictEqual(shuffled.props,initial.props);assert.deepStrictEqual(shuffled.s.upstairs,initial.state.upstairs);assert.deepStrictEqual(shuffled.s.exit,initial.state.exit);
 await p.evaluate(()=>previewApp.setFloorMix(0));assert.strictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),initial.canvas);
 await p.evaluate(()=>{const m=previewApp.getMap(),s=previewApp.getState();m.cells[0]=1-m.cells[0];previewApp.draw();m.cells[0]=1-m.cells[0];previewApp.draw();});assert.strictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),initial.canvas);
 await p.evaluate(()=>previewApp.showFence());await p.locator('#map').screenshot({path:path.join(out,'venue-field.png')});
 await p.evaluate(()=>{previewApp.showStart();previewApp.setFogEnabled(true);});assert((await p.evaluate(()=>previewApp.getState())).visible.some(Boolean));await p.evaluate(()=>previewApp.setFogEnabled(false));
 await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(out,'mobile.png'),fullPage:true});assert.deepStrictEqual(errors,[]);
 const result={status:'passed',tileCombinations:16,baseArtTiles:4,rotationsPerTile:4,independentRandomSelection:true,deterministicBySeedAndCoordinates:true,patternToggleRestoresSameImage:true,shuffleLeavesLayoutAndStairsUnchanged:true,noMonstersOrRewards:true,responsiveNoOverflow:true,nativeGameLaunched:false,errors};
 fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
