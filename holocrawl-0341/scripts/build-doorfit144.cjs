const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit143'),D=path.join(R,'preview/doorfit144');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app'])fs.writeFileSync(path.join(D,name+'144.js'),fs.readFileSync(path.join(S,name+'143.js'),'utf8').replaceAll('143','144'));
fs.writeFileSync(path.join(D,'doors144.js'),`(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function sprite(opened){if(sprites.has(opened))return sprites.get(opened);const c=document.createElement('canvas');c.width=32;c.height=36;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 // Native wall rails span0..27;28..31 are the east-facing shadow, not part of the frame.
 for(const [dx,color]of [[28,'#57696f'],[29,'#3c4f54'],[30,'#2c363c'],[31,'#2f393f']]){q.fillStyle=color;q.fillRect(dx,0,1,36);}
 q.fillStyle='#273b39';q.fillRect(0,0,28,36);q.clearRect(2,3,24,32);
 q.fillStyle='#718a85';q.fillRect(0,0,28,3);q.fillRect(0,3,2,32);q.fillRect(26,3,2,32);
 q.fillStyle='#9ca9aa';q.fillRect(0,0,28,1);q.fillStyle='#7c888d';q.fillRect(0,1,1,34);q.fillStyle='#747d81';q.fillRect(27,1,1,34);
 q.fillStyle='#465c58';q.fillRect(1,2,26,1);q.fillRect(1,35,26,1);
 if(opened){for(const x of [2,22]){q.fillStyle='#304b4d';q.fillRect(x,3,4,32);q.fillStyle='#91a9a2';q.fillRect(x,3,1,31);q.fillStyle='#5f8182';q.fillRect(x+1,5,2,27);q.fillStyle='#bdbe9c';q.fillRect(x+1,24,1,3);}}
 else{for(const x of [2,15]){q.fillStyle='#314b4c';q.fillRect(x,3,11,32);q.fillStyle='#648386';q.fillRect(x+1,4,9,30);q.fillStyle='#93a9a4';q.fillRect(x+1,4,1,29);q.fillRect(x+2,4,7,1);q.fillStyle='#adc0b4';q.fillRect(x+3,7,5,1);q.fillStyle='#28494f';q.fillRect(x+2,8,7,13);q.fillStyle='#426b76';q.fillRect(x+3,9,5,11);q.fillStyle='#729095';q.fillRect(x+3,9,1,10);q.fillStyle='#45696b';q.fillRect(x+2,23,7,1);q.fillStyle='#587574';q.fillRect(x+2,25,7,7);}
  q.fillStyle='#c4c59b';q.fillRect(11,24,1,4);q.fillRect(16,24,1,4);
 }
 sprites.set(opened,c);return c;}
function draw(q,m,d,opened){q.drawImage(sprite(opened),d.x*32,d.y*32-4);}
root.DoorFit144={solids,direction,draw,sprite,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:11,grayRight:27,shadowStart:28,shadowWidth:4}};})(globalThis);`);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('143','144').replace('양방향 문 · 벽 폭과 높이 통일','문틀 · 그림자 아닌 회색 벽선에 정렬');const a=html.indexOf('<h2>벽 폭 그대로'),b=html.indexOf('<footer>',a);html=html.slice(0,a)+'<h2>오른쪽 그림자4px를 문틀에서 분리</h2><p>왼쪽 기준은 유지하고 문틀 오른쪽은 회색 벽선(27열)에 맞췄습니다.28~31열은 벽과 같은 그림자로 연결합니다. 높이36px와 두 방향 동일 규격·동일 폭의 양문을 유지합니다.</p><img src="doors-comparison144.png" style="width:100%;image-rendering:pixelated" alt="그림자까지 넓었던 문·회색 벽선 정렬 닫힘·열림"><p>141벽 연결·홀로홈 고유 입구·실제 지형은 유지합니다.</p>'+html.slice(b);fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>회색 벽선과 문틀 정렬</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>문틀 오른쪽을 회색 벽선에 맞추기</h1><p>왼쪽은 그대로 · 문틀은 회색 벽 끝까지 · 오른쪽4px는 그림자로 연결. 높이와 두 방향 동일 크기는 유지합니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">세로벽 문에서 탐험</a> · <a href="./?seed=F1-mw8yvehm&door=horizontal">가로벽 문에서 탐험</a> · <a href="../doorfit143/door-review.html">이전143</a></p><img src="doors-comparison144.png" alt="이전143·회색 벽선 정렬 닫힘·열림 비교"><p>같은 지도·같은 두 문 자리의 브라우저 시안입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit143.cjs'),'utf8').replaceAll('143','144');fs.writeFileSync(path.join(R,'scripts/check-doorfit144.cjs'),test);
let exp=fs.readFileSync(path.join(R,'scripts/export-doorfit143.cjs'),'utf8').replaceAll('143','144').replace('for(const rev of [142,144])','for(const rev of [143,144])').replace("rev===142?'doorfit142':'doorfit144'","rev===143?'doorfit143':'doorfit144'").replace("['이전142','같은 크기로 수정 · 닫힘','같은 크기로 수정 · 열림']","['이전143 · 그림자까지 문틀','회색 벽선 정렬 · 닫힘','회색 벽선 정렬 · 열림']");fs.writeFileSync(path.join(R,'scripts/export-doorfit144.cjs'),exp);
console.log('Built144: gray frame0..27, separate right shadow28..31.');
