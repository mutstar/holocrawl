from pathlib import Path
import json, shutil

root=Path(__file__).resolve().parents[1]
asset=root/'preview/stairs-up12/stairs-up12-32.png'
approval=dict(status='approved',date='2026-11-04',upstairs='assets/stairs-up12-32.png',downstairs='assets/stairs-down06-32.png',feedback='User approved the second image (revision12) as perfect.',engineIntegrated=False,floorTravelImplemented=False)
for name in ['street','street-vision01']:
    directory=root/'preview'/name
    shutil.copy2(asset,directory/'assets'/asset.name)
    path=directory/'app.js'
    path.write_text(path.read_text(encoding='utf-8').replace('stairs-up08-32.png','stairs-up12-32.png'),encoding='utf-8')
    (directory/'stairs-approval.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=root/'design/street-stairs06.json'
state=json.loads(path.read_text(encoding='utf-8'))
state.update(upstairsRevision='upstairs12',assets=[approval['upstairs'],approval['downstairs']],approved=True,approvedDate='2026-11-04',preview='preview/street-vision01/index.html')
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=root/'migration-status.json'
state=json.loads(path.read_text(encoding='utf-8'));state.update(stairsApproved=True,upstairsRevision='upstairs12',downstairsRevision='spiral06')
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=root/'preview/stairs-up12/generation.json'
state=json.loads(path.read_text(encoding='utf-8'));state.update(approved=True,replacesApprovedAsset=True,approvedDate='2026-11-04')
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='\n\n## 계단 최종 승인 갱신 / 2026-11-04\n\n올라가는 계단은 upstairs12(비교 오른쪽)를 사용자가 완벽하다고 승인했다. street와 street-vision01에 stairs-up12-32.png 적용. 내려가는 stairs-down06-32.png 유지. 이전 upstairs08 승인 기록은 이 기록으로 대체. 시야·탐험 안개 작업 계속.\n'
for path in [root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    with path.open('a',encoding='utf-8') as f:f.write(note)
legacy=root.parent/'company-polka-20261022'
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    path=legacy/name;state=json.loads(path.read_text(encoding='utf-8-sig'))
    state.update(currentStairsUpRevision='upstairs12',currentStairsDownRevision='spiral06',lastArchiveIncludesLatest=False)
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Approved upstairs12; installed in both current previews.')
