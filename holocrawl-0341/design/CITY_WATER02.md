# 현재 검토: 얕은 물 가시성 수정02 / 2026-11-04

사용자: 깊은 물은 괜찮지만 얕은 물이 물처럼 보이지 않는다고 피드백. 얕은 물 원화만 built-in image_gen으로 수정: 회색 콘크리트 덩어리/균열을 줄이고 청록 물빛과 짧은 밝은 파문을 강화. 표면 합성 농도62%→90%. 깊은 물 PNG는01과 동일하게 유지. 새 얕은 물 승인 전.

http://127.0.0.1:8797/native-water02/
원화·프롬프트 art-manifest.json, 그림 water-comparison.png 및 실제 원본 지도 캡처 native-water-field.png/native-water-map6.png. 인공 경계 예시와 실제 지도는 구분. 원본6지도/확정 네모 문12/깊은 물 PNG 보존·6지도/모바일/오류 검증 통과. 실제 게임 미적용. 다음은 얕은 물 색·파문 피드백.

---


재질은128×128/18색으로 정리,32픽셀 구간16개를 파생 사용한다. 기존 물가·오목 모서리·깊이 전환 코드는 유지했다. scripts/prepare-water02.py 및 scripts/install-check-water02.cjs를 사용했다. 깊은 물 재질의 바이트 동일성과 문12 PNG 동일성을 검사했고 browser-validation.json에 저장했다. 얕은 물의 새 원본을 워크스페이스에 보존했으며01도 비교안으로 남긴다.
