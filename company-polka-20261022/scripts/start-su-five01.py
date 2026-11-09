from pathlib import Path
from PIL import Image
import json,re,shutil,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='su-five01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/tide.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(b/f'native/shots/tide-{n}.png').convert('RGB').crop((179,164,627,484)).resize((896,640),Image.Resampling.NEAREST) for n in ['before','cast0','cast1','active','pulse','left','return','ended']]
frames[0].save(o/'tide.gif',save_all=True,append_images=frames[1:],duration=[900,300,400,900,850,900,900,1400],loop=0,optimize=False);frames[3].save(o/'active.png')
base=r/'analysis/previews/su-review01'
css=re.search(r'<style>(.*?)</style>',(base/'tier3-wave03.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스우5성 · 만조</title><style>'''+css+'''</style><h1>스우5성 · 만조</h1><p class="info"><b>주변2칸(최대5×5)을 실제 얕은 물로 만들고, 영역 안 물 위의 적에게 지속 피해를 줍니다. 물 영역이 이동을 따라옵니다.</b><br>해금: 신앙120 · 최소 기도술 제한 없음<br>비용: MP6·신앙12·행동1턴<br>기도술12: 시전 완료 후8.4턴 유지, 종료 후15턴 재사용 대기</p><h2>발동 → 물 영역 → 지속 피해 → 실제 좌우 이동 → 종료</h2><img src="../su-five01/tide.gif"><p>실제 엔진 캡처입니다. 좌우 이동은 실제 이동 명령으로 진행했습니다. 기존5성 시전 이펙트 초안을 유지했고, 실제 물 영역은 기본 얕은 물 타일입니다. 시전 이펙트와 물 영역을 구분해서 확인해 주세요.</p><h2>현재 효과·수치</h2><table><tr><th>항목</th><th>효과</th></tr><tr><td>영역</td><td>본인 주변2칸. 보이는 일반 바닥을 얕은 물로 변경. 벽·다른 임시 지형 제외. 이동하면 벗어난5성 물은 복구하고 새 영역을 물로 변경</td></tr><tr><td>지속</td><td>시전 완료 후6+0.2I턴. I12=8.4턴</td></tr><tr><td>지속 피해</td><td>매1턴마다2d(3+⌊I/6⌋). I12=2d5,2~10·평균6(AC 전). 별도 명중 굴림 없음. 시전 완료1턴 후부터 첫 피해</td></tr><tr><td>피해 대상</td><td>주변2칸 안, 보이는 물 위의 적대 몹. 아군·본인 제외. 영역 밖 적 제외</td></tr><tr><td>3성 강화</td><td>처음부터3줄 폭, 피해+3+⌊I/3⌋, 밀치기2칸. I12:2d11+7,9~29·평균19(AC 전). 사용 시 별도MP3·신앙3 필요</td></tr><tr><td>본인 가호</td><td>스우 신도는 자연/생성 얕은 물의 이동 지연·근접 헛손질 면제. 깊은 물은 기존 규칙</td></tr><tr><td>종료·보존</td><td>5성 물은 원래 지형으로 복구. 자연 물과 아직 지속 중인1성 웅덩이는 유지</td></tr></table><p>I는 기도술. 신앙은 해금에 사용되며 피해·지속시간에 별도 배율을 주지 않습니다. 기도술12 이번 시연 누적 실제 피해: 적A '''+str(proof['damageA'])+''' / 적B '''+str(proof['damageB'])+''' (AC·난수 적용 결과).</p><p>비용·지속·지속 피해·실제 이동·영역 밖 무피해·자연 물 보존·종료 검증 및22신 회귀/저장 복원 검사 통과. 현재5성 검토 중.</p><p><a href="tier3-wave03.html">확정된3성</a> · <a href="tier1-grace01.html">확정된1성</a></p></html>'''
for name in ['index.html','tier5-review01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['su']=[dict(tier=5,option=0,title='만조',image='../su-five01/tide.gif',kind='실제 발동·지속 피해·좌우 이동·종료')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="su" data-god="su"><h2>스우 <small>5성 · 검토 중</small></h2><img class="scene" src="../su-five01/tide.gif"><p>주변2칸 실제 얕은 물이 본인 이동을 따라옴. MP6·신앙12·1턴. 신앙120 해금, 최소 기도술 없음. I12:시전 후8.4턴,매1턴2d5 피해(AC 전). 3성은2d11+7·2칸 밀치기로 강화.</p><p><a href="../su-review01/tier5-review01.html">효과·수치·실제 시연</a></p><label>피드백<textarea data-feedback="su"></textarea></label></article>'
t=re.sub(r'<article id="su".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review='analysis/previews/su-review01/tier5-review01.html'
def update(d):
 d.update(currentGod='su',currentVisualReviewGod='su',currentVisualReviewTier=5,currentVisualReview=review,playBinarySha256=digest,next='Review Su tier5. Su tiers1/3 approved; tier5 pending. 18 gods complete.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('su',{}).update(approved=[1,3],pending=[5],tier5Preview=rev,pendingRevision=rev)
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,artChanged=False,nativeProof=proof,validation=v),indent=2),encoding='utf-8')
note='# 스우5성 만조 검토 / su-five01 / 2026-10-29\n\n스우1·3성 승인 유지.5성 실제 발동/주변2칸 얕은 물/지속피해/실제 좌우 이동/만료 캡처.기존5성 시전도트·전투 유지. MP6/신앙12/1턴,I12시전후8.4턴·매1턴2d5(AC적용),종료후15턴대기.3성강화+7피해·2칸밀치기·시작부터폭3칸,별도3성비용.비용·지속피해·이동영역복구·범위밖무피해·자연물보존·종료 및22신/저장복원통과. fixture추가 실행본갱신. '+review+' 현재5성검토중.완료18신유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su tier5 ready:',proof)
