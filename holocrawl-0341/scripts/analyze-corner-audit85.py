"""Audit every generated wall/corner against the compiled atlas; build a visual sample."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import re
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
run = root / 'analysis/native-corner-audit85'
preview = root / 'preview/wall-audit85'
source = root / 'engine/upstream/crawl-ref/source'
plan = json.loads((run / 'plan.json').read_text())
manifest = json.loads((preview / 'manifest.json').read_text())
generation = json.loads((run / 'generation-validation.json').read_text())
topology = json.loads((run / 'topology-validation.json').read_text())
assert generation['status'] == topology['status'] == 'passed'
assert hashlib.sha256((source / 'dat/tiles/wall.png').read_bytes()).hexdigest() == plan['inputSha256']['atlas']
assert hashlib.sha256((root / 'preview/city-batch22/wall-corners84.js').read_bytes()).hexdigest() == plan['inputSha256']['renderer']

# Read the actual generated C++ coordinates rather than assuming atlas ordering.
cc = (source / 'rltiles/tiledef-wall.cc').read_text()
info = [tuple(map(int, v.split(','))) for v in re.findall(r'tile_info\((\d[^)]*)\)', cc)]
names = re.findall(r'_name_pair\("(holo_city_wall78_\d+_\d+)", (\d+) \+ TILE_FLOOR_MAX\)', cc)
assert len(names) == 2048
wall_atlas = Image.open(preview / 'assets/wall.png').convert('RGBA')
coordinates = {}
for name, index in names:
    width, height, dx, dy, sx, sy, ex, ey = info[int(index)]
    assert (width, height, dx, dy, ex-sx, ey-sy) == (32, 32, 0, 0, 32, 32)
    tile = wall_atlas.crop((sx, sy, ex, ey))
    expected = Image.open(source / f'rltiles/holocrawl/{name}.png').convert('RGBA')
    assert tile.tobytes() == expected.tobytes(), name
    assert tile.getextrema()[3] == (255, 255), name
    coordinates[(sx, sy)] = name

directions = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
patterns, masks, corner_counts = Counter(), Counter(), Counter()
representatives, candidates, all_maps = {}, defaultdict(list), {}
wall_cells = 0
geometry_hashes=set()
with (run / 'corners.jsonl').open('w') as log:
    for entry in manifest['maps']:
        path = preview / entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
        data = json.loads(path.read_text())
        geometry_hashes.add(hashlib.sha256(json.dumps(data['rows'],separators=(',',':')).encode()).hexdigest())
        all_maps[data['seed']] = data
        rows, width, height = data['rows'], data['width'], data['height']
        solid = lambda x,y: not (0 <= x < width and 0 <= y < height) or rows[y][x] in '#G+'
        this_wall = set()
        for y in range(height):
            for x in range(width):
                tile = data['palette'][data['features'][y*width+x]]
                if rows[y][x] != '#' or tile['atlas'] != 'wall':
                    continue
                mask = sum(1 << bit for bit,(dx,dy) in enumerate(directions) if solid(x+dx,y+dy))
                variant = (data['seed'] ^ (x*374761393) ^ (y*668265263)) & 7
                actual = coordinates.get((tile['sx'],tile['sy']))
                assert actual == f'holo_city_wall78_{mask}_{variant}', (data['seed'],x,y,actual,mask,variant)
                masks[mask] += 1
                patterns[(mask,variant)] += 1
                representatives.setdefault(mask, {'seed':data['seed'],'x':x,'y':y,'mask':mask})
                this_wall.add((x,y))
                wall_cells += 1
        for y in range(1,height-2):
            for x in range(1,width-2):
                positions = [(x,y),(x+1,y),(x,y+1),(x+1,y+1)]
                pattern = sum(1 << bit for bit,(xx,yy) in enumerate(positions) if solid(xx,yy))
                if pattern.bit_count() not in [1,3] or not any(p in this_wall for p in positions):
                    continue
                corner_counts[pattern] += 1
                record = {'seed':data['seed'],'x':x,'y':y,'pattern':pattern}
                log.write(json.dumps(record)+'\n')
                # Keep three examples from different random floors per orientation.
                group = candidates[pattern]
                if len(group)<3 and all(p['seed']!=data['seed'] for p in group):
                    group.append(record)

expected_patterns = {1,2,4,8,7,11,13,14}
assert set(corner_counts) == expected_patterns
assert all(len(candidates[k])==3 for k in expected_patterns)

atlases = {name:Image.open(preview/f'assets/{name}.png').convert('RGBA') for name in ['floor','wall','feat']}
def draw_region(data,x,y,w=6,h=6):
    x=max(0,min(data['width']-w,x-2));y=max(0,min(data['height']-h,y-2))
    image=Image.new('RGBA',(w*32,h*32))
    for yy in range(h):
        for xx in range(w):
            i=(y+yy)*data['width']+x+xx
            for layer in ['floors','features']:
                t=data['palette'][data[layer][i]]
                tile=atlases[t['atlas']].crop((t['sx'],t['sy'],t['sx']+t['width'],t['sy']+t['height']))
                image.alpha_composite(tile,(xx*32+t['dx'],yy*32+t['dy']))
    return image.convert('RGB')

# 24 real random-map crops: all four convex and all four concave orientations.
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',12)
cards=[]
labels={1:'바깥 · 좌상',2:'바깥 · 우상',4:'바깥 · 좌하',8:'바깥 · 우하',7:'안쪽 · 우하',11:'안쪽 · 좌하',13:'안쪽 · 우상',14:'안쪽 · 좌상'}
for pattern in [1,2,4,8,7,11,13,14]:
    cards.extend({**case,'label':labels[pattern]} for case in candidates[pattern])
cell_w,cell_h,cols=260,249,4
sheet=Image.new('RGB',(cols*cell_w,6*cell_h+58),'#12191e')
d=ImageDraw.Draw(sheet);d.text((14,12),'새 랜덤 지도 · ㄱ자 8방향 × 3개 실제 사례',font=font,fill='#dfe9e5')
for index,case in enumerate(cards):
    x=index%cols*cell_w;y=58+index//cols*cell_h
    d.rectangle((x+4,y+3,x+cell_w-5,y+cell_h-4),fill='#202d32')
    d.text((x+10,y+7),case['label'],font=font,fill='#d2e3db')
    d.text((x+10,y+29),f"{case['seed']} · {case['x']},{case['y']}",font=small,fill='#aebdbf')
    img=draw_region(all_maps[case['seed']],case['x'],case['y'])
    sheet.paste(img,(x+34,y+49))
sheet.save(preview/'corner-gallery.png')
pattern_pages=[]
ordered=sorted(representatives)
for page_index,start in enumerate(range(0,len(ordered),64)):
    selected=ordered[start:start+64]
    board=Image.new('RGB',(1408,58+194*((len(selected)+7)//8)),'#12191e')
    bd=ImageDraw.Draw(board)
    bd.text((12,12),f'실제 이웃 배치 {start+1}~{start+len(selected)} / {len(ordered)} · 중앙 벽 확인',font=font,fill='#dfe9e5')
    for index,mask in enumerate(selected):
        case=representatives[mask];x=index%8*176;y=58+index//8*194
        bd.text((x+5,y+4),f"mask {mask:03d} · {case['x']},{case['y']}",font=small,fill='#b8cccb')
        img=draw_region(all_maps[case['seed']],case['x'],case['y'],5,5)
        board.paste(img,(x+7,y+25))
    filename=f'pattern-page{page_index+1:02d}.png';board.save(preview/filename);pattern_pages.append(filename)
(run/'visual-cases.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(geometry_hashes)==generation['nativeFloors'], 'Duplicate floor geometry'
summary={**generation,'status':'passed','wallArtRevision':plan['artRevision'],'uniqueMapGeometries':len(geometry_hashes),'wallCellsChecked':wall_cells,'cornersChecked':sum(corner_counts.values()),
    'orientationsCovered':8,'cornerCounts':{str(k):corner_counts[k] for k in sorted(corner_counts)},
    'observedNeighbourMasks':len(masks),'observedTextureCases':len(patterns),
    'atlasSpritesChecked':2048,'exhaustiveNeighbourMasks':256,'topologyAssertions':topology['assertions'],
    'topologyViolations':len(topology['violations']),'realMapVisualSamples':len(cards),
    'visualPatternRepresentatives':len(representatives),'patternPages':pattern_pages,
    'unobservedMasksTestedSynthetically':sorted(set(range(256))-set(masks)),
    'scope':'All generated wall cells/corners checked against the native atlas; exhaustive surface invariants and 24 visual samples. Not a claim about every possible future visual case.'}
(run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(preview/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest['auditSummary']=summary
(preview/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['status','nativeFloors','wallCellsChecked','cornersChecked','observedNeighbourMasks','atlasSpritesChecked','topologyAssertions','topologyViolations']}))
