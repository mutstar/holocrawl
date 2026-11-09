# 혜성·도깨비불·라덴 가면 제단 — altars05

부유하는 상징만으로는 제단처럼 보이지 않는다는 피드백에 따라, 내장 image_gen으로 altars04의 세 칸을 편집했다. 스이세이는 별지도가 있는 남색·은색 석조 제단, 메라는 시메나와·종이 장식·지붕이 있는 자주색 목제 감실로 바꾸되 각자의 혜성·도깨비불 상징은 유지했다. 동일한 원본 제단 위에 아이콘을 얹는 방식이 아니라, 구조와 상징을 포함한 전체 타일을 교체한다.

라덴은 병풍 대신 흰 노멘을 가운데 모신 짙은 녹색·금색 목제 감실로 바꿨다. 실제 사용한 마스크 참고는 [공식 hololive friends with u 상품 이미지](https://shop.hololivepro.com/products/hololivefriendswithu_juufuuteiraden)이며, `raden-mask-product-reference.png`에 저장했다. 얼굴의 흰 바탕·가는 눈·회색 이마점·붉은 입을 참고했다. 별도로 살핀 공식 캐릭터 전신 이미지 2장도 참고 이력으로 보관했지만 생성 도구 입력에는 사용하지 않았다.

`original-atlas.png`가 새 원화이고 `generation-prompt.json`이 전체 프롬프트·입력 경로·출처다. `scripts/import-holo-altars05.py`는 스이세이·라덴·메라만 잘라 32×32 RGBA 타일로 가져온다. 나머지 19개 파일은 altars04와 바이트 단위로 같음을 검사한다. `changed-preview.png`는 해당 세 타일을 최근접 6배 확대했고 `native-preview.png`는 전체 타일을 4배 확대했다. 해시는 `manifest.json`에 있다.
