const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),R=path.resolve(__dirname,'..'),O=path.join(R,'preview/wall-mount119');
const inputs=JSON.parse(fs.readFileSync(path.join(O,'inputs.json'))),checkInputs=()=>{for(const[n,h]of Object.entries(inputs.sourceFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(R,n))).digest('hex'),h,n);};checkInputs();
assert.equal(fs.readFileSync(path.join(R,'preview/city-street118/ambient118.js'),'utf8'),fs.readFileSync(path.join(R,'preview/city-street119/ambient118.js'),'utf8'));
assert.deepEqual(JSON.parse(fs.readFileSync(path.join(R,'preview/city-street119/manifest.json'))).maps,JSON.parse(fs.readFileSync(path.join(R,'preview/city-street118/manifest.json'))).maps);
const oldGen=require('../preview/city-market117/layout115.js'),newGen=require('../preview/city-market119/layout115.js');let marketMaps=0;
for(let floor=4;floor<=7;floor++)for(let n=0;n<20;n++){const a=oldGen.generate('WALL119-'+n,floor,'floor'),b=newGen.generate('WALL119-'+n,floor,'floor');assert.deepEqual(a,b);assert.ok(b.validation.ok);marketMaps++;}
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1280,height:1000}}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
 await p.goto(`${previewURL}/city-street119/`);await p.waitForFunction(()=>window.ready,null,{timeout:60000});
 const counts={wallFixtures:0,utilities:0,alphaPixels:0,nativeFrames:0};
 for(let n=0;n<36;n++){
  if(n){await p.locator('#sample').selectOption(String(n));await p.waitForFunction(n=>window.ready&&play119.getMap().seed===play119.manifest.maps[n].seed&&play119.getMap().depth===play119.manifest.maps[n].depth,n);}
  const a=await p.evaluate(()=>{
   const m=play119.getMap(),plan=play119.getAmbience(),stock={...m,seed:String(m.seed),floorNumber:m.depth},im=play119.getPropImages(),units=play119.getWallUnits();let pixels=0;
   for(const f of [...plan.walls,...plan.infra]){const c=f.length?WallMount119.utilitySprite(f,m,units):WallMount119.fixtureSprite(f,stock,im),data=c.getContext('2d').getImageData(0,0,c.width,32).data;let opaque=0;
    for(let y=0;y<32;y++)for(let x=0;x<c.width;x++)if(data[(y*c.width+x)*4+3]){if(!WallMount119.allowed(m,f.x+Math.floor(x/32),f.y,x%32,y))throw Error('Mount outside front');opaque++;}if(!opaque)throw Error('Empty wall fixture');pixels+=opaque;
   }
   let frames=0;for(let i=0;i<play119.getProbe().frames.length;i++){if(play119.oracleFrame(i)!==0)throw Error('LOS changed');frames++;}return{wallFixtures:plan.walls.length,utilities:plan.infra.length,alphaPixels:pixels,nativeFrames:frames};
  });for(const k of Object.keys(counts))counts[k]+=a[k];
 }
 // Exercise every neighbour arrangement, including concave/convex corners.
 const masks=await p.evaluate(()=>{
  const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],im=play119.getPropImages(),units=play119.getWallUnits(),kinds=MerchCatalog.filter(a=>a.kind==='wall').map(a=>a.id);let cases=0,pixels=0;
  for(let mask=0;mask<256;mask++){
   const cells=Array(25).fill(1);cells[2*5+2]=0;dirs.forEach(([dx,dy],bit)=>{if(mask&(1<<bit))cells[(2+dy)*5+2+dx]=0;});const m={w:5,h:5,cells,seed:'MASK119-'+mask,floorNumber:4};
   for(const type of kinds){const f={x:2,y:2,type},c=WallMount119.fixtureSprite(f,m,im),a=c.getContext('2d').getImageData(0,0,c.width,32).data;
    for(let y=0;y<32;y++)for(let x=0;x<c.width;x++)if(a[(y*c.width+x)*4+3]){const xx=f.x+Math.floor(x/32),south=cells[(f.y+1)*5+xx]===0,east=cells[f.y*5+xx+1]===0,cut=29+Math.floor((y-18)*3/13);if(cells[f.y*5+xx]!==0||south||y<19||y>30||(!east&&x%32>=cut))throw Error('Corner/roof/side leak');pixels++;}cases++;
   }
  }return{cases,pixels};
 });assert.equal(masks.cases,1280);
 // Actual street image differs from the undecorated-wall render only on the front.
 const streetPixels=await p.evaluate(()=>{
  const api=play119,m=api.getMap();document.getElementById('fog').checked=false;document.querySelector('[data-zoom="2"]').click();api.focusAmbient('shops');const state=api.getState(),c=document.getElementById('field'),g=c.getContext('2d'),paint=g.getImageData(0,0,c.width,c.height).data;
  const f=WallMount119.drawFixture,u=WallMount119.drawUtility;WallMount119.drawFixture=()=>{};WallMount119.drawUtility=()=>{};api.reset(state.player,'test');const base=g.getImageData(0,0,c.width,c.height).data;WallMount119.drawFixture=f;WallMount119.drawUtility=u;api.reset(state.player,'검토');
  const{s,ox,oy}=api.getView();let changed=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(paint[i]===base[i]&&paint[i+1]===base[i+1]&&paint[i+2]===base[i+2])continue;const px=Math.floor((x-ox)/s),py=Math.floor((y-oy)/s);if(!WallMount119.allowed(m,Math.floor(px/32),Math.floor(py/32),(px%32+32)%32,(py%32+32)%32))throw Error('Street roof/floor changed');changed++;}return changed;
 });assert.ok(streetPixels>0);
 // Same underlying market maps, member choices, and all fifteen floor sprites.
 const q=await browser.newPage({viewport:{width:1280,height:1000}});q.on('pageerror',e=>errors.push(e.message));await q.goto(`${previewURL}/city-market119/#acrylic`);await q.waitForFunction(()=>window.previewReady);
 const before=await browser.newPage({viewport:{width:1280,height:1000}});await before.goto(`${previewURL}/city-market117/#acrylic`);await before.waitForFunction(()=>window.previewReady);
 const floorSprites=page=>page.evaluate(()=>MerchCatalog.filter(m=>m.kind==='floor').map(m=>{const[footW,footH]=MarketGen.footprints[m.id],f={x:0,y:0,type:m.id,footW,footH},c=document.createElement('canvas');c.width=footW*32;c.height=footH*32;Scene117.draw(c.getContext('2d'),f,{seed:'119-PRESERVE',floorNumber:4},images,32,0);return[m.id,c.toDataURL()];}));
 assert.deepEqual(await floorSprites(q),await floorSprites(before));assert.equal(await q.evaluate(()=>JSON.stringify(previewApp.getMap())),await before.evaluate(()=>JSON.stringify(previewApp.getMap())));await before.close();
 let marketFixtures=0,changedPixels=0;
 for(let floor=4;floor<=7;floor++){
  await q.locator(`[data-floor="${floor}"]`).click();await q.locator('#acrylicView').click();
  const a=await q.evaluate(()=>{
   const m=previewApp.getMap();let painted=0;for(const f of m.marketWalls){const c=WallMount119.fixtureSprite(f,m,images,0),a=c.getContext('2d').getImageData(0,0,64,32).data;for(let y=0;y<32;y++)for(let x=0;x<64;x++)if(a[(y*64+x)*4+3]){if(!WallMount119.allowed(m,f.x+Math.floor(x/32),f.y,x%32,y))throw Error('Market mount outside front');painted++;}}
   const visible=ctx.getImageData(0,0,canvas.width,canvas.height).data,save=WallMount119.drawFixture;WallMount119.drawFixture=()=>{};draw();const base=ctx.getImageData(0,0,canvas.width,canvas.height).data;WallMount119.drawFixture=save;draw();let changed=0;
   const{t,cx,cy,ox,oy}=transform;for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++){const i=(y*canvas.width+x)*4;if(visible[i]===base[i]&&visible[i+1]===base[i+1]&&visible[i+2]===base[i+2])continue;const px=Math.floor(x-ox+cx*t),py=Math.floor(y-oy+cy*t);if(!WallMount119.allowed(m,Math.floor(px/32),Math.floor(py/32),px%32,py%32))throw Error('Market roof/floor changed');changed++;}return{fixtures:m.marketWalls.length,changed,painted};
  });marketFixtures+=a.fixtures;changedPixels+=a.changed;
 }
 await q.setViewportSize({width:390,height:844});assert.ok(await q.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);checkInputs();
 const validation={status:'passed',revision:119,nativeIntegrated:false,sourceVersionsPreserved:[117,118],nativeMaps:36,marketMaps,marketFixtures,counts,neighbourMaskCases:masks.cases,roofCopingSideFloorLeakPixels:0,actualStreetChangedFrontPixels:streetPixels,actualMarketChangedFrontPixels:changedPixels,floorSpritesPixelIdentical:15,geometryAndCollisionIdentical:true,nativeLOSUnchanged:true,errors};
 for(const folder of ['wall-mount119','city-market119','city-street119'])fs.writeFileSync(path.join(R,'preview',folder,'validation.json'),JSON.stringify(validation,null,2)+'\n');console.log(JSON.stringify(validation));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
