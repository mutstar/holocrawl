from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor05'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor04'/name,out/name)
shutil.copytree(root/'preview/city-floor04/assets',out/'assets',dirs_exist_ok=True)
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace("cityUp:'assets/city-stairs-up32.png',cityDown:'assets/city-stairs-down32.png'", "cityUp:'assets/outlined-stairs-up32.png',cityDown:'assets/outlined-stairs-down32.png'");p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8');a=s.index('function groundStair(');b=s.index("\n$('stairStyle')",a)
s=s[:a]+'''const cityOutlined={};
function outlinedCityStair(up){const key=up?'up':'down';if(cityOutlined[key])return cityOutlined[key];const source=up?images.cityUp:images.cityDown,body=document.createElement('canvas');body.width=body.height=32;const bc=body.getContext('2d');bc.imageSmoothingEnabled=false;bc.drawImage(source,1,1,30,30);const mask=document.createElement('canvas');mask.width=mask.height=32;const mc=mask.getContext('2d');mc.drawImage(body,0,0);mc.globalCompositeOperation='source-in';mc.fillStyle='#0b0d0c';mc.fillRect(0,0,32,32);const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;for(const[dx,dy]of [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]])cc.drawImage(mask,dx,dy);cc.drawImage(body,0,0);return cityOutlined[key]=c;}
function groundStair(c,up,px,py,t){c.save();c.imageSmoothingEnabled=false;if(useOriginalStairs){c.translate(px+t,py);c.scale(-1,1);c.drawImage(outlinedCityStair(up),0,0,t,t);}else c.drawImage(up?images.crawlUp:images.crawlDown,px,py,t,t);c.restore();}
'''+s[b:];s=s.replace("'도시 수정안으로 보기'","'방향·외곽선 수정안으로 보기'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 콘크리트 계단 초안','잔향도시 1층 · 계단 방향과 외곽선').replace('돌죽 원본의 직선 계단을 기준으로 회색 콘크리트 재질을 입힌 수정안입니다. 같은 맵에서 원본과 비교하세요.','올라가는 계단은 오른쪽으로, 내려가는 계단은 왼쪽으로 향하게 반전했습니다. 콘크리트 표면에 짙은 1픽셀 외곽선을 더했습니다.');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor04','purpose':'mirror both stairs horizontally and add near-black outer contour','ascent':'right','descent':'left','outline':'1 native pixel; code-native canvas mask stroke preserves exact alpha boundary','sourceArt':'built-in imagegen outline edits; source kept before runtime mirror','terrainAndPlacementUnchanged':True,'logicalFootprint':[1,1],'nativeGameApplied':False},indent=2),encoding='utf-8')
s=(root/'scripts/check-city-floor04.cjs').read_text(encoding='utf-8').replace('city-floor04','city-floor05').replace('콘크리트 수정안','방향·외곽선 수정안')
(root/'scripts/check-city-floor05.cjs').write_text(s,encoding='utf-8')
print(out)
