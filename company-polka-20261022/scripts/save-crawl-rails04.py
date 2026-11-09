from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
preview='analysis/previews/street-stairs04/index.html'
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/name;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentVisualReview=preview,currentDungeonPreview=preview,currentMapArt='street-stairs04',activeWork='crawl-stairs-silver-rails-review',lastArchiveIncludesLatest=False,next='Review DCSS-shaped up/down stairs with silver handrails in street-stairs04. Previous flat rectangular upstairs rejected. Native runtime remains ayame-zanshin02; floor travel not connected.')
 if name=='VFX_DRAFT_STATUS.json':data['review']=preview
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 돌죽형 계단 + 은색 손잡이04 / 2026-11-03\n\n현재 analysis/previews/street-stairs04/index.html (http://127.0.0.1:8794/). 사용자 요청: 위·아래 모두 돌죽처럼 하되 은손잡이 추가. 기존 직사각형 flat02/up03 형태 대신 원본 돌죽 계단을 각각 참조해 image_gen 편집, 32px 두 자산 사용. 올라가기 솟은 윤곽/내려가기 파인 구멍을 구별하고 얇은 손잡이 추가. 원본 비교 stairs-compare.png, 실제 필드 upstairs-field.png/downstairs-field.png. 맵 생성·층 이동 로직은 변경 없음, 독립 JS 미리보기. 실제 층 이동 미연결, native runtime ayame-zanshin02 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for name in ['OPEN_GALLERY.cmd','OPEN_VFX_REVIEW.cmd']:(r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\street-stairs04\\index.html"\r\n',encoding='ascii')
manifest={'revision':'street-stairs04','preview':preview,'engineIntegrated':False,'floorTravelImplemented':False,'assets':['assets/stairs-up04-32.png','assets/stairs-down04-32.png'],'replaces':'Flat rectangular up/down visual style','browserValidation':'analysis/previews/street-stairs04/browser-validation.json'}
(r/'analysis/design/street-stairs04.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved stairs04 review.')
