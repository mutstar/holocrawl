"""Merge complete, disjoint native trial shards with identical source/build."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
parser.add_argument('inputs', type=Path, nargs='+')
args = parser.parse_args()
manifests = []
records = []
seeds = set()
reference = None
invariant_fields = ('engineCommit','buildBinarySha256','sourcePatchSha256','designSha256',
    'scenarios','variants','explorationTraps','randomSpawns','banishmentPolicy','scope','build')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

for path in args.inputs:
    manifest = json.loads(path.with_suffix('.manifest.json').read_text(encoding='utf-8-sig'))
    if reference is None:
        reference = manifest
    assert all(manifest.get(k) == reference.get(k) for k in invariant_fields), f'Build/fixture mismatch: {path}'
    assert digest(path.with_suffix('.engine.patch')) == manifest['sourcePatchSha256']
    assert digest(path.with_suffix('.design.md')) == manifest['designSha256']
    batch_seeds = set(range(manifest['seedStart'],manifest['seedStart']+manifest['trialsPerCase']))
    assert not seeds & batch_seeds, f'Overlapping seeds: {path}'
    seeds |= batch_seeds
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    keys = {(r['scenario'],r['seed'],r['god']) for r in rows}
    expected = {(scenario,seed,god) for scenario in manifest['scenarios'] for seed in batch_seeds for god in manifest['variants']}
    assert keys == expected and len(keys) == len(rows), f'Incomplete/duplicate shard: {path}'
    records.extend(rows)
    manifests.append({'file':path.name,'records':len(rows),'resultsSha256':digest(path),
        'manifestSha256':digest(path.with_suffix('.manifest.json')),
        'binarySha256':manifest['binarySha256'],'seedStart':manifest['seedStart'],
        'trialsPerCase':manifest['trialsPerCase']})

assert seeds and len(seeds) == max(seeds)-min(seeds)+1, 'Combined seed range must be contiguous'
targets = [args.output,args.output.with_suffix('.manifest.json'),args.output.with_suffix('.engine.patch'),args.output.with_suffix('.design.md')]
assert not any(path.exists() for path in targets), 'Output or sidecar already exists; use a fresh output name'
scenario_order = {name:i for i,name in enumerate(reference['scenarios'])}
variant_order = {name:i for i,name in enumerate(reference['variants'])}
records.sort(key=lambda r:(scenario_order[r['scenario']],r['seed'],variant_order[r['god']]))
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records),encoding='utf-8')
merged = {k:v for k,v in reference.items() if k not in ('binary','binarySha256','results')}
merged.update(trialsPerCase=len(seeds),seedStart=min(seeds),results=str(args.output),sourceRuns=manifests)
args.output.with_suffix('.manifest.json').write_text(json.dumps(merged,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(args.inputs[0].with_suffix('.engine.patch'),args.output.with_suffix('.engine.patch'))
shutil.copyfile(args.inputs[0].with_suffix('.design.md'),args.output.with_suffix('.design.md'))
print(f'Merged {len(records):,} native encounters from {len(manifests)} complete shards; source/build/design hashes match.')
