const assert=require('assert/strict'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const output=path.resolve(__dirname,'../preview/wall-history83');
(async()=>{
 const manifest=JSON.parse(fs.readFileSync(path.join(output,'manifest.json'),'utf8'));
 for(const stage of manifest.stages)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(output,stage.image))).digest('hex'),stage.sha256);
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`${previewURL}/wall-history83/`);await page.waitForFunction(()=>window.ready);
  assert.equal(await page.locator('#history article').count(),manifest.stages.length-1);
  await page.locator('#history .image-button').first().click();await page.locator('dialog[open]').waitFor();
  assert.equal(await page.locator('#old-title').textContent(),manifest.stages[0].title);
  await page.locator('#close').click();
  await page.locator('#full').click();assert.equal(await page.evaluate(()=>window.wallHistory83.getMode()),'full');
  assert.equal(await page.locator('#latest').getAttribute('width'),'2560');
  await page.locator('#crop').click();
  assert.equal(await page.locator('#latest').getAttribute('width'),String(manifest.crop.width*32));
  const sheet=await page.evaluate(async()=>{
   const m=window.wallHistory83.manifest,r=m.crop,stages=[...m.stages.filter(s=>s.latest),...m.stages.filter(s=>!s.latest)];
   const w=352,h=256,pad=14,header=54,cellW=w+pad*2,cellH=h+header+pad,cols=3;
   const canvas=document.createElement('canvas');canvas.width=cols*cellW;canvas.height=Math.ceil(stages.length/cols)*cellH+62;
   const c=canvas.getContext('2d');c.fillStyle='#11181d';c.fillRect(0,0,canvas.width,canvas.height);c.imageSmoothingEnabled=false;
   c.fillStyle='#e1e9e8';c.font='bold 24px "Malgun Gothic",sans-serif';c.fillText(`잔향도시 벽 · 이전 ${stages.length-1}종 + 최신`,16,37);
   for(const [i,s]of stages.entries()){
    const x=i%cols*cellW,y=62+Math.floor(i/cols)*cellH;
    c.fillStyle=s.latest?'#29463a':'#1e2b31';c.fillRect(x+5,y+4,cellW-10,cellH-8);
    c.fillStyle=s.latest?'#c0e7ca':'#e0e6e8';c.font='bold 16px "Malgun Gothic",sans-serif';c.fillText(s.title,x+pad,y+26);
    c.fillStyle='#acb9bd';c.font='12px "Malgun Gothic",sans-serif';c.fillText(s.latest?'현재 기본 벽 · 같은 지도 재현':s.id,x+pad,y+44);
    const image=await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=s.image;});
    c.drawImage(image,r.x*32,r.y*32,r.width*32,r.height*32,x+pad,y+header,w,h);
   }
   return canvas.toDataURL().split(',')[1];
  });
  fs.writeFileSync(path.join(output,'all-walls.png'),Buffer.from(sheet,'base64'));
  await page.screenshot({path:path.join(output,'overview.png')});
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'browser-validation.json'),JSON.stringify({status:'passed',wallVersions:manifest.stages.length,sourceHashesVerified:true,compareDialog:true,sameMapToggle:true,mobileOverflow:false,pageErrors:errors},null,2)+'\n');
  console.log(`Verified ${manifest.stages.length} wall versions, latest comparison, full-map toggle and mobile layout.`);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
