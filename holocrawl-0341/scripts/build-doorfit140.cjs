const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit139'),D=path.join(R,'preview/doorfit140');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app'])fs.writeFileSync(path.join(D,name+'140.js'),fs.readFileSync(path.join(S,name+'139.js'),'utf8').replaceAll('139','140'));
fs.writeFileSync(path.join(D,'doors140.js'),`(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 q.drawImage(base,x,y,32,32,x,y,32,32);
 // North/south wall ends anchor the portal; the leaves are viewed obliquely along the wall.
 q.fillStyle='#293735';q.fillRect(x,y,32,3);q.fillRect(x,y+29,32,3);
 q.fillStyle='#70837e';q.fillRect(x,y,32,1);q.fillRect(x,y+29,32,1);
 q.fillStyle='#9aa9a1';q.fillRect(x+10,y+1,5,2);q.fillRect(x+10,y+29,5,2);
 if(opened){
  // Both leaves swing east at the two hinges, clearing the left/right passage in the centre.
  for(const yy of [2,25]){q.fillStyle='#233333';q.fillRect(x+12,y+yy,17,5);q.fillStyle='#637e7f';q.fillRect(x+13,y+yy,14,3);q.fillStyle='#9aacaa';q.fillRect(x+13,y+yy,14,1);q.fillStyle='#3d646c';q.fillRect(x+16,y+yy+1,9,1);q.fillStyle='#344b4a';q.fillRect(x+14,y+yy+3,14,1);}
 }else{
  q.fillStyle='rgba(0,0,0,.28)';q.fillRect(x+23,y+3,3,26);
  for(const yy of [2,17]){q.fillStyle='#263937';q.fillRect(x+10,y+yy,14,13);q.fillStyle='#6f8988';q.fillRect(x+12,y+yy,10,12);q.fillStyle='#a1b2aa';q.fillRect(x+12,y+yy,1,12);q.fillRect(x+13,y+yy,8,1);q.fillStyle='#34535b';q.fillRect(x+14,y+yy+2,6,7);q.fillStyle='#4d747b';q.fillRect(x+15,y+yy+3,4,5);q.fillStyle='#334a4b';q.fillRect(x+21,y+yy+1,2,11);}
  q.fillStyle='#c2b88d';q.fillRect(x+18,y+14,3,1);q.fillRect(x+18,y+17,3,1);
 }
}root.DoorFit140={solids,direction,draw};})(globalThis);`);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('139','140').replace('세로벽 사이 문 · 가로 문틀 형태 시안','세로벽 사이 문 · 옆면 양문 시안');
const a=html.indexOf('<h2>세로벽 사이 문'),b=html.indexOf('<footer>',a);html=html.slice(0,a)+'<h2>벽 방향에 맞춘 옆면 양문</h2><p>가로 문틀 대신 위·아래 벽을 잇는 세로 방향 문짝입니다. 열리면 위·아래 끝으로 문짝이 접혀 가운데 좌우 통로를 비웁니다.</p><img src="doors-comparison140.png" style="width:100%;image-rendering:pixelated" alt="이전 정면 문·새 옆면 양문 닫힘·열림"><p>실제 문 위치·충돌·이동·시야 규칙은 기존과 같습니다.</p>'+html.slice(b);fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>세로벽 문 · 옆면 양문</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>세로벽에 맞춰 옆에서 보는 양문</h1><p>정면 문 위에 보를 얹는 대신, 위·아래 벽을 잇는 세로 문짝. 열리면 양 끝으로 접혀 좌우 통로가 드러납니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">이 문에서 직접 탐험 →</a> · <a href="../doorfit139/door-review.html">이전 가로 문틀 시안</a></p><img src="doors-comparison140.png" alt="이전 정면 문·옆면 양문 닫힘·열림 비교"><p>가로벽 문과 홀로홈 고유 입구·지형은 그대로입니다. 현재는 미술 검토용 브라우저 시안입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit139.cjs'),'utf8').replaceAll('139','140');fs.writeFileSync(path.join(R,'scripts/check-doorfit140.cjs'),test);
let exp=fs.readFileSync(path.join(R,'scripts/export-doorfit139.cjs'),'utf8').replaceAll('139','140').replace('for(const rev of [138,140])','for(const rev of [139,140])').replace("rev===138?'doorfit138':'doorfit140'","rev===139?'doorfit139':'doorfit140'").replace("['이전138','가로 문틀 형태 · 닫힘','가로 문틀 형태 · 열림']","['이전139 · 정면 문','옆면 양문 · 닫힘','옆면 양문 · 열림']");fs.writeFileSync(path.join(R,'scripts/export-doorfit140.cjs'),exp);
console.log('Built140 side-view double doors along vertical walls.');
