from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='mela-breath02';b=r/'analysis/native'/rev;o=r/'analysis/previews/mela-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/breath.json')
assert v['status']==proof['status']=='passed' and v['gods']==22
def frame(name):
 return Image.open(b/f'native/shots/breath-{name}.png').convert('RGB').crop((259,196,611,452)).resize((1056,768),Image.Resampling.NEAREST)
for heat in [0,3]:
 for f in range(4):
  d=read(b/f'native/shots/breath-h{heat}-f{f}.png-cone.json');assert d['status']=='passed' and d['cells']==min(3,f+1)**2
 frames=[frame(f'h{heat}-before')]+[frame(f'h{heat}-f{f}') for f in range(4)]+[frame(f'h{heat}-ended')]
 frames[0].save(o/f'breath02-h{heat}.gif',save_all=True,append_images=frames[1:],duration=[850,160,160,260,220,1100],loop=0,optimize=False)
 frames[3].save(o/f'breath02-h{heat}.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>메라3성 · 화염 역분사</title><style>'''+css+'''</style><h1>메라3성 · 화염 역분사</h1><p class="info">신앙75 해금 / 최소 기도술 제한 없음 / MP3·신앙3·1턴<br>행동 완료 후3턴 재사용 대기. 열기0도 사용 가능</p><h2>열기3개 · 푸른 도깨비불 부채꼴</h2><img src="breath02-h3.gif"><p>시전자 앞에서1칸→3칸→5칸 폭으로 퍼지는 길이3의 부채꼴. 이번 초안은 오른쪽 방향, 총9칸입니다. 불줄기는 몹 아래에, 실제 범위 안 몹의 타격 섬광은 몸통 위에 잠깐 표시합니다. 오른쪽4칸 몹은 범위 밖 대조입니다.</p><h2>열기0개 · 기본 역분사</h2><img src="breath02-h0.gif"><p>열기가 없어도 같은 범위를 공격합니다. 불줄기 크기로 강도를 구분하며 열기3개 영상에서는 본인 표식의3불씨가0개로 바뀝니다.</p><h2>승인한3불씨 기준 수치 · 전투 미적용</h2><table><tr><th>항목</th><th>효과</th></tr><tr><td>범위</td><td>인접8방향 중 선택,길이3·폭1/3/5. 벽·사선에 막힌 칸 제외,자신·아군 피해 없음. 이 외형 검사는 오른쪽만 포함</td></tr><tr><td>피해</td><td>불씨H 전부소모,2d(6+⌊I/3⌋)+8H 순수화염. 필중·AC무시·rF적용</td></tr><tr><td>I12</td><td>H0:평균11 / H1:19 / H2:27 / H3:35 (저항 적용 전)</td></tr><tr><td>불씨 반격</td><td>1성 추가타 중복 없음. 이번 역분사가 자기 불씨를 다시 만들지 않음</td></tr><tr><td>소화</td><td>범위의 일반 화염구름 제거. 유효 적원천 화염구름을 실제 제거하면 새불씨1개,발동당최대1·원천별 획득상한 적용. 이번 피해에 소급하지 않음</td></tr><tr><td>제외</td><td>독·냉기·증기·지옥불·용암 제거 없음. 적의 몸에 붙은 점착화염 소화 없음</td></tr></table><p><b>실제 SDL 렌더러에 불씨 소모·부채꼴·타격 외형을 준비해 촬영한 미리보기입니다.</b> GIF에서 실제피해·열기소모·구름소화는 실행하지 않았습니다.3불씨수치안은 승인됐지만 실제 전투는 아직 기존6열기규칙이며 새이펙트도 전투콜백 미연결입니다. 일반실행본su-five01유지. 오른쪽범위1/4/9칸·자신/범위밖제외·월드/RNG보존·22신/저장복원통과.</p><p>불줄기 원화는built-in imagegen 생성,32px 개별타일로 배치했습니다. 열기0과3의 최대폭20/28px,몹 타격은 확정된1성 불씨폭발 도트를 재사용합니다.</p><p><a href="tier1-heat3-01.html">승인1성·3불씨 환산 수치</a></p></html>'''
for name in ['index.html','tier3-breath02.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['mela']=[dict(tier=3,option=0,title='화염 역분사 · 열기3',image='../mela-review01/breath02-h3.gif',kind='실제 SDL 오른쪽 부채꼴 시각 초안'),dict(tier=3,option=1,title='화염 역분사 · 열기0',image='../mela-review01/breath02-h0.gif',kind='실제 SDL 열기0 비교,피해 미실행')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="mela".*?</article>','<article id="mela" data-god="mela"><h2>메라3성 · 화염 역분사</h2><img class="scene" src="../mela-review01/breath02-h3.gif"><p>신앙75해금/최소기도술없음/MP3·신앙3·1턴. 오른쪽길이3,폭1/3/5칸 도깨비불. 승인3불씨안I12:열기0/1/2/3 평균11/19/27/35,AC무시·rF적용. 시각단계준비캡처,실제피해/소모/소화없음.</p><p><a href="../mela-review01/tier3-breath02.html">열기0비교·효과·수치</a></p><label>피드백<textarea data-feedback="mela"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/mela-review01/tier3-breath02.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='mela',currentVisualReviewGod='mela',currentVisualReviewTier=3,currentVisualReview=review,melaVisualPreviewRevision=rev,melaPreviewBinarySha256=digest,next='Review Mela tier3 eastward breath visual, heat0/3 comparison. Tier1 visual and3-ember numeric design approved. New combat conversion and visual callbacks not implemented; runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('mela',{}).update(approved=[1],pending=[3,5],tier1Revision='mela-heat3-01',tier3Preview=rev,scope='Tier1 visual/3-ember numeric design approved; tier3 visual staged east-only prototype, combat still old6heat')
 if isinstance(d.get('melaHeat3Draft'),dict):d['melaHeat3Draft']['status']='approved-design-not-implemented'
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,art=read(r/'assets/holocrawl/mela-breath01/generation.json')),indent=2),encoding='utf-8')
note='# 메라1성·3불씨안 승인 / 3성역분사 시각 초안 / 2026-10-30\n\n사용자「오케이 다음과정으로」로1성heat3-01시각및3불씨환산안승인.3성breath01:오른쪽길이3·폭1/3/5(진행1/4/9칸)푸른도깨비불,열기0/3비교,몹아래불줄기/몸통타격섬광. 실제SDL준비캡처,HP/열기소모/소화미실행. 새3불씨전투변경및시각콜백미구현,일반실행본su-five01유지. 원본대각선cone좌표와거리제한조합은추후전투연결때별도점검필요(이초안오른쪽만검증). 범위/자신·바깥제외/상태/RNG/22신/복원통과. '+review+' 현재3성검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Mela tier3 staged native breath VFX ready; gameplay unchanged')
