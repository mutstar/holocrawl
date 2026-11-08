"""Put member motifs into functional interior scenery, removing104 exterior posters."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'preview/city-facilities104';WALL=ROOT/'preview/city-facilities103'
OUT=ROOT/'preview/city-facilities105';OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
theater=Image.open(ROOT/'preview/theater-wall31/assets/theater-native.png').convert('RGBA')
manifest={**prior,'revision':105,'title':'잔향도시 · 멤버 특징을 내부 소품으로',
 'styles':[{'id':'new105','label':'내부 소품으로 통합'},{'id':'previous104','label':'수정 전104'}],'maps':[]}

def shape(rows,colors):
    im=Image.new('RGBA',(max(map(len,rows)),len(rows)))
    for y,row in enumerate(rows):
        for x,c in enumerate(row):
            if c!='.':im.putpixel((x,y),colors[c]+(255,))
    return im

def oni_rack():
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    d.ellipse((3,27,29,31),fill=(30,25,29,220))
    for x in [7,24]:
        d.rectangle((x,8,x+2,29),fill=(81,54,42));d.line((x,9,x,27),fill=(155,109,66))
    d.rectangle((5,11,28,13),fill=(105,70,46));d.line((5,11,28,11),fill=(188,139,81))
    # Stage prop blades, fittings and stand are part of the object silhouette.
    d.line((4,26,25,12),fill=(187,196,182),width=2);d.line((9,12,28,26),fill=(143,157,154),width=2)
    d.line((4,26,2,29),fill=(118,66,57),width=3);d.line((28,26,30,29),fill=(118,66,57),width=3)
    icon=theater.crop((8,8,20,19)).resize((18,16),Image.Resampling.NEAREST)
    # Remove the source poster's beige backing: only the actual red mask hangs.
    a=np.array(icon);rgb=a[:,:,:3];a[(rgb[:,:,0]>145)&(rgb[:,:,1]>115)&(rgb[:,:,2]>80),3]=0
    im.alpha_composite(Image.fromarray(a),(7,2))
    d.line((5,29,28,29),fill=(151,108,64),width=2)
    return im

def vanity():
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    d.ellipse((2,28,30,31),fill=(28,25,31,220))
    # Wing-shaped mirror surround, lit bulbs and a dressing tabletop.
    d.polygon([(3,12),(1,7),(7,9),(10,6),(22,6),(25,9),(31,7),(29,13),(24,16),(8,16)],fill=(71,47,65))
    d.ellipse((8,2,23,19),fill=(159,108,124),outline=(221,179,164))
    d.ellipse((10,4,21,17),fill=(100,143,150));d.line((12,6,17,6),fill=(181,205,200))
    d.polygon([(16,16),(11,11),(11,8),(14,7),(16,9),(18,7),(21,8),(21,11)],fill=(217,124,155))
    for x,y in [(7,5),(6,10),(8,16),(24,5),(25,10),(23,16)]:d.rectangle((x,y,x+1,y+1),fill=(235,214,168))
    d.rectangle((3,21,28,25),fill=(100,61,72));d.line((3,20,28,20),fill=(187,126,140));d.line((4,21,27,21),fill=(210,155,160))
    for x in [5,25]:d.rectangle((x,25,x+1,29),fill=(112,81,77))
    d.rectangle((6,17,9,19),fill=(185,143,170));d.rectangle((23,17,25,19),fill=(197,179,129))
    d.rectangle((13,23,18,24),fill=(209,165,120))
    return im

def director_chair():
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    d.ellipse((3,28,29,31),fill=(28,26,24,230))
    d.line((8,18,24,29),fill=(133,100,66),width=2);d.line((24,18,8,29),fill=(162,119,71),width=2)
    d.rectangle((7,6,9,23),fill=(151,106,58));d.rectangle((23,6,25,23),fill=(112,79,48))
    d.rectangle((9,7,23,18),fill=(76,107,105));d.line((9,7,23,7),fill=(121,161,147))
    d.ellipse((11,8,20,16),fill=(232,189,67));d.rectangle((18,11,23,13),fill=(211,138,53));d.point((17,10),fill=(42,45,44))
    d.rectangle((6,21,26,24),fill=(95,132,116));d.line((6,21,26,21),fill=(158,178,132))
    d.line((4,19,10,19),fill=(174,131,75),width=2);d.line((23,19,28,19),fill=(153,113,69),width=2)
    # A small director's megaphone lies at the chair, not on a poster.
    d.polygon([(26,23),(31,21),(31,27),(26,26)],fill=(195,170,106));d.rectangle((24,24,26,25),fill=(99,104,97))
    return im

def fox_signal():
    im=Image.new('RGBA',(32,64));d=ImageDraw.Draw(im)
    d.rectangle((14,29,17,58),fill=(76,97,93));d.line((14,31,14,57),fill=(135,156,142))
    d.polygon([(8,59),(12,56),(21,56),(25,59),(25,62),(8,62)],fill=(73,82,75));d.line((9,59,24,59),fill=(125,140,120))
    d.rectangle((4,3,27,31),fill=(29,43,44));d.rectangle((5,4,26,30),fill=(79,119,112));d.line((6,4,25,4),fill=(165,199,181))
    d.rectangle((7,6,24,24),fill=(28,47,51))
    fox=shape(['w.........w','ww.......ww','wmw.....wmw','wmmwwwwwmmw','wwwwwwwwwww','.wkwwwwwkw.','..wwwwwww..','...wwkww...','....www....'],
      {'w':(224,229,216),'m':(109,181,170),'k':(37,57,64)}).resize((18,15),Image.Resampling.NEAREST)
    im.alpha_composite(fox,(7,7))
    for x,col in [(10,(190,126,104)),(20,(133,198,153))]:d.ellipse((x-2,26,x+2,29),fill=col)
    return im

def tarot_counter():
    im=Image.new('RGBA',(64,32));d=ImageDraw.Draw(im)
    d.ellipse((1,26,62,31),fill=(25,27,28,220))
    d.rectangle((3,5,60,28),fill=(59,39,43));d.rectangle((4,4,59,8),fill=(127,69,67));d.line((4,4,59,4),fill=(190,130,107))
    d.rectangle((5,11,30,26),fill=(83,44,52));d.line((6,12,28,12),fill=(147,90,92))
    wolf=shape(['.b.......b.','.bb.....bb.','.bgb...bgb.','..bbbbbbb..','..brbbbrb..','...bwbwb...','....www....','.....b.....'],
      {'b':(30,34,39),'g':(151,102,96),'r':(218,88,89),'w':(211,207,188)}).resize((20,14),Image.Resampling.NEAREST)
    im.alpha_composite(wolf,(8,12))
    d.rectangle((33,10,57,26),fill=(41,43,46));d.line((34,11,56,11),fill=(100,139,142))
    for x,y in [(35,15),(42,12),(49,15)]:
        d.rectangle((x,y,x+5,y+9),fill=(189,153,104));d.rectangle((x+1,y+1,x+4,y+8),fill=(220,195,143))
        d.rectangle((x+2,y+3,x+3,y+5),fill=(109,69,98))
    for x in [7,55]:d.rectangle((x,28,x+2,30),fill=(99,72,58))
    return im

definitions={'theater':[('ayame','아야메 · 오니 가면과 소품 검 거치대',1,3,oni_rack(),False),
 ('choco','초코 · 날개 하트 분장대',6,3,vanity(),False),
 ('subaru','스바루 · 오리 등받이 감독 의자',1,5,director_chair(),True)],
 'gamers':[('fubuki','후부키 · 승강장 흰여우 신호등',4,1,fox_signal(),False),
 ('mio','미오 · 역무실 늑대 문장 타로 보관대',6,4,tarot_counter(),False)]}
checks=[]
for m in prior['maps']:
    id=m['facility'];o=m['origin'];x0,y0=o['x']*32,o['y']*32;w,h=o['width'],o['height']
    data=json.loads((SRC/m['map']).read_text());local=[r[o['x']:o['x']+w] for r in data['rows'][o['y']:o['y']+h]]
    perimeter=np.zeros((h*32,w*32),bool)
    for y,row in enumerate(local):
        for x,c in enumerate(row):
            if c=='#' and (x in (0,w-1) or y in (0,h-1)):perimeter[y*32:(y+1)*32,x*32:(x+1)*32]=True
    propmask=np.zeros_like(perimeter);members=[]
    for key,name,x,y,sprite,replace in definitions.get(id,[]):
        for ty in range(y,y+sprite.height//32):
            for tx in range(x,x+sprite.width//32):
                assert 0<tx<w-1 and 0<ty<h-1 and local[ty][tx] in '#G',(id,key,tx,ty,local[ty][tx])
        propmask[y*32:y*32+sprite.height,x*32:x*32+sprite.width]=True
        sprite.save(OUT/f'{id}-{key}.png')
        members.append({'id':key,'name':name,'cell':[x,y],'size':[sprite.width//32,sprite.height//32],'interior':True,'usesExistingBlockedCells':True})
    if id=='gamers':members.extend([{'id':'korone','name':'코로네 · 코로네스키 벤치','unchanged':True},
                                   {'id':'okayu','name':'오카유 · 주먹밥 자판기','unchanged':True}])
    allowed=perimeter|propmask
    for state,src_name,wall_name in [('closed',m['images']['new104'],f'{id}-closed103.png'),('open',m['openImage'],f'{id}-open103.png')]:
        image=Image.open(SRC/src_name).convert('RGBA');source=np.array(image);wall=np.array(Image.open(WALL/wall_name).convert('RGBA'))
        crop=source[y0:y0+h*32,x0:x0+w*32].copy();crop[perimeter]=wall[y0:y0+h*32,x0:x0+w*32][perimeter]
        scene=Image.fromarray(crop)
        for key,name,x,y,sprite,replace in definitions.get(id,[]):
            if replace:
                # Replace one already blocked seat, borrowing the clear aisle
                # floor underneath instead of drawing two chairs on each other.
                scene.paste(image.crop((x0+3*32,y0+5*32,x0+4*32,y0+6*32)),(x*32,y*32))
            scene.alpha_composite(sprite,(x*32,y*32))
        a=source.copy();a[y0:y0+h*32,x0:x0+w*32]=np.array(scene)
        assert np.array_equal(np.array(scene)[perimeter],wall[y0:y0+h*32,x0:x0+w*32][perimeter])
        fullmask=np.zeros(source.shape[:2],bool);fullmask[y0:y0+h*32,x0:x0+w*32]=allowed
        assert np.array_equal(a[~fullmask],source[~fullmask])
        final=Image.fromarray(a);final.convert('RGB').save(OUT/f'{id}-{state}105.png')
        final.crop((max(0,x0-32),max(0,y0-32),min(image.width,x0+w*32+32),min(image.height,y0+h*32+48))).convert('RGB').save(OUT/f'{id}-detail-{state}.png')
    shutil.copy2(SRC/m['images']['new104'],OUT/f'{id}-previous104.png');shutil.copy2(SRC/m['map'],OUT/m['map'])
    assert (SRC/m['map']).read_bytes()==(OUT/m['map']).read_bytes()
    manifest['maps'].append({**m,'images':{'new105':f'{id}-closed105.png','previous104':f'{id}-previous104.png'},
      'openImage':f'{id}-open105.png','memberDetails':members})
    checks.append({'facility':id,'members':members,'geometryUnchanged':True,'memberPropsOnlyOnInteriorBlockedCells':True,
      'exteriorWall103PixelIdentical':True,'outsidePerimeterAndPropCellsUnchanged':True,'allDoorSprites104Unchanged':True,
      'mapSha256':hashlib.sha256((OUT/m['map']).read_bytes()).hexdigest()})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1000,690),'#151c20');d=ImageDraw.Draw(sheet)
for i,id in enumerate(['theater','gamers']):
    m=next(a for a in manifest['maps'] if a['facility']==id);x=i*500
    d.text((x+15,10),m['name'],font=font,fill='#e4ece6')
    im=Image.open(OUT/f'{id}-detail-closed.png');sheet.paste(im,(x+(500-im.width)//2,50))
    for j,a in enumerate(m['memberDetails']):d.text((x+15,500+j*35),a['name'],font=font,fill='#c9d5cd')
sheet.save(OUT/'member-comparison.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','facilities':9,'checks':checks,'nativeIntegration':False,
 'scope':'Functional interior props on existing blocked cells, removed exterior posters, preserved104 front-facing doors and103 walls.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared105 interior props and removed104 exterior posters on nine preserved maps.')
