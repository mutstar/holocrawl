"""Export a complete, restorable native107 patch and overlay from the nested engine."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
engine = root / 'analysis/native-play107-01/engine'
snapshot = root / 'migration/engine0341-play107'
snapshot.mkdir(parents=True, exist_ok=True)
base = subprocess.check_output(['git', '-C', str(engine), 'rev-parse', 'HEAD'], text=True).strip()
assert base == '1eebc1a2892e1c89776a0d7a10691f8dac8d9796'
patch = subprocess.check_output(['git', '-C', str(engine), 'diff', '--binary', 'HEAD'])
(snapshot / 'tracked.patch').write_bytes(patch)
untracked = subprocess.check_output(['git', '-C', str(engine), 'ls-files', '--others', '--exclude-standard', '-z']).decode().split('\0')
files = []
for name in filter(None, untracked):
    assert name.startswith(('crawl-ref/source/holo34-', 'crawl-ref/source/rltiles/holocrawl/',
                            'crawl-ref/source/rltiles/holo-city77.txt', 'crawl-ref/source/rltiles/holo-wall78.txt',
                            'crawl-ref/source/scripts/holo_city77.lua')), name
    target = snapshot / 'overlay' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(engine / name, target)
    files.append({'path': name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
manifest = {'baseTag': '0.34.1', 'baseCommit': base,
            'trackedPatchSha256': hashlib.sha256(patch).hexdigest(),
            'overlay': files, 'restore': 'Apply tracked.patch to the base commit, then copy overlay contents.'}
checks = root.parent / '.home-preview/native107'
checks.mkdir(parents=True, exist_ok=True)
restored = Path(tempfile.mkdtemp(prefix='restore-', dir=checks))
subprocess.run(['git', 'init', '-q', str(restored)], check=True)
modified = subprocess.check_output(['git', '-C', str(engine), 'diff', '--name-only', 'HEAD'], text=True).splitlines()
for name in modified:
    target = restored / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(subprocess.check_output(['git', '-C', str(engine), 'show', f'HEAD:{name}']))
subprocess.run(['git', '-C', str(restored), 'apply', '--check', str(snapshot / 'tracked.patch')], check=True)
subprocess.run(['git', '-C', str(restored), 'apply', str(snapshot / 'tracked.patch')], check=True)
for name in modified:
    assert (restored / name).read_bytes().replace(b'\r\n', b'\n') == (engine / name).read_bytes().replace(b'\r\n', b'\n'), name
for item in files:
    target = restored / item['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot / 'overlay' / item['path'], target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == item['sha256']
manifest['restoreCheck'] = {'status': 'passed', 'trackedFiles': len(modified), 'overlayFiles': len(files)}
(snapshot / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(f'Exported native107 patch and {len(files)} overlay files.')
