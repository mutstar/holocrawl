from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[1]
preview=root/'analysis/previews/street-walls01'
frames=[Image.open(preview/f'stage-{i}.png').convert('RGB') for i in range(5)]
frames[0].save(preview/'generation-process.gif',save_all=True,append_images=frames[1:],duration=[1100,1100,1100,1100,2400],loop=0)
manifest={'revision':'street-walls01','preview':'analysis/previews/street-walls01/index.html','generatorImplemented':True,'scope':'independent browser prototype','engineIntegrated':False,'runtimeChanged':False,'movementAndCollision':True,'combatImplemented':False,'art':'Approved venue-street03 concept sampled for rendering; not final tile atlas','validation':'analysis/previews/street-walls01/generator-validation.json','browserValidation':'analysis/previews/street-walls01/browser-validation.json'}
(root/'analysis/design/street-walls01.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for filename in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=root/filename
 data=json.loads(p.read_text(encoding='utf-8-sig'))
 data.update(activeWork='street-procedural-preview-review',currentVisualReview=manifest['preview'],currentDungeonPreview=manifest['preview'],currentMapArt='street-walls01',lastArchiveIncludesLatest=False,next='Review interactive street-walls01. Standalone JS generation and movement work; Crawl engine and combat not integrated. Native runtime remains ayame-zanshin02.')
 if filename=='VFX_DRAFT_STATUS.json':data['review']=manifest['preview']
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 잔향도시 벽장식 시안01 · 80×70칸 / 2026-11-03

현재 미리보기: analysis/previews/street-walls01/index.html (로컬 서버 http://127.0.0.1:8790/).
80×70칸 지도, 넓은 광장·큰길·우회 골목 추가. 지도 번호에 따른 방·광장 분할, 골목 연결, 공연장 입구·펜스 배치, 계단·적 배치 구현. 단계별 보기, 새 지도 생성, 방향키/WASD 및 클릭 이동 가능.
500개 지도에서 연결·출구 도달·동일 번호 재현·적 시작 거리 검증 통과. 브라우저 오류 없음, 출구 이동·벽 충돌·재생성·단계 재생·모바일 가로 넘침 검사 통과.
맵 구조는 street-generator02와 동일. 시멘트 바닥 유지. 기존 거리 그림의 실외기·환기구·덕트 부분을 벽에 렌더링하고 꺾인 배관을 추가. 벽면 밝기 약간 증가, 벽 상부 암막 완화. 독립 JS 프로토타입. 최종 타일 세트·Crawl 엔진 통합·전투·아이템 획득은 아직 미구현. 일반 runtime=ayame-zanshin02 유지. 기존 ZIP은 최신 작업 미포함.

'''
for filename in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md','VFX_COMPANY_FEEDBACK.md']:
 p=root/filename
 p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for filename in ['OPEN_GALLERY.cmd','OPEN_VFX_REVIEW.cmd']:
 (root/filename).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\street-walls01\\index.html"\r\n',encoding='ascii')
print('Saved process GIF, manifest and continuation notes.')



