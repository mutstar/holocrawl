const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit141'),D=path.join(R,'preview/doorfit142');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app'])fs.writeFileSync(path.join(D,name+'142.js'),fs.readFileSync(path.join(S,name+'141.js'),'utf8').replaceAll('141','142'));
let doors=fs.readFileSync(path.join(S,'doors141.js'),'utf8').replaceAll('141','142');
const a=doors.indexOf(' // Retain the front-facing door.'),b=doors.indexOf('\n}root.DoorFit',a);
doors=doors.slice(0,a)+` // Keep141 wall reveals. Recess the ordinary door inside the visible wall rails.
 q.save();q.beginPath();q.rect(x+3,y,26,32);q.clip();
 q.fillStyle='#2d3b39';q.fillRect(x+3,y,26,32);q.drawImage(base,x+5,y+2,22,28,x+5,y+2,22,28);
 q.fillStyle='#859791';q.fillRect(x+3,y,26,2);q.fillRect(x+3,y,1,32);q.fillRect(x+28,y,1,32);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+4,y,24,32);
 q.restore();`+doors.slice(b);
fs.writeFileSync(path.join(D,'doors142.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('141','142').replace('세로벽 문 · 위아래 벽 단면 맞추기','세로벽 문 · 벽선 안으로 문틀 맞추기');const c=html.indexOf('<h2>문 모양 유지'),e=html.indexOf('<footer>',c);html=html.slice(0,c)+'<h2>승인한 벽 연결 유지 · 문틀 돌출만 수정</h2><p>벽 단면은141과 동일합니다. 문틀 양옆을3px씩 안으로 넣고 문짝을24px 폭으로 맞췄습니다. 닫힘과 열림 모두 같은 범위 안에 그립니다.</p><img src="doors-comparison142.png" style="width:100%;image-rendering:pixelated" alt="기존 돌출·문틀 폭 수정 닫힘·열림"><p>벽 연결·가로문·홀로홈·실제 통행은 그대로입니다.</p>'+html.slice(e);fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>문틀 돌출만 수정</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>벽 연결은 유지 · 문틀 돌출만 수정</h1><p>문틀 양옆을3px씩 벽선 안으로 넣었습니다. 기존 벽 단면·높이는 그대로입니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">이 문에서 직접 탐험 →</a> · <a href="../doorfit141/door-review.html">수정 전141</a></p><img src="doors-comparison142.png" alt="이전 돌출·수정 닫힘·수정 열림"><p>같은 지도·같은 문 자리의 브라우저 미술 비교입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit141.cjs'),'utf8').replaceAll('141','142');fs.writeFileSync(path.join(R,'scripts/check-doorfit142.cjs'),test);
let exp=fs.readFileSync(path.join(R,'scripts/export-doorfit141.cjs'),'utf8').replaceAll('141','142').replace('for(const rev of [138,142])','for(const rev of [141,142])').replace("rev===138?'doorfit138':'doorfit142'","rev===141?'doorfit141':'doorfit142'").replace("['기존 · 위아래 두께 차이','연결부 단면 수정 · 닫힘','연결부 단면 수정 · 열림']","['이전141 · 문틀 돌출','문틀 폭 수정 · 닫힘','문틀 폭 수정 · 열림']").replace('Math.abs(Math.floor(x/32)-d.x)<=1&&Math.abs(Math.floor(y/32)-d.y)<=1','Math.floor(x/32)===d.x&&Math.floor(y/32)===d.y');fs.writeFileSync(path.join(R,'scripts/export-doorfit142.cjs'),exp);
console.log('Built142:141 wall reveals preserved; door-frame inset3px per side.');
