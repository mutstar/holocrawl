from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1];old=root/'analysis/native/night-vfx01';run=root/'analysis/native/night-vfx02';run.mkdir(exist_ok=False)
shutil.copytree(old/'before',run/'before')
for n in ['preserved-files.json','corner-art-validation.json']:shutil.copy2(old/n,run/n)
(old/'coverage-followup.json').write_text(json.dumps({'status':'needs-expanded-capture','nativeValidation':'passed','galleryFirstAttempt':'Noel tier1 real-menu capture missing; stopped before installing runtime.','followup':'night-vfx02 adds real menu capture and selectable branches; original outputs retained.'},indent=2),encoding='utf-8')
p=root/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
a='require(you.skill(SK_LONG_BLADES,1,false)==std::min(27,base+6) && you.hp_max==basehp,"Noel native skills / no maxHP gain");'
b=a+'''
            if(const char *shots=getenv("HOLOCRAWL_NIGHT_REVIEW"))for(int f=0;f<2;++f)holo_visual::capture_invocation("noel",you.pos(),f,std::string(shots)+"/noel-menu1-frame"+std::to_string(f)+".png",1);'''
assert a in s;s=s.replace(a,b)
a='    int cast_count=0,roundtrips=0;'
b='''    if(getenv("HOLOCRAWL_NIGHT_REVIEW")) {
        // Selective visual diagnostics use explicitly prepared applause/paint.
        // These are not natural resource-income or win-rate measurements.
        for(int option=0;option<3;++option) {
            auto *m=fixture("polka");holo_batch::s.resource=3;you.hp-=25;
            cast("polka",5,m,m->pos(),option);
        }
        for(int option=1;option<=3;++option) {
            auto *m=fixture("polka");
            if(option==3)for(const auto p:{you.pos()+coord_def(2,1),you.pos()+coord_def(-1,1)}){
                auto mg=mgen_data::hostile_at(MONS_ETTIN,false,p);mg.flags|=MG_FORCE_PLACE;auto *extra=create_monster(mg,false);require(extra,"juggling enemies missing");extra->speed=0;extra->hit_points=extra->max_hit_points=10000;
            }
            cast("polka",1,m,m->pos(),option);
        }
        for(int option=0;option<3;++option) {
            auto *m=fixture("raden");if(option)cast("raden",1,nullptr,you.pos(),option);
            if(option==0){holo_batch::s.targets[m->mid].paint=3;holo_batch::s.targets[m->mid].paint_end=you.elapsed_time+100;}
            cast("raden",3,m,m->pos(),option);
        }
        for(int type=1;type<=3;++type){auto *m=fixture("koyori");cast("koyori",1,nullptr,you.pos(),type);cast("koyori",1,m,m->pos(),10+type);cast("koyori",5,nullptr,you.pos(),type+2);}
        fixture("sopia");const auto origin=you.pos();cast("sopia",5,nullptr,origin+coord_def(2,0));step(70);cast("sopia",6,nullptr,origin+coord_def(2,0));
        fixture("pekora");const auto bomb=you.pos()+coord_def(3,0);cast("pekora",1,nullptr,bomb);cast("pekora",3,nullptr,bomb,1);step(40);
        fixture("pekora");const auto centre=you.pos();holo_batch::manual_positions={centre+coord_def(3,-1),centre+coord_def(3,0),centre+coord_def(3,1)};cast("pekora",5,nullptr,centre+coord_def(3,0));step(70);
    }
'''+a
assert a in s;s=s.replace(a,b);p.write_text(s,encoding='utf-8')
p=root/'scripts/publish-night-vfx01.py';s=p.read_text(encoding='utf-8').replace('night-vfx01','night-vfx02').replace('all-gods-vfx-draft01','all-gods-vfx-draft02').replace('assets/holocrawl/night-vfx02','assets/holocrawl/night-vfx01')
a="entries['noel'].append({'tier':3"
b="entries['noel'].insert(0,{'tier':1,'option':0,'title':skills['noel'][0][0],'image':clip('noel-menu1',[raw/f'noel-menu1-frame{f}.png' for f in range(2)]),'kind':'실제 권능 메뉴 사용 직후'})\n"+a
assert a in s;s=s.replace(a,b)
a='# Preserve reviewed full sequences for approved gods, including original timings.'
b='''for g in ['pekora','sopia']:
    for p in sorted(raw.glob(g+'-impact-*-frame0.png')):
        stem=p.name[:-11];entries[g].append({'tier':5,'option':0,'title':'실제 폭발/기폭','image':clip(stem,[p,raw/(stem+'-frame1.png')]),'kind':'실제 폭발 콜백 · 준비/예약 시전과 구분'})
'''+a
s=s.replace(a,b).replace('../../../../START_HERE_COMPANY.md','../../../START_HERE_COMPANY.md')
(root/'scripts/publish-night-vfx02.py').write_text(s,encoding='utf-8')
print('Prepared night-vfx02 capture expansion; visuals/combat unchanged from01.')
