const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/native-play107');
(async()=>{
 const v=JSON.parse(fs.readFileSync(path.join(out,'validation.json'))),manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 assert.equal(v.status,'passed');assert.equal(manifest.maps.length,177);
 const browser=await chromium.launch({executablePath,headless:true});try{
  const p=await browser.newPage({viewport:{width:1380,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`${previewURL}/native-play107/`);await p.waitForFunction(()=>window.ready);
  const checks=[];let oracleChecks=0,doorChecks=0,layerChecks=0;
  for(let i=0;i<9;i++){
   await p.locator('#sample').selectOption(String(i));await p.waitForFunction(seed=>window.ready&&play107.getMap().seed===seed,manifest.maps[i].seed);
   await p.locator('#facilityStart').click();assert.ok(await p.locator('#fog').isChecked());
   await p.screenshot({path:path.join(out,`${manifest.maps[i].facility}-fog.png`),fullPage:true});
   const native=JSON.parse(fs.readFileSync(path.join(out,manifest.maps[i].file)));assert.deepEqual(await p.evaluate(()=>play107.getMap()),native);
   const oracle=await p.evaluate(()=>{const q=play107.getProbe(),indices=[0,q.frames.length-1,q.frames.findIndex(f=>f.label==='door-closed'),q.frames.findIndex(f=>f.label==='door-open')].filter(i=>i>=0);return indices.map(i=>play107.oracleFrame(i))});assert.ok(oracle.every(n=>n===0));oracleChecks+=oracle.length;
   const door=await p.evaluate(()=>{
    const r=play107,m=r.getMap();let tested=0;
    for(const d of m.doors.filter(d=>m.origin&&d.x>=m.origin.x&&d.y>=m.origin.y&&d.x<m.origin.x+m.origin.width&&d.y<m.origin.y+m.origin.height)){
     const route=r.route(d,false);if(!route.length)throw Error('Native facility door unreachable in browser');
     for(const next of route.slice(1)){let current=r.getState().player;r.move(next.x-current.x,next.y-current.y);current=r.getState().player;if(current.x!==next.x||current.y!==next.y)r.move(next.x-current.x,next.y-current.y)}
     const s=r.getState();if(!d.linked.every(([x,y])=>s.opened.includes(`${x},${y}`)))throw Error('Linked door did not open');tested++;
    }return tested;
   });doorChecks+=door;
   await p.locator('#actorScene').click();await p.locator('#fog').uncheck();
   const diff=await p.evaluate(()=>{
    const input=document.getElementById('actors');input.checked=false;input.dispatchEvent(new Event('change'));const c=document.getElementById('field'),g=c.getContext('2d'),a=g.getImageData(0,0,c.width,c.height).data;
    input.checked=true;input.dispatchEvent(new Event('change'));const b=g.getImageData(0,0,c.width,c.height).data,r=play107.getView(),actors=play107.getProbe().actors.filter(a=>a.kind!=='player');let changed=0,outside=0,box=[1e9,1e9,0,0],examples=[];
    for(let i=0;i<a.length;i+=4)if([0,1,2,3].some(k=>a[i+k]!==b[i+k])){changed++;const x=(i/4)%c.width,y=Math.floor(i/4/c.width);if(!actors.some(t=>x>=r.ox+t.x*32*r.s&&x<r.ox+(t.x+1)*32*r.s&&y>=r.oy+t.y*32*r.s&&y<r.oy+(t.y+1)*32*r.s)){outside++;if(examples.length<8)examples.push({x,y,a:[...a.slice(i,i+4)],b:[...b.slice(i,i+4)]});box=[Math.min(box[0],x),Math.min(box[1],y),Math.max(box[2],x),Math.max(box[3],y)]}}
    return {changed,outside,box,examples,view:r,actors,canvas:[c.width,c.height]};
   });console.log(JSON.stringify({facility:manifest.maps[i].facility,diff}));assert.ok(diff.changed>0);assert.equal(diff.outside,0);layerChecks++;
   await p.screenshot({path:path.join(out,`${manifest.maps[i].facility}-actors.png`),fullPage:true});
   await p.locator('[data-zoom="fit"]').click();await p.screenshot({path:path.join(out,`${manifest.maps[i].facility}-fullmap.png`),fullPage:true});
   await p.locator('[data-zoom="2"]').click();await p.locator('#fog').check();await p.locator('#actors').uncheck();
   checks.push({facility:manifest.maps[i].facility,nativeGeometryExact:true,losMatches:true,doorGroups:true,actorLayerScope:diff,fullMap:true});
  }
  for(const i of [9,22,36]){await p.locator('#sample').selectOption(String(i));await p.waitForFunction(seed=>window.ready&&play107.getMap().seed===seed,manifest.maps[i].seed);assert.equal(await p.evaluate(()=>play107.oracleFrame(0)),0);oracleChecks++;await p.locator('#stairStart').click()}
  await p.locator('#sample').selectOption('0');await p.waitForFunction(()=>window.ready&&play107.getMap().facility==='theater');await p.locator('#actorScene').click();await p.locator('#fog').uncheck();await p.screenshot({path:path.join(out,'overview.png'),fullPage:true});
  await p.locator('#facilityStart').click();await p.locator('#fog').check();await p.screenshot({path:path.join(out,'entrance-fog.png'),fullPage:true});
  await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  const result={status:'passed',checks,browserNativeLosComparisons:oracleChecks,facilityDoorGroupsTested:doorChecks,actorLayerCases:layerChecks,mobileOverflow:false,pageErrors:errors};
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:'passed',facilities:9,oracleChecks,doorChecks,layerChecks}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
