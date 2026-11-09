# 제단 3종 식별성 수정 — altars03

내장 image_gen으로 altars02 원화를 편집했다. 스이세이는 광물 결정 대신 별·혜성 꼬리, 라미는 얼음덩어리 대신 눈꽃 문양 술병과 술잔, 메라는 붉은 화로의 푸른 불꽃으로 변경했다. 전체 프롬프트는 `generation-prompt.json`, 생성 원화는 `original-atlas.png`다.

가져오기 도구 `scripts/import-holo-altars03.py`는 해당 세 칸만 잘라 32×32 RGBA 타일로 축소·배치한다. 나머지 19개의 실제 게임 PNG는 altars02 해시와 비교하여 바이트가 같은지 확인한다. `changed-preview.png`는 수정 타일 3개를 6배 확대하고, `native-preview.png`는 전체 22개를 4배 확대한다. 실제 경로·해시는 `manifest.json`에 기록한다.
