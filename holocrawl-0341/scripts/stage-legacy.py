from pathlib import Path
import hashlib,json,re,shutil,subprocess
root=Path(__file__).resolve().parents[1]
legacy=root.parent/'company-polka-20261022'
source=legacy/'engine/campaign-crawl/crawl-ref/source'
upstream=root/'engine/upstream/crawl-ref/source'
stage=root/'migration/legacy024';stage.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
custom=[];hooks=[]
for p in sorted(source.iterdir()):
 if p.suffix not in {'.cc','.h'}:continue
 text=p.read_text(encoding='utf-8',errors='replace')
 if p.name.startswith('holo'):
  shutil.copy2(p,stage/p.name);custom.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
 else:
  matches=[{'line':i,'text':line.strip()} for i,line in enumerate(text.splitlines(),1) if re.search(r'\bholo(?:crawl|_[a-z_]+)\b',line)]
  if matches:hooks.append({'file':p.name,'existsIn0341':(upstream/p.name).exists(),'references':matches})
art=source/'rltiles/holo'
if art.exists():shutil.copytree(art,root/'migration/assets/legacy-rltiles-holo',dirs_exist_ok=True)
design=root/'design';design.mkdir(exist_ok=True)
for name in ['dungeon-route01.json','street-stairs06.json']:
 p=legacy/'analysis/design'/name
 if p.exists():shutil.copy2(p,design/name)
shutil.copy2(legacy/'scripts/god-art-skills.json',design/'legacy-god-art-skills.json')
preview=legacy/'analysis/previews/street-stairs06';target=root/'preview/street';target.mkdir(parents=True,exist_ok=True)
for name in ['app.js','generator.js','index.html','style.css','stairs-approval.json','upstairs08-generation.json','spiral-generation.json']:
 p=preview/name
 if p.exists():shutil.copy2(p,target/name)
assetnames=set(re.findall(r"'assets/([^']+)'",(preview/'app.js').read_text(encoding='utf-8')))
for name in assetnames:
 out=target/'assets'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(preview/'assets'/name,out)
gods=re.search(r'const char \*ids\[\]=\{(.*?)\};',(source/'holo-worship.cc').read_text(encoding='utf-8'),re.S)
ids=re.findall(r'"([a-z]+)"',gods.group(1))
report={'legacyRoot':str(legacy),'authoritativeSource':str(source),'upstreamTag':'0.34.1','upstreamCommit':subprocess.check_output(['git','-C',str(root/'engine/upstream'),'rev-parse','HEAD'],text=True).strip(),'customSourceFiles':custom,'coreHookFiles':hooks,'gods':ids,'godCount':len(ids),'previewAssets':[{'file':name,'sha256':sha(target/'assets'/name)} for name in sorted(assetnames)],'legacyRuntimeSha256':sha(legacy/'runtime/tiles01/HoloCrawl.exe'),'legacyCodeIntegratedInto0341':False,'previewNativeIntegrated':False}
(root/'analysis/legacy-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'customFiles':len(custom),'coreHookFiles':len(hooks),'gods':len(ids),'previewAssets':len(assetnames),'upstreamCommit':report['upstreamCommit']}))
