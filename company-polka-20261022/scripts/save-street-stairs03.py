from pathlib import Path
import json
from PIL import Image
r=Path(__file__).resolve().parents[1];d=r/'analysis/previews/street-stairs03'
im=Image.open(d/'assets/stairs-up03-original.png').convert('RGBA');bounds=im.getchannel('A').point(lambda a:255 if a>200 else 0).getbbox();im.crop(bounds).resize((28,28),Image.Resampling.NEAREST).save(d/'assets/stairs-up03-28.png')
manifest={'revision':'street-stairs03','preview':'analysis/previews/street-stairs03/index.html','scope':'independent browser prototype','engineIntegrated':False,'runtimeChanged':False,'upstairs':'assets/stairs-up03-28.png','approvedDownstairs':'assets/stairs-flat02-28.png','arrival':'Upstairs on an open 3x3 patch near the former start; player starts one cell south','validation':'analysis/previews/street-stairs03/generator-validation.json','browserValidation':'analysis/previews/street-stairs03/browser-validation.json','floorTravelImplemented':False}
(r/'analysis/design/street-stairs03.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/n;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentVisualReview=manifest['preview'],currentDungeonPreview=manifest['preview'],currentMapArt='street-stairs03',activeWork='street-upstairs-review',lastArchiveIncludesLatest=False,next='Review upstairs and start point in street-stairs03. Approved flat downstairs retained. Fog of war and native floor travel not yet implemented; runtime remains ayame-zanshin02.')
 if n=='VFX_DRAFT_STATUS.json':data['review']=manifest['preview']
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 올라가는 계단·시작 지점03 / 2026-11-03\n\n현재 analysis/previews/street-stairs03/index.html, http://127.0.0.1:8793/. 올라가는 계단 28px 도트 추가, 승인된 내려가는 계단 flat02 유지. 시작 지점 주변3×3 바닥에 귀환 계단 배치, 캐릭터는 바로 남쪽1칸에서 시작. 시작점 보기/다음 층 입구 보기 버튼으로 비교 가능. 자동생성500개 연결·시작계단 배치 검증 통과. 실제 층 이동, 전투 및 탐험 안개는 아직 미구현. 독립 JS 미리보기이며 native runtime은 ayame-zanshin02 유지. 이전 ZIP 최신작업 미포함.\n\n'
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for n in ['OPEN_GALLERY.cmd','OPEN_VFX_REVIEW.cmd']:(r/n).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\street-stairs03\\index.html"\r\n',encoding='ascii')
print('Saved upstairs review and continuation state.')
