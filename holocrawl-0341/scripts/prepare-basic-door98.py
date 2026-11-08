"""A second normal door: opaque fire door, panic bar, opposite hinge."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'preview/basic-door98';SRC=ROOT/'preview/basic-door96'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p.relative_to(ROOT)):sha(p) for p in SRC.glob('*.png')}
def fire_door(opened):
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    d.rectangle((0,1,31,4),fill=(118,130,134));d.line((0,1,31,1),fill=(148,157,158))
    d.rectangle((0,4,3,30),fill=(111,126,131));d.line((0,5,0,29),fill=(134,145,146))
    d.rectangle((29,4,31,30),fill=(71,91,99));d.line((29,5,29,29),fill=(104,122,128))
    d.rectangle((4,5,28,6),fill=(38,54,62));d.rectangle((3,29,28,31),fill=(76,94,101))
    for x in [2,30]:
        for y in [8,25]:d.point((x,y),fill=(163,170,167))
    if opened:
        # The leaf folds against the right jamb, leaving the middle clear.
        d.rectangle((24,7,28,28),fill=(99,109,108));d.line((24,8,24,27),fill=(144,151,145))
        d.line((28,8,28,28),fill=(47,63,69));d.rectangle((24,20,25,22),fill=(173,174,153))
        for y in [10,24]:d.rectangle((27,y,29,y+1),fill=(128,140,141))
    else:
        d.rectangle((4,7,28,28),fill=(101,110,107));d.line((5,7,27,7),fill=(150,155,145))
        d.line((5,8,5,27),fill=(126,137,130));d.line((28,8,28,28),fill=(49,66,71))
        # Solid pressed-steel panels; no window, insignia or glowing light.
        d.rectangle((7,9,25,17),fill=(86,100,100));d.line((8,10,24,10),fill=(111,124,119))
        d.line((8,16,24,16),fill=(64,82,85));d.rectangle((7,24,25,27),fill=(85,100,99))
        d.rectangle((6,19,25,23),fill=(48,65,71));d.rectangle((7,20,24,22),fill=(123,134,125))
        d.rectangle((9,20,22,21),fill=(176,178,157));d.line((9,22,22,22),fill=(92,108,103))
        for y in [10,24]:d.rectangle((27,y,30,y+2),fill=(126,139,139))
        for x,y in [(7,27),(8,28),(23,26),(25,8),(6,12)]:d.point((x,y),fill=(117,97,76))
    return im

hostdir=ROOT/'preview/city-random93';host=json.loads((hostdir/'map.json').read_text())
original=np.array(Image.open(hostdir/f'{host["seed"]}-original84.png').convert('RGBA'))
px,py=next((x,y) for y,row in enumerate(host['rows']) for x,c in enumerate(row) if c=='.' and 3<x<76 and 3<y<66)
floor=original[py*32:(py+1)*32,px*32:(px+1)*32]
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
manifest={'title':'기본 던전문 · A/B 비교','defaultZoom':4,'variants':[
 {'id':'a','label':'A · 확인창 철문96','note':'작은 확인창 · 왼쪽으로 접히는 문짝'},
 {'id':'b','label':'B · 무창 방화문98','note':'막힌 철판 · 가로 푸시바 · 오른쪽으로 접히는 문짝'}],
 'orientations':[{'id':'horizontal','label':'가로 벽'},{'id':'vertical','label':'세로 벽'}],
 'images':{},'sceneSize':96,'nativeIntegration':False,'reviewStatus':'draft-user-feedback'}
checks=[]
for direction in ['horizontal','vertical']:
    rows=['.......']*7
    if direction=='horizontal':rows[3]='###+###'
    else:rows=['...#...' if y!=3 else '...+...' for y in range(7)]
    base=np.tile(floor,(7,7,1));scene,_,_=render(base,rows,grain)
    manifest['images'][direction]={}
    for state,opened in [('closed',False),('open',True)]:
        a=Image.open(SRC/f'new-{direction}-{state}.png').convert('RGBA')
        sprite=fire_door(opened)
        if direction=='vertical':sprite=sprite.transpose(Image.Transpose.ROTATE_90)
        sprite.save(OUT/f'basic-b-{direction}-{state}32.png')
        b=Image.fromarray(scene.copy());b.alpha_composite(sprite,(96,96))
        allowed=np.zeros((224,224),dtype=bool);allowed[96:128,96:128]=True
        assert np.array_equal(np.array(a)[~allowed],np.array(b)[~allowed])
        manifest['images'][direction][state]={}
        for id,image in [('a',a),('b',b)]:
            name=f'{id}-{direction}-{state}.png';image.crop((64,64,160,160)).convert('RGB').save(OUT/name)
            manifest['images'][direction][state][id]=name
        checks.append({'orientation':direction,'state':state,'outsideDoorPixelsChanged':0})
assert np.array(fire_door(False))[15,15,3]==255 and np.array(fire_door(True))[15,15,3]==0
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
for state in ['closed','open']:
    board=Image.new('RGB',(832,470),'#151c20');d=ImageDraw.Draw(board)
    for i,(id,title) in enumerate([('a','A · 확인창 철문'),('b','B · 무창 방화문')]):
        d.text((16+i*416,12),title,font=font,fill='#dce6e0')
        im=Image.open(OUT/f'{id}-horizontal-{state}.png').resize((384,384),Image.Resampling.NEAREST);board.paste(im,(16+i*416,54))
    board.save(OUT/f'comparison-{state}.png')
assert frozen=={p:sha(ROOT/p) for p in frozen}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','checks':checks,'original96Unchanged':True,
 'openCenterTransparent':True,'closedCenterOpaque':True,'normalWallRevision':92,'nativeIntegration':False},indent=2)+'\n')
print('Created basic doorB98; only the door cell differs fromA96 on identical walls/floor.')
