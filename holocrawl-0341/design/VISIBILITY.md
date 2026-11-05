# 시야와 탐험 안개

현재 검토 대상은 `preview/street-vision01/`이다. 승인된 거리 생성기와 도트를 유지하고 시야·기억 표시를 추가했다. 실제 네이티브 게임에 거리 생성기를 연결한 단계는 아니다.

## 규칙

- 기본 시야는 반경 7칸의 정사각형 범위다. 벽에 가려진 칸은 보이지 않는다.
- 벽 표면은 보이고, 대각선으로 맞닿은 두 벽 사이로는 DCSS와 같이 시선이 통한다.
- 펜스는 이동을 막지만 시선을 막지 않는다.
- 처음 보는 곳은 검게 가린다. 이전에 본 지형만 어둡게 기억한다. 보이지 않는 지형 변화는 기억에 반영하지 않는다.
- 몹과 아이템은 현재 시야에 있는 것만 그린다. 계단은 기억한 지형에 남는다.
- 클릭 이동은 탐험한 길만 사용한다. 새 몹이 보이거나 이동에 실패하면 멈춘다.
- 안개 토글과 출발점·계단·펜스 이동 버튼은 미리보기 검토 기능이다.

## 구현과 검증

`holo34-visibility.cc`가 수정하지 않은 0.34.1 `find_ray`의 경로를 추출한다. `visibility.js`는 이 경로를 반사해 시야를 계산한다. `losight`가 만든 고정/무작위 시험 지도 76개, 27,436칸과 결과가 모두 일치했다.

- 네이티브 도구 빌드: `BUILD_VISIBILITY.ps1`
- 경로와 원본 검증 자료 추출: `scripts/export-visibility.py`
- 논리 검사: `node scripts/test-visibility.cjs`
- 브라우저 검사: `node scripts/check-visibility-preview.cjs`
- 결과: `analysis/visibility01/logic-validation.json`, `preview/street-vision01/browser-validation.json`

브라우저 검사는 안개 전환의 기억 보존, 미탐험 클릭 차단, 몹 발견 시 이동 정지, 대각선 키 입력, 모바일 가로 넘침 및 JavaScript 오류를 확인했다.

22신 구조와 원본 0.34.1 기준 실행 파일은 유지한다. 신 권능의 전투 구현은 현재 작업 범위에 추가하지 않는다.
