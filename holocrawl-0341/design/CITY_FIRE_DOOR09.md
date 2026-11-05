# 철제 방화문 도트09 / 2026-11-04

사용자: 원본0.34.1 지형을 긍정, 임시 문이 어색하므로 문부터 제작 요청. 시멘트 도시·공연장 백스테이지에 맞는 회색 철제 방화문을 닫힘/열림2상태로 제작했다. 신규 도트 사용자 승인 전이다.

검토: http://127.0.0.1:8797/native-door09/

기존 임시 문·새 닫힌 문·새 열린 문을 동일 지형/동일 문 위치에서2배 확대 비교한다. 아래 지도는32×32타일을 표시한다. 다른 문/지도 선택, 문 클릭 또는 버튼으로 열기·닫기, 전체 지도/화면 이동, 임시 문 비교를 지원한다. 닫힌 문은 은빛 가로 손잡이, 열린 문은 오른쪽으로 빠진 문짝과 가운데 투명 통로다.

도트는 built-in image_gen으로 생성했다. 닫힌 문 생성 후 이를 편집 대상으로 열린 문을 생성, 원본PNG2개를 워크스페이스에 보존했다. 알파 면적 평균 축소와14색 팔레트 정리로32×32 PNG로 제작했다. 고해상도 생성 원화에서 도트로 변환한 것이며 전 픽셀을 수작업으로 찍었다는 뜻은 아니다.

파일: preview/native-door09/assets/fire-door-{closed,open}-original.png 및 fire-door-{closed,open}32.png. 정확한 최종 프롬프트·모드·처리 기록은 art-manifest.json에 저장했다. 구현 파일은 app.js, index.html, style.css. 설치는 scripts/install-native-door09.cjs, 준비는 scripts/prepare-native-door09.py.

기존 native-layout08은 보존했다. 6개 native-maps.json/JS를 그대로 복사, 좌표/지형 feature는 수정하지 않는다. 열림/닫힘은 브라우저 표시용 별도Set으로 관리한다. 실제 턴 소모·문 통과·소음·시야 갱신·네이티브 게임 행동은 아직 연결하지 않았다. 게임 엔진/실행 파일을 수정하거나 실행하지 않았다. 몹·아이템 배치도 진행하지 않았다.

검사: scripts/check-native-door09.cjs. 두 상태32×32·14색, 닫힘 중앙 불투명/열림 중앙 투명, 열기·닫기 픽셀 변화와 복귀, 원본 지형 데이터 유지, 6지도 표시, 문 이동·기존 문 비교·모바일 폭·JS/이미지 오류 검사 통과. 최종 스크린샷 door-comparison.png, door-closed-field.png, door-open-field.png와 browser-validation.json 보관.

다음은 문 크기·색·벽과의 접합에 대한 사용자 피드백. 아직 승인 또는 런타임 적용으로 간주하지 않는다.
