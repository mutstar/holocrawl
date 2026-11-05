from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor03'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor02'/name,out/name)
shutil.copytree(root/'preview/city-floor02/assets',out/'assets',dirs_exist_ok=True)
src=root/'engine/upstream/crawl-ref/source/rltiles/dngn/gateways'
hashes={}
for kind in ['up','down']:
 p=src/f'stone_stairs_{kind}.png';dest=out/'assets'/f'crawl-stairs-{kind}.png';shutil.copyfile(p,dest);hashes[kind]=hashlib.sha256(dest.read_bytes()).hexdigest()
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace('const sources={',"const sources={crawlUp:'assets/crawl-stairs-up.png',crawlDown:'assets/crawl-stairs-down.png',");p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8');s='let useOriginalStairs=true;\n'+s;s=s.replace('function groundStair(c,up,px,py,t){',"function groundStair(c,up,px,py,t){if(useOriginalStairs){c.save();c.imageSmoothingEnabled=false;c.drawImage(up?images.crawlUp:images.crawlDown,px,py,t,t);c.restore();return;}")
s+="\n$('stairStyle').onclick=()=>{useOriginalStairs=!useOriginalStairs;$('stairStyle').textContent=useOriginalStairs?'기존 원형 계단과 비교':'돌죽 원본 계단으로 보기';draw();};\n"
p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 계단 확대','잔향도시 1층 · 돌죽 원본 계단').replace('위·아래 계단의 투명 여백을 줄여 한 칸을 더 꽉 채우게 키웠습니다. 소품 배치는 이전과 같습니다.','같은 맵에서 위·아래 계단만 돌죽 0.34.1 원본 32×32 PNG로 바꿨습니다. 원형 계단과 버튼으로 비교할 수 있습니다.').replace('<button id="overview">','<button id="stairStyle">기존 원형 계단과 비교</button><button id="overview">');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor02','change':'unaltered upstream DCSS0.34.1 stairs shown on same city map','source':'engine/upstream/crawl-ref/source/rltiles/dngn/gateways/stone_stairs_{up,down}.png','sha256':hashes,'rawPNGSize':[32,32],'extraShadowOnOriginalStairs':False,'logicalFootprint':[1,1],'nativeGameApplied':False},indent=2),encoding='utf-8')
check=(root/'scripts/check-city-floor02.cjs').read_text(encoding='utf-8').replace('city-floor02','city-floor03')
check=check.replace("await p.selectOption('#mapSelect','1');const shots=[];", "await p.selectOption('#mapSelect','1');await p.locator('#stairStyle').click();assert(await p.evaluate(()=>!useOriginalStairs));await p.locator('#stairStyle').click();assert(await p.evaluate(()=>useOriginalStairs));const shots=[];")
(root/'scripts/check-city-floor03.cjs').write_text(check,encoding='utf-8')
print(out)
