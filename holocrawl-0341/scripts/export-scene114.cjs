const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-market114');
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1440,height:1100}});await p.goto(`${previewURL}/city-market114/`);await p.waitForFunction(()=>window.previewReady);
 await p.locator('#exitMode').selectOption('floor');await p.locator('#seed').fill('MARKET114-SCENE-18');await p.locator('#apply').click();
 const proof=await p.evaluate(()=>{
  const m=previewApp.getMap(),a=m.marketProps.find(p=>p.type==='acrylic-rack'&&p.x===60&&p.y===60),b=m.marketProps.find(p=>p.type==='delivery-boxes'&&p.x===56&&p.y===61);if(!a||!b)throw Error('Selected native review objects not generated');
  const center={x:(a.x+b.x)/2+1,y:(a.y+b.y)/2+1},free=[];for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++)if(m.cells[y*m.w+x]===1)free.push({x,y,d:Math.abs(x-center.x)+Math.abs(y-center.y)});free.sort((a,b)=>a.d-b.d);player={x:free[0].x,y:free[0].y};updateVision();draw();
  const x=(center.x-transform.cx)*32,y=(center.y-transform.cy)*32,sx=Math.max(0,Math.min(canvas.width-480,Math.round(x-240))),sy=Math.max(0,Math.min(canvas.height-260,Math.round(y-130))),c=document.createElement('canvas');c.width=960;c.height=520;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(canvas,sx,sy,480,260,0,0,960,520);return {data:c.toDataURL(),seed:m.seed,exitMode:'floor',a,b,validation:m.validation};
 });assert.ok(proof.validation.ok);fs.writeFileSync(path.join(out,'group114.png'),Buffer.from(proof.data.split(',')[1],'base64'));delete proof.data;fs.writeFileSync(path.join(out,'group114.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({status:'passed',seed:proof.seed}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
