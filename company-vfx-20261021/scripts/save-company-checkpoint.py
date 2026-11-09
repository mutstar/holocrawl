"""Non-mutating full company handoff: sources, tools, raw evidence, per-file hashes."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NAME='HOLOCRAWL_COMPANY_CHECKPOINT_2026-10-20_BALANCE01'
ARCHIVE=ROOT.parent/(NAME+'.zip')
PREFIX='HOLOCRAWL_COMPANY_BALANCE01'
MANIFEST=ROOT/'COMPANY_CHECKPOINT_MANIFEST.json'

def skip(rel,isdir=False):
 parts=rel.parts
 if any(x in ('.git','__pycache__','.pytest_cache') for x in parts):return True
 if parts[:2]==('.toolchain','downloads'):return True
 if parts[:2]==('.toolchain','msys64'):
  sub=parts[2:]
  if sub and sub[0] in ('home','tmp','dev'):return True
  if sub[:2] in (('var','cache'),('var','log'),('etc','ssh')):return True
  if sub[:3]==('etc','pacman.d','gnupg'):return True
 if rel.name=='COMPANY_CHECKPOINT_MANIFEST.json':return True
 if rel.suffix in ('.pyc','.pyo'):return True
 if parts[0]=='engine':
  if 'saves' in parts:
   i=parts.index('saves')
   if len(parts)>i+1 and parts[i+1] in ('db','des'):return True
  if rel.suffix in ('.o','.d','.a','.gch'):return True
  if rel.name=='crawl.exe' and rel.as_posix()!='engine/crawl/crawl-ref/source/crawl.exe':return True
 return False

def main():
 assert not ARCHIVE.exists(),'Refusing to overwrite transfer ZIP'
 files=[]
 for current,dirs,names in os.walk(ROOT,followlinks=False):
  directory=Path(current)
  dirs[:]=[d for d in sorted(dirs) if not skip((directory/d).relative_to(ROOT),True) and not (directory/d).is_symlink()]
  for name in sorted(names):
   p=directory/name;rel=p.relative_to(ROOT)
   if skip(rel) or p.is_symlink() or not p.is_file():continue
   files.append(p)
 required=['START_HERE_COMPANY.md','PORTABLE_PATHS.json','analysis/native/balance-final01/settings.json','analysis/native/balance-final01/balance-engine.exe','engine/balance-crawl/crawl-ref/source/holocrawl.cc','.toolchain/msys64/mingw64/bin/python.exe','.toolchain/msys64/mingw64/bin/g++.exe','.toolchain/msys64/usr/bin/bash.exe']
 selected={p.relative_to(ROOT).as_posix() for p in files};assert set(required)<=selected
 total=sum(p.stat().st_size for p in files);print(f'Packaging {len(files)} files, {total/1024**3:.2f} GiB before compression',flush=True)
 entries=[]
 with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
  for i,p in enumerate(files,1):
   stat=p.stat();rel=p.relative_to(ROOT).as_posix();h=hashlib.sha256()
   info=zipfile.ZipInfo.from_file(p,PREFIX+'/'+rel);info.compress_type=zipfile.ZIP_DEFLATED;info._compresslevel=3
   with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dest:
    for data in iter(lambda:src.read(1024*1024),b''):h.update(data);dest.write(data)
   after=p.stat();assert stat.st_size==after.st_size and stat.st_mtime_ns==after.st_mtime_ns,f'File changed during checkpoint: {rel}'
   entries.append(dict(path=rel,bytes=stat.st_size,sha256=h.hexdigest().upper()))
   if i%3000==0:print(f'Packed {i}/{len(files)}',flush=True)
  manifest=dict(version=NAME,createdAtKst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),archiveRoot=PREFIX,
   latestBalance='balance01',activeJobs=False,entryDocument='START_HERE_COMPANY.md',uncompressedBytes=total,
   included='Full project source/runtime data, historical raw native cohorts/failures/reports/binaries and offline build/Python tools.',
   excluded='Git metadata, private compiler home/ssh/keyring, temporary/cache/download data, Python caches, engine saves/db and saves/des generated caches, reproducible engine objects/static build libraries and noncanonical unstripped crawl.exe copies. Frozen original/analysis/runtime evidence binaries retained.',files=entries)
  payload=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n';MANIFEST.write_text(payload,encoding='utf-8');z.writestr(PREFIX+'/COMPANY_CHECKPOINT_MANIFEST.json',payload)
 print('Verifying every archived file SHA256 and ZIP CRC...',flush=True)
 with zipfile.ZipFile(ARCHIVE) as z:
  names=z.namelist();assert len(names)==len(set(names))==len(entries)+1
  for i,v in enumerate(entries,1):
   h=hashlib.sha256();count=0
   with z.open(PREFIX+'/'+v['path']) as f:
    for data in iter(lambda:f.read(1024*1024),b''):h.update(data);count+=len(data)
   assert count==v['bytes'] and h.hexdigest().upper()==v['sha256'],v['path']
   if i%6000==0:print(f'Verified {i}/{len(entries)}',flush=True)
 h=hashlib.sha256()
 with ARCHIVE.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 result=dict(status='passed',archive=str(ARCHIVE),archiveBytes=ARCHIVE.stat().st_size,sha256=h.hexdigest().upper(),files=len(entries),uncompressedBytes=total,allArchivedFileHashesVerified=True,zipCrcVerified=True,relocatedNativeSmoke='pending')
 ARCHIVE.with_suffix('.verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 ARCHIVE.with_suffix('.sha256.txt').write_text(f'{result["sha256"]}  {ARCHIVE.name}\n',encoding='ascii')
 print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
