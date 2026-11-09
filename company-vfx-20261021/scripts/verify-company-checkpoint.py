"""Verify the transferred project and optionally replay one immutable native sample."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest().upper()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
 manifest=json.loads((ROOT/'COMPANY_CHECKPOINT_MANIFEST.json').read_text(encoding='utf-8'))
 for i,v in enumerate(manifest['files'],1):
  p=(ROOT/v['path']).resolve();assert p.is_relative_to(ROOT),v['path']
  assert p.is_file() and p.stat().st_size==v['bytes'] and digest(p)==v['sha256'],f'Integrity mismatch: {v["path"]}'
  if i%5000==0:print(f'Checked {i}/{len(manifest["files"])} files',flush=True)
 print(f'PASS: {len(manifest["files"])} transferred files; all SHA256 match.',flush=True)
 if not a.smoke:return
 result=ROOT/'runtime/company-portability'/uuid.uuid4().hex/'ranged.jsonl';result.parent.mkdir(parents=True)
 subprocess.run([sys.executable,'-X','utf8',str(ROOT/'analysis/run_balanced_holocrawl.py'),'--build','ranged','--trials','1','--seed','980000','--output',str(result)],cwd=ROOT,check=True)
 def load(p):
  rows={}
  for line in p.read_text(encoding='utf-8').splitlines():
   r=json.loads(line);k=(r['build'],r['scenario'],r['seed'],r['god']);assert k not in rows;rows[k]=r
  return rows
 actual=load(result);expected=load(ROOT/'analysis/native/balance-final01/launcher-ranged-smoke.jsonl')
 assert len(actual)==322 and actual==expected,'Relocated native replay differs'
 result.with_suffix('.validation.json').write_text(json.dumps({'status':'passed','exactRows':322,'relocatedRoot':str(ROOT),'result':str(result)},indent=2)+'\n',encoding='utf-8')
 print('PASS: relocated balance01 native launcher,322 exact rows. Original results preserved.',flush=True)

if __name__=='__main__':main()
