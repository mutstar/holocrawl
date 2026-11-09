from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
def update(d):
 if 'tierApprovals' in d:
  s=d['tierApprovals'].setdefault('su',{})
  s.update(approved=[1,3],pending=[5],tier3Revision='su-wave03',pendingRevision=None,feedback='좋다',tier3NumbersApproved=True)
 d['next']='Su tiers1/3 approved. Next: review Su tier5; 18 complete gods, Su/Vivi/Sopia/Mela remain.'
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=r/'analysis/previews/su-review01'
for name in ['index.html','tier3-review01.html','tier3-wave02.html','tier3-wave03.html']:
 p=base/name;t=p.read_text(encoding='utf-8').replace('현재3성 검토 중.','3성 확정. 다음은5성 검토입니다.');p.write_text(t,encoding='utf-8')
note='# 스우3성 확정 / su-wave03 / 2026-10-29\n\n사용자 피드백「좋다」로 스우3성 파도 크기·수치 승인.20×24→24×28확대 버전,물에서폭1→3칸 전진.피해2d(7+floor(I/3)),I12평균12(AC전),1칸밀치기,MP3/신앙3/1턴 유지.스우1·3성 확정,5성만 남음.완료18신 유지,다음 스우5성 검토.실행본 su-wave03 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su tiers1/3 approved; tier5 pending')
