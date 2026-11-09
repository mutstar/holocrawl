from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/towa-vfx02'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/towa-vfx02';out.mkdir(exist_ok=True)
files=list(raw.glob('towa-passive*.png'));assert len(files)==1,files
Image.open(files[0]).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST).save(out/'tier1.png')
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['towa'][0].update(image='../towa-vfx02/tier1.png',kind='1성 전용 악마의 눈 · 흰 눈+연두 눈동자·보라 테두리 · 최대14×10픽셀 · 가호 상태 표시');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];s=s.replace('적과 거리를 벌리고 쏠 때 유리한 가호입니다.','투창·부메랑·돌·다트·투척 그물 등 투척도 명중 보너스를 받습니다. 직접 물리 피해가 있는 투척에는 피해 +10%도 적용되지만, 다트의 독·마비·수면 효과 강도나 지속 시간, 그물의 구속 효과는 강화하지 않습니다. 적과 거리를 벌리고 쏠 때 유리한 가호입니다.');p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='towa-vfx02',playBinarySha256=digest,towaVisualFeedback='Tier1 clear devil eye: pale sclera, lime iris, purple outline, fit14x10px. Throwing accuracy applies to darts; no dart effect duration/damage boost. Other art/combat preserved. Pending review.',towaVisualValidation='analysis/native/towa-vfx02/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['towa']['pendingRevision']='towa-vfx02';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='towa-vfx02',runtimeSha256=digest,changed=[f'rltiles/holo/fx_night_towa1_{i}.png' for i in range(2)],allCombatSourcesAndOtherArtPreserved=True,numericChanges=False,saveFormatChanged=False,nativeFit=[14,10],framesIdentical=True,position=[25,7],prompt='assets/holocrawl/towa-vfx02/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='토와1성 towa-vfx02 검토: 악마의눈 가시성 보강: 흰눈/연두눈동자/보라테두리 최대14x10픽셀,두프레임동일,우측상단. 투창/다트 등 투척 명중 적용,다트 상태효과는 불강화 설명 추가. 3/5성·전투수치·모든소스/다른도트 보존. #towa 미리보기 갱신.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 토와');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 1성:','- 1성: towa-vfx02 흰눈·연두눈동자·보라테두리 악마의눈으로 가시성 보강,현재검토중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published clear devil eye; throwing clarification added; combat and other art preserved.')
