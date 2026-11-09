const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/holohome136'),D=path.join(R,'preview/doorfit137');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
fs.writeFileSync(path.join(D,'generator137.js'),fs.readFileSync(path.join(S,'generator136.js'),'utf8').replaceAll('136','137'));
fs.writeFileSync(path.join(D,'materials137.js'),fs.readFileSync(path.join(S,'materials136.js'),'utf8').replaceAll('136','137'));
fs.writeFileSync(path.join(D,'doors137.js'),`(function(root){'use strict';const maps=new WeakMap();
function solids(m){if(maps.has(m))return maps.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='horizontal')a[d.y*m.w+d.x]=0;maps.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='vertical'){q.fillStyle='#2d3b39';q.fillRect(x,y,32,32);q.drawImage(base,x+2,y+2,28,28,x+2,y+2,28,28);q.fillStyle='#859791';q.fillRect(x,y,32,2);q.fillRect(x,y,2,32);q.fillRect(x+30,y,2,32);q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+2,y,28,32);return;}
 // Ordinary doors are structural openings. Include them when adjoining wall silhouettes are selected.
 WallHeight121.wall(q,solids(m),m.w,m.h,d.x,d.y,32,0);
 // Cut the aperture back to the original floor, retaining the wall shoulders and lintel.
 q.drawImage(base,x+4,y+11,24,21,x+4,y+11,24,21);
 q.fillStyle='#273431';q.fillRect(x+2,y+10,2,22);q.fillRect(x+28,y+10,2,22);
 q.fillStyle='#859791';q.fillRect(x+3,y+10,1,22);q.fillRect(x+28,y+10,1,22);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+3,y+10,26,22);
}
root.DoorFit137={solids,direction,draw};})(globalThis);`);
let app=fs.readFileSync(path.join(S,'app136.js'),'utf8').replaceAll('136','137');
app=app.replace('function background(m){const c=', 'function background(m){const structural=DoorFit137.solids(m);const c=');
app=app.replace('WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32,0)','WallHeight121.wall(q,structural,m.w,m.h,x,y,32,0)');
app=app.replace('for(const d of m.doors)g.drawImage(d.home?HomeMaterial137.door(v.opened.has(d.id)):v.opened.has(d.id)?im.opened:im.closed,d.x*32,d.y*32);',"for(const d of m.doors){if(d.home)g.drawImage(HomeMaterial137.door(v.opened.has(d.id)),d.x*32,d.y*32);else DoorFit137.draw(g,m,d,v.opened.has(d.id),im,v.base);}");
app=app.replace("$('generate').onclick=generate;", "$('doorH').onclick=()=>doorFocus('horizontal');$('doorV').onclick=()=>doorFocus('vertical');$('doorToggle').onclick=()=>{const v=get(),d=v.map.doors.filter(d=>!d.home).sort((a,b)=>Math.max(Math.abs(a.x-v.player.x),Math.abs(a.y-v.player.y))-Math.max(Math.abs(b.x-v.player.x),Math.abs(b.y-v.player.y)))[0];if(d){if(v.opened.has(d.id))v.opened.delete(d.id);else v.opened.add(d.id);draw();save();}};function doorFocus(direction){current=1;const m=get().map,d=m.doors.find(d=>!d.home&&DoorFit137.direction(m,d)===direction);if(d){const p=dirs.map(([dx,dy])=>({x:d.x+dx,y:d.y+dy})).find(p=>p.x>=0&&p.y>=0&&p.x<m.w&&p.y<m.h&&m.open[p.y*m.w+p.x]);if(p)focus(p);}}$('generate').onclick=generate;");
app=app.replace("if(params.get('seed'))$('seed').value=params.get('seed');generate();","if(params.get('seed'))$('seed').value=params.get('seed');generate();if(params.get('door'))doorFocus(params.get('door'));");
fs.writeFileSync(path.join(D,'app137.js'),app);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('136','137');
html=html.replace('홀로홈 · 기존 아치 입구 유지·작은 TV','일반 문 · 높아진 벽과 연결 맞추기');
html=html.replace('<div class="bar"><button id="home"', '<div class="bar"><button id="doorH">가로벽 문</button><button id="doorV">세로벽 문</button><button id="doorToggle">가까운 문 열기/닫기</button><button id="home"');
html=html.replace('value="HOME-20261109"','value="F1-mw8yvehm"');
html=html.replace('<script src="app137.js">','<script src="doors137.js"></script><script src="app137.js">');
// Existing source page has the app tag after the shared scripts.

const a=html.indexOf('<div class="cards">'),b=html.indexOf('<footer>',a);
html=html.slice(0,a)+'<h2>같은 지도 · 문 높이와 연결 전후</h2><p>가로벽 문은22px 벽면에 맞추고, 세로벽 문은32px 통로의 위·아래 벽에 문틀을 이어 붙였습니다. 가로벽·세로벽 모두 정면으로 읽히는 기존 철문 모양을 사용합니다.</p><p><a href="doors-comparison137.png">닫힘·열림과 이전 모습 비교 확대</a> · <a href="random-floor-review.html">같은 랜덤1층 전체 지도</a></p><img src="doors-comparison137.png" style="width:100%;image-rendering:pixelated" alt="가로벽과 세로벽의 일반 문 이전·수정·열림 비교"><p>홀로홈 고유 아치 입구·내부 도트·지형·문 위치·충돌·턴 규칙은 그대로입니다.</p>'+html.slice(b);
html=html.replace('href="prompts.json"','href="../holohome136/prompts.json"');
html=html.replace('href="random-floor-review.html"','href="random-floor-review.html"');
fs.writeFileSync(path.join(D,'index.html'),html);
console.log('Built doorfit137.');
