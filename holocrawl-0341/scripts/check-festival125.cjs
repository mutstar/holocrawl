const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath}=require('./portable-browser-tools.cjs');
const R=path.resolve(__dirname,'..'),D=path.join(R,'preview/festival125'),url=process.env.HOLOCRAWL_PREVIEW_URL||'http://127.0.0.1:8798';
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1}),errors=[],failed=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failed.push([r.status(),r.url()]);});
 await p.goto(url+'/festival125/');await p.waitForFunction(()=>window.festivalReady,{timeout:30000});
 const pixels=await p.evaluate(()=>{
  const api=festival125,alpha=c=>c.getContext('2d').getImageData(0,0,c.width,c.height).data;
  const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');let n=0;
  for(let mask=0;mask<256;mask++)for(let v=0;v<8;v++){
   q.clearRect(0,0,32,32);q.drawImage(api.wall,...api.rects[`${mask}:${v}`],0,0,32,32);const a=alpha(c),d=alpha(api.agedWall(mask,v));
   for(let i=3;i<a.length;i+=4)if(a[i]!==d[i])throw Error(`Wall silhouette mismatch ${mask}:${v}`);n++;
  }
  for(const sprite of [api.stall,api.lantern]){const a=alpha(sprite);let transparent=0,opaque=0;for(let i=3;i<a.length;i+=4){if(a[i]===0)transparent++;else if(a[i]===255)opaque++;else throw Error('Soft sprite alpha');}if(!transparent||!opaque)throw Error('Missing transparency or sprite');}
  const left=alpha(api.agedWall(68,0,1,0)),right=alpha(api.agedWall(68,0,2,0));let seamPixels=0;
  for(let y=10;y<32;y++)if(api.planes['68'][y*32+31]==='1'&&api.planes['68'][y*32]==='1'){for(let k=0;k<3;k++)if(left[(y*32+31)*4+k]!==right[y*32*4+k])throw Error('Material seam at world64');seamPixels++;}
  if(!seamPixels)throw Error('Seam check did not cover the wall front');
  return{wallTiles:n,silhouettePixels:n*1024,continuousMaterialSeamPixels:seamPixels,stall:[api.stall.width,api.stall.height],lantern:[api.lantern.width,api.lantern.height],hardAlpha:true};
 });
 let locations=0;for(let i=0;i<3;i++){
  await p.selectOption('#mapSelect',String(i));await p.waitForFunction(n=>window.festivalReady&&Number(document.getElementById('mapSelect').value)===n,i);
  locations+=await p.evaluate(()=>{const m=festival125.getMap();for(const s of festival125.getSpots())for(let dy=0;dy<4;dy++)for(let dx=-1;dx<4;dx++)if(m.rows[s.y+dy][s.x+dx]!=='.')throw Error('Blocked stall frontage');return festival125.getSpots().length;});
  await p.click('#nextSpot');await p.click('#original');assert.equal(await p.getAttribute('#original','aria-pressed'),'true');await p.click('#aged');
 }
 await p.selectOption('#mapSelect','0');await p.waitForFunction(()=>festivalReady);await p.click('#lamps');await p.click('#lamps');
 const assets=await p.evaluate(()=>{const c=document.getElementById('map'),out=document.createElement('canvas');out.width=c.width*2;out.height=c.height*2;const q=out.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(c,0,0,out.width,out.height);return{stall:festival125.stall.toDataURL(),lantern:festival125.lantern.toDataURL(),material:festival125.texture.toDataURL(),scene:out.toDataURL()};});
 for(const[name,data]of Object.entries(assets)){const target=name==='scene'?path.join(D,'map-example125.png'):path.join(D,'assets',name==='material'?'wall-material64.png':name==='stall'?'takoyaki96.png':'lantern16.png');fs.writeFileSync(target,Buffer.from(data.split(',')[1],'base64'));}
 await p.screenshot({path:path.join(D,'samples125.png'),fullPage:true});await p.locator('.cards').screenshot({path:path.join(D,'asset-samples125.png')});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const catalog=await p.evaluate(()=>festival125.mapCandidates.map(m=>({seed:m.seed,locations:m.locations}))),selectedSeeds=await p.evaluate(()=>festival125.entries.map(m=>m.seed));
 const result={status:'passed',revision:125,browserStudyOnly:true,nativeIntegrated:false,sourceMaps:3,sourceMapsScanned:catalog.length,sourceMapCandidates:catalog,selectedSeeds,validStallLocations:locations,...pixels,pageErrors:errors,failedRequests:failed,mobileOverflow:false};fs.writeFileSync(path.join(D,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
