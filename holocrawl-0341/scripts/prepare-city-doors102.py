"""Approved glass double doors on preserved native facility floors; art preview only."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'preview/city-facilities95'; OUT=ROOT/'preview/city-doors102'
OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
door_dir=ROOT/'preview/basic-doors101'
sprites={s:Image.open(door_dir/f'glass-double-{s}32.png').convert('RGBA') for s in ['closed','open']}
atlases={s:Image.open(ROOT/f'engine/upstream/crawl-ref/source/dat/tiles/{s}.png').convert('RGBA') for s in ['floor','wall','feat']}
manifest={**prior,'title':'잔향도시 · 세로창 양개문 적용 전체맵','revision':102,
 'styles':[{'id':'new102','label':'세로창 양개문 적용'},{'id':'previous95','label':'기존 기본문'}],
 'maps':[],'defaultSample':2,'approvedDoorRevision':101,'nativeIntegration':False,
 'scope':'Existing native door cells only; one forced facility per review floor. Facility doors remain draft95.'}
checks=[]
for m in prior['maps']:
    data=json.loads((SRC/m['map']).read_text()); origin=m['origin']; w,h=m['width'],m['height']
    base=Image.open(SRC/m['images']['new95']).convert('RGBA'); before=np.array(base)
    cells=[{'x':x,'y':y,'width':1} for y,row in enumerate(data['rows']) for x,c in enumerate(row)
           if c=='+' and not (origin['x']<=x<origin['x']+origin['width'] and origin['y']<=y<origin['y']+origin['height'])]
    mask=np.zeros((h*32,w*32),dtype=bool); outputs={}
    for state in ['closed','open']:
        image=base.copy()
        for p in cells:
            x,y=p['x'],p['y']; t=data['palette'][data['floors'][y*w+x]]
            floor=Image.new('RGBA',(32,32))
            floor.alpha_composite(atlases[t['atlas']].crop((t['sx'],t['sy'],t['sx']+t['width'],t['sy']+t['height'])),(t['dx'],t['dy']))
            assert floor.getextrema()[3]==(255,255)
            image.paste(floor,(x*32,y*32));image.alpha_composite(sprites[state],(x*32,y*32))
            mask[y*32:(y+1)*32,x*32:(x+1)*32]=True
        a=np.array(image);assert np.array_equal(a[~mask],before[~mask])
        image.convert('RGB').save(OUT/f'{m["facility"]}-{state}102.png');outputs[state]=a
    assert np.array_equal(outputs['closed'][~mask],outputs['open'][~mask])
    assert bool(np.any(outputs['closed']!=outputs['open']))==bool(cells)
    shutil.copy2(SRC/m['images']['new95'],OUT/f'{m["facility"]}-previous95.png')
    shutil.copy2(SRC/m['map'],OUT/m['map'])
    assert (OUT/m['map']).read_bytes()==(SRC/m['map']).read_bytes()
    manifest['maps'].append({**m,'images':{'new102':f'{m["facility"]}-closed102.png','previous95':f'{m["facility"]}-previous95.png'},
      'openImage':f'{m["facility"]}-open102.png','facilityDoors':m['doors'],'doors':cells,
      'doorFocus':{'x':cells[0]['x']+.5,'y':cells[0]['y']+.5} if cells else m['focus']})
    checks.append({'facility':m['facility'],'ordinaryDoors':len(cells),'newDoorCellsAdded':0,'mapSha256':hashlib.sha256((OUT/m['map']).read_bytes()).hexdigest(),
      'geometryUnchanged':True,'outsideDoorPixelsUnchanged':True,'facilityArtUnchanged':True,'openClosedChangesOnlyDoorCells':True})
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','maps':len(checks),'ordinaryDoorCells':sum(c['ordinaryDoors'] for c in checks),
 'checks':checks,'normalWallRevision':92,'approvedDoorRevision':101,'nativeIntegration':False},indent=2)+'\n')
print(json.dumps({'status':'passed','maps':len(checks),'ordinaryDoors':sum(c['ordinaryDoors'] for c in checks)}))
