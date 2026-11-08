"""Restore member identity and remove legacy rotated facility-door sprites."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'preview/city-facilities103';OUT=ROOT/'preview/city-facilities104'
OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
native95=ROOT/'preview/city-facilities95';art94=ROOT/'preview/city-facilities94'
theater=Image.open(ROOT/'preview/theater-wall31/assets/theater-native.png').convert('RGBA')
manifest={**prior,'revision':104,'title':'잔향도시 · 멤버 장식 복원과 문 방향 수정',
 'styles':[{'id':'new104','label':'멤버 장식·문 방향 수정'},{'id':'previous103','label':'수정 전103'}],'maps':[],'defaultSample':1}
checks=[]

def shape(rows,colors):
    im=Image.new('RGBA',(max(map(len,rows)),len(rows)))
    for y,row in enumerate(rows):
        for x,c in enumerate(row):
            if c!='.':im.putpixel((x,y),colors[c]+(255,))
    return im

def plaque(image,x,y,icon,accent,kind='paper',height=35):
    """A24px inset panel stays between the unchanged structural wall edges."""
    d=ImageDraw.Draw(image);d.rectangle((x,y,x+23,y+height-1),fill=(24,31,36))
    d.rectangle((x+1,y+1,x+22,y+height-2),fill=(115,100,74) if kind=='paper' else (81,105,105))
    d.rectangle((x+3,y+3,x+20,y+height-4),fill=(204,183,146) if kind=='paper' else (32,50,55))
    d.line((x+3,y+3,x+20,y+3),fill=accent)
    # A distinct icon fills most of the poster, rather than a tiny corner decal.
    iw,ih=icon.size;image.alpha_composite(icon,(x+(24-iw)//2,y+6))
    d.line((x+6,y+height-7,x+17,y+height-7),fill=accent)
    return (x,y,x+24,y+height)

for m in prior['maps']:
    id=m['facility'];o=m['origin'];x0,y0=o['x']*32,o['y']*32;w,h=o['width'],o['height']
    data=json.loads((SRC/m['map']).read_text());local=[r[o['x']:o['x']+w] for r in data['rows'][o['y']:o['y']+h]]
    original=Image.open(SRC/m['images']['new103']).convert('RGBA')
    decorated=original.crop((x0,y0,x0+w*32,y0+h*32));mask=np.zeros((h*32,w*32),bool);members=[]
    if id=='theater':
        # Reuse the exact approved Gen2 icons, enlarged with nearest sampling.
        icons=[('ayame','아야메 · 오니 가면',(4,42),theater.crop((8,8,20,19)).resize((18,17),Image.Resampling.NEAREST),(182,72,77)),
               ('choco','초코 · 날개 하트',(w*32-28,42),theater.crop((75,12,90,25)).resize((20,18),Image.Resampling.NEAREST),(226,132,160)),
               ('subaru','스바루 · 오리',(4,176),theater.crop((8,19,20,28)).resize((20,15),Image.Resampling.NEAREST),(223,183,66))]
        for key,name,(x,y),icon,col in icons:
            box=plaque(decorated,x,y,icon,col);mask[box[1]:box[3],box[0]:box[2]]=True
            members.append({'id':key,'name':name,'box':list(box),'source':'theater-wall31 approved entrance icon'})
    if id=='gamers':
        # The railway case keeps the white fox, mint inner ears and dark eyes.
        fox=shape(['w.........w','ww.......ww','wmw.....wmw','wmmwwwwwmmw','wwwwwwwwwww',
          '.wkwwwwwkw.','..wwwwwww..','...wwkww...','....www....'],
          {'w':(225,229,218),'m':(114,187,178),'k':(37,57,64)}).resize((20,17),Image.Resampling.NEAREST)
        box=plaque(decorated,4,64,fox,(159,219,207),'enamel',40);mask[box[1]:box[3],box[0]:box[2]]=True
        members.append({'id':'fubuki','name':'후부키 · 흰여우 신호함','box':list(box),'source':'gamers-station64 white fox signal motif'})
        # A red lacquered tarot cabinet with a wolf crest makes Mio legible.
        wolf=shape(['.b.......b.','.bb.....bb.','.bgb...bgb.','..bbbbbbb..','..brbbbrb..','...bwbwb...','....www....','.....b.....'],
          {'b':(35,38,43),'g':(148,104,99),'r':(215,87,89),'w':(211,207,189)}).resize((18,14),Image.Resampling.NEAREST)
        x=w*32-28;y=48;box=plaque(decorated,x,y,wolf,(195,107,111),'enamel',47)
        d=ImageDraw.Draw(decorated);d.rectangle((x+4,y+23,x+19,y+37),fill=(111,48,58))
        for dx,dy in [(5,26),(10,24),(15,26)]:
            d.rectangle((x+dx,y+dy,x+dx+3,y+dy+9),fill=(208,177,122));d.rectangle((x+dx+1,y+dy+3,x+dx+2,y+dy+5),fill=(93,65,102))
        mask[box[1]:box[3],box[0]:box[2]]=True
        members.append({'id':'mio','name':'미오 · 늑대 문장 타로함','box':list(box),'source':'gamers-station64 red tarot cabinet motif'})
        members.extend([{'id':'korone','name':'코로네 · 코로네스키 벤치','unchanged':True},
                        {'id':'okayu','name':'오카유 · 주먹밥 자판기','unchanged':True}])
    # Every new decorative pixel is mounted on a pre-existing solid wall cell.
    wall=np.repeat(np.repeat(np.array([[c=='#' for c in row] for row in local]),32,0),32,1)
    assert not np.any(mask&~wall)
    oldlocal=np.array(original)[y0:y0+h*32,x0:x0+w*32]
    assert np.array_equal(np.array(decorated)[~mask],oldlocal[~mask])
    native_original=Image.open(art94/f'{id}-original84.png').convert('RGBA');nativea=np.array(native_original)
    candidates=[]
    for y,row in enumerate(local):
        for x,c in enumerate(row):
            if c=='.' and 0<x<w-1 and 0<y<h-1:
                tile=nativea[y0+y*32:y0+(y+1)*32,x0+x*32:x0+(x+1)*32]
                score=np.abs(np.diff(tile[:,:,:3].astype(float),axis=0)).mean()+np.abs(np.diff(tile[:,:,:3].astype(float),axis=1)).mean()
                candidates.append((float(score),x,y))
    _,fx,fy=min(candidates);floor=native_original.crop((x0+fx*32,y0+fy*32,x0+(fx+1)*32,y0+(fy+1)*32))
    door_mask=np.zeros((h*32,w*32),bool);door_checks=[]
    for n,p in enumerate(m['facilityDoors'],1):
        lx,ly=p['x']-o['x'],p['y']-o['y'];width=p['width']
        door_mask[ly*32:(ly+1)*32,lx*32:(lx+width)*32]=True
        for state in ['closed','open']:
            sprite=Image.open(native95/f'{id}-door-{n}-{state}.png').convert('RGBA')
            if p['vertical']:
                sprite=sprite.transpose(Image.Transpose.ROTATE_270)
                assert sprite.size==(32,32)
                # These are the original front-facing95 pixels, never a rotated
                # substitute. Cross-check against a same-width horizontal door.
                for j,other in enumerate(m['facilityDoors'],1):
                    if not other['vertical'] and other['width']==1:
                        ref=Image.open(native95/f'{id}-door-{j}-{state}.png').convert('RGBA')
                        assert np.array_equal(np.array(sprite),np.array(ref))
            sprite.save(OUT/f'{id}-door-{n}-{state}-front.png')
        door_checks.append({'x':p['x'],'y':p['y'],'width':width,'placementAxis':'vertical' if p['vertical'] else 'horizontal',
          'spriteFacing':'front','rotationApplied':False,'legacyRotationRemoved':p['vertical']})
    allowed=np.zeros(np.array(original).shape[:2],bool);allowed[y0:y0+h*32,x0:x0+w*32]=mask|door_mask
    for state,source in [('closed',m['images']['new103']),('open',m['openImage'])]:
        image=Image.open(SRC/source).convert('RGBA');a=np.array(image);a[y0:y0+h*32,x0:x0+w*32][mask]=np.array(decorated)[mask];image=Image.fromarray(a)
        for n,p in enumerate(m['facilityDoors'],1):
            if p['vertical']:
                image.paste(floor,(p['x']*32,p['y']*32));image.alpha_composite(Image.open(OUT/f'{id}-door-{n}-{state}-front.png').convert('RGBA'),(p['x']*32,p['y']*32))
            elif state=='open':
                oldopen=Image.open(native95/f'{id}-open95.png').convert('RGBA')
                box=(p['x']*32,p['y']*32,(p['x']+p['width'])*32,(p['y']+1)*32);image.paste(oldopen.crop(box),box[:2])
        assert np.array_equal(np.array(image)[~allowed],np.array(Image.open(SRC/source).convert('RGBA'))[~allowed])
        image.convert('RGB').save(OUT/f'{id}-{state}104.png')
        image.crop((max(0,x0-32),max(0,y0-32),min(image.width,x0+w*32+32),min(image.height,y0+h*32+48))).convert('RGB').save(OUT/f'{id}-detail-{state}.png')
    shutil.copy2(SRC/m['images']['new103'],OUT/f'{id}-previous103.png');shutil.copy2(SRC/m['map'],OUT/m['map'])
    assert (OUT/m['map']).read_bytes()==(SRC/m['map']).read_bytes()
    manifest['maps'].append({**m,'images':{'new104':f'{id}-closed104.png','previous103':f'{id}-previous103.png'},'openImage':f'{id}-open104.png',
      'basicDoors':m['doors'],'doors':m['doors']+m['facilityDoors'],'memberDetails':members,'doorFacingChecks':door_checks})
    checks.append({'facility':id,'members':members,'doorFacing':door_checks,'newArtOnlyOnExistingWallCells':True,
      'outsideDecorationAndFacilityDoorCellsUnchanged':True,'normalWallsAndBasicDoorsUnchanged':True,'geometryUnchanged':True,
      'mapSha256':hashlib.sha256((OUT/m['map']).read_bytes()).hexdigest()})
    print('Prepared104',id,flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1000,680),'#151c20');d=ImageDraw.Draw(sheet)
for i,id in enumerate(['theater','gamers']):
    m=next(m for m in manifest['maps'] if m['facility']==id);x=i*500
    d.text((x+15,10),m['name'],font=font,fill='#e4ece6')
    im=Image.open(OUT/f'{id}-detail-closed.png');im=im.resize((im.width*1,im.height*1),Image.Resampling.NEAREST);sheet.paste(im,(x+(500-im.width)//2,50))
    names=' / '.join(a['name'].split(' · ')[0] for a in m['memberDetails']);d.text((x+15,485),names,font=font,fill='#b8ccc1')
    for j,a in enumerate(m['memberDetails']):d.text((x+15,520+j*29),a['name'],font=font,fill='#c9d5cd')
sheet.save(OUT/'member-comparison.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','facilities':9,'checks':checks,'nativeIntegration':False,
 'scope':'Member wall decor on theater/gamers and front-facing facility doors on all nine unchanged native maps.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
