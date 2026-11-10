"""Export generated raster originals to the project's small, hard-alpha sprites.

This is palette/size export only; original artwork remains unchanged beside exports.
"""
import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'preview' / 'fortune165'
specs = json.loads((DEST / 'prompts.json').read_text(encoding='utf-8'))['assets']
manifest = []
for s in specs:
    im = Image.open(DEST / 'assets' / (s['id'] + '-source.png')).convert('RGBA')
    alpha = im.getchannel('A')
    assert alpha.getextrema()[0] == 0, 'Expected real generated transparency'
    bounds = alpha.point(lambda a: 255 if a >= 210 else 0).getbbox()
    assert bounds
    crop = im.crop(bounds)
    scale = min((s['w']-4)/crop.width, (s['h']-4)/crop.height)
    size = (max(1, round(crop.width*scale)), max(1, round(crop.height*scale)))
    # Premultiplied alpha prevents black/matte fringes around the reduced outline.
    small = crop.convert('RGBa').resize(size, Image.Resampling.BOX).convert('RGBA')
    hard = small.getchannel('A').point(lambda a: 255 if a >= 170 else 0)
    rgb = small.convert('RGB').quantize(colors=s['colors'], method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    if s['id'] == 'hub':
        # Rare colored network nodes must survive alongside a large gray casing.
        # Select a spread of actual source colors, ignoring fully transparent pixels.
        pixels = small.tobytes(); mask = hard.tobytes()
        hist = Counter(tuple(pixels[i*4:i*4+3]) for i,a in enumerate(mask) if a)
        points = list(hist); distances = [float('inf')]*len(points)
        chosen = max(points,key=hist.get); palette=[]
        for _ in range(s['colors']):
            palette.append(chosen)
            for i,col in enumerate(points):
                dist = sum((col[k]-chosen[k])**2 for k in range(3))
                distances[i] = min(distances[i],dist)
            chosen = points[max(range(len(points)),key=lambda i:distances[i]*hist[points[i]]**.5)]
        pal=Image.new('P',(1,1)); pal.putpalette([v for col in palette+[palette[0]]*(256-len(palette)) for v in col])
        rgb = small.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGB')
    small = rgb.convert('RGBA'); small.putalpha(hard)
    out = Image.new('RGBA', (s['w'], s['h']))
    offset = ((s['w']-size[0])//2, s['h']-2-size[1])
    out.alpha_composite(small, offset)
    out.save(DEST / 'assets' / (s['id']+'-native.png'))
    rgba = out.tobytes()
    colors = {rgba[i:i+3] for i in range(0,len(rgba),4) if rgba[i+3]}
    assert len(colors) <= s['colors']
    assert set(out.getchannel('A').tobytes()) <= {0, 255}
    manifest.append({'id':s['id'],'label':s['label'],'native':[s['w'],s['h']], 'colors':len(colors),'sourceSize':list(im.size),'sourceBounds':list(bounds),'visibleBounds':list(out.getbbox()),'mode':'built-in image_gen; native palette/size export','hardAlpha':True})

# Inspection board: nearest-neighbour enlargement of actual native exports.
board = Image.new('RGB',(720,720),'#1b2428')
draw = ImageDraw.Draw(board)
positions = [(18,30),(360,30),(18,260),(240,260),(462,260),(18,490),(240,490)]
for s,pos in zip(specs,positions):
    a = Image.open(DEST / 'assets' / (s['id']+'-native.png')).convert('RGBA')
    a = a.resize((a.width*3,a.height*3),Image.Resampling.NEAREST)
    board.paste(a,pos,a)
    draw.text((pos[0],pos[1]-15),s['id'],fill='#d0ded7')
board.save(DEST / 'native-sprites165.png')
(DEST / 'assets165.json').write_text(json.dumps({'revision':165,'status':'user-review','assets':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exported':len(manifest),'sizes':{s['id']:s['native'] for s in manifest}}))
