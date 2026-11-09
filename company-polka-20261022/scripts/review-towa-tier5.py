from pathlib import Path
import json,re,shutil
r=Path(__file__).resolve().parents[1];p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8')
backup=r/'analysis/previews/towa-tier5-review01';backup.mkdir();shutil.copy2(p,backup/'before-index.html')
s=s.replace('지금은 토와 3성을 확인합니다.','토와 3성 승인 완료. 지금은 토와 5성을 확인합니다.').replace('토와 <small>1성 승인 · 3성 확인 중</small>','토와 <small>1·3성 승인 · 5성 확인 중</small>').replace("if(active.id==='towa')sel.value='1'","if(active.id==='towa')sel.value='2'")
info=dict(cost='MP 6 · 신앙 12 · 시전0.5턴 · 3성 엄호 구역이 유지 중이어야 사용 가능 · 구역 중심이 시야 안·6칸 이내 · 종료 후 재사용 대기10턴',effect='기존 5×5 엄호 구역을 교차포화로 강화합니다. 지원사격 탄약을8발로 다시 채우고, 일반1턴당 최대2발까지 발사합니다. 구역 안의 보이는 적을 직접 일반 원거리 공격할 때 명중 +6을 받고 적 방어구를70%로 계산합니다. 근접·공격 주문에는 이 원거리 보너스가 적용되지 않습니다.',scaling='시전 후 지속: 5 + 기도술 × 0.2턴. 기도술12면7.4턴입니다. 기존 구역의 남은 지속 시간은 이 시간으로 교체됩니다. 지원사격 한 발의 기본 피해는3성과 동일한 2d(5 + ⌊기도술/3⌋)이며, 발동 조건과 다음 이동 방해도 동일합니다. 화면은 기존5성 시전 초안이며,8발 연속 발사 전체를 보여주는 GIF는 아닙니다.')
s=s.replace('function updateSkillInfo(article,entry){','towaSkillInfo[5]='+json.dumps(info,ensure_ascii=False)+';\nfunction updateSkillInfo(article,entry){')
p.write_text(s,encoding='utf-8')
feedback='ㅇㅋ 잘보이네ㅋㅋ 토와 3성은 이걸로하고 5성으로가자'
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','VFX_DRAFT_STATUS.json']:
 p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'))
 if name=='VFX_DRAFT_STATUS.json':
  a=d['tierApprovals']['towa'];a.update(approved=[1,3],pending=[5],tier3Revision='towa-support05',tier3DiagonalPreview='towa-diagonal01',tier3Feedback=feedback,pendingRevision='original-tier5-draft')
 else:d.update(currentVisualReviewGod='towa',currentVisualReviewTier=5,towaVisualFeedback='Tier1 and Tier3 approved. Tier3 enlarged lavender arrow and diagonal demonstration accepted. Reviewing existing Tier5 cast draft.',towaTier3Approved=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='토와3성 승인 완료: towa-support05 큰 연보라 화살 + towa-diagonal01 대각선1/2칸 지원사격. 다음 검토는5성 악마의 교차포화. 브라우저는기존5성시전초안과코드확인수치를표시. 5성은아직미승인.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Towa tier3 approved; tier5 draft selected with skill details.')
