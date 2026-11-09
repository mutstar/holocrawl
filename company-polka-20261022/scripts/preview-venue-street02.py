"""Original DCSS terrain is the style baseline; one edited wall detail.
Fixed layout composition for art review only, not an engine screenshot.
"""
from pathlib import Path
from PIL import Image
import random,json,shutil,hashlib,sys
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source/rltiles'
rev='venue-street02';a=r/'assets/holocrawl'/rev;out=r/'analysis/previews'/rev
assert not a.exists() and not out.exists()
(a/'originals').mkdir(parents=True);out.mkdir(parents=True)
shutil.copy2(sys.argv[1],a/'originals/wall-poster-generated.png')
poster=Image.open(sys.argv[1]).convert('RGBA').resize((32,32),Image.Resampling.NEAREST);poster.save(a/'wall-poster32.png');poster.save(out/'wall-poster32.png')
floors=[Image.open(src/f'dngn/floor/grey_dirt{i}.png').convert('RGBA') for i in range(8)]
walls=[Image.open(src/f'dngn/wall/brick_dark_1_{i}.png').convert('RGBA') for i in range(12)]
for n,im in enumerate(floors):im.save(a/f'reused-floor{n}.png')
for n,im in enumerate(walls):im.save(a/f'reused-wall{n}.png')
w,h=20,14;grid=[['#']*w for _ in range(h)]
def room(x0,y0,x1,y1):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):grid[y][x]='.'
room(2,2,6,5);room(10,2,16,5);room(3,8,8,11);room(12,8,17,11)
room(6,4,10,4);room(4,5,4,8);room(14,5,14,8);room(8,10,12,10)
rng=random.Random(20261103)
base=Image.new('RGBA',(w*32,h*32))
for y in range(h):
    for x in range(w):
        tile=rng.choices(walls,weights=[100]*4+[10]*4+[5]*4)[0] if grid[y][x]=='#' else rng.choices(floors,weights=[6]*6+[3,1])[0]
        base.alpha_composite(tile,(x*32,y*32))
stairs=Image.open(src/'dngn/gateways/stone_stairs_down.png').convert('RGBA');base.alpha_composite(stairs,(16*32,10*32))
door=Image.open(src/'dngn/doors/closed_door.png').convert('RGBA')
for x,y in [(8,4),(4,7),(14,7),(10,10)]:base.alpha_composite(door,(x*32,y*32))
actor=Image.new('RGBA',(32,32))
for rel in ['player/base/human_m.png','player/boots/long_red.png','player/body/chainmail.png','player/head/fhelm_gray3.png','player/hand1/broadsword.png']:actor.alpha_composite(Image.open(src/rel).convert('RGBA'))
base.alpha_composite(actor,(5*32,4*32))
base.alpha_composite(Image.open(src/'mon/animals/rat.png').convert('RGBA'),(12*32,4*32))
venue=base.copy()
for x,y in [(6,1),(16,7)]:
    assert grid[y][x]=='#';venue.paste(poster,(x*32,y*32))
for name,im in [('original-baseline',base),('scene',venue)]:
    im.convert('RGB').save(out/f'{name}-native.png');im.resize((1280,896),Image.Resampling.NEAREST).convert('RGB').save(out/f'{name}.png')
# Detail at native tile scale, enlarged2x without smoothing.
venue.crop((32,32,320,224)).resize((864,576),Image.Resampling.NEAREST).convert('RGB').save(out/'detail.png')
data=dict(status='revised-art-direction-draft',date='2026-11-03',review=f'analysis/previews/{rev}/index.html',tileSize=[32,32],feedback='Previous modern flat terrain rejected:too unlike DCSS,disconnected block walls,patchwork feel.',direction='Keep original DCSS floor/wall texture,palette and variants. Sparse edited concert-poster wall detail. Room/corridor test composition.',newAsset='wall-poster32.png',engineIntegrated=False,runtimeChanged=False,generatedLayout=False,originalTerrainReused=True,referenceAssets=['grey_dirt0..7','brick_dark_1_0..11'],notes='Art style comparison only. Street theme and final new terrain remain unapproved; these are original dungeon textures, not completed city assets.')
for p in [a/'manifest.json',out/'manifest.json']:p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>잔향도시 도트 방향 수정 · 돌죽 원본 기준</title><style>body{background:#10130f;color:#eef1e9;font:17px "Malgun Gothic",sans-serif;max-width:1280px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#d3dfb9}section{background:#1b2118;padding:18px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}button{background:#35432b;color:white;border:1px solid #8b9e78;padding:10px 18px;cursor:pointer}</style><h1>도트 방향 수정 · 돌죽 원본의 질감과 색조를 기준으로</h1><p>이전 시안의 밝은 보도·매끈한 블록 벽을 제외했습니다. 원본 돌죽 바닥8종·벽12종의 변형을 그대로 사용하고, 작은 공연 포스터가 붙은 벽 도트 하나만 새로 만들었습니다. 도시 테마를 완성한 버전이 아닌 미술 방향 확인용입니다.</p><section><h2>같은 배치에서 비교</h2><button onclick="document.getElementById('scene').src='scene.png'">작은 공연 포스터 추가</button> <button onclick="document.getElementById('scene').src='original-baseline.png'">돌죽 원본 배경</button><p><img id="scene" src="scene.png"></p><p>20×14칸의 고정 방·복도 배치에 타일을 조합한 시안입니다. 실제 엔진 캡처·절차 생성·이동/충돌 구현은 아닙니다. 기존 캐릭터·쥐·계단은 크기 비교용입니다.</p></section><section><h2>근접 보기</h2><img src="detail.png"><p>모든 타일은32×32이며 확대에는 부드럽게 만드는 필터를 쓰지 않았습니다. 원본 벽·바닥의 밀도와 어두운 색조를 유지하고, 공연장 요소는 작게 섞는 방향입니다.</p></section><p>일반 실행본은 ayame-zanshin02 유지. 다음 단계는 이 질감 기준이 맞는지 확인한 뒤 공연장 요소와 새로운 배경 타일을 조금씩 확장하는 것입니다.</p></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:(r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\venue-street02\\index.html"\r\n',encoding='ascii')
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
    p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(activeWork='venue-street-dcss-style-revision-review',currentMapArt=data,currentVisualReview=data['review'],lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=data['review']
    d['next']='Review revised DCSS-native terrain baseline with sparse concert-poster detail.01 modern flat terrain rejected. This is a static composition,not native dungeon integration. Runtime remains ayame-zanshin02. New world route in analysis/design/dungeon-route01.json.'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 잔향도시 도트 방향 수정 / 2026-11-03\n\nanalysis/previews/venue-street02/index.html.01 시안은 돌죽과너무다름/짜깁기느낌으로사용자거절.02는원본돌죽바닥8·벽12변형그대로+작은공연포스터벽1개. 고정방/복도조합이며 실제엔진/절차생성아님. 새도시배경최종승인아직없음. runtime=ayame-zanshin02 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
