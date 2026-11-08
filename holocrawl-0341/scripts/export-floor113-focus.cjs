const fs=require('fs'),path=require('path');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/city-market113');
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage();await p.goto(`${previewURL}/city-market113/#acrylic`);await p.waitForFunction(()=>window.previewReady);
 const data=await p.evaluate(()=>{
  const list=['badge-trays','shirt-stack','delivery-boxes','open-carton'];
  const c=document.createElement('canvas');c.width=896;c.height=536;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#162229';g.fillRect(0,0,c.width,c.height);
  for(let row=0;row<2;row++)for(let i=0;i<list.length;i++){
   const type=list[i],x=i*224,y=row*268,n=document.createElement('canvas');n.width=n.height=32;const q=n.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(floorVariants[0],0,0);
   document.getElementById('beforeFloor113').checked=row===0;
   Scene113.draw(q,{type,x:0,y:0},{seed:'FLOOR113',floorNumber:4},images,32,0);
   g.font='15px "Malgun Gothic", sans-serif';g.textAlign='center';g.fillStyle='#d8e4e9';g.fillText(row===0?'기존112':'입체·접지 정리113',x+112,y+22);
   g.drawImage(n,x+16,y+34,192,192);g.fillText(MerchCatalog.find(m=>m.id===type).name,x+112,y+252);
  }
  return c.toDataURL();
 });fs.writeFileSync(path.join(out,'floor-focus.png'),Buffer.from(data.split(',')[1],'base64'));console.log('Exported4 floor fixtures, before/after at6x.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
