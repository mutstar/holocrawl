from pathlib import Path
from PIL import Image
import json, shutil, hashlib, difflib

r=Path(__file__).resolve().parents[1];rev='suisei-inherit08';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/inheritance/suisei-inherit.json');reload=read(b/'native/inheritance/inherit-reload.json');v=read(b/'capture-validation.json')
assert proof['status']==reload['status']==v['status']=='passed' and v['gods']==22
assert read(b/'native/suisei-focus.json')['status']=='passed' and read(b/'native/suisei-three.json')['status']=='passed'
out=r/'analysis/previews/suisei-inherit01';out.mkdir(parents=True,exist_ok=True)
names=['before','a1','a2','a3','bank','b2','b3'];frames=[]
for name in names:
    im=Image.open(b/f'native/shots/inherit-{name}.png').convert('RGB').crop((323,260,579,388)).resize((768,384),Image.Resampling.NEAREST)
    im.save(out/f'{name}.png');frames.append(im)
frames[0].save(out/'inheritance.gif',save_all=True,append_images=frames[1:],duration=[700,700,700,1000,1100,1600,1000],loop=0)
frames[4].save(out/'starts-at-two.gif',save_all=True,append_images=frames[5:],duration=[1000,1700,1100],loop=0)
design={'status':'implemented-native-validated','date':'2026-11-02','name':'별의 계승','tier':4,'type':'passive','unlockPiety':100,'minimumInvocations':0,'effect':'Consume the existing next-hit kill reward on a fresh marked foe. If the ordinary direct attack deals positive damage and the foe survives, start at2stars rather than1.','cost':'No additional MP/piety/action/star cost. Original attack/spell cost applies.','constraints':['Miss keeps reward.','One-shot and reward-only kills give no inherited stars or recursive reward.','An already stacked target gains the normal1 only, max3.','Original3-turn reward expiry retained.','Single marked-target rule retained.','Divine powers and DoT/pet damage do not trigger inheritance.'],'save':'Banked reward already uses saved offence/three_end fields; inheritance flag is per-action only. Native bank-save, actual next spell outcomes and strict ordinary-combat RNG continuation verified. Full post-targeting-UI RNG equality is logged separately.','implementationRevision':rev,'review':'analysis/previews/suisei-inherit01/index.html'}
(r/'analysis/design/suisei-inherit01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스이세이 4성 · 별의 계승</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1000px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#b7efff}img{max-width:100%;image-rendering:pixelated}section{background:#1d2b3d;padding:18px;border:1px solid #48617b;border-radius:10px;margin:20px 0}td,th{padding:9px;border:1px solid #48617b}table{border-collapse:collapse}</style><h1>스이세이 4성 · 별의 계승 [패시브]</h1><section><h2>적 A 별1→2→3 → 처치 → 적 B 첫 타격에 별2 → 다음 타격에 별3</h2><img src="inheritance.gif" alt="실제 주문으로 별을 쌓은 오크를 처치하고,다음 고블린을 때리면 바로 별2개로 시작"><p>왼쪽은 플레이어,가운데 적A는 오크,오른쪽 적B는 고블린입니다. 일반 마법의 다트를 실제 시전하며 진행했습니다. 처음 적에게 별을1·2·3개 쌓고 처치합니다. 다음 적에게 적중하면 별1개를 거치지 않고2개가 붙습니다.</p><p>실제 SDL 게임 화면을 잘라 정수배 확대하고 읽기 쉽게 느리게 반복했습니다. 별을 화면에 덧그리지 않았습니다. 검사장에서는 적 행동을 정지하고 HP를 높였으며,첫 적의 마지막 처치 직전에 HP를1로 준비했습니다. 주문 MP·행동 시간·처치 보상·별의 계승·다음 공격은 실제 게임 처리입니다.</p></section><section><h2>계승 부분만 보기</h2><img src="starts-at-two.gif"><p>처치 보상 대기 → 다음 적에게 별2개 → 다음 공격으로 최대3개. 별2개부터2성 집중 관측도 활성화되며,명중 보너스는 이후 명중 판정 공격부터 적용됩니다.</p></section><section><h2>효과·기도술·비용</h2><table><tr><td>해금</td><td>신앙100,최소 기도술 없음</td></tr><tr><td>효과</td><td>기존1성 처치 보상을 다음 새 표적에게 소비한 직접 공격에서 실제 피해를 주고 적이 살아남으면,별을1개 대신2개로 시작</td></tr><tr><td>추가 비용</td><td>MP·신앙·추가 턴 소모 없음. 무기/주문의 원래 비용은 정상 적용</td></tr><tr><td>기도술</td><td>계승 수치는 고정2개. 기존 권능의 기도술 피해식과 별 최대3개는 그대로</td></tr><tr><td>빗나감</td><td>처치 보상 유지,계승 없음</td></tr><tr><td>한 방 처치</td><td>적이 죽었으므로 별 계승 없음. 보상 추가 피해만으로 처치해도 보상 무한 재획득 없음</td></tr><tr><td>이미 별이 있는 적</td><td>보통처럼1개만 추가,최대3개</td></tr><tr><td>유효 시간</td><td>기존 처치 보상3턴 유지. 만료하면 다음 적도 보통1개부터 시작</td></tr></table></section><section><h2>검사 완료</h2><p>실제 외운 주문6회와 원래MP·행동 시간,실제 표적 처치·계승2개·다음 타격3개,빗나감/한 방 처치/보상만으로 처치/만료/신앙99·100/권능 제외,죽은 표적 해제와 보상 재귀 방지 확인. 처치와 다음 공격 사이에 저장한 뒤 새 프로세스에서 같은 주문으로2개 시작·후속 전투 상태 복원과 UI를 분리한 일반 전투 난수 재현 검사를 통과했습니다. 기존1·2·3·5성·22신 회귀 검사도 통과 후 일반 실행본에 반영했습니다.</p></section></html>'''
if not reload.get('fullRngAfterUiCastMatches',False):
    page=page.replace('</html>','<section><h2>검증 범위 메모</h2><p>보상 저장 상태와 난수는 정확히 복원되며,다음 일반 주문의 별·피해·자원·시간·배우 상태도 일치했습니다. 타깃 UI를 분리한 전투 적중 처리도 상태와 난수가 일치합니다. 다만 전체 타깃 선택 UI까지 포함한 재생의 최종 난수는 차이가 남아 있어 별도 점검으로 기록했습니다.</p></section></html>')
    (b/'UI_REPLAY_NOTE.md').write_text('# UI replay diagnostic\n\nThe native banked reward/player/actors/RNG restore exactly. Ordinary combat hit + RNG continuation and actual memorised-spell gameplay outcome/time/resources pass. Full post-targeting-UI RNG equality remains false; this diagnostic is retained in native/inheritance/inherit-reload.json, with expected/actual signatures. No claim of full UI replay determinism is made. Inheritance tests run in a separate process from existing Focus/Three/Su-water regressions.\n',encoding='utf-8')
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime)
sha=hashlib.sha256(runtime.read_bytes()).hexdigest();assert sha==hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review=design['review']
def update(d):
    d.update(currentGod='suisei',currentVisualReviewGod='suisei',currentVisualReviewTier=4,currentVisualReview=review,currentDesignGod='suisei',activeWork='suisei-tier4-inheritance-gif-review',playBinarySha256=sha,suiseiCombatRevision=rev,suiseiInheritance=design,lastArchiveIncludesLatest=False,fullKitCompletedGods=['suisei'])
    if 'review' in d:d['review']=review
    d['next']='Review real native tier4 inheritance GIF: marked enemy kill -> real spell on new foe -> starts2 -> next hit caps3. Suisei1/2/3/4/5 are now implemented/deployed. Await feedback before next god Miko. Vivi/Sopia/Mela combat conversions remain pending.'
    if 'tierApprovals' in d:d['tierApprovals'].setdefault('suisei',{}).update(approved=[1,2,3,4,5],combatRevision=rev,tier4Implemented=True,tier4Review=review)
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        f=r/'engine/campaign-crawl/crawl-ref/source'/key
        if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-fullkit01.json';d=read(p)
d['status']='implemented-native-validated';d['scope']='Suisei1/2/3/4/5 combat/VFX/save integration complete; inheritance GIF awaiting feedback.'
d['tier4Candidate'].update(status='approved-and-implemented',review='Actual normal-spell kill -> next target starts at2, validated/deployed.',revision=rev,unlockPiety=100)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-star3-01.json';d=read(p);d['unapprovedPassiveCandidates']={'focusedObservation':'Implemented: piety50, +3 ordinary accuracy at2+stars.','starInheritance':'Implemented: piety100, banked reward hit on a surviving fresh marked foe starts at2stars.'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\suisei-inherit01\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';s=p.read_text(encoding='utf-8-sig');a=s.index('## 1 스이세이');pos=s.index('### 혜성 낙하 ★★★★★',a)
s=s[:pos]+'''### 별의 계승 ★★★★ — 패시브

- 신앙100 해금, 최소 기도술 없음. 기존1성 처치 보상을 새 표적에게 적중시켜 실제 피해를 주고 적이 살아남으면,해당 적의 별은1개 대신2개로 시작한다.
- 별 최대3개·표적1명·기존 처치 보상3턴 유지. 이미 별이 있는 표적은 보통처럼1개만 증가한다.
- 추가MP·신앙·턴 비용 없음. 빗나감은 보상 유지. 한 방 처치·보상 추가 피해만으로 처치하면 계승 없음,보상 무한 재획득 없음. 일반 무기/직접 주문의 원래 비용은 정상 적용한다.
- 2026-11-02 실제 구현·일반 시전GIF·새프로세스 저장후 다음 공격2중첩 복원 검증 완료.

'''+s[pos:];p.write_text(s,encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
    new=r/'engine/campaign-crawl/crawl-ref/source'/old.name
    patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,runtimeDeployed=True,combatChanged=True,binarySha256=sha,nativeProof=proof,freshRestore=reload,validation=v),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 스이세이4성 별의 계승 실제 적용·실제 주문GIF / 2026-11-02\n\n사용자 승인. 신앙100,처치 보상 소비한 새 표적이 피해 후 생존하면 별1대신2시작. 원래 비용만소모. 실제외운마법의다트로 A별1/2/3→처치→B첫타격2→다음3캡 촬영. 빗나감보존/한방처치제외/보상만처치재귀방지/죽은표적해제/기존중첩+1/신앙99·100/만료/권능제외 검증. 처치와후속주문사이저장후새프로세스정상시전2개 및후속전투상태복원·UI분리전투난수일치·22신·기존1/2/3/5통과. runtime='+rev+' 배포. 스이세이1~5실제완료,4성GIF피드백대기. 다음신은미코이나아직착수안함. 비비/소피아/메라미완료유지. 기존ZIP은새변경미포함. '+review+'\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps({'status':'passed','runtimeRevision':rev,'sha256':sha,'nativeProof':proof,'freshRestore':reload},ensure_ascii=False))
