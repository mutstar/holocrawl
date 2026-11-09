from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
preview='analysis/previews/street-stairs05/index.html'
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/name;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentVisualReview=preview,currentDungeonPreview=preview,currentMapArt='street-stairs05',activeWork='crawl-stairs-silver-straight-rails-review',lastArchiveIncludesLatest=False,next='Review DCSS-shaped up/down stairs with silver handrails in street-stairs05. Previous flat rectangular upstairs rejected. Native runtime remains ayame-zanshin02; floor travel not connected.')
 if name=='VFX_DRAFT_STATUS.json':data['review']=preview
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 돌죽형 계단 + 직선 은색 손잡이05 / 2026-11-03\n\n현재 analysis/previews/street-stairs05/index.html (http://127.0.0.1:8795/). 사용자 사진 피드백: 계단마다 꺾인 난간이 아니라 양옆에 각각 길게 이어진 직선 손잡이를 원함. 계단 윤곽을 유지하며 양쪽 연속 은색 봉으로 수정. 기존 직사각형 flat02/up03 형태 대신 원본 돌죽 계단을 각각 참조해 image_gen 편집, 32px 두 자산 사용. 올라가기 솟은 윤곽/내려가기 파인 구멍을 구별하고 얇은 손잡이 추가. 원본 비교 stairs-compare.png, 실제 필드 upstairs-field.png/downstairs-field.png. 맵 생성·층 이동 로직은 변경 없음, 독립 JS 미리보기. 실제 층 이동 미연결, native runtime ayame-zanshin02 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for name in ['OPEN_GALLERY.cmd','OPEN_VFX_REVIEW.cmd']:(r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\street-stairs05\\index.html"\r\n',encoding='ascii')
manifest={'revision':'street-stairs05','preview':preview,'engineIntegrated':False,'floorTravelImplemented':False,'assets':['assets/stairs-up05-32.png','assets/stairs-down05-32.png'],'replaces':'Flat rectangular up/down visual style','browserValidation':'analysis/previews/street-stairs05/browser-validation.json'}
(r/'analysis/design/street-stairs05.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved stairs05 review.')

