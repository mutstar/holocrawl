from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'preview/passage-safe124';F=R/'preview/facility-exteriors124'
nav=json.loads((P/'validation.json').read_text(encoding='utf-8'));browser=json.loads((P/'browser-validation.json').read_text(encoding='utf-8'));reg=json.loads((P/'regressions.json').read_text(encoding='utf-8'));fac=json.loads((F/'validation.json').read_text(encoding='utf-8'))
assert all(x['status']=='passed' for x in [nav,browser,reg,fac]);assert nav['layouts']==416 and nav['maxFinalLocalDetour']<=2
plan=json.loads((P/'plan.json').read_text(encoding='utf-8'))
for name,h in plan['frozenInputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
validation={'status':'passed','revision':124,'navigation':nav,'browser':browser,'regressions':reg,'facilityExteriors':fac,'frozenInputsUnchanged':True,'nativeIntegrated':False,'saveFilesTouched':False}
(P/'final-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for kind in ['street','market']:
 (R/f'preview/city-{kind}124/validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((R/'preview/city-street124/manifest.json').read_text(encoding='utf-8'));m.update(ambientRevision=124,facilityExteriorRevision=124,source='Native107 immutable map/physics; browser wall121 / passage124 / facility exterior124.');(R/'preview/city-street124/manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'preview/city-market124/app.js';s=p.read_text(encoding='utf-8').replace("fixture?MarketStock.describe(fixture,map,stockMix):", "fixture?MarketStock.describe(fixture,map,stockMix)+(fixture.passable?' · 밟고 지나갈 수 있는 장식':''):");p.write_text(s,encoding='utf-8')
fm=json.loads((F/'manifest.json').read_text(encoding='utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
for group in range(3):
 sheet=Image.new('RGB',(2208,784),'#151e22');d=ImageDraw.Draw(sheet)
 for i,m in enumerate(fm['maps'][group*3:group*3+3]):
  im=Image.open(F/f'{m["facility"]}-native124.png');x=i*736;d.text((x+16,10),m['name'],font=font,fill='#deebe5');sheet.paste(im,(x+(736-im.width)//2,57))
 sheet.save(F/f'actual-facilities-{group+1}124.png')
head='''# 2026-11-09 · 1~7층 통로 보호·고정지형 외벽124

- 뭇별 요청: 승인한 벽121(22px)·벽 구조물122 유지. 바닥 소품은1~2칸 통로+인접1칸/ㄱ자 코너/문·계단 주변3칸/시설 경계에서 제외. 안전한 벽 옆으로 이동, 자리 없으면 생략. 종이 잔해는 통과 가능한 낮은 바닥 장식. 2칸 공간 연결/새1칸 병목/연결성/누적 우회 거리 검사.
-236개 지도 구조 /416회 배치 검증 passed: 기존 네이티브 랜덤36지도×배치6변형216 + 새 브라우저 시장50시드×4층200. 새로운 네이티브 생성236회라는 뜻이 아님.6694개 요청→6621개 배치(5786이동/73생략/352통과장식). 최종 배치 전체 재검사: 좁은 길 침범0·새 병목0·단절0·6기준점→전체 잔여 바닥 및 소품4방향 국소 경로의 추가 우회 최대2칸. 모든 가능한 점 쌍 전수검사는 아님.
-고정지형9곳 외벽: 승인한22px 재질/테두리를 공통 적용하고 간판·원형등·입구표지를 전면 안에 배치. 내부 장식·문 픽셀/방향·기하 불변.0기생2줄 암벽 부조는 원본 크기 보존. 브라우저 실제 생성 지도 연결/시설9곳·문10곳 열고 진입/시야 기준 프레임9개 일치/종이 잔해 실제 이동/4층별 동일시드 재생성 passed, JS오류0.6개 표적 회귀 passed. 코너 회귀의 최초 좌표는 코너 옆 직선칸을 잘못 가리켰으므로(8,9)→실제 오목코너(7,9)로 시험 좌표만 수정. 실행 정책 변경이나 실패 우회 없음.
-preview/city-street124 (1~3층 실제 지도+강제 시설9표본), city-market124 (4~7 브라우저 생성), passage-safe124, facility-exteriors124. final-validation.json / narrow-before-after124.png / 시설별 *-native124.png / actual-facilities-1~3-124.png. 이전123 및 원본121/122/106/107 보존.
-scripts: prepare-passage124.py → verify-passage124.cjs; prepare-facility-exteriors124.py → check-passage124-regressions.cjs → export-passage124.cjs → export-passage124-comparison.cjs → finalize-passage124.py. 엔진107 실행파일·실제 세이브·사운드 불변. 배치·외벽은 브라우저 검토본이며 네이티브 이식 별도. 적/보상 보류. 미커밋·미푸시.124 결과 피드백 대기.

'''
for p in [R/'CONTINUE_HERE.md',R.parent/'CONTINUE_HERE.md']:
 old=p.read_text(encoding='utf-8');p.write_text(head+old,encoding='utf-8')
p=R/'design/dungeon-route01.json';d=json.loads(p.read_text(encoding='utf-8'));d['currentArtTask']='잔향도시124: 벽121/벽 구조물122 유지,1~7층 바닥 소품 통로 보호·236구조416배치 검증 passed.고정지형9외벽22px 정렬/멤버 장식·문 보존, 실제 지도 이미지 각각 출력.브라우저만·피드백 대기.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R.parent/'OPEN_LATEST_PREVIEW.ps1';s=p.read_text(encoding='utf-8').replace('/city-street123/','/city-street124/');p.write_text(s,encoding='utf-8')
print('Final124 audit passed; latest launch and handoff updated. No engine/save writes.')
