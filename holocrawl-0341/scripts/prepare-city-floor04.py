from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor04'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor03'/name,out/name)
shutil.copytree(root/'preview/city-floor03/assets',out/'assets',dirs_exist_ok=True)
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace('const sources={',"const sources={cityUp:'assets/city-stairs-up32.png',cityDown:'assets/city-stairs-down32.png',");p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8');a=s.index('function groundStair(');b=s.index("\n$('stairStyle')",a)
s=s[:a]+'''function groundStair(c,up,px,py,t){c.save();c.imageSmoothingEnabled=false;const im=useOriginalStairs?(up?images.cityUp:images.cityDown):(up?images.crawlUp:images.crawlDown);c.drawImage(im,px,py,t,t);c.restore();}
'''+s[b:];s=s.replace("useOriginalStairs?'기존 원형 계단과 비교':'돌죽 원본 계단으로 보기'", "useOriginalStairs?'돌죽 원본과 비교':'도시 수정안으로 보기'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 돌죽 원본 계단','잔향도시 1층 · 콘크리트 계단 초안').replace('같은 맵에서 위·아래 계단만 돌죽 0.34.1 원본 32×32 PNG로 바꿨습니다. 원형 계단과 버튼으로 비교할 수 있습니다.','돌죽 원본의 직선 계단을 기준으로 회색 콘크리트 재질을 입힌 수정안입니다. 같은 맵에서 원본과 비교하세요.').replace('기존 원형 계단과 비교','돌죽 원본과 비교');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor03','purpose':'urban concrete stair reskin draft compared with unaltered original DCSS stairs','mapAndPlacementUnchanged':True,'artMode':'built-in imagegen edits; downsampled for native32px use','nativeGameApplied':False},indent=2),encoding='utf-8')
print(out)
