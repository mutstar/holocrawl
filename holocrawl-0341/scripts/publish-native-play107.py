"""Verify compiled art/runtime evidence and publish only native-generated data."""
from pathlib import Path
import json,re,shutil,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'analysis/native-play107-01';S=RUN/'engine/crawl-ref/source'
SUITE=RUN/'suite-10';OUT=ROOT/'preview/native-play107';(OUT/'maps').mkdir(exist_ok=True);(OUT/'assets').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((RUN/'plan.json').read_text());generation=json.loads((SUITE/'generation-validation.json').read_text());oracle=json.loads((SUITE/'oracle-validation.json').read_text())
assert generation['status']==oracle['status']=='passed' and generation['totalFloors']==oracle['maps']==177
assert generation['binarySha256']==sha(S/'crawl.exe') and oracle['mismatches']==0
for name,expected in plan['baseline'].items():assert sha(ROOT/name)==expected,('Original input changed',name)
atlases={n:Image.open(S/f'dat/tiles/{n}.png').convert('RGBA') for n in ['floor','wall','feat','main','player']}
coord_names={};art_checks=0
for atlas in ['floor','wall','feat']:
    text=(S/f'rltiles/tiledef-{atlas}.cc').read_text()
    info=[tuple(map(int,v.split(','))) for v in re.findall(r'tile_info\((\d[^)]*)\)',text)]
    for name,number in re.findall(r'_name_pair\("(holo_[^" ]+)", (\d+) \+ (?:0|TILE_FLOOR_MAX|TILE_WALL_MAX)\)',text):
        n=int(number);width,height,dx,dy,sx,sy,ex,ey=info[n]
        assert 0<=dx<=32 and 0<=dy<=32 and ex-sx+dx<=32 and ey-sy+dy<=32,(name,info[n])
        actual=Image.new('RGBA',(32,32));actual.alpha_composite(atlases[atlas].crop((sx,sy,ex,ey)),(dx,dy))
        expected=Image.open(S/f'rltiles/holocrawl/{name}.png').convert('RGBA')
        a,b=np.array(actual),np.array(expected);assert np.array_equal(a[:,:,3],b[:,:,3]),name
        assert np.array_equal(a[b[:,:,3]>0,:3],b[b[:,:,3]>0,:3]),name
        coord_names[(atlas,sx,sy,ex-sx,ey-sy,dx,dy)]=name;art_checks+=1
assert art_checks>=2760
buf=(S/'tiledgnbuf.cc').read_text();draw=buf[buf.index('void DungeonCellBuffer::draw_tiles()'):buf.index('void DungeonCellBuffer::draw_icons()')]
assert draw.index('m_buf_wall.draw()')<draw.index('m_buf_city_decal.draw()')<draw.index('m_buf_doll.draw()')<draw.index('m_buf_main.draw()')
assert 'm_buf_city_decal.clear();' in buf and 'm_buf_city_decal.add(tile,x,y);' in buf
catalog=json.loads((S/'holo34-facilities.json').read_text(encoding='utf-8'));specs={e['id']:e for e in catalog}
names={'mountain':'0기생 페이스 마운틴','dining':'1기생 타라후쿠 저니','theater':'2기생 극장','gamers':'게이머즈 폐역','fantasy':'3기생 운동장','wheel':'4기생 관람차','market':'5기생 마트','holox':'holoX 연구소','dev':'DEV_IS 출장소'}
dirs=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
def tile_name(t):return coord_names.get((t['atlas'],t['sx'],t['sy'],t['width'],t['height'],t['dx'],t['dy']))
paths=[]
for id in ['theater','gamers','holox','dev','dining','fantasy','wheel','market','mountain']:paths+=list((SUITE/f'forced-{id}').glob('map-*.json'))
paths+=sorted((SUITE/'random168').glob('map-*.json'),key=lambda p:tuple(map(int,p.stem.split('-')[1:])))
entries=[];wallchecks=0;perimeters=0;actorchecks=0;replays=0;players=None
for path in paths:
    data=json.loads(path.read_text());id=data['facility'];spec=specs.get(id);o=data['origin'];w,h=data['width'],data['height'];forced=path.parent.name.startswith('forced-')
    replay=RUN/'suite-09'/path.relative_to(SUITE)
    assert replay.read_bytes()==path.read_bytes(),('Native repeat changed map',path);replays+=1
    def solid(x,y):
        if not (0<=x<w and 0<=y<h):return False
        if o and o['x']<x<o['x']+o['width']-1 and o['y']<y<o['y']+o['height']-1:
            if spec['rows'][y-o['y']][x-o['x']] in '#G':return False
        return data['rows'][y][x] in '#G+'
    for y in range(h):
        for x in range(w):
            i=y*w+x;t=data['palette'][data['features'][i]];name=tile_name(t)
            if t['atlas']=='wall' and name and name.startswith('holo_city_wall78_'):
                mask=sum(1<<bit for bit,(dx,dy) in enumerate(dirs) if solid(x+dx,y+dy))
                variant=(data['seed']^(x*374761393)^(y*668265263))%8
                assert name==f'holo_city_wall78_{mask}_{variant}',(path,x,y,name,mask,variant);wallchecks+=1
            if o and o['x']<=x<o['x']+o['width'] and o['y']<=y<o['y']+o['height']:
                lx,ly=x-o['x'],y-o['y'];c=spec['rows'][ly][lx]
                assert data['rows'][y][x]==('G' if c=='F' else c),(id,lx,ly,c,data['rows'][y][x])
                if c=='#' and (lx in (0,o['width']-1) or ly in (0,o['height']-1)):
                    assert name and name.startswith('holo_city_wall78_');perimeters+=1
                if c=='+':assert name==f'holo_facility_{id}_{ly*o["width"]+lx}'
            elif data['rows'][y][x]=='+':assert name=='holo_city107_door_closed'
    probe_path=path.parent/f'probe-{data["seed"]}-{data["depth"]}.json';probe=json.loads(probe_path.read_text())
    if forced:
        assert [a['kind'] for a in probe['actors']]==['player','monster','item']
        assert len(probe['actors'][0]['tiles'])>=3
        for a in probe['actors']:
            assert data['passable'][a['y']*w+a['x']]
            for t in a['tiles']:assert t['dx']>=0 and t['dy']>=0 and t['width']+t['dx']<=32 and t['height']+t['dy']<=32
            actorchecks+=1
        players=probe['actors'][0]['tiles']
    shutil.copy2(path,OUT/'maps'/path.name);shutil.copy2(probe_path,OUT/'maps'/probe_path.name)
    entries.append({'file':'maps/'+path.name,'probe':'maps/'+probe_path.name,'seed':data['seed'],'depth':data['depth'],'facility':id,'name':names.get(id,'일반 구역'),'forced':forced,'sha256':sha(path)})
for n in atlases:shutil.copy2(S/f'dat/tiles/{n}.png',OUT/f'assets/{n}.png')
assert len(entries)==177 and actorchecks==27 and replays==177
manifest={'revision':107,'engine':'DCSS0.34.1','maps':entries,'playerTiles':players,'nativeDiagonalCornerAllowed':oracle['diagonalCornerAllowed']==oracle['diagonalCornerCases'],
 'source':'Fresh native builder exports and native compiled tile coordinates; no browser art replacement.', 'validation':'validation.json'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result={'status':'passed','version':107,'nativeFloors':177,'normalScheduleFloors':168,'forcedFacilityFloors':9,'facilitiesCovered':9,
 'compiledArtTilesCompared':art_checks,'nativeWallTilesCompared':wallchecks,'dynamicFacilityPerimeterCells':perimeters,'nativeActorItemPlacements':actorchecks,
 'nativeReplayIdenticalMaps':replays,'originalEngineInputsUnchanged':True,'foregroundDrawOrderChecked':True,'atlasSha256':{n:sha(S/f'dat/tiles/{n}.png') for n in atlases},
 'binarySha256':sha(S/'crawl.exe'),'nativeOracle':oracle,'nativeGeneration':json.loads((SUITE/'random168/validation.json').read_text()),
 'scope':'Generation, native movement/door/LOS, compiled art and controlled actor/item layering. Combat/reward/campaign design excluded.'}
(RUN/'material-validation.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['nativeOracle','nativeGeneration','atlasSha256','scope']}))
