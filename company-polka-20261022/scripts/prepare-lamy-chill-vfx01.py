from pathlib import Path
from PIL import Image
import json, shutil, hashlib

r=Path(__file__).resolve().parents[1]
src=r/'engine/campaign-crawl/crawl-ref/source'
run=r/'analysis/native/lamy-chill-vfx01'
art=r/'assets/holocrawl/lamy-chill-vfx01'
files=['holo-lamy.cc','holo-visual.cc','holo-visual.h','holo-campaign-test.cc','rltiles/dc-holo-feat.txt']
for name in files:
    p=run/'before'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/name,p)
shutil.copy2(r/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
baseline={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob('*.cc') if p.name not in files}
(run/'preserved-source.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
im=Image.open(art/'original.png').convert('RGBA')
rects=[(120,200,275,570),(340,200,615,570),(680,170,1010,590),(1040,170,1395,590),(1400,170,1790,590),(1800,170,2140,590)]
parts=[]
for i,rect in enumerate(rects):
    p=im.crop(rect);bbox=p.getchannel('A').point(lambda v:255 if v>100 else 0).getbbox();p=p.crop(bbox);p.save(art/f'cell{i}.png');parts.append(p)

def fitted(p,w,h):
    q=min(w/p.width,h/p.height);return p.resize((max(1,round(p.width*q)),max(1,round(p.height*q))),Image.Resampling.NEAREST)
def save_pair(name,p,size,box):
    a=Image.new('RGBA',(size,size));q=fitted(p,box[2],box[3]);a.alpha_composite(q,(box[0]+(box[2]-q.width)//2,box[1]+(box[3]-q.height)//2))
    for f in range(2):a.save(src/f'rltiles/holo/fx_{name}_{f}.png')
save_pair('lamychill1',parts[0],32,(23,1,8,8))
save_pair('lamychill2',parts[1],32,(18,1,13,8))
save_pair('lamyslow',parts[0],32,(23,22,8,8))
for f,p in enumerate(parts[2:]):save_pair(f'lamyburst{f}',p,96,(24,24,48,48))

p=src/'rltiles/dc-holo-feat.txt';s=p.read_text(encoding='utf-8');names=['lamychill1','lamychill2','lamyslow']+[f'lamyburst{i}' for i in range(4)]
s=s.replace('carrot HOLO_CARROT',''.join(f'fx_{n}_{f} HOLO_FX_{n.upper()}_{f}\n' for n in names for f in range(2))+'carrot HOLO_CARROT');p.write_text(s,encoding='utf-8')
p=src/'holo-visual.h';s=p.read_text();s=s.replace(',carrot };',','+','.join(names)+',carrot };').replace('void impact(const coord_def','void lamy_chill_burst(const coord_def &pos);\nvoid impact(const coord_def');p.write_text(s)
p=src/'holo-visual.cc';s=p.read_text()
mark='''effect lamy_mark(const coord_def &p) {
    if(!holo_campaign::active() || holo_worship::current()!="lamy")return effect::none;
    const auto &s=holo_batch::s;const int now=you.elapsed_time;
    for(const auto &entry:s.targets) {
        const auto *m=monster_by_mid(entry.first);
        if(!m || !m->alive() || m->pos()!=p || !you.can_see(*m))continue;
        const auto &t=entry.second;
        if(t.expires>now && t.stacks>0)return t.stacks>=2?effect::lamychill2:effect::lamychill1;
        if(t.slowed_until>now)return effect::lamyslow;
    }
    return effect::none;
}
'''
s=s.replace('effect choco_mark(',mark+'\neffect choco_mark(',1)
s=s.replace('    const auto choco=choco_mark(p);','    const auto lamy=lamy_mark(p);if(lamy!=effect::none)return lamy;\n    const auto choco=choco_mark(p);',1)
s=s.replace('    span_x=span_y=1;','''    span_x=span_y=1;
    if(flash_kind>=effect::lamyburst0 && flash_kind<=effect::lamyburst3 && !flashes.empty()) {
        if(p==flashes.front()-coord_def(1,1)){span_x=span_y=3;return flash_kind;}
        if(p==flashes.front())return effect::none;
    }''',1)
animation='''void lamy_chill_burst(const coord_def &p) {
#ifdef USE_TILE_LOCAL
    if(holo_benchmark_active() || !you.see_cell(p))return;
    const char *dir=crawl_state.test?getenv("HOLOCRAWL_LAMY_CHILL_REVIEW"):nullptr;
    if(crawl_state.test && !dir)return;
    const auto before=crawl_state.test?fox_signature():std::string();
    static int sequence=0;const int seq=++sequence;
    for(int f=0;f<4;++f) {
        flashes.assign(1,p);flash_kind=effect(int(effect::lamyburst0)+f);flash_frame=0;
        const auto saved_rng=rng::generators_to_vector();redraw_fox_actors();rng::load_generators(saved_rng);
        if(dir)capture(std::string(dir)+"/lamy3-burst"+std::to_string(seq)+"-frame"+std::to_string(f)+".png",false);
        else scaled_delay(95);
    }
    clear();tiles.invalidate_dungeon_overlays();update_screen();
    if(crawl_state.test && before!=fox_signature())throw std::runtime_error("Lamy burst visuals changed gameplay/RNG");
#endif
}
'''
s=s.replace('void impact(const coord_def',animation+'\nvoid impact(const coord_def',1);p.write_text(s)
p=src/'holo-lamy.cc';s=p.read_text();s=s.replace('        hurt(mon,roll_dice(2,3+s.inv/6),BEAM_COLD,false);','        const auto pos=mon.pos();\n        hurt(mon,roll_dice(2,3+s.inv/6),BEAM_COLD,false);\n        holo_visual::lamy_chill_burst(pos);',1);p.write_text(s)

p=src/'holo-campaign-test.cc';s=p.read_text();anchor='    if(const char *shots=getenv("HOLOCRAWL_LAMY_HUD_REVIEW")) {'
test='''    if(const char *shots=getenv("HOLOCRAWL_LAMY_CHILL_REVIEW")) {
        using namespace holo_batch;
        auto *m=fixture("lamy");const mid_t mid=m->mid;const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Lamy chill visible target setup");
        s.resource=40;
        set_skill_level(SK_ICE_MAGIC,27);set_skill_level(SK_SPELLCASTING,27);
        you.duration[DUR_BRILLIANCE]=100;
        auto shot=[&](const char *name){const auto stable=signature();holo_visual::capture(std::string(shots)+"/lamy3-"+name+".png");require(stable==signature(),"Lamy chill capture mutated gameplay/RNG");};
        shot("before");
        for(int i=1;i<=3;++i) {
            require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success,"Lamy chill actual spell");
            require(s.targets[mid].stacks==i%3,"Lamy chill real spell stack progression");
            shot(("cast"+std::to_string(i)).c_str());step(10);
        }
        require(s.targets[mid].slowed_until>you.elapsed_time,"Lamy chill slow active");
        roundtrip();m=monster_by_mid(mid);shot("restored");
        step(20);shot("slow-expired");
        require(holo_visual::invocation_at(m->pos())==holo_visual::effect::none,"Lamy slow marker expiry");
        require(your_spells(SPELL_OZOCUBUS_REFRIGERATION,40,true)==spret::success,"Lamy expiry cast");
        shot("expiry-stack");step(60);shot("stack-expired");
        require(holo_visual::invocation_at(m->pos())==holo_visual::effect::none,"Lamy stack marker expiry");
        fixture("towa");require(holo_visual::invocation_at(you.pos()+coord_def(2,0))==holo_visual::effect::none,"Lamy marker other god");
        std::ofstream(dir+"/lamy-chill-vfx.json")<<"{\\"status\\":\\"passed\\",\\"realSpellCasts\\":4,\\"stackProgression\\":[1,2,0],\\"expiry\\":true,\\"saveRestore\\":true,\\"renderingStateUnchanged\\":true}\\n";
    }
'''
assert anchor in s;s=s.replace(anchor,test+anchor,1);p.write_text(s)

p=r/'VFX_DRAFT_STATUS.json';d=json.loads(p.read_text(encoding='utf-8'));d['tierApprovals']['lamy'].update(approved=[1],pending=[3,5],tier1Revision='lamy-caster01',tier1Feedback='ㅇㅇ좋다 라미 3성 이펙트도 보자',pendingRevision='lamy-chill-vfx01');d['next']='Review Lamy tier3 passive chill stacks and shatter burst';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared Lamy tier3 sprites, render-only hooks, and native capture controls.')
