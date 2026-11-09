from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1];art=root/'assets/holocrawl/tiles01';raw=art/'originals';raw.mkdir(parents=True,exist_ok=True)
origin=Path(r'C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
for source,name in [('exec-5414e05f-8787-450d-908e-df62c1c8e0b1.png','sprites-atlas.png'),('exec-8d8751af-a2c8-4ee4-a379-2346d514fa74.png','effects-atlas.png')]:
 if not (raw/name).exists():shutil.copy2(origin/source,raw/name)
rl=root/'engine/campaign-crawl/crawl-ref/source/rltiles';tiles=rl/'holo';tiles.mkdir(exist_ok=True)
gods=['suisei','miko','aki','fubuki','ayame','choco','korone','okayu','pekora','noel','watame','towa','lamy','polka','koyori','lui','raden','hajime','su','vivi','sopia','mela']
names=['rose','fox','raven','swordsman','hound','carrot','orbit_icon','warning_icon','puddle','impact_icon']
fx=['warning','urgent','shrine','garden','water','gravity','orbit','fire','exhibit','spotlight','frost','rhythm','shield','slime','impact','comet']
manifest=[]
def export(img,index,name,kind):
 w,h=img.size;x=index%8;y=index//8
 crop=img.crop((round(x*w/8),round(y*h/4),round((x+1)*w/8),round((y+1)*h/4)))
 bbox=crop.getchannel('A').getbbox();assert bbox,name
 sprite=crop.crop(bbox);sprite.thumbnail((28,28),Image.Resampling.NEAREST)
 target=Image.new('RGBA',(32,32));target.alpha_composite(sprite,((32-sprite.width)//2,(32-sprite.height)//2))
 target.save(tiles/(name+'.png'))
 alpha=target.getchannel('A');assert alpha.getextrema()[0]==0
 manifest.append(dict(id=name,kind=kind,sourceCell=index,file='engine/campaign-crawl/crawl-ref/source/rltiles/holo/'+name+'.png',width=32,height=32,sha256=hashlib.sha256((tiles/(name+'.png')).read_bytes()).hexdigest()))
 return target
sheet=Image.open(raw/'sprites-atlas.png').convert('RGBA');preview=Image.new('RGBA',(8*128,4*144),(23,20,32,255));draw=ImageDraw.Draw(preview)
for i,name in enumerate(gods+names):
 tile=export(sheet,i,'god_'+name if i<22 else name,'god' if i<22 else 'sprite')
 preview.alpha_composite(tile.resize((96,96),Image.Resampling.NEAREST),(i%8*128+16,i//8*144+8));draw.text((i%8*128+8,i//8*144+112),name,fill='white')
preview.save(art/'sprites-preview.png')
sheet=Image.open(raw/'effects-atlas.png').convert('RGBA');preview=Image.new('RGBA',(8*128,4*144),(23,20,32,255));draw=ImageDraw.Draw(preview)
for i in range(32):
 name=fx[i//2]+'_'+str(i%2);tile=export(sheet,i,'fx_'+name,'effect')
 preview.alpha_composite(tile.resize((96,96),Image.Resampling.NEAREST),(i%8*128+16,i//8*144+8));draw.text((i%8*128+6,i//8*144+112),name,fill='white')
preview.save(art/'effects-preview.png')
header='%prefix TILE\n%rim 0\n%back none\n%sdir holo\n'
(rl/'dc-holo-feat.txt').write_text(header+''.join('god_'+g+' HOLO_GOD_'+g.upper()+'\n' for g in gods)+''.join('fx_'+f+'_'+str(n)+' HOLO_FX_'+f.upper()+'_'+str(n)+'\n' for f in fx for n in range(2))+'carrot HOLO_CARROT\n',encoding='utf-8')
(rl/'dc-holo-main.txt').write_text(header+''.join(g+' HOLO_'+g.upper()+'\n' for g in ['rose','fox','raven','swordsman','hound'])+''.join('fx_'+f+'_'+str(n)+' HOLO_BURST_'+f.upper()+'_'+str(n)+'\n' for f in ['impact','comet'] for n in range(2)),encoding='utf-8')
for name,include in [('dc-main.txt','dc-holo-main.txt'),('dc-feat.txt','dc-holo-feat.txt')]:
 p=rl/name;t=p.read_text(encoding='utf-8');line='%include '+include
 if line not in t:p.write_text(t+'\n# HoloCrawl generated asset registry\n'+line+'\n',encoding='utf-8')
(art/'manifest.json').write_text(json.dumps(dict(version='tiles01',importPipeline='Equal 8x4 atlas slicing, alpha bounding-box fit to 28px, nearest-neighbor resize into transparent 32px tiles; originals unchanged.',assets=manifest),indent=2)+'\n',encoding='utf-8')
print('Imported',len(manifest),'RGBA tiles, native registries and previews.')

