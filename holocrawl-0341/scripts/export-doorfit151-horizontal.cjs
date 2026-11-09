// Review-only export of the existing151 door between left/right walls.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const D=path.resolve(__dirname,'../preview/doorfit151'),seed='F1-mw8yvehm';
const frozen=['doors151.js','app151.js','generator151.js','materials151.js'];
const hashes=()=>Object.fromEntries(frozen.map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(D,n))).digest('hex')]));
(async()=>{const before=hashes(),b=await chromium.launch({executablePath,headless:true});try{
 const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`${previewURL}/doorfit151/?seed=${seed}&door=horizontal`);await p.waitForFunction(()=>window.homeReady);
 const result=await p.evaluate(async()=>{const a=holoHome151,m=a.getMap(),v=a.getState(),c=document.getElementById('field');a.stop();a.focus(m.homeFocus,true);v.opened.clear();c.width=m.w*32;c.height=m.h*32;a.setOverview(true);
  const d=m.doors.find(d=>!d.home&&DoorFit151.direction(m,d)==='horizontal'&&d.x>=3&&d.x<m.w-3&&d.y>=2&&d.y<m.h-2);
  if(!d||m.cells[d.y*m.w+d.x-1]!==0||m.cells[d.y*m.w+d.x+1]!==0)throw Error('Expected walls on both sides');
  const q=c.getContext('2d'),closed=q.getImageData(0,0,c.width,c.height),frames=[c.toDataURL()];v.opened.add(d.id);a.draw();const opened=q.getImageData(0,0,c.width,c.height);frames.push(c.toDataURL());
  let changed=0,outside=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const k=(y*c.width+x)*4;if(closed.data[k]===opened.data[k]&&closed.data[k+1]===opened.data[k+1]&&closed.data[k+2]===opened.data[k+2]&&closed.data[k+3]===opened.data[k+3])continue;changed++;if(x<d.x*32||x>=(d.x+1)*32||y<d.y*32-4||y>=d.y*32+36)outside++;}
  const out=document.createElement('canvas');out.width=1008;out.height=350;const g=out.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#182120';g.fillRect(0,0,out.width,out.height);g.fillStyle='#deebe3';g.font='21px "Malgun Gothic",sans-serif';
  for(let i=0;i<2;i++){g.fillText(i?'양옆 벽 · 열림':'양옆 벽 · 닫힘',i*504+12,30);const im=new Image();im.src=frames[i];await im.decode();g.drawImage(im,(d.x-2)*32,(d.y-1)*32,160,96,i*504+12,48,480,288);}
  const profile=DoorFit151.capProfile(m,d,v.base);return{png:out.toDataURL(),door:{...d,direction:'horizontal'},changedPixels:changed,changesOutsideDoor:outside,wallProfileHeight:profile.h,wallProfileSource:profile.source};
 });assert(result.changedPixels>0);assert.equal(result.changesOutsideDoor,0);assert.equal(errors.length,0);assert.deepEqual(hashes(),before);
 fs.writeFileSync(path.join(D,'horizontal-wall151.png'),Buffer.from(result.png.split(',')[1],'base64'));delete result.png;
 fs.writeFileSync(path.join(D,'horizontal-review-validation.json'),JSON.stringify({status:'passed',seed,...result,sourceHashes:before,renderingCodeUnchanged:true,pageErrors:errors,scope:'Existing151 horizontal door closed/open screenshot; no art or geometry changes.'},null,2)+'\n');
 const html='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>151번 문 · 양옆에 벽이 있을 때</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1100px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>양옆에 벽이 이어질 때 · 가로벽 문</h1><p>151번 문 모양 그대로입니다. 왼쪽은 닫힘, 오른쪽은 열림이며 위아래로 통행합니다.</p><img src="horizontal-wall151.png" alt="좌우 벽 사이 일반문 닫힘·열림"><p><a href="./?seed=F1-mw8yvehm&door=horizontal">실제 랜덤 지도에서 이동하기</a> · <a href="door-review.html">위아래 벽에서 본 모습</a></p></main></html>';
 fs.writeFileSync(path.join(D,'horizontal-review.html'),html+'\n');console.log(JSON.stringify(result));
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
