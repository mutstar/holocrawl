from pathlib import Path
from PIL import Image
import json, hashlib, shutil, re, difflib, html

r=Path(__file__).resolve().parents[1]
base=r/'analysis/native/koyori-caster02'
original=r/'analysis/native/koyori-caster01/before'
src=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(base/'capture-validation.json')
assert proof['status']=='passed' and proof['gods']==22
assert read(base/'native/koyori-caster.json')['status']=='passed'
assert read(base/'native/koyori-reload.json')['status']=='passed'
for name,digest in read(base/'preserved-files.json').items():
    assert hashlib.sha256((src/name).read_bytes()).hexdigest()==digest,name
out=r/'analysis/previews/koyori-caster02';out.mkdir(parents=True,exist_ok=True)
shots=base/'native/shots'
titles=['발열','냉각','독성'];next_names=['냉각','독성','발열']
effects=['추가 화염 피해 1d(4+⌊I/6⌋). 기도술 12에서는 1~6 피해.',
         '추가 냉기 피해 1d(3+⌊I/9⌋), 2턴간 이동 시간 +15%. 기도술 12에서는 1~4 피해.',
         '2턴 동안 매 턴 2+⌊I/12⌋ 독 피해. 기도술 12에서는 3씩 두 번.']
cards=[]
for i in range(3):
    frames=[]
    for phase in ['before','after','settled']:
        im=Image.open(shots/f'koyori1-{i}-{phase}.png').convert('RGB')
        frames.append(im.crop((291,252,515,428)).resize((448,352),Image.Resampling.NEAREST))
    frames[0].save(out/f'koyori1-{i}.gif',save_all=True,append_images=frames[1:],duration=[850,1000,700],loop=0,optimize=False)
    cards.append(f'<article><h3>{titles[i]} 시약이 실린 주문</h3><p>{effects[i]}</p><p>적중 후 다음 시약: <b>{next_names[i]}</b></p><img src="../koyori-caster02/koyori1-{i}.gif" alt="{titles[i]} 시약 실제 주문 시전 전후"></article>')
css='body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1250px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#ffb8df}h2{color:#a6e9f4}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}article{background:#1b2736;padding:18px;border-radius:12px}img{max-width:100%;image-rendering:pixelated}.info{background:#202b3e;padding:16px;border-radius:10px}section{scroll-margin-top:20px}h3{margin-top:0}b{color:#ffe09d}a{color:#abe7ff}'
page='<!doctype html><html lang="ko"><meta charset="utf-8"><title>코요리 · 마법형 1성 실험 개시</title><style>'+css+'</style><h1>코요리 · 마법형 1성 실험 개시</h1><section id="tier1"><p class="info"><b>발열 → 냉각 → 독성 → 반복</b><br>공격 주문이 실제 피해를 주면 자동으로 시약을 부착합니다. 시약 제조·투척·무기 도포 버튼은 제거했습니다.<br>해금: 신앙 ★(30) · 최소 기도술 제한 없음 · 시약 추가 MP/신앙 소모 없음.</p><p><b>캐릭터 옆 병 = 다음 시약</b> / <b>몹 옆 병 = 이미 붙은 표식</b><br>아래는 실제 마법의 다트 시전 전 → 표식 적용 → 시전 후 장면입니다. 기본 주문 MP1만 소모합니다. 각 클립은 해당 시약 순환 단계에서 시작하는 검토 장면입니다.</p><div class="cards">'+''.join(cards)+'</div><p class="info">표식 유지 6턴. 냉각은 이동만 방해하며 공격·시전 속도는 그대로입니다. 독 면역 적도 원래 주문이 피해를 주면 반응용 표식은 남습니다.<br>한 주문의 다단히트는 같은 적에게 한 번만 적용하며, 광역 주문에는 같은 시약이 실립니다. 빗나감·0피해에는 순환하지 않습니다.<br>평타·마법봉·소환수·구름·독 후속 피해는 제외. 파괴의 구슬은 직접 시전한 투사체의 실제 적중 시 적용됩니다.</p><p>기도술 I는 현재 기도술 수치입니다. 영상은 기도술 12·신앙 60의 고정 시험 장면이며, 3성 반응이 없는 상태에서 1성 효과를 보여줍니다. 표시되는 피해식은 저항 적용 전 수치입니다.</p><p>3성의 공격 주문 사거리 +1·반응 피해 ×0.85, 5성 임계 실험의 MP6·신앙10·0.5턴·8턴/4회·재사용20턴도 코드에 적용했습니다. 현재 시각 검토는 1성부터 진행합니다.</p></section></html>'
(out/'index.html').write_text(page,encoding='utf-8')
(r/'analysis/previews/koyori-review01/index.html').write_text(page,encoding='utf-8')
# Keep the shared gallery's current-character view consistent with the caster implementation.
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8')
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m[1])
data['koyori']=[dict(tier=1,option=i+1,title='실험 개시 · '+titles[i],image=f'../koyori-caster02/koyori1-{i}.gif',kind='실제 일반 주문 시전 전후 · 다음 시약 자동 순환') for i in range(3)]
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):]
article='<article id="koyori" data-god="koyori"><h2>코요리 <small>마법형 1성 · 검토 대기</small></h2><select onchange="choose(this)">'+''.join(f'<option value="{i}">1성 · 실험 개시 · {titles[i]}</option>' for i in range(3))+'</select><p class="scene-note">실제 일반 주문 시전 전후 · 다음 시약 자동 순환</p><img class="scene" src="../koyori-caster02/koyori1-0.gif"><details open><summary>마법형 개편 효과</summary><p><b>1성 · 실험 개시</b> (자동)<br>발열·냉각·독성 시약을 공격 주문에 자동 주입. 추가 MP/신앙 소모 없음. 캐릭터 병은 다음 시약, 몹의 병은 표식.</p><p><b>3성 · 촉매 반응과 마법 전달</b> (자동)<br>공격 주문 사거리 +1(시야 상한), 다른 시약으로 반응. 피해 ×0.85. 주문당 반응 중심 최대 한 곳.</p><p><b>5성 · 임계 실험</b> (사용)<br>MP6·신앙10·0.5턴. 8턴 또는 강화 주문4회. 두 시약 동시 주입, 열충격+50%/AC무시, 폭발·점액+35%. 사용 시점부터 재사용20턴.</p><p><a href="../koyori-review01/index.html#tier1">1성 세 시약 나란히 보기</a></p></details><label>피드백<textarea data-feedback="koyori"></textarea></label></article>'
s,n=re.subn(r'<article id="koyori".*?</article>',lambda _:article,s,count=1,flags=re.S);assert n==1
s=s.replace("location.hash.slice(1)||'polka'","location.hash.slice(1)||'koyori'")
info=dict(effect='공격 주문에 발열→냉각→독성 자동 주입. 표식6턴, 실제 피해가 있을 때만 순환.',cost='자동 · 원래 주문 MP만 소모 · 추가 신앙 소모 없음',scaling='발열1d(4+I/6), 냉각1d(3+I/9)·이동+15%/2턴, 독성(2+I/12)×2회. 나눗셈 버림.')
s=s.replace('function updateSkillInfo(article,entry){','const koyoriCasterInfo='+json.dumps(info,ensure_ascii=False)+';\nfunction updateSkillInfo(article,entry){')
s=s.replace("article.dataset.god==='lamy'?lamySkillInfo[tier]:null","article.dataset.god==='lamy'?lamySkillInfo[tier]:article.dataset.god==='koyori'?koyoriCasterInfo:null")
p.write_text(s,encoding='utf-8')
p=r/'scripts/god-art-skills.json';d=read(p);d['koyori']=[['실험 개시','자동','공격 주문에 발열·냉각·독성 자동 순환. 추가 MP/신앙 없음. 표식6턴.','다음 시약과 적 표식 병 표시'],['촉매 반응·마법 전달','자동','공격 주문 사거리+1(시야상한). 다른 시약 반응 피해×0.85. 주문당 중심1곳.','별도 시각 검토 대기'],['임계 실험','사용','MP6/신앙10/0.5턴.8턴 또는4회.두 시약 동시 주입·반응 강화.재사용20턴.','별도 시각 검토 대기']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(base/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe')
digest=hashlib.sha256((base/'capture-engine.exe').read_bytes()).hexdigest()
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['koyori'].update(approved=[],pending=[1,3,5],pendingRevision='koyori-caster02',combatRevision='koyori-caster02',tier1Revision='koyori-caster02',visualSourceRevision='koyori-caster02');d.update(currentGod='koyori',next='Review Koyori caster02 tier1 native automatic reagent cycle.',numericChanges=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);d.update(combatRevision='koyori-caster02',visualRevision='koyori-caster02',playBinarySha256=digest,currentVisualReviewGod='koyori',currentVisualReviewTier=1,next='Review Koyori tier1 at analysis/previews/koyori-review01/index.html#tier1',koyoriCasterValidation='analysis/native/koyori-caster02/checkpoint-manifest.json')
    if name=='engine/campaign_status.json':
        d['version']='company-koyori-caster02'
        for f in src.glob('holo-koyori.*'):d.setdefault('sourceSha256',{})[f.name]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
        for key in d.get('sourceSha256',{}):
            if (src/key).is_file():d['sourceSha256'][key]=hashlib.sha256((src/key).read_bytes()).hexdigest().upper()
    if name=='engine/implementation_status.json':d.update(current_module='Koyori caster redesign applied to native campaign; tier1 VFX review.',current_scope='Native spell costs, hit attribution, reagent reactions, range, saved state and current-character previews.')
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 코요리 마법형 실제 적용 / koyori-caster02\n\n1성 자동 시약 순환,3성 사거리+1·반응 피해×0.85,5성 MP6/신앙10/0.5턴·8턴/4회·사용부터20턴 적용. 기존 제조·투척·무기 도포 메뉴 제거. 캐릭터 병=다음 시약,몹 병=표식. 최소 기도술 제한 없음. 일반 직접 주문/광역/파괴의 구슬·제외 판정·면역·자신/아군 안전·저장/RNG·22신·새 프로세스 복원 통과. 승률 검증 아님. 옛 코요리 재고/도포/임계 상태는 첫 로드시 새 스키마 플래그로 초기화하며 native save 포맷 변경 없음. 라미 포함 다른 신 구현/기존 도트 보존. 코요리 1·3·5성 시각 승인 대기,현재 1성부터.\n\n검토: analysis/previews/koyori-review01/index.html#tier1\n검증: analysis/native/koyori-caster02/checkpoint-manifest.json\n원본/프롬프트: assets/holocrawl/koyori-caster01/\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','HOME_SESSION.md','HOME_RESUME.md']:
    p=r/name
    if p.exists():p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
# Reviewable source diff and immutable hashes for the final checkpoint.
diff=[];changed={}
for before in original.rglob('*'):
    if not before.is_file() or before.suffix=='.exe':continue
    rel=before.relative_to(original);after=src/rel
    if after.exists() and after.read_bytes()!=before.read_bytes():
        changed[str(rel)]=hashlib.sha256(after.read_bytes()).hexdigest()
        if before.suffix in ['.cc','.h','.obj','.txt']:
            diff.extend(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
for name in ['holo-koyori.cc','holo-koyori.h']:
    changed[name]=hashlib.sha256((src/name).read_bytes()).hexdigest()
    diff.extend(difflib.unified_diff([], (src/name).read_text().splitlines(True),fromfile='/dev/null',tofile=name))
(base/'source.patch').write_text(''.join(diff),encoding='utf-8')
manifest=dict(status='passed',revision='koyori-caster02',binarySha256=digest,sourceSha256=changed,otherSourceAndOldArtPreserved=True,nativeSaveFormatChanged=False,nativeNormalCasting=True,nativeAreaSpell=True,nativeDelayedOrb=True,poisonImmuneMark=True,friendlyAndSelfSafe=True,globalReagentCycle=True,singleReactionCentrePerCast=True,rangeBonus=1,reactionMultiplier=.85,critical=dict(mp=6,piety=10,activationAut=5,durationAut=80,maxCasts=4,cooldownAut=200),allGods=22,freshProcessKoyoriRestore=True,validation=proof,review='analysis/previews/koyori-review01/index.html#tier1',visualApproved=False)
(base/'checkpoint-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['status','revision','binarySha256','allGods','freshProcessKoyoriRestore','review']},indent=2))
