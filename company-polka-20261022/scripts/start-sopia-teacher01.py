from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='sopia-teacher01';b=r/'analysis/native'/rev;o=r/'analysis/previews/sopia-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
validation=read(b/'capture-validation.json');proof=read(b/'native/shots/teacher.json')
assert validation['status']==proof['status']=='passed' and validation['gods']==22 and proof['mpUnchanged']
def frame(name):
 return Image.open(b/f'native/shots/teacher-{name}.png').convert('RGB').crop((259,196,579,420)).resize((960,672),Image.Resampling.NEAREST)
for phase,durations in [('mana',[700,140,140,140,160,900]),('book',[700,160,160,650,250,900])]:
 frames=[frame('before')]+[frame(phase+str(f)) for f in range(4)]+[frame(phase+'-ended')]
 frames[0].save(o/f'teacher01-{phase}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
 frames[3].save(o/f'teacher01-{phase}.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>소피아1성 · 박사의 가르침</title><style>'''+css+'''</style><h1>소피아1성 · 박사의 가르침</h1><p class="info">개편한1성:행성 고리를 마법 지원으로 교체<br>예정 해금:신앙30 / 최소 기도술 제한 없음 / 패시브·선물, 별도 발동 비용 없음</p><h2>MP 회복 · 작은 별빛이 머리 쪽으로 흡수</h2><img src="teacher01-mana.gif"><p>직접 공격 주문으로 적을 처치했을 때의 회복 표시 초안. 별빛만 잠깐 들어오며 지속 버프 표시는 남지 않습니다.</p><h2>주문 선물 · 보라색 연구서가 펼쳐짐</h2><img src="teacher01-book.gif"><p>머리 오른쪽 대각선 위로 작은 연구서가 나타났다 사라집니다. 선물 도착을 알리는 효과이며, 실제 주문3개 선택 메뉴는 아직 연결하지 않았습니다.</p><h2>합의한 효과·수치 · 전투 코드 미적용</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>MP 회복</td><td>직접 공격 주문 처치 시1+⌊I/12⌋ MP, 최대3. I12:2MP</td></tr><tr><td>회복 상한</td><td>광역·다단히트도 시전당 한 번. 그 주문이 실제 소비한 MP까지만 회복</td></tr><tr><td>처치 조건</td><td>자연 생성 경험치 적을 MP소비 직접 공격 주문으로 처치. 소환수·독·구름·지연피해·권능·MP0 주문 제외</td></tr><tr><td>주문 선물</td><td>신앙45·75·110·150에서 각각 한 번. 현재 익힌 학파·배울 수 있는 레벨에 맞는 미습득 주문3개 중1개 선택</td></tr><tr><td>학습</td><td>선택한 주문은 정상 암기 규칙과 주문 레벨을 사용. 배운 주문 제외. 유효 후보가 없으면 선물을 유예</td></tr><tr><td>중복 방지</td><td>각 선물 문턱은 게임당 한 번. 개종·신앙 재상승으로 다시 받지 않음</td></tr></table><p><b>두 GIF는 실제 SDL 렌더러에 효과 단계를 준비해 촬영한 외형 초안입니다.</b> 주문 처치나 실제 MP회복·주문 지급·선택 메뉴가 실행된 영상은 아닙니다. 이번 캡처에서 MP·몬스터HP·월드·RNG는 변하지 않았습니다. 새1·3·5성 캐스터 전투 미구현, 일반실행본su-five01 유지. 소피아3성gravity04·5성bigbang02 외형은 승인 완료, 현재 새1성 외형 검토 중.</p><p>책 원화:built-in imagegen 생성 / 실제 크기 최대24×16px. MP별빛은 기존 생성된 빅뱅 원화의 중심 별을 재사용, 최대10px. 머리 대각선 위 native offset(+14,-24), 단일앵커 검증. 22신·저장 복원 검사 통과.</p><p><a href="tier3-gravity04.html">확정3성 중력장</a> · <a href="tier5-bigbang02.html">확정5성 빅뱅</a> · <a href="tier1.html">개편 전 행성 고리 참고</a></p></html>'''
for name in ['index.html','tier1-teacher01.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['sopia']=[dict(tier=1,option=0,title='박사의 가르침 · MP회복',image='../sopia-review01/teacher01-mana.gif',kind='실제 SDL 별빛 외형 초안, 회복 로직 미연결'),dict(tier=1,option=1,title='박사의 가르침 · 주문선물',image='../sopia-review01/teacher01-book.gif',kind='실제 SDL 연구서 외형 초안, 선물 로직 미연결')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="sopia".*?</article>','<article id="sopia" data-god="sopia"><h2>소피아1성 · 박사의 가르침</h2><p>신앙30해금 / 최소기도술없음 / 패시브·선물·발동비용없음</p><p>MP회복 별빛</p><img class="scene" src="../sopia-review01/teacher01-mana.gif"><p>주문선물 연구서</p><img class="scene" src="../sopia-review01/teacher01-book.gif"><p>I12:직접주문처치당2MP, 시전당1회·실제소비MP상한. 선물:신앙45/75/110/150,미습득주문3개중1개. 두영상은 외형준비캡처, 실제회복/선물미연결.</p><p><a href="../sopia-review01/tier1-teacher01.html">효과·수치·검토범위</a></p><label>피드백<textarea data-feedback="sopia"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/sopia-review01/tier1-teacher01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='sopia',currentVisualReviewGod='sopia',currentVisualReviewTier=1,currentVisualReview=review,sopiaVisualPreviewRevision=rev,sopiaPreviewBinarySha256=digest,next='Review redesigned Sopia tier1 MP recovery and spell gift visual previews. Tiers3/5 visuals approved. New caster gameplay unimplemented; normal runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('sopia',{}).update(approved=[3,5],pending=[1],tier3Revision='sopia-gravity04',tier5Revision='sopia-bigbang02',tier1Preview=rev,scope='New tier1 visual review; caster combat unimplemented')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=validation,art=read(r/'assets/holocrawl'/rev/'generation.json')),indent=2),encoding='utf-8')
note='# 소피아 개편1성 MP·주문선물 시각 초안 / 2026-10-30\n\n사용자「ㅇㅇㅇ」로남은1성 진행. MP회복은작은별빛머리흡수,주문선물은보라금빛연구서14×10→24×16px팝업. nativeoffset(+14,-24),단일플레이어앵커,구형별도장식은이캡처만숨김. 실제SDL준비캡처,주문처치/MP회복/주문지급/선택메뉴미연결,MP/HP/월드/RNG보존. 기존3성gravity04·5성bigbang02시각승인유지,새1성검토중. 새캐스터전투미구현/일반실행본su-five01유지. 22신/저장복원통과. '+review+'\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Sopia redesigned tier1 staged native VFX ready; gameplay unchanged')
