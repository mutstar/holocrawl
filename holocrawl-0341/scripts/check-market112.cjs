const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),out=path.resolve(__dirname,'../preview/city-market112');
const inputs=JSON.parse(fs.readFileSync(path.join(out,'inputs.json')));for(const[n,h]of Object.entries(inputs.sourceFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'../city-market110',n))).digest('hex'),h);
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`${previewURL}/city-market112/#acrylic`);await p.waitForFunction(()=>window.previewReady);
 const map=await p.evaluate(()=>JSON.stringify(previewApp.getMap()));
 await p.locator('#beforeScene112').check();const before=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#map').screenshot({path:path.join(out,'before110.png')});
 const other=await browser.newPage({viewport:{width:1440,height:1100}});await other.goto(`${previewURL}/city-market110/#acrylic`);await other.waitForFunction(()=>window.previewReady);assert.equal(await other.evaluate(()=>document.getElementById('map').toDataURL()),before);await other.close();
 await p.locator('#beforeScene112').uncheck();assert.equal(await p.evaluate(()=>JSON.stringify(previewApp.getMap())),map);const after=await p.evaluate(()=>document.getElementById('map').toDataURL());assert.notEqual(after,before);await p.locator('#map').screenshot({path:path.join(out,'after112.png')});
 // Present one wall fixture and a nearby cardboard box in a common camera.
 const pair=await p.evaluate(()=>{const m=previewApp.getMap(),windows=m.marketWalls.filter(f=>f.type==='acrylic-window'),boxes=m.marketProps.filter(f=>f.type==='delivery-boxes'||f.type==='open-carton');let pair=null,score=Infinity;for(const a of windows)for(const b of boxes){const d=Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y));if(d<score){score=d;pair={a,b,d};}}return pair;});
 assert.ok(pair);
 await p.evaluate(pair=>{const m=previewApp.getMap(),target={x:(pair.a.x+pair.b.x)/2,y:(pair.a.y+pair.b.y)/2},free=[];for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++)if(m.cells[y*m.w+x]===1)free.push({x,y,d:Math.abs(x-target.x)+Math.abs(y-target.y)});free.sort((a,b)=>a.d-b.d);player={x:free[0].x,y:free[0].y};updateVision();draw();},pair);
 for(const [old,name]of [[true,'close-before'],[false,'close-after']]){
  await p.locator('#beforeScene112').setChecked(old);
  const data=await p.evaluate(pair=>{const c=document.getElementById('map'),t=transform;const centerX=(pair.a.x+1-t.cx)*t.t+t.ox,centerY=(pair.a.y+1.5-t.cy)*t.t+t.oy;const sx=Math.max(0,Math.min(c.width-480,Math.round(centerX-240))),sy=Math.max(0,Math.min(c.height-240,Math.round(centerY-120)));const out=document.createElement('canvas');out.width=960;out.height=480;const g=out.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(c,sx,sy,480,240,0,0,960,480);return out.toDataURL();},pair);
  fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data.split(',')[1],'base64'));
 }
 for(const f of [4,5,6,7]){await p.locator(`[data-floor="${f}"]`).click();assert.ok(await p.evaluate(()=>previewApp.getState().validation.ok));}
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({status:'passed',revision:112,source110Preserved:true,comparisonPixelIdenticalTo110:true,geometryUnchanged:true,layoutsChecked:[4,5,6,7],samplePair:pair,errors,nativeIntegrated:false},null,2)+'\n');console.log(JSON.stringify({status:'passed',pair}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
