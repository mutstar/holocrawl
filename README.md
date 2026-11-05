# 홀로돌죽 · HoloCrawl

Hololive를 주제로 만드는 턴제 던전 프로젝트. 기반 엔진은 DCSS0.34.1이며, 현재는 브라우저에서 도시 타일·고정 지형·시야·이동을 검토하고 있습니다.

현재 작업은 **holoX 연구소54의 9×9 고정 지형과 세 가지 층 맵 배치 미리보기**입니다. 검은 장갑 연결 벽·보라색 창·경고띠, 다섯 멤버 시설과 문 없는 비대칭 통로를 검토 중입니다. 최신 입구·좌우 벽 수정은 사용자 피드백을 기다립니다. 적·전투와 실제 네이티브 층 생성기 연결은 추후 진행합니다.

## 회사·집에서 이어가기

```powershell
git clone https://github.com/mutstar/holocrawl.git
Set-Location holocrawl
```

Windows에서 `OPEN_LATEST_PREVIEW.cmd`를 실행합니다. Python3가 필요하며 Codex의 Python도 자동 탐색합니다. 또는:

```powershell
py -3 -m http.server 8798 --bind 127.0.0.1 --directory holocrawl-0341/preview
```

http://127.0.0.1:8798/holox-floor54/ 를 엽니다. `file://`로 직접 열지 않습니다.

다음 작업부터는 이 폴더에서 `git pull --ff-only`로 최신 변경을 받으면 됩니다. 로컬 수정이 남아 있다면 먼저 커밋하거나 별도로 보관합니다.

## 이어받기

- `CONTINUE_HERE.md`: 최신 진행 기록. 위에서부터 읽습니다.
- `holocrawl-0341/design/HOLOX_FLOOR54.md`: 최신 연구소 외관·연결 벽·검증 기록.
- `holocrawl-0341/preview/theater-vault36/`: 승인된 2기생 극장.
- `GITHUB_HOME_GUIDE.md`: 회사/집 Git사용 및 엔진 복원 안내.
- `holocrawl-0341/design/GIT_AUDIT_2026-11-05.json`: 보안 점검 범위와 한계.

## 포함 범위

최신 설계·미리보기·도트 원화·검증 스크립트, 일부0.24 이관 자료, 수정한0.34.1 엔진의 patch와 추가 파일을 포함합니다. 과거 회사 작업본 전체, ZIP, 로컬 인증정보, 컴파일 결과와 runtime은 포함하지 않습니다.

엔진 원본 저장소는 `holocrawl-0341/engine/upstream`에 복원합니다. 현재 변경분은 `holocrawl-0341/migration/engine0341-git-handoff-20261105`에 있으며, 순정0.34.1에 복원 검증했습니다. 이 스냅샷은 자동 갱신되지 않습니다. 엔진 수정 후에는 push전에 새 patch/overlay도 저장해야 합니다.

브라우저 미리보기는 엔진 빌드 없이 실행됩니다. 실제 게임 빌드는 집PC의 컴파일러·MSYS2환경을 별도로 맞춰야 합니다.

DCSS유래 파일의 라이선스는 `LICENSE-DCSS.txt`와 해당 파일의 고지를 참고합니다.
