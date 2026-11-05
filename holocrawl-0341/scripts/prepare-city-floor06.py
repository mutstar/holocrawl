from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor06'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor05'/name,out/name)
shutil.copytree(root/'preview/city-floor05/assets',out/'assets',dirs_exist_ok=True)
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace('const sources={',"const sources={approvedDown:'assets/city-stairs-down-final32.png',previousUp:'assets/city-stairs-up-final32.png',").replace("cityUp:'assets/outlined-stairs-up32.png'","cityUp:'assets/thick-stairs-up32.png'");p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8');a=s.index('function groundStair(');b=s.index("\n$('stairStyle')",a)
s=s[:a]+'''function groundStair(c,up,px,py,t){c.save();c.imageSmoothingEnabled=false;const im=up?(useOriginalStairs?outlinedCityStair(true):images.previousUp):images.approvedDown;c.drawImage(im,px,py,t,t);c.restore();}
'''+s[b:];s=s.replace("useOriginalStairs?'돌죽 원본과 비교':'방향·외곽선 수정안으로 보기'", "useOriginalStairs?'이전 얇은 계단과 비교':'두꺼운 4단 계단으로 보기'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 계단 방향과 외곽선','잔향도시 1층 · 올라가는 계단 4단').replace('올라가는 계단은 오른쪽으로, 내려가는 계단은 왼쪽으로 향하게 반전했습니다. 콘크리트 표면에 짙은 1픽셀 외곽선을 더했습니다.','올라가는 계단을 두꺼운 4단으로 줄였습니다. 오른쪽 상승과 검정 외곽선 유지, 내려가는 계단은 승인한05와 동일합니다.').replace('돌죽 원본과 비교','이전 얇은 계단과 비교');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor05','change':'ascending stair only, four thicker treads matching approved descending style','ascent':'right','descent':'left','approvedDownFile':'assets/city-stairs-down-final32.png','approvedDownSha256':hashlib.sha256((out/'assets/city-stairs-down-final32.png').read_bytes()).hexdigest(),'terrainAndPlacementUnchanged':True,'nativeGameApplied':False},indent=2),encoding='utf-8')
s=(root/'scripts/check-city-floor05.cjs').read_text(encoding='utf-8').replace('city-floor05','city-floor06').replace('돌죽 원본','이전05').replace('방향·외곽선 수정안','두꺼운4단 수정안');(root/'scripts/check-city-floor06.cjs').write_text(s,encoding='utf-8')
print(out)
