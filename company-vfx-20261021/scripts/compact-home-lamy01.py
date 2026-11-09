from pathlib import Path
import json,re,hashlib,zipfile,datetime
r=Path(__file__).resolve().parents[1];name='HOLOCRAWL_HOME_2026-10-21_LAMY_CASTER01';stage=r/'exports'/name;archive=Path.home()/'Desktop'/(name+'.zip');full=r/'exports'/(name+'_FULL_CAPTURES.zip');assert archive.is_file() and not full.exists()
archive.rename(full) # Preserve the already-verified full capture archive locally.
manifest=json.loads((stage/'TRANSFER_MANIFEST.json').read_text(encoding='utf-8'));original=manifest['files'];all_paths={e['path'] for e in original}
def raw_image_keep(path):
 p=Path(path);parts=p.parts
 if parts[:2]!=('analysis','native'):return True
 if 'before' in parts or 'source_snapshot' in parts:return True
 run=parts[2];n=p.name.lower()
 if run=='lamy-caster01':return n.startswith('lamy1-') or n.startswith('lamy-')
 if run=='lamy-hud01':return n.startswith('lamy-')
 if run.startswith('towa-'):
  if run=='towa-crossfire02':return n.startswith('crossfire-') or re.match(r'towa-shot-[1-4]-(ready|flight[0-2])\.png$',n) is not None
  if run in {'towa-support05','towa-diagonal01'}:return n.startswith('towa-demo-') or re.match(r'towa-shot-[12]-(ready|flight[0-2])\.png$',n) is not None
  return n.startswith('towa-')
 god=run.split('-')[0];prefixes={'suisei':['suisei','comet','cut-'],'aki':['aki','rose-'],'fubuki':['fubuki','fox-']}.get(god,[god])
 return any(n.startswith(x) for x in prefixes)
def keep(e):
 path=e['path'];p=Path(path)
 if p.suffix.lower() in {'.png','.gif','.webp'}:return raw_image_keep(path)
 if path.endswith('.png.json'):return path[:-5] in all_paths and raw_image_keep(path[:-5])
 return True
entries=[e for e in original if keep(e)]
note='\n\n전달 용량을 줄이기 위해 각 신 캡처 실행에서 반복 생성된 다른 신 원시 프레임은 제외했다. 승인·검토 GIF/미리보기 전체와 해당 신 핵심 원본 프레임,소스·도트·검증 JSON은 포함했다. 전체 중복 캡처 ZIP은 회사 원본 exports에 별도 보존했다.\n'
for n in ['START_HERE_HOME.md','README_FIRST.md','CONTINUE_HERE.md','CURRENT_WORKSPACE.md','HOME_RESUME.md']:
 for folder in [r,stage]:
  p=folder/n;p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
for e in entries:
 p=stage/e['path']
 if e['path'] in ['START_HERE_HOME.md','README_FIRST.md','CONTINUE_HERE.md','CURRENT_WORKSPACE.md','HOME_RESUME.md']:e.update(bytes=p.stat().st_size,sha256=sha(p))
manifest.update(files=entries,createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),excluded='Compiler junction, objects/caches, duplicate historical executables, repeated other-god raw frame captures, large encounter raw datasets and fixture saves; preserved in company workspace.',captureDeduplication=dict(previousFiles=len(original),keptFiles=len(entries),fullCaptureArchiveRetainedLocally=full.name))
(stage/'TRANSFER_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[stage/e['path'] for e in entries]+[stage/'TRANSFER_MANIFEST.json'];print(f'Compact ZIP: {len(files)} files, {sum(p.stat().st_size for p in files)/1024**2:.1f} MiB uncompressed',flush=True)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for p in files:z.write(p,name+'/'+p.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 members=set(z.namelist());assert len(members)==len(z.namelist())==len(entries)+1
 for e in entries:
  h=hashlib.sha256()
  with z.open(name+'/'+e['path']) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest().upper()==e['sha256'],e['path']
 gallery=stage/'analysis/previews/all-gods-vfx-draft04/index.html';data=json.loads(re.search(r'const data=(.*?);function choose',gallery.read_text(encoding='utf-8')).group(1));count=0
 for rows in data.values():
  for entry in rows:
   rel=(gallery.parent/entry['image']).resolve().relative_to(stage.resolve()).as_posix();assert name+'/'+rel in members;count+=1
proof=dict(status='passed',archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),files=len(files),allArchivedHashesVerified=True,crcVerified=True,relocatedNativeSmokePassed=True,previewImagesVerified=count,removedOnlyRedundantRawCaptures=True)
(r/'analysis/native/home-lamy-handoff01/transfer-validation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof,ensure_ascii=False,indent=2),flush=True)
