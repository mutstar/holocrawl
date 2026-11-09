"""Publish actual successful swap/fire and summon-arrival native frames."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1]
run=root/'analysis/native/fubuki-vfx05';raw=run/'native/shots'
review=json.loads((run/'native/fubuki-review.json').read_text())
assert review['status']=='passed' and review['swapExact'] and review['foxCount']==4
assert review['afterFireHp']<review['beforeFireHp']
assert all(json.loads((raw/f'fubuki-swap-frame{f}-scene.json').read_text())['hitTargets']==1 for f in range(4))
assert json.loads((run/'capture-validation.json').read_text())['status']=='passed'
swap=[raw/f'fubuki-swap-frame{f}.png' for f in range(4)]
gather=[raw/f'fubuki-gather-frame{f}.png' for f in range(6)]
meta=[json.loads((raw/f'fubuki-gather-frame{f}-scene.json').read_text()) for f in range(6)]
assert [m['revealed'] for m in meta]==[0,1,1,2,2,3]
assert all(m['newFoxes']==3 for m in meta)
assert len({p.read_bytes() for p in gather})==6
for rel,h in json.loads((root/'analysis/native/fubuki-vfx01/preserved-files.json').read_text()).items():
    assert hashlib.sha256((root/'engine/campaign-crawl/crawl-ref/source'/rel).read_bytes()).hexdigest()==h,rel
out=root/'analysis/previews/fubuki-vfx05';out.mkdir(exist_ok=True)
box=(227,196,579,484)
def publish(name,paths,durations):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box).resize((704,576),Image.Resampling.NEAREST)
        im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
before=raw/'fubuki-swap-before.png';after=raw/'fubuki-swap-after.png'
gb=raw/'fubuki-gather-before.png';ga=raw/'fubuki-gather-after.png'
publish('swap-fire',[before,*swap,after],[900,260,260,350,350,900])
publish('fox-arrival',[gb,*gather,ga],[900,*([260]*6),1100])
publish('swap-fire-speed',swap,[95]*4)
publish('fox-arrival-speed',gather,[95]*6)
html='''<!doctype html><meta charset="utf-8"><title>후부키 · 바꿔치기와 백여우 행렬</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic";margin:24px;max-width:1000px}p{line-height:1.8}img{image-rendering:pixelated;max-width:100%}section,details{margin:25px 0;padding:20px;background:#1d2b3d}</style><h1>후부키 · 바꿔치기와 백여우 행렬</h1><p>실제 SDL 테스트 전투장 캡처를 확대·느리게 반복했습니다. 효과를 덧그리지 않았습니다. 높은 자원·고정 장비의 장면이며 일반 던전 영상은 아닙니다. 전투 수치·비용·지속시간은 유지했습니다.</p><section><h2>3성 · 여우 바꿔치기</h2><p>사용 전 → 실제 위치 교환 → 양쪽 자리의 흰 연기 → 떠난 자리 주변 3×3 여우불 → 사용 후. 바닥 불꽃은 출발점을 기준으로 표시하고, 실제 HP 피해를 받은 적에게는 몸체 위 푸른 여우불을 따로 표시합니다. 지속 화상 상태를 추가하는 효과는 아닙니다. 연기는 캐릭터 아래에 그립니다.</p><img src="swap-fire.gif"></section><section><h2>5성 · 백여우 행렬</h2><p>기존 여우 하나는 남고, 새로 소환된 여우 셋의 자리에서 푸른 소환 불빛이 차례로 열립니다. 마지막에는 실제 여우 넷이 보입니다. 전투 상태에는 여우들이 즉시 생성되며, 순차 등장은 추가 턴을 소비하지 않는 화면 연출입니다.</p><img src="fox-arrival.gif"></section><details><summary>설정한 연출 프레임 시간 · 95ms</summary><img src="swap-fire-speed.gif"><img src="fox-arrival-speed.gif"></details>'''
(out/'index.html').write_text(html,encoding='utf-8')
files=[before,*swap,after,gb,*gather,ga]
result={'status':'passed','nativeReview':review,'revealSequence':[m['revealed'] for m in meta],'rawFiles':[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'gallery':'analysis/previews/fubuki-vfx05/index.html'}
(run/'gallery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='rawFiles'},ensure_ascii=False,indent=2))
