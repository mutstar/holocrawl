"""Export generated simplified artwork on a coarse integer pixel grid."""
import json
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw

D = Path(__file__).resolve().parents[1] / 'preview' / 'area15-178'
specs = json.loads((D / 'prompts.json').read_text(encoding='utf-8'))['assets']
manifest = []
for s in specs:
    im = Image.open(D / 'assets' / (s['id'] + '-source.png')).convert('RGBA')
    assert im.getchannel('A').getextrema()[0] == 0
    bounds = im.getchannel('A').point(lambda a: 255 if a >= 210 else 0).getbbox()
    crop = im.crop(bounds)
    w, h = s['w'] // 2, s['h'] // 2
    scale = min((w - 2) / crop.width, (h - 2) / crop.height)
    size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    small = crop.convert('RGBa').resize(size, Image.Resampling.BOX).convert('RGBA')
    hard = small.getchannel('A').point(lambda a: 255 if a >= 170 else 0)
    # A small spread of source colors preserves rare member colors on the hub.
    hist = Counter(c[:3] for c, a in zip(small.getdata(), hard.getdata()) if a)
    points = list(hist)
    distances = [float('inf')] * len(points)
    chosen, palette = max(points, key=hist.get), []
    for _ in range(s['colors']):
        palette.append(chosen)
        for i, col in enumerate(points):
            distances[i] = min(distances[i], sum((col[k] - chosen[k]) ** 2 for k in range(3)))
        chosen = points[max(range(len(points)), key=lambda i: distances[i] * hist[points[i]] ** .5)]
    pal = Image.new('P', (1, 1))
    pal.putpalette([v for c in palette + [palette[0]] * (256-len(palette)) for v in c])
    small = small.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE).convert('RGBA')
    small.putalpha(hard)
    canvas = Image.new('RGBA', (w, h))
    canvas.alpha_composite(small, ((w-size[0]) // 2, h-1-size[1]))
    out = canvas.resize((s['w'], s['h']), Image.Resampling.NEAREST)
    out.save(D / 'assets' / (s['id'] + '-native.png'))
    colors = {c[:3] for c in out.getdata() if c[3]}
    manifest.append({'id':s['id'], 'native':[s['w'],s['h']], 'logical':[w,h], 'colors':len(colors), 'hardAlpha':True, 'visibleBounds':list(out.getbbox()), 'mode':'built-in image_gen; palette and integer-grid export'})

board = Image.new('RGB', (900,580), '#1b2428')
draw = ImageDraw.Draw(board)
positions = [(18,30),(360,30),(18,350),(240,350),(420,350)]
for s, pos in zip(specs, positions):
    a = Image.open(D / 'assets' / (s['id']+'-native.png')).convert('RGBA')
    a = a.resize((a.width*3,a.height*3), Image.Resampling.NEAREST)
    board.paste(a,pos,a)
    draw.text((pos[0],pos[1]-15),s['id'],fill='#d0ded7')
board.save(D / 'native-sprites178.png')
(D / 'assets178.json').write_text(json.dumps({'revision':178, 'status':'user-review', 'assets':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exported':len(manifest),'assets':manifest}))
