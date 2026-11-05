from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
note='''# 잔향도시 1층 최종 배치안 / 2026-11-05

사용자 요청: 지금까지 만든 요소를 모두 넣은 1층 최종 배치. 최종 사용자 검토 대기, 승인 완료로 간주하지 않음.

현재 검토: http://127.0.0.1:8798/city-floor-final01/layout-review.html
직접 탐험: http://127.0.0.1:8798/city-floor-final01/?map=0&placement=5110501

원본 0.34.1 D:1 지형 3개 중 1번, 소품 시드 5110501. 지형 행 불변. 아크릴/티셔츠 벽 진열창 각 1곳 + 교차 상품 앞 진열대, 닫힌/반열린 셔터 각 1곳, 배송 상자 3곳(다른 배치 2~3), 쓰레기 1곳, 짧은 펜스 2칸(다른 배치 2~3), 설비 벽장식 4종 모두 포함. 승인된 좌우반전 원본 계단/문/물/바닥/벽 도트 유지. 배관 3~5칸, 왼쪽 위·오른쪽 아래 꺾임 유지. 물은 원본 지형대로; 이 시드에는 깊은 물이 있음, 얕은 물을 강제 추가하지 않음.

소품/펜스는 계단까지의 주요 경로를 피하고, 남은 바닥 전체 연결을 보존. 펜스 이동 차단·시야 투과. 3지도×10배치의 모든 종류/연결/문계단 여유/원본 지형 보존 확인. 상자 파괴→드롭→획득→재접속 저장 검증. 기존 city-explore01 저장과 별도 네임스페이스.

구현: scripts/prepare-final-floor01.py + scripts/final-floor-layout01.js. 재구성 후 show-final-floor01.cjs로 검토 캡처. check-final-floor01.cjs, check-final-floor-crates01.cjs, check-final-floor-exploration01.cjs. RUN_HOME_CHECKS.ps1에 연결. OPEN_HOME_EXPLORER.ps1 기본 최신 배치로 변경.

실제 게임 실행/통합은 보류. 브라우저 시안이며 몹·전투·아이템 사용·다음 층 이동 미구현. 원본 지형은 3개 추출본, 브라우저에서 무제한 원본 지형 생성하는 기능 아님. 이전 ZIP 패키징은 재개하지 않음.

---

'''
for file in [root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
 text=file.read_text(encoding='utf-8-sig')
 if not text.startswith('# 잔향도시 1층 최종 배치안'): file.write_text(note+text,encoding='utf-8')
file=root/'migration-status.json';state=json.loads(file.read_text(encoding='utf-8-sig'))
state.update(updated='2026-11-05',activeWork='browser-city-floor-final01',currentVisualReview='preview/city-floor-final01/layout-review.html',next='Review final first-floor layout candidate; retain approved art and mirrored original stairs. Browser-only; native integration remains deferred.')
state['finalFloorCandidate']={'path':'preview/city-floor-final01','placementSeed':5110501,'map':0,'layoutChecks':30,'status':'awaiting user review','nativeIntegrated':False}
file.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved final-floor continuation notes and current preview pointer.')
