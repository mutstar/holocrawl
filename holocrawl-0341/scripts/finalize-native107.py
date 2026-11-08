"""Install validated native107 metadata and record a scoped handoff."""
from pathlib import Path
import json, hashlib
R = Path(__file__).resolve().parents[1]
G = R.parent
A = R/'analysis/native-play107-01'
P = R/'preview/native-play107'
v = json.loads((A/'material-validation.json').read_text())
b = json.loads((P/'browser-validation.json').read_text())
m = json.loads((R/'migration/engine0341-play107/manifest.json').read_text())
assert v['status'] == b['status'] == m['restoreCheck']['status'] == 'passed'
S = A/'engine/crawl-ref/source'
assert hashlib.sha256((S/'crawl.exe').read_bytes()).hexdigest() == v['binarySha256']
install = {'status':'passed','version':107,'source':S.relative_to(G).as_posix(),
 'binarySha256':v['binarySha256'],'validation':'holocrawl-0341/analysis/native-play107-01/material-validation.json',
 'saveIsolation':'holocrawl-0341/runtime/city107','originalEngineUnchanged':True}
(R/'runtime').mkdir(exist_ok=True)
(R/'runtime/native-city107-install.json').write_text(json.dumps(install,indent=2)+'\n')
plan = json.loads((A/'plan.json').read_text())
plan.update(status='passed',finalSuite='suite-10',replaySuite='suite-09',
 scriptedReplayAnimations='Animation disabled and cosmetic birth/frame clock fixed before generation only in script; actual game unchanged')
(A/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
f = R/'design/dungeon-route01.json'
d = json.loads(f.read_text(encoding='utf-8'))
x = d['jp']['main']['facilityPlacement']
x.update(nativeArtRevision=107,artRevision=107,browserPreview='preview/native-play107/index.html',
 validation='analysis/native-play107-01/material-validation.json',legacyEngineArtRevision=84)
x['nativeIntegration107'] = {**install,'normalWall':92,'basicDoor':101,'facilityArt':106,
 'report':'design/NATIVE_PLAY107_REVIEW.md','browserValidation':'preview/native-play107/browser-validation.json','fullCampaignVerified':False}
for k in ['approvedNormalWall','approvedNormalDoor']:
 x[k]['nativeAtlasIntegration']=True
 x[k]['integrationScope']='Isolated native107 engine; original84 preserved'
for k in ['facilityWallDoorPreview','basicDoorPreview']:
 x[k]['nativeIntegration']=True
 x[k]['integrationScope']='Isolated native107 engine; design approval remains separate'
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report = f'''# 잔향도시 실제 생성·플레이 점검107

뭇별 요청의1~5번을 실제0.34.1 엔진으로 확인했다. 원본84 엔진과 기존 세이브는 보존했다. 별도107 엔진에 벽92·기본문101·시설106이 컴파일돼 있다.

| 항목 | 결과 |
|---|---|
| 1. 시야·안개 | 네이티브 시야5,276프레임 /29,545,600칸 대조, 불일치0. 벽·유리·닫힌/열린 문 포함. 브라우저는 탐험 기억과 현재 시야 구분. |
| 2. 이동·충돌 | 실제 move_player_action 유효이동885회/차단885회, 문 열기→진입948쌍, 연결문 닫기. 문 시야903쌍. 엔진 원래 동작인 두 막힌 모서리 사이 대각선 이동137건 확인. |
| 3. 캐릭터·몬스터·아이템 | 시설9종에 네이티브 플레이어·오크·포션27개 배치. 실제 타일/캐릭터4파트 표시. 표시 변경은 해당 몬스터/아이템 칸 내부에 한정. |
| 4. 무작위 생성·연결 | 새 정상12시드×14층=168층 + 시설별 강제검토9층=177층. 계단·시설 입구 연결성, 충돌, 생성계획 및 저장 왕복 통과. 동일177층 재실행 JSON 완전 일치. |
| 5. 엔진 최신 아트 | 컴파일 아틀라스 {v['compiledArtTilesCompared']:,}타일 원본 일치, 일반벽 {v['nativeWallTilesCompared']:,}셀 및 시설 외벽 {v['dynamicFacilityPerimeterCells']:,}셀 인접연결 확인. 원본 엔진 해시 유지. |

## 수정 사항

- 시설 외벽을 실제 이웃8방향에 맞춰 새 일반벽으로 렌더링하고 장식만 별도 레이어로 올린다. 외벽 명암 계산에 내부 가구를 벽 덩어리로 취급하지 않는다.
- 네이티브의 텍스처별 묶음 그리기로 장식이 벽 뒤에 숨는 문제를 수정했다. 전용 장식 버퍼를 벽 이후/캐릭터 이전에 그리고 초기화한다.
- 기본문101은 가로/세로 같은 정면 디자인. 시설문106 방향과 내부 멤버 소품 적용. 연결된 문은 네이티브 그룹 열기/닫기를 따른다.
- 브라우저에만 있던 대각선 제한을 제거해0.34.1과 맞췄다. 픽셀 좌표를 정수에 맞추고 캔버스 읽기 모드를 고정해 반픽셀 경계/렌더 백엔드 전환에 따른 픽셀 차이를 해결했다.

## 시험 자료와 범위

최종 suite-10, 동일 시드 재현 suite-09. 두 코호트는 같은177층이며354개의 독립 표본으로 세지 않는다. 시설 강제검토9층은 출현율 측정이 아니다. 정상 정책은 층마다50%, 최대1시설, 한 판 중복 없음. 계획 검사20,000시드/280,000층은 실제 생성177층과 구분한다.

실패/중간 결과와 로그를 보존했다. 초기 검사에서 연결문 닫기 누락을 잡아 네이티브 그룹 닫기와 전체 지형 복원 검사를 추가했다. 물 타일은 생성시각 기반 색상과 flavour 초기화로 달라졌다. 최종 시험 스크립트에서 생성 전 birth_time/frame 및 애니메이션을 고정했다. 실제 게임의 시각/애니메이션 설정은 바꾸지 않았다. 내보내기의 apply_variations 중복 호출도 제거했다.

실제 엔진이 지형을 만들고 이동·문·시야·배치를 검사했다. 화면은 그 엔진의 컴파일 아틀라스와 지도 데이터를 그대로 그리는 브라우저 검토기다. 네이티브 SDL 전체 화면 자동 캡처나 전투/적·보상/캠페인 완주 검증으로 확대 해석하지 않는다. 시설문 디자인의 개별 피드백은 계속 가능하다.

## 실행과 이어가기

- 브라우저: http://127.0.0.1:8797/native-play107/ . 시설9종+정상168지도, 시야/전체지도/이동/문/겹침검사.
- 실제 게임: 저장소 루트 PLAY_CITY.cmd. 검증107 바이너리를 선택하며 runtime/city107에 새 저장한다. 기존 city77 저장을 열지 않는다. PLAY_CITY.ps1 -Legacy로 원본84 선택 가능.
- 설치 메타데이터: runtime/native-city107-install.json. 실행 전 바이너리 SHA256 확인.
- 현재 바이너리 SHA256: {v['binarySha256']}
- 복원: migration/engine0341-play107/tracked.patch + overlay.0.34.1 기반 복원검사 통과(추적 {m['restoreCheck']['trackedFiles']}파일, 추가 {m['restoreCheck']['overlayFiles']}파일). BUILD_CITY107.ps1은 별도107을 복원/빌드한다.
- 새 빌드 후 run-native-play107.py suite --attempt <새번호>를 두 번, check-native-oracle107.cjs <최종suite>를 실행한다. publisher의 최종/재현 폴더를 해당 번호로 지정해 감사하고 브라우저 검사 후 설치 메타데이터를 갱신한다. 기존 결과 폴더를 덮어쓰지 않는다.
- 증거: analysis/native-play107-01/material-validation.json, suite-10/oracle-validation.json, preview/native-play107/browser-validation.json.
- 화면: preview/native-play107/overview.png, entrance-fog.png, 시설별 -actors.png/-fullmap.png.

미커밋·미푸시. 적·보상 기획은 기존 요청대로 보류한다.
'''
(R/'design/NATIVE_PLAY107_REVIEW.md').write_text(report,encoding='utf-8')
head = '''# 2026-11-08 · 실제 생성·플레이 점검107 완료

- 최신 http://127.0.0.1:8797/native-play107/ . 벽92/기본문101/시설106을 별도 실제0.34.1 엔진에 컴파일. 원본84 엔진/기존 세이브 보존.
- 새168정상층+9시설 강제층=177층, 동일시드 재현177층 JSON 일치. 시야5,276프레임/29,545,600칸 불일치0. 실제 이동885/차단885, 문 열기→진입948쌍·닫기, 문시야903쌍. 플레이어/오크/포션27배치.
- report: holocrawl-0341/design/NATIVE_PLAY107_REVIEW.md. final suite-10/replay suite-09, material-validation 및 browser-validation passed. 출현50%/층1/한판중복없음 유지.
- PLAY_CITY.cmd는 검증107 엔진 선택, runtime/city107 별도 저장. -Legacy로 원본84 선택. BUILD_CITY107.ps1 + migration/engine0341-play107 복원패치/overlay/manifest. 적/보상·캠페인 통합검증 아님.
- 시설 장식 버퍼·인접 외벽·문그룹/대각선일치 수정. 검사에서만 생성시각/애니메이션 고정. 실제 게임 애니메이션 유지. 실패/중간자료 보존. 시설문 개별 피드백 대기는 유지. 미커밋·미푸시.

'''
for f in [G/'CONTINUE_HERE.md',R/'CONTINUE_HERE.md']:
 f.write_text(head+f.read_text(encoding='utf-8'),encoding='utf-8')
f = G/'OPEN_LATEST_PREVIEW.ps1'
s = f.read_text(encoding='utf-8').replace('/native-city77/?seed=77001&floor=1','/native-play107/')
f.write_text(s,encoding='utf-8')
print('Installed validated native107 launcher and scoped handoff.')
