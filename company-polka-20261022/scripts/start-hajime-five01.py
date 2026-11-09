from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='hajime-five01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/bancho.json');events=read(b/'native/shots/movement.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
def crop(name):return Image.open(b/f'native/shots/bancho-{name}.png').convert('RGB').crop((211,196,595,452)).resize((768,512),Image.Resampling.NEAREST)
frames=[crop(n) for n in ['before','cast0','cast1','active','wait','move1','move2','move3','move4','ended']]
frames[0].save(o/'bancho.gif',save_all=True,append_images=frames[1:],duration=[700,350,400,700,700,850,850,850,1000,900],loop=0,optimize=False)
frames[2].save(o/'cast.png');frames[8].save(o/'moving.png')
base=r/'analysis/previews/hajime-review01';prior=(base/'tier3-review01.html').read_text(encoding='utf-8');css=re.search(r'<style>(.*?)</style>',prior,re.S).group(1)
rows=''.join(f'<tr><td>{x["move"]}</td><td>{x["targetA"]}</td><td>{x["targetB"]}</td></tr>' for x in events)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>하지메 · 5성 반쵸 타임</title><style>'''+css+'''</style><h1>하지메 · 5성 반쵸 타임</h1><p class="info"><b>움직일 때 도착 지점 주변1칸의 적을 공격하는 리듬 상태입니다.</b><br>해금: 신앙★★★★★120 · 최소 기도술 제한 없음<br>비용: MP6·신앙12·행동1턴<br>시전 완료 후6+0.2I턴 → I12에서8.4턴 유지<br>종료 후 재사용 대기15턴</p><h2>발동 → 대기 → 실제 이동 공격 → 종료</h2><img src="../hajime-five01/bancho.gif" alt="하지메5성 실제 발동·대기·네 번 이동·종료"><p>기존5성 시전 고리와 유지 표시를 최신 게임에서 캡처했습니다. 큰 파랑·보라 고리는 발동 이펙트, 주변1칸 바닥 문양은 이동 공격 상태의 범위 표시입니다. 실제 대기 시간은 GIF에서 줄였습니다.</p><h2>현재 효과와 수치</h2><table><tr><th>항목</th><th>적용 내용</th></tr><tr><td>발동 조건</td><td>자발적으로 이동한 뒤 도착 지점 주변1칸의 적마다1회 피해</td></tr><tr><td>피해</td><td>2d(4+⌊I/3⌋)<br>I12에서2d8 → 2~16 · 평균9, AC 적용 전</td></tr><tr><td>명중</td><td>별도 명중 판정 없이 피해 처리, 적의 AC로 감소</td></tr><tr><td>범위</td><td>본인 주변1칸(3×3 중 주변8칸). 인접 적 여러 마리 공격 가능</td></tr><tr><td>이동 속도</td><td>평소 이동 행동 비용 유지. 추가 MP·신앙 소모 없음</td></tr><tr><td>대기·제자리 근접 공격</td><td>5성 주변 피해가 자동으로 들어가지는 않음</td></tr><tr><td>1성 박자</td><td>조건에 맞는 이동이면 함께 축적. 최대3박자 유지</td></tr><tr><td>3성 파고들기와 연계</td><td>별도 MP3·신앙3을 내고3성을 쓰면, 도착 뒤 주변1칸에 같은5성 피해를 추가1회 적용</td></tr></table><p>강제 이동·혼란·행동 불가 상태에서 이 이동 공격은 발동하지 않습니다. 5성이 무기 일반 공격을 자동 반복하는 것은 아닙니다.</p><h2>이번 실제 시연 피해 · AC 적용 후</h2><p>가까운 적A/B와 범위 밖 적을 배치했습니다. 한 턴 대기에는 피해가 없고, 범위 밖 적은 네 번 이동 모두 피해0인 것을 검증했습니다. 아래 수치는 고정 피해가 아닌 이번 시연의 실제 결과입니다.</p><table><tr><th>이동</th><th>적A 피해</th><th>적B 피해</th></tr>'''+rows+'''</table><p><a href="tier3-review01.html">확정된3성</a> · <a href="tier1-rhythm03.html">확정된1성·박자 축적</a></p><p>현재5성 검토 중. 1·3성 승인, 이번 전환에서 전투 수치·도트는 변경하지 않았습니다.</p></html>'''
for name in ['index.html','tier5-review01.html']:(base/name).write_text(page,encoding='utf-8')
(o/'index.html').write_text(page.replace('href="tier3-review01.html"','href="../hajime-review01/tier3-review01.html"').replace('href="tier1-rhythm03.html"','href="../hajime-review01/tier1-rhythm03.html"'),encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['hajime']=[dict(tier=5,option=0,title='반쵸 타임',image='../hajime-five01/bancho.gif',kind='실제 발동·대기·이동 공격·종료')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="hajime" data-god="hajime"><h2>하지메 <small>5성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">5성 · 반쵸 타임</option></select><p class="scene-note">실제 발동·대기·이동 공격·종료</p><img class="scene" src="../hajime-five01/bancho.gif"><p>MP6·신앙12·1턴. 신앙120 해금, 최소 기도술 없음. I12:8.4턴 유지, 이동 후 주변1칸 적에게2d8 피해(AC 전).</p><p><a href="../hajime-review01/tier5-review01.html">효과·수치·실제 피해 보기</a></p><label>피드백<textarea data-feedback="hajime"></textarea></label></article>'
t=re.sub(r'<article id="hajime".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(currentGod='hajime',currentVisualReviewGod='hajime',currentVisualReviewTier=5,currentVisualReview='analysis/previews/hajime-review01/tier5-review01.html',playBinarySha256=digest,next='Review Hajime tier5. Tiers1/3 approved; tier5 pending.')
 if 'review' in d:d['review']='analysis/previews/hajime-review01/tier5-review01.html'
 if 'tierApprovals' in d:d['tierApprovals']['hajime'].update(approved=[1,3],pending=[5],tier3Revision='hajime-dive01',tier5Preview=rev,pendingRevision=rev,feedback='굿 괜찮네 5성으로가보자')
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,artChanged=False,nativeProof=proof,moves=events,validation=v),indent=2))
note='# 하지메3성 확정·5성 반쵸 타임 검토 / hajime-five01 / 2026-10-28\n\n하지메1·3성 승인. 5성 발동·대기·네 번 실제 이동 공격·종료 캡처. MP6/신앙12/1턴, I12시전후8.4턴, 이동 후 주변1칸2d8(AC적용). 대기 무피해·범위밖 무피해·주변 실제피해·종료 검증 및22신/복원 통과. 기존도트/전투수치 유지, fixture 포함 실행본 갱신. 페이지 analysis/previews/hajime-review01/tier5-review01.html. 5성 확인 대기, 다음신 스우는 승인 후.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Hajime tier5 ready',proof,events)
