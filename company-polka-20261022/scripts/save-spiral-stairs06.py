from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];preview='analysis/previews/street-stairs06/index.html'
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/n;data=json.loads(p.read_text(encoding='utf-8-sig'));data.update(currentVisualReview=preview,currentDungeonPreview=preview,currentMapArt='street-stairs06',activeWork='spiral-stairs-review',lastArchiveIncludesLatest=False,next='Review single-tile circular stairs without handrails in street-stairs06. Raised upstairs and recessed downstairs; existing map and engine status unchanged. Native runtime remains ayame-zanshin02.')
 if n=='VFX_DRAFT_STATUS.json':data['review']=preview
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 손잡이 없는 원형 계단06 / 2026-11-03\n\n현재 analysis/previews/street-stairs06/index.html (http://127.0.0.1:8796/). 사용자 요청: 손잡이를 없애고 돌죽과 같은 방향감의 원형 계단, 직관적이고 이질적이지 않게. image_gen으로 올라가기/내려가기 각각 생성한32px 자산 사용. 올라가기 솟은 부채꼴 단/내려가기 어두운 중심 구멍, 회색 시멘트, 단4~5개 중심의 단순한 형태. 기존 맵/시작·출구 배치 로직은 그대로. 브라우저 오류·이동·출구 도달·재현·반응형 검사 통과. 독립 JS 미리보기이며 실제 층 이동 미연결, native runtime ayame-zanshin02 유지. 원본/지시문은 preview 폴더에 저장.\n\n'
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for n in ['OPEN_GALLERY.cmd','OPEN_VFX_REVIEW.cmd']:(r/n).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\street-stairs06\\index.html"\r\n',encoding='ascii')
manifest={'revision':'street-stairs06','preview':preview,'engineIntegrated':False,'runtimeChanged':False,'floorTravelImplemented':False,'assets':['assets/stairs-up06-32.png','assets/stairs-down06-32.png'],'browserValidation':'analysis/previews/street-stairs06/browser-validation.json','artDirection':'Circular stairs, no handrails; raised up and recessed down, one tile'}
(r/'analysis/design/street-stairs06.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved spiral stairs06 review.')

