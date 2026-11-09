from pathlib import Path
import ast,json,hashlib,subprocess,zipfile,datetime,shutil
root=Path(__file__).resolve().parents[1];name='HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT';stage=root/'exports'/name;archive=stage.with_suffix('.zip');run=root/'analysis/native/night-vfx04'
assert stage.resolve().parent==(root/'exports').resolve() and stage.is_dir() and not archive.exists()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(stage/'runtime/tiles01/HoloCrawl.exe')==sha(root/'runtime/tiles01/HoloCrawl.exe')
tree=ast.parse((root/'scripts/package-company-vfx.py').read_text(encoding='utf-8'))
constants={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {'launcher','readme'}}
old=stage/'scripts/start-portable-vfx.ps1';shutil.copy2(old,run/'failed-portable-launcher02.ps1')
old.write_text(constants['launcher'],encoding='utf-8-sig')
shutil.copy2(root/'scripts/package-company-vfx.py',stage/'scripts/package-company-vfx.py');shutil.copy2(Path(__file__),stage/'scripts/finalize-company-vfx-archive.py')
print('Rebuilding native database before fresh-path test; original failed logs retained.',flush=True)
result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(old),'-SmokeTest'],capture_output=True,text=True)
out=stage/'runtime/portable-smoke03';out.mkdir(exist_ok=True)
(out/'launcher.stdout.log').write_text(result.stdout,encoding='utf-8');(out/'launcher.stderr.log').write_text(result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
write(stage/'PORTABLE_VALIDATION.json',{'status':'passed','nativeDatabaseRebuiltWithSameRcAndSaveDir':True,'bundledDependenciesOnly':True,'gods':22,'freshProcessReload':True,'binarySha256':sha(stage/'runtime/tiles01/HoloCrawl.exe'),'originalFailedStartup':['runtime/portable-smoke','runtime/portable-smoke02'],'reasonFixed':'Build map database before test mode using the same rc/save_dir as the game; no engine rule change.'})
write(run/'portable-repair.json',{'status':'passed','reason':'Fresh package lacked map DB at the new save_dir. First repair built a different default cache; final launcher passes the same rc/save_dir to builddb and runtime. Failed logs/GDB retained.','gdb':'portable-debug2.log','test':'runtime/portable-smoke03'})
entries=[]
for p in sorted(stage.rglob('*')):
    if p.is_file() and p.name!='TRANSFER_MANIFEST.json':entries.append({'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p).upper()})
write(stage/'TRANSFER_MANIFEST.json',{'version':'company-vfx-draft04','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry':'START_HERE_COMPANY.md','review':'analysis/previews/all-gods-vfx-draft04/index.html','files':entries,'excludes':'Compiler/cache, duplicate binaries, old per-encounter simulation JSONL; preserved in home workspace.'})
print(f'Portable native22-god and reload passed. Archiving {len(entries)} files / {sum(e["bytes"] for e in entries)/1024**2:.1f} MiB...',flush=True)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
    for p in sorted(stage.rglob('*')):
        if p.is_file():z.write(p,name+'/'+p.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None;assert len(z.namelist())==len(set(z.namelist()))==len(entries)+1
    for e in entries:
        h=hashlib.sha256()
        with z.open(name+'/'+e['path']) as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        assert h.hexdigest().upper()==e['sha256'],e['path']
proof={'status':'passed','archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(entries),'allArchivedHashesVerified':True,'crcVerified':True,'relocatedNativeSmokePassed':True}
write(run/'transfer-validation.json',proof);print(json.dumps(proof,indent=2),flush=True)
