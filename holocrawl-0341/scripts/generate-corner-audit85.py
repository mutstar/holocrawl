"""Generate a frozen random cohort without changing the current review map."""
from pathlib import Path
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import time

root = Path(__file__).resolve().parents[1]
source = root / 'engine/upstream/crawl-ref/source'
run = root / 'analysis/native-corner-audit85'
run.mkdir(parents=True, exist_ok=False)
preview = root / 'preview/wall-audit85'
(preview / 'maps').mkdir(parents=True, exist_ok=True)
(preview / 'assets').mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = {'executable': source / 'crawl.exe', 'atlas': source / 'dat/tiles/wall.png',
          'renderer': root / 'preview/city-batch22/wall-corners84.js'}
hashes = {key: sha(path) for key, path in inputs.items()}
seeds = secrets.SystemRandom().sample(range(100000000, 2000000000), 128)
plan = {'seeds': seeds, 'floors': 128, 'depth': 1, 'facility': False,
        'artRevision': 84, 'inputSha256': hashes,
        'scope': 'New native early city floors plus a separate exhaustive corner audit; no gameplay balance claims.'}
(run / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
settings = run / 'test-init.txt'
settings.write_text(f'save_dir = {(run / "saves").as_posix()}/\nmorgue_dir = {(run / "morgue").as_posix()}/\n')
env = os.environ.copy()
env['HOLOCRAWL_CITY77'] = '1'
env.pop('HOLOCRAWL_STREET01_MAP', None)
env.pop('HOLOCRAWL_CITY_REVIEW_SEED', None)
with (run / 'builddb.log').open('wb') as log:
    subprocess.run([str(source / 'crawl.exe'), '-headless', '-dir', str(source),
                    '-rc', str(settings), '-builddb'], cwd=source, env=env,
                   stdout=log, stderr=subprocess.STDOUT, timeout=120, check=True)
start = time.monotonic()
entries = []
for index, seed in enumerate(seeds):
    target = run / 'raw' / str(seed)
    target.mkdir(parents=True, exist_ok=False)
    current = env.copy()
    current['HOLOCRAWL_CITY_REVIEW_SEED'] = str(seed)
    with (target / 'native.log').open('wb') as log:
        subprocess.run([str(source / 'crawl.exe'), '-headless', '-dir', str(source),
                        '-rc', str(settings), '-script', 'holo_city77', target.as_posix()],
                       cwd=source, env=current, stdout=log, stderr=subprocess.STDOUT,
                       timeout=120, check=True)
    validation = json.loads((target / 'validation.json').read_text())
    assert validation['status'] == 'passed' and validation['seed'] == seed
    assert validation['facility'] is False and validation['connected']
    file = target / f'map-{seed}-1.json'
    data = json.loads(file.read_text())
    assert data['facility'] is None and data['origin'] is None
    assert data['width'] == 80 and data['height'] == 70
    shutil.copy2(file, preview / 'maps' / file.name)
    entries.append({'seed': seed, 'file': f'maps/{file.name}', 'sha256': sha(file),
                    'geometrySha256': hashlib.sha256(json.dumps(data['rows'],separators=(',',':')).encode()).hexdigest()})
    (run / 'state.json').write_text(json.dumps({'status': 'running', 'completed': len(entries),
        'scheduled': len(seeds), 'elapsedSeconds': round(time.monotonic() - start, 2)}, indent=2))
    if len(entries) % 16 == 0:
        print(f'Generated {len(entries)}/{len(seeds)} native random floors.', flush=True)
assert hashes == {key: sha(path) for key, path in inputs.items()}, 'Frozen input changed during generation'
assert len({entry['geometrySha256'] for entry in entries}) == len(seeds), 'Duplicate floor geometry'
for name in ['floor', 'wall', 'feat']:
    shutil.copy2(source / f'dat/tiles/{name}.png', preview / f'assets/{name}.png')
manifest = {'maps': entries, 'wallArtRevision': 84, 'inputSha256': hashes,
            'source': '128 newly generated native city D:1 floors, facilities excluded for wall review.'}
(preview / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
result = {'status': 'passed', 'nativeFloors': len(entries), 'uniqueSeeds': len(set(seeds)),
          'uniqueMaps': len({entry['geometrySha256'] for entry in entries}), 'allConnected': True,
          'allFacilityFree': True, 'frozenInputsUnchanged': True,
          'elapsedSeconds': round(time.monotonic() - start, 2)}
(run / 'generation-validation.json').write_text(json.dumps(result, indent=2) + '\n')
(run / 'state.json').write_text(json.dumps({**result, 'completed': len(entries), 'scheduled': len(seeds)}, indent=2))
print(json.dumps(result), flush=True)
