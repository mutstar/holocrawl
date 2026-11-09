"""Suisei-only review images from native captures, with no VFX compositing."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import hashlib,json,os

root=Path(__file__).resolve().parents[1]
run=root/'analysis/native/suisei-vfx04';raw=run/'native/shots'
review=json.loads((run/'native/suisei-review.json').read_text())
assert review['status']=='passed' and review['afterImpactHp']<review['beforeImpactHp']
assert json.loads((run/'capture-validation.json').read_text())['status']=='passed'
out=root/'analysis/previews/suisei-vfx04';out.mkdir(parents=True,exist_ok=True)
def group(tier):
    a=list(raw.glob(f'suisei-tier{tier}-*-frame0.png'));assert len(a)==1
    stem=a[0].name[:-11]
    return [raw/(stem+'-'+s+'.png') for s in ['frame0','frame1','state']]
one,three,five=group(1),group(3),group(5)
impact=[raw/f'comet-impact-frame{f}.png' for f in range(6)]
for paths in [one,three,five,impact]:
    ims=[Image.open(p).convert('RGB') for p in paths]
    assert ims[0].tobytes()!=ims[1].tobytes()
meta=json.loads(Path(str(three[0])+'.json').read_text());assert meta['effectCells']>=5
cut_diff=ImageChops.difference(Image.open(three[0]).convert('RGB'),Image.open(three[2]).convert('RGB')).getbbox()
assert cut_diff and cut_diff[2]-cut_diff[0]>=120,cut_diff
def publish(name,paths,box,scale=3,durations=None):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box)
        im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations or 550,loop=0)
    return frames
publish('tier1-ingame',one[:2],(323,292,451,388))
publish('tier3-ingame',three[:2],(323,292,579,388))
publish('tier5-call',[raw/'comet-warning.png',raw/'comet-urgent.png'],(355,132,547,420))
publish('tier5-impact',impact,(355,132,547,420),durations=[130,130,130,130,220,280])
publish('tier5-sequence',[raw/'comet-warning.png',raw/'comet-urgent.png',*impact,raw/'comet-aftermath.png'],(355,132,547,420),durations=[900,700,130,130,130,130,220,280,900])
publish('tier5-motion',impact,(355,132,547,420),durations=[65,65,65,65,100,100])
# Approved tier1/3 native frames must match their previous captures exactly.
previous=root/'analysis/native/suisei-vfx03/native/shots'
# Cross-run terrain flavour differs; compare the effect-only change masks,
# not whole framebuffer bytes. Asset hashes are also checked independently.
for paths in [one,three]:
    for p in paths[:2]:
        current=ImageChops.difference(Image.open(p).convert('RGB'),Image.open(paths[2]).convert('RGB')).convert('L').point(lambda v:255 if v else 0)
        prior=ImageChops.difference(Image.open(previous/p.name).convert('RGB'),Image.open(previous/paths[2].name).convert('RGB')).convert('L').point(lambda v:255 if v else 0)
        assert current.tobytes()==prior.tobytes(),p
import hashlib
accepted=json.loads((run/'accepted-tier1-tier3.json').read_text())
for name,digest in accepted.items():
    assert hashlib.sha256((root/'engine/campaign-crawl/crawl-ref/source/rltiles/holo'/name).read_bytes()).hexdigest()==digest
assert len({p.read_bytes() for p in impact})==6
old=json.loads((root/'analysis/native/suisei-vfx03/native/suisei-review.json').read_text())
assert review['beforeImpactHp']==old['beforeImpactHp'] and review['afterImpactHp']==old['afterImpactHp']

tiles=root/'engine/campaign-crawl/crawl-ref/source/rltiles/holo'
preview=[]
for f in (0,1):
    canvas=Image.new('RGBA',(256,256),'#182638');canvas.alpha_composite(Image.open(tiles/f'fx_starmark_{f}.png').resize((256,256),Image.Resampling.NEAREST));preview.append(canvas.convert('RGB'))
preview[0].save(out/'tier1-tile.gif',save_all=True,append_images=preview[1:],duration=550,loop=0)
rel=lambda p:os.path.relpath(p,out).replace('\\','/')
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스이세이 성급별 도트 점검</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;margin:24px;max-width:1100px}p,li{line-height:1.8}section,details{background:#1d2b3d;padding:22px;border:1px solid #48617b;border-radius:12px;margin:20px 0}h2{color:#ffdfa2}img{max-width:100%;image-rendering:pixelated}a{color:#bba9ff}.row{display:flex;gap:22px;align-items:center;flex-wrap:wrap}summary{cursor:pointer;font-weight:bold;color:#ffdfa2}</style><h1>스이세이 5성 · 경고 → 낙하 → 착탄</h1><p>아래 인게임 장면은 실제 SDL 렌더러의 테스트 전투장 캡처입니다. 고정 장비·높은 HP/MP/신앙을 사용했습니다. 확대와 느린 프레임 반복만 적용했으며 효과를 덧그리지 않았습니다. 두 프레임 반복은 게임의 원래 속도와 다릅니다.</p><section><h2>먼저 1성 · 별자리 표식</h2><p><b>효과:</b> 별을 쌓을 대상을 지정합니다. 지정 자체가 공격은 아닙니다. 이후 공격으로 별을 축적합니다.<br><b>표시:</b> 가느다란 청록·금색 모서리 표식과 작은 별점이 선택한 적에게 남습니다. 대상이 움직이면 함께 이동하고, 다른 적을 지정하거나 대상이 사라지면 바뀝니다.</p><div class="row"><div><p>원본 32×32 도트 확대</p><img src="tier1-tile.gif"></div><div><p>실제 인게임 · 왼쪽 플레이어 / 오른쪽 지정한 적</p><img src="tier1-ingame.gif"></div></div><p><b>점검할 것:</b> 적의 모습과 HP 바가 읽히는지, 별 표식이 눈에 띄는지, 색과 크기가 적절한지.</p><a href="'''+rel(one[0])+'''" target="_blank">1성 원본 전체 화면</a><p>이전 버전과 비교:</p><img src="../suisei-vfx01/tier1-ingame.gif"><p>위 이전 화면보다 표식의 채워진 픽셀이 약 65% 줄었습니다.</p></section><details><summary>확정한 3성 · 궤도 절단</summary><p>MP3·신앙3. 실제 관통 판정 방향의 최대 5칸을 가로지르는 하나의 곡선형 베기 궤적을 표시합니다. 흰 날이 지나간 뒤 갈라진 별빛 잔상이 남습니다. 별을 모은 표적에 적중하면 별을 소모해 추가 피해를 줍니다. 피해·비용은 바꾸지 않았습니다.</p><p>새 베기 궤적:</p><img src="tier3-ingame.gif"><p>이전 직선형 효과:</p><img src="../suisei-vfx01/tier3-ingame.gif"><p><a href="'''+rel(three[0])+'''" target="_blank">3성 원본 전체 화면</a></p></details><details open><summary>수정한 5성 · 혜성 낙하</summary><p>MP6·신앙10. 지정 후 노랑→빨강 경고가 나오고, 실제 지연 시간이 끝날 때 혜성이 착탄합니다. 피해는 착탄 시점에 적용됩니다. 자신도 3×3에 들어가면 휘말릴 수 있습니다.</p><p>노란 3×3 경고 → 빨간 임박 경고 → 위에서 내려오는 혜성 4단계 → 큰 착탄 2단계 → 피해 적용 후입니다. 비교를 위해 시간을 늘렸습니다. 낙하 애니메이션은 착탄 처리 시점의 연출이며 추가 게임 턴은 흐르지 않습니다.</p><img src="tier5-sequence.gif"><p>게임에 설정한 낙하·착탄 프레임 시간(초기/반복 대기 제외):</p><img src="tier5-motion.gif"><p><a href="'''+rel(impact[5])+'''" target="_blank">5성 착탄 원본 전체 화면</a></p></details></html>'''
(out/'index.html').write_text(doc,encoding='utf-8')
result=dict(status='passed',review=review,cutVisibleWidth=cut_diff[2]-cut_diff[0],
    rawFiles=[dict(path=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper()) for p in [*one,*three,*five,raw/'comet-warning.png',raw/'comet-urgent.png',*impact,raw/'comet-aftermath.png']],
    firstReview='User accepted tier1/3; review visible warning, descent and impact for tier5',gallery=out.relative_to(root).as_posix()+'/index.html')
(run/'gallery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='rawFiles'},ensure_ascii=False,indent=2))
