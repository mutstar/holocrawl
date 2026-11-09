from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
approval={'status':'approved','date':'2026-11-03','upstairs':'assets/stairs-up08-32.png','downstairs':'assets/stairs-down06-32.png','preview':'analysis/previews/street-stairs06/index.html','feedback':'User accepted upstairs08 as much better; circular upstairs/downstairs pair finalized.','engineIntegrated':False,'next':'Visibility and exploration fog preview; not started.'}
(r/'analysis/previews/street-stairs06/stairs-approval.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2),encoding='utf-8')
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/n;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(stairsApproved=True,currentStairsUpRevision='upstairs08',currentStairsDownRevision='spiral06',lastArchiveIncludesLatest=False,next='Stairs pair approved: upstairs08 and circular downstairs06. Next proposed work: visibility and exploration fog. Native runtime remains ayame-zanshin02; preview floor travel not integrated.')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 원형 계단 최종 승인 / 2026-11-03\n\n올라가기 stairs-up08-32.png + 내려가기 stairs-down06-32.png 한 쌍 사용자 승인. 현재 street-stairs06 미리보기 유지. 다음 제안 작업은 시야·탐험 안개이며 아직 시작 전. 실제 엔진·층 이동 미연결, 기존 ZIP 최신작업 미포함.\n\n'
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Saved approved stairs pair.')
