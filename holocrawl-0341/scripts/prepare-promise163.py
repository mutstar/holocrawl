"""Export generated raster originals to the project's small, hard-alpha sprites.

This is palette/size export only; original artwork remains unchanged beside exports.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'preview' / 'promise163'
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
board = Image.new('RGB',(720,460),'#1b2428')
draw = ImageDraw.Draw(board)
positions = [(18,36),(400,20),(20,225),(135,225),(250,290),(400,330)]
for s,pos in zip(specs,positions):
    a = Image.open(DEST / 'assets' / (s['id']+'-native.png')).convert('RGBA')
    a = a.resize((a.width*3,a.height*3),Image.Resampling.NEAREST)
    board.paste(a,pos,a)
    draw.text((pos[0],pos[1]-15),s['id'],fill='#d0ded7')
board.save(DEST / 'native-sprites163.png')
(DEST / 'assets163.json').write_text(json.dumps({'revision':163,'status':'user-review','assets':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exported':len(manifest),'sizes':{s['id']:s['native'] for s in manifest}}))
