from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='vivi-attention01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/attention.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(b/f'native/shots/attention-{n}.png').convert('RGB').crop((243,196,531,420)).resize((576,448),Image.Resampling.NEAREST) for n in ['0','1','2','3','ended']]
frames[0].save(o/'attention.gif',save_all=True,append_images=frames[1:],duration=[900,1000,1000,1400,900],loop=0,optimize=False);frames[3].save(o/'three.png')
base=r/'analysis/previews/vivi-review01';css=re.search(r'<style>(.*?)</style>',(base/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>비비1성 · 스포트라이트 초안</title><style>'''+css+'''</style><h1>비비1성 · 스포트라이트</h1><p class="info"><b>공격 주문을 적중시켜 주목을 쌓는 마법형 개편의 시각 초안입니다.</b><br>예정 해금: 신앙30 · 최소 기도술 제한 없음<br>예정 비용: 자동 패시브 · 별도MP/신앙 소모 없음</p><h2>0 → 1 → 2 → 3중첩 → 사라짐</h2><img src="../vivi-attention01/attention.gif"><p>머리 대각선 위 분홍 보석1·2·3개가 주목 중첩입니다. 보석의 흰 반짝임으로 어두운 바닥과 구분합니다.32×32타일 안에 보석당8×10픽셀,머리 위8픽셀 올려 배치했습니다.</p><p><b>실제 SDL 게임 화면에 각 시각 단계를 준비해서 캡처한 것입니다.</b> 이 장면은 주문으로 자연스럽게 중첩을 쌓는 전투 시연이 아닙니다. 새 마법형 전투·수급 코드는 아직 적용하지 않았고, 실행본은 기존su-five01을 유지합니다.</p><h2>합의한1성 수치 · 구현 예정</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>획득</td><td>공격 주문 적중 시 주목+1,주문1회당최대1개,최대3중첩. 새 중첩은 다음 주문부터 적용</td></tr><tr><td>주문 피해</td><td>중첩당3+⌊I/12⌋%. 기도술I12:1/2/3중첩→+4/+8/+12%</td></tr><tr><td>유지</td><td>4턴 동안 공격 주문을 적중시키지 않으면 주목 소멸</td></tr><tr><td>제외</td><td>소환수·독·구름 등 지속 피해는 중첩 획득 제외</td></tr><tr><td>기존 효과 교체</td><td>기존 메이크업의MP2시전·은밀도절반·투명제한은 새 개편에서 제거 예정</td></tr></table><p>이번 작업은 생성 보석 도트와 테스트 전용 시각 분기만 추가했습니다.0·1·2·3표시 및 정리,RNG/전투상태 보존,22신 회귀·저장 복원 검증 통과. 현재 비비1성 시각 검토 중.3·5성 새 컨셉 연출은 아직 제작 전입니다.</p></html>'''
for name in ['index.html','tier1.html','tier1-attention01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['vivi']=[dict(tier=1,option=0,title='스포트라이트 · 주목 중첩',image='../vivi-attention01/attention.gif',kind='실제 SDL 시각 단계 초안·전투 미적용')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="vivi" data-god="vivi"><h2>비비 <small>1성 · 시각 초안 검토 중</small></h2><img class="scene" src="../vivi-attention01/attention.gif"><p>분홍 보석1·2·3개로 주목 표시. 예정효과:공격주문 적중 시 중첩, I12주문피해+4/+8/+12%,4턴미적중소멸. 자동패시브·별도소모없음,신앙30해금·최소기도술없음.</p><p>실제 렌더러에 단계를 준비한 초안이며 새 전투 코드는 아직 미적용.</p><p><a href="../vivi-review01/tier1-attention01.html">효과·수치·시각 초안</a></p><label>피드백<textarea data-feedback="vivi"></textarea></label></article>'
t=re.sub(r'<article id="vivi".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/vivi-review01/tier1-attention01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
concept=dict(status='approved-design-not-implemented',tier1=dict(name='Spotlight',stacks=3,bonusPerStack='3+floor(I/12)%',expireAut=40,oneGainPerDamagingCast=True),tier3=dict(name='Encore',mp=2,piety=3,actionAut=5,echoPercent='40+10*consumedStacks+floor(I/6)',armAut=40,cooldownAut=50),tier5=dict(name='Grand finale',mp=6,piety=12,actionAut=10,durationAfterCastAut='60+2*I',cooldownAfterEndAut=150,burst='2d(5+floor(I/3))',radius=1,oneBurstDamagePerVictimPerCast=True))
def update(d):
 d.update(currentGod='vivi',currentVisualReviewGod='vivi',currentVisualReviewTier=1,currentVisualReview=review,viviCasterDraft=concept,viviVisualPreviewRevision=rev,viviPreviewBinarySha256=digest,next='Review Vivi tier1 gem visuals. Caster design approved, combat implementation pending; normal runtime unchanged (su-five01).')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('vivi',{}).update(approved=[],pending=[1,3,5],tier1Preview=rev,pendingRevision=rev)
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,design=concept),indent=2),encoding='utf-8')
note='# 비비 마법형 설계 승인·1성 시각 초안 / vivi-attention01 / 2026-10-29\n\n사용자「좋아 이펙트찍어봐」.앞선1성주목/3성앙코르/5성피날레 수치안 승인,상세는 상태JSON의viviCasterDraft.이번은1성분홍보석1/2/3개 시각초안만.8×10보석/32타일/머리위8픽셀.테스트전용props로0→1→2→3→0준비후 실제SDL캡처,RNG/상태보존·22신/복원통과.전투·주문중첩·신규권능 미적용,런타임su-five01유지(프리뷰바이너리배포안함). '+review+' 현재1성시각검토중.이전메이크업페이지는새초안설명으로교체,수치가게임에적용됐다고안내하지말것.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=r/'BALANCE_WORKPLAN.md';p.write_text('\n## 비비 마법형 상세안 승인 / 2026-10-29\n\n'+json.dumps(concept,ensure_ascii=False,indent=2)+'\n\n현재는시각초안만제작.전투미적용.\n'+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Vivi staged attention visual ready; normal runtime unchanged')
