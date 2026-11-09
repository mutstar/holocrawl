from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/towa-vfx04'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/towa-vfx04';out.mkdir(exist_ok=True)
fs=list(raw.glob('towa-tier3-option0-*-frame0.png'));assert len(fs)==1;stem=fs[0].name.removesuffix('-frame0.png')
frames=[Image.open(raw/(stem+f'-frame{f}.png')).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for f in [0,1]]
frames[0].save(out/'tier3.gif',save_all=True,append_images=frames[1:],duration=[500,500],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['towa'][1].update(image='../towa-vfx04/tier3.gif',kind='3성 엄호사격 설치 이펙트 · 승인한 자주색·연보라·연두 팔레트 적용 · 실제 시전2프레임,지원사격 발사 장면은 미포함');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):]
s=s.replace('지금은 토와 1성을 확인합니다.','지금은 토와 3성을 확인합니다.').replace('토와 <small>1성 확인 중</small>','토와 <small>1성 승인 · 3성 확인 중</small>').replace("if(active.id==='watame')sel.value='2';choose(sel);","if(active.id==='watame')sel.value='2';if(active.id==='towa')sel.value='1';choose(sel);").replace('지정 구역의 적을 사격하면 추가 지원사격','지정 구역의 적이 이동하거나 플레이어를 공격하면 지원사격')
info={'cost':'MP 4 · 신앙 4 · 시전1턴 · 중심 지정 사거리5칸 · 고정5×5 구역 · 구역 유지 중 재설치 불가','effect':'구역 안의 눈에 보이는 적이 이동하거나 플레이어에게 공격을 시도하면 추가 지원사격을 합니다. 구역 중심과 적 사이에 시야가 통해야 합니다. 일반1턴당 최대1발,구역당 총4발이며 빗나가도1발을 소모합니다. 직접 사격을 해야만 발동하는 효과는 아닙니다. 지원사격이 명중하면 적의 다음 이동을 방해합니다.','scaling':'시전 후 지속: 6 + 기도술 × 0.2턴. 기도술12면8.4턴입니다. 지원사격 피해: 2d(5 + ⌊기도술/3⌋),기도술12면2d9로 기본2~18 피해이며 방어구를 적용합니다. 별도 명중 판정 수치는22 + 기도술입니다. 명중하면 최대2턴 동안 다음 이동에 걸리는 시간이50% 늘어나며,한 번 이동하면 풀립니다.4발을 다 써도 구역이 끝날 때까지 기다려야 다시 설치할 수 있습니다.'}
s=s.replace('function updateSkillInfo(article,entry){','towaSkillInfo[3]='+json.dumps(info,ensure_ascii=False)+';\nfunction updateSkillInfo(article,entry){');p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='towa-vfx04',playBinarySha256=digest,currentVisualReviewTier=3,towaVisualFeedback='Tier1 approved. Tier3 covering fire cast in approved magenta/lavender/lime palette; description corrected to movement/attack trigger. Review pending.',towaVisualValidation='analysis/native/towa-vfx04/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['towa']['pendingRevision']='towa-vfx04';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='towa-vfx04',runtimeSha256=digest,changed=[f'rltiles/holo/fx_night_towa3_{i}.png' for i in range(2)],allCombatSourcesAndOtherArtPreserved=True,numericChanges=False,prompt='assets/holocrawl/towa-vfx04/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='토와1성 승인(towa-vfx03),3성 엄호사격 검토중(towa-vfx04). 향후 팔레트는 밝은자주색·연보라+연두포인트로 확정.3성 시전도트도 해당팔레트 반영. 실제엄호사격은 구역안 적의 이동/공격시 발동,총4발/턴당1발. 전투수치 보존.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 토와');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 3성:','- 3성: towa-vfx04 승인팔레트 적용 시전GIF/실제 지원사격 조건·수치 표시,검토중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published Towa3 bright palette preview and verified ability details.')
