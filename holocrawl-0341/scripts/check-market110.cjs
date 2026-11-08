const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),out=path.resolve(__dirname,'../preview/city-market110');
const inputs=JSON.parse(fs.readFileSync(path.join(out,'inputs.json')));
for(const [n,sha]of Object.entries(inputs.sourceFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'../city-market109',n))).digest('hex'),sha);
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`${previewURL}/city-market110/#acrylic`);await p.waitForFunction(()=>window.previewReady);
 const geometry=await p.evaluate(()=>JSON.stringify(previewApp.getMap()));
 await p.locator('#noWear').check();const clean=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#map').screenshot({path:path.join(out,'before108.png')});
 await p.locator('#noWear').uncheck();const levels=[];
 for(const level of [4,5,6,7]){
  await p.locator('#wearLevel').selectOption(String(level));
  const result=await p.evaluate(()=>{const s=Wear110.getStats(),c=Wear110.getLayer(),a=c.getContext('2d').getImageData(0,0,c.width,c.height).data,m=previewApp.getMap();let floorPixels=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(a[(y*c.width+x)*4+3]&&m.cells[Math.floor(y/32)*m.w+Math.floor(x/32)]!==0)floorPixels++;return {...s,floorPixels};});
  console.log(JSON.stringify(result));assert.equal(result.floorPixels,0);assert.ok(result.paintedPixels>0);assert.ok(Object.values(result.styles).every(n=>n>0));assert.ok(result.orientationBins.filter(n=>n>0).length>=10);assert.ok(result.mainLengthRange[1]>result.mainLengthRange[0]*3);assert.equal(await p.evaluate(()=>JSON.stringify(previewApp.getMap())),geometry);
  levels.push(result);await p.locator('#map').screenshot({path:path.join(out,`wear-level${level}.png`)});
 }
 await p.locator('#patternBefore109').check();await p.locator('#map').screenshot({path:path.join(out,'before-pattern109.png')});await p.locator('#patternBefore109').uncheck();await p.locator('#map').screenshot({path:path.join(out,'after-pattern110.png')});
 assert.ok(levels.every((s,i)=>!i||s.paintedPixels>levels[i-1].paintedPixels));
 await p.locator('#wearLevel').selectOption('4');const repeat=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#wearLevel').selectOption('7');await p.locator('#wearLevel').selectOption('4');assert.equal(await p.evaluate(()=>document.getElementById('map').toDataURL()),repeat);
 await p.locator('#noWear').check();assert.equal(await p.evaluate(()=>document.getElementById('map').toDataURL()),clean);
 const old=await browser.newPage({viewport:{width:1440,height:1100}});await old.goto(`${previewURL}/city-market108/#acrylic`);await old.waitForFunction(()=>window.previewReady);assert.equal(await old.evaluate(()=>document.getElementById('map').toDataURL()),clean);await old.close();
 await p.locator('#noWear').uncheck();await p.locator('#wearLevel').selectOption('auto');
 for(const f of [4,5,6,7]){await p.locator(`[data-floor="${f}"]`).click();await p.locator('#acrylicView').click();assert.equal(await p.evaluate(()=>Wear110.getStats().floor),f);assert.ok(await p.evaluate(()=>previewApp.getState().validation.ok));await p.locator('#map').screenshot({path:path.join(out,`floor${f}.png`)});}
 await p.locator('[data-floor="7"]').click();await p.locator('#acrylicView').click();await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({status:'passed',revision:110,source109Preserved:true,cleanModePixelIdenticalTo108:true,geometryUnchanged:true,floorPixelsChanged:0,levels,deterministic:true,floorsTested:[4,5,6,7],pageErrors:errors,mobileOverflow:false,nativeIntegrated:false},null,2)+'\n');console.log(JSON.stringify({status:'passed',levels}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
