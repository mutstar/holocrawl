from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/watame-vfx03'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/watame-vfx03';out.mkdir(exist_ok=True)
fs=list(raw.glob('watame-tier5-option0-*-frame0.png'));assert len(fs)==1,fs;stem=fs[0].name.removesuffix('-frame0.png')
files=[stem+'-frame0.png',stem+'-frame1.png',stem+'-state.png'];frames=[Image.open(raw/n).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for n in files]
frames[0].save(out/'tier5.gif',save_all=True,append_images=frames[1:],duration=[400,400,900],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['watame'][2].update(image='../watame-vfx03/tier5.gif',kind='5성 전용 금빛 음표+발밑 양털 받침 · 3성 양털 고리와 구분 · 버프 동안 캐릭터를 따라갑니다 · 치명상 생존 장면은 별도');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='watame-vfx03',playBinarySha256=digest,watameVisualFeedback='Tiers1/3 approved. Tier5 distinct gold musical notes above head and wool cushion beneath feet; open centre, persistent for saved buff, foreground. Pending review.',watameVisualValidation='analysis/native/watame-vfx03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['watame']['pendingRevision']='watame-vfx03';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for n in ['holo-visual.cc','tilereg-dgn.cc']:patch+=''.join(difflib.unified_diff((run/'before'/n).read_text(encoding='utf-8').splitlines(True),(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='watame-vfx03',runtimeSha256=digest,changed=['holo-visual.cc','tilereg-dgn.cc']+[f'rltiles/holo/fx_night_watame5_{i}.png' for i in range(2)],otherSourceAndArtPreserved=True,numericChanges=False,saveFormatChanged=False,notesWidths=[46,50],woolWidths=[30,34],notesEndY=64,woolStartY=96,persistent='Query saved Watame five_end,follow player,foreground with empty actor centre',prompt='assets/holocrawl/watame-vfx03/generation.json',feedback='pending',validation='capture-validation.json'),indent=2),encoding='utf-8')
note='와타메5성 watame-vfx03 검토: 3성과 같은 양털고리 대신 머리위 금빛음표3개+발밑 작은 양털받침. 가운데캐릭터공간비움. 실제5성 지속중 따라다님,전경표시. 1성12픽셀양털/3성방벽/전투수치 보존.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 와타메');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 5성:','- 5성: watame-vfx03 금빛음표+발밑양털받침으로 교체,5성지속중 유지. 현재검토중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published Watame5 song notes and wool cushion; numeric balance unchanged.')
