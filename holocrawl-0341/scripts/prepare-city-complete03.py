from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-complete03'
out.mkdir(exist_ok=True)
(out/'assets').mkdir(exist_ok=True)
for name in ['index.html','terrain.js','app.js','boot.js','manifest.json']:
    (out/name).write_bytes((root/'preview/city-complete02'/name).read_bytes())
p=out/'index.html'
s=p.read_text(encoding='utf-8').replace('상점 앞과 골목으로 모은 소품','바닥에 붙는 굿즈와 계단')
s=s.replace('굿즈는 진열창 앞, 물류는 셔터 뒤편 적재 구역, 쓰레기는 벽 구석으로 모았습니다. 가운데 길은 비우고 기존 20종을 모두 유지한 검토용 배치입니다.','같은 도트 배치에서 매대 받침의 접촉 그림자와 바닥 마모를 보강하고, 계단을 시멘트 바닥에 연결했습니다. 수정 전후 버튼으로 비교하세요.')
s=s.replace('<button id="fit">','<button id="ground">수정 전과 비교</button><button id="fit">')
s=s.replace('<details><summary>', '<h2 style="font-size:18px">같은 자리 · 수정 전 / 수정 후</h2><p>왼쪽은 이전 모습, 오른쪽은 바닥 접점 수정입니다. 아래 그림은 위 맵에서 그대로 잘라 확대했습니다.</p><div class="scroll" style="overflow:auto"><canvas id="details" width="896" height="696" style="max-width:100%"></canvas></div><details><summary>')
s=s.replace('<script src="boot.js">','<script src="grounding.js"></script><script src="boot.js">')
p.write_text(s,encoding='utf-8')
p=out/'app.js'
s=p.read_text(encoding='utf-8').replace('mix=0;','mix=0,grounded=true;')
s=s.replace('for(const p of mounted)', 'if(grounded)groundFixtures();\nfor(const p of mounted)')
s=s.replace('for(const p of fixtures)MarketStock.draw(ctx,p,m,images,32,mix);','for(const p of fixtures){MarketStock.draw(ctx,p,m,images,32,mix);if(grounded)fixtureFeet(p);}')
s += '''
$('ground').onclick=()=>{grounded=!grounded;$('ground').textContent=grounded?'수정 전과 비교':'수정 후로 보기';draw();};
'''.replace('\n+','\n')
p.write_text(s,encoding='utf-8')
p=out/'terrain.js'
s=p.read_text(encoding='utf-8').replace("c.drawImage(isUp(f)?images.up:images.down,px,py,t,t);return;", "if(grounded)groundStair(c,isUp(f),px,py,t);else c.drawImage(isUp(f)?images.up:images.down,px,py,t,t);return;")
p.write_text(s,encoding='utf-8')
p=out/'boot.js'
s=p.read_text(encoding='utf-8').replace("const sources={", "const sources={groundUp:'assets/stairs-up-grounded32.png',groundDown:'assets/stairs-down-grounded32.png',")
s=s.replace('draw();gallery();window.completePreview=', 'draw();gallery();drawDetails();window.completePreview=')
p.write_text(s,encoding='utf-8')
(out/'grounding.js').write_text('''
// Terrain decoration is drawn in map space, separate from unchanged merchandise sprites.
function groundFixtures(){
 const aprons=[[26,3,5,2],[23,7,3,2],[29,17,4,2]];
 for(const[x,y,w,h]of aprons){const px=x*32,py=y*32;ctx.fillStyle='rgba(162,155,135,.075)';ctx.fillRect(px+3,py+2,w*32-6,h*32-5);ctx.fillStyle='rgba(25,28,24,.20)';ctx.fillRect(px+4,py+h*32-4,w*32-9,1);for(let a=0;a<w;a++){ctx.fillRect(px+a*32+2,py+5,1,h*32-13);ctx.fillStyle='rgba(170,165,148,.12)';ctx.fillRect(px+a*32+3,py+6,1,h*32-15);ctx.fillStyle='rgba(25,28,24,.20)';}}
 for(const p of fixtures){const meta=MerchCatalog.find(a=>a.id===p.type),px=p.x*32,py=p.y*32;if(meta.kind==='wall')continue;
  const loose=['paper-rubbish','trash-bags','shopping-bags','poster-rolls'].includes(p.type);
  ctx.fillStyle='rgba(21,24,20,.20)';ctx.fillRect(px+5,py+25,24,5);ctx.fillRect(px+8,py+30,17,1);
  ctx.fillStyle='rgba(155,148,127,.16)';for(let n=0;n<9;n++){const xx=3+(n*11+p.x*7)%27,yy=23+(n*7+p.y)%9;ctx.fillRect(px+xx,py+yy,1+(n%3===0?1:0),1);}
  if(!loose){ctx.fillStyle='rgba(15,18,15,.48)';ctx.fillRect(px+7,py+28,19,2);}
 }
}
function fixtureFeet(p){const a=MerchCatalog.find(a=>a.id===p.type);if(a.kind==='wall')return;const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');MarketStock.draw(cc,{type:p.type,x:0,y:0},m,images,32,mix);const d=cc.getImageData(0,0,32,32).data;let bottom=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(d[(y*32+x)*4+3]>128)bottom=Math.max(bottom,y);ctx.fillStyle='rgba(12,15,12,.52)';for(let x=0;x<32;x++)if(d[(bottom*32+x)*4+3]>128)ctx.fillRect(p.x*32+x,p.y*32+bottom+1,1,1);}
function groundStair(c,up,px,py,t){const s=t/32;c.save();
 // Worn mortar extends into the surrounding cement; no enclosing badge or platform.
 c.fillStyle='rgba(26,29,25,.33)';for(const[x,y,w,h]of [[5,25,20,3],[3,23,3,3],[24,21,3,4]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.fillStyle='rgba(146,140,125,.23)';for(const[x,y,w,h]of [[3,27,7,1],[9,29,11,1],[24,24,4,1],[5,6,3,1]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.drawImage(up?images.groundUp:images.groundDown,px,py,t,t);c.restore();}
function drawDetails(){const d=$('details'),c=d.getContext('2d'),old=grounded;c.imageSmoothingEnabled=false;c.fillStyle='#141c17';c.fillRect(0,0,d.width,d.height);const views=[{name:'굿즈 매대',x:26,y:2,w:5,h:5},{name:'올라가는 계단',x:3,y:5,w:5,h:3},{name:'내려가는 계단',x:18,y:23,w:5,h:3}];for(let row=0;row<3;row++){for(let j=0;j<2;j++){grounded=!!j;draw();const x=j*448+58,y=row*232+30;c.drawImage(canvas,views[row].x*32,views[row].y*32,160,96,x,y,320,192);c.fillStyle='#c8d8c9';c.font='14px sans-serif';c.fillText(views[row].name+' · '+(j?'수정 후':'수정 전'),x,y-10);}}grounded=old;draw();}
''',encoding='utf-8')
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
manifest.update({'purpose':'terrain contact and sprite grounding review','previous':'city-complete02','sameLayout':True,'merchandiseSpritesUnchanged':True,'stairArt':'built-in imagegen edits, transparent 32px derivatives','grounding':'canvas terrain wear, contact shadows and sprite base occlusion'})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
