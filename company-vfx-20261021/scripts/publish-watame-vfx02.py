from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/watame-vfx02'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/watame-vfx02';out.mkdir(exist_ok=True)
files=list(raw.glob('watame-passive*.png'));assert len(files)==1,files
Image.open(files[0]).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST).save(out/'tier1.png')
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['watame'][0].update(image='../watame-vfx02/tier1.png',kind='1성 전용 흰 양털 뭉치+금빛 반짝임 · 12픽셀 · 실제 추가재생 가호 상태 표시');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='watame-vfx02',playBinarySha256=digest,watameVisualFeedback='Tier1 filled white wool puff and one gold sparkle12px replaces tiny complex ring. Other tiers and combat unchanged. Pending review.',watameVisualValidation='analysis/native/watame-vfx02/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['watame']['pendingRevision']='watame-vfx02';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='watame-vfx02',runtimeSha256=digest,changed=[f'rltiles/holo/fx_night_watame1_{i}.png' for i in range(2)],allCombatSourcesAndOtherArtPreserved=True,numericChanges=False,saveFormatChanged=False,nativeSize=12,framesIdentical=True,position=[26,7],prompt='assets/holocrawl/watame-vfx02/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='와타메1성 watame-vfx02 검토: 복잡한 양털/뿔/음표 고리를 통통한 흰양털+금빛반짝임 하나로 단순화.12픽셀,두프레임동일,기존우측상단위치 유지. 3/5성·전투수치·모든소스/다른도트 보존. #watame 미리보기 갱신.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 와타메');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 1성:','- 1성: watame-vfx02 흰양털뭉치+작은금빛반짝임12픽셀로 단순화,현재검토중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published12px white wool puff; combat and other art preserved.')
