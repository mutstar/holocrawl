from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
note='''# 문 디자인 선택: 네모 철제 문12 / 2026-11-04

사용자는 아치형 양문13보다 직전24×30 네모 철제 문12를 선택했다. 가로·세로 모두 같은32×32 PNG 안의24×30 실루엣, 외짝문 닫힘/열림을 사용한다. 12를 승인/선택 상태로 기록했고13은 비교안으로 보존했다. 실제 게임 적용은 계속 보류한다.

http://127.0.0.1:8797/native-door12/
디자인 design/CITY_SLIM_DOOR12.md, 기존 검증 preview/native-door12/browser-validation.json. 도트나 동작을 새로 변경한 것은 아니다. 이후 브라우저 맵 작업에서는 이 네모 문을 기준으로 삼는다.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 문 디자인 선택: 네모 철제 문12'):
        target.write_text(note+content,encoding='utf-8')
for version,selected in [(12,True),(13,False)]:
    target=root/f'preview/native-door{version}/art-manifest.json'
    data=json.loads(target.read_text(encoding='utf-8'))
    data.update({'approved':selected,'selected':selected,'selectionDate':'2026-11-04','selectionReason':'User prefers24x30 rectangular steel door12 over arched double door13.'})
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
target=root/'migration-status.json';state=json.loads(target.read_text(encoding='utf-8'))
state.update({'activeWork':'browser-map-art-rectangular-door12-approved','currentVisualReview':'preview/native-door12/index.html','doorArtReview':'preview/native-door12/index.html','doorOpenStatesReview':'preview/native-door12/index.html','doorArtType':'rectangular-single-steel','doorArtApproved':True,'doorArtSelectedRevision':'native-door12','doorArtDisplayByWallAxis':{'horizontal':[24,30],'vertical':[24,30]},'actualGameApplicationDeferred':True,'next':'Rectangular steel door12 selected by user. Use its same24x30 silhouette for both axes in subsequent browser map/art work. Arch13 retained as an unselected alternative; native work deferred.'})
target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name;data=json.loads(target.read_text(encoding='utf-8'))
    data.update({'activeWork':state['activeWork'],'currentVisualReview':str(root/'preview/native-door12/index.html'),'doorArtApproved':True,'doorArtSelectedRevision':'native-door12','next':state['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
target=root/'design/CITY_SLIM_DOOR12.md'
target.write_text(target.read_text(encoding='utf-8')+'\n## 최종 선택\n\n2026-11-04 사용자가 아치형 양문13보다 이24×30 네모 문12를 선호하여12를 선택했다. 가로·세로 같은 도트를 기준으로 이후 브라우저 맵 작업을 이어간다. 실제 게임 적용 승인은 아니다.\n',encoding='utf-8')
print('Selected and approved rectangular door12; arch13 retained as an alternative.')
