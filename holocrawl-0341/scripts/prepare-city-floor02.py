from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor02'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor01'/name,out/name)
shutil.copytree(root/'preview/city-floor01/assets',out/'assets',dirs_exist_ok=True)
p=out/'grounding.js';s=p.read_text(encoding='utf-8');a=s.index('const stairMasks={};');s=s[:a]+s[a:].replace('const stairMasks={};','''const stairMasks={},enlargedStairs={};
function visibleStair(up){const key=up?'up':'down';if(enlargedStairs[key])return enlargedStairs[key];const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;
// Fill the tile by removing transparent margins; movement footprint remains one cell.
if(up)cc.drawImage(images.groundUp,4,1,24,30,1,0,30,32);
else cc.drawImage(images.groundDown,1,1,29,29,0,0,32,32);
return enlargedStairs[key]=c;}
''').replace('im=up?images.groundUp:images.groundDown','im=visibleStair(up)').replace('12*s,Math.PI*1.03','13*s,Math.PI*1.03');p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 공연장 앞 거리','잔향도시 1층 · 계단 확대').replace('상점 진열 한 곳과 벽가 소품 몇 개만 남겼습니다.','위·아래 계단의 투명 여백을 줄여 한 칸을 더 꽉 채우게 키웠습니다. 소품 배치는 이전과 같습니다.');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor01','change':'code-native stair display sizing only, unchanged PNGs and terrain/prop logic','upVisibleBefore':[24,30],'upVisibleAfter':[30,32],'downVisibleBefore':[29,29],'downVisibleAfter':[32,32],'logicalFootprint':[1,1],'nativeGameApplied':False},indent=2),encoding='utf-8')
print(out)
