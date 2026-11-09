from pathlib import Path
from PIL import Image
import json,re,shutil
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/noel-supply-sequence01';raw=run/'native/shots';out=root/'analysis/previews/noel-supply-sequence01';out.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(run/'capture-validation.json')['status']=='passed'
files=['noel-supply-before.png','noel-supply-effect0.png','noel-supply-effect1.png','noel-supply-after.png','noel-supply-revealed.png']
frames=[Image.open(raw/n).convert('RGB').crop((227,196,579,484)).resize((704,576),Image.Resampling.NEAREST) for n in files]
frames[0].save(out/'tier3.gif',save_all=True,append_images=frames[1:],duration=[700,240,300,450,1800],loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['noel'][5].update(image='../noel-supply-sequence01/tier3.gif',kind='생성 전 → 보급 이펙트 → 이펙트 종료 → 왼쪽으로 한 칸 이동해 발밑 장비 확인 · 같은 전투의 실제 연속 캡처 · 검사용 진척 사전 설정');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
(run/'sequence-manifest.json').write_text(json.dumps(dict(status='passed',files=files,nativeCapture=True,actualPlayerMovement=True,giftRemainsOnDeliveryTile=True,noScreenshotPainting=True,runtimeUnchanged=True,numericChanges=False,review='analysis/previews/noel-supply-sequence01/tier3.gif'),indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d['noelTier3Preview']='analysis/previews/noel-supply-sequence01/tier3.gif';d['noelVisualFeedback']='Tier1 approved. Tier3 actual native sequence: before/effect0/effect1/after/step left to reveal floor gift. Review pending.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 노엘');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 3성:','- 3성: noel-supply-sequence01 실제 연속 GIF로 수정. 보급전/효과2프레임/종료/왼쪽 한칸 실제이동 후 바닥장비 확인. ',1)+s[b:];p.write_text(s,encoding='utf-8')
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text('노엘3성 미리보기: noel-supply-sequence01/tier3.gif에 실제 보급 이펙트와 한칸 이동 후 바닥 장비 확인까지 포함. 게임 실행파일/전투수치 유지. 검토 중.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published actual gift delivery and step-aside reveal GIF; runtime unchanged.')
