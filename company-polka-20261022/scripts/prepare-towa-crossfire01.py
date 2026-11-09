from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/towa-crossfire01';run.mkdir();(run/'before').mkdir()
changed=['holo-campaign-test.cc']+[f'rltiles/holo/fx_night_towa5_{i}.png' for i in range(2)]
for n in changed:
 p=run/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if str(p.relative_to(src)).replace('\\','/') not in changed};(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
asset=r/'assets/holocrawl/towa-crossfire01';asset.mkdir(parents=True);shutil.copy2('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-4aae33db-acbf-4e39-9b53-62aeedaf184d.png',asset/'crossfire-crest.png')
im=Image.open(asset/'crossfire-crest.png').convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>128 else 0);im.putalpha(a);im=im.crop(a.getbbox())
for f,w in enumerate([44,48]):
 b=im.resize((w,round(w*im.height/im.width)),Image.Resampling.NEAREST);t=Image.new('RGBA',(160,160));t.alpha_composite(b,((160-b.width)//2,64-b.height//2));t.save(src/f'rltiles/holo/fx_night_towa5_{f}.png')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8');start=s.index('    if(const char *shots=getenv("HOLOCRAWL_TOWA_SHOT_REVIEW")) {');end=s.index('    // Noel:',start)
old=s[start:end];old=old.replace('if(const char *shots=getenv("HOLOCRAWL_TOWA_SHOT_REVIEW")) {','if(!getenv("HOLOCRAWL_TOWA_CROSSFIRE_REVIEW")) if(const char *shots=getenv("HOLOCRAWL_TOWA_SHOT_REVIEW")) {',1)
block=r'''    if(const char *shots=getenv("HOLOCRAWL_TOWA_CROSSFIRE_REVIEW")) {
        auto *left=fixture("towa");const auto origin=you.pos();
        require(left->move_to_pos(origin+coord_def(-1,-2)),"Crossfire left setup");
        auto mg=mgen_data::hostile_at(MONS_ETTIN,false,origin+coord_def(1,-2));mg.flags|=MG_FORCE_PLACE;
        auto *right=create_monster(mg,false);require(right,"Crossfire right setup");
        for(auto *m:{left,right}){m->speed=0;m->speed_increment=0;m->hit_points=m->max_hit_points=100;}
        require(invoke(3,nullptr,&origin)==10,"Crossfire real tier3 prerequisite");step(10);
        const std::string stem=std::string(shots)+"/crossfire";
        holo_visual::capture(stem+"-before.png");
        require(invoke(5,nullptr,&origin)==5 && holo_batch::s.resource==8,"Crossfire real tier5 activation eight ammo");
        for(int f=0;f<2;++f)holo_visual::capture_invocation("towa",origin,f,stem+"-cast"+std::to_string(f)+".png",5,false,0);
        step(5);holo_visual::capture(stem+"-active.png");
        std::ofstream proof(dir+"/towa-crossfire.json");proof<<"{\"status\":\"passed\",\"tier\":5,\"volleys\":[";
        for(int volley=0;volley<2;++volley) {
            const int before=left->hit_points+right->hit_points,ammo=holo_batch::s.resource;
            int side=-1;for(auto *m:{left,right}) {
                const auto old=m->pos();const auto dest=origin+coord_def(side*(volley==0?2:1),-2);side=1;
                require(m->move_to_pos(dest),"Crossfire enemy movement");holo_batch::after_monster(*m,old);
            }
            you.elapsed_time+=10;rng::seed(99001+volley);holo_batch::space_tick(you.elapsed_time);
            require(holo_batch::s.resource==ammo-2,"Crossfire two native shots in one turn");
            const int damage=before-left->hit_points-right->hit_points;require(damage>0,"Crossfire real HP loss");
            holo_visual::capture(stem+"-after"+std::to_string(volley)+".png");
            if(volley)proof<<",";proof<<"{\"ammoBefore\":"<<ammo<<",\"ammoAfter\":"<<holo_batch::s.resource<<",\"damage\":"<<damage<<"}";
        }
        proof<<"],\"nativeMovementTrigger\":true,\"shotsPerTurn\":2,\"artOnly\":true}\n";
    }
'''
s=s[:start]+block+old+s[end:];p.write_text(s,encoding='utf-8')
s=(r/'scripts/capture-towa-support05.ps1').read_text(encoding='utf-8').replace('towa-support05','towa-crossfire01').replace('$env:HOLOCRAWL_TOWA_SHOT_REVIEW=$shots;','$env:HOLOCRAWL_TOWA_SHOT_REVIEW=$shots;$env:HOLOCRAWL_TOWA_CROSSFIRE_REVIEW=$shots;');(r/'scripts/capture-towa-crossfire01.ps1').write_text(s,encoding='utf-8')
