const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),out=path.resolve(__dirname,'../preview/city-market117');
const targets=['shopping-bags','shirt-stack','hoodie-rack'],inputs=JSON.parse(fs.readFileSync(path.join(out,'inputs.json')));
for(const[n,h]of Object.entries(inputs.sourceFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'../city-market115',n))).digest('hex'),h);
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const errors=[],p=await browser.newPage({viewport:{width:1440,height:1100}}),q=await browser.newPage({viewport:{width:1440,height:1100}});q.on('pageerror',e=>errors.push(e.message));
 await p.goto(`${previewURL}/city-market115/`);await p.waitForFunction(()=>window.previewReady);await q.goto(`${previewURL}/city-market117/`);await q.waitForFunction(()=>window.previewReady);
 async function render(page,version){return page.evaluate(version=>{
  const api=version===115?Scene115:Scene117,list=MerchCatalog.filter(m=>m.kind==='floor');return list.map(meta=>{
   const[fw,fh]=MarketGen.footprints[meta.id],f={type:meta.id,x:0,y:0,footW:fw,footH:fh},m={seed:'REST116',floorNumber:4};
   const c=document.createElement('canvas');c.width=fw*32;c.height=40;const g=c.getContext('2d',{willReadFrequently:true});g.imageSmoothingEnabled=false;for(let x=0;x<fw;x++)for(let y=0;y<2;y++)g.drawImage(floorVariants[0],x*32,y*32);g.translate(0,4);api.draw(g,f,m,images,32,0);
   const d=api.sprite(f,m,0),clothing=d.clothingIds||[];
   return {id:meta.id,name:meta.name,fw,fh,png:c.toDataURL(),clothing,colors:clothing.map(id=>MarketMembers.find(m=>m.id===id).color)};
  });
 },version);}
 const before=await render(p,115),after=await render(q,117);let unchanged=0;
 for(const a of after){const b=before.find(b=>b.id===a.id);if(!targets.includes(a.id)){assert.equal(a.png,b.png,a.id);unchanged++;}else assert.notEqual(a.png,b.png,a.id);}
 assert.equal(unchanged,12);assert.equal(await p.evaluate(()=>JSON.stringify(previewApp.getMap())),await q.evaluate(()=>JSON.stringify(previewApp.getMap())));
 const checks=await q.evaluate(()=>{
  const m={seed:'REST116',floorNumber:4},f={type:'shopping-bags',x:0,y:0,footW:1,footH:1},d=Scene117.sprite(f,m,0),points=Scene117.bagContacts(d),body=d.canvas.getContext('2d').getImageData(0,0,32,32).data,c=document.createElement('canvas');c.width=c.height=32;Scene117.draw(c.getContext('2d'),f,m,images,32,0);const painted=c.getContext('2d').getImageData(0,0,32,32).data;
  const contactConnected=points.every(p=>p.y===p.bodyY+1&&body[(p.bodyY*32+p.x)*4+3]>=96&&painted[(p.y*32+p.x)*4+3]>0);
  const hoodies=[];for(let mix=0;mix<4;mix++){const ids=Scene117.clothingIds({type:'hoodie-rack',x:0,y:0},m,mix),rgb=ids.map(id=>MarketMembers.find(m=>m.id===id).color).map(h=>[0,2,4].map(i=>parseInt(h.slice(1+i,3+i),16)));hoodies.push({ids,minDistance:Math.min(...[Math.hypot(...rgb[0].map((v,i)=>v-rgb[1][i])),Math.hypot(...rgb[1].map((v,i)=>v-rgb[2][i])),Math.hypot(...rgb[0].map((v,i)=>v-rgb[2][i]))])});}
  const s=Scene117.sprite({type:'shirt-stack',x:0,y:0,footW:2,footH:1},m,0),a=s.canvas.getContext('2d').getImageData(0,0,s.W,s.H).data,raw=document.createElement('canvas');raw.width=s.W;raw.height=s.H;const g=raw.getContext('2d');g.drawImage(s.art,s.x,s.y);const b=g.getImageData(0,0,s.W,s.H).data;let floatingPixels=0;for(let i=3;i<a.length;i+=4)if(a[i]&&!b[i])floatingPixels++;
  return {contactPoints:points.length,contactConnected,hoodies,shirtFloatingOverlayPixels:floatingPixels};
 });assert.ok(checks.contactPoints>0&&checks.contactConnected);assert.equal(checks.shirtFloatingOverlayPixels,0);assert.ok(checks.hoodies.every(h=>new Set(h.ids).size===3&&h.minDistance>=80));
 // Compose actual before/after renderings without opening a user-facing site.
 const exported=await q.evaluate(({before,after,targets})=>new Promise(async resolve=>{
  const c=document.createElement('canvas');c.width=960;c.height=500;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#16232a';g.fillRect(0,0,c.width,c.height);
  for(let row=0;row<2;row++)for(let col=0;col<3;col++){
   const entry=(row?after:before).find(a=>a.id===targets[col]),im=await new Promise(r=>{const a=new Image();a.onload=()=>r(a);a.src=entry.png;}),x=col*320,y=row*250;
   g.fillStyle='#24343e';g.fillRect(x+4,y+4,312,242);g.fillStyle='#e2ebee';g.font='17px "Malgun Gothic",sans-serif';g.textAlign='center';g.fillText(entry.name,x+160,y+25);g.font='14px "Malgun Gothic",sans-serif';g.fillStyle='#b6c9d1';g.fillText(row?'수정117':'기존115',x+160,y+47);g.drawImage(im,x+(320-im.width*4)/2,y+66,im.width*4,160);
  }resolve(c.toDataURL());
 }),{before,after,targets});fs.writeFileSync(path.join(out,'three-fixes.png'),Buffer.from(exported.split(',')[1],'base64'));
 for(const f of[4,5,6,7]){await q.locator(`[data-floor="${f}"]`).click();assert.ok(await q.evaluate(()=>previewApp.getState().validation.ok));}assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({status:'passed',revision:117,source115Preserved:true,targets,otherFloorFixturesPixelIdentical:unchanged,geometryIdentical:true,checks,garmentSamples:after.filter(a=>a.clothing.length).map(({png,...a})=>a),errors,nativeIntegrated:false},null,2)+'\n');console.log(JSON.stringify({status:'passed',unchanged,checks}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
