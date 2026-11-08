const fs=require('fs'),path=require('path');const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs'),O=path.resolve(__dirname,'../preview/city-street118');
(async()=>{const b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage({viewport:{width:1100,height:1000}});await p.goto(`${previewURL}/city-street118/`);await p.waitForFunction(()=>window.ready);
 const scenes=[{i:0,kind:'shops',label:'1층 · 진열창과 작은 매대'},{i:1,kind:'utilities',label:'2층 · 벽 배관'},{i:2,center:[49,32],label:'3층 · 배전함과 길가 울타리'}],shots=[];
 for(const scene of scenes){await p.locator('#sample').selectOption(String(scene.i));await p.waitForFunction(i=>window.ready&&play118.getMap().depth===i+1,scene.i);await p.locator('#fog').uncheck();await p.locator('[data-zoom="2"]').click();await p.evaluate(s=>{
  if(s.kind)play118.focusAmbient(s.kind);else{const m=play118.getMap(),pts=[];for(let y=1;y<m.height-1;y++)for(let x=1;x<m.width-1;x++)if(play118.pass(x,y)&&m.rows[y][x]!=='+')pts.push({x,y});pts.sort((a,b)=>Math.hypot(a.x-s.center[0],a.y-s.center[1])-Math.hypot(b.x-s.center[0],b.y-s.center[1]));play118.reset(pts[0],'거리 소품 검토');}
 },scene);const png=await p.locator('#field').screenshot({path:path.join(O,`floor${scene.i+1}.png`)});shots.push({...scene,png:'data:image/png;base64,'+png.toString('base64')});}
 const board=await p.evaluate(async shots=>{
  const c=document.createElement('canvas');c.width=1060;c.height=3*590;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  for(let i=0;i<shots.length;i++){const s=shots[i],im=await new Promise(r=>{const im=new Image();im.onload=()=>r(im);im.src=s.png;});g.fillStyle='#172228';g.fillRect(0,i*590,1060,590);g.fillStyle='#d7e5ea';g.font='20px "Malgun Gothic",sans-serif';g.fillText(s.label,18,i*590+30);g.drawImage(im,0,85,im.width,550,0,i*590+40,1060,550);}return c.toDataURL();
 },shots);fs.writeFileSync(path.join(O,'street118-review.png'),Buffer.from(board.split(',')[1],'base64'));
 // Uncut floor overview: native map, facility and all ambient placements.
 await p.locator('#sample').selectOption('0');await p.waitForFunction(()=>window.ready&&play118.getMap().depth===1);await p.locator('[data-zoom="fit"]').click();await p.locator('#field').screenshot({path:path.join(O,'floor1-overview.png')});
 console.log('Exported three actual street views and one floor overview.');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
