# 22신 독립 제단 구조물

내장 image_gen으로 8×3 투명 원화 아틀라스 한 장을 생성했다. 원화는 `original-atlas.png`, 사용한 전체 프롬프트는 `generation-prompt.json`이다. 원본 알파를 유지하고 셀을 잘라 최근접 축소·배치하여 각각 32×32 RGBA 타일로 가져왔다. 원본과 이전 tiles01 문양을 보존했다.

`native-preview.png`는 실제 게임 타일을 4배 확대해 비교하는 표다. `manifest.json`은 22개 파일의 경로와 SHA256이다. 게임에서는 이 구조물 자체를 지형 타일로 사용하며, 메뉴의 문양과 분리했다.

재가져오기: Pillow가 있는 Python으로 `scripts/import-holo-altars.py` 실행. SDL 소스 동기화·빌드는 `scripts/build-campaign-tiles.sh`.
