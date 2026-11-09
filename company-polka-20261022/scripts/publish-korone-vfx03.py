from pathlib import Path
from PIL import Image
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/korone-vfx03';src=root/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
for name in ['validation.json','reload.json']:
    assert read(run/'native'/name)['status']=='passed'
raw=run/'native/shots';out=root/'analysis/previews/korone-vfx03';out.mkdir(exist_ok=True)
stems=sorted(raw.glob('korone-tier3-*-frame0.png'));assert len(stems)==1,stems
stem=stems[0].name.removesuffix('-frame0.png')
paths=[raw/(stem+'-frame0.png'),raw/(stem+'-frame1.png'),raw/(stem+'-state.png')]
for name,box,size in [('tier3.gif',(227,196,579,484),(704,576)),('tier3-close.gif',(323,260,467,388),(576,512))]:
    frames=[Image.open(p).convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST) for p in paths]
    frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[350,350,1000],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
assert '../korone-vfx02/tier3.gif' in s
s=s.replace('../korone-vfx02/tier3.gif','../korone-vfx03/tier3.gif')
import re
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m.group(1));data['korone'][1]['kind']='몬스터 앞에 표시하는 주먹·타격점 · 위로 8픽셀 · 실제 게임 110ms/프레임 (검토 GIF는 느리게 반복)'
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();assert digest==read(run/'capture-validation.json')['binarySha256'];shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;d=read(p);d.update(visualRevision='korone-vfx03',playBinarySha256=digest,currentVisualReviewGod='korone',currentVisualReviewTier=3,koroneVisualFeedback='Tier 1 approved. Tier 3 compact high-contrast punch raised 8px, 110ms/frame; awaiting feedback.',koroneVisualValidation='analysis/native/korone-vfx03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 코로네');b=s.index('## 오카유',a);s=s[:a]+s[a:b].replace('- 3성:','- 3성: 가시성 개선 요청 → korone-vfx03. 큰 원형 궤적을 작은 고대비 주먹·타격점으로 교체, 표시 8픽셀 위, 게임 프레임 55→110ms. 미승인, 사용자 검토 대기.',1)+s[b:];p.write_text(s,encoding='utf-8')
d=read(run/'art-validation.json');d.update(runtimeSha256=digest,otherSourceAndArtHashesPreserved=True,tests='22-god native controls and fresh-process restore passed',feedback='pending',prompt='assets/holocrawl/korone-vfx02/generation.json',review='analysis/previews/all-gods-vfx-draft04/index.html#korone');(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Published actual SDL Korone tier3 capture and tested binary; combat values unchanged.')
