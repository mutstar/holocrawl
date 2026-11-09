# 홀로돌죽 · HoloCrawl

2026-11-09 최신 검토는 **문 아래·옆 벽선 같은 굵기151**입니다. 임의3px선을없애고실제인접벽회색선4px를높이1:1로복사해두께·명암·색을맞췄습니다.비교`doorfit151/door-review.html`.28문상태원본벽픽셀차이0·48지도·문도트원본동일검사통과.사용자검토대기·네이티브미적용.

2026-11-09: 고정지형을 JP·ID·EN 어디서든 추첨하는 공용 설계로 변경했습니다. 최신 실행기는 `facility-pool131`의 제작 목록·배정 계획을 엽니다. 기존9종과 미제작33종을 구분하며 전체42종 제작이 완료된 상태가 아닙니다. 최근 맵 미술 검토는 아래의130을 보존합니다. 새 공용 정책은 브라우저 설계 단계이고 기존 네이티브107은 아직JP 전용입니다.

Hololive를 주제로 만드는 턴제 던전 프로젝트. 기반 엔진은 DCSS0.34.1입니다. 현재 브라우저 검토본은 **130번 잔향도시8층 낡은 축제장 랜덤 맵**입니다. 포장마차5종과 공용 소품7종을80×70 시드 생성 지형에 배치하고 전체 지도·장소 확대·탐험으로 확인합니다.24개 시드의 연결·비중복·계단 간격·재현성을 검사했습니다. 공통 브라우저 생성기를 확장한 시안이며 네이티브 통합 및9~10층 별도 프로필은 후속 작업입니다. 개별 도트는festival128/129,1~7층 기준 검토본은124입니다. 실제 네이티브 실행본107과 브라우저 미술 검토본은 구분합니다.

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

[축제장 공용 소품7종](http://127.0.0.1:8798/festival129/), [홀로멤 포장마차5종](http://127.0.0.1:8798/festival128/), [벽·초롱 샘플](http://127.0.0.1:8798/festival125/), [1~3층 실제 지도 위 배치](http://127.0.0.1:8798/city-street124/), [4~7층 랜덤 상점가](http://127.0.0.1:8798/city-market124/)를 엽니다.

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
