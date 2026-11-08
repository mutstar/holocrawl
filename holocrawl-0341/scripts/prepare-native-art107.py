"""Bake approved92/101/106 art into an isolated0.34.1 source tree."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'analysis/native-play107-01';SRC=RUN/'engine/crawl-ref/source'
ART=ROOT/'preview/city-facilities106';OUT=SRC/'rltiles/holocrawl'
plan=json.loads((RUN/'plan.json').read_text(encoding='utf-8'));assert plan['status']=='isolated-engine-copied'
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
directions=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
tiles=[]
for variant in range(8):
    texture=np.roll(np.roll(grain,variant*32,axis=1),(variant*3%8)*32,axis=0)
    for mask in range(256):
        rows=[list('.....') for _ in range(5)];rows[2][2]='#'
        for bit,(dx,dy) in enumerate(directions):
            if mask&(1<<bit):rows[2+dy][2+dx]='#'
        a,_,_=render(np.full((160,160,4),255,dtype='uint8'),[''.join(r) for r in rows],texture)
        im=Image.fromarray(a).crop((64,64,96,96));name=f'holo_city_wall78_{mask}_{variant}'
        assert im.getextrema()[3]==(255,255);im.save(OUT/f'{name}.png')
        tiles.append({'name':name,'sha256':hashlib.sha256(im.tobytes()).hexdigest()})
manifest=json.loads((ART/'manifest.json').read_text(encoding='utf-8'))
catalog=json.loads((SRC/'holo34-facilities.json').read_text(encoding='utf-8'))
byid={m['facility']:m for m in manifest['maps']};decalsets=[];facility_tiles=[]
for spec in catalog:
    id=spec['id'];m=byid[id];data=json.loads((ART/m['map']).read_text(encoding='utf-8'));o=m['origin'];w,h=o['width'],o['height']
    base=Image.open(ART/m['images']['new106']).convert('RGBA');opened=Image.open(ART/m['openImage']).convert('RGBA')
    visual=[list(r) for r in data['rows']]
    for y in range(1,h-1):
        for x in range(1,w-1):
            if data['rows'][o['y']+y][o['x']+x] in '#G':visual[o['y']+y][o['x']+x]='.'
    concrete,_,_=render(np.array(base),[''.join(r) for r in visual],grain)
    decal=[]
    for y in range(h):
        for x in range(w):
            index=y*w+x;name=f'holo_facility_{id}_{index}';xx,yy=(o['x']+x)*32,(o['y']+y)*32
            im=base.crop((xx,yy,xx+32,yy+32))
            perimeter=spec['rows'][y][x]=='#' and (x in (0,w-1) or y in (0,h-1))
            if perimeter:
                a=np.array(im);under=concrete[yy:yy+32,xx:xx+32];diff=np.any(a[:,:,:3]!=under[:,:,:3],axis=2)
                a[:,:,3]=np.where(diff,255,0).astype('uint8');im=Image.fromarray(a)
                if diff.any():decal.append(index)
            im.save(OUT/f'{name}.png')
            facility_tiles.append({'name':name,'perimeterDecal':perimeter,'sha256':hashlib.sha256(im.tobytes()).hexdigest()})
            if spec['rows'][y][x]=='+':opened.crop((xx,yy,xx+32,yy+32)).save(OUT/f'{name}_open.png')
    decalsets.append('{'+','.join(map(str,decal))+'}')
(SRC/'holo34-art107.inc').write_text('// Generated perimeter decal indices; catalog order preserved.\nconst std::set<int> city_decals107[] = {\n'+',\n'.join(decalsets)+'\n};\n')
# Put basic doors in the transparent feature atlas so the existing native floor
# underlay and foreground actor/item ordering are used by the real renderer.
decl='\n# HOLOCRAWL ART107\n%sdir holocrawl\n%back none\n%rim 0\n%shrink 0\n%weight 10\n'
for state in ['closed','open']:
    name=f'holo_city107_door_{state}';shutil.copy2(ROOT/f'preview/basic-doors101/glass-double-{state}32.png',OUT/f'{name}.png')
    decl+=name+' '+name.upper()+'\n'
feat=SRC/'rltiles/dc-feat.txt';text=feat.read_text(encoding='utf-8');assert '# HOLOCRAWL ART107' not in text;feat.write_text(text+decl)
(RUN/'art-inputs.json').write_text(json.dumps({'wallTiles':tiles,'facilityTiles':facility_tiles,'wallRenderer':'scripts/city_concrete_material92.py',
 'doorRevision':101,'facilityRevision':106,'dynamicPerimeter':True,'facilityCount':9},indent=2)+'\n')
plan['status']='artwork-prepared';(RUN/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print('Baked2048 wall92 tiles and9 facility106 tile sets; prepared101 basic doors and dynamic perimeter decals.')
