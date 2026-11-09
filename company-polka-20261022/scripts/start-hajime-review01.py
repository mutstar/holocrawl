from pathlib import Path
import json,re,shutil
r=Path(__file__).resolve().parents[1];review='analysis/previews/hajime-review01/tier1.html';o=r/Path(review).parent;o.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
source=r/'analysis/previews/all-gods-vfx-draft04/clips/hajime-passive-0.png';shutil.copy2(source,o/'passive.png')
css=re.search(r'<style>(.*?)</style>',(r/'analysis/previews/raden-review01/index.html').read_text(encoding='utf-8'),re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>하지메 · 1성 반쵸의 스텝</title><style>'''+css+'''</style><h1>하지메 · 1성 반쵸의 스텝</h1><p class="info"><b>적 근처에서 이동해 박자를 모으고, 다음 근접 공격을 강화합니다.</b><br>해금: 신앙★30 · 최소 기도술 제한 없음<br>자동 패시브 · MP/신앙 소모 없음 · 별도 시전 버튼 없음</p><div class="cards"><article><h2>현재 실제 게임 초안</h2><img src="passive.png" alt="하지메 박자 유지 상태의 기존 실제 게임 캡처"><p>머리 오른쪽 위 파랑·보라의 작은 리듬 표식이 박자가 있는 상태를 나타냅니다. 현재 표식 모양은 박자1·2·3개를 구분하지 않습니다.</p><p>이 이미지는 기존 실제 엔진 캡처입니다. 이동·획득·소모의 연속 재생은 아직 아닙니다.</p></article><article><h2>박자를 쌓는 조건</h2><p>자발적으로 이동한 뒤 주변1칸에 유효한 적이 있고, 그 적이 이동 전 위치에서도2칸 이내이며 시야가 연결되면 박자+1. 한 번 이동에 최대1개, 총3개까지 쌓입니다.</p><p>제자리 대기나 강제 이동은 적립되지 않습니다. 혼란·행동 불가 상태에서도 적립되지 않습니다. 마지막 적립에서3턴이 지나면 박자가 사라집니다.</p><h2>다음 근접 공격 보너스</h2><p>피해 보너스: 박자 수 × (3+⌊I/6⌋)<br>명중 보너스: 박자 수<br>I는 기도술, ⌊ ⌋는 소수점 버림.</p><table><tr><th>기도술12</th><th>피해 보너스</th><th>명중 보너스</th></tr><tr><td>1박자</td><td>+5</td><td>+1</td></tr><tr><td>2박자</td><td>+10</td><td>+2</td></tr><tr><td>3박자</td><td>+15</td><td>+3</td></tr></table><p>박자는 근접 공격을 시도할 때 전부 소모합니다. 빗나가도 소모하며, 최종 피해는 실제 공격 계산과 적의 방어에 따라 달라집니다. 원거리·주문 공격에는 이1성 보너스를 주지 않습니다.</p></article></div><p>라덴 1·3·5성 확정 완료. 현재 하지메 1성 검토 중이며 기존 도트·전투 수치는 변경하지 않았습니다.</p></html>'''
(o/'tier1.html').write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['hajime']=[dict(tier=1,option=0,title='반쵸의 스텝',image='../hajime-review01/passive.png',kind='기존 실제 박자 유지 캡처')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="hajime" data-god="hajime"><h2>하지메 <small>1성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">1성 · 반쵸의 스텝</option></select><p class="scene-note">기존 실제 박자 유지 캡처</p><img class="scene" src="../hajime-review01/passive.png"><p>적 근처 자발적 이동으로 박자 축적, 다음 근접 공격 강화. 신앙30 해금, 최소 기도술 제한 없음. MP·신앙 소모 없음.</p><p><a href="../hajime-review01/tier1.html">조건·효과·상세 수치</a></p><label>피드백<textarea data-feedback="hajime"></textarea></label></article>'
t=re.sub(r'<article id="hajime".*?</article>',lambda _:article,t,count=1,flags=re.S);t=t.replace("location.hash.slice(1)||'raden'","location.hash.slice(1)||'hajime'");p.write_text(t,encoding='utf-8')
main=read(r/'VFX_DRAFT_STATUS.json');approved=main['approvedGods'];
if 'raden' not in approved:approved.append('raden')
pending=[g for g in main['draftGods'] if g!='raden']
def update(d):
 d.update(currentGod='hajime',currentVisualReviewGod='hajime',currentVisualReviewTier=1,currentVisualReview=review,next='Review Hajime tier1. Raden tiers1/3/5 approved; remaining Hajime, Su, Vivi, Sopia, Mela.')
 if 'review' in d:d['review']=review
 if 'approvedGods' in d:d['approvedGods']=approved.copy()
 if 'draftGods' in d:d['draftGods']=pending.copy()
 if 'tierApprovals' in d:
  d['tierApprovals'].setdefault('raden',{}).update(approved=[1,3,5],pending=[],pendingRevision=None,tier5Revision='raden-five04',combatRevision='raden-balance01',feedback='오 이거멋지다 인정 이제다음')
  d['tierApprovals'].setdefault('hajime',{}).update(approved=[],pending=[1,3,5],pendingRevision='hajime-review01')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 라덴 전체 확정·하지메1성 시작 / 2026-10-28\n\n사용자 라덴5성 옻칠 병풍 승인(raden-five04). 라덴1/3/5성 전체 확정, 전투 수치raden-balance01 유지. 완료17신, 남은5신: 하지메→스우→비비→소피아→메라. 현재 하지메1성 반쵸의 스텝, 기존 실제 박자 캡처와 소스 수치를 analysis/previews/hajime-review01/tier1.html 에 정리. 도트/전투/실행본 변경 없음. 22신 시각 작업부터 완료 후 중간 패시브/성급 재검토 계획 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Approved gods:',len(approved),'Current review:',review)
