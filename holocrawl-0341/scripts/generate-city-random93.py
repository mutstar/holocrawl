"""One fresh native city floor, displayed with the unchanged repaired92 material."""
from pathlib import Path
import hashlib,json,os,secrets,subprocess
import numpy as np
from PIL import Image
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine/upstream/crawl-ref/source'
OUT=ROOT/'preview/city-random93'
RUN=ROOT/'analysis/native-city-random93'
OUT.mkdir(parents=True,exist_ok=False)
RUN.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs={'binary':ENGINE/'crawl.exe','wallAtlas':ENGINE/'dat/tiles/wall.png',
        'renderer':ROOT/'scripts/city_concrete_material92.py'}
frozen={name:sha(p) for name,p in inputs.items()}
seed=secrets.randbelow(1800000000)+100000000
plan={'seed':seed,'depth':1,'facility':False,'nativeBuilder':True,'nativeArtRevision':84,'previewWallRevision':92,
      'inputSha256':frozen,'scope':'One fresh native geometry with the already reviewed92 wall material.'}
(RUN/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
# The reusable renderer must match the exact reviewed92 image before new work.
old=ROOT/'preview/city-concrete92'
oldmap=json.loads((ROOT/'preview/wall-audit85/maps/map-802302584-1.json').read_text())
oldbase=np.array(Image.open(old/'802302584-original84.png').convert('RGBA'))
old92,_,_=render(oldbase,oldmap['rows'],grain)
assert np.array_equal(old92,np.array(Image.open(old/'802302584-concrete92.png').convert('RGBA')))
del oldbase,old92

rc=RUN/'test-init.txt'
rc.write_text(f'save_dir = {(RUN/"saves").as_posix()}/\nmorgue_dir = {(RUN/"morgue").as_posix()}/\n')
env=os.environ.copy();env['HOLOCRAWL_CITY77']='1';env['HOLOCRAWL_CITY_REVIEW_SEED']=str(seed)
env.pop('HOLOCRAWL_STREET01_MAP',None)
for name,args in [('builddb',['-builddb']),('native',['-script','holo_city77',RUN.as_posix()])]:
    with (RUN/f'{name}.log').open('wb') as log:
        subprocess.run([str(ENGINE/'crawl.exe'),'-headless','-dir',str(ENGINE),'-rc',str(rc),*args],
                       cwd=ENGINE,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
native=json.loads((RUN/'validation.json').read_text())
assert native['status']=='passed' and native['seed']==seed and native['connected'] and native['facility'] is False
map_path=RUN/f'map-{seed}-1.json';data=json.loads(map_path.read_text())
assert data['width']==80 and data['height']==70 and data['facility'] is None and data['origin'] is None
assert data['rows']!=oldmap['rows']
assert data['rows']!=json.loads((ROOT/'preview/city-random82/map.json').read_text())['rows']
atlases={name:Image.open(ENGINE/f'dat/tiles/{name}.png').convert('RGBA') for name in ['floor','wall','feat']}
image=Image.new('RGBA',(data['width']*32,data['height']*32))
for y in range(data['height']):
    for x in range(data['width']):
        for layer in ['floors','features']:
            t=data['palette'][data[layer][y*data['width']+x]]
            part=atlases[t['atlas']].crop((t['sx'],t['sy'],t['sx']+t['width'],t['sy']+t['height']))
            image.alpha_composite(part,(x*32+t['dx'],y*32+t['dy']))
base=np.array(image);result,walls,repaired=render(base,data['rows'],grain)
assert np.array_equal(result[~walls],base[~walls])
image.convert('RGB').save(OUT/f'{seed}-original84.png')
Image.fromarray(result).convert('RGB').save(OUT/f'{seed}-concrete92.png')
(OUT/'map.json').write_bytes(map_path.read_bytes())
candidate=[]
for y in range(2,68):
    for x in range(2,78):
        block=[data['rows'][y+dy][x+dx]=='#' for dx,dy in [(0,0),(1,0),(0,1),(1,1)]]
        if sum(block)==3:candidate.append((abs(x-40)+abs(y-35),x,y))
_,fx,fy=min(candidate)
entry={'seed':seed,'width':80,'height':70,'focus':{'x':fx+.5,'y':fy+.5},'images':{
 'concrete92':f'{seed}-concrete92.png','original84':f'{seed}-original84.png'}}
manifest={'title':'잔향도시 새 랜덤 지도 · 접합 수정92','revision':93,'tileSize':32,'maps':[entry],
 'styles':[{'id':'concrete92','label':'접합 채운 최신 벽92'},{'id':'original84','label':'기존 도시벽84'}],
 'nativeMapSha256':sha(map_path),'scope':plan['scope']}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert frozen=={name:sha(p) for name,p in inputs.items()}
validation={'status':'passed','seed':seed,'nativeValidation':native,'newGeometry':True,'connected':True,'facility':False,
 'reviewed92RendererPixelMatch':True,'frozenInputsUnchanged':True,'nonWallPixelsChanged':0,
 'alphaUnchanged':bool(np.array_equal(base[:,:,3],result[:,:,3])),'repairedJoinPixels':int(repaired.sum()),
 'nativeMapSha256':sha(map_path),'nativeIntegration':False,'scope':plan['scope']}
(RUN/'material-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps({'status':'passed','seed':seed,'connected':True,'preview':'city-random93/'}),flush=True)
