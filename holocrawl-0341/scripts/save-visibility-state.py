from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
legacy = root.parent / 'company-polka-20261022'
logic = json.loads((root / 'analysis/visibility01/logic-validation.json').read_text(encoding='utf-8'))
browser = json.loads((root / 'preview/street-vision01/browser-validation.json').read_text(encoding='utf-8'))
assert logic['status'] == browser['status'] == 'passed'
status_path = root / 'migration-status.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status.update(phase='visibility-preview', activeWork='visibility-preview',
              visibilityPreview='preview/street-vision01/index.html',
              visibilityPreviewImplemented=True, nativeLOSFixtureMatch=True,
              visibilityFixtureCases=76, visibilityComparedCells=27436,
              next='Review sight and exploration fog in the approved street preview; keep the 22-god scaffold parked until dungeon foundations are ready.')
status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
note = '''# 현재 작업: 시야·탐험 안개 / 2026-11-04

사용자 정정: 22신은 0.34.1용 구조를 마련해 둔 상태로 두고, 먼저 시야·탐험 안개 작업을 이어간다. 신 설계 검토나 일반 숭배 이식을 다음 작업으로 자동 진행하지 않는다.

현재 미리보기: http://127.0.0.1:8797/street-vision01/
로컬 파일: holocrawl-0341/preview/street-vision01/index.html
서버: holocrawl-0341/preview에서 Python http.server 8797 실행.

DCSS 0.34.1 원본 find_ray 경로를 내보내 브라우저 시야에 사용했다. 반경 7칸, 벽 가림, 대각선 모서리 사이 시선 통과, 펜스 시선 통과. 미탐험은 검게, 탐험했던 지형은 어둡게 기억하며 시야 밖 몹은 숨긴다. 방향키/WASD 및 QEZC 대각선 이동, 알려진 길 클릭 이동, 새로운 몹 발견 시 자동 이동 정지. 안개 끄기는 비교용이며 탐험 기억을 늘리지 않는다.

원본 losight의 76개 지도·27,436칸 결과와 전부 일치. Node 논리 검사와 데스크톱/모바일 브라우저 검증 통과. 자세한 구현은 design/VISIBILITY.md 참조.

승인된 바닥·벽·펜스·계단 도트 유지. 현재는 독립 브라우저 미리보기이며 새 거리 던전과 22신의 실제 게임 연결은 아직 미완료다. 아래 이전 기록의 '다음은 신 구현' 및 '시야 미구현' 문구는 이 기록으로 대체한다.

---

'''
for path in [root/'README.md', root/'CONTINUE_HERE.md', root.parent/'CONTINUE_HERE.md',
             *[legacy/name for name in ['CONTINUE_HERE.md', 'CURRENT_WORKSPACE.md', 'START_HERE_HOME.md']]]:
    existing = path.read_text(encoding='utf-8-sig') if path.exists() else ''
    if not existing.startswith('# 현재 작업: 시야·탐험 안개'):
        path.write_text(note + existing, encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json', 'VFX_DRAFT_STATUS.json']:
    path = legacy/name
    state = json.loads(path.read_text(encoding='utf-8-sig'))
    state.update(activeWork='visibility-preview', activeProject=str(root),
                 currentVisualReview=str(root/'preview/street-vision01/index.html'),
                 lastArchiveIncludesLatest=False, next=status['next'])
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Saved visibility preview checkpoint; god scaffold parked.')
