from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];feedback='ㅇㅋ 좋다ㅋㅋ 토와는 이걸로하고 다음 라미로가자'
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'))
 if name=='VFX_DRAFT_STATUS.json':
  if 'towa' not in d['approvedGods']:d['approvedGods'].append('towa')
  d['draftGods']=[x for x in d['draftGods'] if x!='towa'];d.update(currentGod='lamy',next='Review Lamy caster redesign direction before committing mechanics and VFX')
  d['tierApprovals']['towa'].update(approved=[1,3,5],pending=[],tier5Revision='towa-crossfire02',feedback=feedback,pendingRevision=None)
 else:d.update(currentVisualReviewGod='lamy',currentVisualReviewTier=1,towaVisualFeedback='All tiers approved; tier5 winged bolt crossfire02. Now reviewing Lamy caster direction.',lamyReviewStatus='Existing drink/chill mechanics remain. Caster focus accepted in principle; detailed redesign not yet decided or implemented.')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');s=s.replace('토와 3성 승인 완료. 지금은 토와 5성을 확인합니다.','토와 전체 승인 완료. 지금은 라미의 마법 중심 개편 방향을 확인합니다.').replace('토와 <small>1·3성 승인 · 5성 확인 중</small>','토와 <small>전체 승인</small>').replace('라미 <small>초안 · 회사 피드백 대기</small>','라미 <small>기존 초안 · 마법 중심 개편 검토</small>').replace("const id=location.hash.slice(1)||'towa'","const id=location.hash.slice(1)||'lamy'").replace("if(active.id==='towa')sel.value='2';choose(sel);","if(active.id==='towa')sel.value='2';if(active.id==='lamy')sel.value='0';choose(sel);")
p.write_text(s,encoding='utf-8')
note='토와 전체 승인(towa-crossfire02). 다음은 라미. 기존 술/취기/냉각/근접오라 구현은 유지된 상태. 일반 주문 시전을 돕는 마법 중심 신으로 옮기자는 방향만 승인됐으며,별별 상세개편과수치는아직미확정·미구현.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Towa approved; Lamy direction review selected.')
