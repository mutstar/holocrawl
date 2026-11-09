from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='mela-heat3-01';b=r/'analysis/native'/rev;o=r/'analysis/previews/mela-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/onibi.json')
assert v['status']==proof['status']=='passed' and v['gods']==22 and proof['targetHpUnchanged']
def frame(name):
 return Image.open(b/f'native/shots/onibi-{name}.png').convert('RGB').crop((259,196,579,420)).resize((960,672),Image.Resampling.NEAREST)
heat=[frame('heat'+str(h)) for h in [0,1,3]]
heat[0].save(o/'heat3-01-heat.gif',save_all=True,append_images=heat[1:],duration=[900,900,1100],loop=0,optimize=False)
for i,h in enumerate([0,1,3]):heat[i].save(o/f'heat3-01-heat{h}.png')
hit=[heat[2]]+[frame('hit'+str(f)) for f in range(4)]+[frame('after')]
hit[0].save(o/'heat3-01-counter.gif',save_all=True,append_images=hit[1:],duration=[850,110,140,200,180,1200],loop=0,optimize=False)
hit[3].save(o/'heat3-01-counter.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>메라1성 · 푸른 도깨비불</title><style>'''+css+'''</style><h1>메라1성 · 불조심의 가호</h1><p class="info">신앙30 해금 / 최소 기도술 제한 없음 / 상시 패시브·무료 설정</p><h2>열기0 → 1 → 3 · 도깨비불과 작은 불씨</h2><img src="heat3-01-heat.gif"><p>머리 오른쪽 위의 푸른 도깨비불은 가호 표시. 열기가 늘면 조금 커지고, 아래 한 줄의 작은 불씨 최대3개로 현재 열기를 표시합니다. 0에서도 기본 가호 불꽃은 남습니다.</p><h2>불씨 반격 · 열기3 → 적 몸통의 푸른 불꽃 → 열기2</h2><img src="heat3-01-counter.gif"><p>반격은 적 몸통 중심에서 청백색 섬광과 짧은 푸른 불꽃이 사방으로 터집니다. 위로 피어오르는 가호 도깨비불과 다른 모양이며 지속 장판이 아닙니다. 열기 한 개를 쓴 뒤 본인 옆 작은 불씨도3개에서2개로 줄어드는 모습입니다.</p><h2>3불씨 개편 수치 제안 · 전투 미적용</h2><table><tr><th>항목</th><th>제안</th></tr><tr><td>열기 상한</td><td>6→3개. 새1개=기존2개 분량</td></tr><tr><td>획득</td><td>일반 유효피격2회당1개, 적 화염 유효피격/틱1회당1개. 적원천1턴구간 최대1개분량. 일반피격 충전 절반은 내부에서 추적하고 추가 불씨는 표시하지 않음</td></tr><tr><td>1성 반격</td><td>불씨1개소비,2d(3+⌊I/6⌋)추가화염. I12:2d5,평균6. AC무시·rF적용. 같은 시전/행동당1명·1회</td></tr><tr><td>저장 화력</td><td>I12 만충전:기존6개×평균3=18 / 새3개×평균6=18. 공격당피해와발동빈도는 달라지므로 실전동일성 보장은 아님</td></tr><tr><td>3성 역분사</td><td>2d(6+⌊I/3⌋)+8H. I12 H0/1/2/3:평균11/19/27/35. 기존H6 최대35유지</td></tr><tr><td>5성 강화 역분사</td><td>3d(6+⌊I/3⌋)+8H. I12 H0/1/2/3:평균16.5/24.5/32.5/40.5. 기존H6 최대40.5유지</td></tr><tr><td>5성 충전</td><td>시전시3개충전,이후4턴마다1개. 기존2턴마다1/6충전을4턴마다1/3충전으로 환산</td></tr><tr><td>화염구름 흡수</td><td>유효구름 제거 보상2→1개. 원천별 획득상한 유지</td></tr><tr><td>감쇠</td><td>획득후3턴유지,이후4턴마다1개. 내부 절반충전도 유효접촉/획득 없이3턴 지나거나 층이동/배교 시 제거</td></tr><tr><td>유지</td><td>rF/MP·신앙비용/행동시간/범위/권능지속/쿨다운 유지</td></tr></table><p><b>실제 SDL 렌더러에 열기 표시와 반격 외형 단계를 준비해 촬영한 초안입니다.</b> 이번 GIF에서 실제 공격·열기 획득/소비·추가 피해는 실행하지 않았고, 실제 열기·대상HP·월드·RNG는 변하지 않았습니다. 이번3불씨 수치는제안상태로실제전투는아직기존6열기규칙이며 새 이펙트는 아직 전투 콜백에 연결하지 않았습니다. 일반실행본su-five01유지. 도깨비불 원화는built-in imagegen으로 생성,가호8×12~11×18px/한줄최대3개불씨3px/반격최대28px폭로 적용. 본인 가호와 대상 반격 위치 검증·22신/저장복원 통과.</p><p><a href="tier1.html">수정 전 기존 가호 표시</a></p></html>'''
for name in ['index.html','tier1-heat3-01.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['mela']=[dict(tier=1,option=0,title='불조심의 가호 · 열기',image='../mela-review01/heat3-01-heat.gif',kind='실제 SDL 열기0/1/3 시각 초안'),dict(tier=1,option=1,title='불씨 반격',image='../mela-review01/heat3-01-counter.gif',kind='실제 SDL 준비캡처, 실제 추가피해 미실행')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="mela".*?</article>','<article id="mela" data-god="mela"><h2>메라1성 · 푸른 도깨비불</h2><p>열기0→1→3</p><img class="scene" src="../mela-review01/heat3-01-heat.gif"><p>불씨 반격·열기3→2</p><img class="scene" src="../mela-review01/heat3-01-counter.gif"><p>신앙30해금/최소기도술없음/패시브·설정무료. rF+1,새상한3개,반격1개소비·I12화염2d5(평균6)제안. 시각단계준비캡처,실제공격·열기소비·HP변화없음.</p><p><a href="../mela-review01/tier1-heat3-01.html">효과·수치·검토범위</a></p><label>피드백<textarea data-feedback="mela"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/mela-review01/tier1-heat3-01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='mela',currentVisualReviewGod='mela',currentVisualReviewTier=1,currentVisualReview=review,melaVisualPreviewRevision=rev,melaPreviewBinarySha256=digest,next='Review Mela tier1 blue onibi heat0/3/6 and counterflash6to5. Visual stages only, not combat-triggered; existing Mela combat unchanged. Normal runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('mela',{}).update(approved=[],pending=[1,3,5],tier1Preview=rev,scope='New tier1 native VFX staged review; existing combat unchanged, visual hooks unconnected')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,art=read(r/'assets/holocrawl'/rev/'generation.json')),indent=2),encoding='utf-8')
note='# 메라1성 푸른 도깨비불 시각 초안 / 2026-10-30\n\n사용자「불씨6개너무난잡3개로줄이고수치조정」. 3개한줄표시0/1/3→반격후2,기존반격도트보존. 새수치별도제안 analysis/design/mela-heat3-01.json,실제6열기전투미변경. 청록/청색/보라끝도깨비불신규생성. 가호8×12~11×18px,밑에3px불씨0~3개한줄;0/1/3열기시각비교. 반격만별도생성한사방불씨폭발14→24→28→20px폭으로교체/가호불변,준비표시3→2. 실제SDLrender-only,실제공격/열기변경/피해없음. 기존메라전투수치유지,새시각콜백미연결/일반실행본su-five01유지. 위치/상태/RNG/22신/저장복원통과. '+review+' 현재1성외형검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Mela onibi tier1 staged native VFX ready; gameplay unchanged')
