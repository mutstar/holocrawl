"""Run the native builder and native save/load regressions in an isolated directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=root / 'analysis/native-city77')
parser.add_argument('--executable', type=Path)
arguments = parser.parse_args()
output = arguments.output.resolve()
output.mkdir(parents=True, exist_ok=False)
source = root / 'engine/upstream/crawl-ref/source'
executable = (arguments.executable or source / 'crawl.exe').resolve()
settings = output / 'test-init.txt'
settings.write_text(f'save_dir = {(output / "saves").as_posix()}/\nmorgue_dir = {(output / "morgue").as_posix()}/\n', encoding='utf-8')
environment = os.environ.copy()
environment['HOLOCRAWL_CITY77'] = '1'
environment.pop('HOLOCRAWL_STREET01_MAP', None)
environment.pop('HOLOCRAWL_CITY_REVIEW_SEED', None)
command = [str(executable), '-headless', '-dir', str(source), '-rc', str(settings),
           '-script', 'holo_city77', output.as_posix()]
started = time.monotonic()
with (output / 'builddb.log').open('wb') as log:
    cache = subprocess.run([str(executable), '-headless', '-dir', str(source),
                            '-rc', str(settings), '-builddb'], cwd=source,
                           env=environment, stdout=log, stderr=subprocess.STDOUT,
                           timeout=180)
if cache.returncode:
    raise RuntimeError(f'Native map database failed. See {output / "builddb.log"}')
with (output / 'native.log').open('wb') as log:
    process = subprocess.run(command, cwd=source, env=environment, stdout=log,
                             stderr=subprocess.STDOUT, timeout=600)
if process.returncode:
    raise RuntimeError(f'Native validation failed with {process.returncode}. See {output / "native.log"}')
validation_path = output / 'validation.json'
result = json.loads(validation_path.read_text(encoding='utf-8'))
assert result['status'] == 'passed' and result['nativeFloors'] == 168
assert result['facilitiesCovered'] == 9
result['binarySha256'] = hashlib.sha256(executable.read_bytes()).hexdigest()
result['elapsedSeconds'] = round(time.monotonic() - started, 3)
result['scope'] = 'Native 0.34.1 city prototype generation; combat, loot and campaign progression deferred.'
validation_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2), flush=True)
