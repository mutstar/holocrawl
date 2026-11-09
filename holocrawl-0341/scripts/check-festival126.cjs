const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath}=require('./portable-browser-tools.cjs');
const R=path.resolve(__dirname,'..'),D=path.join(R,'preview/festival126'),url=process.env.HOLOCRAWL_PREVIEW_URL||'http://127.0.0.1:8798';
const region=s=>s.slice(s.indexOf(' function agedWall('),s.indexOf(' function maskAt('));
assert.equal(region(fs.readFileSync(path.join(R,'preview/festival125/festival125.js'),'utf8')),region(fs.readFileSync(path.join(D,'festival126.js'),'utf8')),'Current wall lighting renderer differs');
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1}),errors=[],failed=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)failed.push([r.status(),r.url()]);});
 await p.goto(url+'/festival126/');await p.waitForFunction(()=>window.festivalReady);
 const specs=await p.evaluate(()=>festival126.stock.map(s=>({id:s.id,name:s.name})));assert.equal(specs.length,5);
 const original=await p.evaluate(()=>Array.from(document.getElementById('map').getContext('2d').getImageData(0,0,576,352).data));
 const hashes=[],checks=[];
 for(const s of specs){
  await p.getByRole('button',{name:s.name+' 포장마차 선택',exact:true}).click();
  assert.equal(await p.inputValue('#stallSelect'),s.id);assert.equal(await p.getAttribute(`[data-stall="${s.id}"]`,'aria-pressed'),'true');
  const data=await p.evaluate(({id,original})=>{
   const api=festival126,s=api.getSelected();if(s.id!==id)throw Error('Wrong selected stall');if(s.sprite.width!==96||s.sprite.height!==64)throw Error('Wrong sprite size');
   const q=s.sprite.getContext('2d'),a=q.getImageData(0,0,96,64).data;let opaque=0,transparent=0;
   for(let i=3;i<a.length;i+=4){if(a[i]===255)opaque++;else if(a[i]===0)transparent++;else throw Error('Soft alpha halo');}if(!opaque||!transparent)throw Error('Invalid cutout');
   const m=api.getMap(),spot=api.getSpot(),ox=Math.max(0,Math.min(m.width-18,spot.x-8)),oy=Math.max(0,Math.min(m.height-11,spot.y-3)),sx=(spot.x-ox)*32,sy=(spot.y-oy)*32,c=document.getElementById('map'),pixels=c.getContext('2d').getImageData(0,0,576,352).data;
   let outsideChanges=0;for(let y=0;y<352;y++)for(let x=0;x<576;x++)if(x<sx||x>=sx+96||y<sy||y>=sy+64){const i=(y*576+x)*4;for(let k=0;k<4;k++)if(pixels[i+k]!==original[i+k]){outsideChanges++;break;}}
   if(outsideChanges)throw Error('Changing stall modified map outside its footprint');
   const out=document.createElement('canvas');out.width=1152;out.height=704;const o=out.getContext('2d');o.imageSmoothingEnabled=false;o.drawImage(c,0,0,1152,704);
   return{sprite:s.sprite.toDataURL(),scene:out.toDataURL(),opaque,transparent,outsideChanges};
  },{id:s.id,original});
  const bytes=Buffer.from(data.sprite.split(',')[1],'base64');fs.writeFileSync(path.join(D,'assets',s.id+'96.png'),bytes);hashes.push(crypto.createHash('sha256').update(bytes).digest('hex'));fs.writeFileSync(path.join(D,`map-${s.id}126.png`),Buffer.from(data.scene.split(',')[1],'base64'));checks.push({id:s.id,opaque:data.opaque,transparent:data.transparent,outsideFootprintChanges:data.outsideChanges});
 }
 assert.equal(new Set(hashes).size,5,'Stall sprites must be distinct');
 for(let i=0;i<3;i++){await p.selectOption('#mapSelect',String(i));await p.waitForFunction(()=>festivalReady);for(const s of specs){await p.selectOption('#stallSelect',s.id);assert.equal(await p.evaluate(()=>festival126.getSelected().id),s.id);}await p.click('#nextSpot');await p.click('#original');await p.click('#aged');}
 await p.selectOption('#mapSelect','0');await p.waitForFunction(()=>festivalReady);await p.selectOption('#stallSelect','yakisoba');
 await p.locator('#stalls').screenshot({path:path.join(D,'catalog126.png')});await p.screenshot({path:path.join(D,'samples126.png'),fullPage:true});
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(D,'mobile126.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={status:'passed',revision:126,stalls:checks,spriteDimensions:[96,64],distinctSprites:5,sourceMapSwitches:3,stallMapCombinations:15,wallLighting02RendererIdentical:true,pageErrors:errors,failedRequests:failed,mobileOverflow:false,nativeIntegrated:false};fs.writeFileSync(path.join(D,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
