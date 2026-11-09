from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/noel-vfx05'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native-layer/shots';out=root/'analysis/previews/noel-vfx05';out.mkdir(exist_ok=True)
files=['noel-tier5-option0-50-frame0.png','noel-tier5-option0-50-frame1.png','noel-tier5-option0-50-state.png']
frames=[Image.open(raw/n).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for n in files]
frames[0].save(out/'tier5.gif',save_all=True,append_images=frames[1:],duration=[400,400,900],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['noel'][1].update(image='../noel-vfx05/tier5.gif',kind='5성 전용 은빛 날개·작은 기사관 · 중앙은 비워 캐릭터 보존 · 시전 후에도 버프가 유지되는 동안 캐릭터를 따라갑니다');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=root/'analysis/native/noel-vfx05-layer/capture-engine.exe';shutil.copy2(run/'capture-engine.exe',run/'capture-engine-before-layer.exe');shutil.copy2(binary,run/'capture-engine.exe');digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='noel-vfx05',playBinarySha256=digest,noelVisualFeedback='Tiers1/3 approved. Tier5 silver wing/crown regalia64/68px,open centre,persistent during actual saved commander buff; pending review.',noelVisualValidation='analysis/native/noel-vfx05/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['noel']['pendingRevision']='noel-vfx05';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''.join(difflib.unified_diff((run/'before/holo-visual.cc').read_text(encoding='utf-8').splitlines(True),(src/'holo-visual.cc').read_text(encoding='utf-8').splitlines(True),fromfile='before/holo-visual.cc',tofile='after/holo-visual.cc'));patch+=''.join(difflib.unified_diff((run/'before/tilereg-dgn.cc').read_text(encoding='utf-8').splitlines(True),(src/'tilereg-dgn.cc').read_text(encoding='utf-8').splitlines(True),fromfile='before/tilereg-dgn.cc',tofile='after/tilereg-dgn.cc'));(run/'source.patch').write_text(patch,encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='noel-vfx05',runtimeSha256=digest,changed=['holo-visual.cc','tilereg-dgn.cc']+[f'rltiles/holo/fx_night_noel5_{i}.png' for i in range(2)],otherSourceAndArtPreserved=True,numericChanges=False,saveFormatChanged=False,nativeWidths=[64,68],centre=[80,74],persistent='Query actual noel_commander buff, follow player, foreground with transparent centre, no new state',prompt='assets/holocrawl/noel-vfx05/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='노엘5성 noel-vfx05 검토: 3성 방패틀과 구분되는 양옆 은빛날개+머리위 작은 기사관.64/68픽셀,중앙비움,캐릭터앞 레이어(중앙 투명). 실제5성 버프동안 플레이어를 따라다니고 종료시 제거. 1성12/14픽셀 은빛방패/3성 보급/전투수치 보존.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 노엘');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 5성:','- 5성: noel-vfx05 은빛날개·기사관으로 교체,중앙비움,실제5성 버프동안 유지. 현재 검토 중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published distinct persistent silver wings/crown for Noel5; combat and other art preserved.')
