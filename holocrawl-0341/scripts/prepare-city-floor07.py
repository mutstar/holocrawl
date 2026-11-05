from pathlib import Path
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor07'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js']:
 shutil.copyfile(root/'preview/city-floor06'/name,out/name)
shutil.copytree(root/'preview/city-floor06/assets',out/'assets',dirs_exist_ok=True)
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace("previousUp:'assets/city-stairs-up-final32.png'","previousUp:'assets/city-stairs-up-thick-final32.png'").replace("cityUp:'assets/thick-stairs-up32.png'","cityUp:'assets/five-stairs-up32.png'");p.write_text(s,encoding='utf-8')
p=out/'grounding.js';s=p.read_text(encoding='utf-8').replace('이전 얇은 계단과 비교','이전 4단 계단과 비교').replace('두꺼운 4단 계단으로 보기','거친 5단 계단으로 보기');p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('올라가는 계단 4단','올라가는 계단 5단').replace('올라가는 계단을 두꺼운 4단으로 줄였습니다. 오른쪽 상승과 검정 외곽선 유지, 내려가는 계단은 승인한05와 동일합니다.','올라가는 계단을 5단으로 조정하고 디딤판을 조금 좁혔습니다. 원본 돌죽처럼 거친 표면과 밝은 모서리·어두운 옆면을 살렸습니다. 오른쪽 상승과 검정 외곽선 유지, 내려가는 계단은 승인한05와 동일합니다.').replace('이전 얇은 계단과 비교','이전 4단 계단과 비교');p.write_text(s,encoding='utf-8')
(out/'revision.json').write_text(json.dumps({'previous':'city-floor06','change':'ascending stair only; five narrower rough treads and clearer riser contrast','ascent':'right','descent':'left','approvedDownSha256':hashlib.sha256((out/'assets/city-stairs-down-final32.png').read_bytes()).hexdigest(),'terrainAndPlacementUnchanged':True,'nativeGameApplied':False},indent=2),encoding='utf-8')
s=(root/'scripts/check-city-floor06.cjs').read_text(encoding='utf-8').replace('city-floor06','city-floor07').replace('이전05','이전4단').replace('두꺼운4단 수정안','거친5단 수정안');(root/'scripts/check-city-floor07.cjs').write_text(s,encoding='utf-8')
s=(root/'scripts/export-final-stairs06.cjs').read_text(encoding='utf-8').replace('city-floor06','city-floor07').replace('city-stairs-up-thick-final32','city-stairs-up-five-final32');(root/'scripts/export-final-stairs07.cjs').write_text(s,encoding='utf-8')
print(out)
