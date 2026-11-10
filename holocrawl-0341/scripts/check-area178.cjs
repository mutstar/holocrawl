const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const dir=path.join(__dirname,'../preview/area15-178'),browser=await chromium.launch({executablePath,headless:true}),page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
await page.goto(previewURL+'/area15-178/');await page.waitForFunction(()=>window.area178Ready,{timeout:30000});
const validation=await page.evaluate(()=>{const a=AreaArt178,results=[];
for(const mode of ['attached','standalone']){const m=a.maps[mode],d=AreaLayout178.distances(m,m.start),rooms=m.servicePoints.map(p=>({id:p.id,reachable:d[p.y*m.w+p.x]>=0}));
const outer=mode==='standalone'?[...Array(m.h).keys()].every(y=>[0,1,m.w-2,m.w-1].every(x=>m.open[y*m.w+x]))&&[...Array(m.w).keys()].every(x=>[0,1,m.h-2,m.h-1].every(y=>m.open[y*m.w+x])):true;
const occupied=new Set();let overlaps=0,outsideRoom=0,unblockedFurniture=0;for(const p of [...m.props,...m.furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const i=y*m.w+x;if(occupied.has(i))overlaps++;occupied.add(i);if(!m.inner[i])outsideRoom++;if(m.open[i])unblockedFurniture++;}
const strandedInterior=m.inner.reduce((n,inside,i)=>n+(inside&&m.open[i]&&d[i]<0?1:0),0);
results.push({mode,rooms,entryReachable:d[m.entry.y*m.w+m.entry.x]>=0,outerTwoTileRing:outer,furnitureCount:m.furniture.length,overlaps,outsideRoom,unblockedFurniture,strandedInterior});}
const ca=a.canvases.attached.getContext('2d').getImageData(0,0,736,672).data,cb=a.canvases.standalone.getContext('2d').getImageData(0,0,736,672).data;let differingInteriorPixels=0;
for(let y=0;y<672;y++)for(let x=0;x<736;x++)if(a.maps.attached.inner[Math.floor(y/32)*23+Math.floor(x/32)]){const i=(y*736+x)*4;if([0,1,2,3].some(k=>ca[i+k]!==cb[i+k]))differingInteriorPixels++;}
return {revision:178,results,differingInteriorPixels,doorOpeningPixels:a.doorMask.reduce((x,y)=>x+y,0),nativeIntegrated:false};});
for(const r of validation.results){assert(r.rooms.every(p=>p.reachable));assert(r.entryReachable&&r.outerTwoTileRing);for(const k of ['overlaps','outsideRoom','unblockedFurniture','strandedInterior'])assert.equal(r[k],0,k);}assert.equal(validation.differingInteriorPixels,0);assert(validation.doorOpeningPixels>300);
for(const mode of ['attached','standalone']){const data=await page.locator('#'+mode).evaluate(c=>c.toDataURL().split(',')[1]);fs.writeFileSync(path.join(dir,mode+'178.png'),Buffer.from(data,'base64'));}
await page.locator('#door').click();assert.equal(await page.evaluate(()=>AreaArt178.getState().opened),false);await page.locator('#door').click();
await page.locator('[data-mode=standalone]').click();assert.equal(await page.locator('#zoom').evaluate(c=>c.width),1472);await page.locator('#close').click();
await page.screenshot({path:path.join(dir,'page178.png'),fullPage:true});await page.setViewportSize({width:390,height:844});validation.mobileOverflow=await page.evaluate(()=>Math.max(0,document.documentElement.scrollWidth-innerWidth));assert.equal(validation.mobileOverflow,0);assert.deepEqual(errors,[]);validation.errors=errors;validation.status='passed';fs.writeFileSync(path.join(dir,'validation.json'),JSON.stringify(validation,null,2)+'\n');console.log(JSON.stringify(validation));await browser.close();})().catch(e=>{console.error(e);process.exit(1);});
