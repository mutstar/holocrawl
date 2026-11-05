from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
proof=json.loads((root/'analysis/street01/validation.json').read_text(encoding='utf-8'))
assert proof['status']=='passed'
note='''# 현재 작업: 잔향도시 실제 엔진 1층 / 2026-11-04

사용자 방침: 몹·아이템 배치는 맵 구성 후. 22신은 0.34.1 구조를 유지하고 던전부터 진행.

PLAY_STREET.cmd로 새 0.34.1 타일 엔진 시제품을 실행한다. 승인한 JS 지도 생성기를 새 시드로 실행해 실제 D:1 지형으로 가져온다. 80×70, 승인된 바닥·벽·실외기·파이프·펜스, 올라가는12/내려가는06. 원본 이동·충돌·시야·탐험 기억 사용. 몹·바닥 아이템·함정은 생성하지 않는다. 캐릭터 기본 시작 장비는 유지한다.

현재는 빈 1층만 연결한 단계다. 계단 사용 시 다음 단계 안내만 표시하며 원본 D:2나 탈출로 넘어가지 않는다. 새 층 생성·왕복 이동은 다음 작업이다. 실제 엔진 내부에서 JS를 실행하는 방식이 아니라 실행기가 생성한 지도를 읽는다. 저장 시 지도·타일은 원본 저장 체계를 사용한다.

상세: design/STREET_NATIVE01.md. 네이티브 검사: analysis/street01/validation.json. 원본 0.34.1 실행 파일과 이전 0.24 실행 파일 보존.

다음: 층 이동·지도 저장 왕복 확인 → 잔향도시 14층 구간별 테마 → JP 분기·커튼콜 연결. 몹·아이템은 그 후.

아래 이전 기록의 브라우저만 구현/시야 미구현/08 계단 표기는 현재 기록으로 대체한다.

---

'''
status_path=root/'migration-status.json';status=json.loads(status_path.read_text(encoding='utf-8'))
status.update(phase='native-street-first-floor',activeWork='native-street-first-floor',customDungeonIntegrated=True,customDungeonIntegrationScope='D:1 prototype import from approved JS generator',nativeStreetFirstFloor=True,nativeStreetValidationPassed=True,nativeStreetTerrainCellsChecked=proof['nativeTerrainCellsChecked'],nativeStreetLauncher='PLAY_STREET.cmd',floorTravelImplemented=False,campaignMapComplete=False,monstersPlaced=False,groundItemsPlaced=False,next='Connect floor transitions and round-trip level persistence, then city14 themes and JP branch entrances. Place creatures/items after map structure.')
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for path in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    existing=path.read_text(encoding='utf-8-sig')
    if not existing.startswith('# 현재 작업: 잔향도시 실제 엔진 1층'):
        path.write_text(note+existing,encoding='utf-8')
legacy=root.parent/'company-polka-20261022'
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    path=legacy/name;state=json.loads(path.read_text(encoding='utf-8-sig'))
    state.update(activeProject=str(root),activeWork='native-street-first-floor',nativeStreetLauncher=str(root/'PLAY_STREET.cmd'),nativeStreetFirstFloor=True,floorTravelImplemented=False,lastArchiveIncludesLatest=False,next=status['next'])
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved native street first-floor checkpoint.')
