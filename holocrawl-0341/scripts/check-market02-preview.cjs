const fs=require('fs'),path=require('path'),assert=require('assert');
const G=require('../preview/city-market02/market-generator.js'),S=require('../preview/city-market02/market-stock.js');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/city-market02'),types=new Set(),memberIds=new Set();
 assert.strictEqual(S.catalog.length,20);assert.strictEqual(S.members.length,84);assert.strictEqual(S.catalog.filter(p=>p.kind==='wall').length,5);assert.strictEqual(new Set(S.members.map(m=>m.id)).size,84);
 for(const m of S.members){assert(fs.existsSync(path.join(out,m.image)));assert(/^#[0-9a-f]{6}$/i.test(m.color));}
 for(const floor of [4,5,6,7])for(let i=0;i<30;i++){
   const map=G.generate('MARKET02-CHECK-'+i,floor,'floor');assert(map.validation.ok&&map.path.length>0);assert.strictEqual(map.enemies.length+map.items.length,0);
   for(const p of [...map.marketWalls,...map.marketProps]){types.add(p.type);const ids=S.select(map.seed,floor,p);assert.strictEqual(ids.length,3);assert.strictEqual(new Set(ids).size,3);ids.forEach(id=>memberIds.add(id));assert.deepStrictEqual(ids,S.select(map.seed,floor,p));}
 }
 assert.strictEqual(types.size,20);assert.strictEqual(memberIds.size,84);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8797/city-market02/#acrylic');await p.waitForFunction(()=>window.previewReady===true);
 const initial=await p.evaluate(()=>({s:previewApp.getState(),cells:Array.from(previewApp.getMap().cells),canvas:document.getElementById('map').toDataURL()}));
 await p.locator('#map').screenshot({path:path.join(out,'acrylic-field.png')});await p.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
 await p.locator('#shuffleStock').click();const shuffled=await p.evaluate(()=>({s:previewApp.getState(),cells:Array.from(previewApp.getMap().cells),canvas:document.getElementById('map').toDataURL()}));
 assert.deepStrictEqual(shuffled.cells,initial.cells);assert.deepStrictEqual(shuffled.s.marketWalls,initial.s.marketWalls);assert.deepStrictEqual(shuffled.s.marketProps,initial.s.marketProps);assert.notDeepStrictEqual(shuffled.s.stock,initial.s.stock);assert.notStrictEqual(shuffled.canvas,initial.canvas);
 await p.evaluate(()=>previewApp.setStockMix(0));assert.strictEqual(await p.evaluate(()=>document.getElementById('map').toDataURL()),initial.canvas);
 await p.locator('#shirtView').click();assert((await p.locator('#stockInfo').innerText()).includes('티셔츠'));await p.locator('#map').screenshot({path:path.join(out,'shirts-field.png')});
 for(const floor of [4,5,6,7]){await p.locator(`[data-floor="${floor}"]`).click();await p.locator('#marketView').click();assert((await p.evaluate(()=>previewApp.getState())).validation.ok);await p.locator('#map').screenshot({path:path.join(out,`floor${floor}-field.png`)});}
 await p.locator('[data-floor="4"]').click();await p.locator('#acrylicView').click();await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 await p.setViewportSize({width:1440,height:1100});await p.goto('http://127.0.0.1:8797/city-market02/catalog.html');await p.waitForFunction(()=>window.catalogReady===true);assert.strictEqual(await p.locator('#propSwatches figure').count(),20);assert.strictEqual(await p.locator('#memberGrid .member').count(),84);
 await p.locator('#propSwatches').screenshot({path:path.join(out,'fixture-catalog.png')});await p.locator('#memberGrid').screenshot({path:path.join(out,'member-catalog.png')});
 await p.locator('#memberFilter').fill('Suisei');assert.strictEqual(await p.locator('#memberGrid .member').count(),1);await p.locator('#memberFilter').fill('');
 assert.deepStrictEqual(errors,[]);
 const result={status:'passed',fixtureTypes:20,wallFacades:5,floorProps:15,members:84,mapCases:120,allFixtureTypesPlaced:true,allMembersReachableFromRandomPool:true,threeDistinctMembersPerDisplay:true,deterministicStock:true,stockShufflePreservesMapAndFixtures:true,shirtColorsAvailableForAllMembers:true,memberSearchWorks:true,responsiveNoOverflow:true,nativeGameLaunched:false,errors};
 fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
