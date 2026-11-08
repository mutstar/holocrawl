"""Rebuild facility shells on the approved92 wall, preserving themed ornaments."""
from pathlib import Path
import hashlib,json,shutil
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'preview/city-facilities94';OUT=ROOT/'preview/city-facilities95'
OUT.mkdir(parents=True,exist_ok=True)
ENGINE=ROOT/'engine/upstream/crawl-ref/source'
catalog={s['id']:s for s in json.loads((ENGINE/'holo34-facilities.json').read_text(encoding='utf-8'))}
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
THEMES={'holox':(160,112,194),'theater':(177,117,81),'dev':(164,119,187),
 'dining':(177,132,92),'gamers':(116,168,157),'fantasy':(160,166,106),
 'wheel':(166,123,166),'market':(119,168,133),'mountain':(177,161,115)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dilation(mask,radius=1):
    return np.array(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.MaxFilter(radius*2+1)))>0
def rgbmix(a,b,t):return tuple(int(round(x*(1-t)+y*t)) for x,y in zip(a,b))

def door_sprite(id,width,opened,portal=False):
    """A shared concrete/steel jamb, with separately drawn themed leaves."""
    im=Image.new('RGBA',(width,32));d=ImageDraw.Draw(im);accent=THEMES[id]
    jamb=(111,128,135);light=(148,163,166);shadow=(50,67,74);steel=(60,79,87)
    # Frame follows the32px grid; open states leave the actual passage clear.
    d.rectangle((0,1,width-1,4),fill=jamb);d.line((0,1,width-1,1),fill=light)
    d.rectangle((0,4,3,30),fill=jamb);d.rectangle((width-4,4,width-1,30),fill=shadow)
    d.line((1,5,1,29),fill=light);d.line((width-3,5,width-3,29),fill=(87,108,116))
    d.rectangle((3,5,width-4,6),fill=(37,53,60));d.rectangle((3,29,width-4,31),fill=(72,91,97))
    d.line((4,5,width-5,5),fill=accent)
    for x in (2,width-3):
        for y in (8,26):d.point((x,y),fill=(177,185,180))
    if opened:
        d.rectangle((4,7,6,28),fill=rgbmix(steel,accent,.25));d.rectangle((width-7,7,width-5,28),fill=steel)
        d.line((6,8,6,27),fill=accent);d.line((width-7,8,width-7,27),fill=rgbmix(accent,shadow,.40))
        if portal:
            d.rectangle((width//2-3,1,width//2+3,4),fill=rgbmix(accent,steel,.35))
            if id=='mountain':d.ellipse((width//2-1,1,width//2+1,3),fill=(207,195,143))
        return im
    body=rgbmix((48,64,73),accent,.16);d.rectangle((4,7,width-5,28),fill=body)
    d.line((4,7,width-5,7),fill=rgbmix(body,light,.35));d.line((width//2,8,width//2,28),fill=(29,44,52))
    centers=[width//4,3*width//4] if width>=48 else [width//2]
    if id in ('theater','dining','market'):
        for cx in centers:
            if id=='dining':
                d.ellipse((cx-5,9,cx+5,18),fill=(29,45,52),outline=accent)
                d.line((cx-2,11,cx+1,11),fill=(153,185,183))
            else:
                d.rectangle((cx-6,9,cx+5,19),fill=(31,51,62),outline=rgbmix(accent,jamb,.30))
                d.line((cx-4,11,cx+2,11),fill=(127,162,170));d.line((cx-4,12,cx-4,16),fill=(91,132,143))
        d.rectangle((6,22,width-7,26),fill=rgbmix(body,accent,.22))
    elif id=='holox':
        d.rectangle((6,9,width-7,22),fill=(37,43,62));cx=width//2
        d.line((cx-3,12,cx+3,18),fill=accent,width=2);d.line((cx+3,12,cx-3,18),fill=accent,width=2)
        for x in range(7,width-7,5):d.line((x,25,x+2,23),fill=(183,160,83))
    elif id=='dev':
        d.rectangle((6,9,width-7,23),fill=(36,43,60))
        for i in range(5):
            x=width//2-8+i*4;hh=[4,8,12,7,5][i]
            d.line((x,21-hh,x,21),fill=rgbmix(accent,(224,192,219),.20))
    elif id=='gamers':
        d.rectangle((6,9,width-7,19),fill=(35,60,64),outline=rgbmix(accent,jamb,.25))
        d.rectangle((6,22,width-7,24),fill=accent)
        for x in range(8,width-8,6):d.line((x,22,x+2,24),fill=(62,89,90))
    else:
        for x in range(7,width-6,5):d.line((x,9,x,26),fill=rgbmix(steel,accent,.30))
        d.rectangle((width//2-3,12,width//2+3,18),fill=rgbmix(accent,steel,.25))
    d.line((width//2-3,20,width//2-3,24),fill=(185,188,169))
    d.line((width//2+3,20,width//2+3,24),fill=(141,155,148))
    d.point((width-7,8),fill=(138,207,167))
    return im

def groups(cells):
    cells=set(cells);out=[]
    while cells:
        x,y=min(cells,key=lambda p:(p[1],p[0]));row=[(x,y)];cells.remove((x,y))
        while (row[-1][0]+1,y) in cells:
            p=(row[-1][0]+1,y);cells.remove(p);row.append(p)
        out.append(row)
    return out

manifest={'title':'잔향도시 · 시설 전용벽과 신규 문95','revision':95,'tileSize':32,
 'styles':[{'id':'new95','label':'새 전용벽·문95'},{'id':'previous94','label':'수정 전94'}],
 'maps':[],'normalWallRevision':92,'nativeIntegration':False}
checks=[];door_examples=[]
for m in prior['maps']:
    id=m['facility'];spec=catalog[id];data=json.loads((SRC/m['map']).read_text());o=m['origin'];accent=THEMES[id]
    original=Image.open(SRC/f'{id}-original84.png').convert('RGBA');base=np.array(original)
    previous=np.array(Image.open(SRC/m['images']['integrated92']).convert('RGBA'))
    fresh,wall,_=render(base,data['rows'],grain)
    x0,y0=o['x']*32,o['y']*32;x1,y1=x0+o['width']*32,y0+o['height']*32
    old=base[y0:y1,x0:x1].copy();new=fresh[y0:y1,x0:x1].copy()
    structural=np.zeros((o['height']*32,o['width']*32),dtype=bool)
    rail=np.zeros_like(structural)
    for y,row in enumerate(spec['rows']):
        for x,c in enumerate(row):
            if x in (0,o['width']-1) or y in (0,o['height']-1):
                if c=='#':structural[y*32:(y+1)*32,x*32:(x+1)*32]=True
                if c=='G':rail[y*32+29:(y+1)*32,x*32:(x+1)*32]=True
    # Shared92 planes replace the shell's dark box. Existing themed colour
    # remains as a restrained tint in exposed coping, not a second outer frame.
    a=old.copy();a[structural]=new[structural]
    newrgb=new[:,:,:3].astype(float)
    trim=structural&(newrgb.min(axis=2)>78)
    a[trim,:3]=np.rint(newrgb[trim]*.84+np.array(accent)*.16).astype('uint8')
    # Preserve original ornament pixels and their small dark outlines. Artwork
    # remains sourced from the reviewed scene, rather than re-invented icons.
    rgb=old[:,:,:3].astype(int);maximum=rgb.max(axis=2);minimum=rgb.min(axis=2)
    pigment=((maximum>=125)&((maximum-minimum)>=24))|(minimum>=112)
    ornament=dilation(pigment,1)&structural
    # Screen and carved relief are full inset panels rather than bright decals.
    if id=='theater':ornament[1:29,33:(o['width']-1)*32-1]=True
    if id=='mountain':
        ornament[:64]=False
        ornament[4:32,4:o['width']*32-4]=True
        ornament[32:64,64:224]=structural[32:64,64:224]
    # The small theatre title remains above the new double door.
    if id=='theater':ornament[(o['height']-1)*32:(o['height']-1)*32+7,64:192]=True
    # The old single-pixel exterior frame belongs to the previous wall, not
    # to the decoration. Remove it instead of leaving coloured floating lines.
    ornament[:3,:]=False;ornament[-3:,:]=False;ornament[:,:3]=False;ornament[:,-3:]=False
    a[ornament]=old[ornament]
    if id=='holox':
        # The old hazard tape sat on the retired outside border. Put it on
        # the new concrete front instead, keeping its readable yellow slashes.
        yy,xx=np.indices(structural.shape)
        bottom=(yy>=(o['height']-1)*32)&structural
        clean=bottom&(yy%32>=26)&(a[:,:,:3].max(axis=2)<110)
        a[clean]=new[clean]
        tape=bottom&(yy%32>=27)&(yy%32<=29)
        a[tape,:3]=[47,58,63]
        slashes=tape&((xx+yy)%7<3);a[slashes,:3]=[192,170,86]
    # Recolour only exact dominant dark backing colours on inner structural
    # tiles. Embedded research desks, kitchen fixtures and character art stay.
    counts=Counter(map(tuple,old[structural,:3].tolist()))
    backing=[c for c,n in counts.most_common(24) if max(c)<85 and max(c)-min(c)<60 and n>60]
    inner=np.zeros_like(structural)
    for y,row in enumerate(spec['rows']):
        for x,c in enumerate(row):
            if c=='#' and x not in (0,o['width']-1) and y not in (0,o['height']-1):inner[y*32:(y+1)*32,x*32:(x+1)*32]=True
    protected=dilation(pigment,2)
    inner_changes=np.zeros_like(structural)
    for color in backing:
        mask=inner&~protected&np.all(old[:,:,:3]==color,axis=2)
        a[mask,:3]=np.rint(np.array(color)*.38+np.array([39,48,54])*.62).astype('uint8');inner_changes|=mask
    # Outdoor fencing keeps its rails; a narrow concrete footing ties it to
    # the common walls without replacing transparent terrain with solid walls.
    a[rail,:3]=[91,108,112]
    fresh[y0:y1,x0:x1]=a
    # Exact outside-facility92 colour and all floor scenery are kept.
    outside=np.ones(wall.shape,dtype=bool);outside[y0:y1,x0:x1]=False
    fresh[outside]=previous[outside]
    closed=Image.fromarray(fresh);opened=closed.copy()
    logical_doors=[(x,y) for y,r in enumerate(spec['rows']) for x,c in enumerate(r) if c=='+']
    portals=[(p['x']-o['x'],p['y']-o['y']) for p in m['entrances'] if spec['rows'][p['y']-o['y']][p['x']-o['x']]=='.']
    # Select a quiet actual facility floor tile for the new door's underlay.
    candidates=[]
    for y,r in enumerate(spec['rows']):
        for x,c in enumerate(r):
            if c=='.' and 0<x<o['width']-1 and 0<y<o['height']-1:
                tile=old[y*32:(y+1)*32,x*32:(x+1)*32]
                score=np.abs(np.diff(tile[:,:,:3].astype(float),axis=0)).mean()+np.abs(np.diff(tile[:,:,:3].astype(float),axis=1)).mean()
                candidates.append((float(score),x,y))
    _,tx,ty=min(candidates);floor=Image.fromarray(old[ty*32:(ty+1)*32,tx*32:(tx+1)*32])
    door_checks=[]
    for portal,cells in [(False,logical_doors),(True,portals)]:
        for group in groups(cells):
            x,y=group[0];width=32*len(group)
            north=spec['rows'][y-1][x] in '#G' if y else True
            south=spec['rows'][y+1][x] in '#G' if y+1<o['height'] else False
            vertical=not portal and len(group)==1 and north and south
            sprites=[]
            header=8 if id=='theater' and y==o['height']-1 else 0
            for state,image in [(False,closed),(True,opened)]:
                for gx,gy in group:image.paste(floor,(x0+gx*32,y0+gy*32))
                sprite=door_sprite(id,width,state or portal,portal)
                if vertical:sprite=sprite.transpose(Image.Transpose.ROTATE_90)
                if header:
                    image.paste(Image.fromarray(old[y*32:y*32+header,x*32:(x+len(group))*32]),(x0+x*32,y0+y*32))
                    sprite=sprite.resize((width,32-header),Image.Resampling.NEAREST)
                image.alpha_composite(sprite,(x0+x*32,y0+y*32+header));sprites.append(sprite)
            if not portal:
                assert not np.array_equal(np.array(sprites[0]),np.array(sprites[1]))
                door_checks.append({'x':o['x']+x,'y':o['y']+y,'width':len(group),'vertical':vertical})
                for state,sprite in zip(['closed','open'],sprites):sprite.save(OUT/f'{id}-door-{len(door_checks)}-{state}.png')
                door_examples.append((id,width,sprites[0],sprites[1]))
    for name,image in [('closed95',closed),('open95',opened)]:image.convert('RGB').save(OUT/f'{id}-{name}.png')
    shutil.copy2(SRC/m['images']['integrated92'],OUT/f'{id}-previous94.png')
    shutil.copy2(SRC/m['map'],OUT/m['map'])
    final=np.array(closed);final_open=np.array(opened)
    assert np.array_equal(final[outside],previous[outside]) and np.array_equal(final_open[outside],previous[outside])
    door_pixels=np.zeros(wall.shape,dtype=bool)
    for x,y in logical_doors:door_pixels[y0+y*32:y0+(y+1)*32,x0+x*32:x0+(x+1)*32]=True
    changed_state=np.any(final!=final_open,axis=2)
    assert not np.any(changed_state&~door_pixels)
    assert bool(changed_state.any())==bool(logical_doors)
    # Non-wall/non-door interior scenery is protected, except the explicit
    # open portal frames at already walkable entrance cells.
    allowed=np.zeros_like(structural);allowed|=structural|inner_changes|rail
    for x,y in logical_doors+portals:allowed[y*32:(y+1)*32,x*32:(x+1)*32]=True
    assert np.array_equal(final[y0:y1,x0:x1][~allowed],old[~allowed])
    crop=(max(0,x0-48),max(0,y0-48),min(2560,x1+48),min(2240,y1+80))
    for state,image in [('closed',closed),('open',opened)]:image.crop(crop).convert('RGB').save(OUT/f'{id}-facility-{state}.png')
    entry={**m,'images':{'new95':f'{id}-closed95.png','previous94':f'{id}-previous94.png'},
           'openImage':f'{id}-open95.png','doors':door_checks,'openPortals':len(portals)}
    manifest['maps'].append(entry)
    checks.append({'facility':id,'nativeMapSha256':sha(SRC/m['map']),'normal92OutsideFacilityUnchanged':True,
      'interiorSceneryUnchanged':True,'ornamentPixels':int(ornament.sum()),'innerBackingPixels':int(inner_changes.sum()),
      'nativeDoorCells':len(logical_doors),'doorGroups':len(door_checks),'openPortalCells':len(portals),
      'closedOpenDiffer':bool(door_checks),'doorStateChangesOnlyDoorCells':True,'geometryUnchanged':True})
    print(f'Rebuilt {id} shell; preserved scenery; {len(door_checks)} door groups and {len(portals)} open portals.',flush=True)

font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1296,1530),'#151c20');d=ImageDraw.Draw(sheet)
for i,m in enumerate(manifest['maps']):
    ox=(i%3)*432;oy=(i//3)*510;d.text((ox+12,oy+8),m['name'],font=font,fill='#dbe6e2')
    im=Image.open(OUT/f'{m["facility"]}-facility-closed.png');im.thumbnail((408,462),Image.Resampling.NEAREST);sheet.paste(im,(ox+12,oy+40))
sheet.save(OUT/'all-facilities.png')
doorboard=Image.new('RGB',(768,max(1,len(door_examples))*115+36),'#151c20');d=ImageDraw.Draw(doorboard)
d.text((14,6),'신규 문 · 닫힘 / 열림',font=font,fill='#e1e7e3')
for i,(id,w,c,o) in enumerate(door_examples):
    yy=35+i*115;d.text((14,yy+26),catalog[id]['name'],font=font,fill='#b7c8c4')
    for j,im in enumerate([c,o]):doorboard.paste(im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST),(350+j*210,yy),im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST))
doorboard.save(OUT/'doors.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','facilities':9,'checks':checks,'normalWallRevision':92,
 'nativeIntegration':False,'scope':'Wall and door artwork preview on unchanged native94 geometry.'},indent=2)+'\n')
print('Prepared facility shells and doors95 without changing native geometry or normal92 walls.')
