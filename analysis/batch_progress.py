"""Count complete retained records without loading live JSONL files into memory."""
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]/'runtime'/'results'
rows=[]
for path in sorted(root.glob('native-*-v2-*.jsonl')):
    if not re.fullmatch(r'native-(head|tail)-v2-(melee|ranged|magic)-(01|02)\.jsonl',path.name):
        continue
    with path.open('rb') as stream:
        count=sum(chunk.count(b'\n') for chunk in iter(lambda:stream.read(1024*1024),b''))
    rows.append(dict(run=path.stem,records=count,complete=count==46000))
print(json.dumps(dict(records=sum(r['records'] for r in rows),target=552000,runs=rows),indent=2))
