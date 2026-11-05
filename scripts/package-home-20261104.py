from pathlib import Path
import os,json,time,hashlib,zipfile,collections

root=Path(__file__).resolve().parents[1]
desktop=Path(os.environ['USERPROFILE'])/'Desktop'
name='HOLOCRAWL_HOME_2026-11-05_CITY_EXPLORE03'
target=desktop/(name+'.zip')
revision=2
while target.exists():
    target=desktop/(name+f'_REV{revision:02d}.zip');revision+=1
prefix=name+'/'
skip_dirs={'.git','.toolchain','node_modules','__pycache__','exports','.home-preview','handoff-portable-check'}
skip_suffix={'.o','.obj','.d','.a','.pch','.gch','.pdb','.ilk','.res','.zip','.7z','.pyc'}
excluded=collections.Counter();files=[]
for base,dirs,names in os.walk(root,followlinks=False):
    keep=[]
    for d in dirs:
        p=Path(base)/d;parts=p.relative_to(root).parts
        duplicate_snapshot=('analysis' in parts and 'native' in parts and d in {'before','source_snapshot','snapshots','frozen_source','baseline_source','shots','frames','rawframes'})
        cache_save=('analysis' in parts and 'native' in parts and (d=='saves' or d.endswith('-save') or d.endswith('-saves')))
        if d in skip_dirs or p.is_symlink() or cache_save or duplicate_snapshot:excluded['directory '+d]+=1
        else:keep.append(d)
    dirs[:]=keep
    for n in names:
        p=Path(base)/n;rel=p.relative_to(root)
        if p.is_symlink():excluded['symlink']+=1;continue
        if p.suffix.lower() in skip_suffix:excluded['extension '+p.suffix.lower()]+=1;continue
        if p.suffix.lower() in {'.exe','.dll'} and ('runtime' not in rel.parts or 'analysis' in rel.parts):excluded['duplicate binary outside runtime']+=1;continue
        if n.startswith('HOME_PACKAGE_MANIFEST') or n in {'CHECKPOINT_MANIFEST.json','TRANSFER_MANIFEST.json'}:excluded['old package manifest']+=1;continue
        files.append((rel,p,p.stat().st_size))
files.sort(key=lambda x:x[0].as_posix())
total=sum(s for _,_,s in files)
print(json.dumps({'phase':'inventory','files':len(files),'rawMiB':round(total/2**20,1),'zip':str(target),'excluded':excluded},ensure_ascii=False),flush=True)
records=[];last=time.monotonic();start=last
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for i,(rel,p,size) in enumerate(files):
        h=hashlib.sha256();info=zipfile.ZipInfo.from_file(p,arcname=prefix+rel.as_posix());info.compress_type=zipfile.ZIP_STORED if p.suffix.lower() in {'.png','.gif','.jpg','.jpeg','.webp','.mp4','.ogg','.mp3','.woff2'} else zipfile.ZIP_DEFLATED
        with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
            while chunk:=src.read(1024*1024):h.update(chunk);dst.write(chunk)
        records.append({'path':rel.as_posix(),'size':size,'sha256':h.hexdigest()})
        if time.monotonic()-last>15:
            print(json.dumps({'phase':'packing','done':i+1,'total':len(files),'elapsedSeconds':round(time.monotonic()-start)}),flush=True);last=time.monotonic()
    manifest={'created':'2026-11-05','entry':'START_HOME_2026-11-04.md','launcher':'OPEN_HOME_EXPLORER.cmd','currentProject':'holocrawl-0341','preview':'holocrawl-0341/preview/city-explore01/index.html','legacy':'company-polka-20261022','excluded':dict(excluded),'scope':'Project sources, designs, art, previews, reports, scripts and runtime. Old exports/archives/build caches/toolchain excluded. Browser localStorage is not part of the filesystem snapshot.','files':records}
    z.writestr(prefix+'PACKAGE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'phase':'verifying','files':len(records),'zipMiB':round(target.stat().st_size/2**20,1)}),flush=True)
with zipfile.ZipFile(target) as z:
    assert len(z.namelist())==len(records)+1
    for i,record in enumerate(records):
        h=hashlib.sha256()
        with z.open(prefix+record['path']) as f:
            while chunk:=f.read(1024*1024):h.update(chunk)
        assert h.hexdigest()==record['sha256'],record['path']
        if time.monotonic()-last>15:
            print(json.dumps({'phase':'verifying','done':i+1,'total':len(records)}),flush=True);last=time.monotonic()
    for required in ['OPEN_HOME_EXPLORER.cmd','START_HOME_2026-11-04.md','holocrawl-0341/preview/city-explore01/crates-validation.json','holocrawl-0341/engine/upstream/crawl-ref/source/los.cc','company-polka-20261022/HOLOCRAWL_DESIGN.md']:
        assert prefix+required in z.namelist(),required
archive_hash=hashlib.sha256()
with target.open('rb') as f:
    while chunk:=f.read(1024*1024):archive_hash.update(chunk)
result={'status':'passed','zip':str(target),'zipBytes':target.stat().st_size,'zipMiB':round(target.stat().st_size/2**20,1),'files':len(records),'sha256':archive_hash.hexdigest(),'allMemberHashesVerified':True,'elapsedSeconds':round(time.monotonic()-start)}
out=root/'holocrawl-0341/analysis/home-package-20261105'
out.mkdir(exist_ok=True)
(out/'package-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False),flush=True)
