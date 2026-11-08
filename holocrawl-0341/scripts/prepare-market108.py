"""Create a separate code-rendered market review using frozen native92 walls."""
from pathlib import Path
import json,re,shutil,hashlib
R=Path(__file__).resolve().parents[1];SRC=R/'preview/city-market02';OUT=R/'preview/city-market108'
OUT.mkdir(exist_ok=True)
files=[p for p in SRC.iterdir() if p.suffix in ['.js','.css','.html','.json'] and not p.name.endswith('validation.json')]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for p in files:shutil.copy2(p,OUT/p.name)
# Shared original bitmaps remain untouched. Rendering recolours only neutral
# fixture surfaces; member images and colours keep their original data.
for name in ['app.js','members.js','merch-catalog.js']:
 p=OUT/name;s=p.read_text(encoding='utf-8').replace("'assets/","'../city-market02/assets/").replace('"assets/','"../city-market02/assets/');p.write_text(s,encoding='utf-8')
source=R/'analysis/native-play107-01/engine/crawl-ref/source/rltiles/tiledef-wall.cc'
s=source.read_text();info=[tuple(map(int,v.split(','))) for v in re.findall(r'tile_info\((\d[^)]*)\)',s)]
tiles={}
for mask,var,n in re.findall(r'_name_pair\("holo_city_wall78_(\d+)_(\d+)", (\d+) \+ TILE_FLOOR_MAX\)',s):
 width,height,dx,dy,sx,sy,ex,ey=info[int(n)];assert width==height==32 and dx==dy==0
 tiles[f'{mask}:{var}']=[sx,sy,ex-sx,ey-sy]
assert len(tiles)==2048
(OUT/'wall92.json').write_text(json.dumps(tiles,separators=(',',':')))
p=OUT/'app.js';s=p.read_text(encoding='utf-8')
s=s.replace("ctx=canvas.getContext('2d')","ctx=canvas.getContext('2d',{willReadFrequently:true})")
s=s.replace("function draw(){", "function draw(){")
a=s.index('for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){const px=x*t,py=y*t;')
b=s.index('// Existing venue artwork',a)
old=s[a:b]
new="""if(Market108.isOld()){
OLD
}else{
 for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++){
  const px=x*t,py=y*t;
  if(stage!==0&&cells[y*map.w+x]!==G.WALL){const i=floorMode==='repeat'?0:RandomFloor.index(map.seed+'-F'+marketFloor,floorMix,x,y);ctx.drawImage(floorVariants[i],px,py,t,t);}
  else Market108.wall(ctx,cells,map.w,map.h,x,y,t,hash(x,y)%8);
 }
}
""".replace('OLD',old)
s=s[:a]+new+s[b:]
# Retire the old procedural wall units only in the new style. New wall
# fixtures provide coherent, inset storefront detail without extra collision.
s=s.replace("if(stage>=3){for(let y=1;y<map.h-1", "if(stage>=3&&Market108.isOld()){for(let y=1;y<map.h-1")
s=s.replace("for(const shop of map.marketWalls)MarketStock.draw(ctx,shop,map,images,t,stockMix);", "for(const shop of map.marketWalls)MarketStock.draw(ctx,shop,map,images,t,stockMix);")
s=s.replace("ctx.drawImage(images.fence,prop.x*t,prop.y*t+t*.31,t,t*.69)","ctx.drawImage((Market108.isOld()?images:Market108.images).fence,prop.x*t,prop.y*t+t*.31,t,t*.69)")
needle="texture([326,57,105,73],door.x*t,door.y*t,door.w*t,door.h*t);ctx.fillStyle='#bab1a0';ctx.fillRect(map.exit.x*t+t*.14,map.exit.y*t,t*.72,Math.max(1,t*.09));"
assert needle in s
s=s.replace(needle,"if(Market108.isOld()){ "+needle+" }else{Market108.exitDoor(ctx,door,t);}")
s=s.replace("MarketStock.makeSprites(images);MarketStock.gallery(images);", "Market108.prepare(images);MarketStock.makeSprites(images);MarketStock.gallery(images);")
s=s.replace("Promise.all(Object.entries(sources).map(async([k,src])=>{images[k]=await loadImage(src);})).then", "Promise.all([Market108.load(),...Object.entries(sources).map(async([k,src])=>{images[k]=await loadImage(src);})]).then")
s+="\ndocument.getElementById('compareOld').onchange=e=>{Market108.setOld(e.target.checked);MarketStock.gallery(images);draw();};\n"
p.write_text(s,encoding='utf-8')
p=OUT/'market-stock.js';s=p.read_text(encoding='utf-8');s=s.replace('ctx.drawImage(images[meta.id],x,y,w,t);',"""if(root.Market108&&!root.Market108.isOld()){
 const art=root.Market108.images[meta.id];
 if(meta.kind==='wall'){
  // Preserve the4px coping and continuous outside corners of material92.
  ctx.drawImage(art,x+4*scale,y+6*scale,w-8*scale,t-8*scale);
 }else ctx.drawImage(art,x,y,w,t);
}else ctx.drawImage(images[meta.id],x,y,w,t);""")
# Member overlays stay full colour, but sit inside the new inset frames.
s=s.replace("ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);", "ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);if(root.Market108&&!root.Market108.isOld()&&meta.kind==='wall'){ctx.translate(4,6);ctx.scale(56/64,24/32);}")
p.write_text(s,encoding='utf-8')
p=OUT/'catalog.js';s=p.read_text(encoding='utf-8').replace('MarketStock.makeSprites(images);','Market108.prepare(images);MarketStock.makeSprites(images);');p.write_text(s,encoding='utf-8')
p=OUT/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 · 상점가 소품20종','잔향도시 · 새 콘크리트 상점가108').replace('익숙한 도시 벽과 시멘트 바닥 위로 굿즈 상점·진열대·배송 상자가 들어섭니다. 진열장·상품 더미·배송·쓰레기 소품20종과 멤버별 랜덤 굿즈를 배치합니다.','확정 콘크리트 벽과 세로창 양개문에 맞춘 4~7층 상점가 시안입니다. 진열장·셔터·물류 소품은 청회색으로 맞추고, 멤버 굿즈와 종이 상자의 색은 남겼습니다.')
s=s.replace('<div class="districts">','<div class="reviewbar"><label><input type="checkbox" id="compareOld"> 수정 전02 비교</label><a href="buildings.html">상점 외관 3종 비교</a><a href="catalog.html">소품20종 크게 보기</a></div><div class="districts">')
s=s.replace('<script src="generator.js', '<script src="material108.js"></script><script src="generator.js')
s=s.replace('app.js?v=market02','app.js?v=108').replace('4~7층 도트·구조 초안 · 브라우저 검토용','벽92·문101·상점가108 · 기존 지도 구조 보존 · 브라우저 검토용 · 실제 엔진 적용 전')
p.write_text(s,encoding='utf-8')
p=OUT/'catalog.html';s=p.read_text(encoding='utf-8').replace('<script src="members.js', '<script src="material108.js"></script><script src="members.js');p.write_text(s,encoding='utf-8')
p=OUT/'style.css';s=p.read_text(encoding='utf-8');s+='\n:root{--bg:#141b20;--panel:#1d282e;--line:#45545c;--muted:#abb8be;--ink:#e0e8ea;--cyan:#a1c7d0}.reviewbar{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:18px 0}.reviewbar label{display:flex;align-items:center;gap:8px}.reviewbar input{width:auto}.reviewbar a,a{color:#b5d3dc}.floor-tabs .selected{border-color:#91aebc;background:#2f414b;color:#e1edf2}#propSwatches figure{background:#36434a}select{max-width:100%}\n';p.write_text(s,encoding='utf-8')
(OUT/'inputs.json').write_text(json.dumps({'revision':108,'wallRevision':92,'doorRevision':101,'oldFiles':before,'oldMap':'city-market02','sourceGeometryChanged':False,'nativeIntegrated':False},indent=2)+'\n')
print('Created market108 code review, preserving market02 and native engine.')
