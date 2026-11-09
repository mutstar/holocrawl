from pathlib import Path
import hashlib,json,shutil,re,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/okayu-balance03'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['capture-validation.json','native/validation.json','native/reload.json','native/okayu-waking.json']:
    assert read(run/name)['status']=='passed',name
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
names=[p.name for p in (run/'before').glob('*') if p.suffix in ['.h','.cc']]
patch=[];snap=run/'source_snapshot';snap.mkdir(exist_ok=True)
for name in names:
    p=src/name;shutil.copy2(p,snap/name)
    assert p.read_bytes()==(root/'engine/tiles-crawl/crawl-ref/source'/name).read_bytes(),name
    patch+=difflib.unified_diff((run/'before'/name).read_text(encoding='utf-8').splitlines(True),p.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+name,tofile='after/'+name)
(run/'source.patch').write_text(''.join(patch),encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();assert digest==read(run/'capture-validation.json')['binarySha256'];shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
old='이 권능 자체는 직접 피해를 주지 않습니다.'
new='시전 자체는 직접 피해를 주지 않습니다. 이 권능으로 재운 적을 깨우는 첫 직접 공격은 피해가30% 증가합니다. 평타·사격·공격 주문에 한 번만 적용되며, 추가 피해 상한은 8 + ⌊기도술/3⌋입니다. 소환수·독·구름·권능에는 적용되지 않고,5성의 기존 수면 보너스와 중복되지 않습니다.'
assert old in s;s=s.replace(old,new,1)
s=s.replace('수면은 최대2턴이며, 정신 면역·수면 불가 대상은 잠들지 않습니다.','수면은 최대2턴이며, 정신 면역·수면 불가 대상은 잠들지 않습니다. 첫 타격 추가 피해는 최소1·상한8+⌊기도술/3⌋. 기도술12라면 피해20→26,피해100→112입니다.',1)
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m.group(1));data['okayu'][1]['kind']='3성 보강: 수면 후 첫 직접 타격 +30% (추가 피해 상한 있음) · 표시 중인 GIF는 시전 도트'
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;d=read(p);d.update(combatRevision='okayu-balance03',playBinarySha256=digest,currentVisualReviewGod='okayu',currentVisualReviewTier=3,okayuCombatFeedback='3* waking hit implemented: first ordinary direct positive hit on own nap sleep +30%,minimum1,cap8+I/3. No divine/5* double stack. Save format unchanged.',okayuCombatValidation='analysis/native/okayu-balance03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['numericChanges']=True;d['combatRevision']='okayu-balance03';d['next']='Continue Okayu tier3 visual feedback, then tier5';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='오카유3성 보강(okayu-balance03): 자신의 낮잠 표식으로 재운 적을 깨우는 첫 직접 타격 +30%,최소+1·추가 피해 상한8+floor(I/3). 기도술12에서20→26,100→112. 평타/사격/공격주문만,독·구름·소환수·신 권능 제외. 5성 기존 수면+30%와 중복 없음. 피해가 완전히 막히면 미소모,기존 암습/피해배율 계산 후 상한 적용. 기도술/MP/신앙/만복 비용과 수면 확률·지속은 유지. 새 저장필드 없이 기존kind/root 상태 사용,레거시 수면 저장·소모 전후 태그 재로드·일반 새 프로세스 재로드 검증. 다른 신 전투 소스 및 모든 도트 해시 보존. 검증은 고정 전투장 기능 검사이며 전체 승률 향상 입증은 아니다.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
    p=root/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=root/'BALANCE_WORKPLAN.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n## 2026-10-21 오카유 3성 단독 보상 구현\n\n'+note,encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 오카유');b=s.index('## 페코라',a);part=s[a:b].replace('- 3성:','- 3성: 5성 전 메리트 부족 피드백에 따라 수면 후 첫 직접 타격 +30%(상한8+I/3) 구현,okayu-balance03. 전용 기능/저장/22신 검사 통과. 시전 도트는 현재 초안 검토 중.',1);p.write_text(s[:a]+part+s[b:],encoding='utf-8')
d=dict(status='passed',revision='okayu-balance03',runtimeSha256=digest,changedSourceSha256={n:sha(src/n) for n in names},artHashesPreserved=True,otherSourceHashesPreserved=True,saveFormatChanged=False,proof='native/okayu-waking.json',regression='native/validation.json',freshRestore='native/reload.json',scope='Native function/arena controls, not campaign winrate validation',wakingBonusPercent=30,wakingBonusMinimum=1,wakingBonusCap='8+floor(Invocations/3)',review='analysis/previews/all-gods-vfx-draft04/index.html#okayu')
(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Okayu waking hit deployed; native cases,22-god regression and save controls passed. All art preserved.')
