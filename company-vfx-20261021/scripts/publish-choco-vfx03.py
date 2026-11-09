from pathlib import Path
from PIL import Image
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/choco-vfx03'
src=root/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for name in ['validation.json','reload.json','choco-review.json']:
    assert read(run/'native'/name)['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
raw=run/'native/shots';out=root/'analysis/previews/choco-vfx03';out.mkdir(exist_ok=True)
paths=[raw/'choco-corner-upper.png',*[raw/f'choco-kiss-1-frame{f}.png' for f in range(4)],raw/'choco-kiss-after.png']
for name,box,size in [('tier3.gif',(227,196,579,484),(704,576)),('tier3-close.gif',(323,275,467,387),(576,448))]:
    frames=[Image.open(p).convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST) for p in paths]
    frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[650,300,300,450,500,1000],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
assert 'clips/choco-kiss.gif' in s
s=s.replace('clips/choco-kiss.gif','../choco-vfx03/tier3.gif').replace('실제 HP 회복이 있을 때만 귀환 하트','채운 귀환 하트 · 10→14픽셀 · 5픽셀 위 · 실제 HP 회복 시에만 표시')
p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();assert digest==read(run/'capture-validation.json')['binarySha256']
shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;d=read(p);d.update(visualRevision='choco-vfx03',playBinarySha256=digest,currentVisualReviewGod='choco',currentVisualReviewTier=3,chocoVisualFeedback='Tier 1 approved. Tier 3 return heart uses approved solid art, 14px, raised 5px, 170ms per return frame; awaiting feedback.',chocoVisualValidation='analysis/native/choco-vfx03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');s=s.replace('개선 검토 중, 미승인.','choco-vfx03: 승인된 채운 하트 원화를 재사용, 10→14픽셀 확대·5픽셀 위·귀환 프레임 110→170ms. 실제 SDL 캡처 갱신, 피드백 대기.');p.write_text(s,encoding='utf-8')
d=read(run/'art-validation.json');d.update(runtimeSha256=digest,tests='22-god native controls, Choco actual-heal/full-HP/charm controls, fresh-process restore passed',feedback='pending',changedSourceSha256={n:sha(src/n) for n in d['changed']},review='analysis/previews/all-gods-vfx-draft04/index.html#choco');(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Published native Choco tier 3 GIF and tested runtime; unchanged source and other assets verified.')
