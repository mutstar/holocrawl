from pathlib import Path
from PIL import Image
import json,re,hashlib,difflib
r=Path(__file__).resolve().parents[1];rev='sopia-gravity01';b=r/'analysis/native'/rev;o=r/'analysis/previews/sopia-review01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/gravity.json')
assert v['status']==proof['status']=='passed' and v['gods']==22
for radius in range(1,4):
 frames=[]
 for f in range(4):
  p=b/f'native/shots/gravity-r{radius}-f{f}.png';check=read(Path(str(p)+'-range.json'))
  assert check['status']=='passed' and check['cells']==(2*radius+1)**2
  frames.append(Image.open(p).convert('RGB').crop((275,210,611,466)).resize((1008,768),Image.Resampling.NEAREST))
 frames[0].save(o/f'gravity-r{radius}.gif',save_all=True,append_images=frames[1:],duration=180,loop=0,optimize=False)
 frames[1].save(o/f'gravity-r{radius}.png')
css=re.search(r'<style>(.*?)</style>',(o/'tier1.html').read_text(encoding='utf-8'),re.S)[1]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>소피아3성 · 성장하는 중력 실험실</title><style>'''+css+''' .sizes{display:flex;gap:12px;flex-wrap:wrap}.sizes figure{flex:1;min-width:240px;margin:0}.sizes img{width:100%;image-rendering:pixelated}</style><h1>소피아3성 · 중력 실험실</h1><p class="info">기도술에 따라 커지는 중력장 · 현재 외형 검토 중<br>신앙75 해금 / 최소 기도술 제한 없음 / 예정 비용 MP3·신앙3·1턴</p><h2>기도술12 · 5×5</h2><img src="gravity-r2.gif"><p>중앙의 작은 보라·금빛 중력핵, 중심으로 흐르는 바닥 입자, 범위를 둘러싼 끊어진 연보라 테두리. 바닥 흐름은 몹 아래에 표시합니다.</p><h2>기도술에 따른 크기 비교</h2><div class="sizes"><figure><figcaption>기도술0~7 · 3×3</figcaption><img src="gravity-r1.gif"></figure><figure><figcaption>기도술8~15 · 5×5</figcaption><img src="gravity-r2.gif"></figure><figure><figcaption>기도술16~27 · 7×7</figcaption><img src="gravity-r3.gif"></figure></div><h2>합의한 개편 수치 · 전투 코드 미적용</h2><table><tr><th>항목</th><th>예정 효과</th></tr><tr><td>설치</td><td>사거리4의 보이는 유효 바닥 / 하나만 유지 / 중심 고정</td></tr><tr><td>지속</td><td>8+0.2I턴. I12에서10.4턴</td></tr><tr><td>주기</td><td>설치 완료2턴 뒤부터 매2턴. 애니메이션 반복 횟수가 피해·끌기 횟수는 아닙니다.</td></tr><tr><td>압축 피해</td><td>1d(4+⌊I/4⌋), AC 한 번 적용. I12:1d7·평균4</td></tr><tr><td>끌기</td><td>중심 방향1칸. 확률75+2I−2HD%, 최소25%·최대95%. I12·HD10:79%</td></tr><tr><td>면역·아군</td><td>끌기 면역·이동할 칸이 없는 적도 압축 피해는 받음. 자신·아군 제외</td></tr></table><p><b>실제 SDL 렌더러에 새 범위를 준비한 외형 미리보기입니다.</b> 이번 GIF에서는 몹이 이동하거나 HP가 줄지 않습니다. 개편된 범위·피해·끌기와 1성 MP/주문 선물·5성 응축은 아직 전투 코드에 연결하지 않았습니다. 일반 실행본 su-five01 유지. 9/25/49칸 표시·상태/RNG 보존·22신 및 저장 복원 검사 통과.</p><p>중력핵 원화는 built-in imagegen으로 생성하고22~26px로 적용. 바닥 입자·테두리는 native 렌더러 도형입니다.</p><p><a href="tier1.html">개편 전 1성 참고</a></p></html>'''
for name in ['index.html','tier3-gravity01.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['sopia']=[dict(tier=3,option=0,title='중력 실험실 · 5×5',image='../sopia-review01/gravity-r2.gif',kind='실제 SDL 외형 미리보기 · 전투 개편 미적용')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=re.sub(r'<article id="sopia".*?</article>','<article id="sopia" data-god="sopia"><h2>소피아3성 · 중력 실험실</h2><img class="scene" src="../sopia-review01/gravity-r2.gif"><p>기도술0~7:3×3 / 8~15:5×5 / 16이상:7×7. 예정 MP3·신앙3·1턴, I12:10.4턴·2턴마다1d7·HD10끌기79%. 현재는 외형만 준비한 캡처, 몹 이동·HP 변화 없음.</p><p><a href="../sopia-review01/tier3-gravity01.html">세 크기 비교·수치·효과</a></p><label>피드백<textarea data-feedback="sopia"></textarea></label></article>',t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
review='analysis/previews/sopia-review01/tier3-gravity01.html';digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
def update(d):
 d.update(currentGod='sopia',currentVisualReviewGod='sopia',currentVisualReviewTier=3,currentVisualReview=review,sopiaVisualPreviewRevision=rev,sopiaPreviewBinarySha256=digest,next='Review Sopia growing gravity field VFX. Caster numerical design approved to proceed; revised combat not implemented. Runtime su-five01 unchanged.')
 if 'review' in d:d['review']=review
 if isinstance(d.get('sopiaCasterDraft'),dict):d['sopiaCasterDraft']['status']='approved-design-not-implemented'
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('sopia',{}).update(approved=[],pending=[1,3,5],reviewRevision=rev,scope='Tier3 VFX only; new tier1 and tier5 pending')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/sopia-caster01.json';d=read(p);d['status']='approved-design-not-implemented';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,previewBinarySha256=digest,runtimeDeployed=False,combatChanged=False,nativeProof=proof,validation=v,art=read(r/'assets/holocrawl'/rev/'generation.json')),indent=2),encoding='utf-8')
note='# 소피아3성 성장 중력장 VFX / 2026-10-30\n\n사용자 수정안 진행 승인 후 외형 제작 요청. 3×3/5×5/7×7 범위, 중심22~26px 보라금빛 중력핵, 몹 아래 흡입 입자/연보라 경계. generated asset assets/holocrawl/sopia-gravity01. native SDL에서9/25/49칸·상태/RNG보존 및22신/복원 통과. 이번은render-only, 몹이동/피해없음. 새캐스터1/3/5 전투미구현,일반실행본su-five01유지. '+review+' 현재3성외형검토중. 개편전1성고리는확정본아님.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Sopia gravity native VFX preview ready; gameplay unchanged')
