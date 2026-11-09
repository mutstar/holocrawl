from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/noel-vfx03'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/noel-vfx03';out.mkdir(exist_ok=True)
frames=[Image.open(raw/f'noel-menu1-frame{f}.png').convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for f in [0,1]]
frames[0].save(out/'tier1.gif',save_all=True,append_images=frames[1:],duration=[500,500],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['noel'][0].update(image='../noel-vfx03/tier1.gif',kind='노엘 전용 은빛 방패와 반짝임 · 메이스 문양 제거 · 14/16픽셀 · 크기·위치·전투 수치 유지');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='noel-vfx03',playBinarySha256=digest,noelVisualFeedback='Tier1 clean silver shield plus sparkle only, mace removed;14/16px same location. Combat noel-balance01 preserved. Pending review.',noelVisualValidation='analysis/native/noel-vfx03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['noel']['pendingRevision']='noel-vfx03';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='noel-vfx03',runtimeSha256=digest,changed=[f'rltiles/holo/fx_night_noel1_{i}.png' for i in range(2)],allCombatSourcesAndOtherArtPreserved=True,numericChanges=False,saveFormatChanged=False,nativeSizes=[14,16],position=[24,8],prompt='assets/holocrawl/noel-vfx03/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='노엘1성 noel-vfx03 검토: 메이스를 제거하고 은빛 방패·반짝임만 남김. 크기14/16픽셀·위치유지. noel-balance01 전투수치와 모든 소스/다른도트 해시보존. 통합 #noel 갱신.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 노엘');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 1성:','- 1성: noel-vfx03 메이스 제거/은빛방패와 반짝임만 유지,현재 검토 중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published clean silver shield; other sources/art and combat stats preserved.')
