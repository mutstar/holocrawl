//153: one mirrored wall-return asset, not separately sized left/right extensions.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit152'),D=path.join(R,'preview/doorfit153');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const inputs=Object.fromEntries(['doors152.js','app152.js','generator152.js','materials152.js'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(S,n))).digest('hex')]));
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:153,base:152,inputs,scope:'Mirror the same left wall junction around the28px arch center; remove the horizontal-only one-sided shadow. No sprite or geometry changes.',checks:['actual left/right junction pixel symmetry in closed/open states','same door sprites','same48 maps and navigation/save/fog checks','same vertical review example','native4px sill exact','open passage pixels preserved']},null,2)+'\n');
for(const n of fs.readdirSync(path.join(S,'assets')))fs.copyFileSync(path.join(S,'assets',n),path.join(D,'assets',n));
for(const n of ['generator','materials','app'])fs.writeFileSync(path.join(D,n+'153.js'),fs.readFileSync(path.join(S,n+'152.js'),'utf8').replaceAll('152','153'));
let doors=fs.readFileSync(path.join(S,'doors152.js'),'utf8').replaceAll('152','153');
const start=doors.indexOf('function horizontalReturns('),end=doors.indexOf('function draw(',start);
doors=doors.slice(0,start)+`function horizontalReturns(q,m,d,base){
 if(!base||direction(m,d)!=='horizontal')return;
 const x=d.x*32,y=d.y*32,left=document.createElement('canvas');left.width=22;left.height=36;
 const g=left.getContext('2d');g.imageSmoothingEnabled=false;
 // Eight pixels of real wall plus the left half of the arch shoulder.
 // Use the same dimensions/source for both sides, including the reveal shading.
 g.drawImage(base,x-8,y,8,36,0,0,8,36);
 const p=capProfile(m,d,base);
 for(let px=0;px<14;px++){
  const top=Math.max(0,archTop(px)-4);
  if(top>0)g.drawImage(base,x-1,y,1,top,px+8,0,1,top);
  const h=Math.min(p.h,top);
  if(h>0)g.drawImage(p.image,p.sx,p.sy+p.h-h,1,h,px+8,top-h,1,h);
 }
 q.drawImage(left,x-8,y);
 // Mirror around the actual arch center13.5; the32px tile includes4px padding.
 q.save();q.translate(x+36,y);q.scale(-1,1);q.drawImage(left,0,0);q.restore();
}
`+doors.slice(end);
doors=doors.replace("for(let dx=0;dx<4;dx++){q.fillStyle=", "if(direction(m,d)!=='horizontal')for(let dx=0;dx<4;dx++){q.fillStyle=");
fs.writeFileSync(path.join(D,'doors153.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('152','153');html=html.replace('양옆 벽을 아치 문틀까지 연결','좌우 같은 모양으로 아치 문틀 연결');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>153 · 좌우 같은 벽 접합부</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1200px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>문틀 좌우 같은 접합부</h1><p>같은 벽 접합부를 좌우 반전하여 폭·높이·꺾이는 위치를 맞췄습니다. 오른쪽에만 있던 추가4px와 그림자를 따로 붙이지 않습니다.</p><img src="horizontal-wall153.png" alt="좌우 같은 벽 연결 닫힘·열림"><p><a href="./?seed=F1-mw8yvehm&door=horizontal">직접 이동</a> · <a href="../doorfit152/door-review.html">이전152</a></p><details><summary>151과 비교</summary><img src="doors-comparison153.png"></details></main></html>\n');
fs.writeFileSync(path.join(R,'scripts/check-doorfit153.cjs'),fs.readFileSync(path.join(R,'scripts/check-doorfit152.cjs'),'utf8').replaceAll('152','153'));
let exp=fs.readFileSync(path.join(R,'scripts/export-doorfit152.cjs'),'utf8').replaceAll('152','153').replace('},151+n);','},n===0?151:153);');
exp=exp.replace('return{pair:sheet',`const junctionChecks=[];for(const [state,rgba]of [['closed',now],['open',newOpen]])for(const d of horiz){let diff=0,pixels=0;
   const same=(lx,rx,y)=>{const li=((d.y*32+y)*c.width+d.x*32+lx)*4,ri=((d.y*32+y)*c.width+d.x*32+rx)*4;pixels++;for(let k=0;k<4;k++)if(rgba[li+k]!==rgba[ri+k])diff++;};
   for(let j=0;j<8;j++)for(let y=0;y<36;y++)same(-8+j,35-j,y);
   for(let x=0;x<14;x++)for(let y=0;y<Math.max(0,DoorFit153.archTop(x)-4);y++)same(x,27-x,y);
   junctionChecks.push({state,id:d.id,pixels,componentDifferences:diff});
  }
  return{junctionChecks,pair:sheet`);
exp=exp.replace('assert(result.changedPixels>0);',"for(const j of result.junctionChecks)assert.equal(j.componentDifferences,0,'asymmetric junction '+j.id+'/'+j.state);assert(result.changedPixels>0);");
fs.writeFileSync(path.join(R,'scripts/export-doorfit153.cjs'),exp);
console.log('Built153 mirrored wall-return layer;152 preserved.');
