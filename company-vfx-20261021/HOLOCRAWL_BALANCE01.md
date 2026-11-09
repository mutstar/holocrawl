# balance01 확정 적용 부록

원래 기획/엔진은 보존한다. 최종 전투 코어 설정은 analysis/native/balance-final01/settings.json이다.

- 메라 브레스의 열기당 가산4→3. 비비 버스트2d(6+floor(I/3))→2d(5+floor(I/3)). 나머지 피해식·비용·범위·쿨다운 유지.
- 메라 추가 화염 보호의 실제 피해 경로 수정, native 저항 뒤 화염 성분에 한 번만50%. 아군 범위/만료 준수.
- 자동 정책13조합 및 루이 주문 지휘 생략은 settings.json의 목록이 기준이다. 미코 근접 새 정책은 미채택.
- 신앙/선물/징벌/저장 공통 규칙은 HOLOCRAWL_BALANCE_RULES_VNEXT.md의 설계 결정이며 정상 캠페인 구현 완료를 뜻하지 않는다.
- 전체22신 수치·강약·자원 제약·검증 범위는 BALANCE_REVIEW_ALL_22_KO.md를 우선한다. 이 파일은 실제 승률을 강제로 같게 만드는 수정이 아니다.
