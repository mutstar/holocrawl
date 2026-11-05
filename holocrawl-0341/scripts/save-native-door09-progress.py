from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
note='''# 현재 검토: 철제 방화문 도트09 / 2026-11-04

사용자가0.34.1 원본 지형을 긍정하고 임시 문 교체 요청. 회색 철제 방화문32×32 닫힘/열림2상태를 생성해 원본6지도에 표시. 아직 도트 승인 전.

http://127.0.0.1:8797/native-door09/
상세 design/CITY_FIRE_DOOR09.md. 동일 위치에서 임시/닫힘/열림 비교와 문 클릭 열기·닫기 지원. 표시용 토글이며 실제 게임 행동은 연결하지 않음. 6지도/투명도/표시 전환/모바일 검증 통과. 원본 지형과 이전08 보존. 회사에서는 브라우저 도트·구조·배치만 진행. 다음은 문 색·크기·벽 접합 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 철제 방화문 도트09'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json'
status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-fire-door-art-review09','currentVisualReview':'preview/native-door09/index.html','doorArtReview':'preview/native-door09/index.html','doorArtStates':['closed','open'],'doorArtTileSize':32,'doorArtApproved':False,'doorGameActionsIntegrated':False,'actualGameApplicationDeferred':True,'next':'Review32px steel fire door closed/open in native-door09. Native terrain retained; door toggle is browser display only.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name
    state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(root/'preview/native-door09/index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved door09 art review and continuation pointers.')
