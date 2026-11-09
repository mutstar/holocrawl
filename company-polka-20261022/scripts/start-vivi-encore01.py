from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='vivi-encore01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/encore.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
names=['stacks','ready0','ready1','spell0','spell1','echo0','echo1','ended']
frames=[Image.open(b/f'native/shots/encore-{n}.png').convert('RGB').crop((243,196,595,420)).resize((704,448),Image.Resampling.NEAREST) for n in names]
frames[0].save(o/'encore.gif',save_all=True,append_images=frames[1:],duration=[1100,650,650,180,180,230,450,1100],loop=0,optimize=False);frames[1].save(o/'ready.png');frames[6].save(o/'echo.png')
base=r/'analysis/previews/vivi-review01';css=re.search(r'<style>(.*?)</style>',(base/'tier1-lipstick01.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>비비3성 · 앙코르 초안</title><style>'''+css+'''</style><h1>비비3성 · 앙코르</h1><p class="info"><b>주목을 모두 소모해 다음 공격 주문에 추가 타격을 예약하는 권능의 시각 초안입니다.</b><br>예정 해금: 신앙75 · 최소 기도술 제한 없음<br>예정 비용: MP2·신앙3·0.5턴 · 주목 최소1개 필요</p><h2>주목 소모 → 대기 → 일반 타격 예시 → 분홍 잔상 타격</h2><img src="../vivi-encore01/encore.gif"><table><tr><th>표시</th><th>의미</th></tr><tr><td>세워진 립스틱1·2·3개</td><td>1성 주목 중첩. 이번 예시는3중첩 준비</td></tr><tr><td>기울어진 립스틱 하나</td><td>주목을 소모한 뒤 다음 주문의 앙코르 대기 표시</td></tr><tr><td>몹 몸통의 분홍 겹친 잔상</td><td>첫 주문 피해 뒤 추가 타격이 들어간다는 연출</td></tr></table><p><b>실제 SDL 렌더러에 각 단계를 준비한 시각 초안입니다.</b> 중간 일반 타격은 특정 주문이 아닌 공통 타격 표시로 대신했습니다. 주문 시전·MP/신앙 차감·중첩 소모·추가 피해는 아직 새 전투 코드에 연결되지 않았습니다. 이번 장면에서 몹HP는 줄지 않습니다.</p><h2>합의한 수치 · 구현 예정</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>소모</td><td>현재 주목을 모두 소모.최소1개</td></tr><tr><td>추가 타격</td><td>원래 준 피해의40+10×소모중첩+⌊I/6⌋%. I12:1/2/3중첩→52/62/72%</td></tr><tr><td>추가 소모</td><td>앙코르 추가 타격 자체는MP를 다시 쓰지 않음. 원래 공격 주문의MP는 정상 소모</td></tr><tr><td>예약·대기</td><td>예약4턴 유지,사용 후5턴 재사용 대기</td></tr><tr><td>복제 제한</td><td>피해만 추가. 상태이상·소환·지형 효과는 복제하지 않음</td></tr></table><p>각 잔상은32×32타일 안에서16×18→20×22픽셀로 표시합니다. 1성 립스틱 시각 승인,3성 시각 검토 중. 전투 구현은 미완료이고 일반 실행본은su-five01을 유지합니다. 시각 단계·RNG/상태 보존 및22신 회귀·저장 복원 검사 통과.</p><p><a href="tier1-lipstick01.html">확정된1성 립스틱 초안</a></p></html>'''
for name in ['index.html','tier3-encore01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['vivi']=[dict(tier=3,option=0,title='앙코르',image='../vivi-encore01/encore.gif',kind='실제 SDL 단계별 시각 초안·피해 미적용')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="vivi" data-god="vivi"><h2>비비 <small>3성 · 시각 초안 검토 중</small></h2><img class="scene" src="../vivi-encore01/encore.gif"><p>주목소모→기울어진 립스틱 대기→일반 타격 예시→분홍 잔상. 예정:MP2·신앙3·0.5턴,신앙75해금,최소기도술없음. I12·3중첩:다음 공격주문 피해72%추가.</p><p>단계를 준비한 시각 초안이며 실제 추가 피해는 미구현.</p><p><a href="../vivi-review01/tier3-encore01.html">수치·표시 의미·구현 상태</a></p><label>피드백<textarea data-feedback="vivi"></textarea></label></article>'
t=re.sub(r'<article id="vivi".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest();review='analysis/previews/vivi-review01/tier3-encore01.html'
def update(d):
 d.update(currentGod='vivi',currentVisualReviewGod='vivi',currentVisualReviewTier=3,currentVisualReview=review,viviVisualPreviewRevision=rev,viviPreviewBinarySha256=digest,next='Review Vivi tier3 Encore VFX. Tier1 lipstick visuals approved. Caster combat not implemented; normal runtime unchanged (su-five01).')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('vivi',{}).update(approved=[1],pending=[3,5],tier1Revision='vivi-lipstick01',tier3Preview=rev,pendingRevision=rev,feedback='굿 그다음작업')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v),indent=2),encoding='utf-8')
note='# 비비1성 시각 확정·3성 앙코르 초안 / vivi-encore01 / 2026-10-29\n\n사용자「굿 그다음작업」으로1성립스틱표시승인.3성은주목3→기울어진립스틱대기→공통일반타격→분홍겹친잔상→소멸을 실제SDL에서준비캡처.정상주문/추가피해/비용/중첩소모미구현,대상HP불변확인.1성은시각승인만이며새마법형전투는전체미적용.새초안20×22이내/32타일,범용추가타격효과.22신/복원통과,프리뷰바이너리만빌드하고일반실행본su-five01유지. '+review+' 현재3성시각검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Vivi Encore staged VFX ready; caster combat remains unimplemented')
