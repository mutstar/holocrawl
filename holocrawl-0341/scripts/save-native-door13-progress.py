from pathlib import Path
import json

root=Path(__file__).resolve().parents[1];preview=root/'preview/native-door13'
note='''# 현재 검토: 아치형 철제 양문13 / 2026-11-04

사용자: 돌죽처럼 아치+양쪽 철문이면 어떨지 요청. built-in image_gen으로 회색 아치/푸른 회색 철제 문짝2개를 생성하고 닫힘/양쪽 열림2상태 제작. 좁은24×30 실루엣을32×32 PNG 안에 배치, 가로·세로 동일 크기. 아직 사용자 승인 전.

http://127.0.0.1:8797/native-door13/
상세 design/CITY_ARCHED_DOUBLE_DOOR13.md. 닫힘/열림과 가로/세로4개를 동시에 표시하고 실제 지도 연결. 6지도×2방향·투명도/새 파일·모바일/오류 검증 통과. 이전12/외짝문/원본지형/게임런타임 보존. 회사에서는 브라우저 도트·구조·배치만 진행. 다음은 양문 아치 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 아치형 철제 양문13'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json';status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-arched-double-steel-door-review13','currentVisualReview':'preview/native-door13/index.html','doorArtReview':'preview/native-door13/index.html','doorOpenStatesReview':'preview/native-door13/index.html','doorArtType':'arched-double-steel','doorArtDisplayByWallAxis':{'horizontal':[24,30],'vertical':[24,30]},'doorArtApproved':False,'actualGameApplicationDeferred':True,'next':'Review arched double steel door13, including both-axis closed/open states. Same24x30 silhouette inside32px tile. Browser-only; previous12 preserved.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name;state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(preview/'index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved arched-double-door13 and continuation pointers.')
