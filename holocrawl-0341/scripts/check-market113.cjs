const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),out=path.resolve(__dirname,'../preview/city-market113');
const inputs=JSON.parse(fs.readFileSync(path.join(out,'inputs.json')));for(const[n,h]of Object.entries(inputs.sourceFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'../city-market112',n))).digest('hex'),h);
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`${previewURL}/city-market113/#acrylic`);await p.waitForFunction(()=>window.previewReady);
 const map=await p.evaluate(()=>JSON.stringify(previewApp.getMap()));
 await p.locator('#beforeFloor113').check();const before=await p.evaluate(()=>document.getElementById('map').toDataURL());await p.locator('#map').screenshot({path:path.join(out,'before112.png')});
 const other=await browser.newPage({viewport:{width:1440,height:1100}});await other.goto(`${previewURL}/city-market112/#acrylic`);await other.waitForFunction(()=>window.previewReady);assert.equal(await other.evaluate(()=>document.getElementById('map').toDataURL()),before);await other.close();
 await p.locator('#beforeFloor113').uncheck();assert.equal(await p.evaluate(()=>JSON.stringify(previewApp.getMap())),map);const after=await p.evaluate(()=>document.getElementById('map').toDataURL());assert.notEqual(after,before);await p.locator('#map').screenshot({path:path.join(out,'after113.png')});
 const scope=await p.evaluate(()=>{document.getElementById('beforeFloor113').checked=true;draw();const a=ctx.getImageData(0,0,canvas.width,canvas.height).data;document.getElementById('beforeFloor113').checked=false;draw();const b=ctx.getImageData(0,0,canvas.width,canvas.height).data;let changed=0,outside=0;for(let i=0;i<a.length;i+=4)if(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2]){changed++;const px=(i/4)%canvas.width,py=Math.floor(i/4/canvas.width),x=Math.floor((px-transform.ox)/transform.t)+transform.cx,y=Math.floor((py-transform.oy)/transform.t)+transform.cy;if(!map.marketProps.some(f=>f.x===x&&f.y===y))outside++;}return {changed,outside};});
 assert.ok(scope.changed>0);assert.equal(scope.outside,0);
 const fixtureIds=await p.evaluate(()=>MerchCatalog.filter(m=>m.kind==='floor').map(m=>{const c=Scene113.sprite({type:m.id,x:0,y:0},map,0);const a=c.getContext('2d').getImageData(0,0,32,32).data;let pixels=0;for(let i=3;i<a.length;i+=4)if(a[i])pixels++;return {id:m.id,pixels};}));assert.equal(fixtureIds.length,15);assert.ok(fixtureIds.every(m=>m.pixels>20));

 // Present one wall fixture and a nearby cardboard box in a common camera.
 const pair=await p.evaluate(()=>{const m=previewApp.getMap(),windows=m.marketWalls.filter(f=>f.type==='acrylic-window'),boxes=m.marketProps.filter(f=>f.type==='delivery-boxes'||f.type==='open-carton');let pair=null,score=Infinity;for(const a of windows)for(const b of boxes){const d=Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y));if(d<score){score=d;pair={a,b,d};}}return pair;});
 assert.ok(pair);
 await p.evaluate(pair=>{const m=previewApp.getMap(),target={x:(pair.a.x+pair.b.x)/2,y:(pair.a.y+pair.b.y)/2},free=[];for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++)if(m.cells[y*m.w+x]===1)free.push({x,y,d:Math.abs(x-target.x)+Math.abs(y-target.y)});free.sort((a,b)=>a.d-b.d);player={x:free[0].x,y:free[0].y};updateVision();draw();},pair);
 for(const [old,name]of [[true,'close-before'],[false,'close-after']]){
  await p.locator('#beforeFloor113').setChecked(old);
  const data=await p.evaluate(pair=>{const c=document.getElementById('map'),t=transform;const centerX=(pair.a.x+1-t.cx)*t.t+t.ox,centerY=(pair.a.y+1.5-t.cy)*t.t+t.oy;const sx=Math.max(0,Math.min(c.width-480,Math.round(centerX-240))),sy=Math.max(0,Math.min(c.height-240,Math.round(centerY-120)));const out=document.createElement('canvas');out.width=960;out.height=480;const g=out.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(c,sx,sy,480,240,0,0,960,480);return out.toDataURL();},pair);
  fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data.split(',')[1],'base64'));
 }
 for(const f of [4,5,6,7]){await p.locator(`[data-floor="${f}"]`).click();assert.ok(await p.evaluate(()=>previewApp.getState().validation.ok));}
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({status:'passed',revision:113,source112Preserved:true,comparisonPixelIdenticalTo112:true,geometryUnchanged:true,layoutsChecked:[4,5,6,7],samplePair:pair,floorRenderScope:scope,floorFixtures:fixtureIds,wallInsetsPixelUnchanged:true,errors,nativeIntegrated:false},null,2)+'\n');console.log(JSON.stringify({status:'passed',pair}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
