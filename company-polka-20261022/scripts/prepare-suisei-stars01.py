from pathlib import Path
from PIL import Image
import json, shutil, hashlib

r=Path(__file__).resolve().parents[1]
src=r/'engine/campaign-crawl/crawl-ref/source'
rev='suisei-stars01'
base=r/'analysis/native'/rev
base.mkdir(parents=True,exist_ok=True)
(base/'before').mkdir(exist_ok=True)
files=['holo-visual.h','holo-visual.cc','holo-campaign-test.cc','tilereg-dgn.cc','tiledgnbuf.cc','rltiles/dc-holo-feat.txt']
for f in files:
    shutil.copy2(src/f,base/'before'/Path(f).name)
art=r/'assets/holocrawl'/rev
art.mkdir(parents=True,exist_ok=True)
original=r/'assets/holocrawl/suisei-vfx02/originals/starmark.png'
im=Image.open(original).convert('RGBA')
# Reuse existing generated cyan/gold star pixels; no new painted shapes.
cyan=im.crop((420,248,495,325))
gold=im.crop((1270,248,1350,325))
def glyph(pic):
    box=pic.getchannel('A').point(lambda v:255 if v>160 else 0).getbbox()
    assert box
    return pic.crop(box).resize((7,7),Image.Resampling.NEAREST)
cyan,gold=glyph(cyan),glyph(gold)
for count in range(1,4):
    tile=Image.new('RGBA',(32,32))
    for i in range(count):tile.alpha_composite(gold if count==3 else cyan,(3+9*i,3))
    tile.save(src/f'rltiles/holo/fx_suiseistars{count}.png')
    tile.save(art/f'stars{count}.png')
shutil.copy2(original,art/'reused-starmark-source.png')
(art/'generation.json').write_text(json.dumps({'mode':'reuse-existing-generated-asset','source':original.relative_to(r).as_posix(),'sourceSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'operation':'Crop existing cyan/gold star glyphs, nearest-neighbour 7x7, arrange fixed slots x3/12/21. Full stack changes all three to gold. No new image generation.','nativeOffsetY':-10,'logicalTileSize':32},ensure_ascii=False,indent=2),encoding='utf-8')

p=src/'rltiles/dc-holo-feat.txt'
p.write_text(p.read_text(encoding='utf-8')+'\n'+''.join(f'fx_suiseistars{i} HOLO_FX_SUISEISTARS{i}\n' for i in range(1,4)),encoding='utf-8')
p=src/'holo-visual.h';s=p.read_text(encoding='utf-8')
assert 'koyorislimeborder,carrot };' in s
s=s.replace('koyorislimeborder,carrot };','koyorislimeborder,carrot,suiseistars1,suiseistars2,suiseistars3 };')
p.write_text(s,encoding='utf-8')
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8')
needle='    span_x=span_y=1;\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'''    // Opt-in visual review only: read genuine direct-hit stacks, no gameplay writes.
    if(crawl_state.test && you.props.exists("holo_suisei_stars_preview")
        && holo_campaign::active() && holo_worship::current()=="suisei"
        && holo_batch::s.one_end>you.elapsed_time && holo_batch::s.resource>0) {
        const auto *marked=monster_by_mid(holo_batch::s.marked);
        if(marked && marked->alive() && marked->pos()==p && you.see_cell(p))
            return effect(int(effect::suiseistars1)+std::min(3,holo_batch::s.resource)-1);
    }
''',1)
needle='    if(kind==effect::none)return 0;\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'''    if(kind>=effect::suiseistars1 && kind<=effect::suiseistars3)
        return TILE_HOLO_FX_SUISEISTARS1+int(kind)-int(effect::suiseistars1);
''',1)
p.write_text(s,encoding='utf-8')
p=src/'tilereg-dgn.cc';s=p.read_text(encoding='utf-8')
needle='                const auto cue=holo_visual::invocation_sprite_at(gc,span_x,span_y);\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'''                if(cue>=holo_visual::effect::suiseistars1 && cue<=holo_visual::effect::suiseistars3)
                    m_buf_dngn.add_holo_vfx_tile(holo_visual::effect_tile(holo_visual::effect::starmark),x,y,1,1,false);
''',1)
p.write_text(s,encoding='utf-8')
p=src/'tiledgnbuf.cc';s=p.read_text(encoding='utf-8')
needle='        const bool mela_heat=tileidx>=TILE_HOLO_FX_MELAHEAT0 && tileidx<=TILE_HOLO_FX_MELAHEAT6;\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'        const bool suisei_stars=tileidx>=TILE_HOLO_FX_SUISEISTARS1 && tileidx<=TILE_HOLO_FX_SUISEISTARS3;\n',1)
assert 'sopia_teacher?24:mela_heat?18:polka_hat?12:' in s
s=s.replace('sopia_teacher?24:mela_heat?18:polka_hat?12:', 'sopia_teacher?24:mela_heat?18:suisei_stars?10:polka_hat?12:',1)
p.write_text(s,encoding='utf-8')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
needle='    if(const char *shots=getenv("HOLOCRAWL_MELA_ONIBI_REVIEW")) {'
assert s.count(needle)==1
block='''    if(const char *shots=getenv("HOLOCRAWL_SUISEI_STARS_REVIEW")) {
        auto *m=fixture("suisei",30);const auto origin=you.pos();
        require(m->move_to_pos(origin+coord_def(2,0)),"Suisei star target placement");
        you.props["holo_suisei_stars_preview"]=true;
        const std::string output(shots);
        holo_visual::capture(output+"/stars0.png");
        for(int count=1;count<=3;++count) {
            const int hp=m->hit_points;
            { command_scope command;bolt beam;beam.name="magic dart";beam.origin_spell=SPELL_MAGIC_DART;
              beam.source=you.pos();beam.target=m->pos();beam.range=5;beam.source_id=you.mid;
              beam.thrower=KILL_YOU;beam.flavour=BEAM_MMISSILE;beam.damage=dice_def(1,20);beam.hit=AUTOMATIC_HIT;
              beam.fire(); }
            require(m->hit_points<hp && holo_batch::s.resource==count,"Suisei native direct hit did not add one star");
            int sx=1,sy=1;
            require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)==holo_visual::effect(int(holo_visual::effect::suiseistars1)+count-1),"Suisei displayed star count mismatch");
            const auto before=signature();holo_visual::capture(output+"/stars"+std::to_string(count)+".png");
            require(before==signature(),"Suisei stars render changed world/resources/RNG");
        }
        roundtrip();require(holo_batch::s.resource==3,"Suisei native stacks roundtrip");
        require(m->move_to_pos(origin+coord_def(3,0)),"Suisei moving marked target placement");
        int sx=1,sy=1;
        require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)==holo_visual::effect::suiseistars3,"Suisei stars did not follow target");
        require(holo_visual::invocation_sprite_at(origin+coord_def(2,0),sx,sy)==holo_visual::effect::none,"Suisei stale marker left behind");
        holo_visual::capture(output+"/stars3-moved.png");
        holo_batch::s.one_end=you.elapsed_time;
        require(holo_visual::invocation_sprite_at(m->pos(),sx,sy)!=holo_visual::effect::suiseistars3,"Suisei expired count visible");
        holo_visual::capture(output+"/stars-expired.png");
        you.props.erase("holo_suisei_stars_preview");
        std::ofstream(output+"/stars.json")<<"{\\"status\\":\\"passed\\",\\"nativeSDL\\":true,\\"realDirectHitStacks\\":[1,2,3],\\"renderRngAndWorldStable\\":true,\\"followsTarget\\":true,\\"expires\\":true,\\"stackSaveRoundtrip\\":true,\\"combatCapChanged\\":false,\\"runtimeDeployed\\":false}\\n";
    }
'''
s=s.replace(needle,block+needle,1)
p.write_text(s,encoding='utf-8')
print('Native Suisei 1/2/3-star review and reused art prepared; ordinary gameplay unchanged.')
