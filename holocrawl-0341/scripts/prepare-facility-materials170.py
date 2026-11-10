"""Export built-in generated swatches to a small limited palette; no geometry edits."""
import json
from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parents[1]/'preview/facility-exteriors170'
manifest=[]
for s in json.loads((D/'prompts.json').read_text(encoding='utf-8'))['assets']:
    im=Image.open(D/'assets'/(s['id']+'-source.png')).convert('RGB')
    im=im.resize((64,32),Image.Resampling.BOX).quantize(colors=s['colors'],method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB').resize((128,64),Image.Resampling.NEAREST)
    im.save(D/'assets'/(s['id']+'-native.png'))
    manifest.append({'id':s['id'],'native':[128,64],'logical':[64,32],'colors':len(set(im.getdata())),'opaque':True})
(D/'materials170.json').write_text(json.dumps({'revision':170,'mode':'built-in image_gen; palette/size export','assets':manifest},indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest))
