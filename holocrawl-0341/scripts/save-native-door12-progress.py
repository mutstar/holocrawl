from pathlib import Path
import json

root=Path(__file__).resolve().parents[1];preview=root/'preview/native-door12'
note='''# 현재 검토: 좁은 비율 문 원화 재제작12 / 2026-11-04

사용자: 세 번째 비교 문처럼 가로가 짧은 문으로 도트 재제작 요청. built-in image_gen으로 철제 외짝문 닫힘/열림 원화를 새로 만들고24×30 실루엣을 투명32×32 PNG 안에 배치. 가로·세로 모두 같은 PNG/크기 사용. 양문 전환은 하지 않음. 새 도트 승인 전.

http://127.0.0.1:8797/native-door12/
상세 design/CITY_SLIM_DOOR12.md. 가로/세로×닫힘/열림4개 동시 표시 및 실제 지도 연결. 6지도×2방향·투명도/새 파일/상태 전환·모바일/오류 검증 통과. 이전11/원화/지형/게임 런타임 보존. 회사에서는 브라우저 도트·구조·배치만 진행. 다음은 새 좁은 문 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 좁은 비율 문 원화 재제작12'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json';status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-redrawn-slim-door-review12','currentVisualReview':'preview/native-door12/index.html','doorArtReview':'preview/native-door12/index.html','doorOpenStatesReview':'preview/native-door12/index.html','doorArtDisplayByWallAxis':{'horizontal':[24,30],'vertical':[24,30]},'doorArtCanvas':[32,32],'doorArtRedrawn':True,'doorArtApproved':False,'actualGameApplicationDeferred':True,'next':'Review newly generated slim single-leaf door12. Same24x30 silhouette within32px tile for both wall axes; closed/open shown together. Browser-only.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name;state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(preview/'index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved redraw12 and continuation pointers.')
