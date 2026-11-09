# 22신 전체 작업 자료 · 2026-11-09 동기화

집에서 올린 `a627fdc6`(2026-11-09 08:38 KST, 124번까지)을 먼저 fast-forward한 뒤 회사에 남아 있던 자료를 합쳤습니다. 최신 잔향도시 작업은 최상위 `CONTINUE_HERE.md`와 `holocrawl-0341/`에서 이어갑니다.

## 보관 위치

| 위치 | 내용 |
|---|---|
| `holocrawl-0341/` | 현재0.34.1 던전·시야·시설·22신 공통 구조, 최신 네이티브107 복원 자료와 브라우저124 |
| `company-polka-20261022/` | 누적22신 설계,0.24 전투 소스, 승인 도트·GIF·효과 미리보기, 밸런스·실플레이 검증 기록과 초기 도시 작업 |
| `company-vfx-20261021/` | 이전 회사22신 전투·VFX 작업본과 비교 근거 |
| `analysis/` | 초기 신 검증·분석 자료 |
| `engine/patches/holocrawl-engine.patch` | 최초0.24 checkout의 최신 수정분을 내보낸 패치 |
| `CHECKPOINT_MANIFEST.json`, `HOME_RESUME.md`, `review-company-20261021/` | 초기 체크포인트와 이관 기록 |

22신 기능 요약은 `company-polka-20261022/FULLKIT_CORE_INVENTORY.md`, 이후 승인·수정 기록은 같은 폴더의 `CONTINUE_HERE.md`와 `analysis/design/`에 있습니다. 과거 안내문·해시 목록은 당시 스냅샷이며 파일별 생성 시점이 다릅니다.

0.24의 캠페인·타일 엔진 소스는 각 회사 작업본의 `engine/campaign-crawl/crawl-ref/source/`와 `engine/tiles-crawl/crawl-ref/source/`에 있습니다. 두 작업본과 두 엔진의 차이를 보존했습니다.0.34.1의22신 공통 구조와0.24의 실제 전투 구현은 이식 단계가 다릅니다. 특히 비비·소피아·메라 개편의 설계·미리보기와 실제 전투 연결 상태는 기존 기록을 확인해야 합니다.

## 집에서 받기

현재 clone이 있다면 로컬 수정을 먼저 커밋한 뒤 최상위에서 실행합니다.

```powershell
git pull --ff-only
```

최신 도시 미리보기는 `OPEN_LATEST_PREVIEW.cmd`로 엽니다. 예전22신 도트·GIF 검토는 별도 터미널에서 다음 서버를 실행합니다.

```powershell
py -3 -m http.server 8766 --bind 127.0.0.1 --directory company-polka-20261022
```

이후 `http://127.0.0.1:8766/analysis/previews/`에서 신별 검토 폴더를 고릅니다. 브라우저 미리보기에는 네이티브 빌드가 필요하지 않습니다.

실제 게임은 컴파일러·MSYS2·외부 라이브러리를 집PC에 맞춰 빌드해야 합니다.0.34.1은 최상위 `BUILD_CITY107.ps1` 및 `holocrawl-0341/design/NATIVE_PLAY107_REVIEW.md`를,0.24는 회사 작업본의 `scripts/build-campaign-engine.sh`와 `scripts/build-campaign-tiles.sh`를 참고합니다. 옛 스크립트에는 회사 경로가 남아 있습니다.

## Git 보관 범위

소스·설계·도트 원화·PNG·GIF·미리보기·재현 스크립트와 기존 검증 자료를 보관합니다. 같은 내용의 파일은 Git이 내용 단위로 공유합니다.

중복 전달용 ZIP/exports, 실행파일·DLL·컴파일 중간물, 도구체인·의존성 설치본, 개인 인증정보·환경파일, 생성된 게임 DB·캐시·임시 세이브와 로컬 로그는 제외합니다. 원본 파일은 로컬 디스크에 보존합니다. 과거 체크포인트 검증기의 전체 파일 수·runtime 해시는 이 제외 범위 때문에 clone만으로 재현되지 않을 수 있습니다.

이번 작업은 자료 보관·동기화이며 새 전투 기능을 구현하거나 게임 실행을 검증한 작업은 아닙니다. 점검 결과는 `holocrawl-0341/design/GIT_FULL_SYNC_2026-11-09.json`에 기록합니다.
