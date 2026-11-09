from pathlib import Path
from PIL import Image
import json,re,shutil
r=Path(__file__).resolve().parents[1];rev='raden-tier3-review01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
validation=read(b/'capture-validation.json');assert validation['status']=='passed' and validation['gods']==22
o.mkdir(parents=True,exist_ok=True)
for i in range(3):
 files=sorted((b/'native/shots').glob(f'raden-tier3-option{i}-*-frame0.png'));assert files,i
 stem=files[0].name.removesuffix('-frame0.png')
 frames=[Image.open(b/f'native/shots/{stem}-frame{f}.png').convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for f in range(2)]
 frames[0].save(o/f'ability{i}.gif',save_all=True,append_images=frames[1:],duration=650,loop=0,optimize=False)
 frames[1].save(o/f'ability{i}.png')
base=r/'analysis/previews/raden-review01';css=re.search(r'<style>(.*?)</style>',(base/'index.html').read_text(encoding='utf-8'),re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>라덴 · 3성 소장품 발동</title><style>'''+css+'''</style><h1>라덴 · 3성 소장품 발동</h1><section id="tier3"><p class="info"><b>현재 전시 중인 작품에 맞춰 세 가지 권능 중 하나를 사용합니다.</b><br>해금: 신앙 ★★★75 · 최소 기도술 제한 없음<br>공통 비용: MP3 · 신앙3 · 행동1턴<br>1성: 붓·은빛 조각상·옥색 공예 문양 확정. 아래는 현재 3성 효과의 새 엔진 캡처입니다.</p><div class="cards">
<article><h2>회화 · 채색 폭발</h2><img src="../raden-tier3-review01/ability0.gif" alt="실제 회화 채색 폭발 시전"><p>사거리5칸 내 채색된 적을 골라, 해당 적의 채색을 모두 소모하고 <b>주변1칸(3×3)</b>을 폭발시킵니다.</p><p>피해: 2d(6+⌊I/3⌋)+4×채색 수<br>I=12·3중첩: <b>2d10+12 → 14~32</b> (감쇠 전).<br>범위 안에 본인이 있으면 본인도 피해를 받습니다.</p><p>회화 가호 회복: 사용 시작부터5턴, 시전 완료 직후4턴 남음. 그동안 회화의 채색·추가 피해도 쉽니다.</p></article>
<article><h2>조각 · 조각의 파동</h2><img src="../raden-tier3-review01/ability1.gif" alt="실제 조각 파동 시전"><p>선택한 방향으로 <b>폭1칸·길이3칸</b>의 직선 파동. 맞은 적에게 피해를 주고 살아 있으면 뒤로1칸 밀어냅니다. 벽·빈칸 여부에 따라 이동이 막힐 수 있습니다.</p><p>피해: 2d(5+⌊I/3⌋)<br>I=12: <b>2d9 → 2~18</b> (감쇠 전).</p><p>조각 가호 회복: 사용 시작부터5턴, 시전 완료 직후4턴 남음. 그동안 조각의 AC 가호도 쉽니다.</p></article>
<article><h2>공예 · 옻칠의 가호</h2><img src="../raden-tier3-review01/ability2.gif" alt="실제 공예 보호막 시전"><p><b>피해를 흡수하는 보호막</b>을 얻습니다. 보호량 10+⌊2I/3⌋ → I=12에서 <b>18</b>.<br>시전 완료 후5턴 유지하거나 보호량을 다 쓰면 소멸.</p><p>동시에 독 지속시간5턴 감소, 혼란·감속·공포의 남은 시간 절반 감소.</p><p>공예 가호 회복: 사용 시작부터5턴, 시전 완료 직후4턴 남음. 그동안 처치 회복도 쉽니다. 보호막이 남아 있으면 재시전할 수 없습니다.</p></article></div>
<p>위 GIF는 실제 시전 직후 두 프레임입니다. 파동 이동·넉백·보호막 흡수까지 이어지는 연속 재생은 아닙니다. 현재 이펙트 외형을 먼저 확인하는 초안입니다.</p><p><a href="brush03.html#tier1">확정된 1성·붓/조각/공예 전환 보기</a></p></section></html>'''
(base/'tier3.html').write_text(page,encoding='utf-8');(base/'index.html').write_text(page,encoding='utf-8');(o/'index.html').write_text(page.replace('href="brush03.html#tier1"','href="../raden-review01/brush03.html#tier1"'),encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['raden']=[dict(tier=3,option=i,title=n,image=f'../{rev}/ability{i}.gif',kind='실제 3성 시전 직후') for i,n in enumerate(['채색 폭발','조각의 파동','옻칠의 가호'])];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="raden" data-god="raden"><h2>라덴 <small>3성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">3성 · 채색 폭발</option><option value="1">3성 · 조각의 파동</option><option value="2">3성 · 옻칠의 가호</option></select><p class="scene-note">실제 3성 시전 직후</p><img class="scene" src="../raden-tier3-review01/ability0.gif"><p>MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음.</p><p><a href="../raden-review01/tier3.html#tier3">세 가지 효과·상세수치 보기</a></p><label>피드백<textarea data-feedback="raden"></textarea></label></article>'
t=re.sub(r'<article id="raden".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(currentGod='raden',currentVisualReviewGod='raden',currentVisualReviewTier=3,currentVisualReview='analysis/previews/raden-review01/tier3.html#tier3',next='Review Raden tier3 exhibits. Tier1 approved; tiers3/5 pending.')
 if 'review' in d:d['review']='analysis/previews/raden-review01/tier3.html'
 if 'tierApprovals' in d:d['tierApprovals']['raden'].update(approved=[1],pending=[3,5],tier1Revision='raden-vfx03',tier3Preview=rev,pendingRevision=rev,feedback='라덴 1성은 이걸로하고 3성으로가자')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 라덴 1성 확정·3성 검토 시작 / 2026-10-28\n\n1성 붓·은빛 조각상·옥색 공예 전환 승인(raden-vfx03). 현재3성 소장품 발동: 회화 채색 폭발/조각 파동/공예 가호. 최신 실행본으로 실제 세 분기 시전 직후 새 캡처,22신·복원 검사 통과. 외형/전투 수치/실행본 변경 없음. 새 페이지 analysis/previews/raden-review01/tier3.html#tier3. 3·5성 미승인.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
(b/'preview-validation.json').write_text(json.dumps(dict(status='passed',revision=rev,nativeCasts=3,artChanged=False,combatChanged=False,validation=validation),indent=2))
print('Raden tier1 approved; tier3 ready')
