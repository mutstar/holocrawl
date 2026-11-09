"""One portable ZIP: current game/source/art/previews and verified handoff."""
from pathlib import Path
import os,json,hashlib,shutil,subprocess,re,zipfile,datetime
r=Path(__file__).resolve().parents[1];name='HOLOCRAWL_HOME_2026-10-30_FULLKIT01';(r/'exports').mkdir(exist_ok=True);stage=r/'exports'/name;archive=Path.home()/'Desktop'/(name+'.zip');proofdir=r/'analysis/native/home-fullkit-handoff01';stage.mkdir();proofdir.mkdir()
company_readme=(r/'START_HERE_HOME.md').read_text(encoding='utf-8')
assert not archive.exists(),'Preserve existing archive'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(r/'analysis/native/lui-attack06/checkpoint-manifest.json')['status']=='passed'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(p,rel):
 q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def tree(folder,rel,predicate=lambda p:True):
 for cur,dirs,names in os.walk(folder):
  cur=Path(cur);dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','.pytest_cache','saves','morgue','downloads','node_modules'} and not(cur/d).is_symlink()]
  for n in names:
   p=cur/n
   if p.is_file() and predicate(p):copy(p,Path(rel)/p.relative_to(folder))
def source_ok(p):
 if p.suffix.lower() in {'.o','.d','.gch','.exe','.obj','.dll','.log','.zip','.7z','.tar','.xz','.gz','.db'} and p.name!='Makefile.obj':return False
 if p.name in {'.cflags','.lflags','.contrib-libs'}:return False
 if p.suffix=='.a' and 'install' not in p.parts:return False
 return True
for checkout in ['campaign-crawl','tiles-crawl']:
 folder=r/'engine'/checkout/'crawl-ref/source';tree(folder,Path('engine')/checkout/'crawl-ref/source',source_ok)
for folder in ['assets','scripts','analysis/design','analysis/previews','analysis/handoff-history','analysis/checkpoints']:tree(r/folder,folder,lambda p:p.suffix not in {'.pyc','.pyo'})
selected=set('suisei-vfx04 miko-vfx02 aki-vfx05 fubuki-vfx05 ayame-vfx02 choco-vfx02 choco-vfx03 korone-vfx09 okayu-vfx05 okayu-balance03 pekora-vfx02 pekora-balance01 noel-vfx04 noel-vfx05 noel-supply-sequence01 noel-balance01 watame-vfx02 watame-vfx03 towa-vfx03 towa-vfx04 towa-support05 towa-diagonal01 towa-crossfire02 lamy-hud01 lamy-caster01 lamy-chill-vfx01 lamy-tools05 lamy-banquet-vfx03 lamy-banquet-vfx04 lamy-banquet-vfx05 polka-review01'.split())
selected.update('polka-vfx05 polka-leap02 polka-vfx07 koyori-tube02 koyori-tier3-border01 koyori-five-critical04 lui-ganmo-sharp01 lui-attack06'.split())

selected.update(p.name for p in (r/'analysis/native').iterdir() if p.is_dir() and p.name.startswith(('raden-', 'hajime-', 'su-', 'vivi-', 'sopia-', 'mela-')))

def evidence_ok(p):
 rel=p.relative_to(r/'analysis/native');parts=rel.parts
 if p.suffix.lower() in {'.exe','.dll','.o','.d','.db','.cs','.lua','.saf','.bones'}:return False
 if p.suffix.lower() in {'.png','.gif','.webp'}:return parts[0] in selected and not any(x.startswith('native-attempt') for x in parts)
 if p.suffix.lower() in {'.jsonl','.csv','.tsv'}:return p.stat().st_size<1024*1024
 return p.stat().st_size<8*1024*1024
tree(r/'analysis/native','analysis/native',evidence_ok)
for p in (r/'analysis').rglob('*.md'):
 if 'previews' not in p.parts:copy(p,p.relative_to(r))
for p in r.iterdir():
 if p.is_file() and p.suffix.lower() in {'.md','.json','.cmd','.ps1'} and p.name not in {'TRANSFER_MANIFEST.json','PORTABLE_VALIDATION.json','RUNTIME_DEPENDENCIES.json'}:copy(p,p.name)
copy(r/'TRANSFER_MANIFEST.json','analysis/handoff-history/original-import-TRANSFER_MANIFEST.json')
for p in (r/'engine').glob('*.json'):copy(p,p.relative_to(r))
copy(r/'runtime/tiles01/HoloCrawl.exe','runtime/tiles01/HoloCrawl.exe')
# Preserve root analysis runners and latest Polka native originals, whose local import omitted full PNGs.
for p in (r/'analysis').glob('*.py'):copy(p,p.relative_to(r))
# Resolve every non-Windows PE import against this build's own compiler runtime.
bin_dir=r/'.toolchain/msys64/mingw64/bin';dlls={p.name.lower():p for p in bin_dir.glob('*.dll')};deps=stage/'runtime/deps';deps.mkdir();pending=[stage/'runtime/tiles01/HoloCrawl.exe'];done=set();system=[]
while pending:
 p=pending.pop();result=subprocess.run([str(bin_dir/'objdump.exe'),'-p',str(p)],capture_output=True,text=True,check=True)
 for dll in re.findall(r'DLL Name:\s*(\S+)',result.stdout):
  key=dll.lower()
  if key in done:continue
  done.add(key)
  if key in dlls:copy(dlls[key],Path('runtime/deps')/dlls[key].name);pending.append(deps/dlls[key].name)
  else:
   assert (Path(os.environ.get('WINDIR','C:/Windows'))/'System32'/dll).exists() or key.startswith(('api-ms-win-','ext-ms-win-')),dll
   system.append(dll)
write(stage/'RUNTIME_DEPENDENCIES.json',dict(bundled=[p.name for p in deps.glob('*.dll')],windowsSystem=system,compilerBundled=False,rebuild='Reuse existing home MSYS2/MINGW64 .toolchain; source and contrib install libraries included.'))
# Launchers are relative to the new extraction directory.
for n in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:(stage/n).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\polka-review01\\index.html"\r\n',encoding='ascii')
(stage/'VERIFY_HOME.cmd').write_text('@echo off\r\ncd /d "%~dp0"\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0VERIFY_TRANSFER.ps1"\r\nif errorlevel 1 pause\r\n',encoding='ascii')
copy(r/'scripts/start-portable-vfx.ps1','scripts/start-portable-vfx.ps1')
(stage/'START_HERE_COMPANY.md').write_text(company_readme,encoding='utf-8')
(stage/'README_FIRST.md').write_text(company_readme,encoding='utf-8')
(stage/'OPEN_VFX_REVIEW.cmd').write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\polka-review01\\index.html"\r\n',encoding='ascii')
(stage/'OPEN_GALLERY.cmd').write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\all-gods-vfx-draft04\\index.html"\r\n',encoding='ascii')
(stage/'START_HERE_CAMPAIGN.md').write_text('# Current entry\n\nUse START_HERE_HOME.md and PLAY_HOLOCRAWL.cmd.\n',encoding='utf-8')
for launch in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:copy(r/launch,launch)
print('Stage copied. Running relocated game using bundled DLLs only...',flush=True)
result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(stage/'scripts/start-portable-vfx.ps1'),'-SmokeTest'],capture_output=True,text=True)
(proofdir/'launcher.stdout.log').write_text(result.stdout,encoding='utf-8');(proofdir/'launcher.stderr.log').write_text(result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
smoke=stage/'runtime/portable-smoke03';assert read(smoke/'validation.json')['gods']==22 and read(smoke/'reload.json')['status']=='passed' and read(smoke/'lamy-caster.json')['status']=='passed'
write(stage/'PORTABLE_VALIDATION.json',dict(status='passed',bundledDependenciesOnly=True,relocatedNativeGame=True,gods=22,freshProcessReload=True,lamyCaster=read(smoke/'lamy-caster.json'),binarySha256=sha(stage/'runtime/tiles01/HoloCrawl.exe')))
# Every referenced local preview image must be present in the transfer.
gallery=stage/'analysis/previews/all-gods-vfx-draft04/index.html';html=gallery.read_text(encoding='utf-8');data=json.loads(re.search(r'const data=(.*?);function choose',html).group(1));images=[gallery.parent/entry['image'] for entries in data.values() for entry in entries];assert all(p.is_file() for p in images)
active=stage/'analysis/previews/mela-review01/tier5-dispatch01.html';active_html=active.read_text(encoding='utf-8');local_refs=re.findall(r'(?:src|href)="([^"]+)"',active_html);assert all((active.parent/ref.split('#')[0]).is_file() for ref in local_refs if ref and not ref.startswith(('http:', 'https:', '#')));
write(stage/'PREVIEW_LINK_VALIDATION.json',dict(status='passed',gods=len(data),images=len(images),currentGod='mela',currentTier=5,allImagesPresent=True))
# Generated caches and fixture saves are not part of the portable source snapshot.
def transfer_file(p):
 rel=p.relative_to(stage);parts=rel.parts
 if 'saves' in parts or 'morgue' in parts:return False
 if p.suffix.lower() in {'.db','.o','.d','.pyc'}:return False
 return True
assert read(stage/'VFX_DRAFT_STATUS.json')['tierApprovals']['koyori']['approved']==[1,3,5]
assert read(stage/'analysis/native/lui-attack06/checkpoint-manifest.json')['status']=='passed'
assert (stage/'analysis/previews/lui-attack06/attack.gif').is_file()
assert sha(stage/'runtime/tiles01/HoloCrawl.exe')==sha(r/'runtime/tiles01/HoloCrawl.exe')
assert read(stage/'VFX_DRAFT_STATUS.json')['all22GodVisualsApproved'] is True
assert read(stage/'VFX_DRAFT_STATUS.json')['passiveExpansionPolicy']['assignmentsApproved'] is False
assert (stage/'analysis/design/mela-dispatch01.json').is_file()
assert (stage/'FULLKIT_CORE_INVENTORY.md').is_file()
files=sorted(p for p in stage.rglob('*') if p.is_file() and transfer_file(p));entries=[dict(path=p.relative_to(stage).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
write(stage/'TRANSFER_MANIFEST.json',dict(version='home-fullkit01',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),entry='START_HERE_HOME.md',source='engine/campaign-crawl/crawl-ref/source',review='analysis/previews/mela-review01/tier5-dispatch01.html',next='At home compare 22 core kits: strong add 1 passive, ambiguous add 2; per-god counts/content undecided. Start Suisei. Pending Vivi/Sopia/Mela combat integration.',files=entries,excluded='Compiler junction, objects/caches, duplicate historical EXEs, large encounter raw datasets and test saves; originals retained in company workspace.'))
files.append(stage/'TRANSFER_MANIFEST.json');print(f'Packing {len(files)} files, {sum(p.stat().st_size for p in files)/1024**2:.1f} MiB...',flush=True)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for p in files:z.write(p,name+'/'+p.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(entries)+1
 for e in entries:
  h=hashlib.sha256()
  with z.open(name+'/'+e['path']) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest().upper()==e['sha256'],e['path']
proof=dict(status='passed',archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),files=len(files),allArchivedHashesVerified=True,crcVerified=True,relocatedNativeSmokePassed=True,previewImagesVerified=len(images))
write(proofdir/'transfer-validation.json',proof);print(json.dumps(proof,ensure_ascii=False,indent=2),flush=True)
