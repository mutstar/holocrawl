from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='vivi-finale01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/finale.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
names=['before','cast0','cast1','mark0','mark1','spell0','spell1','burst0','burst1','burst2','ended']
frames=[Image.open(b/f'native/shots/finale-{n}.png').convert('RGB').crop((211,164,659,484)).resize((896,640),Image.Resampling.NEAREST) for n in names]
frames[0].save(o/'finale.gif',save_all=True,append_images=frames[1:],duration=[800,450,450,650,650,160,160,90,220,220,1200],loop=0,optimize=False);frames[4].save(o/'marked.png');frames[8].save(o/'burst.png')
base=r/'analysis/previews/vivi-review01';css=re.search(r'<style>(.*?)</style>',(base/'tier3-encore04.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>비비5성 · 그랜드 피날레 초안</title><style>'''+css+'''</style><h1>비비5성 · 그랜드 피날레</h1><p class="info"><b>주문으로 적에게 조명 표식을 남기고, 같은 적을 다시 주문으로 맞히면 주변1칸까지 폭발시키는 시각 초안입니다.</b><br>예정 해금: 신앙120 · 최소 기도술 제한 없음<br>예정 비용: MP6·신앙12·행동1턴</p><h2>발동 → 적 조명 표식 → 다음 타격 예시 → 주변 펄 폭발 → 종료</h2><img src="../vivi-finale01/finale.gif"><table><tr><th>표시</th><th>의미</th></tr><tr><td>캐릭터 머리 위 금빛 표식</td><td>5성 피날레 유지 중</td></tr><tr><td>적 머리 위 금빛 표식</td><td>첫 공격 주문에 맞아 조명 표식을 받은 적. 다음 주문으로 다시 맞히면 폭발 예정</td></tr><tr><td>중앙 금빛·분홍 폭발</td><td>조명 표식이 터지는 대상</td></tr><tr><td>주변 작은 분홍·보라 펄</td><td>주변1칸,최대3×3 폭발 범위. 아래 두 칸 떨어진 몹은 범위 밖</td></tr></table><p><b>실제 SDL 렌더러에 각 단계를 준비해서 촬영한 초안입니다.</b> 주문 적중·표식 생성·피해·MP/신앙·지속시간은 새 전투 코드에 아직 연결하지 않았습니다. 중간 타격은 공통 타격 표시로 대신했고,이번 GIF에서 몹HP는 변하지 않습니다.</p><h2>합의한 효과·수치 · 구현 예정</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>유지</td><td>시전 완료 후6+0.2I턴.기도술I12:8.4턴</td></tr><tr><td>표식</td><td>직접 공격 주문으로 맞힌 적에게 조명 표식.같은 적을 다음 공격 주문으로 다시 맞히면 표식 소모·폭발</td></tr><tr><td>폭발 피해</td><td>2d(5+⌊I/3⌋). I12:2d9,2~18·평균10</td></tr><tr><td>폭발 범위</td><td>표식 대상 주변1칸.한 번의 주문에서 같은 적이 여러 폭발에 겹쳐도 폭발 피해는1회로 제한</td></tr><tr><td>적용 제외</td><td>소환수·독·구름 지속 피해는 표식 발동 제외</td></tr><tr><td>재사용</td><td>피날레 종료 후15턴 대기</td></tr></table><p>중앙 폭발은18→28→26픽셀,주변 펄은10→16→14픽셀.전체를늘린한장의그림이아니라32×32개별타일로배치했습니다.1·3성 시각 승인,5성 시각 검토 중.캐스터 전투 구현은 미완료,일반 실행본은su-five01 유지.시각 단계/RNG·상태 보존 및22신 회귀/저장 복원 검사 통과.</p><p><a href="tier3-encore04.html">확정된3성 팝 폭발</a> · <a href="tier1-lipstick01.html">확정된1성 립스틱</a></p></html>'''
for name in ['index.html','tier5-finale01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['vivi']=[dict(tier=5,option=0,title='그랜드 피날레',image='../vivi-finale01/finale.gif',kind='실제 SDL 조명 표식·주변 폭발 초안')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="vivi" data-god="vivi"><h2>비비 <small>5성 · 시각 초안 검토 중</small></h2><img class="scene" src="../vivi-finale01/finale.gif"><p>금빛 조명 표식→다음 주문 타격 예시→주변1칸펄폭발. 예정:MP6·신앙12·1턴,신앙120해금·최소기도술없음. I12:시전후8.4턴·폭발2d9(평균10).</p><p>시각 단계만 준비한 초안이며 표식·추가피해 전투 코드는 미구현.</p><p><a href="../vivi-review01/tier5-finale01.html">효과·수치·표시 의미</a></p><label>피드백<textarea data-feedback="vivi"></textarea></label></article>'
t=re.sub(r'<article id="vivi".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest();review='analysis/previews/vivi-review01/tier5-finale01.html'
def update(d):
 d.update(currentGod='vivi',currentVisualReviewGod='vivi',currentVisualReviewTier=5,currentVisualReview=review,viviVisualPreviewRevision=rev,viviPreviewBinarySha256=digest,next='Review Vivi tier5 Grand finale VFX. Tiers1/3 visuals approved. Caster combat remains unimplemented; normal runtime unchanged (su-five01).')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('vivi',{}).update(approved=[1,3],pending=[5],tier1Revision='vivi-lipstick01',tier3Revision='vivi-encore04',tier5Preview=rev,pendingRevision=rev,feedback='ㅇㅋ그다음')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,art=read(r/'assets/holocrawl/vivi-finale01/generation.json')),indent=2),encoding='utf-8')
note='# 비비3성 시각 확정·5성 피날레 초안 / vivi-finale01 / 2026-10-29\n\n사용자「ㅇㅋ그다음」으로3성encore04시각승인.현재5성그랜드피날레:본인금빛활성표식→적조명표식→다음공통타격예시→중앙금빛폭발+주변8칸작은펄폭발→종료를실제SDL에서준비캡처.중앙28px/주변16px/개별32타일.대상·주변HP불변,RNG/상태보존·22신/복원통과.새캐스터의표식/추가피해/비용/지속/중첩코드는여전히미구현,일반실행본su-five01유지. '+review+' 현재5성시각검토중.1·3성은시각승인만.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Vivi Grand finale staged VFX ready; gameplay not applied')
