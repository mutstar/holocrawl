"""Import generated two-frame VFX strips without redrawing their pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, shutil

root = Path(__file__).resolve().parents[1]
art = root / 'assets/holocrawl/god-vfx01'
inputs = json.loads((art / 'inputs.json').read_text(encoding='utf-8'))
target = root / 'engine/campaign-crawl/crawl-ref/source/rltiles/holo'
assets = []
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 17)
sheet = Image.new('RGB', (900, 5 * 190), '#161d2a')
draw = ImageDraw.Draw(sheet)
for i, entry in enumerate(inputs):
    original = art / 'originals' / (entry['effect'] + '.png')
    original.parent.mkdir(parents=True, exist_ok=True)
    if not original.exists():
        shutil.copy2(entry['source'], original)
    strip = Image.open(original).convert('RGBA')
    x, y = (i % 2) * 450, (i // 2) * 190
    draw.text((x + 14, y + 8), entry['name'], font=font, fill='white')
    for frame in range(2):
        cell = strip.crop((round(frame * strip.width / 2), 0,
                           round((frame + 1) * strip.width / 2), strip.height))
        box = cell.getchannel('A').point(lambda a: 255 if a >= 96 else 0).getbbox()
        assert box, entry['effect']
        sprite = cell.crop(box)
        sprite.thumbnail((28, 28), Image.Resampling.NEAREST)
        tile = Image.new('RGBA', (32, 32))
        tile.paste(sprite, ((32 - sprite.width)//2, (32 - sprite.height)//2))
        name = f"fx_{entry['effect']}_{frame}"
        path = target / (name + '.png')
        assert not path.exists(), f'Refusing to replace an existing tile: {path}'
        tile.save(path)
        assets.append(dict(id=name, path=path.relative_to(root).as_posix(),
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                           original=original.relative_to(root).as_posix(),
                           frame=frame,
                           centerOpaqueFraction=sum(a>=96 for a in tile.getchannel('A').crop((10,10,22,22)).getdata())/144))
        sample = Image.new('RGBA', (128, 128), '#202838')
        sample.alpha_composite(tile.resize((128, 128), Image.Resampling.NEAREST))
        sheet.paste(sample.convert('RGB'), (x + 40 + frame * 165, y + 40))
assert len(assets) == 20
assert len({a['sha256'] for a in assets}) == 20, 'Frames must be distinct'
(art / 'manifest.json').write_text(json.dumps(dict(version='god-vfx01',
    mode='built-in image_gen; crop, alpha-preserving fit and nearest-neighbor only',
    assets=assets), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
sheet.save(art / 'contact-sheet.png')
print(art / 'contact-sheet.png')
