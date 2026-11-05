# 2026-11-06 · holoX52 홀로도리 아지트 외형을 참고한 입구

- 사용자: 홀로도리 holoX 건물과 비슷하게 요청.51원본보존, 최신 `/holox-floor52/?map=2`.
- 실제게임화면 확인: https://dengekionline.com/article/202607/79730 및 https://note.com/kandaharubo/n/nbf26a9548907 . 전격온라인 공식선행화면의 검은 장갑벽/보라색 원형창/보라색 외곽선/노란CAUTION띠를 입구 벽 모듈로 각색. 원본 건물 전체를 복제한 외관이 아님.
- 새2칸64x32 도트 built-in image_gen. 원화 entrance-original.png 보존,24색/단단한알파/실제64x27가시영역으로감축. design/holox52-prompts.json 및 design/holox52-reference/sources.json, art-manifest.json.
- 입구 기존벽 x4/5와7/8,y8에각각왼쪽모듈과좌우반전모듈을연결. 둥근보라창4개, 노란경고띠, 각진보라출입구틀. 개별멤버명판/바닥장식없음. 중앙x6열린바닥보존. 기존connectedwall·내부시설·바닥유지.
- export-holox-floor52.cjs / check-holox-floor52.cjs. 최초export require상대경로 오류를수정후실행. 3사례모두 최종validation passed: 원래48과전체지형행동일/벽위설치/입구통행/계단·5멤버·보상접근/자동진입·줍기/안개/모바일/페이지·HTTP오류0. lab-2.png 시각검토.
- 외관검토대기. 네이티브생성기/게임미적용. 소스·수치·세이브미변경. 로컬미커밋/미푸시.
