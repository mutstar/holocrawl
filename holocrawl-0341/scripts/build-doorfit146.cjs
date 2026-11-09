const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit145'),D=path.join(R,'preview/doorfit146');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app'])fs.writeFileSync(path.join(D,name+'146.js'),fs.readFileSync(path.join(S,name+'145.js'),'utf8').replaceAll('145','146'));
fs.writeFileSync(path.join(D,'doors146.js'),`(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
const archTop=x=>Math.round(10*(1-Math.sqrt(Math.max(0,1-Math.pow((x-13.5)/13.5,2))))),openingTop=x=>archTop(x)+3;
function sprite(opened){if(sprites.has(opened))return sprites.get(opened);const c=document.createElement('canvas');c.width=32;c.height=36;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 for(const [dx,color]of [[28,'#57696f'],[29,'#3c4f54'],[30,'#2c363c'],[31,'#2f393f']]){q.fillStyle=color;q.fillRect(dx,0,1,36);}
 // The existing dark wall material fills the two shoulders above the iron arch.
 q.fillStyle='#202629';q.fillRect(0,0,28,36);
 for(let x=0;x<28;x++){const y=archTop(x);q.fillStyle='#34474b';q.fillRect(x,y,1,36-y);q.fillStyle='#71848a';q.fillRect(x,y+1,1,2);q.fillStyle='#a5b0ad';q.fillRect(x,y,1,1);}
 q.fillStyle='#7c888d';q.fillRect(0,archTop(0)+1,1,35-archTop(0));q.fillStyle='#747d81';q.fillRect(27,archTop(27)+1,1,35-archTop(27));
 // An integer stair-step arch aperture preserves hard pixel edges.
 q.save();q.beginPath();q.moveTo(2,35);q.lineTo(2,openingTop(2));for(let x=2;x<26;x++){q.lineTo(x,openingTop(x));q.lineTo(x+1,openingTop(x));}q.lineTo(26,35);q.closePath();q.clip();q.clearRect(0,0,28,36);
 const leaf=document.createElement('canvas');leaf.width=opened?4:12;leaf.height=32;const p=leaf.getContext('2d');
 if(opened){p.fillStyle='#34454e';p.fillRect(0,0,4,32);p.fillStyle='#a0aaa8';p.fillRect(0,0,1,31);p.fillStyle='#687b82';p.fillRect(1,1,2,30);p.fillStyle='#c1bc9e';p.fillRect(2,21,1,3);}
 else{p.fillStyle='#55666f';p.fillRect(0,0,12,32);p.fillStyle='#87989c';p.fillRect(0,0,1,32);p.fillStyle='#273e45';p.fillRect(11,0,1,32);
  p.fillStyle='#354b56';p.fillRect(2,7,8,21);p.fillStyle='#627781';p.fillRect(3,8,6,19);p.fillStyle='#71858b';p.fillRect(3,8,1,18);
  for(const y of [10,25]){p.fillStyle='#354950';p.fillRect(0,y,11,3);p.fillStyle='#919c9c';p.fillRect(0,y,11,1);p.fillStyle='#6b7e83';p.fillRect(0,y+1,11,1);p.fillStyle='#c1c3b5';p.fillRect(2,y+1,1,1);p.fillRect(8,y+1,1,1);}
  p.fillStyle='#293c42';p.fillRect(8,19,3,6);p.fillStyle='#babca6';p.fillRect(9,20,2,4);p.fillStyle='#667575';p.fillRect(10,21,1,2);
 }
 q.drawImage(leaf,2,3);q.save();q.translate(26,3);q.scale(-1,1);q.drawImage(leaf,0,0);q.restore();q.restore();
 sprites.set(opened,c);return c;}
function draw(q,m,d,opened){q.drawImage(sprite(opened),d.x*32,d.y*32-4);}
root.DoorFit146={solids,direction,draw,sprite,archTop,openingTop,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:12,closedSeamWidth:2,closedSeamOpaque:true,mirroredInterior:true,grayRight:27,shadowStart:28,shadowWidth:4,archRise:10,material:'solid iron'}};})(globalThis);`);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('145','146').replace('양문 · 가운데 틈 채우기와 대칭 정리','아치형 철제 양문');const a=html.indexOf('<h2>닫힌 문 사이'),b=html.indexOf('<footer>',a);html=html.slice(0,a)+'<h2>완만한 아치 · 철판과 보강띠</h2><p>기존 폭·높이·회색 벽선 연결을 유지하고, 둥근 철제 문틀과 철판 양문으로 바꿨습니다. 양문 내부는 대칭이며 가운데는 더 진한 불투명 금속 이음선입니다.</p><img src="doors-comparison146.png" style="width:100%;image-rendering:pixelated" alt="사각문과 아치형 철문 닫힘·열림 비교"><p>가로·세로 모두 같은 도트이며 홀로홈 고유 입구는 유지합니다.</p>'+html.slice(b);fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>아치형 철제 양문</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>아치형 철제 양문</h1><p>회색 아치 문틀·철판·보강띠·리벳. 가운데 이음선은 더 진한 금속색이고 닫힌 문 안쪽은 불투명합니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">세로벽 문에서 탐험</a> · <a href="./?seed=F1-mw8yvehm&door=horizontal">가로벽 문에서 탐험</a> · <a href="../doorfit145/door-review.html">이전 사각문</a></p><img src="door-detail146.png" style="width:816px;max-width:100%" alt="사각문과 아치형 철문 확대 비교"><details open id="walls"><summary>벽과 이어진 두 방향 비교</summary><img src="doors-comparison146.png" alt="실제 지도에서 아치형 철문 닫힘·열림 비교"></details><p>폭·높이·오른쪽 그림자·기존 벽 연결과 실제 통행 규칙은 유지한 브라우저 시안입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit145.cjs'),'utf8').replaceAll('145','146');fs.writeFileSync(path.join(R,'scripts/check-doorfit146.cjs'),test);
let exp=fs.readFileSync(path.join(R,'scripts/export-doorfit145.cjs'),'utf8').replaceAll('145','146').replace('for(const rev of [144,146])','for(const rev of [145,146])').replace("rev===144?'doorfit144':'doorfit146'","rev===145?'doorfit145':'doorfit146'").replace("['이전144 · 가운데 틈','대칭·이음선 수정 · 닫힘','대칭·이음선 수정 · 열림']","['이전145 · 사각문','아치형 철문 · 닫힘','아치형 철문 · 열림']");fs.writeFileSync(path.join(R,'scripts/export-doorfit146.cjs'),exp);
console.log('Built146 arched solid-iron double doors with darker opaque seam.');
