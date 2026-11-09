from pathlib import Path
import json,re,shutil
r=Path(__file__).resolve().parents[1];o=r/'analysis/previews/vivi-review01';o.mkdir(parents=True,exist_ok=True)
review='analysis/previews/vivi-review01/tier1.html'
shutil.copy2(r/'analysis/previews/all-gods-vfx-draft04/clips/vivi-tier1-option0-74.gif',o/'makeup-existing.gif')
css=re.search(r'<style>(.*?)</style>',(r/'analysis/previews/su-review01/index.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>비비1성 · 메이크업</title><style>'''+css+'''</style><h1>비비1성 · 메이크업</h1><p class="info"><b>화려한 메이크업으로 공격 피해를 높이는 지속형 강화입니다. 대신 은밀성이 줄고 투명 효과를 받을 수 없습니다.</b><br>해금: 신앙30 · 최소 기도술 제한 없음<br>비용: MP2·행동1턴 · 신앙 소모 없음</p><h2>기존 실제 게임 초안</h2><img src="makeup-existing.gif"><p>캐릭터 머리 옆 분홍색 장식이 현재1성 메이크업 이펙트입니다. 이 GIF는 기존 실제 엔진 캡처이며 이번에 새로 촬영한 공격·만료 연속 시연은 아닙니다.</p><h2>현재 소스 수치</h2><table><tr><th>항목</th><th>효과</th></tr><tr><td>피해 증가</td><td>10+⌊I/6⌋%. I0:+10%,I12:+12%,I27:+14%. 일반 근접·원거리 공격과 직접 주문 피해에 적용. 보조타격·소환수·장판 등은 일반 직접 공격 보너스 대상 아님</td></tr><tr><td>지속</td><td>시전 완료 후15+0.5I턴. I12에서21턴</td></tr><tr><td>은밀성</td><td>활성 중 은밀도 계산 결과 절반</td></tr><tr><td>투명</td><td>활성 중 투명 판정 불가. 투명 지속시간 자체를 삭제하는 방식은 아님</td></tr><tr><td>재사용</td><td>활성 중 재시전 불가. 종료 후 별도 대기시간 없이 다시 시전 가능.5성 중에는1성 재시전 불가</td></tr><tr><td>기도술·신앙</td><td>I는 기도술. 피해 증가율과 지속시간에 적용. 신앙은 해금 조건이며 별도 피해 배율 없음</td></tr><tr><td>3성 연계</td><td>메이크업이 켜져 있으면3성의 권능 피해에도 같은 증가율 적용</td></tr></table><p>이번 전환에서는 도트·전투 수치·실행 파일을 변경하지 않았습니다. 스우1·3·5성 확정,19신 완료. 남은 신:비비→소피아→메라. 지금은 비비1성 검토 중입니다.</p></html>'''
for name in ['index.html','tier1.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['vivi']=[dict(tier=1,option=0,title='메이크업',image='../vivi-review01/makeup-existing.gif',kind='기존 실제 엔진1성 캡처')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="vivi" data-god="vivi"><h2>비비 <small>1성 · 검토 중</small></h2><img class="scene" src="../vivi-review01/makeup-existing.gif"><p>메이크업:MP2·1턴,신앙 소모 없음. 신앙30 해금,최소 기도술 없음. I12:공격 피해+12%,시전 후21턴. 은밀도 절반·투명 판정 불가.</p><p><a href="../vivi-review01/tier1.html">효과·수치·현재 초안</a></p><label>피드백<textarea data-feedback="vivi"></textarea></label></article>'
t=re.sub(r'<article id="vivi".*?</article>',lambda _:article,t,count=1,flags=re.S);t=t.replace("location.hash.slice(1)||'su'","location.hash.slice(1)||'vivi'");p.write_text(t,encoding='utf-8')
def update(d):
 d.update(currentGod='vivi',currentVisualReviewGod='vivi',currentVisualReviewTier=1,currentVisualReview=review,next='Review Vivi tier1. Su fully approved; 19 gods complete. Remaining Vivi, Sopia, Mela.')
 if 'review' in d:d['review']=review
 if isinstance(d.get('approvedGods'),list) and 'su' not in d['approvedGods']:d['approvedGods'].append('su')
 if isinstance(d.get('draftGods'),list):d['draftGods']=[g for g in d['draftGods'] if g!='su']
 if 'tierApprovals' in d:
  d['tierApprovals'].setdefault('su',{}).update(approved=[1,3,5],pending=[],pendingRevision=None,tier5Revision='su-five01',feedback='ㅇㅋㅇㅋ그다음캐릭')
  d['tierApprovals'].setdefault('vivi',{}).update(approved=[],pending=[1,3,5],pendingRevision='vivi-review01')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/previews/su-review01/tier5-review01.html';p.write_text(p.read_text(encoding='utf-8').replace('현재5성 검토 중.','5성 확정. 스우1·3·5성 전체 승인.'),encoding='utf-8')
note='# 스우 전체 확정·비비1성 검토 시작 / 2026-10-29\n\n사용자「ㅇㅋㅇㅋ그다음캐릭」으로 스우5성 su-five01 승인,스우1·3·5성전체완료.완료19신,비비→소피아→메라3신남음.비비1성 메이크업 기존 실제 엔진GIF와 현재 소스 수치를 '+review+' 에정리. MP2/1턴/신앙0,신앙30해금,피해+(10+floor(I/6))%,시전후15+0.5I턴(I12:+12%/21턴),은밀도절반·투명판정불가.도트/전투/실행본변경없음.실행본은su-five01유지.현재비비1성검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su approved; Vivi tier1 ready:',review)
