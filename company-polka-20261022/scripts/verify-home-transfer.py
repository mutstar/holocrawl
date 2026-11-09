"""Verify a fresh extracted home handoff without executing archived instructions."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'HOME_HANDOFF_MANIFEST.json').read_text(encoding='utf-8'))
for i,v in enumerate(manifest['files'],1):
    p=(root/v['path']).resolve()
    assert p.is_relative_to(root) and p.is_file(),v['path']
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    assert p.stat().st_size==v['bytes'] and h.hexdigest().upper()==v['sha256'],v['path']
    if i%10000==0:print(f'Checked {i}/{len(manifest["files"])}',flush=True)
print(f'PASS: {len(manifest["files"])} files match the handoff SHA256 manifest.')
