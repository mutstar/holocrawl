from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/okayu-vfx03';src=root/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(run/'capture-validation.json')['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
for name in ['validation.json','reload.json']:assert read(run/'native'/name)['status']=='passed'
raw=run/'native/shots';out=root/'analysis/previews/okayu-vfx03';out.mkdir(exist_ok=True)
p=raw/'okayu-passive1.png';assert p.is_file();im=Image.open(p).convert('RGB')
im.crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST).save(out/'tier1.png')
im.crop((339,292,435,372)).resize((576,480),Image.Resampling.NEAREST).save(out/'tier1-close.png')
tile=Image.open(src/'rltiles/holo/fx_night_okayu1_0.png');tile.resize((256,256),Image.Resampling.NEAREST).save(out/'icon.png')
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html')
m=re.search(r'const data=(.*?);function choose',s);data=json.loads(m.group(1));data['okayu'][0].update(image='../okayu-vfx03/tier1.png',kind='주먹밥 자체12픽셀 · 투명 여백 오류 수정 · 밥·김 형태 보존')
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False)+s[m.end(1):]
s=s.replace('먹을 수 있는 식량을 먹으면 만복 +20, 그 외 음식은 +8.','보존식량(ration)을 먹으면 만복 +20, 먹을 수 있는 고기 조각(chunk)은 +8.')
p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();assert digest==read(run/'capture-validation.json')['binarySha256'];shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;d=read(p);d.update(visualRevision='okayu-vfx03',playBinarySha256=digest,currentVisualReviewGod='okayu',currentVisualReviewTier=1,okayuVisualFeedback='Tier1 onigiri import crop corrected: visible sprite12x11 instead of7x7; original artwork preserved. Pending review.',okayuVisualValidation='analysis/native/okayu-vfx03/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 오카유');b=s.index('## 페코라',a);part=s[a:b].replace('- 1성:','- 1성: okayu-vfx03 검토 대기. 투명 여백 포함 축소 오류로 실제7픽셀 → 보이는 주먹밥 자체12x11픽셀로 재수입. 원화·색·우측상단 위치 유지. 나머지 파란 보호막/자원 표시 유지. 다른 도트·전투 소스 해시 보존.',1);p.write_text(s[:a]+part+s[b:],encoding='utf-8')
d=read(run/'art-validation.json');d.update(runtimeSha256=digest,otherSourceAndArtHashesPreserved=True,tests='22-god native controls and fresh-process restore passed',feedback='pending',prompt='assets/holocrawl/okayu-vfx02/generation.json',review='analysis/previews/all-gods-vfx-draft04/index.html#okayu');(run/'checkpoint-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'CURRENT_WORKSPACE.md';p.write_text('현재 오카유1성 okayu-vfx03 검토: 연보라 밥+짙은 김 주먹밥12픽셀로 가호 표시 수정. 보호막/만복 공통 배지·3/5성·전투 코드는 유지. 원화·프롬프트 assets/holocrawl/okayu-vfx02,수입 교정 근거 analysis/native/okayu-vfx03.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published native Okayu passive icon and tested runtime; other source/art preserved.')
