"""Replace complete facility perimeter walls, retaining explicit inset artwork only.

Unlike95, no brightness-derived ornament mask can resurrect retired wall borders.
Native geometry, interior scenery and approved ordinary doors stay frozen.
"""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from city_concrete_material92 import render

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'preview/city-doors102';OUT=ROOT/'preview/city-facilities103'
OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
themes={'holox':(160,112,194),'theater':(177,117,81),'dev':(164,119,187),'dining':(177,132,92),
 'gamers':(116,168,157),'fantasy':(160,166,106),'wheel':(166,123,166),'market':(119,168,133),'mountain':(177,161,115)}
# Reviewed artwork bounding boxes, excluding long old facade trims. These are
# inset panels, not brightness masks or crops of the complete old wall strip.
top_panels={'holox':[(32,5,256,26)],'theater':[(24,3,232,29)],'dining':[(111,17,178,28)],
 'gamers':[(30,3,128,17),(194,4,232,20)],'market':[(104,17,184,28)],
 'mountain':[(64,3,224,61)]}
manifest={**prior,'title':'잔향도시 · 시설 외벽 연결 수정','revision':103,
 'styles':[{'id':'new103','label':'새 벽에 맞춘 시설 외벽'},{'id':'previous102','label':'수정 전 외벽'}],
 'maps':[],'nativeIntegration':False,'facilityWallRevision':103}
checks=[]
for m in prior['maps']:
    id=m['facility'];data=json.loads((SRC/m['map']).read_text());o=m['origin'];w,h=o['width'],o['height']
    x0,y0=o['x']*32,o['y']*32;x1,y1=x0+w*32,y0+h*32
    before=Image.open(SRC/m['images']['new102']).convert('RGBA');old=np.array(before)
    local_rows=[r[o['x']:o['x']+w] for r in data['rows'][o['y']:o['y']+h]]
    # Furniture is collision-solid in the native export, but is not a connected
    # ceiling mass. Do not let a stage/shelf erase the perimeter's front face.
    visual_rows=[list(r) for r in data['rows']]
    for ly in range(1,h-1):
        for lx in range(1,w-1):
            if local_rows[ly][lx] in '#G':visual_rows[o['y']+ly][o['x']+lx]='.'
    concrete,_,_=render(old,[''.join(r) for r in visual_rows],grain)
    shell=np.zeros((h*32,w*32),bool);fence=np.zeros_like(shell);portals=[]
    for y,row in enumerate(local_rows):
        for x,c in enumerate(row):
            if x not in (0,w-1) and y not in (0,h-1):continue
            if c=='#':shell[y*32:(y+1)*32,x*32:(x+1)*32]=True
            if c=='G':fence[y*32:(y+1)*32,x*32:(x+1)*32]=True
            if c=='.':portals.append((x,y))
    crop=old[y0:y1,x0:x1].copy();fresh=concrete[y0:y1,x0:x1]
    crop[shell]=fresh[shell]
    artmask=np.zeros_like(shell)
    # Extract panel artwork, then seat it within the new concrete coping.
    srcart=before.crop((x0,y0,x1,y1))
    for box in top_panels.get(id,[]):
        panel=srcart.crop(box)
        # Keep the mountain faces full-sized; other signs sit below a4px rim.
        dest=(box[0],box[1]) if id=='mountain' else (box[0],19)
        if id=='holox':
            # The old violet facade rail was not a member ornament. Retain its
            # round lamps as separate recesses, never the continuous old rail.
            continue
        if id!='mountain':panel=panel.resize((panel.width,min(12,panel.height)),Image.Resampling.NEAREST)
        a=np.array(panel);xx,yy=dest;hh,ww=a.shape[:2]
        mask=shell[yy:yy+hh,xx:xx+ww].copy()
        # Rim and side face are structural: no decal can overwrite them.
        mask &= np.indices(mask.shape)[0]+yy>=5
        mask &= np.indices(mask.shape)[1]+xx>=5
        mask &= np.indices(mask.shape)[1]+xx<w*32-5
        crop[yy:yy+hh,xx:xx+ww][mask]=a[mask]
        artmask[yy:yy+hh,xx:xx+ww]|=mask
    # Small theme insets sit on the cap. Continuous outer edges stay material92.
    panelimage=Image.fromarray(crop);d=ImageDraw.Draw(panelimage)
    accent=themes[id]
    if id=='holox':
        for cx in [54,111,175,234]:
            d.rectangle((cx-9,19,cx+9,30),fill=(28,34,44))
            d.ellipse((cx-5,20,cx+5,29),fill=(99,61,143),outline=accent)
            d.rectangle((cx-2,21,cx+1,23),fill=(213,173,238))
            artmask[19:31,cx-9:cx+10]=True
    if id=='dev':
        # Pink/teal studio lights in recessed boxes, replacing the floating rail.
        for xa,xb,col in [(43,94,(199,125,172)),(192,245,(108,164,183))]:
            d.rectangle((xa,21,xb,27),fill=(26,34,42));d.line((xa+3,24,xb-3,24),fill=col,width=2)
            artmask[21:28,xa:xb+1]=True
    if id=='wheel':
        for cx,col in [(44,(214,169,128)),(88,(173,130,176)),(199,(204,159,117)),(240,(194,141,178))]:
            d.rectangle((cx-4,21,cx+4,28),fill=(35,38,47));d.rectangle((cx-2,23,cx+2,26),fill=col)
            artmask[21:29,cx-4:cx+5]=True
    crop=np.array(panelimage)
    # Outdoor ground retains its transparent rail geometry. Its concrete plinth
    # uses the same material family without turning the fence into a solid wall.
    fence_edit=np.zeros_like(shell)
    if id=='fantasy':
        for y,row in enumerate(local_rows):
            for x,c in enumerate(row):
                if c!='G' or (x not in (0,w-1) and y not in (0,h-1)):continue
                if y in (0,h-1):sl=(slice(y*32+27,y*32+32),slice(x*32,(x+1)*32))
                elif x==0:sl=(slice(y*32,(y+1)*32),slice(x*32+27,x*32+32))
                else:sl=(slice(y*32,(y+1)*32),slice(x*32,x*32+5))
                crop[sl]=[62,77,81,255];fence_edit[sl]=True
    # Open entry paths get a compact matching frame; do not retain the obsolete
    # long header lines on their floor tile. The portal itself stays visibly open.
    portal_mask=np.zeros_like(shell)
    for x,y in portals:
        # Quiet floor underlay taken from a nearby walkable facility interior.
        floors=[]
        for fy,row in enumerate(local_rows):
            for fx,c in enumerate(row):
                if c!='.' or fx in (0,w-1) or fy in (0,h-1):continue
                tile=old[y0+fy*32:y0+(fy+1)*32,x0+fx*32:x0+(fx+1)*32]
                score=np.abs(np.diff(tile[:,:,:3].astype(float),axis=0)).mean()+np.abs(np.diff(tile[:,:,:3].astype(float),axis=1)).mean()
                floors.append((score,fx,fy))
        _,fx,fy=min(floors)
        tile=Image.fromarray(old[y0+fy*32:y0+(fy+1)*32,x0+fx*32:x0+(fx+1)*32]);td=ImageDraw.Draw(tile)
        td.rectangle((0,0,2,31),fill=(109,127,134));td.rectangle((29,0,31,31),fill=(73,95,103))
        td.line((0,0,0,31),fill=(130,141,145));td.line((31,0,31,31),fill=(87,105,111))
        td.rectangle((3,0,28,2),fill=(116,125,129));td.line((5,4,26,4),fill=accent)
        crop[y*32:(y+1)*32,x*32:(x+1)*32]=np.array(tile);portal_mask[y*32:(y+1)*32,x*32:(x+1)*32]=True
    # Theme plaques next to the entry are separate compact decorations on the
    # new wall surface. Never copy the old whole entrance strip back.
    for p in m['entrances'][:1]:
        x,y=p['x']-o['x'],p['y']-o['y'];sy=y*32
        for lx in [x-1,x+1]:
            if not 0<=lx<w or local_rows[y][lx]!='#':continue
            xa=lx*32+10;box=(xa,sy+6,xa+11,sy+15)
            im=Image.fromarray(crop);di=ImageDraw.Draw(im);di.rectangle(box,fill=(29,38,46),outline=accent)
            if id=='dev':
                di.line((xa+3,sy+9,xa+8,sy+9),fill=(204,133,177));di.line((xa+3,sy+12,xa+8,sy+12),fill=(108,174,187))
            else:di.line((xa+3,sy+10,xa+8,sy+10),fill=accent,width=2)
            crop=np.array(im);artmask[sy+6:sy+16,xa:xa+12]=True
    # Keep all internal floors/furniture/character artwork exactly, with no
    # automatic restoration of old outer lines by brightness or colour.
    allowed_local=shell|fence_edit|portal_mask
    assert np.array_equal(crop[~allowed_local],old[y0:y1,x0:x1][~allowed_local])
    assert not np.any(artmask&~shell)
    assert np.array_equal(crop[shell&~artmask],fresh[shell&~artmask])
    allowed=np.zeros(old.shape[:2],bool);allowed[y0:y1,x0:x1]=allowed_local
    for state,source_name in [('closed',m['images']['new102']),('open',m['openImage'])]:
        im=Image.open(SRC/source_name).convert('RGBA');a=np.array(im);a[y0:y1,x0:x1][allowed_local]=crop[allowed_local]
        before_state=np.array(im);assert np.array_equal(a[~allowed],before_state[~allowed])
        final=Image.fromarray(a);final.convert('RGB').save(OUT/f'{id}-{state}103.png')
        bounds=(max(0,x0-32),max(0,y0-32),min(im.width,x1+32),min(im.height,y1+48))
        final.crop(bounds).convert('RGB').save(OUT/f'{id}-detail-{state}.png')
    shutil.copy2(SRC/m['images']['new102'],OUT/f'{id}-previous102.png');shutil.copy2(SRC/m['map'],OUT/m['map'])
    assert (OUT/m['map']).read_bytes()==(SRC/m['map']).read_bytes()
    manifest['maps'].append({**m,'images':{'new103':f'{id}-closed103.png','previous102':f'{id}-previous102.png'},'openImage':f'{id}-open103.png'})
    checks.append({'facility':id,'perimeterWallPixels':int(shell.sum()),'explicitInsetPixels':int(artmask.sum()),
      'wallMaterial92ExactOutsideInsets':True,'interiorSceneryUnchanged':True,'normalWallsAndBasicDoorsUnchanged':True,
      'geometryUnchanged':True,'outsideAllowedPixelsUnchanged':True,'mapSha256':hashlib.sha256((OUT/m['map']).read_bytes()).hexdigest(),
      'openPortalsReframed':len(portals),'outdoorFencePreserved':id=='fantasy'})
    print('Rebuilt perimeter:',id,flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1296,1530),'#151c20');d=ImageDraw.Draw(sheet)
for i,m in enumerate(manifest['maps']):
    x=i%3*432;y=i//3*510;d.text((x+12,y+8),m['name'],font=font,fill='#e2ebe6')
    im=Image.open(OUT/f'{m["facility"]}-detail-closed.png');im.thumbnail((408,462),Image.Resampling.NEAREST);sheet.paste(im,(x+12,y+40))
sheet.save(OUT/'all-facilities.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','facilities':9,'checks':checks,'normalWallRevision':92,
 'basicDoorRevision':101,'nativeIntegration':False,'scope':'Full perimeter replacement with explicit inset artwork, frozen geometry and interior scenery.'},indent=2)+'\n')
