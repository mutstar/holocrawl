from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='sopia-bigbang02';b=r/'analysis/native'/rev;o=r/'analysis/previews/sopia-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
validation=read(b/'capture-validation.json');proof=read(b/'native/shots/bigbang.json')
assert validation['status']==proof['status']=='passed' and validation['gods']==22
for radius in [2,3]:
 frames=[];durations=[]
 for charge in range(5):
  for f in range(4):
   p=b/f'native/shots/bigbang-r{radius}-c{charge}-f{f}.png';d=read(Path(str(p)+'-range.json'))
   assert d['status']=='passed' and d['radius']==(2 if charge==4 else radius)
   frames.append(Image.open(p).convert('RGB').crop((275,210,611,466)).resize((1008,768),Image.Resampling.NEAREST))
   durations.append([90,120,200,200][f] if charge==4 else 360 if charge==3 and f==3 else 170)
 frames.append(Image.open(b/f'native/shots/bigbang-r{radius}-ended.png').convert('RGB').crop((275,210,611,466)).resize((1008,768),Image.Resampling.NEAREST));durations.append(1000)
 frames[0].save(o/f'bigbang02-r{radius}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
 frames[13].save(o/f'bigbang02-r{radius}-charge3.png');frames[18].save(o/f'bigbang02-r{radius}-burst.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>소피아5성 · 빅뱅 가설</title><style>'''+css+'''</style><h1>소피아5성 · 빅뱅 가설</h1><p class="info">예정 해금:신앙120 / 최소 기도술 제한 없음<br>예정 비용:MP7·신앙12·1턴. 별도 기폭은 추가 MP·신앙0, 행동1턴</p><h2>응축0 → 별1개 → 별2개 → 별3개 → 기폭 → 종료</h2><img src="bigbang02-r2.gif"><p>3성에서 승인한 반투명 중력 문양 유지. 응축할수록 금빛 별이1·2·3개 표시되고 문양이 밝아집니다. 기폭 순간은 다른 별빛 충격파가 중심에서 중앙5×5까지 퍼졌다 사라집니다. 몹은 문양 위에 표시됩니다.</p><h2>기도술20 예시:7×7 중력장과 중앙5×5 기폭 구분</h2><img src="bigbang02-r3.gif"><p>장판은3성의 성장 규칙을 따릅니다. 기폭은 기도술과 무관하게 중앙5×5를 유지하며 바깥쪽 장판은 종료됩니다.</p><h2>합의한 효과·수치 · 전투 코드 미적용</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>설치/강화</td><td>사거리4의 유효 바닥에 강화 중력장 설치. 기존 장이 있으면 중심 유지한 채 강화</td></tr><tr><td>유지</td><td>시전 완료 후10+0.2I턴. I12:12.4턴</td></tr><tr><td>중력장</td><td>I0~7:3×3 / I8~15:5×5 / I16이상:7×7. 2턴마다3성과 같은 피해·끌기. 강화 직후 중복 틱 없음</td></tr><tr><td>응축</td><td>MP를 소비한 직접 공격 주문으로 장 안 유효 적에게 실제 피해를 주면+1. 광역·다단히트도 시전당 최대1, 총3중첩. 소환수·독·구름·권능 제외. 기다리기만 해서는 쌓이지 않음</td></tr><tr><td>기폭</td><td>응축1이상 / 중심과 거리6이내·사선·시야 필요 / 중앙5×5 적에게3d(8+⌊I/3⌋)+6C / AC 한 번 적용 / 생존 적 최대2칸 바깥 밀침 / 자신·아군 제외</td></tr><tr><td>I12 피해</td><td>C1:평균25.5 / C2:31.5 / C3:37.5 (AC 적용 전)</td></tr><tr><td>종료</td><td>기폭 또는 자연 만료 시 소멸. 만료는 자동 폭발 없음. 종료 후15턴 재사용 대기</td></tr></table><p><b>이 영상은 실제 SDL 렌더러에 응축·기폭 외형 단계를 준비해 촬영한 시각 초안입니다.</b> 이번 GIF에서 주문이 발사되거나 응축이 실제 주문으로 쌓이는 것은 아니며, 몹의 HP·위치도 변하지 않습니다. 새1·3·5성 캐스터 전투는 아직 미구현, 일반 실행본은su-five01 유지. 새 기폭 문양은 built-in imagegen 생성 도트이며, 응축 별은 기폭 원화의 중심 별을 재사용하며, 바닥 흐름은 native 렌더러 도형입니다. 상태/RNG 보존·범위·앵커·22신/저장 복원 검사 통과.</p><p><a href="tier3-gravity04.html">확정된3성 반투명 중력장</a></p></html>'''
for name in ['index.html','tier5-bigbang02.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['sopia']=[dict(tier=5,option=0,title='빅뱅 가설',image='../sopia-review01/bigbang02-r2.gif',kind='실제 SDL 응축·기폭 시각 초안, 전투 연결 전')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="sopia".*?</article>','<article id="sopia" data-god="sopia"><h2>소피아5성 · 빅뱅 가설</h2><img class="scene" src="../sopia-review01/bigbang02-r2.gif"><p>응축0→별1·2·3개→중앙5×5 별빛 충격파→종료. 예정:신앙120해금/최소기도술없음/MP7·신앙12·1턴. I12:12.4턴·C3기폭평균37.5(AC전). 시각단계만 준비했으며 실제 주문/응축/피해/밀침 미연결.</p><p><a href="../sopia-review01/tier5-bigbang02.html">7×7 장판 비교·효과·수치</a></p><label>피드백<textarea data-feedback="sopia"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/sopia-review01/tier5-bigbang02.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='sopia',currentVisualReviewGod='sopia',currentVisualReviewTier=5,currentVisualReview=review,sopiaVisualPreviewRevision=rev,sopiaPreviewBinarySha256=digest,next='Review Sopia tier5 charge and Big Bang visual draft. Tier3 visual approved. New caster gameplay and new tier1 visual still pending; runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('sopia',{}).update(approved=[3],pending=[1,5],tier3Revision='sopia-gravity04',tier5Preview=rev,scope='New caster visual previews; revised combat unimplemented')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=validation,art=read(r/'assets/holocrawl/sopia-bigbang01/generation.json')),indent=2),encoding='utf-8')
note='# 소피아5성 응축·빅뱅 시각 초안 / 2026-10-30\n\n사용자「rrr」로5성 진행. 승인3성문양 유지,응축0/1/2/3별과불투명도105/125/145/165. 별빛 기폭 신규생성,중심1→3→5칸충격파/몹아래/고정5×5피해표시. I12장판5×5,I20장판7×7 비교. 실제SDL준비캡처:응축이실제주문으로쌓이거나HP/위치변화하는영상아님. 3성외형승인유지,5성검토중/새1성외형미검토. 새캐스터전투미구현/일반실행본su-five01유지. 범위/앵커/상태/RNG/22신/복원통과. '+review+'\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Sopia tier5 staged native VFX ready; gameplay unchanged')
