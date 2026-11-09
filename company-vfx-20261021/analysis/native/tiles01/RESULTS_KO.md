# 도트·효과 연결 — tiles01 / 2026-10-20

첫 도트 패스를 실제 SDL 타일 실행본에 연결했다. 시작 파일은 프로젝트 루트의 `PLAY_HOLOCRAWL.cmd`, 또는 `./scripts/start-campaign-tiles.ps1`다. 기존 문자 실행은 `./scripts/start-campaign.ps1`로 유지한다. 두 버전은 `runtime/campaign01/saves`를 공유하며, **문자 버전 저장을 그래픽 버전에서 복원하는 검사까지 통과했다.** 실제 개인 저장을 테스트용으로 열거나 덮어쓰지 않았다.

## 구현 범위

[도트 원화·프롬프트 기록](../../../assets/holocrawl/tiles01/README.md)에 32×32 RGBA 파일 64개와 생성 원본·프롬프트를 보관했다. 22신 문양, 장미·여우·까마귀·검객·사냥개, 당근 폭탄, 16종의 2프레임 효과, 예비 도트 4종이다.

신 선택/설명 메뉴에 문양을 붙였다. 실제 가입한 제단은 그 층의 `env.properties`에 신 ID를 저장해서 문양과 설명을 유지한다. 원래 제단·가입 규칙·단축키는 유지한다. 타일 번호를 저장하지 않으며, 이전 저장에는 마이그레이션이 필요 없다.

소환물은 기존 네이티브 몬스터의 전투·이동 판정을 그대로 사용하고 그림만 바꾼다. 기존 저장의 이름과 징벌 속성에서도 새 그림을 찾는다. 적대/우호 표시는 네이티브 표시를 유지한다.

성역·정원·물·중력·고리·점액·지원 사격 영역은 실제 저장된 좌표·반경·기한·벽 판정에서 바닥 표시를 읽는다. 폭탄·혜성·배교 예고는 황색 경고, 남은 10 aut 이내는 빨간 경고로 표시한다. 적과 바닥을 가리지 않는 투명 중심 테두리를 사용한다. 시야 밖 능력 범위는 그리지 않는다.

권능 사용과 폭발에 짧은 2프레임 반짝임을 연결했다. 각 프레임은 35ms 요청이며 사용자 지연 설정을 따른다. 전투 상태·턴·타이머를 진행시키지 않고 기존 SDL 화면 버퍼만 다시 그린다. 지속 영역의 프레임은 저장된 월드 시간에 따라 바뀐다. 층 이동 시 임시 반짝임은 정리한다. 문자 버전에서는 이 그래픽 경로를 실행하지 않는다.

이번 패스는 **문양·소환물·범위 표시·공통 반짝임**이다. 22명 캐릭터 전신/얼굴, 플레이어 외형 변경, 모든 권능의 개별 긴 애니메이션은 아직 남아 있다. 신 밸런스 수치와 봇 정책은 바꾸지 않았다.

## 확인한 검사

- `analysis/native/campaign-abilities01/tiles01-final01/`: 문자 실행본에서 22신 권능 58회, 일반 처치 신앙, 숭배 직렬화 176회, 활성 상태 저장·새 프로세스 진행·계단·부채·보급 등 기존 기능 검사 통과.
- 같은 실행의 `tiles-model.json`: 22신의 시각 조회가 MP·신앙·저장 속성·전투 코어·RNG를 바꾸지 않음. 활성 상태의 표시 좌표가 저장 왕복 22회 뒤 일치. 성역·고리·당근·경고 긴급 전환·계단 정리 확인.
- `analysis/native/tiles01/sdl-fixture01/`: **실제 SDL 실행본에서도** 같은 22신 검사·숭배 176회·저장 복원·다음 월드 진행 일치를 확인. 문자 버전의 저장도 불러와 숭배 기록·신앙·RNG를 확인했다.
- `analysis/native/tiles01/capture-final/`: 실제 SDL OpenGL 프레임버퍼 6장. 성역, 고리/중력장, 당근/황색 경고, 빨간 긴급 경고, 까마귀 6개, 22신 제단을 확인했다. 테스트용 고정 방·배치이며 실제 던전 플레이 결과가 아니다.
- `asset-render-validation.json`: 64개 PNG의 32×32·RGBA·투명도·해시·타일 체크아웃 일치, 최종 6장 서로 다른 화면과 제단 22개·성역 25칸을 확인했다.
- `fixed-combat.validation.json`: 기존 balance01 전투 결과 **322개 정확히 일치**.

초기 캡처에서 테스트용 게임 화면 초기화 누락과 SDL 뷰포트 좌표 변환 오류를 발견해 수정했다. `capture01`~`capture04`는 보존한 중간 기록이며 해당 폴더의 `review.json`을 따른다. **최종 화면은 `capture-final`만 사용한다.**

기능·표시·회귀 검사다. 전체 던전 클리어율이나 최종 신 밸런스 검증이 아니다. 사용자 결정대로 추가 봇 검사는 재개하지 않았다.

## 실행과 빌드

`PLAY_HOLOCRAWL.cmd`를 열면 약 12.8MB의 `runtime/tiles01/HoloCrawl.exe`를 사용한다. `a` 권능, `^` 신앙, 그 화면의 `?` 설명. 기본 타일 배율은 48px 표시이며 `runtime/campaign01/tiles.rc`에서 바꿀 수 있다. 원본 타일은 32px이고 최근접 표시다. 제단 문양은 가입한 제단부터 연결된다.

그래픽 체크아웃 `engine/tiles-crawl/crawl-ref/source`는 문자 소스와 분리하여 빌드 산출물이 섞이지 않는다. 원본 구현은 `engine/campaign-crawl/crawl-ref/source`가 기준이다. `scripts/prepare-tiles-source.py`로 동기화하고 `scripts/build-campaign-tiles.sh`로 빌드한다. 성공하면 경량 실행 파일도 갱신한다. 첫 그래픽 의존성 설치는 프로젝트 MSYS2에서 `scripts/setup-tiles-dependencies.sh`를 사용한다. SDL2·SDL2_image·FreeType·libpng·pkgconf는 `.toolchain`에 설치했다. Windows 기본 Consolas/Segoe UI 폰트를 참조하며 폰트 파일을 배포본에 복사하지 않는다.

재현 검사: `./scripts/test-campaign-abilities.ps1 -Name 새이름`, `./scripts/test-campaign-tiles.ps1 -Name 새이름 -ConsoleFixture 문자검사폴더`. PNG 검사·미리보기 재생성은 Pillow가 있는 Python에서 `scripts/import-holo-tiles.py`, `analysis/native/tiles01/verify-assets.py`를 사용한다. 생성 프롬프트는 기록용이며 가져오기 작업이 이미지 생성을 다시 호출하지 않는다.

## 저장과 다음 단계

상태는 `engine/campaign_status.json`, 해시·소스/PNG 스냅샷은 이 폴더의 `checkpoint.json`과 `source_snapshot/`에 있다. 네이티브 타일 실행 파일과 생성 아틀라스도 별도로 고정했다. 소스 전용 패치는 PNG를 담지 않으므로 `rltiles/holo` 원본 파일과 함께 사용한다.

다음은 실제 플레이에서 배율·명도·경고 가독성을 확인하고, 원하면 캐릭터 외형과 권능별 전용 애니메이션으로 넓히는 작업이다. 별도 요청 전에는 봇 승률 작업을 다시 시작하지 않는다.
