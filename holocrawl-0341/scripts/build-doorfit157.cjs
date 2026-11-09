//157 fixes the sill's position, not its thickness or the accepted32px metal artwork.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit155'),D=path.join(R,'preview/doorfit157');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const inputs=Object.fromEntries(['doors155.js','app155.js','generator155.js','materials155.js'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(S,n))).digest('hex')]));
const seed=JSON.parse(fs.readFileSync(path.join(R,'preview/city-random156/validation.json'),'utf8')).seed;
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:157,base:155,seed,inputs,scope:'Keep32px sprite; place native4px sill INSIDE tile rows28..31 instead of32..35. All overlays end at row31. Preserve side junctions within the tile; remove their extra4px tail.',checks:['isolated door draw cannot modify rows below tile for both states/directions','actual same-map sill edge ends at neighboring wall bottom','sill shading equals native wall profile','same metal sprite','same48 maps and navigation/save/fog','left/right joins match inside tile','same previous whole-map geometry']},null,2)+'\n');
for(const n of fs.readdirSync(path.join(S,'assets')))fs.copyFileSync(path.join(S,'assets',n),path.join(D,'assets',n));
for(const n of ['generator','materials','app'])fs.writeFileSync(path.join(D,n+'157.js'),fs.readFileSync(path.join(S,n+'155.js'),'utf8').replaceAll('155','157'));
let doors=fs.readFileSync(path.join(S,'doors155.js'),'utf8').replaceAll('155','157');
doors=doors.replace('left.width=22;left.height=36','left.width=22;left.height=32').replace('g.drawImage(base,x-8,y,8,36,0,0,8,36)','g.drawImage(base,x-8,y,8,32,0,0,8,32)');
doors=doors.replace('x,y+32,28,p.h','x,y+32-p.h,28,p.h').replace('yOffset:32,source:', 'yOffset:"32-native-height",insideTile:true,source:');
doors=doors.replace('// Copy the actual native gray rail profile at1:1 vertical scale: thickness and shading stay identical.','// The native rail replaces the final rows INSIDE the32px tile. Never append it below the wall.');
fs.writeFileSync(path.join(D,'doors157.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('155','157').replace('벽 높이에 맞춘32px 문','문 아래 돌출 제거');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>157 · 문 아래 돌출 제거</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1280px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>문 밑면을 벽 끝 안쪽에 맞추기</h1><p>32px 바깥에 붙던4px 밑선을 마지막4px 안으로 옮겼습니다. 문 아래로 추가되는 픽셀이 없고, 양옆 벽과 같은 높이에서 끝납니다.</p><img src="height-comparison157.png" alt="돌출된 기존 밑면·수정 닫힘·열림"><p><a href="full-map.html">같은 전체 지도</a> · <a href="./?seed='+seed+'&door=horizontal">직접 이동</a> · <a href="../doorfit155/door-review.html">이전155</a></p></main></html>\n');
fs.writeFileSync(path.join(R,'scripts/check-doorfit157.cjs'),fs.readFileSync(path.join(R,'scripts/check-doorfit155.cjs'),'utf8').replaceAll('155','157'));
console.log('Built157: native sill at32-height, all door overlays bounded to32px.');
