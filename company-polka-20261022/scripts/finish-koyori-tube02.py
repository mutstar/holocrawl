from pathlib import Path
from PIL import Image
import json,hashlib,shutil
r=Path(__file__).resolve().parents[1];rev='koyori-tube02';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
assert read(b/'native/koyori-caster.json')['status']=='passed'
assert read(b/'native/koyori-reload.json')['status']=='passed'
for name,h in read(b/'preserved-files.json').items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==h,name
o=r/'analysis/previews'/rev;o.mkdir(parents=True,exist_ok=True)
for i in range(3):
 frames=[Image.open(b/f'native/shots/koyori1-{i}-{p}.png').convert('RGB').crop((291,252,515,428)).resize((448,352),Image.Resampling.NEAREST) for p in ['before','after','settled']]
 frames[0].save(o/f'koyori1-{i}.gif',save_all=True,append_images=frames[1:],duration=[850,1000,700],loop=0,optimize=False)
p=r/'analysis/previews/koyori-review01/index.html';page=p.read_text(encoding='utf-8').replace('../koyori-tube01/','../koyori-tube02/').replace('옆 병','옆 시험관')
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';p.write_text(p.read_text(encoding='utf-8').replace('../koyori-tube01/','../koyori-tube02/').replace('캐릭터 병','캐릭터 시험관').replace('몹의 병','몹의 시험관'),encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');h=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['koyori'].update(pendingRevision=rev,tier1Revision=rev,visualSourceRevision=rev);d['next']='Review Koyori tier1 slim test tube art.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/n;d=read(p);d.update(visualRevision=rev,playBinarySha256=h);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 코요리 시험관 도트 / koyori-tube02\n\n시험관 길이를 18px에서 14px로 축소. 폭 8px 유지. 주황·하늘·연두 구분 유지. 8×14 도트를 32×32 타일 우상단에 배치. 전투 수치는 koyori-caster02 그대로. 1성 시각 검토 대기.\n\n'
for n in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
m=dict(status='passed',revision=rev,combatRevision='koyori-caster02',gameplayAndOtherArtPreserved=True,binarySha256=h,validation=v,visualApproved=False,iconSize=[8,14],tilePosition=[21,0])
(b/'checkpoint-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8');print(json.dumps(m))
