from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/noel-vfx02'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/noel-balance.json','native/pekora-balance.json','native/okayu-waking.json']:assert read(run/n)['status']=='passed',n
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/noel-vfx02';out.mkdir(exist_ok=True)
frames=[Image.open(raw/f'noel-menu1-frame{f}.png').convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for f in [0,1]]
frames[0].save(out/'tier1.gif',save_all=True,append_images=frames[1:],duration=[500,500],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['noel'][0].update(image='../noel-vfx02/tier1.gif',kind='노엘 전용 은빛 방패·메이스 문양 · 14/16픽셀 · 비마법 전투 스킬 +6 · 오카와루보다 지속5턴 추가');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):]
m=re.search(r'const noelSkillInfo=(.*?);\n',s);d=json.loads(m.group(1));d['1'].update(effect='전투(Fighting), 모든 무기·맨손·투척·갑옷·회피·은밀·방패 등 비마법 전투 스킬의 유효 레벨을 +6 올립니다. 오카와루의 +5보다1 높습니다. 마법 스킬과 실제 훈련 레벨은 바뀌지 않으며, 유효 레벨은 최대27입니다. 전투 스킬 보너스는 공격 계산에 적용되고 최대HP는 늘리지 않습니다.',scaling='증가량은 기도술과 무관하게 +6입니다. 지속은 오카와루와 같은 기도술 기반 난수 계산에5턴 추가: 시전 시점부터15 + random2avg(기도술 × 6, 2)턴, 최대110턴. random2avg는 두 번 뽑은 난수의 평균입니다. 기도술12에서 평균 약50턴(시전1턴 포함), 오카와루는 약45턴입니다. 자발적으로 광폭화하면 효과가 끝나고 신앙10을 잃습니다.');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];s=s.replace('전투·현재 무기/맨손·갑옷·방패 유효 스킬 증가','모든 비마법 전투 스킬 유효 레벨 +6 · 오카와루보다 지속5턴 추가');p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='noel-vfx02',combatRevision='noel-balance01',playBinarySha256=digest,noelVisualFeedback='Tier1 silver shield/mace crest14/16px; +6 mundane skills; Heroism duration+5 turns. Review pending.',noelCombatValidation='analysis/native/noel-vfx02/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d.update(combatRevision='noel-balance01',numericChanges=True);d['tierApprovals']['noel']['pendingRevision']='noel-vfx02';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
changed=['holo-campaign.cc','holo-campaign-test.cc']+[f'rltiles/holo/fx_night_noel1_{i}.png' for i in range(2)]
patch=[]
for n in changed:
 p=run/'source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
 if n.endswith('.cc'):patch.extend(difflib.unified_diff((run/'before'/n).read_text(encoding='utf-8').splitlines(True),(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(''.join(patch),encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='noel-vfx02',combatRevision='noel-balance01',runtimeSha256=digest,changedHashes={n:sha(src/n) for n in changed},otherSourceAndArtPreserved=True,saveFormatChanged=False,bonus=6,duration='min(110,15+random2avg(6*I,2)) turns from cast start',nativeIconSizes=[14,16],generation='assets/holocrawl/noel-vfx02/generation.json',validation='native/noel-balance.json',regression='native/validation.json',restore='native/reload.json',feedback='pending',scope='Native mechanics/save tests; not full campaign winrate'),indent=2),encoding='utf-8')
note='노엘1성 noel-vfx02/noel-balance01 검토 중: 비마법 전투 스킬 전체 유효+6(전투는 공격만,HP증가 없음),지속은오카와루식난수+5턴/최대110턴. MP2·신앙2·시전1턴 유지. 은빛방패/메이스14·16픽셀 전용도트. 22신/저장/기존오카유·페코라 기능검사 통과. 프롬프트 assets/holocrawl/noel-vfx02/generation.json.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'BALANCE_WORKPLAN.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n'+note,encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 노엘');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 1성:','- 1성: 사용자 요청 보강 구현(noel-vfx02): 비마법 전투 스킬전체+6/오카와루식 지속+5턴/은빛방패·메이스14·16픽셀. 검토 대기. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published Noel skill buff and native silver-knight crest.')
