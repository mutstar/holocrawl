from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib,sys
r=Path(__file__).resolve().parents[1];rev=sys.argv[1] if len(sys.argv)>1 else 'aki-nutrient01';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/aki/aki-nutrient.json');reload=read(b/'native/aki/aki-reload.json')
assert v['status']==proof['status']==reload['status']=='passed' and v['gods']==22
out=r/'analysis/previews'/rev;out.mkdir(exist_ok=False);raw=b/'native/shots'
for tier in [1,3,5]:
    im=Image.open(raw/f'aki-tier{tier}-{7 if tier==5 else 5}x{7 if tier==5 else 5}.png').convert('RGB').crop((227,196,515,484)).resize((576,576),Image.Resampling.NEAREST)
    im.save(out/f'tier{tier}.png')
imgs=[Image.open(raw/f'aki-mp-{name}.png').convert('RGB').crop((227,0,1152,484)) for name in ['before','after']]
imgs[0].save(out/'mp-recovery.gif',save_all=True,append_images=imgs[1:],duration=[1200,1700],loop=0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>아키 · MP 회복과 5/5/7</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#ffcadc}</style><h1>아키 · 정원5×5 → 5×5 → 7×7 / 2성MP 회복 실제 적용</h1><section><h2>1성 — 장미의 씨앗 [액티브] · 5×5</h2><img src="tier1.png"><p>처음부터5×5. MP3 / 신앙 소모 없음 / 1턴, 완료1턴 뒤 개화, 개화 후20+0.5×기도술 턴 지속. 가시 최대3, 이동 지연·지속 피해 수치는 유지. 최소 기도술 없음.</p></section><section><h2>2성 — 장미의 양분 [패시브]</h2><img src="mp-recovery.gif"><p>우측MP 수치10→12: 실제 공격 bolt로 가시3중첩 적을 처치했습니다. 적 위치·HP·행동을 통제한SDL 검사장이며 일반 던전 플레이 영상은 아닙니다.</p><p>신앙50 / 최소 기도술 없음 / 추가 비용·행동 없음. 정원 안 경험치 대상 적이 가시3중첩으로 죽으면 min(3,1+floor(기도술/12))MP 회복. 기도술0/12/27에서1/2/3MP. 30aut마다 최대1회. 직접 공격·정원 지속 피해·아키 공격 식물 처치에 적용. 5성 만개는 소모 직전3중첩 인정. 최대MP까지 회복하며 풀MP이면 보상 저장·재사용 대기 발생 없음.</p></section><section><h2>3성 — 가시 장미 [액티브] · 5×5</h2><img src="tier3.png"><p>MP4 / 신앙3 / 1턴, 공격 식물2개. 지속8+0.3×기도술 턴, 최대2개. 정원 범위5×5 유지. 신앙75, 최소 기도술 없음.</p></section><section><h2>5성 — 붉은 정원의 만개 [액티브] · 7×7</h2><img src="tier5.png"><p>MP6 / 신앙12 / 1턴. 기존7×7 만개·가시 폭발·식물 가속·시듦 수치는 유지. 신앙120, 최소 기도술 없음.</p></section><p>실제 일반 공격·정원 지속 피해·식물의 native bolt·만개 처치,3중첩/만료/정원 밖/경험치 없음/풀MP/신앙 경계/재사용 간격 검증. 새 프로세스 저장복원 후 재사용 간격과 실제 처치MP·상태·난수 일치.22신 회귀 및 기존 저장복원 검사 통과 후 일반 실행본 반영.</p></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime);sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design=dict(status='implemented-native-validated',date='2026-11-03',revision=rev,review=f'analysis/previews/{rev}/index.html',widths=[5,5,7],tier2=dict(name='장미의 양분',type='passive',unlockPiety=50,mp='min(3,1+floor(Inv/12))',cooldownAut=30,stacks=3,sources=['direct','garden DoT','own rose','bloom pre-consumption'],fullMp='No storage or cooldown consumed'),save='Existing saved rest[0] cooldown; no serializer layout changes.',runtimeDeployed=True,binarySha256=sha)
(r/'analysis/design/aki-nutrient01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='aki',currentDesignGod='aki',currentVisualReviewGod='aki',currentVisualReviewTier=2,currentVisualReview=design['review'],activeWork='aki-mp557-implemented-review',akiCombatRevision=rev,akiFullKit=design,playBinarySha256=sha,lastArchiveIncludesLatest=False,fullKitCompletedGods=['suisei','miko','aki'])
    if 'review' in d:d['review']=design['review']
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('aki',{}).update(approved=[1,2,3,5],pending=[],combatRevision=rev,tier2Implemented=True)
    d['next']='Review AkiMP-on-three-thorn-kill and5/5/7 native preview. Suisei,Miko,Aki full kits implemented. Next original-order god Fubuki. Vivi/Sopia/Mela combat conversions remain pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        p=r/'engine/campaign-crawl/crawl-ref/source'/key
        if p.is_file():d['sourceSha256'][key]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\'+rev+'\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';text=p.read_text(encoding='utf-8-sig');a=text.index('## 3 아키');z=text.index('## 4 후부키',a);part=text[a:z]
part=part.replace('시야 안 4칸 바닥에 3×3 정원','시야 안 4칸 바닥에 5×5 정원').replace('정원 5×5로 상시 확대. 새 칸은 10 aut 뒤 개화. 가시 축적도 10 aut마다 1.','정원5×5 유지. 가시 축적은10aut마다1. 2026-11-03 승인: 처음부터5×5, 3성5×5, 5성7×7.')
i=part.index('### 가시 장미 ★★★');part=part[:i]+'''### 장미의 양분 ★★ — 패시브

- 신앙50 해금, 최소 기도술 없음. 정원 안 가시3중첩 경험치 대상 적을 직접 공격·정원 지속 피해·자신의 공격 식물로 처치하면 `min(3,1+floor(I/12))`MP 회복. 30aut마다 최대1회.
- 5성 만개는 가시 소모 직전3중첩 인정. 최대MP까지만 회복. 풀MP에서는 저장 보상·쿨다운 없음. 추가 자원·행동 비용 없음.
- 2026-11-03 실제 전투·native bolt 식물 처치·저장복원/동일 전투 난수 검증 완료.

'''+part[i:];text=text[:a]+part+text[z:];p.write_text(text,encoding='utf-8')
note='# 아키 MP 회복·5/5/7 실제 적용 / 2026-11-03\n\n'+design['review']+' 신앙50 장미의 양분[패시브]: 정원 안 가시3중첩 처치 시MP1/2/3(Inv0/12/27), CD30aut. 직접·정원DoT·아키식물·만개소모직전3 인정. 일반/신앙75 정원5×5, 만개7×7. 기존가시피해·식물수·만개수치 유지. 새프로세스저장후CD·실제처치MP·난수/상태일치·22신 회귀 통과. runtime='+rev+'. 다음후부키. 비비/소피아/메라 개편전투처리 미완료 유지. 기존ZIP 최신변경미포함.\n\n'
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
