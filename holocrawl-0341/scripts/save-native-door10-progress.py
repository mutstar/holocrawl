from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
preview=root/'preview/native-door10'
art=json.loads((preview/'art-manifest.json').read_text(encoding='utf-8'))
art.update({'revision':'native-door10','approved':False,'doorDisplay':{'tile':[32,32],'spriteDraw':[24,30],'offset':[4,1],'sourceSpritesUnchanged':True},'wallMaterial':json.loads((preview/'wall-material-manifest.json').read_text(encoding='utf-8')),'crawlReference':{'version':'0.34.1','closed':'assets/crawl-closed_door.png','open':'assets/crawl-open_door.png','originalDirectory':'engine/upstream/crawl-ref/source/rltiles/dngn/doors','purpose':'Unmodified originals used only for comparison.'}})
(preview/'art-manifest.json').write_text(json.dumps(art,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 현재 검토: 문 비율·벽 반복 수정10 / 2026-11-04

사용자:09 방화문 가로 폭이 넓어 보임, 원본 돌죽 문 모양 질문, 벽 패널이 매 칸 반복돼 겹쳐 보인다고 피드백. 원본0.34.1 문 비교 추가, 기존 철제 문은 표시 폭24×높이30으로 조정. 벽은 연속 콘크리트 표면과 드문 줄눈·배관으로 변경. 새 버전 승인 전.

http://127.0.0.1:8797/native-door10/
상세 design/CITY_DOOR_WALL10.md. 같은 문 위치의 돌죽/이전/수정 및 긴 벽 이전/수정 비교. 6지도·문/벽 전환·재그리기·모바일·오류 검사 통과. 바닥/원본 지형/이전09/실제 게임 런타임 유지. 브라우저 전용 검토. 다음은 문의 비율과 벽의 색·재질 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 문 비율·벽 반복 수정10'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json'
status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-door-wall-art-review10','currentVisualReview':'preview/native-door10/index.html','doorArtReview':'preview/native-door10/index.html','doorArtDisplaySize':[24,30],'doorArtApproved':False,'wallMaterialReview':'preview/native-door10/index.html','actualGameApplicationDeferred':True,'next':'Review24x30 door display against original DCSS and previous32x32, plus continuous concrete wall surface in door10. Browser-only work.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name
    state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(preview/'index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved door10 comparison, art manifest and continuation pointers.')
