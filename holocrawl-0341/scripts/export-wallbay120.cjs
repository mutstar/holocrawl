const fs=require('fs'),path=require('path');const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),O=path.resolve(__dirname,'../preview/wall-bay120');
const save=(name,data)=>fs.writeFileSync(path.join(O,name),Buffer.from(data.split(',')[1],'base64'));
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1280,height:1000}});await p.goto(`${previewURL}/city-street120/`);await p.waitForFunction(()=>window.ready);
 const board=await p.evaluate(()=>{
  const c=document.createElement('canvas');c.width=1152;c.height=672;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#172229';g.fillRect(0,0,c.width,c.height);g.fillStyle='#e0e9ed';g.font='21px "Malgun Gothic",sans-serif';g.fillText('1~7층 · 소품 뒤의 벽 전면을 높여 크기 회복',20,31);
  const m={w:6,h:4,cells:[...Array(12).fill(0),...Array(12).fill(1)],seed:'WALL119-GALLERY',floorNumber:4},im=play120.getPropImages(),units=play120.getWallUnits();
  const types=[...MerchCatalog.filter(m=>m.kind==='wall').map(m=>({type:m.id,name:m.name})),{type:'pipe',name:'배관',length:3},{type:'air',name:'실외기',length:1},{type:'vent',name:'환기구',length:1},{type:'cabinet',name:'배전함',length:1}];
  for(let i=0;i<types.length;i++){
   const col=i%3,row=Math.floor(i/3),left=col*384,top=60+row*204,kind=types[i],f={...kind,x:kind.length===1?2:1,y:1};
   g.fillStyle='#223038';g.fillRect(left+3,top,378,200);g.textAlign='center';g.fillStyle='#dbe7ea';g.font='15px "Malgun Gothic",sans-serif';g.fillText(kind.name,left+192,top+22);g.fillStyle='#b1bfc6';g.font='13px "Malgun Gothic",sans-serif';g.fillText('축소119',left+96,top+43);g.fillText('확대120',left+288,top+43);
   for(const after of [false,true]){
    const field=document.createElement('canvas');field.width=96;field.height=64;const q=field.getContext('2d');q.imageSmoothingEnabled=false;q.translate(-32,-32);
    for(let x=1;x<=3;x++){Market108.wall(q,m.cells,m.w,m.h,x,1,32,0);q.drawImage(im.reference,270,150,32,32,x*32,64,32,32);}
    if(!kind.length){if(after)WallBay120.drawFixture(q,f,m,im,32,0);else WallMount119.drawFixture(q,f,m,im,32,0);}
    else if(after)WallBay120.drawUtility(q,f,m,units);else WallMount119.drawUtility(q,f,m,units);
    for(const name of ['body','boots','armour','helmet','sword'])q.drawImage(im[name],96,64,32,32);
    g.drawImage(field,left+(after?192:0),top+56,192,128);
   }
  }return c.toDataURL();
 });save('size-comparison120.png',board);
 await p.locator('#sample').selectOption('0');await p.waitForFunction(()=>window.ready&&play120.getMap().depth===1);await p.locator('#fog').uncheck();await p.locator('[data-zoom="2"]').click();await p.evaluate(()=>play120.focusAmbient('shops'));
 const street=await p.evaluate(()=>{const src=document.getElementById('field'),c=document.createElement('canvas');c.width=960;c.height=500;const q=c.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(src,(src.width-960)/2,(src.height-500)/2,960,500,0,0,960,500);return c.toDataURL();});save('street1-wall120.png',street);
 const q=await b.newPage({viewport:{width:1440,height:1100}});await q.goto(`${previewURL}/city-market120/?floor=4#acrylic`);await q.waitForFunction(()=>window.previewReady);
 const market=await q.evaluate(()=>{const c=document.createElement('canvas');c.width=960;c.height=500;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(canvas,(canvas.width-480)/2,(canvas.height-250)/2-24,480,250,0,0,960,500);return c.toDataURL();});save('market4-wall120.png',market);
 const actual=await p.evaluate(async({street,market})=>{const c=document.createElement('canvas');c.width=960;c.height=1080;const g=c.getContext('2d');g.fillStyle='#172229';g.fillRect(0,0,c.width,c.height);g.imageSmoothingEnabled=false;let i=0;for(const[label,png]of [['1~3층 거리 · 확대120',street],['4~7층 상점가 · 확대120',market]]){g.fillStyle='#deeaee';g.font='20px "Malgun Gothic",sans-serif';g.fillText(label,16,i*540+28);const im=await new Promise(r=>{const im=new Image();im.onload=()=>r(im);im.src=png;});g.drawImage(im,0,i*540+40);i++;}return c.toDataURL();},{street,market});save('actual-maps120.png',actual);
 console.log('Exported all nine before/after wall fixtures and actual street/market views.');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
