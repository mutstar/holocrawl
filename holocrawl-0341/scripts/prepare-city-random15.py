from pathlib import Path
import subprocess,json,hashlib,shutil
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-random15';work=root/'analysis/city-random15'
out.mkdir(exist_ok=True);work.mkdir(parents=True,exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','grounding.js','final-layout.js','wall-volume.js']:
 shutil.copyfile(root/'preview/city-floor-final01'/name,out/name)
shutil.copytree(root/'preview/city-floor-final01/assets',out/'assets',dirs_exist_ok=True)
for name in ['app.js','index.html']:
 p=out/name;s=p.read_text(encoding='utf-8-sig').replace('holocrawl-city-floor-final01','holocrawl-city-random15').replace('잔향도시 1층 · 확정 벽 탐험','잔향도시 1층 · 새 랜덤 지형')
 if name=='index.html':
  s=s.replace('새로 생성한 원본 D:1 지형3개 중 선택하며','이번에 새로 생성한 원본 D:1 지형3개 중 선택하며')
 p.write_text(s,encoding='utf-8')
seeds=[str(20261105151+i) for i in range(45)]
s=(root/'scripts/export-native-layouts.lua').read_text(encoding='utf-8');a=s.index('local cases =');b=s.index('for _, case',a)
s=s[:a]+'local cases = {'+','.join("{seed='%s',place='D:1'}"%seed for seed in seeds)+'}\n'+s[b:]
(root/'runtime/base0341/scripts/city_random15.lua').write_text(s,encoding='utf-8')
rc=work/'init.txt';rc.write_text(f'name = CityRandomTerrainExport\nsave_dir = {(work/"saves").as_posix()}/\nmorgue_dir = {(work/"morgue").as_posix()}/\nremember_name = false\nshow_more = false\n',encoding='utf-8')
exe=root/'runtime/base0341/HoloCrawl-0341-base.exe'
cmd=[str(exe),'-headless','-dir',str(exe.parent),'-rc',str(rc),'-seed','2026110500']
for suffix in [['-builddb'],['-script','city_random15']]:
 r=subprocess.run(cmd+suffix,cwd=exe.parent,capture_output=True,timeout=55)
 log=(r.stdout+b'\n'+r.stderr).decode('utf-8',errors='replace');(work/('builddb.log' if suffix[0]=='-builddb' else 'export.log')).write_text(log,encoding='utf-8')
 if r.returncode:raise RuntimeError(log[-2500:])
maps=[json.loads(line.split('HOLO_TERRAIN_JSON ',1)[1])for line in log.splitlines()if line.startswith('HOLO_TERRAIN_JSON ')]
allowed={'rock_wall','stone_wall','clear_rock_wall','floor','closed_door','open_door','exit_dungeon','granite_statue','tree','shallow_water','deep_water','stone_arch','escape_hatch_down','escape_hatch_up','shaft','trap_web','trap_teleport'}
clean=[m for m in maps if all(f in allowed or f.startswith('stone_stairs_') for f in m['palette'])]
selected=[];layouts=set()
for m in clean:
 layout=next((part for part in m['vaults'].replace(',',' ').split() if part.startswith('layout_')),'unknown')
 if layout not in layouts:selected.append(m);layouts.add(layout)
for m in clean:
 if len(selected)>=3:break
 if m not in selected:selected.append(m)
maps=selected[:3]
assert len(maps)==3, 'Need more clean terrain seeds; inspect export.log'
old=json.loads((root/'preview/city-floor-final01/native-d1.json').read_text(encoding='utf-8'))
assert all(m['rows']!=o['rows']for m in maps for o in old['maps'])
payload={'engine':'DCSS0.34.1','method':'new native headless D:1 exports, not the previous three maps; terrain only','browserRuntime':'three new static snapshots; not unlimited native generation in browser','maps':maps,'nativeBinarySha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
(out/'native-d1.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'native-d1.js').write_text('globalThis.NativeD1='+json.dumps(payload,ensure_ascii=False)+';',encoding='utf-8')
print(json.dumps([{'seed':m['seed'],'vaults':m['vaults'],'features':m['palette']}for m in maps],ensure_ascii=False))

