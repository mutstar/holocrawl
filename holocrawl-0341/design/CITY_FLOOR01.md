# 현재 검토: 실제 원본 D:1 지형 + 소품 적은 랜덤 배치01 / 2026-11-04

사용자 요청: 전체 요소를 넣지 말고 실제1층처럼 랜덤생성해서 보여주기. native0.34.1 headless builder에서 새 D:1 지형3개를 추출(2026110411/12/13). 게임 창/플레이 없음. 지형 행은 원본 그대로. 원본 exit_dungeon만 도시 입구의 올라가는 계단으로 표시. 원본 내려가는 계단3개 유지. 기본 화면은2번 지형2026110412.

http://127.0.0.1:8797/city-floor01/

각 층에 진열창1 + 작은진열1 + 벽가 배송상자1 + 쓰레기1=4곳만 시드 랜덤 배치. 모든20종 강제 배치 안 함. 계단/문3칸 이내 회피, 벽가/연결성 검사. 소품 재추첨 버튼은 지형 유지, 지형 선택은 추출3개 중 선택(브라우저 native생성기 이식 아님). 몹·아이템/전투 없음. 벽 자동 장식 빈도1/4,04의 그림자 유지. 실제 게임 엔진 미적용.

30배치(3지형×10시드) 원본행불변/계단연결/모든기존이동연결/소품4개상한/브라우저·모바일 검사 통과. native-d1.json과 analysis/city-floor01/export.log 원본, browser-validation.json. street.png / entrance.png / downstairs.png / overview.png / full-map.png. export-city-floor01.py → prepare-city-floor01.py → check-city-floor01.cjs. 이전 전체도트01~04 보존.

---

