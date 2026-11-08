"""Export one fresh, facility-free early city floor through the native builder."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=None)
parser.add_argument('--attempt', type=int, default=1)
args = parser.parse_args()
seed = args.seed if args.seed is not None else secrets.randbelow(900000000) + 100000000
assert 0 <= seed < 2**53
source = root / 'engine/upstream/crawl-ref/source'
run = root / (f'analysis/native-city-random82-{seed}' + (f'-attempt{args.attempt}' if args.attempt > 1 else ''))
run.mkdir(parents=True, exist_ok=False)
plan = {'seed': seed, 'depth': 1, 'facility': False, 'nativeBuilder': True,
        'wallArtRevision': json.loads((source / 'holo34-wall78.json').read_text())['artRevision'],
        'scope': 'One complete random early floor for wall art review.'}
(run / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
settings = run / 'test-init.txt'
settings.write_text(f'save_dir = {(run / "saves").as_posix()}/\nmorgue_dir = {(run / "morgue").as_posix()}/\n')
env = os.environ.copy()
env['HOLOCRAWL_CITY77'] = '1'
env['HOLOCRAWL_CITY_REVIEW_SEED'] = str(seed)
env.pop('HOLOCRAWL_STREET01_MAP', None)
with (run / 'builddb.log').open('wb') as log:
    subprocess.run([str(source / 'crawl.exe'), '-headless', '-dir', str(source),
                    '-rc', str(settings), '-builddb'], cwd=source, env=env,
                   stdout=log, stderr=subprocess.STDOUT, timeout=120, check=True)
command = [str(source / 'crawl.exe'), '-headless', '-dir', str(source), '-rc', str(settings),
           '-script', 'holo_city77', run.as_posix()]
with (run / 'native.log').open('wb') as log:
    subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                   timeout=120, check=True)
validation = json.loads((run / 'validation.json').read_text())
assert validation['status'] == 'passed' and validation['seed'] == seed
data_file = run / f'map-{seed}-1.json'
data = json.loads(data_file.read_text())
assert data['facility'] is None and data['origin'] is None
assert data['width'] == 80 and data['height'] == 70
validation['binarySha256'] = hashlib.sha256((source / 'crawl.exe').read_bytes()).hexdigest()
validation['mapSha256'] = hashlib.sha256(data_file.read_bytes()).hexdigest()
validation['scope'] = plan['scope']
(run / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
preview = root / 'preview/city-random82'
(preview / 'assets').mkdir(parents=True, exist_ok=True)
shutil.copy2(data_file, preview / 'map.json')
for name in ['floor', 'wall', 'feat']:
    shutil.copy2(source / f'dat/tiles/{name}.png', preview / f'assets/{name}.png')
(preview / 'manifest.json').write_text(json.dumps({**plan, 'validation': str(run.relative_to(root)),
    'binarySha256': validation['binarySha256'], 'mapSha256': validation['mapSha256']}, indent=2) + '\n')
print(json.dumps({'seed': seed, 'output': str(run), 'preview': 'city-random82/'}))
