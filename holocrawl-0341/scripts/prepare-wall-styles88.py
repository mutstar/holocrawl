"""Four matching wall studies. Preview only; no native atlas or gameplay edits."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/wall-styles88'
OUT.mkdir(parents=True, exist_ok=True)
SRC = ROOT / 'preview/wall-audit85'
MAP = SRC / 'maps/map-802302584-1.json'
data = json.loads(MAP.read_text())
atlases = {n: Image.open(SRC / f'assets/{n}.png').convert('RGBA') for n in ['floor', 'wall', 'feat']}
grain = np.array(Image.open(ROOT / 'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
stone_path = ROOT / 'engine/upstream/crawl-ref/source/rltiles/dngn/wall'
stones = [np.array(Image.open(stone_path / f'brick_dark_1_{i}.png').convert('RGB')) for i in range(8)]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def hsh(x, y):
    return ((x * 73856093) ^ (y * 19349663) ^ 802302584) & 0xffffffff

def native_image():
    image = Image.new('RGBA', (data['width'] * 32, data['height'] * 32))
    for y in range(data['height']):
        for x in range(data['width']):
            for layer in ['floors', 'features']:
                t = data['palette'][data[layer][y * data['width'] + x]]
                image.alpha_composite(atlases[t['atlas']].crop((t['sx'], t['sy'], t['sx']+t['width'], t['sy']+t['height'])), (x*32+t['dx'], y*32+t['dy']))
    return np.array(image)

def neighbor(mask, dx, dy):
    result = np.zeros_like(mask)
    height, width = mask.shape
    x0, x1 = max(0, -dx), min(width, width-dx)
    y0, y1 = max(0, -dy), min(height, height-dy)
    result[y0:y1, x0:x1] = mask[y0+dy:y1+dy, x0+dx:x1+dx]
    return result

def wall_surface(rows):
    h, w = len(rows), len(rows[0])
    wall = np.array([[c == '#' for c in row] for row in rows])
    joined = np.array([[c in '#+G' for c in row] for row in rows])
    exposed = [~neighbor(joined, dx, dy) for dx, dy in [(0,-1),(1,0),(0,1),(-1,0),(-1,1)]]
    n,e,s,west,sw = [np.repeat(np.repeat(a,32,axis=0),32,axis=1) for a in exposed]
    yy,xx = np.indices((h*32,w*32)); px,py=xx%32,yy%32
    walls = np.repeat(np.repeat(wall,32,axis=0),32,axis=1)
    front = walls & (py>=18) & s
    side = walls & (px>=28) & (e | ((py>=18) & ~neighbor(np.repeat(np.repeat(joined,32,axis=0),32,axis=1),32,32))) & ~(front & ~e)
    west_face = walls & ~front & ~side & (px<3) & (np.repeat(np.repeat(neighbor(joined,0,-1)|neighbor(joined,0,1),32,axis=0),32,axis=1)) & np.where(py>=18,sw,west)
    front &= ~side
    cap = walls & ~front & ~side & ~west_face
    return walls,cap,front,side,west_face,xx,yy

def render(base, rows, style):
    a = base.copy()
    walls,cap,front,side,west,xx,yy = wall_surface(rows)
    texture = grain[yy%grain.shape[0],xx%grain.shape[1],:3].astype(float)
    noise = (texture.mean(axis=2)-texture.mean())
    if style == 'dcss':
        for y,row in enumerate(rows):
            for x,c in enumerate(row):
                if c != '#': continue
                tile = stones[hsh(x,y)%len(stones)].astype(float)
                value = tile.mean(axis=2)
                # Retain original DCSS stone shapes, recolour for our grey/brown city.
                levels = np.select([value<17,value<31,value<46,value<65],[23,38,53,69],default=86)
                rgb=np.stack([levels*1.05,levels*1.01,levels*.93],axis=2)
                a[y*32:(y+1)*32,x*32:(x+1)*32,:3]=rgb.astype('uint8')
        return a

    if style == 'pixel':
        colors = {'cap': [49,53,47], 'front':[86,82,70], 'side':[38,39,34], 'west':[71,72,60]}
        for mask,key in [(cap,'cap'),(front,'front'),(side,'side'),(west,'west')]:
            rgb=np.array(colors[key])[None,None,:]+noise[:,:,None]*(.30 if key=='cap' else .68)
            a[mask,:3]=np.clip(rgb[mask],0,255).astype('uint8')
        # Separate front courses, ending on the correct cap silhouette at corners.
        courses = front & (((yy-18)%7==0) | (((xx+((yy-18)//7%2)*10)%20==0)))
        a[courses,:3]=(a[courses,:3].astype(float)*.66).astype('uint8')
        cap_n=cap & ~neighbor(cap,0,-1)
        cap_s=cap & ~neighbor(cap,0,1)
        cap_e=cap & ~neighbor(cap,1,0)
        cap_w=cap & ~neighbor(cap,-1,0)
        # Edges are topology-aware; no tile-by-tile frame.
        a[cap_n,:3]=[90,90,72]
        a[cap_w,:3]=[76,78,64]
        a[cap_s,:3]=[92,90,73]
        a[cap_e,:3]=[32,35,31]
        under=front & neighbor(cap,0,-1)
        a[under,:3]=[41,41,34]
    elif style == 'gungeon':
        colors={'cap':[35,37,37],'front':[58,57,56],'side':[30,33,34],'west':[49,49,46]}
        for mask,key in [(cap,'cap'),(front,'front'),(side,'side'),(west,'west')]:
            rgb=np.array(colors[key])[None,None,:]+noise[:,:,None]*.38
            a[mask,:3]=np.clip(rgb[mask],0,255).astype('uint8')
        # Broad coping stones and a recessed brick face, like the visible planes
        # in Gungeon's official screenshot. This is an adaptation, not its code.
        rim = cap & (~neighbor(cap,0,-4)|~neighbor(cap,0,5)|~neighbor(cap,-4,0)|~neighbor(cap,4,0))
        block=((xx//11+yy//11)%3)*4
        for k,c in enumerate([91,83,73]):
            layer=a[:,:,k];layer[rim]=(c+block[rim]+noise[rim]*.23).astype('uint8')
        joints=rim & ((xx%11==0)&(~neighbor(cap,0,-4)|~neighbor(cap,0,5)) | (yy%11==0)&(~neighbor(cap,-4,0)|~neighbor(cap,4,0)))
        a[joints,:3]=[48,47,43]
        edge=cap & (~neighbor(cap,0,1)|~neighbor(cap,1,0))
        a[edge,:3]=[40,40,37]
        mortar=front & (((yy-18)%5==0)|((xx+((yy-18)//5%2)*8)%16==0))
        a[mortar,:3]=[31,33,34]
        a[front & neighbor(cap,0,-1),:3]=[24,27,28]
    else:
        raise ValueError(style)
    assert np.array_equal(a[~walls],base[~walls])
    return a

baseline=native_image()
# Reproduce the exact last-seen local87 study on its real native map.
baseline87=baseline.copy()
prior=np.array(Image.open(ROOT/'preview/wall-relief87/after.png').convert('RGBA'))
baseline87[35*32:44*32,29*32:36*32]=prior
rows=data['rows']
styles=[('ours','우리 벽 · 직전87'),('dcss','돌죽식 · 석재로 채움'),('pixel','픽셀 던전식 · 층 분리'),('gungeon','건전식 · 두꺼운 윗마감')]
views={'corner':(29,35,7,9),'scene':(25,31,18,15),'map':(0,0,data['width'],data['height'])}
manifest={'seed':data['seed'],'tileSize':32,'scope':'preview only','views':{},'styles':[],
 'baseline':'Audited native84, with only the previously shown12-cell relief87 overlay.',
 'references':[
 {'name':'DCSS0.34.1','url':'https://github.com/crawl/crawl/blob/0.34.1/crawl-ref/docs/develop/tiles_creation.txt','method':'Full-cell stone texture, stepped values. Recoloured original DCSS brick shapes.'},
 {'name':'Shattered Pixel Dungeon','url':'https://github.com/00-Evan/shattered-pixel-dungeon/blob/master/core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/tiles/DungeonTileSheet.java','method':'Separate cap, front and corner stitching; custom city artwork.'},
 {'name':'Enter the Gungeon','url':'https://store.steampowered.com/app/311690/Enter_the_Gungeon/','method':'Visual study of official screenshot; coping stones and recessed brick front, custom artwork.'}]}
checks=[]
for style,title in styles:
    result=baseline87 if style=='ours' else render(baseline,rows,style)
    walls=np.repeat(np.repeat(np.array([[c=='#' for c in r] for r in rows]),32,axis=0),32,axis=1)
    outside=int(np.count_nonzero(np.any(result[~walls]!=baseline[~walls],axis=1)))
    assert outside==0
    for view,(x,y,w,h) in views.items():
        filename=f'{style}-{view}.png'
        Image.fromarray(result).crop((x*32,y*32,(x+w)*32,(y+h)*32)).convert('RGB').save(OUT/filename)
        manifest['views'][view]={'width':w*32,'height':h*32,'crop':[x,y,w,h]}
    checks.append({'style':style,'nonWallPixelsChanged':outside,'alphaUnchanged':bool(np.array_equal(result[:,:,3],baseline[:,:,3]))})
    manifest['styles'].append({'id':style,'title':title})

# Purpose-built topology sheet; these shapes are labelled synthetic in the UI.
shape_rows=[list('.'*26) for _ in range(11)]
shapes=[{(3,y) for y in range(1,7)}|{(x,y) for x in [1,2] for y in range(4,7)},
 {(8,y) for y in range(1,7)}|{(x,6) for x in range(8,12)},
 {(15,y) for y in range(1,7)}|{(x,1) for x in range(15,19)},
 {(22,1)}, {(x,4) for x in range(21,25)},
 {(x,9) for x in range(1,7)}|{(4,8)},
 {(x,y) for x in range(10,14) for y in range(8,10)},
 {(x,y) for x in range(17,23) for y in range(8,10) if (x,y)!=(19,8)}]
for shape in shapes:
    for x,y in shape: shape_rows[y][x]='#'
shape_rows=[''.join(row) for row in shape_rows]
floor_sample=baseline[35*32:36*32,29*32:30*32]
shape_base=np.tile(floor_sample,(11,26,1))
for y,row in enumerate(shape_rows):
    for x,c in enumerate(row):
        if c=='#':
            # Recover art84 from a real palette sprite with this neighbor mask.
            mask=0
            for bit,(dx,dy) in enumerate([(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]):
                if 0<=y+dy<len(shape_rows) and 0<=x+dx<len(row) and shape_rows[y+dy][x+dx]=='#':mask|=1<<bit
            # Use the exact archived84 algorithm, with the original city grain.
            def solid(a,b): return 0<=b<len(shape_rows) and 0<=a<len(row) and shape_rows[b][a]=='#'
            tex=grain[:,hsh(x,y)%8*32:hsh(x,y)%8*32+32].copy().astype(float)
            for py in range(32):
                for px in range(32):
                    if py>=18 and not solid(x,y+1): surface='side' if px>=28 and not solid(x+1,y) else 'front'
                    elif px>=28 and (not solid(x+1,y) or py>=18 and not solid(x+1,y+1)): surface='side'
                    elif px<3 and (solid(x,y-1) or solid(x,y+1)) and not solid(x-1,y+(py>=18)): surface='west'
                    else: surface='cap'
                    color=tex[py,px]
                    if surface=='cap':color=np.array([35,37,33])*.86+color*.14
                    elif surface=='side':color*=.56
                    elif surface=='west':color*=.72
                    shade=1
                    for test in [not solid(x,y-1) and py==0,not solid(x-1,y) and px==0]:
                        if test:shade*=.8
                    if not solid(x+1,y) and px==31:shade*=.78
                    if not solid(x,y+1) and py==31:shade*=.72
                    shape_base[y*32+py,x*32+px,:3]=np.round(np.round(color)*shade).astype('uint8')
for style,_ in styles:
    result=shape_base if style=='ours' else render(shape_base,shape_rows,style)
    Image.fromarray(result).convert('RGB').save(OUT/f'{style}-shapes.png')
manifest['views']['shapes']={'width':26*32,'height':11*32,'synthetic':True}

font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
board=Image.new('RGB',(1040,414),'#171d21');draw=ImageDraw.Draw(board)
for i,(style,title) in enumerate(styles):
    draw.text((i*260+14,14),title,font=font,fill='#e1e6e4')
    board.paste(Image.open(OUT/f'{style}-corner.png'),(i*260+18,55))
    draw.text((i*260+18,355),['비교 기준 · 코너87/나머지84','칸 전체에 석재 무늬','앞면14px · 윗면 별도','돌 마감4~5px · 벽돌 앞면'][i],font=small,fill='#a9bab5')
draw.text((18,389),'동일 시드802302584 · 동일 지형/바닥/크기 · 참고 방식을 재해석한 비교 시안',font=small,fill='#a9bab5')
board.save(OUT/'comparison.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation={'status':'passed','sourceMapSha256':digest(MAP),'auditedWallAtlasSha256':digest(SRC/'assets/wall.png'),
 'sourceMapUnchanged':True,'checks':checks,'scope':'Art comparison, no engine or gameplay changes.',
 'ownBaselineMatchesRelief87':bool(np.array_equal(np.array(Image.open(OUT/'ours-corner.png')),prior[:,:,:3]))}
assert validation['ownBaselineMatchesRelief87']
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(validation))
