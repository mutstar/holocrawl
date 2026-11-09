# 최신 집 인계: 2026-11-04 CITY_EXPLORE03

최신 실행은 최상위 OPEN_HOME_EXPLORER.cmd. 먼저 START_HOME_2026-11-04.md를 읽는다.
현재:0.34.1 D:1 브라우저 직접탐험, 확정 원본좌우반전계단, 벽장식4종, 벽가굿즈, 배송상자2~3개 파괴/드롭/습득/저장.
아래 오래된 문서·실행 경로는 기록이며 최신 안내보다 우선하지 않는다.

---

# 집 코덱스에서 이어가기

2026-10-19 저장. 사용자 뭇별 요청으로 회사 PC 실행을 정지했다. 사용자에게 신마다 보고하거나 매번 확인받을 필요는 없다. 단, 지금은 저장 요청을 완료한 상태이며 재개는 다음 사용자 요청에 따른다.

## 저장된 내용

- HOLOCRAWL_DESIGN.md: 승인된 22신 컨셉·상세 수치 및 조정안.
- engine/patches/holocrawl-engine.patch: DCSS 0.24.0 기반 수정 소스 전체. 신규 holo-batch 파일도 포함한다.
- scripts, analysis: 빌드·전투 실행·검사·집계 코드, 검증된 노엘/소피아 데이터 및 최신 검증 근거.
- runtime/results, runtime/logs, runtime/reports: 완료·개발·중단 기록과 각 패치/기획서 스냅샷. superseded/v1/04 개발 기록을 최종 결과로 섞지 않는다.
- CHECKPOINT_MANIFEST.json: ZIP 안 모든 작업 파일의 크기와 SHA256. 기존 과거 ZIP도 함께 보존한다.

재다운로드/재빌드 가능한 engine/crawl, .toolchain, runtime/bin 및 Git 내부 DB는 ZIP에서 제외했다. 수정 코드는 위 패치에 전부 들어 있다. 새 PC bootstrap 전체 과정은 아직 그 PC에서 실행 검증하지 않았다.

## 확인된 현재 상태

22신의 고정 조우용 전투 코어를 연결했다. 최신 05 검사에서 빌드별 552개씩 정·역순 결과가 일치했다(총 1,656 비교). 기존 노엘 48개와 소피아 72개 샘플도 재현됐다. 노엘/소피아의 기존 대규모 검증본은 유지된다.

현재 v2 본 실행 부분 기록은 87,137줄이며 완성 샤드는 없다. 목표는 1,000시드 × 8상황 × 23종류 × 3빌드 = 552,000조우. 중단에 따른 native exit -1/controller exit 1은 사용자 요청으로 정지한 결과다. 아직 최종 22신 승률표·552,000조우 감사 결과가 없다. runtime/reports/batch-smoke-05는 생성기 확인용 소표본이다.

일반 신앙 UI, 신앙 수급/징벌, 캠페인·저장 통합, 장비 선물 등은 미구현이다. 시간 틱은 native 몬스터 단계 후의 현재 위치로 처리하며 긴 행동 안의 중간 위치를 재구성하지 않는다. 자세한 범위는 analysis/native/batch/VALIDATION_SCOPE.md를 따른다.

## 새 PC 환경 복구

ZIP을 풀고 프로젝트 폴더에서 PowerShell을 연다. Git과 네트워크가 필요하다. 다음 명령은 이어서 작업하라는 요청을 받은 뒤 실행한다.

```powershell
./scripts/bootstrap-engine.ps1
./scripts/build-engine.ps1
```

bootstrap은 engine/upstream.json의 고정 커밋과 필요한 submodule을 받고 로컬 패치를 적용한다. engine/toolchain.json에 툴체인 출처와 체크섬이 있다. 이 회사 PC에서 소스 빌드와 native 실행은 확인했다.

## 검증 재개 순서 (다음 코덱스용)

1. 현재 상태와 제외 목록을 읽는다: analysis/native/batch/job_state.json, development_exclusions.json, saved_progress.json. 소스 패치 해시는 `19D47E5C764F8E5247484B55D55A2E36945E85BE6FCC5AE3D4D2F9DDC87F018A`다. 수치를 임의 변경하지 않는다.
2. 새 PC에서 재빌드한 바이너리는 기존 바이너리와 해시가 다를 수 있다. 부분 JSONL은 보존하고 기존 이름에 덮어쓰거나 완성으로 표시하지 않는다. 전투 중간부터 이어쓰기 기능은 없다.
3. 각 빌드 melee/ranged/magic에 대해 `./scripts/check-batch-replays.ps1 -Build melee -Version home01` 형식으로 새 정·역순 검사 이름을 사용한다. 이 명령을 빌드별로 실행한다. 기존 05 결과를 덮어쓰지 않는다.
4. 새 본 실행 버전 v3를 사용한다. 빌드별 head/tail 두 작업, 총 6개를 실행할 수 있다. 예: `./scripts/run-batch-shards.ps1 -Build melee -Prefix native-head-v3 -Shards 2 -TrialsPerShard 250 -SeedStart 1000`, tail은 Prefix native-tail-v3 및 SeedStart 1500. ranged/magic도 동일하게 실행한다. 모든 작업의 소스/기획서/빌드 해시를 동결하고 작업 중 수정·재빌드하지 않는다.
5. 시작 전에 job_state.json의 기존 v2 상태를 별도 파일에 보존하고 v3 새 작업 상태를 만든다. 새 빌드/소스/기획서 해시, replayVersion home01, 6개 작업과 실제 종료 코드를 기록한다. 현재 상태의 stopped를 임의로 complete로 바꾸지 않는다. analysis/batch_progress.py는 v2 이름만 세므로 v3용으로 수정하거나 새 버전 도구를 만든다.
6. 전 샤드 정상 종료 및 무결성 확인 후 `./scripts/finalize-batch.ps1 -Version v3 -ReplayVersion home01`. 이 스크립트는 job_state의 모든 작업 complete/exitCode0, 일치하는 동결 해시, 완전한 12샤드, 샘플 재현 및 기존 노엘·소피아 전체 근접 기준군 대조를 요구한다. 미완료 상태에서 통과하도록 우회하지 않는다.
7. 최종 552,000조우 감사·보고서가 완료되면 현재 상태 문서와 핸드오프 ZIP을 갱신한다. 고정 조우의 자동 행동 결과라는 범위를 함께 보고한다.

## 새 대화에 보낼 메시지

“이 ZIP을 풀고 CONTINUE_HERE.md, HOME_RESUME.md, HOLOCRAWL_DESIGN.md를 읽어줘. 저장된 22신 전투 코어 구현을 바탕으로 미완료된 실제 DCSS 0.24 전투 검증을 이어가자. 과거 결정은 다시 묻지 말고 신별 중간 보고 없이 계속 진행해. 부분 기록을 최종 승률로 쓰지 말고 전체 검사와 보고서를 완료해줘.”
