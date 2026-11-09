from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib,sys
r=Path(__file__).resolve().parents[1];rev=sys.argv[1] if len(sys.argv)>1 else 'ayame-zanshin02';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/ayame/ayame-zanshin.json');reload=read(b/'native/ayame/ayame-reload.json')
assert v['status']==proof['status']==reload['status']=='passed' and v['gods']==22
out=r/'analysis/previews'/rev;out.mkdir(exist_ok=False)
for name in ['banked','before','after']:
    Image.open(b/f'native/shots/ayame-zanshin-{name}.png').convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST).save(out/f'{name}.png')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>아야메2성 귀인의 잔심</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#ffd3df}</style><h1>아야메2성 — 귀인의 잔심 [패시브] · 실제 적용</h1><section><h2>지정 상대 근접 처치 → 다음 새 적 첫 타부터1성 보너스</h2><p>신앙50 / 최소 기도술 없음 / 추가MP·신앙·행동 비용 없음. 경험치를 주는 지정 상대를 직접 인접 근접 처치하면, 해당 공격 완료 후30aut(보통3턴) 동안 잔심을 획득합니다. 다음 새로운 경험치 대상 적을 인접 근접 공격하면 첫 타부터 명중3+floor(기도술/6), 살육2+floor(기도술/9)를 적용합니다.</p><p>기도술12에서 명중+5·살육+3. 추가EV나5성 강화 보너스는 없음. 첫 공격 시도에 소모되며 빗나가도 소모합니다. 행동 취소·무턴 행동·원거리·주문·리치·경험치 없는 대상에는 소모하지 않습니다. 만료·층 이동 시 제거. 중첩 없이 새 보상은 시간을 갱신합니다.</p></section><section><h2>쌍섬 [액티브]과 연결</h2><p>새 적에게 쌍섬을 쓰면 첫 타는 잔심으로1성 명중·살육 보너스, 두 번째는 첫 타 후 지정된 결투 상대의 기존1성 보너스를 받습니다. 첫 타 적중 시 두 번째 명중+8이라는 기존 규칙도 유지합니다. 잔심은 한 번만 소모됩니다. 5성 결투장 처치의MP 회복·쌍섬 제한 해제와 함께 발동합니다.</p></section><section><h2>실제 검사장</h2><img src="before.png"><p>기존 상대를 실제 일반 근접 공격으로 처치하고, 잔심이 남은 상태에서 다음 오크에게 실제 근접 공격을 실행했습니다. 위치·장비·적HP를 통제한SDL 검사장이며 일반 던전 플레이 영상은 아닙니다. 이번 변경은 전투 처리이며 새 전용 이펙트는 추가하지 않았습니다.</p></section><section><h2>검사 통과</h2><p>실제 첫 근접 지정·지정 상대 처치·공격 완료 후3턴 보장·다음 상대 첫 근접 소모·쌍섬·5성 처치 호환, 기도술0/12/27의명중·살육, 빗나감 소모·취소/무턴 보존·리치/주문/원거리/경험치 없음/만료/층 이동 제외, 새 프로세스 저장복원 후 동일한 실제 근접2회·피해·상태·난수 일치,22신 회귀와 기존 저장복원 검사 통과.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime);sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design=dict(status='implemented-native-validated',date='2026-11-03',revision=rev,review=f'analysis/previews/{rev}/index.html',tier=2,type='passive',name='귀인의 잔심',unlockPiety=50,durationAfterCompletedKillAut=30,accuracy='3+floor(Inv/6)',slaying='2+floor(Inv/9)',trigger='Direct adjacent ordinary melee kill of marked XP foe; next new adjacent XP foe first melee swing gains1star hit/slaying and consumes on attempt,even miss.',save='Existing saved tertiary expiry; action-only eligibility/snapshot fields are transient. No serializer layout changes.',newVfxAdded=False,runtimeDeployed=True,binarySha256=sha)
(r/'analysis/design/ayame-zanshin01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='ayame',currentDesignGod='ayame',currentVisualReviewGod='ayame',currentVisualReviewTier=2,currentVisualReview=design['review'],activeWork='ayame-zanshin-implemented-review',ayameCombatRevision=rev,ayameZanshin=design,playBinarySha256=sha,lastArchiveIncludesLatest=False,fullKitCompletedGods=['suisei','miko','aki','fubuki','ayame'])
    if 'review' in d:d['review']=design['review']
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('ayame',{}).update(approved=[1,2,3,5],pending=[],combatRevision=rev,tier2Implemented=True)
    d['next']='Ayame2-star zanshin implemented and validated. No new VFX claimed. Next original-order god Choco. Vivi/Sopia/Mela combat redesigns remain pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        p=r/'engine/campaign-crawl/crawl-ref/source'/key
        if p.is_file():d['sourceSha256'][key]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\'+rev+'\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';text=p.read_text(encoding='utf-8-sig');a=text.index('## 5 아야메');i=text.index('### 쌍섬 ★★★',a)
text=text[:i]+'''### 귀인의 잔심 ★★ — 패시브

- 신앙50 해금, 최소 기도술 없음. 지정한 경험치 대상 적을 직접 인접 근접 처치하면, 공격 완료 후30aut 동안 잔심 획득. 중첩 없음, 재획득 시 시간 갱신.
- 다음 새 경험치 대상 적의 첫 인접 근접 공격부터1성 명중 `3+floor(I/6)`·살육 `2+floor(I/9)` 적용. 첫 시도에 소모, 빗나가도 소모. 추가EV·5성 강화 보너스 없음.
- 취소·무턴·원거리·주문·리치·경험치 없는 대상에는 보존. 만료·층 이동 시 해제. 추가 자원·행동 비용 없음.
- 쌍섬 첫 타 잔심, 두 번째는 새 지정 상대의 기존1성 보너스. 5성 처치 보상과 호환. 기존 tertiary로저장, action context의사용/해금 스냅샷은임시. 2026-11-03 실제근접처치·쌍섬·다음상대첫근접·새프로세스복원 검증완료.

'''+text[i:];p.write_text(text,encoding='utf-8')
note='# 아야메2성 귀인의 잔심 실제 적용 / 2026-11-03\n\n'+design['review']+' 신앙50. 지정XP적 인접근접처치 완료후3턴, 다음새적첫근접에1성명중/살육 적용, 빗나가도소모. Inv12 +5/+3, 추가EV없음. 실제처치·쌍섬·5성호환·다음첫근접·취소/무턴/리치/비근접/무경험치/만료/층이동·새프로세스복원후동일근접2회상태/난수·22신 회귀 통과. 새VFX추가없음. runtime='+rev+'. 다음초코. 비비/소피아/메라 개편전투처리 미완료 유지. 기존ZIP최신변경미포함.\n\n'
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
