from pathlib import Path
import json

root=Path(__file__).resolve().parents[1];preview=root/'preview/native-door11'
target=preview/'art-manifest.json';art=json.loads(target.read_text(encoding='utf-8'))
art.update({'revision':'native-door11','approved':False,'newRasterAssets':False,'doorDisplay':{'tile':[32,32],'byWallAxis':{'horizontal':[24,30],'vertical':[32,30]},'sourceSpritesUnchanged':True,'orientationAwareFrames':True},'renderingRevision':'Vertical door north wall face suppressed; exposed side faces connect above/below; frontal source sprites retained. A24/B32/Cdirectional browser comparisons.'})
target.write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 현재 검토: 가로·세로 벽의 문 연결11 / 2026-11-04

사용자: 가로 벽의 폭24문은 괜찮지만 세로 벽은 어색하여 넓은 문으로 복귀할지 고민. A모두24/B모두32/C가로24·세로32와 벽 연결 비교 추가. C는 세로 문 위의 잘못 그려진 가로 벽면을 빼고, 벽 옆면·위아래 문설주를 연결. 승인 전.

http://127.0.0.1:8797/native-door11/
상세 design/CITY_DOOR_ORIENTATION11.md. 각 방향 A/B/C와 열림 비교, 실제 지도에서 모드/문 이동 지원. 6지도×2방향×3모드36조합·지형/가로문 보존·모바일/오류 검사 통과. 기존10·PNG·원본 지형·게임 런타임 유지. 브라우저 전용. 다음은 C방향별 처리와 B전부 넓은 문 선호 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 가로·세로 벽의 문 연결11'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json';status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-door-orientation-review11','currentVisualReview':'preview/native-door11/index.html','doorArtReview':'preview/native-door11/index.html','doorArtDisplayByWallAxis':{'horizontal':[24,30],'vertical':[32,30]},'doorArtApproved':False,'actualGameApplicationDeferred':True,'next':'Review A24/B32/Cdirectional doors in native-door11. C preserves horizontal24 and widens vertical32 with corrected wall/frame context. No final choice yet.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name;state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(preview/'index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved door orientation11 review and continuation pointers.')
