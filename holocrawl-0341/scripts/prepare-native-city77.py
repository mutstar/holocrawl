"""Publish audited native floor snapshots and their exact compiled tile atlases."""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
run = root / 'analysis/native-city82-final01'
source = root / 'engine/upstream/crawl-ref/source'
preview = root / 'preview/native-city77'
validation = json.loads((run / 'validation.json').read_text(encoding='utf-8'))
assert validation['status'] == 'passed' and validation['nativeFloors'] == 168
assert validation['nativeLevelSaveRoundtrip'] and validation['placementFailureKeepsPlan']
assert hashlib.sha256((source / 'crawl.exe').read_bytes()).hexdigest() == validation['binarySha256']
(preview / 'maps').mkdir(parents=True, exist_ok=True)
(preview / 'assets').mkdir(exist_ok=True)
seeds = [77001, 77002, 77003]
for seed in seeds:
    used = set()
    for depth in range(1, 15):
        filename = f'map-{seed}-{depth}.json'
        data = json.loads((run / filename).read_text(encoding='utf-8'))
        assert data['seed'] == seed and data['depth'] == depth
        assert len(data['rows']) == data['height'] == 70
        assert all(len(row) == data['width'] == 80 for row in data['rows'])
        assert len(data['floors']) == len(data['features']) == 5600
        assert all(0 <= value < len(data['palette']) for value in data['floors'] + data['features'])
        if data['facility']:
            assert data['facility'] not in used
            used.add(data['facility'])
        shutil.copy2(run / filename, preview / 'maps' / filename)
for atlas in ['floor', 'wall', 'feat']:
    shutil.copy2(source / 'dat/tiles' / f'{atlas}.png', preview / 'assets' / f'{atlas}.png')
manifest = {'engine': 'DCSS 0.34.1', 'seeds': seeds, 'floorsPerSeed': 14,
            'artRevision': 84, 'nativeArtRevision': 84,
            'localArtPreview': 'wall-selection81.json',
            'source': 'Actual native builder and native level save/load snapshots',
            'binarySha256': validation['binarySha256'],
            'nativeValidation': str(run.relative_to(root) / 'validation.json')}
(preview / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('Prepared 42 audited native floors for browser review.')
