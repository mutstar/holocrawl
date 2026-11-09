from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='mela-dispatch01';b=r/'analysis/native'/rev;o=r/'analysis/previews/mela-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/dispatch.json')
assert v['status']==proof['status']=='passed' and v['gods']==22
def frame(name):
 return Image.open(b/f'native/shots/dispatch-{name}.png').convert('RGB').crop((259,228,611,452)).resize((1056,672),Image.Resampling.NEAREST)
for f in range(4):
 ward=read(b/f'native/shots/dispatch-activate{f}.png-ward.json');assert ward['status']=='passed' and ward['cells']==25
 ray=read(b/f'native/shots/dispatch-beam{f}.png-cone.json');assert ray['status']=='passed' and ray['cells']==[1,3,6,6][f] and ray['range']==6
names=['before']+['activate'+str(f) for f in range(4)]+['beam'+str(f) for f in range(4)]+['empty','recharge','ended']
frames=[frame(n) for n in names];durations=[800,220,220,220,650,160,160,280,220,700,1100,1100]
frames[0].save(o/'dispatch01-full.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
frames[4].save(o/'dispatch01-active.png');frames[7].save(o/'dispatch01-beam.png')
activation=[frame(n) for n in ['before','activate0','activate1','activate2','activate3','ended']]
activation[0].save(o/'dispatch01-activation.gif',save_all=True,append_images=activation[1:],duration=[800,220,220,300,900,1000],loop=0,optimize=False)
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>메라5성 · 메라조 출동!</title><style>'''+css+'''</style><h1>메라5성 · 메라조 출동!</h1><p class="info">예정 해금:신앙120 / 최소 기도술 제한 없음<br>발동 MP6·신앙12·1턴 / I12:8.4턴 유지 / 종료 후15턴 재사용 대기</p><h2>출동·불씨3충전 → 강화 직선방사 → 불씨0 → 자동충전1 예시 → 종료</h2><img src="dispatch01-full.gif"><p>발밑의 작은 푸른 도깨비불 고리는 출동 유지 표시입니다. 옅은5×5 외곽은 자신·아군의 화염 보호와 소화 범위로, 적에게 지속 피해를 주는 장판이 아닙니다. 고리와 불줄기는 몹 아래에 표시합니다.</p><h2>출동 효과만 보기</h2><img src="dispatch01-activation.gif"><h2>기존 합의 효과·3불씨 환산 + 강화 사거리 제안</h2><table><tr><th>항목</th><th>효과</th></tr><tr><td>불씨</td><td>발동 즉시3개,유지 중4턴마다1개 자동충전. 최대3,발동 중 자연감쇠 정지</td></tr><tr><td>화염 저항</td><td>본인 rF추가+1. 1성 가호와 합계+2단계,장비·종족과 정상상한 적용</td></tr><tr><td>보호</td><td>본인 중심5×5의 보이는 자신·아군에게 화염 피해를 정상rF 적용 후50% 추가 감소. 물리·냉기·전기·지옥불·용암에는 적용하지 않음</td></tr><tr><td>자동 소화</td><td>발동 완료 즉시와매1턴,범위의 일반 화염구름 및 자신·아군의 점착화염 제거. 자동소화로 추가 불씨 획득 없음</td></tr><tr><td>강화 방사·범위 제안</td><td>3성 폭1·길이5 → 출동 중 폭1·길이6 직선관통. 이6칸은이번외형초안의새제안이며아직사용자확정전</td></tr><tr><td>강화 방사·피해</td><td>3d(6+⌊I/3⌋)+8H,화염·rF적용·AC무시. I12 H0/1/2/3:평균16.5/24.5/32.5/40.5</td></tr><tr><td>강화 방사·비용</td><td>별도3성권능 사용:MP3·신앙3·1턴·불씨전부소모,행동완료후3턴대기 유지. 자동발사는 아님</td></tr></table><p><b>실제 SDL 렌더러에 출동·불씨표시·강화방사·충전 외형단계를 준비해 찍은 시각 초안입니다.</b> 이번GIF에서 실제MP/신앙소모·보호감소·소화·자동충전·적피해는 실행하지 않았습니다. 불씨1개충전 장면은4턴경과를 실제로 재생한 장면도 아닙니다. 실제 메라는 아직 기존6열기·부채꼴 전투이며,새3불씨/직선/시각콜백은 미구현. 일반실행본su-five01유지.5×5보호범위·강화선1/3/6칸·상태/RNG보존·22신/복원검사통과.</p><p>도깨비불 고리 원화:built-in imagegen 생성,56~64px 그림을96px캔버스에배치·약49%불투명도로몹아래표시. 강화불줄기는승인3성의두꺼운불원화를192×32px로통합배치했습니다.</p><p><a href="tier3-beam02.html">확정3성 직선 도깨비불</a> · <a href="tier1-heat3-01.html">확정1성·3불씨안</a></p></html>'''
for name in ['index.html','tier5-dispatch01.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['mela']=[dict(tier=5,option=0,title='메라조 출동!',image='../mela-review01/dispatch01-full.gif',kind='실제 SDL 출동/강화방사/충전 시각 초안,전투미연결')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="mela".*?</article>','<article id="mela" data-god="mela"><h2>메라5성 · 메라조 출동!</h2><img class="scene" src="../mela-review01/dispatch01-full.gif"><p>신앙120해금/최소기도술없음/MP6·신앙12·1턴/I12유지8.4턴. 작은도깨비불고리·5×5화염보호범위·3불씨충전·강화직선방사·충전1예시. 강화사거리6칸은새외형제안. 실제보호/피해/충전/소화미실행.</p><p><a href="../mela-review01/tier5-dispatch01.html">출동단독GIF·효과·수치·범위제안</a></p><label>피드백<textarea data-feedback="mela"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/mela-review01/tier5-dispatch01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='mela',currentVisualReviewGod='mela',currentVisualReviewTier=5,currentVisualReview=review,melaVisualPreviewRevision=rev,melaPreviewBinarySha256=digest,next='Review final Mela tier5 dispatch aura,5x5fireward and proposed1x6 enhanced beam visuals. Tiers1/3 approved. All new Mela3heat/line combat and Sopia/Vivi caster changes remain unimplemented; runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('mela',{}).update(approved=[1,3],pending=[5],tier1Revision='mela-heat3-01',tier3Revision='mela-beam02',tier5Preview=rev,scope='Final tier5 visual review; six-cell enhanced range is proposal,combat conversion pending')
 d['melaDispatchDraft']=read(r/'analysis/design/mela-dispatch01.json')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,art=read(r/'assets/holocrawl'/rev/'generation.json')),indent=2),encoding='utf-8')
note='# 메라5성 메라조출동 시각 초안 / 2026-10-30\n\n사용자「5성레츠고」. 작은푸른도깨비불고리56~64px/몹아래불투명도125/255,5×5보호범위외곽,열기0→출동3→강화직선방사소모0→충전1예시→종료. 강화폭1·길이6은신규외형제안/미승인. 3성승인5칸은유지. 실제SDL준비캡처이며MP/신앙/열기/피해/보호/소화/실제4턴경과없음. native보호25칸/방사1·3·6칸/상태/RNG/22신/복원통과. 실제전투기존6열기·부채꼴,새3불씨·직선·소피아/비비개편미구현,일반실행본su-five01유지. '+review+' 현재마지막5성외형검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Mela tier5 staged native dispatch VFX ready; gameplay unchanged')
