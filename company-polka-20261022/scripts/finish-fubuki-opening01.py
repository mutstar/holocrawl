from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib,sys
r=Path(__file__).resolve().parents[1];rev=sys.argv[1] if len(sys.argv)>1 else 'fubuki-opening01';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/fubuki/fubuki-opening.json');reload=read(b/'native/fubuki/fubuki-reload.json')
assert v['status']==proof['status']==reload['status']=='passed' and v['gods']==22
out=r/'analysis/previews'/rev;out.mkdir(exist_ok=False)
for name in ['before','after']:
    Image.open(b/f'native/shots/fubuki-opening-{name}.png').convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST).save(out/f'{name}.png')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>후부키2성 여우의 빈틈</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#bceeff}</style><h1>후부키2성 — 여우의 빈틈 [패시브] · 실제 적용</h1><section><h2>기만 → 첫 직접 적중 → 추가 여우불1발</h2><p>신앙50 해금 / 최소 기도술 없음 / 추가MP·신앙·행동 비용 없음. 기만당한 살아 있는 적에게 플레이어가 무기·투척·직접 공격 주문을 처음 적중시키면, 그 적을 속인 분신 하나가 기존 협공에 더해 여우불1발을 추가 발사합니다.</p><p>기만 성공1회당 한 번. 빗나가면 기회 유지. 추가 여우불 자체의 빗나감은 재발사하지 않습니다. 피해가AC 등으로0이어도 직접 공격이 적중했다면 발동합니다. 플레이어 공격이나 기존 협공으로 적이 먼저 죽으면 취소합니다. 분신 사망·기만 만료·시야/사선/거리 조건 불충족 시 추가 발사는 없습니다.</p><p>기존 여우불 명중20+기도술, 피해1d(6+floor(기도술/3)), 화염 절반·영적 물리 절반 및 방어 처리, min(공격소요aut,10)/10 시간 보정 그대로입니다. 기도술12·1턴 공격이면 추가 발사 명중 시 평균5.5, 방어 적용 전. 5성에서4분신이어도 추가는1발뿐입니다.</p><p>권능·지속 피해·소환수·무턴 행동은 발동 대상이 아닙니다. 새 기만 성공 시 다시1회 가능. 추가 발사 사용 여부는 기존 저장 필드로 보존됩니다.</p></section><section><h2>실제 검사장</h2><img src="before.png"><p>실제로 분신을 소환해 기만에 성공시킨 뒤 일반 공격 주문bolt를 적중시켜 추가 여우불과 실제 피해 증가를 검사했습니다. 높은 적HP·고정 위치를 사용한 검사장입니다. 별도의 새 이펙트나 투사체 애니메이션을 추가한 변경은 아닙니다.</p></section><section><h2>검사 통과</h2><p>신앙49/50, 실제 기만·일반 주문 적중·추가 피해, 두 번째 적중 중복 방지, 실제 빗나감 후 기회 유지, 근접/원거리/주문 적중 경로, 빠른 공격·무턴 행동, 만료·죽은 분신·거리 제외,4분신 중 추가1회, 새 기만 재충전, 미사용·사용 상태 각각 새프로세스 저장복원 후 동일 공격·피해·상태·난수 일치,22신 회귀와 기존 저장복원 검사 통과.</p></section><section><h2>기존 승인 이펙트</h2><p>3성 — 여우 바꿔치기 [액티브]</p><img src="../fubuki-vfx05/swap-fire.gif"><p>5성 — 백여우 행렬 [액티브]</p><img src="../fubuki-vfx05/fox-arrival.gif"></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime);sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design=dict(status='implemented-native-validated',date='2026-11-03',revision=rev,review=f'analysis/previews/{rev}/index.html',tier=2,type='passive',name='여우의 빈틈',unlockPiety=50,extraFoxfire=1,trigger='First successful ordinary direct hit on living deceived foe; only its deceiving image fires extra, once per successful deception.',cost='No extra MP/piety/action. Same native hit/resistance/time-scaling as ordinary foxfire.',save='Existing Fubuki target.kind:0unspent/1spent. Reset on successful deception. Existing raven_hits stores deceiving image and expiry. No serializer layout changes.',newVfxAdded=False,runtimeDeployed=True,binarySha256=sha)
(r/'analysis/design/fubuki-opening01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='fubuki',currentDesignGod='fubuki',currentVisualReviewGod='fubuki',currentVisualReviewTier=2,currentVisualReview=design['review'],activeWork='fubuki-opening-implemented-review',fubukiCombatRevision=rev,fubukiOpening=design,playBinarySha256=sha,lastArchiveIncludesLatest=False,fullKitCompletedGods=['suisei','miko','aki','fubuki'])
    if 'review' in d:d['review']=design['review']
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('fubuki',{}).update(approved=[1,2,3,5],pending=[],combatRevision=rev,tier2Implemented=True)
    d['next']='Fubuki2-star first-hit extra foxfire implemented and validated. No new projectile/VFX claimed. Next original-order god Ayame. Vivi/Sopia/Mela combat redesigns remain pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        p=r/'engine/campaign-crawl/crawl-ref/source'/key
        if p.is_file():d['sourceSha256'][key]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\'+rev+'\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';text=p.read_text(encoding='utf-8-sig');a=text.index('## 4 후부키');i=text.index('### 여우 바꿔치기 ★★★',a)
text=text[:i]+'''### 여우의 빈틈 ★★ — 패시브

- 신앙50 해금, 최소 기도술 없음. 기만당한 살아 있는 적에게 플레이어가 첫 일반 직접 공격을 적중시키면, 해당 적을 기만한 분신 하나가 여우불1발 추가 협공. 기만 성공1회당 한 번.
- 빗나감은 기회 유지. 추가 여우불 자체가 빗나가도 재발사 없음. 근접·투척·직접 공격 주문에 적용. 권능·지속 피해·소환수·무턴 행동 제외.
- 추가 비용·턴 없음. 기존 여우불 명중·저항·AC·빠른 공격 피해 시간 보정 유지. 5성4분신이어도 추가는1발. 적이 먼저 죽으면 취소. 기만 만료·분신 사망·거리/시야/사선 조건 적용.
- 기존 target.kind와 raven_hits로 사용 여부·기만 분신/만료 저장. 새 기만 성공 시 재충전. 2026-11-03 실제 기만/주문적중·추가 피해·미사용/사용 저장복원 검증 완료.

'''+text[i:];p.write_text(text,encoding='utf-8')
note='# 후부키2성 여우의 빈틈 실제 적용 / 2026-11-03\n\n'+design['review']+' 기만된 적 첫 직접 적중에 기만한 분신이추가여우불1회, 기만성공당1회. 신앙50. 빗나감유지·4분신중1추가·빠른공격/무턴/만료/죽은분신/거리·실제추가피해·미사용/사용각새프로세스복원동일상태/난수·22신 회귀 통과. 새VFX추가없음. runtime='+rev+'. 다음아야메. 비비/소피아/메라 개편전투처리 미완료 유지. 기존ZIP최신변경미포함.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md','BALANCE_WORKPLAN.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
patch=''
for old in (b/'before').rglob('*'):
    if old.is_file() and old.suffix in {'.cc','.h'}:
        rel=old.relative_to(b/'before');new=r/'engine/campaign-crawl/crawl-ref/source'/rel
        patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),new.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=sha,nativeProof=proof,freshReload=reload,validation=v,runtimeDeployed=True),indent=2),encoding='utf-8')
print(json.dumps(dict(status='passed',revision=rev,sha256=sha)))
