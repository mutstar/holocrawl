from pathlib import Path
from PIL import Image
import json, hashlib, difflib, re

r=Path(__file__).resolve().parents[1]
rev='suisei-stars03'
b=r/'analysis/native'/rev
raw=b/'native/shots'
out=r/'analysis/previews/suisei-stars01'
out.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(raw/'stars.json')
validation=read(b/'capture-validation.json')
assert proof['status']==validation['status']=='passed'
assert validation['gods']==22
# Only crop and nearest-neighbour scale actual engine framebuffers.
box=(323,260,547,388)
frames=[]
for name in ['stars0','stars1','stars2','stars3','stars3-moved','stars-expired']:
    im=Image.open(raw/(name+'.png')).convert('RGB').crop(box)
    im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
    im.save(out/(name+'.png'))
    frames.append(im)
assert len({f.tobytes() for f in frames[:4]})==4
frames[0].save(out/'stacking.gif',save_all=True,append_images=frames[1:4],duration=[700,900,900,1400],loop=0)
frames[3].save(out/'follow-and-expire.gif',save_all=True,append_images=frames[4:],duration=[900,1000,1000],loop=0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스이세이 1성 · 별 중첩</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#b7efff}img{max-width:100%;image-rendering:pixelated}section,.info{background:#1d2b3d;padding:18px;border:1px solid #48617b;border-radius:10px;margin:20px 0}a{color:#ffdfa2}table{border-collapse:collapse}td,th{padding:9px;border:1px solid #48617b}</style><h1>스이세이 1성 · 별자리 표식 [패시브 / 수동 표적 변경]</h1><p class="info">중첩 표시 초안: 직접 공격 적중 → 머리 위 별 1개 → 2개 → 3개.<br>1·2개는 밝은 청록색, 3개는 금색으로 완성 표시. 기존 몹 몸통의 청록·금색 표적 모서리는 유지합니다.</p><section><h2>실제 직접 공격으로 1→2→3개</h2><img src="stacking.gif" alt="실제 게임에서 직접 공격 3회로 별 1개 2개 3개"><p>기존 승인 도트의 작은 별을 재사용했습니다. 별은 고정된 세 자리에서 한 개씩 늘어나며 몹의 머리 위에 표시합니다. 영상은 읽기 쉽도록 느리게 반복합니다.</p></section><section><h2>표적 이동과 중첩 만료 표시</h2><img src="follow-and-expire.gif" alt="별 표식이 몹을 따라 이동하고 만료 후 별이 사라지는 모습"></section><section><h2>1성 효과·기도술</h2><p>별 축적은 자동 패시브이며 공격 자체의 MP·행동 시간은 원래 규칙을 따릅니다. 별 축적에 추가 MP·신앙 소모는 없습니다. 표적 수동 변경만 별도 1턴입니다. 기도술 최소 제한은 없습니다.</p><p>이번 3중첩 수치안: 처치 시 3턴간 다음 무기 공격·직접 공격 주문에 1d(3+4×별) 추가 물리 피해, AC 적용. 별 1/2/3개면 평균 4/6/8. 별 자체로 현재 적에게 평타 추가 피해를 주지는 않습니다.</p><p><b>실제 SDL 렌더러의 시각 검토용 빌드입니다.</b> 기존 직접 주문 적중 처리로 실제 중첩을 1·2·3개 쌓고 그 수를 읽어 표시했습니다. 일반 플레이는 아직 기존 최대 5개·기존 피해식이며, 최대 3개/새 피해식/별의 계승은 미적용입니다. 테스트의 적은 높은 HP로 설정했고 주문 MP·턴 소모를 포함한 정상 던전 플레이 영상은 아닙니다. 이동은 검토용으로 배치했고 만료 상태는 테스트에서 지정했습니다. 촬영 때문에 별·HP·RNG가 추가로 바뀌지 않는지 확인했습니다.</p></section><section><h2>추가 후보 · 별의 계승 [4성 패시브]</h2><p>표적 처치 보상을 다음 적에게 적중시키고 그 적이 살아남으면, 새 표적의 별은 1개 대신 2개로 시작합니다. 사용자 의견에 따라 이 후보를 유지합니다. 최대 3개, 한 표적 원칙은 그대로이며 실제 전투 연결은 아직 없습니다.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
review='analysis/previews/suisei-stars01/index.html'
binary_hash=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
    p=r/name;d=read(p)
    d.update(currentGod='suisei',currentVisualReviewGod='suisei',currentVisualReviewTier=1,currentVisualReview=review,review=review,currentDesignGod='suisei',activeWork='suisei-three-star-visual-review',suiseiStarPreviewRevision=rev,suiseiStarPreviewBinarySha256=binary_hash)
    d['next']='Review Suisei native 1/2/3-star display; retain proposed inheritance start at 2 stars after kill-reward hit. Three-star cap/formulas/passives not implemented in ordinary runtime. Preserve pending Vivi/Sopia/Mela conversions.'
    d['suiseiThreeStarDraft']=read(r/'analysis/design/suisei-star3-01.json')
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-star3-01.json';d=read(p)
d['visualReview']=review
d['visualStatus']='native-preview-awaiting-user-review'
d['unapprovedPassiveCandidates']['starInheritance']='Retain user-preferred start at 2/3: only when existing kill-reward bonus hits a new marked target and it survives. Not implemented.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-fullkit01.json';d=read(p)
d['tier4Candidate']['review']='2026-11-02: user prefers keeping start-at-2 despite three-star cap. Retain candidate. Combat not implemented.'
d['tier2Candidate']['threeStarProposal']='Accuracy +3 threshold at 2 stars if this candidate is retained; not implemented.'
d['threeStarProposal']='analysis/design/suisei-star3-01.json'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
master=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=master.read_text(encoding='utf-8')
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m[1])
data['suisei']=[{'tier':1,'option':0,'title':'별자리 표식 · 별1→2→3','image':'../suisei-stars01/stacking.gif','kind':'실제 직접 공격 중첩·시각 검토, 최대3개 전투 변경 미적용'}]
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):]
s=re.sub(r'<article id="suisei".*?</article>','<article id="suisei" data-god="suisei"><h2>스이세이 1성 · 별자리 표식 [패시브]</h2><img class="scene" src="../suisei-stars01/stacking.gif"><p>몹 위 별1→2→3. 직접 주문 적중으로 중첩, native SDL 시각 검토. 일반 실행본 최대3개/새 수치/추가 패시브 미적용.</p><p><a href="../suisei-stars01/index.html">효과·수치·기도술·이동 표시</a></p><textarea data-feedback="suisei"></textarea></article>',s,count=1,flags=re.S)
# Existing current-character filter resolves from hash, so preserve all approved historical entries.
master.write_text(s,encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\suisei-stars01\\index.html"\r\n',encoding='ascii')
patch=''
for old in (b/'before').iterdir():
    new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
    patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps({'revision':rev,'nativeProof':proof,'validation':validation,'runtimeDeployed':False,'combatChanged':False,'previewBinarySha256':binary_hash,'art':read(r/'assets/holocrawl/suisei-stars01/generation.json')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# スイセイ / 스이세이 별 1→2→3 시각 초안 / 2026-11-02\n\n사용자 요청: 별최대3개 방향, 1성중첩별시각, 다음적별2개시작 후보유지. 기존승인별원화 재사용·7px별3슬롯·몹머리위10px오프셋·3개금색. 실제직접주문적중으로1/2/3중첩 표시검사, native SDL 캡처·렌더상태/RNG보존·표적이동·만료·중첩roundtrip·22신/복원 통과. 최대3개/새피해식/추가패시브는아직일반전투미적용,기존실행본su-five01유지. 비비/소피아/메라개편연결도계속미완료. '+review+' 검토후다음진행.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Suisei 1/2/3 native preview ready; ordinary runtime unchanged.')
