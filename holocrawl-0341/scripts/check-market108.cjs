const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-market108'),base=path.resolve(out,'../city-market02');
const oldG=require(path.join(base,'market-generator.js')),newG=require(path.join(out,'market-generator.js'));
const sources=JSON.parse(fs.readFileSync(path.join(out,'inputs.json')));
for(const [name,sha]of Object.entries(sources.oldFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(base,name))).digest('hex'),sha);
for(const floor of [4,5,6,7])for(let i=0;i<20;i++){const a=oldG.generate('MARKET108-'+i,floor,'floor'),b=newG.generate('MARKET108-'+i,floor,'floor');assert.deepEqual(b,a);assert.ok(b.validation.ok);assert.equal(b.enemies.length+b.items.length,0);}
(async()=>{
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
  await p.goto(`${previewURL}/city-market108/#acrylic`);await p.waitForFunction(()=>window.previewReady);
  // Rendering-only comparison must not alter geometry, member choices or turns.
  const before=await p.evaluate(()=>({map:JSON.stringify(previewApp.getMap()),state:previewApp.getState(),pixels:document.getElementById('map').toDataURL()}));
  await p.locator('#compareOld').check();const old=await p.evaluate(()=>({map:JSON.stringify(previewApp.getMap()),state:previewApp.getState(),pixels:document.getElementById('map').toDataURL()}));
  assert.equal(old.map,before.map);assert.deepEqual(old.state,before.state);assert.notEqual(old.pixels,before.pixels);
  await p.locator('#map').screenshot({path:path.join(out,'before02.png')});await p.locator('#compareOld').uncheck();
  assert.equal(await p.evaluate(()=>document.getElementById('map').toDataURL()),before.pixels);
  await p.locator('#map').screenshot({path:path.join(out,'after108.png')});
  // Check alpha preservation and member art/representative colours directly.
  const palette=await p.evaluate(()=>{
   const changes=[];for(const meta of MerchCatalog){const a=document.createElement('canvas');a.width=images[meta.id].width;a.height=images[meta.id].height;const c=a.getContext('2d',{willReadFrequently:true});c.drawImage(images[meta.id],0,0);const orig=c.getImageData(0,0,a.width,a.height).data,n=Market108.images[meta.id].getContext('2d').getImageData(0,0,a.width,a.height).data;let rgb=0,alpha=0;for(let i=0;i<n.length;i+=4){if(orig[i+3]!==n[i+3])alpha++;if(orig[i]!==n[i]||orig[i+1]!==n[i+1]||orig[i+2]!==n[i+2])rgb++;}changes.push({id:meta.id,changed:rgb,alphaChanges:alpha});}return changes;});
  assert.equal(palette.length,20);assert.ok(palette.every(p=>p.changed>0&&p.alphaChanges===0));
  for(const floor of [4,5,6,7]){await p.locator(`[data-floor="${floor}"]`).click();await p.locator('#marketView').click();assert.ok((await p.evaluate(()=>previewApp.getState())).validation.ok);await p.locator('#map').screenshot({path:path.join(out,`floor${floor}.png`)});}
  await p.locator('[data-floor="4"]').click();await p.locator('#acrylicView').click();await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await p.locator('#fog').click();await p.locator('#map').screenshot({path:path.join(out,'fog.png')});await p.locator('#fog').click();
  await p.locator('#exitMode').selectOption('wall');await p.locator('#map').screenshot({path:path.join(out,'door101.png')});
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.setViewportSize({width:1440,height:1100});await p.goto(`${previewURL}/city-market108/catalog.html`);await p.waitForFunction(()=>window.catalogReady);
  assert.equal(await p.locator('#propSwatches figure').count(),20);assert.equal(await p.locator('#memberGrid .member').count(),84);await p.locator('#propSwatches').screenshot({path:path.join(out,'props20.png')});
  await p.goto(`${previewURL}/city-market108/buildings.html`);await p.waitForFunction(()=>window.buildings108Ready);await p.locator('#street').screenshot({path:path.join(out,'storefronts108.png')});await p.screenshot({path:path.join(out,'buildings-overview.png'),fullPage:true});
  await p.locator('#before').check();await p.locator('#street').screenshot({path:path.join(out,'storefronts-before27.png')});assert.deepEqual(errors,[]);
  const result={status:'passed',revision:108,unchangedGeometryMaps:80,originalInputsPreserved:true,normalWall:92,basicDoor:101,fixturePalette:palette,membersUnchanged:84,comparisonPreservesMapAndStock:true,responsiveOverflow:false,nativeIntegrated:false,errors};
  fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:'passed',maps:80,props:20,members:84}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
