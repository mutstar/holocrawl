# 제단 도트 스타일 수정 — altars02

altars01의 세밀한 원화 축소 느낌을 줄이기 위해 내장 image_gen으로 더 단순한 새 아틀라스를 생성했다. 첫 편집 시안은 여전히 세밀해 `candidate-detailed-*`로 보존했다. 최종본은 별도 이미지 참조 없이 22개 구조물 목록과 저해상도 스타일 지시로 생성했다. 전체 프롬프트는 `generation-prompt.json`, 최종 원화는 `original-atlas.png`다. 엄격한 수작업 도트나 고정 16색 팔레트를 보장하는 방식은 아니다.

게임 파일은 기존과 같은 32×32 RGBA 타일이다. `native-preview.png`는 실제 타일을 최근접 4배 확대한 미리보기다. 파일 경로·해시는 `manifest.json`. 원본 알파를 보존해 셀을 자르고 최근접 축소하는 가져오기는 `scripts/import-holo-altars02.py`를 사용한다. 이전 아트와 게임 검사본은 보존했다.
