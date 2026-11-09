from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib,sys
r=Path(__file__).resolve().parents[1];rev=sys.argv[1] if len(sys.argv)>1 else 'miko-passive01';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/miko/miko-passive.json');reload=read(b/'native/miko/miko-reload.json')
assert v['status']==proof['status']==reload['status']=='passed' and v['gods']==22
out=r/'analysis/previews'/rev;out.mkdir(exist_ok=False);raw=b/'native/shots'
for name,seq in [('heal',1),('shield',3)]:
    paths=[raw/f'miko-{name}-before.png']+[raw/f'miko-proc-{seq}-{f}.png' for f in range(1,5)]+[raw/f'miko-{name}-after.png']
    imgs=[Image.open(p).convert('RGB').crop((291,244,483,404)).resize((576,480),Image.Resampling.NEAREST) for p in paths]
    for i,im in enumerate(imgs):im.save(out/f'{name}-{i}.png')
    imgs[0].save(out/f'{name}.gif',save_all=True,append_images=imgs[1:],duration=[850,220,220,220,350,1600],loop=0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>미코2성 봉납의 벚꽃 · 실제 적용</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:960px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#ffcadc}</style><h1>미코2성 — 봉납의 벚꽃 [패시브] · 실제 구현</h1><p>기존 승인된 초록 십자가·벚꽃5개와 연분홍 원형 보호막을 실제 적 처치·회복·보호막에 연결했습니다. 실제SDL 검사장에서 일반 공격 주문 bolt를 적중시켜HP1인 적을 처치한 장면입니다. 위치·HP·행동속도를 통제한 검사장이며 일반 던전 플레이 영상은 아닙니다. 화면에 효과를 덧그리지 않았습니다.</p><section><h2>실제 처치 → HP 회복</h2><img src="heal.gif"><p>기도술12: HP가 부족하면4 회복. 초록 십자가와 벚꽃이 캐릭터로 모입니다.</p></section><section><h2>풀피에서 실제 처치 → 원형 보호막</h2><img src="shield.gif"><p>기도술12: 보호막4 생성, 상한8. 보호막이 있는 동안 연분홍 원형 표시가 유지됩니다.</p></section><section><h2>실제 수치</h2><p>신앙50 해금 / 최소 기도술 없음 / 추가MP·신앙·행동 소모 없음. 자신과 경험치를 주는 적이 모두 성역 안일 때 직접 처치하면2+floor(기도술/6) HP 회복. 20aut마다 최대1회. 초과 회복량은 보호막으로, 상한4+floor(기도술/3). 초과 회복을 얻을 때 지속50aut로 갱신. 성역 이탈·재설치·층 이동·만료·신앙50 미만이면 제거.</p><p>일반 공격·주문·독·구름·함정 등은 피해 감소 후 보호막으로 흡수합니다. 자해 비용·고통·신의 징벌은 제외합니다. 불꽃 지속 피해·소환수 처치·경험치 없는 적은 회복 발동 대상이 아닙니다.</p></section><p>실제 처치·부분 초과·풀피·발동 간격·상한·흡수·제외 조건·성역 이탈·만료·층 이동, 새 프로세스 저장복원과 동일한 흡수 후 상태/난수,22신 회귀 검사 통과. 일반 실행본 반영.</p></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime);sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design=dict(status='implemented-native-validated',revision=rev,date='2026-11-03',name='봉납의 벚꽃',tier=2,type='passive',unlockPiety=50,heal='2+floor(Inv/6)',shieldCap='4+floor(Inv/3)',procIntervalAut=20,shieldDurationAut=50,save='Existing saved shield/defence/proc_ready fields; no new serializer layout. Fresh-process absorption/state/RNG verified.',visual='Approved green cross,five blossoms,pale circular barrier now connected to actual kills and shield.',review=f'analysis/previews/{rev}/index.html',combatImplemented=True,runtimeDeployed=True,binarySha256=sha)
(r/'analysis/design/miko-passive01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='miko',currentDesignGod='miko',currentVisualReviewGod='miko',currentVisualReviewTier=2,currentVisualReview=design['review'],activeWork='miko-tier2-implemented-review',mikoCombatRevision=rev,mikoPassive=design,playBinarySha256=sha,lastArchiveIncludesLatest=False,fullKitCompletedGods=['suisei','miko'])
    if 'mikoBloomDraft' in d:d['mikoBloomDraft'].update(status='approved-art-connected-to-gameplay',combatImplemented=True,runtimeDeployed=True,combatRevision=rev)
    if 'review' in d:d['review']=design['review']
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('miko',{}).update(approved=[1,2,3,5],pending=[],combatRevision=rev,tier2Implemented=True)
    d['next']='Miko1/2/3/5 complete: review actual kill-heal/overflow-shield GIF. Next original-order god is Aki; preserve approved core art and assess one/two extra passives. Vivi/Sopia/Mela combat conversions remain pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        p=r/'engine/campaign-crawl/crawl-ref/source'/key
        if p.is_file():d['sourceSha256'][key]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\'+rev+'\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';text=p.read_text(encoding='utf-8-sig');start=text.index('## 2 미코');i=text.index('### 액막이 불꽃 ★★★',start)
text=text[:i]+'''### 봉납의 벚꽃 ★★ — 패시브

- 신앙50 해금, 최소 기도술 없음. 자신과 경험치 대상 적이 모두 성역 안일 때 직접 처치하면 `2+floor(I/6)` HP 회복. 20aut마다 최대1회, 추가 비용·턴 없음.
- 최대HP를 넘는 회복량은 벚꽃 보호막. 상한 `4+floor(I/3)`, 초과 회복 획득 시 지속50aut 갱신. 성역 밖·재설치·층 이동·만료·신앙50 미만이면 제거.
- 일반 공격·주문·독·구름·함정 등 피해 감소 후 흡수. 자해 비용·고통·징벌 제외. 소환수·성역 불꽃 지속 피해·경험치 없는 적의 처치로는 발동하지 않음.
- 승인된 초록 십자가+벚꽃5개, 연분홍 원형 보호막을 실제 처치 및 보호막 상태에 연결. 2026-11-03 실제 구현·새 프로세스 저장복원 검증.

'''+text[i:];p.write_text(text,encoding='utf-8')
note='# 미코2성 봉납의 벚꽃 실제 적용 / 2026-11-03\n\n'+design['review']+' 실제 처치회복·초과보호막·승인된 이펙트 연결. Inv12 회복4/보호막상한8, 신앙50, 간격20aut, 지속50aut. 저장된 shield/defence/proc_ready 재사용. 새프로세스복원·흡수후상태/난수·22신 회귀 통과. runtime='+rev+'. 미코1/2/3/5 완료, 다음은아키. 비비/소피아/메라 개편 전투처리 미완료 유지. 기존ZIP 최신변경미포함.\n\n'
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
