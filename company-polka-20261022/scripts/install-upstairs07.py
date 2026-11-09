from pathlib import Path
from PIL import Image
import sys,shutil,json
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-stairs06';a=d/'assets'
shutil.copy2(sys.argv[1],a/'stairs-up07-original.png')
im=Image.open(a/'stairs-up07-original.png').convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
box=im.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox();im.crop(box).resize((32,32),Image.Resampling.NEAREST).save(a/'stairs-up07-32.png')
for n in ['app.js','stairs-compare.html']:
 p=d/n;p.write_text(p.read_text(encoding='utf-8-sig').replace('stairs-up06-32.png','stairs-up07-32.png'),encoding='utf-8')
p=d/'index.html';p.write_text(p.read_text(encoding='utf-8-sig').replace('v=spiral-stairs06','v=upstairs07'),encoding='utf-8')
note='# 올라가는 계단 수정07 / 2026-11-03\n\n현재 street-stairs06 미리보기에서 올라가는 계단만 stairs-up07-32.png로 교체. 사용자: 내려가는 원형 계단은 직관적, 올라가는 부채형은 이질적. 내려가는 stairs-down06-32.png 그대로 유지. 올라가는 쪽은 방사형 부채/중심축을 없애고 완만한 곡선의4단 계단과 단차가 보이는 윤곽으로 수정. 맵 로직/위치/실제 층 이동 구현 여부 변함없음.\n\n'
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/n;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentStairsUpRevision='upstairs07',currentStairsDownRevision='spiral06',lastArchiveIncludesLatest=False,next='Review upstairs07 in street-stairs06; approved circular downstairs06 unchanged. Runtime remains ayame-zanshin02.')
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated upstairs only; downstairs06 unchanged.',box)
