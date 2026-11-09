from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='raden-five01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/exhibition.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(b/f'native/shots/exhibition-{n}.png').convert('RGB').crop((243,196,563,452)).resize((640,512),Image.Resampling.NEAREST) for n in ['before','cast0','cast1','active','ended']]
frames[0].save(o/'exhibition.gif',save_all=True,append_images=frames[1:],duration=[800,400,500,1300,900],loop=0,optimize=False)
frames[2].save(o/'cast.png');frames[3].save(o/'active.png')
base=r/'analysis/previews/raden-review01';prior=(base/'tier3-balance01.html').read_text(encoding='utf-8');css=re.search(r'<style>(.*?)</style>',prior,re.S).group(1)
details=re.search(r'<h2>5성 특별전 중.*?</table>',prior,re.S).group(0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>라덴 · 5성 특별전 개막</title><style>'''+css+'''</style><h1>라덴 · 5성 특별전 개막</h1><p class="info"><b>회화·조각·공예를 동시에 전시하고, 세 가지 3성 권능을 강화합니다.</b><br>해금: 신앙★★★★★120 · 최소 기도술 제한 없음<br>비용: MP6·신앙12·행동1턴<br>시전 완료 후 6+0.2I턴 → 기도술12에서8.4턴. 종료 후 재사용 대기15턴.</p><h2>발동 → 유지 → 종료 · 실제 게임</h2><img src="../raden-five01/exhibition.gif" alt="실제 특별전 발동·유지·종료"><p>기존 5성 시전 연출을 최신 게임에서 다시 캡처한 초안입니다. 가운데 큰 금빛·다색 고리는 시전 효과, 이후 플레이어 칸에 남는 문양은 특별전 유지 표시입니다. 유지·종료 장면 사이의 실제 대기 시간은 GIF에서 줄였습니다.</p><h2>특별전 중 함께 받는 1성 가호</h2><ul><li>회화: 채색 중첩 및 이미 채색된 적에게 추가 마법 피해.</li><li>조각: AC +2+⌊I/9⌋ → I12에서+3.</li><li>공예: 직접 일반 공격 처치 시 HP 2+⌊I/6⌋ → I12에서4 회복, 재발동 간격2턴.</li></ul><p>해당 작품의 3성 권능을 사용하면 그 작품의 가호는 기존 회복 시간 동안 쉽니다. 특별전 중에는 1성 전시 전환이 잠기며, 특별전 종료 후 원래 선택한 전시로 돌아갑니다.</p>'''+details+'''<p>회화·조각 피해는 AC 적용 전. 공예의 독 시간 감소·혼란/감속/공포 시간 절반 효과 유지. 강화 공예의 남은 보호막 시간은 특별전 종료와 별개입니다.</p><p><a href="tier3-balance01.html">확정된 3성 수치와 이펙트</a> · <a href="brush03.html">확정된 1성 전환</a></p><p>현재5성 외형 검토 중. 1·3성 확정, 전투 수치는 raden-balance01 유지.</p></html>'''
for name in ['index.html','tier5-review01.html']:(base/name).write_text(page,encoding='utf-8')
(o/'index.html').write_text(page.replace('href="tier3-balance01.html"','href="../raden-review01/tier3-balance01.html"').replace('href="brush03.html"','href="../raden-review01/brush03.html"'),encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['raden']=[dict(tier=5,option=0,title='특별전 개막',image='../raden-five01/exhibition.gif',kind='실제 발동·유지·종료')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="raden" data-god="raden"><h2>라덴 <small>5성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">5성 · 특별전 개막</option></select><p class="scene-note">실제 발동·유지·종료</p><img class="scene" src="../raden-five01/exhibition.gif"><p>MP6·신앙12·1턴. 신앙120 해금, 최소 기도술 없음. 세 전시 가호 동시 적용 및3성 강화.</p><p><a href="../raden-review01/tier5-review01.html">효과·수치 보기</a></p><label>피드백<textarea data-feedback="raden"></textarea></label></article>'
t=re.sub(r'<article id="raden".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(currentGod='raden',currentVisualReviewGod='raden',currentVisualReviewTier=5,currentVisualReview='analysis/previews/raden-review01/tier5-review01.html',playBinarySha256=digest,next='Review Raden tier5. Tiers1/3 approved; tier5 pending.')
 if 'review' in d:d['review']='analysis/previews/raden-review01/tier5-review01.html'
 if 'tierApprovals' in d:d['tierApprovals']['raden'].update(approved=[1,3],pending=[5],tier3Revision='raden-three04',combatRevision='raden-balance01',pendingRevision=rev,tier5Preview=rev,feedback='라덴 3성은 이걸로하고 5성으로가자')
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,artChanged=False,exhibition=proof,validation=v),indent=2))
note='# 라덴3성 확정·5성 검토 시작 / raden-five01 / 2026-10-28\n\n사용자 라덴3성 승인. 1·3성 확정,5성 미승인. 기존5성 발동·유지·종료를 최신 SDL에서 재캡처하고 비용/지속/종료/AC가호 검증. 3성·5성 강화 수치는 raden-balance01 유지, 아트 변경 없음. 신규 캡처 fixture 포함 실행본 배포. 미리보기 analysis/previews/raden-review01/tier5-review01.html. 다음신 이동은5성 승인 후.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Raden tiers1/3 approved, tier5 preview ready',proof)
