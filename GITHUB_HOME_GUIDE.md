# 2026-11-09 최신 재개 안내

회사·집 모두 `mutstar/holocrawl`의 `main`에서 이어갑니다. 로컬 수정을 먼저 보관한 뒤 `git pull --ff-only`, `OPEN_LATEST_PREVIEW.cmd`를 실행하세요. 최신은 `city-street124`(1~3층 실제 지도 위 배치), `city-market124`(4~7층 브라우저 랜덤 생성), `facility-exteriors124`(시설9곳 외벽)입니다. `CONTINUE_HERE.md` 상단을 먼저 읽으세요.

이번 동기화에는 이전 커밋 이후124번까지의 설계·소스·도트·미리보기·검증 자료와 최신 네이티브107 patch/overlay가 포함됩니다. 승인한 벽121과 구조물122는 유지했습니다. 네이티브107 실행본과 브라우저124 변경을 혼동하지 않도록 구분합니다. 브라우저 검토는 별도 컴파일 없이 가능합니다.

2026-11-09 전체 동기화로 `company-polka-20261022`, `company-vfx-20261021`의22신 소스·아트·미리보기·검증 기록도 포함합니다. `LEGACY_GODS_ARCHIVE.md`에서 위치와 실행 범위를 확인하세요. 재빌드 가능한 실행파일, 임시 세이브·캐시, 인증정보와 중복 ZIP은 제외합니다. 아래 최초 업로드·옛 버전 안내는 당시 기록이므로 반복 실행하지 않습니다. 특히 과거 폴더를 업로드하지 않는다는 옛 설명은 이번 전체 동기화로 대체합니다.

# 2026-11-06 재개 안내 기록

회사·집 모두 기존 `mutstar/holocrawl`의 `main`에서 이어갑니다. 로컬 수정이 없음을 확인한 뒤 `git pull --ff-only`, `OPEN_LATEST_PREVIEW.cmd`를 실행하세요. 최신은 `holox-floor54`, 승인된 극장은 `theater-vault36`입니다. 가장 먼저 `CONTINUE_HERE.md` 상단을 읽으세요.

아래 2026-11-05의 master/커밋0개/최초 업로드 절차는 **당시 감사 기록**입니다. 이미 존재하는 저장소에서 초기화·remote추가·최초생성 절차를 반복하지 않습니다.

# HoloCrawl — 비공개 GitHub 저장소로 집에서 이어가기

점검일: 2026-11-05. 비공개 원격은 https://github.com/mutstar/holocrawl 이다. 아래 최초 생성·업로드 절차는 점검 기록이며, 이미 연결된 회사PC에서 반복 실행하지 않는다. 집에서는3번 clone절차부터 진행한다.

## 확인된 Git 상태

- 바깥 `HoloCrawl` 저장소: `master`, 커밋0개, 추적 파일0개, remote없음. 기존 커밋과 비교하는 diff는 없으며 파일들이 미추적 상태다.
- 실제 엔진은 별도 저장소 `holocrawl-0341/engine/upstream`에 있다.
- 엔진 브랜치 `codex/holocrawl-0341`, 기준 태그 `0.34.1`, HEAD `1eebc1a2892e1c89776a0d7a10691f8dac8d9796`.
- 엔진 tracked수정8개, 새 파일102개(소스7개+타일95개). tracked diff는8파일/158줄 추가다.
- 엔진 origin은 공식 `https://github.com/crawl/crawl.git`이다. 여기에 우리 작업을 push하는 것이 아니다.

## 보안·용량 점검

- 전체 작업공간 텍스트239,746개에서 알려진 GitHub/OpenAI/AWS/Google/Slack 키, 개인키 헤더, URL내 인증정보 형식을 검사했다. 해당 서명 매치0건.
- password대입 후보2건은 중복된 upstream `ssh_guide.txt` 접속 안내문에 해당한다. 개인 API키로 판정한 것은 아니며, 엔진 checkout원본은 업로드에서 제외한다.
- 최신 프로젝트 업로드 후보는 별도로 검사했다. 텍스트4,837개에서 키 서명 및 의심 문자열 대입 후보0건. 엔진 변경 파일110개도 별도 서명 검사했다.
- 모든 비밀이 없음을 증명하는 검사는 아니다. Git메타데이터, ZIP내부, 바이너리, 8MiB초과 파일, 의존성·툴체인 디렉터리는 내용검사에서 제외했다.
- 최초 미추적 파일은 약503,990개로, 회사 작업본·중복 exports가 대부분이었다. 통째로 `git add .` 하지 않는다.
- 원본 엔진 checkout에 약440MiB짜리 `crawl.exe`가 있다. GitHub 일반 Git의100MiB 파일 제한에 걸리므로 제외한다. 예전 ZIP에는 약1.3GiB 파일도 있다.
- `.gitignore`에 환경파일·개인키·인증파일·브라우저 인증상태·로그·캐시·ZIP·최신 runtime·중첩 엔진 checkout 제외 규칙을 추가했다. 파일을 삭제하지 않았다.
- 아래 명시적 업로드 범위에는 현재 검사에서50MiB이상 단일 파일이 없었다. 이미지 원화를 포함하므로 최초 clone/push는 수백MiB 규모다.

정량 결과: `holocrawl-0341/design/GIT_AUDIT_2026-11-05.json`.

## 중첩 엔진 변경분 보존

`holocrawl-0341/migration/engine0341-git-handoff-20261105/`에 다음을 준비했다.

- `tracked.patch`: 기준0.34.1 대비 tracked8파일의 변경.
- `overlay/`: 미추적102파일의 원본 바이트.
- `manifest.json`: 기준commit, 파일목록, SHA-256, 복원검증 결과.

임시 별도 저장소에 기준 파일을 꺼내 patch와 overlay를 적용한 뒤 현재 원본과 비교했다. 복원 통과. tracked텍스트3개는 CRLF/LF 차이만 있었으며 정규화한 내용은 같았다. 원본 엔진의 index·브랜치·파일은 변경하지 않았다.

이것은 **2026-11-05 점검 시점의 스냅샷**이다. 엔진을 나중에 수정하면 push 전에 스냅샷도 다시 내보내야 한다. checkout자체가 바깥 Git에서 제외되어 있으므로 자동으로 동기화되지는 않는다.

## 1. GitHub에서 빈 비공개 저장소 만들기

1. 본인 GitHub에 로그인하고 https://github.com/new 를 연다.
2. Owner를 본인 계정으로, 이름을 예: `holocrawl`로 설정한다.
3. **Private**를 선택한다.
4. README / .gitignore / License 자동 생성은 모두 끈 빈 저장소로 만든다. 프로젝트의 기존 라이선스 파일은 그대로 유지한다.
5. HTTPS주소를 복사한다. 주소에 비밀번호나 PAT를 넣지 않는다.

현재 회사 PC의 PATH에는 GitHub CLI(`gh`)가 없으므로 아래는 기본 Git 기준이다. push시 Git Credential Manager의 브라우저 로그인으로 인증할 수 있다. 토큰을 파일이나 Git remote URL에 저장하지 않는다.

## 2. 회사 PC에서 선택한 파일만 커밋하기

아래 명령은 아직 실행하지 않았다. `mutstar`를 본인 계정명으로 바꾼다.

```powershell
Set-Location 'C:\Users\071staff\Documents\ChatGPT\HoloCrawl'

git add -- .gitignore GITHUB_HOME_GUIDE.md CONTINUE_HERE.md HOLOCRAWL_DESIGN.md holocrawl-0341 scripts OPEN_HOME_EXPLORER.cmd OPEN_HOME_EXPLORER.ps1 RUN_HOME_CHECKS.ps1 START_HOME_2026-11-04.md

git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
```

확인사항: `company-polka-20261022`, `company-vfx-20261021`, ZIP, `.env`, 개인키, `.home-preview`, `holocrawl-0341/runtime`, `holocrawl-0341/engine/upstream`가 staged목록에 없어야 한다. 과거 폴더가 계속 `??`로 보이는 것은 업로드하지 않은 로컬 기록이므로 정상이다. 필요한 옛0.24 소스 일부는 최신 프로젝트의 `migration/legacy024`에도 있다. 과거 폴더 전체가 이 저장소로 옮겨지는 것은 아니다.

staged목록을 확인한 다음:

```powershell
git commit -m "Save HoloCrawl 0.34.1 source, art and 8x8 theater vault"
git branch -M main
git remote add origin https://github.com/mutstar/holocrawl.git
git push -u origin main
```

Git이 사용자 이름/이메일을 요구하면 공개될 커밋 작성자 정보를 이 저장소에만 `git config user.name ...`, `git config user.email ...`로 지정한다. 이메일 공개를 피하려면 GitHub계정에 표시되는 본인의 noreply주소를 쓴다.

GitHub 웹에서 저장소에 **Private** 표시가 있고, 최신 `theater-vault34` 및 엔진 스냅샷이 있는지 확인한다.

공식 참고:

- https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
- https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 3. 집 PC에서 현재 브라우저 작업 이어가기

```powershell
git clone https://github.com/mutstar/holocrawl.git HoloCrawl
Set-Location HoloCrawl
py -3 -m http.server 8798 --bind 127.0.0.1 --directory holocrawl-0341/preview
```

Python을 `python` 명령으로 설치했다면 `py -3` 대신 `python`을 쓴다. 서버가 실행 중인 상태에서:

http://127.0.0.1:8798/theater-vault34/

를 연다. HTML을 `file://`로 바로 열지 않는다. 최신 설명은 최상위 `CONTINUE_HERE.md`부터 읽는다. 예전 `OPEN_HOME_EXPLORER`는 이전1층 화면을 여는 실행기라 현재 극장은 위 주소로 이동해야 한다. 브라우저 미리보기에는 네이티브 엔진·runtime·MSYS2가 필요 없다.

Node검증을 다시 하려면 Node.js/Playwright/Chrome또는Edge가 필요하다. 예:

```powershell
Set-Location holocrawl-0341
$env:HOLOCRAWL_PREVIEW_URL='http://127.0.0.1:8798'
node scripts/check-vault34.cjs
```

## 4. 집에서 네이티브 엔진 소스까지 복원할 때

바깥 HoloCrawl 폴더에서 아래를 실행한다. **대상 `holocrawl-0341/engine/upstream`가 이미 있으면 새로 clone하거나 덮어쓰지 말고 먼저 상태를 확인한다.**

```powershell
$enginePath='holocrawl-0341/engine/upstream'
$snapshotPath=(Resolve-Path 'holocrawl-0341/migration/engine0341-git-handoff-20261105').Path

git clone --branch 0.34.1 --depth 1 https://github.com/crawl/crawl.git $enginePath
git -C $enginePath switch -c codex/holocrawl-0341
git -C $enginePath rev-parse HEAD
# 위 결과가 1eebc1a2892e1c89776a0d7a10691f8dac8d9796 인지 확인
git -C $enginePath apply --check "$snapshotPath/tracked.patch"
# check가 성공한 뒤:
git -C $enginePath apply "$snapshotPath/tracked.patch"
Copy-Item -Path "$snapshotPath/overlay/*" -Destination $enginePath -Recurse -Force
git -C $enginePath status --short
```

필요한 엔진 submodule은 이후 `git -C $enginePath submodule update --init --recursive`로 받는다.

주의: 회사 `BUILD_*.ps1`과 일부 shell빌드 스크립트는 과거 MSYS2위치를 참조한다. 집 PC에서 실제 게임을 빌드하려면 컴파일러·라이브러리·이 경로를 별도로 맞춰야 한다. 소스 복원과 네이티브 빌드 환경 설치는 별개다. `.gitignore`에서 제외한230MiB가량의 runtime은 이 방식으로 내려오지 않는다.

## 이후 회사/집 작업

작업 시작: 깨끗한 상태에서 `git pull --ff-only`.

작업 종료: 변경사항·민감정보 점검 → 필요한 파일만 add → commit → push.

회사와 집에서 같은 파일을 동시에 수정하지 않는 편이 편하다. 비공개 저장소라도 비밀번호·API키는 커밋하지 않는다.
