const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit138'),D=path.join(R,'preview/doorfit139');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app'])fs.writeFileSync(path.join(D,name+'139.js'),fs.readFileSync(path.join(S,name+'138.js'),'utf8').replaceAll('138','139'));
fs.writeFileSync(path.join(D,'doors139.js'),`(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 // The reference's low rectangular door is seated inside a full-height structural portal.
 // The lintel reaches the north wall; side piers meet the south wall. No world-cell changes.
 q.drawImage(base,x,y,32,32,x,y,32,32);
 q.fillStyle='#283634';q.fillRect(x,y,32,32);
 q.drawImage(base,x+4,y+10,24,22,x+4,y+10,24,22);
 q.fillStyle='#5f7372';q.fillRect(x+1,y+1,30,3);q.fillRect(x+1,y+4,3,28);q.fillRect(x+28,y+4,3,28);
 q.fillStyle='#99a8a1';q.fillRect(x,y,32,1);q.fillRect(x+1,y+1,30,1);q.fillRect(x+1,y+4,1,28);q.fillRect(x+30,y+4,1,28);
 q.fillStyle='#3b4e4e';q.fillRect(x+4,y+4,24,6);q.fillStyle='#768985';q.fillRect(x+4,y+8,24,2);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+3,y+10,26,22);
}root.DoorFit139={solids,direction,draw};})(globalThis);`);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('138','139');html=html.replace('세로벽 사이 문만 · 문틀 연결 수정','세로벽 사이 문 · 가로 문틀 형태 시안').replace('위·아래로 이어진 세로벽 사이 문만 수정했습니다. 가로벽 사이 문은136 원래 모습으로 되돌렸습니다.','참고 이미지처럼 넓은 가로 문틀과 양옆 기둥을 둘렀습니다. 문짝은22px 높이로 낮추고 위쪽 연결부는 문틀로 채웠습니다. 가로벽 문은 원래 모습 그대로입니다.');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>세로벽 문 · 가로 문틀 형태</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>세로벽 사이 문 · 참고 이미지의 가로 문틀 적용</h1><p>문 위에 넓은 가로 보, 양옆에 이어지는 프레임. 문짝은 낮게, 위·아래 벽까지 문틀로 연결한 시안입니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">이 문에서 직접 탐험 →</a> · <a href="../doorfit138/door-review.html">이전138</a></p><img src="doors-comparison139.png" alt="세로벽 문 이전138·가로 문틀 시안 닫힘·열림"><p>가로벽 문·홀로홈 고유 입구·지형·실제 통행 규칙은 그대로입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit138.cjs'),'utf8').replaceAll('138','139');fs.writeFileSync(path.join(R,'scripts/check-doorfit139.cjs'),test);
let exporter=fs.readFileSync(path.join(R,'scripts/export-doorfit138.cjs'),'utf8').replaceAll('138','139').replace('for(const rev of [136,139])','for(const rev of [138,139])').replace("rev===136?'holohome136':'doorfit139'","rev===138?'doorfit138':'doorfit139'").replace("['이전 문','벽 높이·연결 수정','수정한 문 · 열림']","['이전138','가로 문틀 형태 · 닫힘','가로 문틀 형태 · 열림']");fs.writeFileSync(path.join(R,'scripts/export-doorfit139.cjs'),exporter);
console.log('Built139 reference-like lintel and piers for vertical-wall doors only.');
