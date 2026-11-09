from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1];old=root/'analysis/native/night-vfx02';run=root/'analysis/native/night-vfx03';run.mkdir(exist_ok=False)
shutil.copytree(old/'before',run/'before')
for n in ['preserved-files.json','corner-art-validation.json']:shutil.copy2(old/n,run/n)
p=root/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';shutil.copy2(p,old/'failed-test-source.cc');s=p.read_text(encoding='utf-8')
a='cast("pekora",1,nullptr,bomb);cast("pekora",3,nullptr,bomb,1);step(40);'
b='cast("pekora",1,nullptr,bomb);step(10);cast("pekora",3,nullptr,bomb,1);step(40);'
assert a in s;s=s.replace(a,b);p.write_text(s,encoding='utf-8')
(old/'failure.json').write_text(json.dumps({'status':'failed','reason':'Delayed detonation diagnostic attempted before native bomb arming time; native rejected action correctly. Added required10aut world step in03. Combat and VFX unchanged.','gdb':'debug.log','originalsPreserved':True},indent=2),encoding='utf-8')
p=root/'scripts/publish-night-vfx02.py';s=p.read_text(encoding='utf-8').replace('night-vfx02','night-vfx03').replace('all-gods-vfx-draft02','all-gods-vfx-draft03');(root/'scripts/publish-night-vfx03.py').write_text(s,encoding='utf-8')
p=root/'scripts/package-company-vfx.py';s=p.read_text(encoding='utf-8').replace('night-vfx02','night-vfx03').replace('all-gods-vfx-draft02','all-gods-vfx-draft03').replace("'night-vfx01','night-vfx03'","'night-vfx01','night-vfx02','night-vfx03'");p.write_text(s,encoding='utf-8')
print('Prepared03 with real arming wait;02 failure and GDB retained.')
