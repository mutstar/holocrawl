"""Close only concave bevel corner gaps; keep study91 colour and geometry."""
from pathlib import Path
import json, hashlib, shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'preview/city-concrete91'
OUT=ROOT/'preview/city-concrete92'
OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
grain=np.array(Image.open(ROOT/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,dx,dy):
    out=np.zeros_like(a);h,w=a.shape;x0,x1=max(0,-dx),min(w,w-dx);y0,y1=max(0,-dy),min(h,h-dy)
    out[y0:y1,x0:x1]=a[y0+dy:y1+dy,x0+dx:x1+dx];return out

def render(base,rows):
    cell=np.array([[c=='#' for c in r] for r in rows]);solid=np.array([[c in '#+G' for c in r] for r in rows])
    up=lambda a:np.repeat(np.repeat(a,32,axis=0),32,axis=1)
    wall=up(cell);e,s,se=[up(near(solid,dx,dy)) for dx,dy in [(1,0),(0,1),(1,1)]]
    yy,xx=np.indices(wall.shape);px,py=xx%32,yy%32
    raw_front=wall&(py>=18)&~s
    # Three-pixel east face, with a diagonal mitre into the bottom14px front.
    # At a convex SE corner its width tapers3,2,1,0 instead of a black post.
    corner=wall&~e&~s&(py>=18)
    cut=29+((py-18)*3//13)
    side=wall&(px>=29)&(~e|((py>=18)&~se))&~(raw_front&e)
    side=np.where(corner,wall&(px>=cut),side)
    front=raw_front&~side
    # A separate west-facing stripe made two adjacent borders. Fold it into
    # the continuous coping footprint instead of adding another strip.
    cap=wall&~front&~side
    assert np.all((cap.astype('uint8')+front+side)[wall]==1)
    tex=grain[yy%grain.shape[0],xx%grain.shape[1]].mean(axis=2)
    noise=tex-tex.mean();a=base.copy()
    for mask,color,factor in [(cap,[31,37,40],.30),(front,[52,62,67],.65),(side,[48,58,64],.52)]:
        rgb=np.array(color)[None,None,:]+noise[:,:,None]*factor
        a[mask,:3]=np.clip(np.rint(rgb[mask]),0,255).astype('uint8')
    n=cap&~near(cap,0,-4);sedge=cap&~near(cap,0,4)
    w=cap&~near(cap,-4,0);edge=cap&~near(cap,4,0);rim=n|sedge|w|edge
    # Cardinal-only bands miss the4x4 square immediately behind an inside
    # corner. A diagonal footprint completes that same-width coping turn.
    diagonal=cap&(~near(cap,-4,-4)|~near(cap,4,-4)|~near(cap,-4,4)|~near(cap,4,4))
    repaired=diagonal&~rim
    rim|=repaired
    for k,c in enumerate([116,125,129]):
        layer=a[:,:,k];layer[rim]=np.clip(c+noise[rim]*.52,0,255).astype('uint8')
    # One joined bevel, with a moderate lighting change between its planes.
    north=cap&~near(cap,0,-1);west=cap&~near(cap,-1,0)
    south=cap&~near(cap,0,1);east=cap&~near(cap,1,0)
    a[north,:3]=[134,144,148];a[west,:3]=[124,136,141]
    a[south,:3]=[90,107,112];a[east,:3]=[87,105,111]
    for dx,dy,color in [(-1,-1,[129,140,145]),(1,-1,[110,125,130]),(-1,1,[107,121,126]),(1,1,[89,106,112])]:
        tip=cap&near(cap,dx,0)&near(cap,0,dy)&~near(cap,dx,dy)
        a[tip,:3]=color
        repaired|=tip
    # The front and side now share material and meet at the sloped corner.
    a[front&near(cap,0,-1),:3]=[49,65,70]
    a[side&near(cap,-1,0),:3]=[60,79,84]
    # Put joints only on straight runs, away from inside/outside turns.
    horizontal=n|sedge;vertical=w|edge
    straight_h=horizontal&near(horizontal,-4,0)&near(horizontal,4,0)
    straight_v=vertical&near(vertical,0,-4)&near(vertical,0,4)
    joints=((xx%48==0)&straight_h)|((yy%48==0)&straight_v)
    a[joints,:3]=(a[joints,:3].astype(float)*.83).astype('uint8')
    construction=front&(xx%64==0)&~near(side,1,0)
    a[construction,:3]=(a[construction,:3].astype(float)*.83).astype('uint8')
    holes=front&(yy%32==24)&(xx%48==14);a[holes,:3]=[41,52,56]
    # Pixel checks concern the repaired corner geometry, not visual preference.
    for y in range(len(rows)):
        for x in range(len(rows[0])):
            if not cell[y,x] or (x+1<len(rows[0]) and solid[y,x+1]) or (y+1<len(rows) and solid[y+1,x]):continue
            widths=side[y*32+18:y*32+32,x*32:(x+1)*32].sum(axis=1)
            assert np.all(widths[:-1]>=widths[1:]) and widths[-1]==0 and widths[0]==3
    assert np.array_equal(a[~wall],base[~wall]) and np.array_equal(a[:,:,3],base[:,:,3])
    return a,wall,repaired

manifest={'title':'잔향도시 · 콘크리트 접합 수정92','revision':92,'tileSize':32,'scope':'Palette-only preview; corner90 geometry retained.',
 'styles':[{'id':'concrete92','label':'접합 수정92'},{'id':'concrete91','label':'수정 전91'},{'id':'original84','label':'기존 도시벽84'}],
 'maps':[],'material':{'frontHeight':14,'eastSideWidth':3,'sideFrontCorner':'tapered mitre','separateWestStripe':False,'doubleDarkOutline':False}}
assert manifest['material']==prior['material']
checks=[]
for m in prior['maps']:
    source=ROOT/m['sourceMap'];data=json.loads(source.read_text());seed=m['seed']
    base_path=SRC/m['images']['original84'];old_path=SRC/m['images']['concrete91']
    original_hash,old_hash=sha(base_path),sha(old_path)
    base=np.array(Image.open(base_path).convert('RGBA'));a,wall,repaired=render(base,data['rows'])
    previous=np.array(Image.open(old_path).convert('RGBA'))
    changed=np.any(a!=previous,axis=2)
    assert not np.any(changed&~repaired)
    entry={k:m[k] for k in ['seed','width','height','sourceMap','sourceMapSha256','auditedWallAtlasSha256']};entry['images']={}
    for style,p in [('original84',base_path),('concrete91',old_path)]:
        name=f'{seed}-{style}.png';shutil.copy2(p,OUT/name);entry['images'][style]=name
    name=f'{seed}-concrete92.png';Image.fromarray(a).convert('RGB').save(OUT/name);entry['images']['concrete92']=name
    if seed==802302584:
        for style in ['concrete91','concrete92']:
            Image.open(OUT/entry['images'][style]).crop((29*32,35*32,36*32,44*32)).save(OUT/f'corner-{style}.png')
    assert sha(base_path)==original_hash and sha(old_path)==old_hash and sha(source)==m['sourceMapSha256']
    manifest['maps'].append(entry)
    checks.append({'seed':seed,'nonWallPixelsChanged':0,'alphaUnchanged':True,'prior91Unchanged':True,'convexSideTaperChecked':True,'onlyConcaveJoinPixelsChanged':True,'changedPixels':int(changed.sum()),'outsideJoinChanges':0})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
board=Image.new('RGB',(960,650),'#151c20');d=ImageDraw.Draw(board)
for i,(style,title) in enumerate([('concrete91','수정 전91 · 안쪽 모서리 틈'),('concrete92','수정92 · 안쪽 마감 연결')]):
    d.text((i*480+16,13),title,font=font,fill='#dce6dd')
    image=Image.open(OUT/f'corner-{style}.png').resize((448,576),Image.Resampling.NEAREST);board.paste(image,(i*480+16,58))
board.save(OUT/'material-comparison.png')
# Match the supplied screenshot exactly against native91 at2x. Keep the same
# screen rectangle for the after crop so the repaired4px join is easy to see.
screenshot=Path('C:/Users/IN/AppData/Local/Temp/codex-clipboard-f1590151-2698-4fbd-a410-58dff596ff32.png')
if screenshot.exists():
    supplied=Image.open(screenshot).convert('RGB')
    box=(2003,2426,2003+supplied.width,2426+supplied.height)
    close=Image.new('RGB',(620,300),'#151c20');draw=ImageDraw.Draw(close)
    for i,(style,title) in enumerate([('concrete91','수정 전 · 접합부 틈'),('concrete92','수정 후 · 이어진 마감')]):
        image=Image.open(OUT/f'802302584-{style}.png').convert('RGB')
        image=image.resize((image.width*2,image.height*2),Image.Resampling.NEAREST).crop(box)
        if i==0:assert np.array_equal(np.array(image),np.array(supplied))
        image.resize((supplied.width*2,supplied.height*2),Image.Resampling.NEAREST).save(OUT/f'join-{style}.png')
        close.paste(image.resize((supplied.width*2,supplied.height*2),Image.Resampling.NEAREST),(i*310+14,48))
        draw.text((i*310+14,9),title,font=font,fill='#dce6dd')
    close.save(OUT/'join-comparison.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','maps':2,'checks':checks,'nativeIntegration':False,
 'sourceScreenshotMatch':{'seed':802302584,'scale':2,'origin':[2003,2426],'pixelError':0} if screenshot.exists() else None,
 'scope':'Two existing maps; visual preference still for user review.'},indent=2)+'\n')
print(json.dumps({'status':'passed','maps':2,'nonWallPixelsChanged':0,'convexCornersTapered':True}))
