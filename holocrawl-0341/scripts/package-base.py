from pathlib import Path
import subprocess,shutil,re,json,hashlib
root=Path(__file__).resolve().parents[1];source=root/'engine/upstream/crawl-ref/source';out=root/'runtime/base0341'
bin_dir=root.parent/'company-polka-20261022/.toolchain/msys64/mingw64/bin'
exe=out/'HoloCrawl-0341-base.exe';assert exe.exists(),'Build base first'
for dirname in ['dat','test']:
 shutil.copytree(source/dirname,out/dirname,dirs_exist_ok=True)
for p in (source/'rltiles').glob('*.png'):shutil.copy2(p,out/'dat/tiles'/p.name)
shutil.copytree(source.parent/'settings',out/'settings',dirs_exist_ok=True)
for name in ['CREDITS.txt','LICENSE','licence.txt','README.md']:
 p=root/'engine/upstream'/name
 if not p.exists():p=source.parent/name
 if p.exists():shutil.copy2(p,out/name)
pending=[exe];copied=set()
while pending:
 p=pending.pop();text=subprocess.check_output([str(bin_dir/'objdump.exe'),'-p',str(p)],text=True,errors='replace')
 for name in re.findall(r'DLL Name:\s*(\S+)',text):
  original=bin_dir/name
  if name.lower() not in copied and original.exists():
   copied.add(name.lower());target=out/name;shutil.copy2(original,target);pending.append(target)
(out/'init.txt').write_text('name = HoloBase\nsave_dir = saves/\nmorgue_dir = morgue/\nremember_name = false\nshow_more = false\n',encoding='utf-8')
manifest={'engine':'DCSS','tag':'0.34.1','commit':subprocess.check_output(['git','-C',str(root/'engine/upstream'),'rev-parse','HEAD'],text=True).strip(),'binary':'runtime/base0341/HoloCrawl-0341-base.exe','sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'runtimeDlls':sorted(copied),'holocrawlGodsIntegrated':False,'customDungeonIntegrated':False,'purpose':'Unmodified 0.34.1 engine baseline for HoloCrawl migration; debug tiles build.'}
(root/'analysis/base-build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest))
