from pathlib import Path
from collections import deque,defaultdict
import json,subprocess,shutil,random,math,re,hashlib
root=Path(__file__).resolve().parents[1];work=root/'analysis/city-batch21';out=root/'preview/city-batch21';src=root/'preview/city-doors17'
work.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True)
lua=(root/'scripts/export-native-layouts.lua').read_text(encoding='utf-8');a=lua.index('local cases =');b=lua.index('for _, case',a)
seeds=[str(20261105200+i)for i in range(120)]
lua=lua[:a]+'local cases = {'+','.join("{seed='%s',place='D:1'}"%s for s in seeds)+'}\n'+lua[b:]
(root/'runtime/base0341/scripts/city_batch21.lua').write_text(lua,encoding='utf-8')
rc=work/'init.txt';rc.write_text(f'name = CityBatchTerrainExport\nsave_dir = {(work/"saves").as_posix()}/\nmorgue_dir = {(work/"morgue").as_posix()}/\nremember_name = false\nshow_more = false\n',encoding='utf-8')
exe=root/'runtime/base0341/HoloCrawl-0341-base.exe';cmd=[str(exe),'-headless','-dir',str(exe.parent),'-rc',str(rc),'-seed','2026110500']
for suffix in [['-builddb'],['-script','city_batch21']]:
 r=subprocess.run(cmd+suffix,cwd=exe.parent,capture_output=True,timeout=55);log=(r.stdout+b'\n'+r.stderr).decode('utf-8',errors='replace');(work/('builddb.log' if suffix[0]=='-builddb' else 'export.log')).write_text(log,encoding='utf-8')
 if r.returncode:raise RuntimeError(log[-2000:])
all_maps=[json.loads(l.split('HOLO_TERRAIN_JSON ',1)[1])for l in log.splitlines()if l.startswith('HOLO_TERRAIN_JSON ')]
allowed={'rock_wall','stone_wall','clear_rock_wall','floor','closed_door','open_door','exit_dungeon','granite_statue','tree','shallow_water','deep_water','stone_arch','escape_hatch_down','escape_hatch_up','shaft','trap_web','trap_teleport'}
groups=defaultdict(list)
old=[m for folder in ['city-floor-final01','city-random15']for m in json.loads((root/'preview'/folder/'native-d1.json').read_text(encoding='utf-8'))['maps']]
for m in all_maps:
 if not all(f in allowed or f.startswith('stone_stairs_')for f in m['palette']):continue
 if any(m['rows']==o['rows']for o in old):continue
 layout=next(iter(re.findall(r'\blayout_\w+',m['vaults'])),'unknown');m['layout']=layout;groups[layout].append(m)
selected=[]
while len(selected)<8 and any(groups.values()):
 for layout in sorted(groups):
  if groups[layout] and len(selected)<8:selected.append(groups[layout].pop(0))
assert len(selected)==8,f'Only {len(selected)} compatible maps from {len(all_maps)} candidates'
assert len({json.dumps(m['rows'])for m in selected})==8
data={'engine':'DCSS0.34.1','method':'8 newly exported native D:1 snapshots; prior maps excluded','browserRuntime':'Eight static native snapshots, not a browser port of the native generator','nativeBinarySha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'maps':selected}
(out/'native-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Reuse exactly the reviewed room-entrance door pass, with no I/O from its preparation script.
door_source=(root/'scripts/prepare-city-doors17.py').read_text(encoding='utf-8-sig');block=door_source[door_source.index('report=[]'):door_source.index('data.update(')]
scope={'data':data,'deque':deque,'random':random,'math':math};exec(compile(block,'prepare-city-doors17.py:door-pass','exec'),scope)
data.update(method='8 new native D:1 geometries plus reviewed probabilistic room-entrance door pass17',wallGeometryUnchanged=True,nativeTerrainUnchanged=False)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','final-layout.js','wall-volume.js','glass-wall.js','showcase-joint.js']:shutil.copyfile(src/name,out/name)
shutil.copytree(src/'assets',out/'assets',dirs_exist_ok=True)
(out/'native-d1.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'native-d1.js').write_text('globalThis.NativeD1='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
(out/'door-placement17.json').write_text(json.dumps(scope['report'],ensure_ascii=False,indent=2),encoding='utf-8')
p=out/'app.js';s=p.read_text(encoding='utf-8-sig').replace('holocrawl-city-doors17','holocrawl-city-batch21').replace('Math.min(2,Number(q)||0)','Math.min(NativeD1.maps.length-1,Number(q)||0)').replace('active.selected<3','active.selected<NativeD1.maps.length');p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8-sig');s=re.sub(r'<title>.*?</title>','<title>잔향도시 1층 · 랜덤 맵 8종</title>',s);s=re.sub(r'<h1>.*?</h1>','<h1>잔향도시 1층 · 랜덤 맵 8종</h1>',s)
s=re.sub(r'(<select id="mapSelect">).*?(</select>)',lambda match:match[1]+''.join(f'<option value="{i}">{i+1}번</option>'for i in range(8))+match[2],s)
s=s.replace('지형3개','지형8개').replace('지형3개','지형8개');p.write_text(s,encoding='utf-8')
print(json.dumps([{'map':i+1,'seed':m['seed'],'layout':m['layout'],'doors':m['doorPlacement']['total']}for i,m in enumerate(selected)],ensure_ascii=False))
