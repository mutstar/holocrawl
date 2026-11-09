from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='mela-onibi01';b=r/'analysis/native'/rev;o=r/'analysis/previews/mela-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/onibi.json')
assert v['status']==proof['status']=='passed' and v['gods']==22 and proof['targetHpUnchanged']
def frame(name):
 return Image.open(b/f'native/shots/onibi-{name}.png').convert('RGB').crop((259,196,579,420)).resize((960,672),Image.Resampling.NEAREST)
heat=[frame('heat'+str(h)) for h in [0,3,6]]
heat[0].save(o/'onibi01-heat.gif',save_all=True,append_images=heat[1:],duration=[900,900,1100],loop=0,optimize=False)
for i,h in enumerate([0,3,6]):heat[i].save(o/f'onibi01-heat{h}.png')
hit=[heat[2]]+[frame('hit'+str(f)) for f in range(4)]+[frame('after')]
hit[0].save(o/'onibi01-counter.gif',save_all=True,append_images=hit[1:],duration=[850,110,140,200,180,1200],loop=0,optimize=False)
hit[3].save(o/'onibi01-counter.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>메라1성 · 푸른 도깨비불</title><style>'''+css+'''</style><h1>메라1성 · 불조심의 가호</h1><p class="info">신앙30 해금 / 최소 기도술 제한 없음 / 상시 패시브·무료 설정</p><h2>열기0 → 3 → 6 · 도깨비불과 작은 불씨</h2><img src="onibi01-heat.gif"><p>머리 오른쪽 위의 푸른 도깨비불은 가호 표시. 열기가 늘면 조금 커지고, 아래 작은 불씨 개수로 현재 열기를 표시합니다. 0에서도 기본 가호 불꽃은 남습니다.</p><h2>불씨 반격 · 열기6 → 적 몸통의 푸른 불꽃 → 열기5</h2><img src="onibi01-counter.gif"><p>반격 불꽃은 적 중심에 잠깐 피어나며 지속 장판이 아닙니다. 열기 한 개를 쓴 뒤 본인 옆 작은 불씨도6개에서5개로 줄어드는 모습입니다.</p><h2>기존 효과·수치 유지</h2><table><tr><th>항목</th><th>내용</th></tr><tr><td>가호</td><td>상시rF+1단계. 장비·종족저항과 정상 합산</td></tr><tr><td>열기</td><td>최대6. 유효 적 공격에 명중·방패방어 시+1, 적 화염 공격/화염지속피해는 대신+2. 적원천 획득은1턴구간 합계최대2</td></tr><tr><td>불씨 반격</td><td>ON일 때 일반 직접 공격이 기본 피해를 주면 열기1소비, 주대상1명에게1d(3+⌊I/6⌋)추가화염. I12:1d5·평균3. AC무시·rF적용</td></tr><tr><td>공격 종류</td><td>근접·맨손·사격·투척·직접 피해 주문. 행동당1회. 빗나감·기본피해0이면 미소모. 소환수·지속피해 제외</td></tr><tr><td>설정</td><td>무료 무턴ON/OFF. OFF로3성용 열기 저장 가능</td></tr><tr><td>감쇠</td><td>마지막 획득 후3턴 유지, 이후2턴마다1감소. 층이동·배교 시 제거</td></tr></table><p><b>실제 SDL 렌더러에 열기 표시와 반격 외형 단계를 준비해 촬영한 초안입니다.</b> 이번 GIF에서 실제 공격·열기 획득/소비·추가 피해는 실행하지 않았고, 실제 열기·대상HP·월드·RNG는 변하지 않았습니다. 메라 기존 전투 수치는 변경하지 않았으며 새 이펙트는 아직 전투 콜백에 연결하지 않았습니다. 일반실행본su-five01유지. 도깨비불 원화는built-in imagegen으로 생성,가호8×12~11×18px/작은불씨3px/반격최대26×30px로 적용. 본인 가호와 대상 반격 위치 검증·22신/저장복원 통과.</p><p><a href="tier1.html">수정 전 기존 가호 표시</a></p></html>'''
for name in ['index.html','tier1-onibi01.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['mela']=[dict(tier=1,option=0,title='불조심의 가호 · 열기',image='../mela-review01/onibi01-heat.gif',kind='실제 SDL 열기0/3/6 시각 초안'),dict(tier=1,option=1,title='불씨 반격',image='../mela-review01/onibi01-counter.gif',kind='실제 SDL 준비캡처, 실제 추가피해 미실행')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="mela".*?</article>','<article id="mela" data-god="mela"><h2>메라1성 · 푸른 도깨비불</h2><p>열기0→3→6</p><img class="scene" src="../mela-review01/onibi01-heat.gif"><p>불씨 반격·열기6→5</p><img class="scene" src="../mela-review01/onibi01-counter.gif"><p>신앙30해금/최소기도술없음/패시브·설정무료. rF+1,열기최대6,반격열기1소비·I12화염1d5(평균3). 시각단계준비캡처,실제공격·열기소비·HP변화없음.</p><p><a href="../mela-review01/tier1-onibi01.html">효과·수치·검토범위</a></p><label>피드백<textarea data-feedback="mela"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/mela-review01/tier1-onibi01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
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
note='# 메라1성 푸른 도깨비불 시각 초안 / 2026-10-30\n\n사용자「ㅇㅇ이펙트 ㄱㄱ」. 청록/청색/보라끝도깨비불신규생성. 가호8×12~11×18px,밑에3px불씨0~6개;0/3/6열기시각비교. 반격은대상몸통14×18→26×30→18×22,준비표시6→5. 실제SDLrender-only,실제공격/열기변경/피해없음. 기존메라전투수치유지,새시각콜백미연결/일반실행본su-five01유지. 위치/상태/RNG/22신/저장복원통과. '+review+' 현재1성외형검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Mela onibi tier1 staged native VFX ready; gameplay unchanged')
