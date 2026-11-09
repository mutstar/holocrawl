"""Create one self-contained home transfer ZIP and verify every archived byte."""
from pathlib import Path
import collections,datetime,hashlib,json,os,zipfile
root=Path(__file__).resolve().parents[1]
archive=Path('C:/Users/071staff/Desktop/HOLOCRAWL_HOME_2026-10-20_WRATH02_SKILLS.zip')
prefix='HoloCrawl_HOME_2026-10-20'
manifest_path=root/'HOME_HANDOFF_MANIFEST.json'
required_exes={
 'analysis/native/balance-final01/balance-engine.exe',
 'analysis/native/campaign-abilities01/wrath02-console02/abilities-engine.exe',
 'analysis/native/tiles01/wrath02-sdl01/tiles-engine.exe',
 'engine/campaign-crawl/crawl-ref/source/crawl.exe',
 'engine/tiles-crawl/crawl-ref/source/crawl.exe',
 'runtime/tiles01/HoloCrawl.exe'
}
def skip(rel,isdir=False):
    ps=rel.parts;s=rel.as_posix()
    if any(p in {'.git','__pycache__','.pytest_cache'} for p in ps):return True
    if len(ps)==1:
        if isdir:return ps[0] not in {'.toolchain','analysis','assets','engine','runtime','scripts','settings'}
        return rel.name=='HOME_HANDOFF_MANIFEST.json' or rel.suffix.lower() not in {'.md','.cmd','.json'}
    if ps[0]=='.toolchain':
        if ps[1]=='downloads':return True
        if ps[1]=='msys64':
            sub=ps[2:]
            if sub and sub[0] in {'home','tmp','dev'}:return True
            if sub[:2] in [('var','cache'),('var','log'),('etc','ssh')]:return True
            if sub[:3]==('etc','pacman.d','gnupg'):return True
    if ps[0]=='engine':
        if ps[1] not in {'campaign-crawl','tiles-crawl','balance-crawl','patches'} and len(ps)>2:return True
        if len(ps)==2 and isdir and ps[1] not in {'campaign-crawl','tiles-crawl','balance-crawl','patches'}:return True
        if 'saves' in ps:
            i=ps.index('saves')
            if len(ps)>i+1 and ps[i+1] in {'db','des'}:return True
        if (rel.suffix in {'.o','.d','.gch','.obj'} and rel.name != 'Makefile.obj') or rel.name in {'.cflags','.lflags','.contrib-libs'}:return True
        if rel.suffix=='.a' and not ('contrib' in ps and 'install' in ps):return True
    if ps[0]=='runtime' and ps[1] not in {'tiles01','campaign01','results','reports','logs'}:return True
    if rel.suffix in {'.pyc','.pyo'}:return True
    if rel.suffix.lower()=='.exe' and ps[0]!='.toolchain' and s not in required_exes:return True
    return False
assert not archive.exists(),'Refusing to replace an existing home ZIP'
state=json.loads((root/'engine/campaign_status.json').read_text(encoding='utf-8'))
assert state['version']=='wrath02'
assert hashlib.sha256((root/state['playBinary']).read_bytes()).hexdigest().upper()==state['playBinarySha256']
assert json.loads((root/'analysis/previews/current-god-art/skills-validation.json').read_text())['tierSummaries']==66
files=[]
for cur,ds,names in os.walk(root,followlinks=False):
    cur=Path(cur);ds[:]=[d for d in sorted(ds) if not (cur/d).is_symlink() and not skip((cur/d).relative_to(root),True)]
    for n in sorted(names):
        p=cur/n
        if p.is_file() and not p.is_symlink() and not skip(p.relative_to(root)):files.append(p)
selected={p.relative_to(root).as_posix() for p in files}
required=required_exes|{'START_HERE_HOME.md','OPEN_GALLERY.cmd','VERIFY_HOME.cmd','HOME_HANDOFF_STATE.json','analysis/previews/current-god-art/index.html','analysis/previews/current-god-art/skills-4.png','scripts/god-art-skills.json','.toolchain/msys64/usr/bin/bash.exe','.toolchain/msys64/mingw64/bin/python.exe','.toolchain/msys64/mingw64/bin/g++.exe'}
assert required<=selected,required-selected
print(f'Packaging {len(files)} files, {sum(p.stat().st_size for p in files)/1024**3:.2f} GiB uncompressed.',flush=True)
entries=[]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
    for i,p in enumerate(files,1):
        before=p.stat();name=p.relative_to(root).as_posix();h=hashlib.sha256()
        info=zipfile.ZipInfo.from_file(p,prefix+'/'+name);info.compress_type=zipfile.ZIP_DEFLATED;info._compresslevel=3
        with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
            for b in iter(lambda:src.read(1024*1024),b''):h.update(b);dst.write(b)
        after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),name
        entries.append(dict(path=name,bytes=before.st_size,sha256=h.hexdigest().upper()))
        if i%10000==0:print(f'Packed {i}/{len(files)}',flush=True)
    manifest=dict(version='home-wrath02-skills',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archiveRoot=prefix,entryDocument='START_HERE_HOME.md',latestGame='wrath02',gallery='analysis/previews/current-god-art/index.html',files=entries,excluded='Old nested ZIPs, duplicate obsolete executables/checkouts, engine objects/generated DB caches, private toolchain home/SSH/keyrings/temp/downloads. Historical reports/raw result data retained.',uncompressedBytes=sum(e['bytes'] for e in entries))
    payload=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n';manifest_path.write_text(payload,encoding='utf-8');z.writestr(prefix+'/HOME_HANDOFF_MANIFEST.json',payload)
print('Verifying every ZIP entry SHA256 and CRC...',flush=True)
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==len(set(z.namelist()))==len(entries)+1
    for i,e in enumerate(entries,1):
        h=hashlib.sha256();count=0
        with z.open(prefix+'/'+e['path']) as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b);count+=len(b)
        assert count==e['bytes'] and h.hexdigest().upper()==e['sha256'],e['path']
        if i%10000==0:print(f'Verified {i}/{len(entries)}',flush=True)
    assert z.read(prefix+'/HOME_HANDOFF_MANIFEST.json').decode()==payload
h=hashlib.sha256()
with archive.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
proof=dict(status='passed',archive=str(archive),bytes=archive.stat().st_size,sha256=h.hexdigest().upper(),files=len(entries),everyArchivedSHA256Verified=True,crcVerified=True)
(root/'analysis/previews/current-god-art/home-archive-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,indent=2),flush=True)
