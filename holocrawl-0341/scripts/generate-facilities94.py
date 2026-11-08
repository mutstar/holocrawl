"""Nine explicit facility-art samples; one native facility on each fresh floor."""
from pathlib import Path
import hashlib,json,os,secrets,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];ENGINE=ROOT/'engine/upstream/crawl-ref/source'
RUN=ROOT/'analysis/native-facilities94';OUT=ROOT/'preview/city-facilities94'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exe=RUN/'crawl-facilities94.exe'
catalog={f['id']:f for f in json.loads((ENGINE/'holo34-facilities.json').read_text(encoding='utf-8'))}
ids=['holox','theater','dev','dining','gamers','fantasy','wheel','market','mountain']
seeds=secrets.SystemRandom().sample(range(100000000,1900000000),len(ids))
inputs={'originalExecutable':ENGINE/'crawl.exe','originalSource':ENGINE/'holo34-city.cc',
 'reviewExecutable':exe,'floorAtlas':ENGINE/'dat/tiles/floor.png','wallAtlas':ENGINE/'dat/tiles/wall.png',
 'featAtlas':ENGINE/'dat/tiles/feat.png','renderer92':ROOT/'scripts/city_concrete_material92.py'}
frozen={n:sha(p) for n,p in inputs.items()}
assert frozen['originalExecutable']=='2ac32df1d925b258522fa8d986d50b143d1f74d3ccedf9f7cac9497d89c0754c'
assert sha(ENGINE/'holo34-city.cc')==sha(RUN/'holo34-city.original.cc')
if (RUN/'plan.json').exists():
    plan=json.loads((RUN/'plan.json').read_text());assert plan['inputSha256']==frozen
    assert [e['facility'] for e in plan['samples']]==ids
    seeds=[e['seed'] for e in plan['samples']]
else:
    plan={'scope':'Nine forced single-facility art samples, not a frequency sample.',
     'samples':[{'facility':id,'seed':seed} for id,seed in zip(ids,seeds)],'inputSha256':frozen,
     'normalPlayPolicy':'Unchanged50% per floor, maximum1, no duplicates per run.', 'normalWallApprovedRevision':92}
    (RUN/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
env=os.environ.copy();env['HOLOCRAWL_CITY77']='1'
env.pop('HOLOCRAWL_CITY_REVIEW_SEED',None);env.pop('HOLOCRAWL_STREET01_MAP',None)
env['PATH']=str(ENGINE)+os.pathsep+env.get('PATH','')
rc=RUN/'test-init.txt';rc.write_text(f'save_dir = {(RUN/"saves").as_posix()}/\nmorgue_dir = {(RUN/"morgue").as_posix()}/\n')
with (RUN/'builddb-review.log').open('wb') as log:
    subprocess.run([str(exe),'-headless','-dir',str(ENGINE),'-rc',str(rc),'-builddb'],cwd=ENGINE,env=env,
                   stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
atlases={n:Image.open(ENGINE/f'dat/tiles/{n}.png').convert('RGBA') for n in ['floor','wall','feat']}
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
manifest={'title':'잔향도시 · 확정 일반벽92와 JP 시설','revision':94,'tileSize':32,
 'styles':[{'id':'integrated92','label':'확정 벽92 + 시설'},{'id':'original84','label':'기존 일반벽과 비교'}],
 'maps':[],'scope':plan['scope'],'ordinaryFacilityPolicyUnchanged':True}
checks=[];geometry=set()

for id,seed in zip(ids,seeds):
    target=RUN/'raw'/id;target.mkdir(parents=True,exist_ok=False)
    current=env.copy();current['HOLOCRAWL_CITY_FACILITY_REVIEW94']=id;current['HOLOCRAWL_CITY_FACILITY_SEED94']=str(seed)
    with (target/'native.log').open('wb') as log:
        subprocess.run([str(exe),'-headless','-dir',str(ENGINE),'-rc',str(rc),'-script','holo_city77',target.as_posix()],
                       cwd=ENGINE,env=current,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    nv=json.loads((target/'validation.json').read_text());assert nv['status']=='passed' and nv['facility']==id and nv['connected']
    path=target/f'map-{seed}-1.json';data=json.loads(path.read_text());o=data['origin'];spec=catalog[id]
    assert data['facility']==id and o['width']==spec['width'] and o['height']==spec['height']
    shape=hashlib.sha256(json.dumps(data['rows']).encode()).hexdigest();assert shape not in geometry;geometry.add(shape)
    image=Image.new('RGBA',(2560,2240))
    for y in range(70):
        for x in range(80):
            for layer in ['floors','features']:
                t=data['palette'][data[layer][y*80+x]]
                image.alpha_composite(atlases[t['atlas']].crop((t['sx'],t['sy'],t['sx']+t['width'],t['sy']+t['height'])),(x*32+t['dx'],y*32+t['dy']))
    base=np.array(image);a,wall,_=render(base,data['rows'],grain)
    x0,y0=o['x']*32,o['y']*32;x1,y1=x0+o['width']*32,y0+o['height']*32
    facility=np.zeros(wall.shape,dtype=bool);facility[y0:y1,x0:x1]=True
    a[facility]=base[facility]
    # Preserve themed interiors and the reviewed entrance. At solid-to-solid
    # exterior joins only, fade the outer4px dark backing toward the city cap.
    # No new frame, floor apron, pipe or furniture is added.
    seam=np.zeros(wall.shape,dtype=bool);shade=np.zeros(wall.shape,dtype=float)
    def set_strip(xa,ya,xb,yb,axis):
        for i,weight in enumerate([.48,.32,.18,.08]):
            if axis=='top':sl=(slice(ya+i,ya+i+1),slice(xa,xb))
            elif axis=='bottom':sl=(slice(yb-i-1,yb-i),slice(xa,xb))
            elif axis=='left':sl=(slice(ya,yb),slice(xa+i,xa+i+1))
            else:sl=(slice(ya,yb),slice(xb-i-1,xb-i))
            shade[sl]=np.maximum(shade[sl],weight)
    for ly,row in enumerate(spec['rows']):
        for lx,c in enumerate(row):
            if c!='#':continue
            gx,gy=o['x']+lx,o['y']+ly;xa,ya=gx*32,gy*32
            for condition,dx,dy,axis in [(ly==0,0,-1,'top'),(ly==o['height']-1,0,1,'bottom'),(lx==0,-1,0,'left'),(lx==o['width']-1,1,0,'right')]:
                if condition and data['rows'][gy+dy][gx+dx]=='#':set_strip(xa,ya,xa+32,ya+32,axis)
    rgb=base[:,:,:3].astype(float)
    seam=(shade>0)&facility&wall&(rgb.max(axis=2)<100)&((rgb.max(axis=2)-rgb.min(axis=2))<55)
    a[seam,:3]=np.rint(rgb[seam]*(1-shade[seam,None])+np.array([31,37,40])*shade[seam,None]).astype('uint8')
    assert np.array_equal(a[facility&~seam],base[facility&~seam])
    assert np.array_equal(a[~wall],base[~wall])
    entrances=[]
    for lx,c in enumerate(spec['rows'][-1]):
        gx=o['x']+lx;gy=o['y']+o['height']-1
        if c in '.+' and data['rows'][gy+1][gx] not in '#G~':entrances.append({'x':gx,'y':gy})
    assert entrances
    for p in entrances:
        xx,yy=p['x']*32,p['y']*32
        assert np.array_equal(a[yy:yy+32,xx:xx+32],base[yy:yy+32,xx:xx+32])
    before=f'{id}-original84.png';after=f'{id}-integrated92.png'
    image.convert('RGB').save(OUT/before);Image.fromarray(a).convert('RGB').save(OUT/after)
    (OUT/f'{id}-map.json').write_bytes(path.read_bytes())
    crop=(max(0,x0-64),max(0,y0-64),min(2560,x1+64),min(2240,y1+96))
    Image.fromarray(a).crop(crop).convert('RGB').save(OUT/f'{id}-facility.png')
    manifest['maps'].append({'seed':seed,'depth':1,'facility':id,'name':spec['name'],'width':80,'height':70,
       'origin':o,'entrances':entrances,'focus':{'x':o['x']+o['width']/2,'y':o['y']+o['height']/2},
       'images':{'integrated92':after,'original84':before},'map':f'{id}-map.json','mapSha256':sha(path)})
    checks.append({'facility':id,'seed':seed,'nativeConnected':True,'entrancePreserved':True,'interiorPreservedOutsideContactBand':True,
       'contactBandPixels':int(seam.sum()),'nonWallPixelsChanged':0,'normal92RetainedOutsideFacility':True})
    (RUN/'state.json').write_text(json.dumps({'status':'running','completed':len(checks),'scheduled':9},indent=2)+'\n')
    print(f'Prepared {id}: native connected floor, preserved entrance and interior.',flush=True)

font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
sheet=Image.new('RGB',(1296,1530),'#151c20');d=ImageDraw.Draw(sheet)
for i,m in enumerate(manifest['maps']):
    ox=(i%3)*432;oy=(i//3)*510
    d.text((ox+12,oy+8),m['name'],font=font,fill='#dbe6e2')
    im=Image.open(OUT/f'{m["facility"]}-facility.png');im.thumbnail((408,462),Image.Resampling.NEAREST)
    sheet.paste(im,(ox+12,oy+40))
sheet.save(OUT/'all-facilities.png')
assert frozen=={n:sha(p) for n,p in inputs.items()}
v={'status':'passed','nativeFloors':9,'facilitiesCovered':9,'uniqueGeometries':len(geometry),'checks':checks,
   'frozenInputsUnchanged':True,'originalEngineRestored':True,'normalWallApprovedRevision':92,'nativeIntegration':False,
   'scope':plan['scope'],'normalPlayFrequencyUnchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n');(RUN/'material-validation.json').write_text(json.dumps(v,indent=2)+'\n')
(RUN/'state.json').write_text(json.dumps({'status':'passed','completed':9,'scheduled':9},indent=2)+'\n')
print('Prepared nine new native floors with one facility each; original engine and policy preserved.',flush=True)
