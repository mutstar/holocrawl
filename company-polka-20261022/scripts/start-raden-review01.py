from pathlib import Path
import json,re,shutil

r=Path(__file__).resolve().parents[1]
review='analysis/previews/raden-review01/index.html'
out=r/Path(review).parent
out.mkdir(parents=True,exist_ok=True)
gallery=r/'analysis/previews/all-gods-vfx-draft04/index.html'
text=gallery.read_text(encoding='utf-8')
data=json.loads(re.search(r'const data=(.*?);function choose',text).group(1))
clips=[x for x in data['raden'] if x['tier']==1][:2]
for i,c in enumerate(clips):
    source=gallery.parent/c['image'];assert source.is_file(),source
    shutil.copy2(source,out/f'exhibit{i+1}.gif')
css=re.search(r'<style>(.*?)</style>',(r/'analysis/previews/lui-review01/index.html').read_text(encoding='utf-8'),re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>라덴 · 1성 이동 박물관</title><style>'''+css+'''</style>
<h1>라덴 · 1성 이동 박물관</h1><section id="tier1">
<p class="info"><b>회화·조각·공예 중 하나를 전시해 가호를 바꿉니다.</b><br>가호 해금: 신앙 ★30 · 최소 기도술 제한 없음<br>전환 비용: MP1 · 신앙0 · 행동1턴<br>일반 상태에서는 매 턴 다시 전환 가능. 같은 작품 재선택 불가, 5성 특별전 중에는 전환 불가.</p>
<div class="cards"><article><h2>현재 실제 게임 초안 · 조각 전환</h2><img src="exhibit1.gif" alt="기존 실제 게임 캡처: 조각 전시 전환"><p>기존 엔진에서 캡처한 시전 직후 두 프레임입니다. 새로 그린 효과나 전투 재현 영상은 아닙니다.</p></article>
<article><h2>현재 실제 게임 초안 · 공예 전환</h2><img src="exhibit2.gif" alt="기존 실제 게임 캡처: 공예 전시 전환"><p>현재 1성 표식은 세 작품을 개별 도트로 구분하지 않습니다. 이번에는 1성부터 외형을 검토합니다.</p></article></div>
<h2>작품별 가호 · 기도술 I=12 예시</h2><table><tr><th>전시</th><th>현재 적용 효과</th></tr>
<tr><td>회화 · 기본 전시</td><td>피해를 준 살아 있는 적에게 채색1중첩, 최대3 · 마지막 갱신 후6턴 유지.<br>이미 채색된 적을 다시 때리면 추가 마법 피해 1d(2+⌊I/6⌋) → 1~4.<br>추가 피해가 중첩 수만큼 배증하지는 않습니다. 채색은 3성 폭발에도 사용합니다.</td></tr>
<tr><td>조각</td><td>AC +2+⌊I/9⌋ → +3.</td></tr>
<tr><td>공예</td><td>직접 일반 공격으로 적을 처치하면 HP 2+⌊I/6⌋ → 4 회복.<br>회복 재발동 간격2턴.</td></tr></table>
<p>각 작품에 대응하는 3성 권능을 쓰면 해당 작품은 회복 시간 동안 1성 가호도 쉬어갑니다. 그때 다른 작품으로 전환할 수 있습니다.</p>
<p>루이 1·3·5성 확정 완료. 현재 라덴 1성 검토 중입니다. 22신 시각 작업을 먼저 끝낸 뒤 중간 패시브·성급 배치를 재검토하는 계획은 유지합니다.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
article='''<article id="raden" data-god="raden"><h2>라덴 <small>1성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">1성 · 조각 전시</option><option value="1">1성 · 공예 전시</option></select><p class="scene-note">기존 실제 게임 캡처 · 시전 직후 두 프레임</p><img class="scene" src="clips/raden-tier1-option1-8.gif"><p>회화: 추가 피해·채색 / 조각: AC / 공예: 처치 회복. 전환 MP1·신앙0·1턴. 가호 신앙30 해금, 최소 기도술 없음.</p><p><a href="../raden-review01/index.html#tier1">효과·수치·실제 캡처 보기</a></p><label>피드백<textarea data-feedback="raden"></textarea></label></article>'''
text=re.sub(r'<article id="raden".*?</article>',lambda _:article,text,count=1,flags=re.S)
data['raden']=clips
m=re.search(r'const data=(.*?);function choose',text)
text=text[:m.start(1)]+json.dumps(data,ensure_ascii=False)+text[m.end(1):]
text=text.replace("location.hash.slice(1)||'lui'","location.hash.slice(1)||'raden'")
gallery.write_text(text,encoding='utf-8')

def update(d):
    for key in ['approvedGods']:
        if key in d and 'lui' not in d[key]:d[key].append('lui')
    if 'draftGods' in d:d['draftGods']=[g for g in d['draftGods'] if g!='lui']
    d.update(currentGod='raden',currentVisualReviewGod='raden',currentVisualReviewTier=1,currentVisualReview=review+'#tier1',next='Review Raden tier1. Lui tiers1/3/5 approved on 2026-10-28.')
    if 'review' in d:d['review']=review
    if 'tierApprovals' in d:
        d['tierApprovals'].setdefault('lui',{}).update(approved=[1,3,5],pending=[],pendingRevision=None,feedback='오호 그럼 그다음신으로',tier5Revision='lui-wings02')
        d['tierApprovals']['raden']=dict(approved=[],pending=[1,3,5],pendingRevision='raden-review01')
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])

for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));update(d)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 라덴 1성 검토 시작 / 2026-10-28\n\n사용자 다음 신 진행 승인으로 루이 1·3·5성 전체 확정(lui-wings02). 완료16신, 남은6신: 라덴→하지메→스우→비비→소피아→메라. 현재 라덴 1성 이동 박물관. 기존 실제 엔진 캡처 두 개와 현재 소스 수치를 analysis/previews/raden-review01/index.html#tier1 에 정리. 새 전투 캡처/도트 변경 없음. 런타임은 lui-wings02 유지. 22신 시각 작업 우선 완료 후 중간 패시브/성급 재검토 계획 유지. 기존 10/22 ZIP은 갱신하지 않음.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Lui approved; Raden tier1 preview ready:',out/'index.html')
