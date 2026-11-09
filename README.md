# 홀로돌죽 · HoloCrawl

Hololive를 주제로 만드는 턴제 던전 프로젝트. 기반 엔진은 DCSS0.34.1입니다. 최신 브라우저 검토본은 **124번**이며, 승인한22px 벽과1~7층 거리·상점가 소품, 통로 보호 배치, JP 고정지형9곳의 외벽을 포함합니다. 소품 배치는236개 지도 구조에서416회 검사했고, 시설 문10곳의 열기·진입을 확인했습니다. 실제 네이티브 실행본107과 이후 브라우저 아트·배치 검토본124는 구분합니다.

회사·집에서 이어갈 때는 로컬 수정을 먼저 보관한 뒤 `git pull --ff-only`하고 `OPEN_LATEST_PREVIEW.cmd`를 실행하세요. 다음 작업과 검증 범위는 `CONTINUE_HERE.md` 상단에 있습니다. 브라우저 검토에는 엔진 빌드가 필요하지 않습니다.

잔향도시 4~7층의 고정 지형 미리보기로 [2기생 극장](http://127.0.0.1:8798/theater-vault57/), [holoX 연구소](http://127.0.0.1:8798/holox-floor62/?map=2), [게이머즈 폐역](http://127.0.0.1:8798/gamers-station64/?map=2), [3기생 도타바타 그라운드](http://127.0.0.1:8798/fantasy-ground67/?map=2), [4기생 관람차 광장](http://127.0.0.1:8798/wheel-plaza71/?map=2)이 있습니다. 최신 미리보기에는 페이스 마운틴, 타라후쿠 저니, 네포라보 마트와 DEV_IS 출장소가 추가됐습니다.

## 회사·집에서 이어가기

```powershell
git clone https://github.com/mutstar/holocrawl.git
Set-Location holocrawl
```

Windows에서 `OPEN_LATEST_PREVIEW.cmd`를 실행합니다. Python3가 필요하며 Codex의 Python도 자동 탐색합니다. 또는:

```powershell
py -3 -m http.server 8798 --bind 127.0.0.1 --directory holocrawl-0341/preview
```

[1~3층 실제 지도 위 최신 배치](http://127.0.0.1:8798/city-street124/), [4~7층 랜덤 상점가](http://127.0.0.1:8798/city-market124/), [고정지형9곳 외벽](http://127.0.0.1:8798/facility-exteriors124/)을 엽니다.

다음 작업부터는 이 폴더에서 `git pull --ff-only`로 최신 변경을 받으면 됩니다. 로컬 수정이 남아 있다면 먼저 커밋하거나 별도로 보관합니다.

## 이어받기

- `CONTINUE_HERE.md`: 최신 진행 기록. 위에서부터 읽습니다.
- `holocrawl-0341/design/HOLOX_FLOOR54.md`: 최신 연구소 외관·연결 벽·검증 기록.
- `holocrawl-0341/preview/theater-vault36/`: 승인된 2기생 극장.
- `GITHUB_HOME_GUIDE.md`: 회사/집 Git사용 및 엔진 복원 안내.
- `holocrawl-0341/design/GIT_AUDIT_2026-11-05.json`: 보안 점검 범위와 한계.

## 포함 범위

최신 설계·미리보기·도트 원화·검증 스크립트, 수정한0.34.1 엔진의 patch와 추가 파일에 더해, **22신의0.24 전투 소스·도트·이펙트·검증 기록과 과거 회사 작업본**을 함께 보관합니다. 위치와 복원 범위는 `LEGACY_GODS_ARCHIVE.md`를 확인하세요. ZIP 중복 백업, 로컬 인증정보, 컴파일 결과·runtime·임시 세이브는 제외합니다.

최신 네이티브107 소스 변경분은 `holocrawl-0341/migration/engine0341-play107`의 patch·overlay·해시 목록에 보존되어 있습니다. `BUILD_CITY107.ps1`로 별도 엔진을 복원·빌드하며, 실행·검증·설치 절차는 `holocrawl-0341/design/NATIVE_PLAY107_REVIEW.md`를 확인하세요. `BUILD_CITY.ps1`과 `migration/engine0341-city77`은 이전 엔진 복원용입니다. 실제 실행파일·컴파일 도구·개인 세이브는 Git에 포함하지 않습니다.

브라우저 미리보기는 엔진 빌드 없이 실행됩니다. 실제 게임 빌드는 집PC의 컴파일러·MSYS2환경을 별도로 맞춰야 합니다.

DCSS유래 파일의 라이선스는 `LICENSE-DCSS.txt`와 해당 파일의 고지를 참고합니다.
