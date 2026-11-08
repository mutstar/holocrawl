"""Unbranded normal dungeon door; separate one-facility-at-a-time review."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/basic-door96';REVIEW=ROOT/'preview/holox-door97'
OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def basic(opened):
    image=Image.new('RGBA',(32,32));d=ImageDraw.Draw(image)
    # Neutral cast-concrete jamb and a single hinged steel leaf. No facility
    # emblem, neon accent or access-control colour is used for this normal door.
    d.rectangle((0,1,31,4),fill=(118,130,134));d.line((0,1,31,1),fill=(148,157,158))
    d.rectangle((0,4,3,30),fill=(111,126,131));d.line((0,5,0,29),fill=(134,145,146))
    d.rectangle((29,4,31,30),fill=(71,91,99));d.line((29,5,29,29),fill=(104,122,128))
    d.rectangle((4,5,28,6),fill=(38,54,62));d.rectangle((3,29,28,31),fill=(76,94,101))
    for x in [2,30]:
        for y in [8,25]:d.point((x,y),fill=(163,170,167))
    if opened:
        d.rectangle((4,7,7,28),fill=(69,88,98));d.line((7,8,7,27),fill=(108,125,132))
        d.line((4,8,4,26),fill=(42,59,68));d.rectangle((5,11,6,16),fill=(45,69,82))
        d.point((6,23),fill=(163,157,124))
    else:
        d.rectangle((4,7,28,28),fill=(65,83,94));d.line((5,7,27,7),fill=(104,121,128))
        d.line((5,8,5,27),fill=(84,103,112));d.line((28,8,28,28),fill=(36,54,64))
        d.rectangle((12,9,19,17),fill=(33,48,57),outline=(110,126,131))
        d.rectangle((13,10,18,16),fill=(45,71,84));d.line((14,11,17,11),fill=(116,144,151))
        d.line((14,12,14,14),fill=(77,112,127))
        d.rectangle((23,20,25,24),fill=(39,54,61));d.line((24,21,24,23),fill=(167,164,139))
        for y in [10,23]:d.rectangle((3,y,6,y+2),fill=(118,130,132))
        d.line((8,25,20,25),fill=(53,72,84));d.line((10,26,15,26),fill=(79,97,106))
        for p in [(8,9),(26,27),(7,26),(20,8)]:d.point(p,fill=(106,117,120))
    return image

source=ROOT/'preview/city-random93';host=json.loads((source/'map.json').read_text())
hostimage=np.array(Image.open(source/f'{host["seed"]}-original84.png').convert('RGBA'))
px,py=next((x,y) for y,row in enumerate(host['rows']) for x,c in enumerate(row) if c=='.' and 3<x<76 and 3<y<66)
floor=hostimage[py*32:(py+1)*32,px*32:(px+1)*32]
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
old_path=ROOT/'engine/upstream/crawl-ref/source/rltiles/dngn/doors'
manifest={'title':'기본 던전문 · 콘크리트 벽용','kind':'basic','defaultZoom':2,
 'styles':[{'id':'new','label':'새 기본문'},{'id':'old','label':'돌죽 기존 기본문'}],'scenes':[],'nativeIntegration':False}
for direction in ['horizontal','vertical']:
    rows=['.......']*7;rows=list(rows)
    if direction=='horizontal':rows[3]='###+###'
    else:rows=['...#...' if y!=3 else '...+...' for y in range(7)]
    base=np.tile(floor,(7,7,1));scene,_,_=render(base,rows,grain)
    entry={'id':direction,'label':'가로 벽' if direction=='horizontal' else '세로 벽','width':224,'height':224,'images':{}}
    for style in ['new','old']:
        entry['images'][style]={}
        states=[]
        for opened in [False,True]:
            state='open' if opened else 'closed'
            sprite=basic(opened) if style=='new' else Image.open(old_path/f'{"open" if opened else "closed"}_door.png').convert('RGBA')
            if direction=='vertical':sprite=sprite.transpose(Image.Transpose.ROTATE_90)
            if style=='new':sprite.save(OUT/f'basic-{direction}-{state}32.png')
            im=Image.fromarray(scene.copy());im.alpha_composite(sprite,(96,96));im.convert('RGB').save(OUT/f'{style}-{direction}-{state}.png')
            entry['images'][style][state]=f'{style}-{direction}-{state}.png';states.append(np.array(im))
        allowed=np.zeros((224,224),dtype=bool);allowed[96:128,96:128]=True
        assert not np.any(np.any(states[0]!=states[1],axis=2)&~allowed)
    manifest['scenes'].append(entry)
assert np.array(basic(False))[15,15,3]==255 and np.array(basic(True))[15,15,3]==0
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Review only holoX now. Other facility-door drafts stay in95 and are not
# automatically approved or advanced by this dedicated review page.
src=ROOT/'preview/city-facilities95';m=json.loads((src/'manifest.json').read_text(encoding='utf-8'))['maps'][0]
assert m['facility']=='holox'
review={'title':'시설문1 · holoX 연구소','kind':'facility','defaultZoom':3,
 'styles':[{'id':'new','label':'holoX 문 시안'}],'scenes':[],'reviewOrder':1,'reviewStatus':'awaiting-user-feedback'}
native=json.loads((src/m['map']).read_text());entrance=m['entrances'][0]
points=[('entry','입구 문',entrance['x'],entrance['y']),('inside','내부 문',m['doors'][0]['x'],m['doors'][0]['y'])]
for id,label,x,y in points:
    width,height=160,128;box=((x-2)*32,(y-1)*32,(x+3)*32,(y+3)*32)
    scene={'id':id,'label':label,'width':width,'height':height,'images':{'new':{}}}
    for state,filename in [('closed',m['images']['new95']),('open',m['openImage'])]:
        im=Image.open(src/filename).crop(box).convert('RGB');name=f'holox-{id}-{state}.png';im.save(REVIEW/name);scene['images']['new'][state]=name
    review['scenes'].append(scene)
(REVIEW/'manifest.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
def board(folder,prefix,w,h,scale,title,name):
    pw=w*scale;ph=h*scale;canvas=Image.new('RGB',(pw*2+48,ph+100),'#151c20');d=ImageDraw.Draw(canvas)
    d.text((16,9),title,font=font,fill='#dce6e0')
    for i,(state,label) in enumerate([('closed','닫힘'),('open','열림')]):
        d.text((16+i*(pw+16),44),label,font=font,fill='#adbfba')
        im=Image.open(folder/f'{prefix}-{state}.png').resize((pw,ph),Image.Resampling.NEAREST);canvas.paste(im,(16+i*(pw+16),83))
    canvas.save(folder/name)
board(OUT,'new-horizontal',224,224,2,'새 기본 던전문 · 시설 문양 없는 철문','comparison.png')
board(REVIEW,'holox-entry',160,128,3,'시설문1 · holoX 연구소 입구','comparison.png')
v={'status':'passed','basicDoorStyles':2,'orientations':2,'openCenterTransparent':True,'stateChangesOnlyDoorCell':True,
 'hostMapUnchanged':True,'normalWallRevision':92,'facilityReview':'holoX only','nativeIntegration':False}
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n');(REVIEW/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('Created neutral basic dungeon door96 and isolated holoX facility-door review97.')
