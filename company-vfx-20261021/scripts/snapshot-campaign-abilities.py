"""Freeze campaign powers/income proof and the complete delta from balance01."""
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'analysis/native/campaign-abilities01'
RUN = FOLDER / 'native16'
SOURCE = ROOT / 'engine/campaign-crawl/crawl-ref/source'
BASE = ROOT / 'engine/balance-crawl/crawl-ref/source'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


manifest = read(RUN / 'manifest.json')
proofs = ['validation.json', 'reload.json', 'membership.json',
          'membership.json.reload.json']
for name in proofs:
    assert read(RUN / name)['status'] == 'passed', name
assert read(RUN / 'validation.json')['noelSupplies']
assert read(RUN / 'reload.json')['nextWorldStepExact']
assert read(RUN / 'membership.json')['nativePlayerTagRoundtrips'] == 176
regression = FOLDER / 'combat-regression03.validation.json'
assert read(regression)['status'] == 'passed'
assert read(regression)['exactRows'] == 322
assert read(regression)['binarySha256'] == manifest['binarySha256']
assert sha(RUN / 'abilities-engine.exe') == manifest['binarySha256']
assert sha(SOURCE / 'crawl.exe') == manifest['buildSha256']

snapshot = FOLDER / 'source_snapshot-r2'
patch = ROOT / 'engine/patches/campaign-abilities01-r2-from-balance01.patch'
assert not snapshot.exists() and not patch.exists(), 'Preserve existing snapshots'
names = []
lines = []
for file in sorted(SOURCE.iterdir()):
    if file.suffix not in ('.cc', '.h') and file.name != 'Makefile.obj':
        continue
    if file.name in ('build.h', 'compflag.h'):
        continue
    original = BASE / file.name
    before = original.read_text(encoding='utf-8').splitlines(keepends=True) if original.exists() else []
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
logs = FOLDER / 'build-logs'
logs.mkdir(exist_ok=True)
for file in ROOT.glob('campaign-abilities-*.log'):
    shutil.copy2(file, logs / file.name)

status_file = ROOT / 'engine/campaign_status.json'
previous = FOLDER / 'previous-worship01-status.json'
if not previous.exists():
    shutil.copy2(status_file, previous)
state = dict(
    version='campaign-abilities01', revision=2, phase='normal-powers-income-save-verified',
    savedAtUtc=datetime.now(timezone.utc).isoformat(),
    sourceDirectory='engine/campaign-crawl/crawl-ref/source',
    originalBalanceSourcePreserved=True,
    baseBalancePatchSha256='12EB0A3291D0A1478A74372E862DC66A42BD1B124E5964D2A6F2BC7D3BDBAB78',
    incrementalPatch=str(patch.relative_to(ROOT)).replace('\\', '/'),
    incrementalPatchSha256=sha(patch),
    sourceSha256={name: sha(SOURCE / name) for name in names},
    buildSha256=manifest['buildSha256'], binarySha256=manifest['binarySha256'],
    validation=[str((RUN / name).relative_to(ROOT)).replace('\\', '/') for name in proofs],
    combatRegression=str(regression.relative_to(ROOT)).replace('\\', '/'),
    normalCombatAbilitiesConnected=True, pietyIncomeConnected=True,
    nativeCoreEffectPersistenceConnected=True, noelSuppliesConnected=True,
    invocationsTrainingConnected=True, holoWrathDeliveryConnected=False,
    nativeCampaignClearRatesValidated=False,
    limits=['Controlled fixtures are not full dungeon clear-rate tests.',
            'Native post-monster ticks sample current positions; long actions do not reconstruct intermediate positions.',
            'God-specific wrath delivery/resolution, art/music and extended ordinary-play QA remain.',
            'Corrupted-altar purification requires a world feature that is not implemented.'],
    next='Implement god-specific wrath delivery/resolution, then broader ordinary dungeon play/level-transition QA.')
status_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(FOLDER / 'checkpoint-r2.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
excluded = dict(
    native01='Harness compared unsaved RNG debug call counts; changed to native serialized RNG state.',
    native02='Fixed Korone manual punch inheriting an automatic-policy restriction.',
    native03='Harness used the real-skill flag when checking the temporary Noel skill bonus.',
    native04='Stopped the harness waiting for stat selection after a monster with artificially inflated maxHP granted excess XP.',
    native05='Harness used a single 3000-aut native action; replaced it with normal 10-aut steps.',
    native06='GDB identified derived hp_max missing after a raw tag restore; the harness now runs native calc_hp.',
    native07='Intermediate pass before boundary, supplies and training coverage.',
    native08='Ordinary movement exposed a missing native visit ledger in the battle fixture; initialized normal floor-entry metadata.',
    native09='Harness expected 30 drunkenness to decay in five ticks; corrected to six 20-aut ticks.',
    native11='Intermediate pass before final training integration.',
    native12='Intermediate pass before final training integration.',
    native14='Final code passed; superseded by native15 bundling membership checks on the exact same binary.',
    native15='Prior checkpoint; r2 adds the explicit blood-sublimation HP-cost conduct check.',
    finalRun='native16', finalRegression='combat-regression03',
    note='Compile failures are preserved in build logs; failed runs were not edited into passes.')
(FOLDER / 'development_exclusions-r2.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(status='saved', files=len(names), patch=state['incrementalPatch'],
                     sha256=state['binarySha256']), indent=2))
