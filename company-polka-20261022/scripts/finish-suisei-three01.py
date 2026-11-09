from pathlib import Path
from PIL import Image
import json, hashlib, shutil, difflib

r=Path(__file__).resolve().parents[1]
rev='suisei-three03'
b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/suisei-three.json')
validation=read(b/'capture-validation.json')
reload=read(b/'native/suisei-reload.json')
assert proof['status']==validation['status']==reload['status']=='passed'
assert validation['gods']==22
raw=b/'native/shots'
out=r/'analysis/previews/suisei-three01'
out.mkdir(parents=True,exist_ok=True)
frames=[]
for i in range(5):
    im=Image.open(raw/f'three-{i}.png').convert('RGB').crop((323,260,547,388)).resize((672,384),Image.Resampling.NEAREST)
    im.save(out/f'stars{i}.png');frames.append(im)
frames[0].save(out/'stacking-and-cap.gif',save_all=True,append_images=frames[1:],duration=[700,850,850,1200,1200],loop=0)

focus={
 'status':'proposal-not-implemented','date':'2026-11-02','name':'集中観測 / 집중 관측',
 'tier':2,'type':'passive','proposedUnlockPiety':50,'minimumInvocations':0,
 'condition':'Current marked target alive, mark unexpired, at least2of3 stars.',
 'effect':'Accuracy +3 on attacks with ordinary hit checks, including melee/ranged and eligible attack spells. No damage bonus. Auto-hit attacks and MR checks unaffected.',
 'cost':'No activation, MP, piety consumption, extra action or star consumption.',
 'scaling':'Fixed +3; does not scale with Invocations or increase hit chance by a flat3 percentage points.',
 'visualDirection':'Use the approved 2/3-star indicator to recognize eligibility; no new large effect required.'
}
(r/'analysis/design/suisei-focus01.json').write_text(json.dumps(focus,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
design=r/'analysis/design/suisei-star3-01.json';d=read(design)
d.update(status='implemented-native-validated',implementationRevision=rev,visualStatus='approved-and-live',visualProposal='Approved indicator now connected to ordinary gameplay: cyan1/2 and gold3 above marked enemy.',ordinaryRuntime='runtime/tiles01/HoloCrawl.exe')
d['constraints']=[x for x in d['constraints'] if not x.startswith('Actual game still')]
d['saveMigration']='Legacy v1 Suisei stars ceil(3*S/5), cap3; keep already-rolled reward and preserve +5/old-star bonus of already queued comets. New Suisei payload v2. Other gods remain v1.'
design.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스이세이 · 3중첩 적용 / 2성 초안</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#b7efff}img{max-width:100%;image-rendering:pixelated}section{background:#1d2b3d;padding:18px;border:1px solid #48617b;border-radius:10px;margin:20px 0}table{border-collapse:collapse}td,th{padding:9px;border:1px solid #48617b}</style><h1>스이세이 · 최대 별3개 실제 적용</h1><section><h2>실제 적중0→1→2→3→3</h2><img src="stacking-and-cap.gif" alt="실제 적중 네 번, 별은3개에서 유지"><p>기존 승인 표시를 일반 플레이에 연결했습니다. 네 번째 적중에도 별이3개로 유지됩니다. native 엔진의 직접 주문 적중을 사용한 고정 시험장 영상이며,적HP는 검사 목적으로 높게 설정했습니다. 확대·반복만 적용했습니다.</p></section><section><h2>반영한 권능</h2><table><tr><th>성급·구분</th><th>수치</th></tr><tr><td>1성·패시브 / 수동 표적 변경</td><td>별 최대3개. 처치 보상1d(3+4S),별1/2/3 평균4/6/8. 3턴 내 다음 무기 공격·직접 주문에 추가 물리 피해,AC 적용. 별 자체가 평타 피해를 올리지는 않음</td></tr><tr><td>3성·액티브</td><td>MP3·신앙3·1턴,사거리5. 2d(8+⌊I/2⌋)+5S. I12 별0/1/2/3 평균15/20/25/30,AC 전</td></tr><tr><td>5성·액티브</td><td>MP6·신앙10·1턴,사거리6 고정3×3,시전 완료2턴 후낙하. 3d(10+⌊I/2⌋)+8S,표적만별추가. I12 평균25.5/33.5/41.5/49.5,AC 전</td></tr></table><p>S는 별,I는 기도술. 기존 명중·소모·아군피해 규칙 유지. 실제피해·비용·착탄시각·저장복원·22신회귀 검사 통과 후 일반실행본에 배포했습니다.</p></section><section><h2>다음: 2성 집중 관측 [패시브·제안]</h2><p>예정 해금 신앙50 / 최소 기도술 없음 / MP·신앙·턴·별 소모 없음.</p><p>현재 표적에게 별2개 이상이면 명중+3. 근접·원거리·명중 판정이 있는 공격 주문에 적용하는 안입니다. 필중 공격·마법저항 판정에는 영향 없음. 명중률3% 증가라는 뜻은 아니며, 피해는 그대로입니다. 기도술과 무관하게 고정+3.</p><p><b>2성 효과와4성 별의 계승은 아직 미구현입니다.</b> 이번에 실제 반영한 범위는 기존1·3·5성의3중첩 수치와 표시입니다.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')

# Preserve the exact previous runtime before installing the checked binary.
runtime=r/'runtime/tiles01/HoloCrawl.exe'
assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe')
shutil.copy2(b/'capture-engine.exe',runtime)
sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
assert sha==hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review='analysis/previews/suisei-three01/index.html'
def update(d):
    d.update(currentGod='suisei',currentVisualReviewGod='suisei',currentVisualReviewTier=2,currentVisualReview=review,currentDesignGod='suisei',activeWork='suisei-tier2-passive-design',playBinarySha256=sha,suiseiCombatRevision=rev,suiseiThreeStarDraft=read(design),suiseiFocusDraft=focus,lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=review
    d['next']='Review Suisei tier2 Focused Observation passive proposal: piety50, +3 accuracy vs live marked target at2+stars. Core cap3/reward/cut/comet and approved stack indicator are implemented and deployed. Tier2/tier4 not implemented. Vivi/Sopia/Mela combat conversions remain pending.'
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('suisei',{}).update(approved=[1,3,5],combatRevision=rev,starIndicatorApproved=True)
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        p=r/'engine/campaign-crawl/crawl-ref/source'/key
        if p.is_file():d['sourceSha256'][key]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for filename in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/filename;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-fullkit01.json';d=read(p)
d['coreCombatRevision']=rev;d['coreThreeStarsImplemented']=True;d['tier2Proposal']='analysis/design/suisei-focus01.json'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\suisei-three01\\index.html"\r\n',encoding='ascii')
patch=''
for old in (b/'before').iterdir():
    new=r/'engine/campaign-crawl/crawl-ref/source'/old.name
    patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,runtimeDeployed=True,combatChanged=True,binarySha256=sha,nativeProof=proof,validation=validation,suiseiFreshRestore=reload,passive2Implemented=False,passive4Implemented=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 스이세이 최대3별·실제수치·표시 연결 완료 / 2026-11-02\n\n사용자 승인에 따라 기존1/3/5를 실제변경: cap3,처치보상1d(3+4S),3성별당+5,5성표적별당+8. 승인청록1/2·금색3표시 일반플레이연결. 비용/거리/착탄시각유지. native실적중4회cap·보상소비·활성피해비교·시간/비용·구저장변환·별/혜성freshrestore·22신회귀통과. runtime/tiles01/HoloCrawl.exe='+rev+' 배포,이전실행본은 analysis/native/'+rev+'/previous-runtime.exe 보존. 추가2/4성미구현. 다음2성집중관측[패시브]안:신앙50,별2이상표적명중+3,필중/MR제외,비용없음. 비비/소피아/메라미완료유지. 기존ZIP은이번변경미포함. '+review+'\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps({'status':'passed','deployedRevision':rev,'sha256':sha,'next':'Suisei tier2 passive proposal','nativeDamageProof':proof},ensure_ascii=False))
