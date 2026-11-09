from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/okayu-vfx05';src=root/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
assert read(run/'native/okayu-waking.json')['status']=='passed'
raw=run/'native/shots';out=root/'analysis/previews/okayu-vfx05';out.mkdir(exist_ok=True)
stems=list(raw.glob('okayu-tier5-*-frame0.png'));assert len(stems)==1,stems
stem=stems[0].name.removesuffix('-frame0.png')
paths=[raw/(stem+'-frame0.png'),raw/(stem+'-frame1.png'),raw/(stem+'-state.png')]
for name,box,size in [('tier5.gif',(227,196,579,484),(704,576)),('tier5-close.gif',(291,260,435,388),(576,512))]:
 frames=[Image.open(p).convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST) for p in paths]
 frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[300,300,1000],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['okayu'][2].update(image='../okayu-vfx05/tier5.gif',kind='5성 전용 꿈 흡수 소용돌이 · 24→18픽셀로 수축 · 몹 중앙보다6픽셀 위 · 실제 게임 캡처');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='okayu-vfx05',playBinarySha256=digest,currentVisualReviewGod='okayu',currentVisualReviewTier=5,okayuVisualFeedback='Tiers1/3 approved. Tier5 compact dream vortex24→18px instead of sleep motif; foreground,110ms/frame,review pending.',okayuVisualValidation='analysis/native/okayu-vfx05/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['okayu']['pendingRevision']='okayu-vfx05';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 오카유');b=s.index('## 페코라',a);part=re.sub(r'- 5성:.*', '- 5성: okayu-vfx05 검토 중. 기존 거대 수면 도트 대신24→18픽셀 꿈 흡수 소용돌이로 교체. 몹 중앙보다6픽셀 위,전경110ms/프레임. 1·3성/전투 수치 보존.',s[a:b]);p.write_text(s[:a]+part+s[b:],encoding='utf-8')
d=read(run/'art-validation.json');d.update(runtimeSha256=digest,otherSourceAndArtHashesPreserved=True,tests='22 native god controls, Okayu waking bonus and fresh-process restore passed',feedback='pending',artwork='assets/holocrawl/okayu-vfx05/dream-vortex.png',prompt='assets/holocrawl/okayu-vfx05/generation.json');(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text('오카유5성 okayu-vfx05 검토 중: 수면 도트를24→18픽셀 꿈 흡수 소용돌이로 교체. 실제 게임 캡처 미리보기 갱신. 1·3성 승인/okayu-balance03 수치 유지.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published compact tier5 dream vortex and validated runtime.')
