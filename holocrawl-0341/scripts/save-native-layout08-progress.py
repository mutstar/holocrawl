from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
note='''# 현재 검토: 돌죽0.34.1 원본 지형 × 도시 타일08 / 2026-11-04

사용자가 원본 생성 소스를 그대로 쓰면 어떻게 나오는지 질문. 순정0.34.1 베이스의 원본 builder를 헤드리스 도구로 호출해 D:5 세 개/D:10 세 개를 추출하고 도시 타일로 표시했다. 길/벽/물/문/계단 위치 원본 그대로. 실제 게임 창/플레이 세션 및 도시 지형 엔진 적용은 진행하지 않았다.

http://127.0.0.1:8797/native-layout08/
상세 design/NATIVE_LAYOUT_REVIEW08.md. 브라우저는 추출한6개 지도를 보여주며 새 원본 지도 생성은 아직 연결하지 않았다. 33600칸 데이터 일치·6지도 렌더·전환·모바일·오류 검사 통과. 원본 생성기로의 프로젝트 전환은 아직 미확정. 다음은 원본 방/통로 구조와 C의 넓은 공간 비교 피드백.

---

'''
for target in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    content=target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: 돌죽0.34.1 원본 지형'):
        target.write_text(note+content,encoding='utf-8')
target=root/'migration-status.json'
status=json.loads(target.read_text(encoding='utf-8'))
status.update({'activeWork':'browser-native-terrain-snapshot-review08','currentVisualReview':'preview/native-layout08/index.html','nativeTerrainSnapshotReview':'preview/native-layout08/index.html','nativeTerrainSnapshotCount':6,'nativeTerrainHeadlessExport':True,'browserNativeGeneratorPorted':False,'actualGameApplicationDeferred':True,'next':'Review unmodified native 0.34.1 terrain snapshots with city tiles. No project-wide generator switch approved yet; browser-only design work continues.'})
target.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    target=root.parent/'company-polka-20261022'/name
    state=json.loads(target.read_text(encoding='utf-8'))
    state.update({'activeWork':status['activeWork'],'currentVisualReview':str(root/'preview/native-layout08/index.html'),'next':status['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True})
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved native terrain review08 and continuation pointers.')
