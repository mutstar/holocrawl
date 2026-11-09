//159: separate the32px metal door from the native wall's own coping line.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit157'),D=path.join(R,'preview/doorfit159');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const inputs=Object.fromEntries(['doors157.js','app157.js','generator157.js','materials157.js'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(S,n))).digest('hex')]));
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:159,base:157,inputs,scope:'Remove the door rail. Draw the real wall tile below a vertical doorway with its native north-facing coping exposed. Preserve above-wall connection and32px metal sprite. Native wall atlas and physical map unchanged.',checks:['same32px metal sprites','lower wall tile equals independent native atlas rendering','no door draw below tile','pixel changes confined to removed bottom4 rows and actual wall tiles below vertical doors','same48 maps and interactions','same158 whole-map geometry']},null,2)+'\n');
for(const n of fs.readdirSync(path.join(S,'assets')))fs.copyFileSync(path.join(S,'assets',n),path.join(D,'assets',n));
for(const n of ['generator','materials','app'])fs.writeFileSync(path.join(D,n+'159.js'),fs.readFileSync(path.join(S,n+'157.js'),'utf8').replaceAll('157','159'));
const appPath=path.join(D,'app159.js');fs.writeFileSync(appPath,fs.readFileSync(appPath,'utf8').replace('WallHeight121.wall(q,structural,m.w,m.h,x,y,32,0)','WallHeight121.wall(q,DoorFit159.wallCells(m,x,y),m.w,m.h,x,y,32,0)'));
let doors=fs.readFileSync(path.join(S,'doors157.js'),'utf8').replaceAll('157','159');
doors=doors.replace('function direction(m,d)',`const lowerWallMasks=new WeakMap();
function wallCells(m,x,y){
 if(!lowerWallMasks.has(m)){
  const mask=solids(m).slice(),below=new Set();
  for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical'){
   mask[d.y*m.w+d.x]=1;below.add((d.y+1)*m.w+d.x);
  }
  lowerWallMasks.set(m,{mask,below});
 }
 const info=lowerWallMasks.get(m);return info.below.has(y*m.w+x)?info.mask:solids(m);
}
function direction(m,d)`);
doors=doors.replace(' const p=capProfile(m,d,base);q.drawImage(p.image,p.sx,p.sy,1,p.h,x,y+32-p.h,28,p.h);',' // Native wall coping is already in base; do not paint a second rail across the door.');
doors=doors.replace('wallSill:{w:28,h:"native-wall-cap",yOffset:"32-native-height",insideTile:true,source:"actual native wall pixels; no independent thickness"}', 'wallSill:null,wallLineSource:"adjacent native wall in base; no independent door sill"');
doors=doors.replace('={solids,direction,draw,','={solids,wallCells,direction,draw,');
fs.writeFileSync(path.join(D,'doors159.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('157','159').replace('문 아래 돌출 제거','문 밑선과 벽 테두리 중복 제거');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>159 · 문 밑선과 벽선 분리</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1280px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>문에 덧그린 밑선을 빼고 원래 벽선에 연결</h1><p>문 높이·위치·금속 도트는 그대로32px입니다. 아래 벽에 이미 있는 테두리를 사용하고, 문 안쪽에 그리던 두 번째 회색 받침은 없앴습니다.</p><img src="height-comparison159.png" alt="이전 중복 밑선·원래 벽선 사용 닫힘·열림"><p><a href="full-map.html">같은 전체 지도</a> · <a href="./?seed=CITY157-13ffd346&door=vertical">직접 이동</a> · <a href="../doorfit157/door-review.html">이전157</a></p></main></html>\n');
fs.writeFileSync(path.join(R,'scripts/check-doorfit159.cjs'),fs.readFileSync(path.join(R,'scripts/check-doorfit157.cjs'),'utf8').replaceAll('157','159'));
console.log('Built159: same32px metal sprite, no duplicate gray rail.');
