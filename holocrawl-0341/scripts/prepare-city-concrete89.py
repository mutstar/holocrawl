"""Gungeon-inspired concrete wall study on complete existing native city maps."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/city-concrete89'
OUT.mkdir(parents=True,exist_ok=True)
GRAIN=ROOT/'preview/native-water02/assets/concrete-wall-surface256.png'
grain=np.array(Image.open(GRAIN).convert('RGB'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def adjacent(a,dx,dy):
    out=np.zeros_like(a);h,w=a.shape
    x0,x1=max(0,-dx),min(w,w-dx);y0,y1=max(0,-dy),min(h,h-dy)
    out[y0:y1,x0:x1]=a[y0+dy:y1+dy,x0+dx:x1+dx]
    return out

def surfaces(rows):
    cells=np.array([[c=='#' for c in row] for row in rows])
    solid=np.array([[c in '#+G' for c in row] for row in rows])
    expand=lambda a:np.repeat(np.repeat(a,32,axis=0),32,axis=1)
    walls=expand(cells)
    n,e,s,w,se,sw=[expand(adjacent(solid,dx,dy)) for dx,dy in [(0,-1),(1,0),(0,1),(-1,0),(1,1),(-1,1)]]
    yy,xx=np.indices(walls.shape);px,py=xx%32,yy%32
    raw_front=walls&(py>=18)&~s
    side=walls&(px>=28)&(~e|((py>=18)&~se))&~(raw_front&e)
    front=raw_front&~side
    west=walls&~front&~side&(px<3)&(n|s)&~np.where(py>=18,sw,w)
    cap=walls&~front&~side&~west
    assert np.all((cap.astype('uint8')+front+side+west)[walls]==1)
    return walls,cap,front,side,west,xx,yy

def compose(data,assets):
    atlases={name:Image.open(assets/f'{name}.png').convert('RGBA') for name in ['floor','wall','feat']}
    image=Image.new('RGBA',(data['width']*32,data['height']*32))
    for y in range(data['height']):
        for x in range(data['width']):
            for layer in ['floors','features']:
                t=data['palette'][data[layer][y*data['width']+x]]
                crop=atlases[t['atlas']].crop((t['sx'],t['sy'],t['sx']+t['width'],t['sy']+t['height']))
                image.alpha_composite(crop,(x*32+t['dx'],y*32+t['dy']))
    return np.array(image)

def render(base,rows,style):
    a=base.copy();walls,cap,front,side,west,xx,yy=surfaces(rows)
    texture=grain[yy%grain.shape[0],xx%grain.shape[1],:3].astype(float)
    noise=texture.mean(axis=2)-texture.mean()
    if style=='stone88':
        colors={'cap':[35,37,37],'front':[58,57,56],'side':[30,33,34],'west':[49,49,46]}
    else:
        colors={'cap':[35,38,36],'front':[70,71,66],'side':[34,38,36],'west':[53,56,50]}
    for mask,key in [(cap,'cap'),(front,'front'),(side,'side'),(west,'west')]:
        factor=.38 if style=='stone88' else (.30 if key=='cap' else .80)
        rgb=np.array(colors[key])[None,None,:]+noise[:,:,None]*factor
        a[mask,:3]=np.clip(rgb[mask] if style=='stone88' else np.rint(rgb[mask]),0,255).astype('uint8')
    north=cap&~adjacent(cap,0,-4);south=cap&~adjacent(cap,0,5)
    west_edge=cap&~adjacent(cap,-4,0);east_edge=cap&~adjacent(cap,4,0)
    rim=north|south|west_edge|east_edge
    if style=='stone88':
        block=((xx//11+yy//11)%3)*4
        for k,c in enumerate([91,83,73]):
            layer=a[:,:,k];layer[rim]=(c+block[rim]+noise[rim]*.23).astype('uint8')
        joints=rim&(((xx%11==0)&(north|south))|((yy%11==0)&(west_edge|east_edge)))
        a[joints,:3]=[48,47,43]
        edge=cap&(~adjacent(cap,0,1)|~adjacent(cap,1,0));a[edge,:3]=[40,40,37]
        mortar=front&(((yy-18)%5==0)|((xx+((yy-18)//5%2)*8)%16==0))
        a[mortar,:3]=[31,33,34]
        a[front&adjacent(cap,0,-1),:3]=[24,27,28]
    else:
        # One concrete coping slab spans48px, instead of 11px masonry blocks.
        slab=(xx//48+yy//48)%3-1
        for k,c in enumerate([91,93,87]):
            layer=a[:,:,k];layer[rim]=np.clip(c+slab[rim]*2+noise[rim]*.65,0,255).astype('uint8')
        joints=(((xx%48==0)&(north|south))|((yy%48==0)&(west_edge|east_edge)))&rim
        a[joints,:3]=[59,63,59]
        # Crisp two-tone lip and recessed underside follow the complete cap
        # silhouette, including inside turns; never draw a frame per grid cell.
        top=cap&~adjacent(cap,0,-1);left=cap&~adjacent(cap,-1,0)
        bottom=cap&~adjacent(cap,0,1);right=cap&~adjacent(cap,1,0)
        a[top,:3]=[111,112,103];a[left,:3]=[98,102,93]
        a[bottom,:3]=[54,59,54];a[right,:3]=[51,57,53]
        a[front&adjacent(cap,0,-1),:3]=[30,35,32]
        a[front&adjacent(cap,0,-2)&~adjacent(cap,0,-1),:3]=[49,53,47]
        # Sparse casting joins and form-tie holes. No staggered brick courses.
        construction=front&(xx%64==0);a[construction,:3]=[48,53,47]
        form_line=front&(yy%32==27);a[form_line,:3]=(a[form_line,:3].astype(float)*.88).astype('uint8')
        holes=front&(yy%32==23)&(xx%48==14);a[holes,:3]=[45,49,43]
        # Small exposed-aggregate chips; preserve a continuous readable rim.
        random=((xx*1103515245)^(yy*12345))&0xffff
        chips=rim&(random%127==0)&~top&~left&~bottom&~right
        a[chips,:3]=[68,73,66]
    assert np.array_equal(base[~walls],a[~walls])
    assert np.array_equal(base[:,:,3],a[:,:,3])
    return a

plans=[(ROOT/'preview/wall-audit85/maps/map-802302584-1.json',ROOT/'preview/wall-audit85/assets'),
       (ROOT/'preview/city-random82/map.json',ROOT/'preview/city-random82/assets')]
manifest={'title':'잔향도시 · 건전식 콘크리트 벽89','revision':89,'tileSize':32,'scope':'Complete-map browser material study only.',
 'styles':[{'id':'concrete89','label':'콘크리트89'},{'id':'stone88','label':'앞선 건전식88'},{'id':'original84','label':'기존 도시벽84'}],
 'maps':[],'material':{'frontHeight':14,'eastSideWidth':4,'copingWidth':[4,5],'slabJointPeriod':48,'brickCourses':False}}
checks=[]
for source,assets in plans:
    data=json.loads(source.read_text());seed=data['seed'];base=compose(data,assets)
    walls=surfaces(data['rows'])[0]
    entry={'seed':seed,'width':data['width'],'height':data['height'],'sourceMap':str(source.relative_to(ROOT)).replace('\\','/'),
           'sourceMapSha256':sha(source),'auditedWallAtlasSha256':sha(assets/'wall.png'),'images':{}}
    for style in ['original84','stone88','concrete89']:
        result=base if style=='original84' else render(base,data['rows'],style)
        if style=='stone88' and seed==802302584:
            preserved=np.array(Image.open(ROOT/'preview/wall-styles88/gungeon-map.png').convert('RGBA'))
            assert np.array_equal(result,preserved)
        filename=f'{seed}-{style}.png';Image.fromarray(result).convert('RGB').save(OUT/filename)
        entry['images'][style]=filename
        outside=int(np.count_nonzero(np.any(result[~walls]!=base[~walls],axis=1)))
        assert outside==0
        checks.append({'seed':seed,'style':style,'nonWallPixelsChanged':outside,'alphaUnchanged':True})
        if seed==802302584:
            Image.fromarray(result).crop((29*32,35*32,36*32,44*32)).convert('RGB').save(OUT/f'corner-{style}.png')
    assert sha(source)==entry['sourceMapSha256'] and sha(assets/'wall.png')==entry['auditedWallAtlasSha256']
    manifest['maps'].append(entry)

font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
board=Image.new('RGB',(960,670),'#151c20');draw=ImageDraw.Draw(board)
for i,(style,title) in enumerate([('stone88','앞선 건전식88'),('concrete89','잔향도시 콘크리트89')]):
    draw.text((i*480+20,15),title,font=font,fill='#dee5df')
    image=Image.open(OUT/f'corner-{style}.png').resize((448,576),Image.Resampling.NEAREST)
    board.paste(image,(i*480+16,60))
board.save(OUT/'material-comparison.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation={'status':'passed','maps':len(plans),'checks':checks,'auditedSourcesUnchanged':True,'geometryUnchanged':True,'priorGungeon88PixelMatch':True,
            'sourceConcreteTextureSha256':sha(GRAIN),'nativeIntegration':False,'scope':'Visual material study, not new level generation.'}
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps({'status':'passed','maps':len(plans),'nonWallPixelsChanged':0}))
