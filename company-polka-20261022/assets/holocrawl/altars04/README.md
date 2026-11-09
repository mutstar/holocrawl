# 스이세이 혜성 · 메라 도깨비불 — altars04

내장 image_gen으로 altars03 원화의 두 칸을 수정했다. 첫 번째 참고는 기존 아틀라스, 두 번째 참고 `mela-reference.png`는 사용자가 첨부한 인물의 머리 옆 도깨비불 형태·색이다. 인물 자체를 게임에 추가한 작업은 아니다. 전체 편집 프롬프트는 `generation-prompt.json`, 결과는 `original-atlas.png`다.

스이세이는 오각별·초승달 받침 대신 둥근 청색 혜성 머리와 우상향하는 세 갈래 꼬리로 바꿨다. [팬마크 목록의 ☄️](https://www.oshimark.com/hololive)를 형태 참고로 삼았다. 특정 플랫폼 이모지 이미지 파일을 그대로 복사한 것은 아니다.

메라는 화로와 붉은 구조물을 제거했다. 사용자 이미지에서 읽히는 청록색·흰색 중심, 연보라색 말리는 꼬리, 작은 부유 불씨를 사용해 둥근 도깨비불로 재구성했다.

`scripts/import-holo-altars04.py`는 해당 두 칸만 가져온다. 나머지 20개 PNG는 altars03과 바이트가 같은지 검사한다. `changed-preview.png`는 실제 32×32 게임 타일을 6배 확대했고 `native-preview.png`는 전체를 4배 확대했다. 파일 경로·해시는 `manifest.json`에 있다.
