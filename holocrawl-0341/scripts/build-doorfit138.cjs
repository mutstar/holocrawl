const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit137'),D=path.join(R,'preview/doorfit138');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const name of ['generator','materials','app']){let s=fs.readFileSync(path.join(S,name+'137.js'),'utf8').replaceAll('137','138');fs.writeFileSync(path.join(D,name+'138.js'),s);}
fs.writeFileSync(path.join(D,'doors138.js'),`(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 // Only the doorway between north/south wall tiles gains a continuous outer frame.
 q.fillStyle='#2d3b39';q.fillRect(x,y,32,32);q.drawImage(base,x+2,y+2,28,28,x+2,y+2,28,28);
 q.fillStyle='#859791';q.fillRect(x,y,32,2);q.fillRect(x,y,2,32);q.fillRect(x+30,y,2,32);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+2,y,28,32);
}root.DoorFit138={solids,direction,draw};})(globalThis);`);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('137','138');
html=html.replace('일반 문 · 높아진 벽과 연결 맞추기','세로벽 사이 문만 · 문틀 연결 수정');
const a=html.indexOf('<h2>같은 지도'),b=html.indexOf('<footer>',a);
html=html.slice(0,a)+'<h2>세로벽 사이 문 · 좌우로 통과하는 자리</h2><p>위·아래로 이어진 세로벽 사이 문만 수정했습니다. 가로벽 사이 문은136 원래 모습으로 되돌렸습니다.</p><img src="doors-comparison138.png" style="width:100%;image-rendering:pixelated" alt="세로벽 사이 문 이전·수정·열림 비교"><p>홀로홈 고유 입구·내부·지형·가로벽 문은 그대로입니다.</p>'+html.slice(b);
fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>세로벽 사이 문만 수정</title><style>body{margin:0;background:#17201f;color:#dfe9df;font:16px/1.6 system-ui}main{max-width:1380px;margin:auto;padding:20px}h1{font-size:25px;margin:0}p{color:#b7c8bd;margin:8px 0}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>세로벽 사이 문 · 좌우로 통과하는 자리</h1><p>위·아래 벽에 문틀이 이어지도록 이 방향만 수정. 가로벽 문은 원래대로 복원했습니다.</p><p><a href="./?seed=F1-mw8yvehm&door=vertical">같은 문에서 직접 탐험 →</a> · <a href="./?seed=F1-mw8yvehm&door=horizontal">가로벽 문 원래 모습 확인</a></p><img src="doors-comparison138.png" alt="세로벽 사이 문 이전·수정·열림 비교"><p>같은1층의 같은 문을 비교한 브라우저 시안입니다.</p></main></html>');
let test=fs.readFileSync(path.join(R,'scripts/check-doorfit137.cjs'),'utf8').replaceAll('137','138');fs.writeFileSync(path.join(R,'scripts/check-doorfit138.cjs'),test);
console.log('Built138: vertical-wall doors only, horizontal restored.');
