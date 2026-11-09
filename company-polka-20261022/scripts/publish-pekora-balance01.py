from pathlib import Path
import hashlib,json,shutil,re,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/pekora-balance01';native=run/'native-retry06';binary=root/'analysis/native/pekora-balance01-final/capture-engine.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['validation.json','reload.json','pekora-balance.json','okayu-waking.json']:assert read(native/name)['status']=='passed',name
for rel,d in read(run/'preserved-files.json').items():assert sha(src/rel)==d,rel
shutil.copy2(run/'capture-engine.exe',run/'capture-engine-attempt01.exe');shutil.copy2(binary,run/'capture-engine.exe');shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe');digest=sha(binary).upper()
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
s=s.replace('MP 2 · 신앙 1 · 설치 1턴','MP 2 · 신앙 1 · 설치 0.5턴')
s=s.replace('즉시 기폭: 선택한 당근들을 바로 터뜨립니다. 지연 기폭: 선택한 당근들이 시전 시점부터2.5턴 뒤 터지도록 예약합니다.','즉시 기폭: 선택한 당근들을 피해 +30%로 바로 터뜨립니다. 지연 기폭: 시전 시점부터2.5턴 뒤 피해 +50%로 터지도록 예약합니다.')
s=s.replace('폭발 피해는1성과 동일한 2d(8 + ⌊기도술/3⌋)입니다. 기도술12면 기본2~24 피해를 화염·파편으로 나눠 적용합니다.','기본 폭발 피해 2d(8 + ⌊기도술/3⌋)에 즉시 ×1.3 / 지연 ×1.5를 한 번 적용하고 소수점은 버립니다. 기본 피해20이면 즉시26 / 지연30입니다. 강화 후 화염·파편으로 나눠 저항·방어구를 적용합니다. 연쇄된 당근에도 같은 강화가 전파되며 계속 곱해지지 않습니다. 서로 다른 강화가 연결되면 더 높은 배율 하나만 씁니다.')
s=s.replace('3성 · 도화선 조작 · 선택0','3성 · 즉시 기폭 (+30%)').replace('3성 · 도화선 조작 · 선택1','3성 · 지연 기폭 (+50%)')
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m.group(1));data['pekora'][4]['kind']='즉시 기폭 피해 +30% · 연결된 당근도 같은 강화 · 폭발 도트는 공용 이펙트 유지';data['pekora'][5]['kind']='2.5턴 뒤 지연 기폭 피해 +50% · 연쇄 배율은 한 번만 적용 · 폭발 도트는 공용 이펙트 유지';s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):]
p.write_text(s,encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(combatRevision='pekora-balance01',playBinarySha256=digest,pekoraCombatFeedback='Plant5aut, immediate130%,delayed150%,chain max multiplier once; saved in existing hazard.extra,legacy delayed supported.',pekoraCombatValidation='analysis/native/pekora-balance01/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d.update(numericChanges=True,combatRevision='pekora-balance01');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
changed=['holo-batch-space.cc','holo-campaign-test.cc']
patch=[]
for n in changed:
 out=run/'source_snapshot'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,out)
 patch.extend(difflib.unified_diff((run/'before'/n).read_text(encoding='utf-8').splitlines(True),(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(''.join(patch),encoding='utf-8')
d=dict(status='passed',revision='pekora-balance01',runtimeSha256=digest,plantAut=5,immediateMultiplier=130,delayedMultiplier=150,chain='maximum multiplier once, independent of vector order',numericChanges=True,saveFormatChanged=False,artHashesPreserved=True,otherSourceHashesPreserved=True,sourceHashes={n:sha(src/n) for n in changed},validation='native-retry06/pekora-balance.json',regression='native-retry06/validation.json',restore='native-retry06/reload.json',scope='Native ability damage/save controls; not campaign winrate validation');(run/'checkpoint-manifest.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
note='페코라1·3성 보강(pekora-balance01): 당근 설치0.5턴. 즉시 기폭 피해×1.3,지연 기폭×1.5(소수점 버림,화염/파편 분할 전). 연쇄는 가장 높은 배율 한 번만 적용,폭탄 순서 무관. 비용·무장 시간·폭발 범위·5성 자체 피해 유지. 강화 상태는 기존hazard.extra에 저장,저장 형식 유지. 실제 피해/지연 저장/22신 검사 통과. 미리보기 설명 갱신.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'BALANCE_WORKPLAN.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n'+note,encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 페코라');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 3성:','- 3성: 사용자 승인 보강안 구현(pekora-balance01). 설치0.5턴/즉시+30%/지연+50%/연쇄강화1회. 기능검사 통과. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Pekora combat changes deployed and browser details updated.')
