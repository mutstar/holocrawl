"""Save a portable, checksummed project checkpoint without build caches."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
import zipfile

root = Path(__file__).resolve().parents[1]
stamp = datetime.now(timezone.utc).isoformat()
def read_json(path):
    return json.loads((root / path).read_text(encoding='utf-8-sig'))
def write_json(path, value):
    (root / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest().upper()

progress = json.loads(subprocess.check_output([__import__('sys').executable, str(root / 'analysis/batch_progress.py')]))
write_json('analysis/native/batch/saved_progress.json', progress)
state = read_json('analysis/native/batch/job_state.json')
assert digest(root / 'engine/patches/holocrawl-engine.patch') == state['sourcePatchSha256']
state.update(phase='saved_at_user_request', savedAtUtc=stamp, retainedPartialRecords=progress['records'], finalDatasetComplete=False,
             stopReason='User requested saving all work to continue on home Codex.',
             resumePolicy='Partial shards are preserved, not resumable mid-encounter. Rebuild on home machine, use fresh cohort/replay names, freeze hashes, and rerun incomplete cohorts before finalization.')
for job in state['jobs']:
    job.update(status='stopped_at_user_request', exitCode=1, nativeExitCode=-1, intentionalStop=True)
write_json('analysis/native/batch/job_state.json', state)
status = read_json('engine/implementation_status.json')
status.update(phase='saved-checkpoint-all-gods-validation-incomplete',
              current_module='All 22 combat cores connected; native fixture checks and 1,656 forward/reverse comparisons passed. Large v2 cohorts intentionally stopped for home handoff.',
              checkpoint_saved_at_utc=stamp, partial_v2_encounters=progress['records'], full_22_god_win_rates_available=False)
write_json('engine/implementation_status.json', status)
registry = read_json('engine/batch_registry.json')
registry['checkpoint_status'] = 'saved; large all-god validation incomplete'
write_json('engine/batch_registry.json', registry)

intro = f'''# 홀로죽 이어가기 — 집 코덱스용 최신 저장본

> **최신 상태: 사용자 요청으로 실행을 중단하고 저장했다.** 현재 실행 중인 작업은 없다. 22신 전투 코어 구현 및 native 동작 검사, 근접/원거리/주문 정·역순 **1,656개 비교 일치**까지 완료했다. v2 대규모 검증은 목표 552,000조우 중 **{progress['records']:,}줄의 부분 기록**을 보존했다. 부분 파일은 완성된 데이터나 확정 승률로 사용하지 않는다. 노엘 24,000조우·소피아 32,000조우의 기존 검증본은 별도로 보존되어 있다.

집에서는 ZIP을 작업 폴더에 풀고 **HOME_RESUME.md**부터 읽는다. 기획서, 수정 소스 전체 패치, 실행/분석 스크립트, 원본 결과와 로그, 검증 근거를 포함했다. 재생성 가능한 원본 엔진 체크아웃·툴체인·컴파일 바이너리는 제외했으며 bootstrap으로 복구한다. 최신 소스 패치 SHA256: `{state['sourcePatchSha256']}`.

**다음 코덱스에게:** 먼저 HOME_RESUME.md와 현재 job_state.json, VALIDATION_SCOPE.md를 확인한다. 아래의 ‘실행 중’, ‘04 검사 예정’ 등은 과거 기록이며 최신 상태가 아니다. 사용자 요청은 집에서 이어갈 수 있도록 저장하는 것이었으므로 자동으로 테스트를 시작하지 말고 다음 사용자 요청을 따른다. 이어서 진행하라고 요청받으면 기존 결정을 다시 묻지 말고, 새 빌드/새 실행 이름으로 미완료 검증을 계속한다. 22신의 일반 플레이 통합이나 전체 밸런스 검증이 끝났다고 말하지 않는다.

---

## 이전 진행 기록 (최신 상태는 위와 HOME_RESUME.md 우선)

'''
continue_path = root / 'CONTINUE_HERE.md'
continue_path.write_text(intro + continue_path.read_text(encoding='utf-8-sig'), encoding='utf-8')
readme = root / 'engine/README.md'
text = readme.read_text(encoding='utf-8-sig').replace('The 1,000-seed all-god cohorts are currently running;', 'The 1,000-seed all-god cohorts were intentionally stopped for a home handoff;')
readme.write_text(text, encoding='utf-8')

home = f'''# 집 코덱스에서 이어가기

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

현재 v2 본 실행 부분 기록은 {progress['records']:,}줄이며 완성 샤드는 없다. 목표는 1,000시드 × 8상황 × 23종류 × 3빌드 = 552,000조우. 중단에 따른 native exit -1/controller exit 1은 사용자 요청으로 정지한 결과다. 아직 최종 22신 승률표·552,000조우 감사 결과가 없다. runtime/reports/batch-smoke-05는 생성기 확인용 소표본이다.

일반 신앙 UI, 신앙 수급/징벌, 캠페인·저장 통합, 장비 선물 등은 미구현이다. 시간 틱은 native 몬스터 단계 후의 현재 위치로 처리하며 긴 행동 안의 중간 위치를 재구성하지 않는다. 자세한 범위는 analysis/native/batch/VALIDATION_SCOPE.md를 따른다.

## 새 PC 환경 복구

ZIP을 풀고 프로젝트 폴더에서 PowerShell을 연다. Git과 네트워크가 필요하다. 다음 명령은 이어서 작업하라는 요청을 받은 뒤 실행한다.

```powershell
./scripts/bootstrap-engine.ps1
./scripts/build-engine.ps1
```

bootstrap은 engine/upstream.json의 고정 커밋과 필요한 submodule을 받고 로컬 패치를 적용한다. engine/toolchain.json에 툴체인 출처와 체크섬이 있다. 이 회사 PC에서 소스 빌드와 native 실행은 확인했다.

## 검증 재개 순서 (다음 코덱스용)

1. 현재 상태와 제외 목록을 읽는다: analysis/native/batch/job_state.json, development_exclusions.json, saved_progress.json. 소스 패치 해시는 `{state['sourcePatchSha256']}`다. 수치를 임의 변경하지 않는다.
2. 새 PC에서 재빌드한 바이너리는 기존 바이너리와 해시가 다를 수 있다. 부분 JSONL은 보존하고 기존 이름에 덮어쓰거나 완성으로 표시하지 않는다. 전투 중간부터 이어쓰기 기능은 없다.
3. 각 빌드 melee/ranged/magic에 대해 `./scripts/check-batch-replays.ps1 -Build melee -Version home01` 형식으로 새 정·역순 검사 이름을 사용한다. 이 명령을 빌드별로 실행한다. 기존 05 결과를 덮어쓰지 않는다.
4. 새 본 실행 버전 v3를 사용한다. 빌드별 head/tail 두 작업, 총 6개를 실행할 수 있다. 예: `./scripts/run-batch-shards.ps1 -Build melee -Prefix native-head-v3 -Shards 2 -TrialsPerShard 250 -SeedStart 1000`, tail은 Prefix native-tail-v3 및 SeedStart 1500. ranged/magic도 동일하게 실행한다. 모든 작업의 소스/기획서/빌드 해시를 동결하고 작업 중 수정·재빌드하지 않는다.
5. 시작 전에 job_state.json의 기존 v2 상태를 별도 파일에 보존하고 v3 새 작업 상태를 만든다. 새 빌드/소스/기획서 해시, replayVersion home01, 6개 작업과 실제 종료 코드를 기록한다. 현재 상태의 stopped를 임의로 complete로 바꾸지 않는다. analysis/batch_progress.py는 v2 이름만 세므로 v3용으로 수정하거나 새 버전 도구를 만든다.
6. 전 샤드 정상 종료 및 무결성 확인 후 `./scripts/finalize-batch.ps1 -Version v3 -ReplayVersion home01`. 이 스크립트는 job_state의 모든 작업 complete/exitCode0, 일치하는 동결 해시, 완전한 12샤드, 샘플 재현 및 기존 노엘·소피아 전체 근접 기준군 대조를 요구한다. 미완료 상태에서 통과하도록 우회하지 않는다.
7. 최종 552,000조우 감사·보고서가 완료되면 현재 상태 문서와 핸드오프 ZIP을 갱신한다. 고정 조우의 자동 행동 결과라는 범위를 함께 보고한다.

## 새 대화에 보낼 메시지

“이 ZIP을 풀고 CONTINUE_HERE.md, HOME_RESUME.md, HOLOCRAWL_DESIGN.md를 읽어줘. 저장된 22신 전투 코어 구현을 바탕으로 미완료된 실제 DCSS 0.24 전투 검증을 이어가자. 과거 결정은 다시 묻지 말고 신별 중간 보고 없이 계속 진행해. 부분 기록을 최종 승률로 쓰지 말고 전체 검사와 보고서를 완료해줘.”
'''
(root / 'HOME_RESUME.md').write_text(home, encoding='utf-8')

files = set()
for path in root.iterdir():
    if path.is_file() and (path.suffix in {'.md', '.zip', '.json'} or path.name == '.gitignore'):
        if not path.name.startswith('HOLOCRAWL_ALL_GODS_CHECKPOINT_') and path.name != 'CHECKPOINT_MANIFEST.json':
            files.add(path)
for dirname in ('scripts', 'analysis', 'engine', 'runtime'):
    for path in (root / dirname).rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if '__pycache__' in rel.parts or (dirname == 'engine' and len(rel.parts) > 1 and rel.parts[1] == 'crawl') or (dirname == 'runtime' and len(rel.parts) > 1 and rel.parts[1] == 'bin'):
            continue
        files.add(path)
manifest = dict(savedAtUtc=stamp, sourcePatchSha256=state['sourcePatchSha256'], partialProgress=progress,
                excludedRebuildable=['.git', '.toolchain', 'engine/crawl', 'runtime/bin'],
                files=[dict(path=p.relative_to(root).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(files)])
write_json('CHECKPOINT_MANIFEST.json', manifest)
files.add(root / 'CHECKPOINT_MANIFEST.json')
archive = root / 'HOLOCRAWL_ALL_GODS_CHECKPOINT_2026-10-19.zip'
if archive.exists():
    raise RuntimeError('Refusing to overwrite an existing checkpoint ZIP')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for path in sorted(files):
        output.write(path, path.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as saved:
    assert saved.testzip() is None
    for entry in manifest['files']:
        assert hashlib.sha256(saved.read(entry['path'])).hexdigest().upper() == entry['sha256'], entry['path']
verification = dict(archive=archive.name, bytes=archive.stat().st_size, sha256=digest(archive),
                    files=len(files), allFileChecksumsVerified=True, zipCrcVerified=True, savedAtUtc=stamp)
write_json('HOLOCRAWL_ALL_GODS_CHECKPOINT_2026-10-19.verification.json', verification)
print(json.dumps(verification, indent=2))
