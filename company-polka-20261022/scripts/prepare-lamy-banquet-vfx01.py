from pathlib import Path
from PIL import Image
import json,hashlib,shutil
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-banquet-vfx01';art=r/'assets/holocrawl/lamy-banquet-vfx01'
changed=['holo-lamy.cc','holo-visual.cc','holo-visual.h','tilereg-dgn.cc','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']
for n in changed:
    p=run/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
shutil.copy2(r/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
baseline={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if str(p.relative_to(src)).replace('\\','/') not in changed}
(run/'preserved-files.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
im=Image.open(art/'original.png').convert('RGBA');bounds=[(8,330),(336,680),(686,1005),(1013,1403),(1409,1795),(1801,2172)];parts=[]
for i,(x1,x2) in enumerate(bounds):
    p=im.crop((x1,80,x2,620));b=p.getchannel('A').point(lambda a:255 if a>100 else 0).getbbox();p=p.crop(b);p.save(art/f'cell{i}.png');parts.append(p)
def fit(p,w,h):
    scale=min(w/p.width,h/p.height);return p.resize((max(1,round(p.width*scale)),max(1,round(p.height*scale))),Image.Resampling.NEAREST)
def canvas(p,size,w,h):
    out=Image.new('RGBA',(size,size));p=fit(p,w,h);out.alpha_composite(p,((size-p.width)//2,(size-p.height)//2));return out
def pair(name,p):
    for f in range(2):p.save(src/f'rltiles/holo/fx_{name}_{f}.png')
for stage,wh in enumerate([42,54]):canvas(parts[0],96,wh,wh).save(src/f'rltiles/holo/fx_lamybanquetcast0_{stage}.png')
for stage,wh in enumerate([68,68]):canvas(parts[0],96,wh,wh).save(src/f'rltiles/holo/fx_lamybanquetcast1_{stage}.png')
active=Image.new('RGBA',(32,32));p=fit(parts[1],30,13);active.alpha_composite(p,((32-p.width)//2,31-p.height));pair('lamybanquetactive',active)
for f,p in enumerate(parts[2:]):
    burst=canvas(p,96,[48,82,94,94][f],[48,82,94,94][f]);burst.save(art/f'burst{f}-96.png')
    for c in range(9):pair(f'lamybanquetburst{f}{c}',burst.crop((32*(c%3),32*(c//3),32*(c%3+1),32*(c//3+1))))
names=['lamybanquetcast0','lamybanquetcast1','lamybanquetactive']+[f'lamybanquetburst{f}{c}' for f in range(4) for c in range(9)]
p=src/'rltiles/dc-holo-feat.txt';s=p.read_text();s=s.replace('carrot HOLO_CARROT',''.join(f'fx_{n}_{f} HOLO_FX_{n.upper()}_{f}\n' for n in names for f in range(2))+'carrot HOLO_CARROT');p.write_text(s)
p=src/'holo-visual.h';s=p.read_text();s=s.replace(',carrot };',','+','.join(names)+',carrot };').replace('void lamy_chill_burst(','void lamy_banquet_burst(const coord_def &pos);\nvoid lamy_chill_burst(',1);p.write_text(s)
p=src/'holo-lamy.cc';s=p.read_text().replace('holo_visual::invocation("lamy",3,centre);','holo_visual::lamy_banquet_burst(centre);');p.write_text(s)
p=src/'holo-visual.cc';s=p.read_text()
s=s.replace('    flashes.clear();flash_kind=invocation_effect(g);','    flashes.clear();flash_kind=invocation_effect(g);\n    if(g=="lamy" && tier==5){flash_kind=effect::lamybanquetcast0;flashes.push_back(you.pos());return;}',1)
s=s.replace('const int frames=flash_kind==effect::night_korone5?4:', 'const int frames=flash_kind==effect::lamybanquetcast0?4:flash_kind==effect::night_korone5?4:',1)
s=s.replace('scaled_delay(flash_kind==effect::night_okayu5?', 'scaled_delay(flash_kind==effect::lamybanquetcast0?105:flash_kind==effect::night_okayu5?',1)
s=s.replace('if(g=="lamy")base=effect::frost;','if(g=="lamy")base=effect::lamybanquetactive;',1)
anchor='    // Keep the actual 3x3 strike footprint visible during render-only descent.'
s=s.replace(anchor,'''    // Split the generated 96px flower into native cells. Each cell uses the
    // same 3x3 radius/line predicate as combat and remains below all actors.
    if(flash_kind==effect::lamybanquetburst00 && !flashes.empty()
        && area(p,flashes.front(),1) && !cell_is_solid(p)) {
        const auto d=p-flashes.front();const int cell=(d.y+1)*3+d.x+1;
        result.push_back(effect(int(effect::lamybanquetburst00)+9*flash_frame+cell));
    }
'''+anchor,1)
s=s.replace('if(flash_kind!=effect::none && std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return flash_kind;', 'if(flash_kind!=effect::none && flash_kind!=effect::lamybanquetburst00\n        && std::find(flashes.begin(),flashes.end(),p)!=flashes.end())return flash_kind;',1)
s=s.replace('    span_x=span_y=1;', '''    span_x=span_y=1;
    if(flash_kind==effect::lamybanquetcast0 && !flashes.empty()) {
        if(p==flashes.front()-coord_def(1,1)){span_x=span_y=3;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }''',1)
s=s.replace('    if(kind==effect::carrot)return TILE_HOLO_CARROT;', '''    if(kind==effect::carrot)return TILE_HOLO_CARROT;
    if(kind==effect::lamybanquetcast0) {
        if(frame<0)frame=flash_frame;
        return TILE_HOLO_FX_LAMYBANQUETCAST0_0+std::min(3,std::max(0,frame));
    }''',1)
hook='''void lamy_banquet_burst(const coord_def &p) {
#ifdef USE_TILE_LOCAL
    if(holo_benchmark_active() || !you.see_cell(p))return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_LAMY_BANQUET_REVIEW"):nullptr;
    if(crawl_state.test && !dir)return;
    static int sequence=0;const int seq=++sequence;
    const auto before=crawl_state.test?fox_signature():std::string();
    for(int f=0;f<4;++f) {
        flashes.assign(1,p);flash_kind=effect::lamybanquetburst00;flash_frame=f;
        const auto saved=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved);
        if(dir) {
            const auto stem=std::string(dir)+"/lamy5-burst"+std::to_string(seq)+"-frame"+std::to_string(f);
            capture(stem+".png",false);
            int cells=0;for(int y=-1;y<=1;++y)for(int x=-1;x<=1;++x) {
                const auto effects=at(p+coord_def(x,y));
                for(auto e:effects)if(e>=effect::lamybanquetburst00 && e<=effect::lamybanquetburst38)++cells;
            }
            std::ofstream(stem+"-area.json")<<"{\\"centre\\":["<<p.x<<','<<p.y<<"],\\"radius\\":1,\\"frame\\":"<<f<<",\\"visibleFloorCells\\":"<<cells<<",\\"underActors\\":true}\\n";
        } else scaled_delay(110);
    }
    clear();const auto saved=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved);
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Lamy banquet visuals changed gameplay/RNG");
#endif
}
'''
s=s.replace('void lamy_chill_burst(',hook+'\nvoid lamy_chill_burst(',1);p.write_text(s)
p=src/'tilereg-dgn.cc';s=p.read_text();s=s.replace('|| cue==holo_visual::effect::foxcircle || cue==holo_visual::effect::foxflame);','|| cue==holo_visual::effect::foxcircle || cue==holo_visual::effect::foxflame\n                    || cue==holo_visual::effect::lamybanquetcast0);',1);p.write_text(s)
print('Prepared activation, following foot wreath and LOS-clipped under-actor 3x3 snowflower frames.')
