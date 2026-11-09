from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/korone-vfx06';src=root/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
for name in ['validation.json','reload.json']:assert read(run/'native'/name)['status']=='passed'
raw=run/'native/shots';out=root/'analysis/previews/korone-vfx06';out.mkdir(exist_ok=True)
stems=sorted(raw.glob('korone-tier5-*-frame0.png'));assert len(stems)==1,stems
stem=stems[0].name.removesuffix('-frame0.png')
paths=[raw/(stem+'-frame0.png'),raw/(stem+'-frame1.png'),raw/(stem+'-state.png')]
for name,box,size in [('tier5.gif',(227,196,579,484),(704,576)),('tier5-close.gif',(291,260,435,388),(576,512))]:
    frames=[Image.open(p).convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST) for p in paths]
    frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[350,350,1000],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m.group(1))
data['korone'][2].update(image='../korone-vfx06/tier5.gif',kind='3성과 같은 강아지 발바닥 · 32→38픽셀로 짧게 강조 · 기존보다 약 74% 축소 · 느린 검토 재생')
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();assert digest==read(run/'capture-validation.json')['binarySha256'];shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;d=read(p);d.update(visualRevision='korone-vfx06',playBinarySha256=digest,currentVisualReviewGod='korone',currentVisualReviewTier=5,koroneVisualFeedback='Tiers 1 and 3 approved. Tier5 reuses approved dog paw, 32/38px (was116/148), foreground,110ms/frame; awaiting feedback.',koroneVisualValidation='analysis/native/korone-vfx06/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 코로네');b=s.index('## 오카유',a);part=s[a:b].replace('- 5성:','- 5성: korone-vfx06 검토 대기. 요청: 3성 멍멍이 발바닥 재사용·크기 축소. 승인된 원화를 그대로32/38픽셀로 배치 (기존116/148), 전경110ms. 다른 도트·전투 코드는 보존. 실제 SDL 캡처/저장 검사 통과.',1);p.write_text(s[:a]+part+s[b:],encoding='utf-8')
d=read(run/'art-validation.json');d.update(runtimeSha256=digest,otherSourceAndArtHashesPreserved=True,tests='22-god native controls and fresh-process restore passed',feedback='pending',review='analysis/previews/all-gods-vfx-draft04/index.html#korone');(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'CURRENT_WORKSPACE.md';p.write_text('현재 코로네5성 korone-vfx06 검토: 승인된3성 발바닥 원화를 재사용,32/38픽셀로 약74% 축소. 전경110ms. 1·3성 승인 유지,5성 피드백 대기.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published native tier5 paw and tested runtime; approved tiers1/3 and combat source hashes preserved.')
