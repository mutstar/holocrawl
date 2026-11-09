"""Summarize native DCSS trial records. Timeouts remain a separate outcome."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from statistics import mean

parser = argparse.ArgumentParser()
parser.add_argument('input',type=Path)
args = parser.parse_args()
records = [json.loads(line) for line in args.input.read_text(encoding='utf-8').splitlines() if line.strip()]
assert records, 'No trials were recorded'
manifest_path = args.input.with_suffix('.manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig')) if manifest_path.exists() else None
if manifest and 'scenarios' in manifest:
    assert all(r.get('build','melee')==manifest.get('build','melee') for r in records), 'Mixed or incorrect character builds'
    expected = {(scenario, seed, god)
        for scenario in manifest['scenarios']
        for seed in range(manifest['seedStart'], manifest['seedStart'] + manifest['trialsPerCase'])
        for god in manifest['variants']}
    actual = {(r['scenario'], r['seed'], r['god']) for r in records}
    assert actual == expected, f'Incomplete or unexpected batch: missing={len(expected-actual)}, extra={len(actual-expected)}'
groups = defaultdict(list)
unique = set()
paired = defaultdict(dict)
for row in records:
    key = row['scenario'],row['seed'],row['god']
    assert key not in unique, ('Duplicate trial',key)
    unique.add(key)
    assert row['outcome'] in ('win','loss','timeout','banished')
    assert row['outcome'] != 'loss' or row['hp'] <= 0, 'Loss recorded without actual engine HP depletion'
    if 'effects' in row:
        assert all(value>=0 for value in row['effects'].values()), 'Negative ability metrics'
        if row['god'] in ('no_god','noel_v2'):
            assert not any(row['effects'].values()), 'Sopia effect leaked into reference variant'
        if row['god']=='sopia_ring':
            assert all(row['effects'][key]==0 for key in ('field_casts','field_ticks','field_hits','pull_attempts','pulls','big_casts','detonations')), 'Field/big-bang leaked into ring-only variant'
    groups[row['scenario'],row['god']].append(row)
    paired[row['scenario'],row['seed']][row['god']] = row

def wilson(wins,n):
    z=1.95996398454
    p=wins/n
    center=(p+z*z/(2*n))/(1+z*z/n)
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0,center-radius),min(1,center+radius)]

summary=[]
for (scenario,god),rows in sorted(groups.items()):
    wins=sum(r['outcome']=='win' for r in rows)
    summary.append({
        'scenario':scenario,'god':god,'trials':len(rows),'wins':wins,
        'losses':sum(r['outcome']=='loss' for r in rows),
        'banishments':sum(r['outcome']=='banished' for r in rows),
        'timeouts':sum(r['outcome']=='timeout' for r in rows),
        'win_rate':wins/len(rows),'win_rate_wilson95':wilson(wins,len(rows)),
        'mean_survivor_hp':mean([r['hp'] for r in rows if r['outcome']=='win']) if wins else None,
        'mean_aut':mean(r['aut'] for r in rows),
        'mean_mp':mean(r['mp'] for r in rows),
        'mean_piety':mean(r['piety'] for r in rows),
        'mean_effects':{key:mean(r['effects'][key] for r in rows) for key in rows[0].get('effects',{})},
    })

for (scenario,seed),variants in paired.items():
    expected_variants=set(manifest['variants']) if manifest else {'no_god','noel_v1','noel_v2'}
    assert set(variants)==expected_variants, ('Incomplete seed pairing',scenario,seed)
    if not scenario.startswith('late_') and {'noel_v1','noel_v2'}<=set(variants):
        before,after=variants['noel_v1'],variants['noel_v2']
        assert all(before[k]==after[k] for k in ('outcome','hp','mp','piety','aut','actions')), 'Noel commander adjustment leaked into early/mid stages'
    if scenario.startswith('early_') and {'sopia_ring','sopia_full'}<=set(variants):
        ring,full=variants['sopia_ring'],variants['sopia_full']
        assert all(ring[k]==full[k] for k in ('outcome','hp','mp','piety','aut','actions','effects')), 'Locked Sopia abilities affected early fixtures'

comparisons=[]
for scenario in sorted({scenario for scenario,seed in paired}):
    seeds=[variants for (name,seed),variants in paired.items() if name==scenario]
    for before,after in [('no_god','noel_v2'),('noel_v1','noel_v2'),('no_god','sopia_full'),('noel_v2','sopia_full'),('sopia_ring','sopia_full')]:
        if before not in seeds[0] or after not in seeds[0]:
            continue
        differences=[int(p[after]['outcome']=='win')-int(p[before]['outcome']=='win') for p in seeds]
        n=len(differences)
        delta=mean(differences)
        variance=sum((d-delta)**2 for d in differences)/(n-1) if n>1 else None
        # With no observed variation, a zero-width Wald interval is misleading.
        radius=1.95996398454*math.sqrt(variance/n) if variance is not None and variance>0 else None
        comparisons.append({
            'scenario':scenario,'before':before,'after':after,'paired_seeds':n,
            'before_only_wins':sum(d==-1 for d in differences),
            'after_only_wins':sum(d==1 for d in differences),
            'both_win':sum(p[before]['outcome']==p[after]['outcome']=='win' for p in seeds),
            'win_rate_difference':delta,
            'paired_difference_95_normal': [max(-1,delta-radius),min(1,delta+radius)] if radius is not None else None,
        })

output=args.input.with_suffix('.summary.json')
output.write_text(json.dumps({'scope':records[0]['scope'],'trials':len(records),
    'pairing_verified':True,'summary':summary,'paired_comparisons':comparisons},ensure_ascii=False,indent=2),encoding='utf-8')
for row in summary:
    lo,hi=row['win_rate_wilson95']
    print(f"{row['scenario']:24} {row['god']:10} {row['wins']:5}/{row['trials']:<5} "
          f"{row['win_rate']:6.1%} [{lo:.1%},{hi:.1%}] banished={row['banishments']} timeout={row['timeouts']} aut={row['mean_aut']:.1f}")
print(output)
