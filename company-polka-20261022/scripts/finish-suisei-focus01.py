from pathlib import Path
from PIL import Image
import json, hashlib, shutil, difflib

r=Path(__file__).resolve().parents[1];rev='suisei-focus02';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/suisei-focus.json');reload=read(b/'native/focus-reload.json');v=read(b/'capture-validation.json')
assert proof['status']==reload['status']==v['status']=='passed' and v['gods']==22
assert read(b/'native/suisei-three.json')['status']=='passed'
out=r/'analysis/previews/suisei-focus01';out.mkdir(parents=True,exist_ok=True)
frames=[]
for count in range(1,4):
    im=Image.open(b/f'native/shots/focus{count}.png').convert('RGB').crop((323,260,547,388)).resize((672,384),Image.Resampling.NEAREST)
    im.save(out/f'stars{count}.png');frames.append(im)
frames[0].save(out/'threshold.gif',save_all=True,append_images=frames[1:],duration=[1100,1300,1300],loop=0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스이세이 2성 · 집중 관측</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#b7efff}img{max-width:100%;image-rendering:pixelated}section{background:#1d2b3d;padding:18px;border:1px solid #48617b;border-radius:10px;margin:20px 0}td,th{padding:9px;border:1px solid #48617b}table{border-collapse:collapse}</style><h1>스이세이 2성 · 집중 관측 [패시브]</h1><section><h2>실제 적용한 효과</h2><table><tr><td>해금</td><td>신앙50,최소 기도술 없음</td></tr><tr><td>조건</td><td>현재 표적의 유효한 별2개 이상</td></tr><tr><td>효과</td><td>해당 표적에게 일반 근접·원거리 공격 및 명중 판정이 있는 공격 주문의 명중+3</td></tr><tr><td>비용</td><td>MP·신앙·턴·별 소모 없음</td></tr><tr><td>제외</td><td>필중·마법저항·폭발/휩싸기·신 권능. 무기 투사체에 중복 적용하지 않음</td></tr><tr><td>종료</td><td>별이2개 미만,표적변경/만료,신앙50 미만이면 보너스 해제</td></tr></table><p>기도술과 무관한 고정+3입니다. 명중률을3%p 올리는 효과는 아닙니다. 별을 쌓은 두 번째 공격 자체에는 소급하지 않고,그 다음 공격부터 적용합니다.</p></section><section><h2>별1개:대기 → 별2·3개:집중 관측 적용</h2><img src="threshold.gif"><p>기존 승인 별 표시를 그대로 사용합니다. 실제SDL 엔진에서 각 중첩 상태를 준비해 촬영한 비교 화면입니다. 확률적 명중 차이를 영상만으로 증명하는 시연은 아닙니다. 신앙/별 조건과 활성 여부는 게임 신앙 상태 설명에도 표시됩니다.</p></section><section><h2>검사</h2><p>native 근접·돌·투창·다트 기본 명중 보너스+3과 최종 명중 계산 경로 확인. 일반 공격 주문64개 고정 시드 비교: 별1개 '''+str(proof['spellHitsBefore'])+'''회 적중 / 별2개 '''+str(proof['spellHitsAfter'])+'''회 적중. 이 숫자는 고정 검사용 대상·낮춘 기본 명중에서의 결과이며 일반 던전 명중률 추정이 아닙니다.</p><p>필중 피해/RNG와마법저항 결과/RNG 동일,권능제외·신앙49/50·기도술0/12/27·만료·무비용 검사 및 새프로세스 저장복원과22신 회귀통과. 승인 후 일반 실행본에 적용했습니다. 기존3중첩/3·5성 피해 검사도 유지했습니다.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/design/suisei-focus01.json';d=read(p)
d.update(status='implemented-native-validated',name='집중 관측',unlockPiety=50,implementationRevision=rev,review='analysis/previews/suisei-focus01/index.html')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-fullkit01.json';d=read(p)
d['status']='core-and-tier2-implemented-tier4-pending';d['tier2Candidate'].update(status='approved-and-implemented',effect='Piety50: +3 ordinary melee/ranged and eligible attack-spell accuracy versus live marked target at2+stars. Fixed bonus, no cost. Auto-hit/MR/divine unaffected.',revision=rev)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime)
digest=hashlib.sha256(runtime.read_bytes()).hexdigest();assert digest==hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review='analysis/previews/suisei-focus01/index.html'
def update(d):
    d.update(currentGod='suisei',currentVisualReviewGod='suisei',currentVisualReviewTier=2,currentVisualReview=review,currentDesignGod='suisei',activeWork='suisei-tier2-complete',playBinarySha256=digest,suiseiCombatRevision=rev,suiseiFocusDraft=read(r/'analysis/design/suisei-focus01.json'),lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=review
    d['next']='Suisei tier2 Focused Observation implemented/deployed: piety50, +3 ordinary weapon/spell accuracy vs marked target at2+stars. Existing cap3/core preserved. Tier4 inheritance remains pending; await next review. Vivi/Sopia/Mela combat redesigns remain unimplemented.'
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('suisei',{}).update(approved=[1,2,3,5],combatRevision=rev,tier2Implemented=True,tier4Implemented=False)
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        f=r/'engine/campaign-crawl/crawl-ref/source'/key
        if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for filename in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/filename;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\suisei-focus01\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';s=p.read_text(encoding='utf-8-sig');a=s.index('## 1 스이세이');position=s.index('### 궤도 절단 ★★★',a)
s=s[:position]+'''### 집중 관측 ★★ — 패시브

- 신앙50 해금, 최소 기도술 없음. 현재 표적의 유효한 별2개 이상일 때 일반 근접·원거리 공격과 명중 판정 공격 주문에 명중+3.
- 별2개를 쌓은 공격 자체에는 소급하지 않고 다음 공격부터 적용. MP·신앙·턴·별 소모 없음, 기도술과 무관한 고정값.
- 필중·마법저항·휩싸기/폭발·신 권능 제외. 표적변경/만료·별2 미만·신앙50 미만이면 해제. 2026-11-02 실제 구현 및 일반 실행본 반영, native 검사와 저장 복원 통과.

'''+s[position:];p.write_text(s,encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
    new=r/'engine/campaign-crawl/crawl-ref/source'/old.name
    patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,runtimeDeployed=True,combatChanged=True,binarySha256=digest,nativeProof=proof,validation=v,freshRestore=reload,tier4Implemented=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 스이세이2성 집중 관측 실제 적용 완료 / 2026-11-02\n\n사용자「ㅇㅇ좋다」승인. 신앙50해금,현재표적유효별2이상명중+3,일반근접/원거리/명중공격주문 적용. 필중/MR/신권능제외·무비용·기도술고정. 근접및돌/투창/다트raw명중+3,실제주문64시드비교,필중/MR결과/RNG불변,조건·자원·저장freshrestore·22신/기존3중첩검사통과. runtime='+rev+' 배포,이전실행본체크포인트보존.4성별의계승미구현·다음검토대기.비비/소피아/메라미완료유지.기존ZIP은이번변경미포함. '+review+'\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps({'status':'passed','runtimeRevision':rev,'sha256':digest,'nativeProof':proof},ensure_ascii=False))
