"""Centered jambs and equal double leaves; show both wall axes together."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'preview/basic-doors100'
OUT.mkdir(parents=True,exist_ok=True)
DESIGNS=[
 {'id':'plate','name':'1 · 평판 철문','note':'푸른 철판 · 얕은 눌림','body':[67,86,97]},
 {'id':'glass','name':'2 · 세로창 철문','note':'긴 확인창 · 밝은 문짝','body':[83,105,109]},
 {'id':'fire','name':'3 · 무창 방화문','note':'회색 철판 · 가로 푸시바','body':[104,111,106]},
 {'id':'reinforced','name':'4 · 보강 철문','note':'짙은 강판 · 가로 보강대','body':[51,66,78]},
 {'id':'vent','name':'5 · 환기구 철문','note':'탁한 녹회색 · 환기 슬롯','body':[85,100,88]}]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def mirror_double(im):
    im.paste(im.crop((0,0,16,32)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(16,0))
    return im
def sprite(design,kind,opened):
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);body=tuple(design['body']);id=design['id'];double=kind=='double'
    d.rectangle((0,1,31,4),fill=(118,130,134));d.line((0,1,31,1),fill=(148,157,158))
    d.rectangle((0,4,3,30),fill=(111,126,131));d.line((0,5,0,29),fill=(134,145,146))
    d.rectangle((28,4,31,30),fill=(111,126,131));d.line((31,5,31,29),fill=(134,145,146))
    d.rectangle((4,5,27,6),fill=(38,54,62));d.rectangle((3,29,28,31),fill=(76,94,101))
    for x in (2,29):
        for y in (8,25):d.point((x,y),fill=(163,170,167))
    light=mix(body,(177,184,171),.42);shade=mix(body,(22,38,48),.50)
    if opened:
        spans=[(4,7)]
        for x0,x1 in spans:
            d.rectangle((x0,7,x1,28),fill=body)
            d.line((x1 if x0==4 else x0,8,x1 if x0==4 else x0,27),fill=light)
            d.line((x0 if x0==4 else x1,8,x0 if x0==4 else x1,28),fill=shade)
            if id=='glass':d.line((x0+1,10,x0+1,17),fill=(47,84,101))
            elif id=='fire':d.rectangle((x0+1,20,x0+2,22),fill=(177,178,158))
            elif id=='reinforced':
                for y in (11,22):d.rectangle((x0,y,x1,y+1),fill=(111,128,137))
            elif id=='vent':
                for y in (11,14,17):d.line((x0+1,y,x0+2,y),fill=shade)
            d.point((x0+1,25),fill=(151,155,139))
        return mirror_double(im) if double else im
    panels=[(4,14)] if double else [(4,27)]
    for left,right in panels:
        d.rectangle((left,7,right,28),fill=body);d.line((left+1,7,right-1,7),fill=light)
        d.line((left+1,8,left+1,27),fill=mix(body,light,.55));d.line((right,8,right,28),fill=shade)
        if id=='plate':
            d.line((left+3,10,right-3,10),fill=mix(body,light,.35))
            d.line((left+3,25,right-3,25),fill=shade)
        elif id=='glass':
            window_left,window_right=(7,11) if double else (12,19)
            d.rectangle((window_left,9,window_right,19),fill=(30,48,58),outline=(134,153,154))
            d.rectangle((window_left+1,10,window_right-1,18),fill=(43,80,98))
            d.line((window_left+1,10,window_right-1,10),fill=(139,171,175))
            d.point((window_left+1,12),fill=(98,139,153))
        elif id=='fire':
            d.rectangle((left+3,9,right-3,16),fill=mix(body,shade,.23))
            d.line((left+3,10,right-3,10),fill=mix(body,light,.27))
            d.rectangle((left+2,19,right-2,23),fill=(47,64,71))
            d.rectangle((left+3,20,right-3,21),fill=(178,180,159))
            d.line((left+3,22,right-3,22),fill=(99,115,105))
        elif id=='reinforced':
            for y in (11,22):
                d.rectangle((left+1,y,right-1,y+2),fill=(101,120,130));d.line((left+1,y,right-1,y),fill=(142,156,156))
                for x in (left+2,right-2):d.point((x,y+1),fill=(43,60,71))
            d.line((left+3,16,right-3,16),fill=(67,85,99))
        else:
            for y in (10,13,16):
                d.rectangle((left+3,y,right-3,y+1),fill=(40,57,54));d.line((left+3,y,right-3,y),fill=(121,139,122))
            d.rectangle((left+3,24,right-3,26),fill=mix(body,shade,.28))
        for x,y in [(left+2,27),(right-2,8)]:d.point((x,y),fill=mix(light,(126,100,74),.55))
    if double:
        d.rectangle((15,7,16,28),fill=(31,48,57))
        if id!='fire':
            for x in (12,19):d.line((x,21,x,24),fill=(173,173,151))
    elif id!='fire':
        d.rectangle((23,20,25,24),fill=shade);d.line((24,21,24,23),fill=(173,173,151))
    for x in [3]:
        for y in (10,24):d.rectangle((x,y,x+2,y+2),fill=(124,138,140))
    return mirror_double(im) if double else im

src=ROOT/'preview/city-random93';host=json.loads((src/'map.json').read_text())
original=np.array(Image.open(src/f'{host["seed"]}-original84.png').convert('RGBA'))
px,py=next((x,y) for y,r in enumerate(host['rows']) for x,c in enumerate(r) if c=='.' and 3<x<76 and 3<y<66)
floor=original[py*32:(py+1)*32,px*32:(px+1)*32]
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
manifest={'title':'기본문5종 · 단일문/양개문','revision':100,'normalWallRevision':92,'sceneSize':64,'designs':DESIGNS,
 'kinds':[{'id':'single','label':'단일문'},{'id':'double','label':'양개문'}],
 'sameFacingForBothAxes':True,'footprint':[32,32],'images':{},'nativeIntegration':False,'reviewStatus':'draft-user-feedback',
 'centering':{'axisX':15.5,'jambWidthEach':4,'clearOpening':[4,27],'doubleLeaves':[[4,14],[17,27]],'seam':[15,16]}}
checks=[]
for direction in ['horizontal','vertical']:
    rows=['.......']*7
    if direction=='horizontal':rows[3]='###+###'
    else:rows=['...#...' if y!=3 else '...+...' for y in range(7)]
    base=np.tile(floor,(7,7,1));scene,_,_=render(base,rows,grain)
    manifest['images'][direction]={}
    for state,opened in [('closed',False),('open',True)]:
        manifest['images'][direction][state]={}
        for design in DESIGNS:
            id=design['id'];manifest['images'][direction][state][id]={}
            for kind in ['single','double']:
                tile=sprite(design,kind,opened)
                # Deliberately identical sprite bytes on horizontal/vertical
                # walls. Only the surrounding geometry changes.
                sprite_file=OUT/f'{id}-{kind}-{state}32.png'
                if direction=='horizontal':tile.save(sprite_file)
                else:assert np.array_equal(np.array(tile),np.array(Image.open(sprite_file)))
                image=Image.fromarray(scene.copy());image.alpha_composite(tile,(96,96))
                filename=f'{id}-{kind}-{direction}-{state}.png'
                image.crop((80,80,144,144)).convert('RGB').save(OUT/filename)
                manifest['images'][direction][state][id][kind]=filename
                pixels=np.array(image);allowed=np.zeros((224,224),dtype=bool);allowed[96:128,96:128]=True
                assert np.array_equal(pixels[~allowed],scene[~allowed])
                checks.append({'design':id,'kind':kind,'orientation':direction,'state':state,'outsideDoorPixelsChanged':0})
for design in DESIGNS:
    for kind in ['single','double']:
        assert np.array(sprite(design,kind,True))[15,15,3]==0
        assert np.array(sprite(design,kind,False))[15,15,3]==255
        if kind=='double':
            for opened in [False,True]:
                pixels=np.array(sprite(design,kind,opened))
                assert np.array_equal(pixels,pixels[:,::-1])
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
for state in ['closed','open']:
    sheet=Image.new('RGB',(1040,1160),'#151c20');draw=ImageDraw.Draw(sheet)
    draw.text((14,9),'중앙 정렬 수정 · '+('닫힘' if state=='closed' else '열림'),font=font,fill='#e2e9e3')
    columns=[('single','horizontal','단일 · 가로'),('single','vertical','단일 · 세로'),('double','horizontal','양개 · 가로'),('double','vertical','양개 · 세로')]
    for j,(_,_,label) in enumerate(columns):draw.text((210+j*204,46),label,font=small,fill='#acbfb4')
    for i,design in enumerate(DESIGNS):
        y=80+i*214;draw.text((12,y+76),design['name'],font=font,fill='#d9e6de')
        for j,(kind,direction,_) in enumerate(columns):
            im=Image.open(OUT/manifest['images'][direction][state][design['id']][kind]).resize((192,192),Image.Resampling.NEAREST)
            sheet.paste(im,(210+j*204,y))
    sheet.save(OUT/f'comparison-{state}.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','designs':5,'kinds':2,'doorDesigns':10,'checks':checks,
 'spritesIdenticalAcrossOrientations':True,'openCentersTransparent':True,'closedCentersOpaque':True,
 'footprint':[32,32],'normalWallRevision':92,'nativeIntegration':False,'jambsEqualWidth':True,
 'openingCenterX':15.5,'doubleLeafWidths':[11,11],'doubleSpriteMirrorExact':True},indent=2)+'\n')
print('Centered all10 doors; exact mirrored double leaves,4px jambs, both axes side by side.')
