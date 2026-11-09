//32px door study: redraw shorter jambs/leaves; do not rescale the existing bitmap.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit153'),D=path.join(R,'preview/doorfit155');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const inputs=Object.fromEntries(['doors153.js','app153.js','generator153.js','materials153.js'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(S,n))).digest('hex')]));
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:155,base:153,inputs,height:32,bodyBottom:32,sillBottom:36,scope:'32px sprite anchored at tile y0; same28px width and10px arch curve, mirrored wall returns, original4px wall sill. Redraw shortened leaves and hardware positions; no bitmap scaling.',checks:['same48 maps and interactions','outside side junctions exact153 pixels','actual sill exact153/native profile','left/right joins mirror exactly','sprite32x32/opaque closed aperture/mirrored leaf details','changes confined to ordinary door neighborhoods','common open passage pixels preserved']},null,2)+'\n');
for(const n of fs.readdirSync(path.join(S,'assets')))fs.copyFileSync(path.join(S,'assets',n),path.join(D,'assets',n));
for(const n of ['generator','materials','app'])fs.writeFileSync(path.join(D,n+'155.js'),fs.readFileSync(path.join(S,n+'153.js'),'utf8').replaceAll('153','155'));
let doors=fs.readFileSync(path.join(S,'doors153.js'),'utf8').replaceAll('153','155');
const start=doors.indexOf('function sprite('),end=doors.indexOf('const capCache=',start);
doors=doors.slice(0,start)+`function sprite(opened){
 if(sprites.has(opened))return sprites.get(opened);
 const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 // Same28px span and10px curve: keep the arch/rivets sharp at native pixel size.
 for(let x=0;x<28;x++){const y=archTop(x);q.fillStyle='#65757b';q.fillRect(x,y,1,32-y);q.fillStyle='#96a4a7';q.fillRect(x,y+1,1,2);q.fillStyle='#c3cbc7';q.fillRect(x,y,1,1);}
 q.fillStyle='#7c888d';q.fillRect(0,archTop(0)+1,1,31-archTop(0));q.fillStyle='#747d81';q.fillRect(27,archTop(27)+1,1,31-archTop(27));
 q.fillStyle='#d0d4cb';for(const x of [3,8,19,24])q.fillRect(x,archTop(x)+1,1,1);for(const y of [16,27]){q.fillRect(1,y,1,1);q.fillRect(26,y,1,1);}
 q.save();q.beginPath();q.moveTo(2,32);q.lineTo(2,openingTop(2));for(let x=2;x<26;x++){q.lineTo(x,openingTop(x));q.lineTo(x+1,openingTop(x));}q.lineTo(26,32);q.closePath();q.clip();q.clearRect(0,0,28,32);
 const leaf=document.createElement('canvas');leaf.width=opened?4:12;leaf.height=29;const p=leaf.getContext('2d');
 if(opened){p.fillStyle='#2a3c46';p.fillRect(0,0,4,29);p.fillStyle='#74898e';p.fillRect(0,0,1,27);p.fillStyle='#435f6d';p.fillRect(1,1,2,26);p.fillStyle='#aeb8b4';p.fillRect(2,18,1,3);}
 else{p.fillStyle='#35454e';p.fillRect(0,0,12,29);p.fillStyle='#75858c';p.fillRect(0,0,1,28);p.fillStyle='#22343a';p.fillRect(11,0,1,29);
  p.fillStyle='#263a44';p.fillRect(2,7,8,17);p.fillStyle='#445b66';p.fillRect(3,8,6,15);p.fillStyle='#607782';p.fillRect(3,8,1,14);
  for(const y of [10,21]){p.fillStyle='#243840';p.fillRect(0,y,11,3);p.fillStyle='#7f9096';p.fillRect(0,y,11,1);p.fillStyle='#4f666f';p.fillRect(0,y+1,11,1);p.fillStyle='#bdc5bf';p.fillRect(2,y+1,1,1);p.fillRect(8,y+1,1,1);}
  p.fillStyle='#293c42';p.fillRect(8,16,3,6);p.fillStyle='#aeb8b4';p.fillRect(9,17,2,4);p.fillStyle='#667575';p.fillRect(10,18,1,2);
 }
 q.drawImage(leaf,2,3);q.save();q.translate(26,3);q.scale(-1,1);q.drawImage(leaf,0,0);q.restore();q.restore();sprites.set(opened,c);return c;
}
`+doors.slice(end);
// Preserve the eight-pixel lateral return columns; only redraw the interior shoulder
// down to the new arch. No second coping strip is stacked over its new contour.
doors=doors.replace(' const p=capProfile(m,d,base);\n for(let px=0;px<14;px++){',' for(let px=0;px<14;px++){');
doors=doors.replaceAll('Math.max(0,archTop(px)-4)','archTop(px)');
doors=doors.replace('  const h=Math.min(p.h,top);\n  if(h>0)g.drawImage(p.image,p.sx,p.sy+p.h-h,1,h,px+8,top-h,1,h);\n','');
doors=doors.replace('q.drawImage(sprite(opened),x,y-4);','q.drawImage(sprite(opened),x,y);').replace('q.fillRect(x+28+dx,y+6,1,26);','q.fillRect(x+28+dx,y+10,1,22);').replace('w:28,h:36,canvasW:32,xOffset:0,yOffset:-4','w:28,h:32,canvasW:32,xOffset:0,yOffset:0');
fs.writeFileSync(path.join(D,'doors155.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('153','155').replaceAll('doors-comparison155.png','height-comparison155.png');html=html.replace('좌우 같은 모양으로 아치 문틀 연결','벽 높이에 맞춘32px 문').replace('좌우 벽 끝을 문틀로 이어 붙이고, 아치 바깥 어깨는 실제 옆 벽의 단면으로 채웠습니다. 은빛 아치·짙은 문짝·실제 벽과 같은 밑선은 유지합니다.','문 폭과 아치 곡률은 유지하고 기둥·문짝을32px에 맞춰 다시 그렸습니다. 밑선 위치와 실제4px 벽 도트, 좌우 접합은 유지합니다.');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>155 · 벽 높이에 맞춘32px 문</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1300px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>벽 높이에 맞춘32px 문</h1><p>아래 끝·실제4px 벽 밑선·좌우 접합을 유지하고, 문 높이를36→32px로 낮췄습니다. 폭과 아치 곡률은 그대로이며 문짝·손잡이·보강띠를 새 높이에 맞춰 다시 그렸습니다.</p><img src="height-comparison155.png" alt="이전36px·새32px 닫힘·열림, 양방향"><p><a href="./?seed=F1-mw8yvehm&door=horizontal">양옆 벽에서 이동</a> · <a href="./?seed=F1-mw8yvehm&door=vertical">위아래 벽에서 이동</a> · <a href="../doorfit153/door-review.html">이전153</a></p></main></html>\n');
fs.writeFileSync(path.join(R,'scripts/check-doorfit155.cjs'),fs.readFileSync(path.join(R,'scripts/check-doorfit153.cjs'),'utf8').replaceAll('153','155'));
console.log('Built155 redraw:32px body at y0,28px width/10px curve/native sill preserved.');
