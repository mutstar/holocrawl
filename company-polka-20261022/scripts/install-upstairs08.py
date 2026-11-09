from pathlib import Path
from PIL import Image
import sys,shutil,json
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-stairs06';a=d/'assets'
shutil.copy2(sys.argv[1],a/'stairs-up08-original.png')
im=Image.open(a/'stairs-up08-original.png').convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
box=im.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox();im.crop(box).resize((32,32),Image.Resampling.NEAREST).save(a/'stairs-up08-32.png')
for n in ['app.js','stairs-compare.html']:
 p=d/n;p.write_text(p.read_text(encoding='utf-8-sig').replace('stairs-up07-32.png','stairs-up08-32.png'),encoding='utf-8')
p=d/'index.html';p.write_text(p.read_text(encoding='utf-8-sig').replace('v=upstairs07','v=upstairs08'),encoding='utf-8')
note='# 올라가는 계단 재제작08 / 2026-11-03\n\n현재 street-stairs06 미리보기에서 올라가는 계단만 stairs-up08-32.png로 교체. 사용자: 내려가는 원형 계단은 직관적, 올라가는 계단을 원형으로 다시 제작 요청. 내려가는 stairs-down06-32.png 그대로 유지. 올라가는 쪽은 작은 중심축을 감아 오르는 원형 계단5단, 거친 회색 시멘트, 밝은 테두리 절제, 어두운 단 옆면으로 높이 표시. 맵 로직/위치/실제 층 이동 구현 여부 변함없음.\n\n'
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/n;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentStairsUpRevision='upstairs08',currentStairsDownRevision='spiral06',lastArchiveIncludesLatest=False,next='Review upstairs08 in street-stairs06; approved circular downstairs06 unchanged. Runtime remains ayame-zanshin02.')
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Rebuilt circular upstairs only; downstairs06 unchanged.',box)


