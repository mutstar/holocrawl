"""Import generated sheets; only crop, nearest-neighbor fit, and tile placement."""
from pathlib import Path
from PIL import Image,ImageDraw
from collections import deque
import argparse,json,hashlib,shutil

root=Path(__file__).resolve().parents[1]
art=root/'assets/holocrawl/combat-art01';raw=art/'originals';raw.mkdir(parents=True,exist_ok=True)
rl=root/'engine/campaign-crawl/crawl-ref/source/rltiles';target=rl/'holo'
gods='suisei miko aki fubuki ayame choco korone okayu pekora noel watame towa lamy polka koyori lui raden hajime su vivi sopia mela'.split()
creatures='rose fox raven swordsman hound'.split()
effects='warning urgent shrine garden water gravity orbit fire exhibit spotlight frost rhythm shield slime impact comet'.split()
statuses='five shield warning urgent wrath cooldown resource active'.split()
p=argparse.ArgumentParser()
for k in ['summons','effects','ui','player']:p.add_argument('--'+k)
a=p.parse_args()
manifest_path=art/'manifest.json'
assets={x['id']:x for x in json.loads(manifest_path.read_text())['assets']} if manifest_path.exists() else {}

def save(name,tile,kind):
    path=target/(name+'.png');tile.save(path)
    assert tile.mode=='RGBA' and tile.size==(32,32) and tile.getchannel('A').getextrema()[0]==0,name
    assets[name]=dict(id=name,kind=kind,path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest().upper())

def fit(sheet,i,cols,rows,max_size=(28,28),position=None,align_bottom=False,main_object=False):
    x,y=i%cols,i//cols
    cell=sheet.crop((round(x*sheet.width/cols),round(y*sheet.height/rows),round((x+1)*sheet.width/cols),round((y+1)*sheet.height/rows)))
    # Generated transparent sheets can contain near-invisible edge noise.
    # Use visible alpha only to locate the crop; retain the original pixels.
    box=cell.getchannel('A').point(lambda v:255 if v>=96 else 0).getbbox();assert box,i
    if main_object:
        # Crop to the bird, excluding a detached sliver from the next cell.
        # This only selects the crop rectangle; original pixels/alpha remain intact.
        alpha=cell.getchannel('A');pixels=alpha.load();seen=set();best=[]
        for cy in range(cell.height):
            for cx in range(cell.width):
                if pixels[cx,cy]<96 or (cx,cy) in seen:continue
                component=[];q=deque([(cx,cy)]);seen.add((cx,cy))
                while q:
                    px,py=q.popleft();component.append((px,py))
                    for nx,ny in [(px-1,py),(px+1,py),(px,py-1),(px,py+1)]:
                        if 0<=nx<cell.width and 0<=ny<cell.height and (nx,ny) not in seen and pixels[nx,ny]>=96:seen.add((nx,ny));q.append((nx,ny))
                if len(component)>len(best):best=component
        if best:box=(max(0,min(p[0] for p in best)-1),max(0,min(p[1] for p in best)-1),min(cell.width,max(p[0] for p in best)+2),min(cell.height,max(p[1] for p in best)+2))
    sprite=cell.crop(box);sprite.thumbnail(max_size,Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(32,32))
    xy=position if position is not None else ((32-sprite.width)//2,31-sprite.height if align_bottom else (32-sprite.height)//2)
    tile.paste(sprite,xy);return tile

def original(kind,path):
    dest=raw/(kind+'-atlas.png')
    if path:shutil.copy2(path,dest)
    return Image.open(dest).convert('RGBA')

if a.summons:
    sheet=original('summons',a.summons)
    for i,g in enumerate(creatures):
        for frame in range(2):save(g if frame==0 else g+'_1',fit(sheet,i+frame*5,5,2,align_bottom=True,main_object=g=='raven'),'creature')
if a.effects:
    sheet=original('effects',a.effects)
    for i,g in enumerate(effects):
        for frame in range(2):save('fx_'+g+'_'+str(frame),fit(sheet,i*2+frame,8,4,max_size=(30,30)),'effect')
if a.ui:
    sheet=original('ui',a.ui)
    positions=[(0,0),(0,24),(24,0),(24,0),(24,0),(24,24),(24,24),(0,0)]
    for i,g in enumerate(statuses):save('status_'+g,fit(sheet,i,4,2,max_size=(8,8),position=positions[i]),'status')
if a.player:
    sheet=original('player',a.player)
    for i,name in enumerate(['avatar_base_a','avatar_base_b']):save(name,fit(sheet,i,2,1,max_size=(16,29),align_bottom=True),'player')
    for g in gods:
        icon=Image.open(target/('god_'+g+'.png')).convert('RGBA')
        icon=icon.crop(icon.getchannel('A').getbbox());icon.thumbnail((8,8),Image.Resampling.NEAREST)
        tile=Image.new('RGBA',(32,32));tile.paste(icon,(24,2))
        save('charm_'+g,tile,'faith-charm')

# Existing IDs stay in order; append animation/UI records to the same includes.
header='%prefix TILE\n%rim 0\n%back none\n%sdir holo\n'
path=rl/'dc-holo-main.txt';text=path.read_text(encoding='utf-8')
if 'HOLO_ROSE_1' not in text:text+='\n'+''.join(g+'_1 HOLO_'+g.upper()+'_1\n' for g in creatures)
if 'HOLO_STATUS_FIVE' not in text:text+='\n'+''.join('status_'+s+' HOLO_STATUS_'+s.upper()+'\n' for s in statuses)
path.write_text(text,encoding='utf-8')
if a.player:
    (rl/'dc-holo-player.txt').write_text(header.replace('TILE\n','TILEP\n',1)+''.join(n+' HOLO_'+n.upper()+'\n' for n in ['avatar_base_a','avatar_base_b'])+''.join('charm_'+g+' HOLO_CHARM_'+g.upper()+'\n' for g in gods),encoding='utf-8')
    path=rl/'dc-player.txt';text=path.read_text(encoding='utf-8')
    if '%include dc-holo-player.txt' not in text:path.write_text(text+'\n%include dc-holo-player.txt\n',encoding='utf-8')

for kind in ['creature','effect','status','player','faith-charm']:
    names=[x['id'] for x in assets.values() if x['kind']==kind]
    if kind=='creature':names=[g+('_1' if frame else '') for frame in range(2) for g in creatures if g+('_1' if frame else '') in names]
    if not names:continue
    cols=8 if kind in ['effect','faith-charm'] else 5 if kind=='creature' else 4 if kind=='status' else 2
    rows=(len(names)+cols-1)//cols
    preview=Image.new('RGBA',(cols*128,rows*148),(26,26,34,255));d=ImageDraw.Draw(preview)
    for i,n in enumerate(names):
        tile=Image.open(target/(n+'.png')).convert('RGBA');preview.alpha_composite(tile.resize((128,128),Image.Resampling.NEAREST),(i%cols*128,i//cols*148));d.text((i%cols*128+3,i//cols*148+130),n,fill='white')
    preview.save(art/(kind+'-preview.png'))
manifest_path.write_text(json.dumps(dict(tool='built-in image_gen',nativeSize=[32,32],assets=list(assets.values())),indent=2)+'\n',encoding='utf-8')
print('Imported',len(assets),'native combat art tiles so far.')
