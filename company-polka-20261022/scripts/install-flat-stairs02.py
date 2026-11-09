from pathlib import Path
from PIL import Image
import shutil,sys,json
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-stairs01';a=d/'assets'
shutil.copy2(sys.argv[1],a/'stairs-flat02-original.png')
im=Image.open(a/'stairs-flat02-original.png').convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
box=im.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox()
# Trim transparent canvas margin only, then export with nearest-neighbor sampling.
im.crop((249,364,982,905)).resize((28,28),Image.Resampling.NEAREST).save(a/'stairs-flat02-28.png')
p=d/'app.js';s=p.read_text(encoding='utf-8').replace("downstairs:'assets/stairs-rails48.png'","downstairs:'assets/stairs-flat02-28.png'")
s=s.replace("ctx.drawImage(images.downstairs,(map.exit.x-.25)*t,(map.exit.y-.5)*t,t*1.5,t*1.5);","ctx.drawImage(images.downstairs,(map.exit.x+.0625)*t,(map.exit.y+.0625)*t,t*.875,t*.875);")
p.write_text(s,encoding='utf-8')
p=d/'index.html';s=p.read_text(encoding='utf-8').replace('v=stairs01','v=flat-stairs02').replace('잔향도시 · 계단과 손잡이','잔향도시 · 1칸 계단 도트');p.write_text(s,encoding='utf-8')
for filename in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/filename;p.write_text('# 바닥 계단 도트 수정02 / 2026-11-03\n\n이전 48px/1.5칸 원근 계단은 이질적이라 사용자 거절. street-stairs01에서 stairs-flat02-28.png로 교체, 1칸 안쪽28px로 표시. 바닥 직사각형 구멍+4줄 계단+짧은 손잡이 방향으로 수정. 맵 생성/출구 로직 및 벽 입구는 유지. 실제 층 이동 미연결.\n\n'+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Installed flat stairs inside one tile.')

