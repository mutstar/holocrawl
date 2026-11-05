from pathlib import Path
import hashlib,json,re,shutil,subprocess

root=Path(__file__).resolve().parents[1]
work=root/'analysis/native-layout08'
out=root/'preview/native-layout08'
for target in [work/'scripts',out]: target.mkdir(parents=True,exist_ok=True)
shutil.copy2(root/'scripts/export-native-layouts.lua',root/'runtime/base0341/scripts/native_layouts08.lua')
(work/'init.txt').write_text(f'name = TerrainExport\nsave_dir = {(work/"saves").as_posix()}/\nmorgue_dir = {(work/"morgue").as_posix()}/\nremember_name = false\nshow_more = false\n',encoding='utf-8')
exe=root/'runtime/base0341/HoloCrawl-0341-base.exe'
cmd=[str(exe),'-headless','-dir',str(root/'runtime/base0341'),'-rc',str(work/'init.txt'),'-seed','2026110400','-script','native_layouts08']
cache=subprocess.run(cmd[:-2]+['-builddb'],cwd=exe.parent,capture_output=True,timeout=55)
(work/'builddb.log').write_bytes(cache.stdout+b'\n'+cache.stderr)
if cache.returncode: raise RuntimeError(cache.stderr.decode('utf-8',errors='replace')[-2000:])
result=subprocess.run(cmd,cwd=exe.parent,capture_output=True,timeout=55)
stdout=result.stdout.decode('utf-8',errors='replace')
stderr=result.stderr.decode('utf-8',errors='replace')
(work/'export.log').write_text(stdout+'\n'+stderr,encoding='utf-8')
if result.returncode: raise RuntimeError((stdout+'\n'+stderr)[-2500:])
maps=[json.loads(line.split('HOLO_TERRAIN_JSON ',1)[1]) for line in stderr.splitlines() if line.startswith('HOLO_TERRAIN_JSON ')]
assert len(maps)==6, f'Expected six maps, got {len(maps)}; see {work}/export.log'
for m in maps:
    assert len(m['rows'])==m['h'] and all(len(row)==m['w'] for row in m['rows'])
    m['layout']=next(iter(re.findall(r'\blayout_[a-z0-9_]+',m['vaults'])),'unknown')
payload={'engine':'DCSS','version':'0.34.1','commit':'1eebc1a2892e1c89776a0d7a10691f8dac8d9796','nativeBinarySha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'bootstrapSeed':'2026110400','caseSeedMeaning':'Builder RNG reset in a test harness, not the same as generating a complete normal game with this seed.','method':'Unmodified baseline native builder called by upstream test.regenerate_level; exact dgn.grid terrain features exported. No game window or play session.','terrainUnchanged':True,'browserRuntime':'Static exported terrain snapshots, not a browser port of the native generator.','monstersAndItemsExported':False,'maps':maps}
(out/'native-maps.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'native-maps.js').write_text('globalThis.NativeCrawlMaps='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(json.dumps({'maps':len(maps),'binarySha256':payload['nativeBinarySha256'],'layouts':[{'place':m['place'],'seed':m['seed'],'layout':m['layout'],'features':m['palette']} for m in maps]},ensure_ascii=False,indent=2))
