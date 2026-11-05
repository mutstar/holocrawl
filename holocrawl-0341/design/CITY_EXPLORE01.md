# 현재 작업: 잔향도시1층 직접탐험01 / 2026-11-04

사용자 요청: 확정계단/테두리 도트 포함 랜덤1층을 직접 탐험. 새로 native0.34.1 D:1 지형3개(2026110461/62/63)를 headless로추출,게임창/플레이/엔진도트적용없음. 브라우저에8방향이동/벽·소품·깊은물충돌/문범프열기·인접닫기/시야7칸/미탐험검정·기억어둡게/알려진곳클릭자동이동/발견지역미니맵/브라우저자동저장·복원연결. 계단은확정원본좌우반전08그대로. 소품4개만랜덤배치. 아직몹·아이템·전투·다음층없음.

http://127.0.0.1:8797/city-explore01/

방향키/WASD, QEZC·숫자패드대각선, 문에부딪히면열림, 발견한바닥클릭이동, M탐험지도, Esc자동이동중단. 버튼새1층은추출3지형순환+소품재추첨, 무한native생성이아님. 선택/배치별localStorage자동저장. 시야는0.34.1 원본최소경로표를사용하는기존브라우저모듈+문/투명벽차폐연결이며전체게임시야엔진이식주장없음.

3지도원본행보존/계단연결/벽충돌/닫힌문너머차폐→열면보임/문진입전열기/닫기/알려진곳자동이동/탐험기억/새로고침복원/모바일·오류검증통과. browser-validation.json 및 exploration-manifest.json. explore-start.png/explore-walked.png/review-page.png. 원본지형 native-d1.json, 생성로그 analysis/city-explore01/export.log. 원본tree/statue는도시스킨에서통행차단콘크리트구조로표시. 원본PNG 바이트동일확인.

export-city-explore01.py → prepare-city-explore01.py → check-city-explore01.cjs. 기본입구/지도1. 사용자직접탐험피드백대기.

---

