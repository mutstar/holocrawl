from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='hajime-dive01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/dive.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(b/f'native/shots/dive-{n}.png').convert('RGB').crop((275,228,563,436)).resize((576,416),Image.Resampling.NEAREST) for n in ['before','cast0','cast1','after']]
frames[0].save(o/'dive.gif',save_all=True,append_images=frames[1:],duration=[1100,450,450,1300],loop=0,optimize=False);frames[2].save(o/'cast.png')
base=r/'analysis/previews/hajime-review01';css=re.search(r'<style>(.*?)</style>',(base/'tier1.html').read_text(encoding='utf-8'),re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>하지메 · 3성 파고들기</title><style>'''+css+'''</style><h1>하지메 · 3성 파고들기</h1><p class="info"><b>2~3칸 떨어진 적 옆으로 최대2칸 이동하고, 박자를 모두 소모해 한 번 타격합니다.</b><br>해금: 신앙★★★75 · 최소 기도술 제한 없음<br>비용: MP3·신앙3·행동1턴<br>재사용: 사용 시작부터4턴 → 시전 완료 후3턴</p><h2>3박자 준비 → 접근·타격 → 소모 · 실제 게임</h2><img src="../hajime-dive01/dive.gif" alt="실제 하지메3성: 두 칸 접근·타격·박자 소모"><p>시연은3박자를 준비한 상태로 시작합니다. 현재 실제 권능으로 두 칸 이동하고 타격을 판정한 뒤, 박자가 사라지는 모습을 캡처했습니다. 이동은 게임에서 즉시 처리되며, 중간 경로를 따라 미끄러지는 연속 애니메이션은 아직 없습니다.</p><p>몹 주변 파랑·보라 고리는 현재3성 시전 이펙트 초안입니다. 고리 크기가 실제 공격 범위를 뜻하지는 않습니다. 이 권능은 선택한 적 하나를 공격합니다.</p><h2>현재 수치 · 기도술I=12</h2><p>권능 피해: 2d(6+⌊I/3⌋)+3×소모 박자<br>권능 명중: 20+I+2×소모 박자<br>적의 AC가 피해를 줄이고, 명중 판정에 실패할 수 있습니다.</p><table><tr><th>소모 박자</th><th>피해 범위 · 평균</th><th>명중 수치</th></tr><tr><td>0</td><td>2~20 · 평균11</td><td>32</td></tr><tr><td>1</td><td>5~23 · 평균14</td><td>34</td></tr><tr><td>2</td><td>8~26 · 평균17</td><td>36</td></tr><tr><td>3</td><td>11~29 · 평균20</td><td>38</td></tr></table><p>위 명중 수치는 명중률(%)이 아닙니다. 피해는 AC 적용 전입니다. 명중 여부와 관계없이 박자·MP·신앙은 소모됩니다.</p><h2>이동 조건</h2><p>보이는 적이2~3칸 거리에 있어야 합니다. 적 옆의 빈 바닥 칸을 골라 최대2칸 경로로 접근하며, 벽이나 다른 개체가 길을 막으면 사용할 수 없습니다. 붙잡힌 상태에서는 사용할 수 없습니다. 이미 인접한 적에게는 사용할 수 없습니다.</p><p>무기의 일반 공격을 한 번 더 하는 방식이 아니라 별도의 권능 피해입니다. 1성의 일반 근접 공격 피해 보너스를 중복해서 더하지 않습니다. 5성 중 추가 주변 공격은5성 검토에서 따로 확인합니다.</p><p><a href="tier1-rhythm03.html">확정된1성·실제 박자 축적 보기</a></p><p>현재3성 이펙트·사용감 검토 중. 이번 전환에서 전투 수치·도트는 변경하지 않았습니다.</p></html>'''
for name in ['index.html','tier3-review01.html']:(base/name).write_text(page,encoding='utf-8')
(o/'index.html').write_text(page.replace('href="tier1-rhythm03.html"','href="../hajime-review01/tier1-rhythm03.html"'),encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['hajime']=[dict(tier=3,option=0,title='파고들기',image='../hajime-dive01/dive.gif',kind='실제 두 칸 접근·타격·박자 소모')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="hajime" data-god="hajime"><h2>하지메 <small>3성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">3성 · 파고들기</option></select><p class="scene-note">실제 두 칸 접근·타격·박자 소모</p><img class="scene" src="../hajime-dive01/dive.gif"><p>MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음. 기도술12·3박자: 평균20피해(AC 전), 시전 완료 후 재사용3턴.</p><p><a href="../hajime-review01/tier3-review01.html">효과·조건·상세 수치</a></p><label>피드백<textarea data-feedback="hajime"></textarea></label></article>'
t=re.sub(r'<article id="hajime".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(currentGod='hajime',currentVisualReviewGod='hajime',currentVisualReviewTier=3,currentVisualReview='analysis/previews/hajime-review01/tier3-review01.html',playBinarySha256=digest,next='Review Hajime tier3. Tier1 approved; tiers3/5 pending.')
 if 'review' in d:d['review']='analysis/previews/hajime-review01/tier3-review01.html'
 if 'tierApprovals' in d:d['tierApprovals']['hajime'].update(approved=[1],pending=[3,5],tier1Revision='hajime-rhythm03',tier3Preview=rev,pendingRevision=rev,feedback='굿 그다음3성')
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,artChanged=False,nativeProof=proof,validation=v),indent=2))
note='# 하지메1성 확정·3성 파고들기 검토 / hajime-dive01 / 2026-10-28\n\n1성 실제 음표1/2/3 축적·소모 승인(hajime-rhythm03). 현재3성:3박자 준비 상태에서 실제 권능으로 거리3칸 적에게2칸 접근·타격·박자소모 캡처. 비용/쿨다운/위치/RNG 검증 및22신·복원 검사 통과. 연속 이동경로 애니메이션 없음. 기존3성 고리 이펙트/전투 수치 유지. 캡처 fixture 포함 실행본 갱신. 페이지 analysis/previews/hajime-review01/tier3-review01.html. 3·5성 미승인.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Hajime tier1 approved; tier3 preview ready',proof)
