"""Require overlapping fixed encounters to be independent of batch/order."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('first', type=Path)
parser.add_argument('second', type=Path)
parser.add_argument('--combat-only', action='store_true', help='Compare combat outcomes/resources while allowing schema/scope/metrics additions')
args = parser.parse_args()

def load(path):
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    keyed = {(r.get('build','melee'),r['scenario'], r['seed'], r['god']): r for r in records}
    assert len(keyed) == len(records), f'Duplicate records in {path}'
    return keyed

first, second = load(args.first), load(args.second)
overlap = first.keys() & second.keys()
assert overlap, 'No overlapping trials'
combat_fields=('outcome','hp','max_hp','mp','piety','aut','actions')
different = [key for key in overlap if
    (any(first[key][field]!=second[key][field] for field in combat_fields) if args.combat_only else first[key]!=second[key])]
assert not different, f'{len(different)} order/batch-dependent trials; first mismatches: {different[:5]}'
print(f'{len(overlap)} overlapping trials match exactly, including HP, resources and elapsed aut.')
