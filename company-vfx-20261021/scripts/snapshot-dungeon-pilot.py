"""Freeze audited real-dungeon pilots without replacing earlier checkpoints."""
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'analysis/native/dungeon-pilot01'
SOURCE = ROOT / 'engine/campaign-crawl/crawl-ref/source'
BASE = ROOT / 'engine/balance-crawl/crawl-ref/source'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


audit = read(FOLDER / 'validation.json')
assert audit['status'] == 'passed' and audit['cases'] == 81
active = read(FOLDER / 'active-save-validation.json')
assert active['status']=='passed' and active['cases']==3
reg_dir = ROOT / 'analysis/native/campaign-abilities01/dungeon-regression03'
reg_manifest = read(reg_dir / 'manifest.json')
for name in ['validation.json', 'reload.json', 'membership.json', 'membership.json.reload.json']:
    assert read(reg_dir / name)['status'] == 'passed', name
fixed = read(FOLDER / 'fixed-combat-regression03.validation.json')
assert fixed['exactRows'] == 322 and fixed['status'] == 'passed'
assert fixed['binarySha256'] == reg_manifest['binarySha256']
assert sha(SOURCE / 'crawl.exe') == reg_manifest['buildSha256'] == active['compiledBuildSha256']
assert read(ROOT / 'analysis/native/campaign-abilities01/dungeon-regression02/manifest.json')['buildSha256']==audit['compiledBuildSha256']
assert read(FOLDER / 'fixed-combat-regression02.validation.json')['status']=='passed'

snapshot = FOLDER / 'source_snapshot'
patch = ROOT / 'engine/patches/dungeon-pilot01-from-balance01.patch'
assert not snapshot.exists() and not patch.exists(), 'Preserve prior snapshots'
names, lines = [], []
for file in sorted(SOURCE.iterdir()):
    if file.suffix not in ('.cc', '.h') and file.name != 'Makefile.obj':
        continue
    if file.name in ('build.h', 'compflag.h'):
        continue
    before_path = BASE / file.name
    before = before_path.read_text(encoding='utf-8').splitlines(keepends=True) if before_path.exists() else []
    after = file.read_text(encoding='utf-8').splitlines(keepends=True)
    if before == after:
        continue
    names.append(file.name)
    path = 'crawl-ref/source/' + file.name
    lines.append(f'diff --git a/{path} b/{path}\n')
    if not before:
        lines.append('new file mode 100644\n')
    lines.extend(difflib.unified_diff(before, after,
                 fromfile='a/' + path if before else '/dev/null', tofile='b/' + path))
patch.write_text(''.join(lines), encoding='utf-8', newline='\n')
git = shutil.which('git') or str(ROOT / '.toolchain/msys64/usr/bin/git.exe')
subprocess.run([git, 'apply', '--check', '--ignore-space-change', str(patch)],
               cwd=BASE.parents[1], check=True)
snapshot.mkdir()
for name in names:
    shutil.copy2(SOURCE / name, snapshot / name)
(FOLDER / 'build-logs').mkdir(exist_ok=True)
for file in ROOT.glob('dungeon-pilot-*.log'):
    shutil.copy2(file, FOLDER / 'build-logs' / file.name)
shutil.copy2(ROOT / 'engine/campaign_status.json', FOLDER / 'previous-campaign-status.json')
state = dict(version='dungeon-pilot01', phase='real-dungeon-D1-pilot-audited',
    savedAtUtc=datetime.now(timezone.utc).isoformat(),
    sourceDirectory='engine/campaign-crawl/crawl-ref/source',
    originalBalanceSourcePreserved=True,
    incrementalPatch=str(patch.relative_to(ROOT)).replace('\\', '/'),
    incrementalPatchSha256=sha(patch), sourceSha256={n: sha(SOURCE / n) for n in names},
    buildSha256=reg_manifest['buildSha256'], pilotMainBuildSha256=audit['compiledBuildSha256'],
    activeSaveValidation='analysis/native/dungeon-pilot01/active-save-validation.json',
    pilotValidation='analysis/native/dungeon-pilot01/validation.json',
    pilotPanels=['analysis/native/dungeon-pilot01/all22-03', 'analysis/native/dungeon-pilot01/natural-02', 'analysis/native/dungeon-pilot01/active-save02'],
    fixtureRegression='analysis/native/campaign-abilities01/dungeon-regression03',
    combatRegression='analysis/native/dungeon-pilot01/fixed-combat-regression03.validation.json',
    normalCombatAbilitiesConnected=True, pietyIncomeConnected=True,
    nativeCoreEffectPersistenceConnected=True, noelSuppliesConnected=True,
    invocationsTrainingConnected=True, holoWrathDeliveryConnected=False,
    realDungeonD1PilotCases=84, primaryPilotCases=81, activeStateSaveCases=3, nativeCampaignClearRatesValidated=False,
    next='Improve equipment, retreat and consumable policies; widen seeds/builds and ability coverage before balance inference. God-specific wrath remains separate.')
(FOLDER / 'checkpoint.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(ROOT / 'engine/campaign_status.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
exclusions = dict(
    smoke01='Harness changed save/cache directory after map-index loading; corrected via startup rc save_dir.',
    smoke02='Harness omitted native baseline action time; zero-time movement trials excluded.',
    smoke03='Earlier policy waited for unreachable enemies behind transparent walls; interrupted at restore confirmation / timeout.',
    smoke04='Inactive no-god core scratch state and UI RNG were incorrectly compared as persistent gameplay state.',
    smoke05='Earlier RNG comparison was superseded. Upstream get_generator ignores its argument; final active-save audit selects each stream explicitly and compares before native restart initialization.',
    smoke06='Successful preliminary 7-case pilot, before death-source and blocked-ally policy refinements.',
    all22_01='Stopped superseded policy. Fubuki image could block the bot; raw partial cases retained.',
    all22_02='Stopped superseded policy. Final driver prioritizes native stair delays before rejected-move fallback.',
    natural_01='Completed intermediate natural panel; superseded by natural-02 on the final build.',
    active_save01='Stronger active-state checkpoint exposed upstream viewwindow gameplay RNG draws. GDB confirmed original safety/pathfinding code; all-stream selection in the checker was also corrected.',
    finalAssigned='all22-03', finalNatural='natural-02', finalActiveSave='active-save02',
    rule='No failed/interrupted pilot is included in the final 81-case audit; raw logs and saves were preserved.')
(FOLDER / 'development_exclusions.json').write_text(json.dumps(exclusions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

assigned = [json.loads(s) for s in (FOLDER / 'all22-03/results.jsonl').read_text().splitlines()]
natural = [json.loads(s) for s in (FOLDER / 'natural-02/results.jsonl').read_text().splitlines()]
special = [json.loads(s) for s in (FOLDER / 'active-save02/results.jsonl').read_text().splitlines()]
god_names = dict(no_god='무신앙', suisei='스이세이', miko='미코', aki='아키', fubuki='후부키',
    ayame='아야메', choco='초코', korone='코로네', okayu='오카유', pekora='페코라', noel='노엘',
    watame='와타메', towa='토와', lamy='라미', polka='폴카', koyori='코요리', lui='루이',
    raden='라덴', hajime='하지메', su='스우', vivi='비비', sopia='소피아', mela='메라')


def cell(row):
    return f"D:{row['maxDepth']} " + {'death': '사망', 'target_reached': '도달',
        'action_limit': '행동한도', 'policy_stalled': '정체', 'left_main_dungeon': '다른 분기'}[row['outcome']]


table = ['| 신 | 시드101 | 시드202 | 시드303 | 권능 발동 합계 |', '|---|---|---|---|---:|']
for god, label in god_names.items():
    own = [r for r in assigned if r['requestedGod'] == god]
    table.append('| ' + label + ' | ' + ' | '.join(cell(next(r for r in own if r['seed'] == seed)) for seed in [101, 202, 303])
                 + f" | {sum(r['powers'] for r in own)} |")
native_table = ['| 시드 | 선택 신 | 결과 | 실제 가입 | 권능 발동 |', '|---:|---|---|---|---:|']
for row in natural:
    native_table.append(f"| {row['seed']} | {god_names[row['requestedGod']]} | {cell(row)} | {god_names.get(row['joinedGod'], '무신앙' if row['requestedGod']=='no_god' else '가입 전')} | {row['powers']} |")
outcomes = dict(Counter(r['outcome'] for r in assigned + natural + special))
text = f'''# 실제 D:1 진행 검사 — dungeon-pilot01

원본 DCSS 0.24의 새 캐릭터·던전 생성부터 출발한 **기본81개 진행과 활성 상태 저장3개, 합계84개**를 감사했다. D:5 도달을 목표로 했으며, 게임 전체 클리어율·플레이어 승률·22신 밸런스 확정 검사가 아니다. 이번 봇은 모두 D:1~D:4에서 사망했고 D:5 도달은0이다.

## 조건과 확인 범위

- 시드101/202/303, 인간 전사·롱소드·원본 시작 장비/기술/HP18·MP1·XL1. 이후 경험치·레벨업·STR 선택·회복·음식·시간은 원본 규칙이다. HP/MP/XP/신앙을 보충하거나 몬스터를 시험장으로 교체하지 않았다.
- 기본 69개 비교 진행은 무신앙 대조군+22신 ×3시드. 비교용 신 지정만 D:1에서 수행하고 원래 지형을 복원했다. 가입 신앙15를 사용했으며, 이 모드를 자연 제단 발견으로 부르지 않는다.
- 12개 정상 진행은 무신앙/노엘/루이/소피아 ×3시드. 무신앙으로 출발하여 실제 발견한 제단에서 일반 가입 메뉴를 이용했다. 가입 전 사망도 그대로 기록했다.
- 봇은 탐색한 지도와 보이는 적을 사용한다. 전체 지형 해시는 동일 시드 D:1 생성 대조용으로만 기록한다. 보이지 않는 지형을 길찾기에 쓰지 않는다.
- 원본 이동/근접/문/일반 음식·알려진 물약/신별 수동 권능/휴식/계단 지연을 사용한다. 첫 D:2 도달 후 실제 계단으로 D:1→D:2→D:1→D:2 왕복을 시도한다.
- 250행동을 생존한 진행은 실제 캐릭터·층 저장 후 프로세스를 종료하고 새 프로세스에서 이어 갔다. 기본81개는 권능·플레이어·전투 난수 상태를 확인했다. 별도 강화 검사3개는 까마귀/폭탄/고리가 활성인 순간 저장하고, 원본 재개 초기화 전에42개 RNG 스트림 전체와 저장된 권능 상태가 정확히 복원됐는지 확인했다. 초기화 뒤 권능·까마귀 MID/HP/위치를 검사했다. 원본 위험도 표시의 경로찾기가 전투 난수를 소비하는 현상을 GDB로 확인했으며 이 난수를 임의로 되돌리지 않았다.
- 테스트 빌드의 자동 부활을 막고 첫 실제 사망을 기록했다. 사망 후 HP 추가 변경도 막았다. 원본 신 enum·전투 밸런스 수식은 바꾸지 않았다.

## 감사 결과

기본81개 패널과 강화된 저장 검사3개는 검사 계측 버전이 다르다. 각 빌드 해시를 별도로 보존했다. 변경은 RNG 관찰과 검사뿐이며 두 빌드 모두 원래 전투322행 일치 검사를 통과했다. 활성 상태3개는 `active-save-validation.json`과 `active-save02`를 따른다. 까마귀1마리·설치 폭탄·고리가 실제로 활성인 저장임을 별도 감사했다.

- 84개 최종 진행 결과: `{json.dumps(outcomes, ensure_ascii=False)}`.
- 별도 새 프로세스 복원 {audit['freshProcessResumes']+3}개, 실제 계단 왕복 {audit['staircaseRoundtrips']+3}개, 권능 발동 {audit['powers']+sum(r['powers'] for r in special)}회, 정상 제단 가입 {audit['naturalJoins']}개.
- 같은 시드의 시작 D:1 지형이 모두 일치했다. 무신앙 대조군은 두 모드에서 동일 결과를 재현했다.
- 최신 빌드에서도 22신 대표 권능58회·저장 상태22개·숭배 저장176개와 기존 balance01 사격322행 전체 필드 일치 검사를 재통과했다.
- 감사 원문: `validation.json`. 비교 원문: `all22-03/results.jsonl`. 정상 진행 원문: `natural-02/results.jsonl`. 각 하위 폴더에 이벤트·로그·체크포인트가 있다. 생존/사망 결과는 엔진 동작 결과이며, `completed`를 던전 클리어 성공으로 해석하지 않는다.

## D:1 신 지정 비교 — 순위가 아님

동일 근접 봇에 최소한의 신별 사용 정책을 붙인 파일럿이다. 서로 다른 RNG 경로·자원 소비·신별 정책 미숙의 영향이 크다. 세 시드로 강약을 단정하거나 수치를 조정하지 않았다. D:5 도달은 D:5 입구 도착이며 D:5 전층 정리가 아니다.

''' + '\n'.join(table) + '''

## 실제 제단을 찾는 진행

''' + '\n'.join(native_table) + f'''

## 한계와 다음 검사

현재 봇은 장비 교체·강적 회피·퇴각·미확인 소모품 판단이 단순하다. 기본81개 패널의 실제 사망 원인은 `{json.dumps(audit['deathSources'], ensure_ascii=False)}`다. 초반 사망으로 해금되지 않은 권능은 이 진행에서 검증됐다고 주장하지 않는다. 3성·5성·장비 보급의 전수 캠페인 검증은 별도로 확장해야 한다.

후부키 환영에 막혀 동일 이동을 반복하던 봇 경로를 고쳤고, 계단 지연을 실패 이동과 구분했다. 지도 캐시 경로·기본 행동시간·재개 확인창·UI 난수 비교 문제는 검사 도구 문제였으며 실패/중단 자료는 보존했다. 최종 패널에는 포함하지 않았다.

다음은 장비·퇴각·소모품 정책을 개선한 뒤 더 많은 시드/빌드에서 해금·권능별 도달 범위를 넓히는 작업이다. 신별 실제 징벌과 전체 던전 클리어 검증은 아직 남아 있다.

## 재현

PowerShell 콘솔에서 프로젝트 루트로 이동한다. 새 실행 이름을 써서 기존 결과를 보존한다.

```powershell
./.toolchain/msys64/mingw64/bin/python.exe -X utf8 analysis/run_dungeon_pilot.py --name fresh-pilot --panel smoke --seeds 101
./.toolchain/msys64/mingw64/bin/python.exe -X utf8 analysis/run_dungeon_pilot.py --name fresh-all --panel all --seeds 101,202,303
```

일반 플레이 세이브는 `runtime/campaign01/saves`, 검사 세이브·지도 캐시는 각 실행 폴더의 `saves`에 분리된다. 최신 소스 해시·누적 패치·상태는 `engine/campaign_status.json`과 이 폴더의 `checkpoint.json`이다.
'''
(FOLDER / 'RESULTS_D1_PILOT_KO.md').write_text(text, encoding='utf-8')
print(json.dumps(dict(status='saved', sourceFiles=len(names), cases=84,
                     report='analysis/native/dungeon-pilot01/RESULTS_D1_PILOT_KO.md'), ensure_ascii=False))
