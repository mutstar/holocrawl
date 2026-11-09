"""Normalize generated raster tiles and render a tile-composition art preview.
No dungeon generator, native terrain or combat runtime is changed.
"""
from pathlib import Path
from PIL import Image
import json,shutil,html
r=Path(__file__).resolve().parents[1]
rev='venue-street01';a=r/'assets/holocrawl'/rev;out=r/'analysis/previews'/rev
source=json.loads((r/'scripts/venue-street01-sources.json').read_text(encoding='utf-8'))
assert not a.exists() and not out.exists(),'Preserve previous draft outputs'
(a/'originals').mkdir(parents=True);out.mkdir(parents=True)
names={'asphalt':'アスファルト','sidewalk':'보도','wall':'공연장 외벽','fence':'대기열 펜스','ticket':'티켓 안내기'}
names['asphalt']='아스팔트'
tiles={}
for name,path in source.items():
    shutil.copy2(path,a/'originals'/f'{name}.png');im=Image.open(path).convert('RGBA')
    if name in ['fence','ticket']:
        assert im.getextrema()[3][0]==0
        im=im.crop(im.getbbox());im.thumbnail((28,22) if name=='fence' else (20,28),Image.Resampling.NEAREST)
        tile=Image.new('RGBA',(32,32));tile.alpha_composite(im,((32-im.width)//2,31-im.height))
    else:tile=im.resize((32,32),Image.Resampling.NEAREST)
    assert tile.size==(32,32);tile.save(a/f'{name}32.png');tile.save(out/f'{name}32.png');tiles[name]=tile
src=r/'engine/campaign-crawl/crawl-ref/source/rltiles'
actor=Image.new('RGBA',(32,32))
actor_parts=['player/base/human_m.png','player/boots/long_red.png','player/body/chainmail.png','player/head/fhelm_gray3.png','player/hand1/broadsword.png']
for rel in actor_parts:actor.alpha_composite(Image.open(src/rel).convert('RGBA'))
rat=Image.open(src/'mon/animals/rat.png').convert('RGBA')
stairs=Image.open(src/'dngn/gateways/stone_stairs_down.png').convert('RGBA')
rows=[
'################',
'###....###.....#',
'###....###.....#',
'#..............#',
'#..####........#',
'#..####........#',
'#..............#',
'#.......####...#',
'#.......####...#',
'#..............#',
'#..............#',
'################']
assert len(rows)==12 and all(len(row)==16 for row in rows)
scene=Image.new('RGBA',(512,384),(14,18,25,255))
for y,row in enumerate(rows):
    for x,c in enumerate(row):
        near=any(0<=x+dx<16 and 0<=y+dy<12 and rows[y+dy][x+dx]=='#' for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
        tile=tiles['wall' if c=='#' else 'sidewalk' if near else 'asphalt']
        scene.alpha_composite(tile,(32*x,32*y))
for x,y in [(10,4),(11,4),(12,4),(3,8),(4,8)]:scene.alpha_composite(tiles['fence'],(32*x,32*y))
for x,y in [(5,2),(13,1)]:scene.alpha_composite(tiles['ticket'],(32*x,32*y))
scene.alpha_composite(stairs,(14*32,9*32))
scene.convert('RGB').save(out/'terrain-native.png')
scene.resize((1024,768),Image.Resampling.NEAREST).convert('RGB').save(out/'terrain.png')
scene.alpha_composite(actor,(5*32,7*32));scene.alpha_composite(rat,(10*32,6*32))
scene.convert('RGB').save(out/'scene-native.png');scene.resize((1024,768),Image.Resampling.NEAREST).convert('RGB').save(out/'scene.png')
data=dict(status='tile-art-draft',date='2026-11-03',region='잔향도시1~3층 공연장 앞 거리',tileSize=[32,32],assets=list(tiles),review=f'analysis/previews/{rev}/index.html',newRasterTool='built-in image_gen',composition='Generated raster tiles assembled in a fixed16x12 tile test map; existing DCSS doll,rat and stairs are scale references.',engineIntegrated=False,proceduralGeneratorImplemented=False,collisionImplemented=False,runtimeChanged=False,notes='Only floor/wall/prop art readability prototype. Prop collisions,door/curb/corner connections,terrain variants and native generation integration remain pending.')
(a/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cards=''.join(f'<figure><img src="{key}32.png"><figcaption>{label}<br>32×32</figcaption></figure>' for key,label in names.items())
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>잔향도시 · 공연장 앞 거리 도트 초안</title><style>body{background:#10151c;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:1100px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#b9e7ff}section{background:#1a2532;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}.tiles{display:flex;flex-wrap:wrap;gap:18px}figure{margin:0;text-align:center;background:#10151c;padding:15px}.tiles img{width:96px;height:96px}button{background:#243b52;color:white;border:1px solid #7099b7;padding:10px 18px;cursor:pointer}p{max-width:1000px}</style><h1>잔향도시1~3층 · 공연장 앞 거리</h1><p>32×32 바닥·벽·소품 도트를 조합한 첫 시안입니다. 기존 돌죽 캐릭터·쥐·계단은 크기 비교용입니다. 일반 실행본이나 절차 생성 던전에 아직 적용하지 않았습니다.</p><section><h2>거리 조합 미리보기</h2><button onclick="document.getElementById('scene').src='scene.png'">캐릭터와 함께</button> <button onclick="document.getElementById('scene').src='terrain.png'">배경만</button><p><img id="scene" src="scene.png" alt="공연장 앞 거리 타일 조합"></p><p>어두운 아스팔트 → 조금 밝은 보도 → 두꺼운 건물 벽. 펜스와 안내기는 공연장 입구 분위기를 담당합니다. 단일 타일의 반복감과 색조를 보는 고정 배치 검사장입니다.</p></section><section><h2>새 도트5종</h2><div class="tiles">'''+cards+'''</div><p>기본 이미지 생성 도구로 만든 원본을 보존하고, 최근접 방식으로32픽셀에 맞췄습니다. 벽 연결부·보도 가장자리·문·다양한 바닥 변형은 다음 작업입니다.</p></section><section><h2>확인할 점</h2><p>길과 벽이 구분되는지, 캐릭터보다 배경이 튀지 않는지, 펜스·안내기가32픽셀에서 알아보이는지 확인하는 단계입니다. 이동·충돌·시야는 구현되지 않은 미술 시안입니다.</p></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\venue-street01\\index.html"\r\n',encoding='ascii')
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
    p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(activeWork='venue-street32px-art-draft-review',currentMapArt=data,currentVisualReview=data['review'],lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=data['review']
    d['next']='Review first venue street32px terrain kit and composition. New world route is in analysis/design/dungeon-route01.json. Native runtime remains ayame-zanshin02; new dungeon generation and terrain not implemented. Choco full-kit work paused by user dungeon redesign focus.'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 잔향도시 도트 초안 / 2026-11-03\n\nanalysis/previews/venue-street01/index.html.1~3층공연장앞거리32px 아스팔트·보도·외벽·펜스·티켓안내기5종, 고정배치조합. 기존캐릭터/쥐/계단은크기참고. 실제엔진/절차생성/충돌미구현, 일반runtime=ayame-zanshin02 유지. 새세계관·루트승인내용: analysis/design/dungeon-route01.json (JP잔향도시14+커튼콜7,기본30층3룬~최대60층15룬,ID→EN난이도/순차개방). 현재신추가패시브보다새던전/도트설계진행중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
