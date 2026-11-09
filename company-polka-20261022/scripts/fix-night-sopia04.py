from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';old=root/'analysis/native/night-vfx03';run=root/'analysis/native/night-vfx04';run.mkdir(exist_ok=False)
shutil.copytree(old/'before',run/'before')
for name in ['holo-sopia.cc','holo-sopia.h']:shutil.copy2(src/name,run/'before'/name)
for name in ['preserved-files.json','corner-art-validation.json']:shutil.copy2(old/name,run/name)
def edit(name,a,b):
    p=src/name;s=p.read_text(encoding='utf-8');assert a in s;p.write_text(s.replace(a,b),encoding='utf-8')
edit('holo-sopia.h','bool five_active();','coord_def field_centre(); // Read-only saved field centre for VFX.\nbool five_active();')
edit('holo-sopia.cc','bool five_active(){','coord_def field_centre(){return centre;}\nbool five_active(){')
edit('holo-visual.cc','if(g=="towa" && tier==5)centre=holo_batch::s.centre;','if(g=="sopia" && (tier==3 || tier==5))centre=holo_sopia::field_centre();\n        else if(g=="towa" && tier==5)centre=holo_batch::s.centre;')
a='cast(g,1,m,aim);cast(g,3,m,aim);cast(g,5,m,origin+coord_def(3,0));cast_count+=3;'
b='cast(g,1,m,aim);cast(g,3,m,aim);const auto fixed=holo_sopia::field_centre();cast(g,5,m,origin+coord_def(3,0));require(holo_sopia::field_centre()==fixed,"Sopia upgrade moved actual centre");cast_count+=3;'
edit('holo-campaign-test.cc',a,b)
p=root/'scripts/publish-night-vfx03.py';s=p.read_text(encoding='utf-8').replace('night-vfx03','night-vfx04').replace('all-gods-vfx-draft03','all-gods-vfx-draft04')
a="assert normalized==before,'Combat/campaign changed beyond visual-only arguments/hooks'"
b=a+'''\nsopia=(src/'holo-sopia.cc').read_text(encoding='utf-8').replace('coord_def field_centre(){return centre;}\\n','')
assert sopia==(run/'before/holo-sopia.cc').read_text(encoding='utf-8'),'Sopia logic changed beyond read-only accessor'\n'''
s=s.replace(a,b);(root/'scripts/publish-night-vfx04.py').write_text(s,encoding='utf-8')
p=root/'scripts/package-company-vfx.py';s=p.read_text(encoding='utf-8').replace('night-vfx03','night-vfx04').replace('all-gods-vfx-draft03','all-gods-vfx-draft04').replace('company-vfx-draft03','company-vfx-draft04').replace("'night-vfx01','night-vfx02','night-vfx04'","'night-vfx01','night-vfx02','night-vfx03','night-vfx04'");p.write_text(s,encoding='utf-8')
(old/'followup.json').write_text(json.dumps({'nativeValidation':'passed','runtimeInstalled':False,'reason':'Final visual alignment fix: Sopia upgrade cue must read saved field centre, not ignored new aim.04 adds read-only accessor and centre regression; numerical logic unchanged.'},indent=2),encoding='utf-8')
print('Prepared04, fixed-field VFX alignment only.')
