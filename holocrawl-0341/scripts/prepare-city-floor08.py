from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor08'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor03'/name,out/name)
shutil.copytree(root/'preview/city-floor03/assets',out/'assets',dirs_exist_ok=True)
p=out/'grounding.js';s=p.read_text(encoding='utf-8');a=s.index('function groundStair(');b=s.index("\n$('stairStyle')",a)
s=s[:a]+'''function groundStair(c,up,px,py,t){c.save();c.imageSmoothingEnabled=false;const im=up?images.crawlUp:images.crawlDown;if(useOriginalStairs){c.translate(px+t,py);c.scale(-1,1);c.drawImage(im,0,0,t,t);}else c.drawImage(im,px,py,t,t);c.restore();}
'''+s[b:];s=s.replace("useOriginalStairs?'기존 원형 계단과 비교':'돌죽 원본 계단으로 보기'", "useOriginalStairs?'반전 전 원본과 비교':'좌우반전 계단으로 보기'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 돌죽 원본 계단','잔향도시 1층 · 원본 계단 좌우반전').replace('같은 맵에서 위·아래 계단만 돌죽 0.34.1 원본 32×32 PNG로 바꿨습니다. 원형 계단과 버튼으로 비교할 수 있습니다.','돌죽 0.34.1 원본 계단을 좌우만 반전했습니다. 오른쪽 상승·왼쪽 하강이며 원본의 색·질감·외곽선·32×32 크기는 그대로입니다.').replace('기존 원형 계단과 비교','반전 전 원본과 비교');p.write_text(s,encoding='utf-8')
upstream=root/'engine/upstream/crawl-ref/source/rltiles/dngn/gateways'
hashes={}
for kind in ['up','down']:
 source=upstream/f'stone_stairs_{kind}.png';target=out/'assets'/f'crawl-stairs-{kind}.png'
 assert source.read_bytes()==target.read_bytes()
 hashes[kind]=hashlib.sha256(source.read_bytes()).hexdigest()
(out/'revision.json').write_text(json.dumps({'previous':'city-floor07','selected':'DCSS0.34.1 original stairs with horizontal reflection only','sourceSha256':hashes,'sourceSize':[32,32],'recolor':False,'extraOutline':False,'extraShadow':False,'resample':False,'ascent':'right','descent':'left','terrainAndPlacementUnchanged':True,'nativeGameApplied':False},indent=2),encoding='utf-8')
s=(root/'scripts/check-city-floor07.cjs').read_text(encoding='utf-8').replace('city-floor07','city-floor08').replace('이전4단','원본').replace('거친5단 수정안','원본 좌우반전');(root/'scripts/check-city-floor08.cjs').write_text(s,encoding='utf-8')
print(out)
