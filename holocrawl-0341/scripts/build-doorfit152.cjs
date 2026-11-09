// Keep151 artwork immutable; fix only the horizontal wall-to-door reveal.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),S=path.join(R,'preview/doorfit151'),D=path.join(R,'preview/doorfit152');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const inputs=Object.fromEntries(['doors151.js','app151.js','generator151.js','materials151.js'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(S,n))).digest('hex')]));
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:152,base:151,inputs,scope:'Horizontal ordinary door wall returns only. Sprite, vertical example, map cells, collision, stairs, home and actual native engine stay unchanged.',checks:['same closed/open door sprite','48 maps geometry and interaction regression','before/after changes inside horizontal door neighborhoods only','vertical example pixels unchanged','native sill profile exact','horizontal closed/open difference inside door only']},null,2)+'\n');
for(const id of ['entrance','tv'])fs.copyFileSync(path.join(S,'assets',id+'-native.png'),path.join(D,'assets',id+'-native.png'));
for(const n of ['generator','materials','app'])fs.writeFileSync(path.join(D,n+'152.js'),fs.readFileSync(path.join(S,n+'151.js'),'utf8').replaceAll('151','152'));
let doors=fs.readFileSync(path.join(S,'doors151.js'),'utf8').replaceAll('151','152');
doors=doors.replace("if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;","if(!d.home)a[d.y*m.w+d.x]=0;");
const hook='function draw(q,m,d,opened,im,base)';
doors=doors.replace(hook,`function horizontalReturns(q,m,d,base){
 if(!base||direction(m,d)!=='horizontal')return;
 const x=d.x*32,y=d.y*32;
 // Join wall mass to the outside of the unchanged arch. Never cover the aperture.
 // Each return copies the actual neighboring wall edge at its original vertical scale.
 for(let px=0;px<32;px++){
  const top=px<28?Math.max(0,archTop(px)-4):32;
  const sx=px<14?x-1:x+32;
  if(top>0)q.drawImage(base,sx,y,1,top,x+px,y,1,top);
  if(px>=28)q.drawImage(base,sx,y,1,32,x+px,y,1,32);
 }
 // Mitre the native coping down to the curved shoulder, leaving no dark slit
 // between the straight wall rail and the unchanged silver arch.
 const p=capProfile(m,d,base);
 for(let px=0;px<32;px++){
  const end=px<28?Math.max(0,archTop(px)-4):Math.max(0,archTop(27)-4);
  const h=Math.min(p.h,end);
  if(h>0)q.drawImage(p.image,p.sx,p.sy+p.h-h,1,h,x+px,y+end-h,1,h);
 }
}
`+hook);
doors=doors.replace('const x=d.x*32,y=d.y*32;\n // Wall shoulders','const x=d.x*32,y=d.y*32;\n horizontalReturns(q,m,d,base);\n // Wall shoulders');
doors=doors.replace('solids,direction,draw,sprite,','solids,direction,draw,sprite,horizontalReturns,');
fs.writeFileSync(path.join(D,'doors152.js'),doors);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('151','152');html=html.replace('<h2>옆 벽 회색선을 두께 그대로 연결</h2>','<h2>양옆 벽을 아치 문틀까지 연결</h2>').replace('옆 벽의 실제 회색 테두리 픽셀을 문 밑에 그대로 이어줍니다. 밝은 윗줄 포함4px이며, 색·층별 명암·높이 비율을 따로 바꾸지 않습니다.','좌우 벽 끝을 문틀로 이어 붙이고, 아치 바깥 어깨는 실제 옆 벽의 단면으로 채웠습니다. 은빛 아치·짙은 문짝·실제 벽과 같은 밑선은 유지합니다.');fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'door-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>152 · 양옆 벽과 문틀 연결</title><style>body{background:#17201f;color:#dfe9df;font:16px/1.6 system-ui;margin:0}main{max-width:1200px;margin:auto;padding:20px}h1{font-size:25px}a{color:#a3d5c5}img{width:100%;height:auto;image-rendering:pixelated}</style><main><h1>양옆 벽과 아치 문틀 연결</h1><p>문 모양은 그대로 두고, 벽 끝과 아치 바깥을 실제 옆 벽 도트로 이어 붙였습니다.</p><img src="horizontal-wall152.png" alt="벽에 이어진 문 닫힘·열림"><p><a href="./?seed=F1-mw8yvehm&door=horizontal">이 문에서 직접 이동</a> · <a href="../doorfit151/horizontal-review.html">이전151</a></p><details><summary>수정 전후 비교</summary><img src="doors-comparison152.png" alt="이전151·수정152 닫힘·열림"></details></main></html>\n');
// Reuse the established meaningful geometry, navigation, save, fog and responsive checks.
fs.writeFileSync(path.join(R,'scripts/check-doorfit152.cjs'),fs.readFileSync(path.join(R,'scripts/check-doorfit151.cjs'),'utf8').replaceAll('151','152').replaceAll('()=>homeReady','()=>window.homeReady'));
console.log('Prepared152 horizontal wall returns; immutable151 retained.');
