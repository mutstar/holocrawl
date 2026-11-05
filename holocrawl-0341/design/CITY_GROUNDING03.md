# 현재 검토: 굿즈·계단 바닥 접점 통합03 / 2026-11-04

사용자 요청: 굿즈와 계단이 바닥에 자연스럽게 붙어 보이게 수정하고 맵으로 보여주기. city-complete02와 동일 지형/소품20종 좌표 유지. 굿즈 PNG는 그대로, 맵 렌더에 받침 접촉 그림자/바닥 마모/상점 앞 콘크리트 접합 추가. 계단은 built-in image_gen 수정 원본2개 보관 및32×32/20색 파생 PNG 사용: 올라가는 계단 낮은 발판 연결, 내려가는 계단 밝은 원형 외곽선 제거·어두운 파인 입구. 도트 사용자 승인 전. 기존 승인 계단/이전02는 보존.

http://127.0.0.1:8797/city-complete03/

수정 전후 버튼 및 같은 위치 확대3쌍 제공. complete-map.png, contact-comparison.png, art-manifest.json(프롬프트/도구), browser-validation.json.20종/모든 이동 연결/계단 도달/브라우저 오류 없음/모바일 검증 통과. 이 지도는 수동 검토용이며 실제 게임 엔진 적용/플레이는 계속 보류.

재구성: prepare-city-complete03.py → install-grounded-stairs03.py → check-city-complete03.cjs. 원화2개는 assets에 있음.

---

