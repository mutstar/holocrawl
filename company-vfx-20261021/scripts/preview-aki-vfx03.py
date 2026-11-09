"""Native bolt traversal and bloom capture, no composited VFX."""
from pathlib import Path
from PIL import Image
import json, hashlib
root=Path(__file__).resolve().parents[1]
run=root/'analysis/native/aki-vfx03';raw=run/'native/shots'
review=json.loads((run/'native/aki-review.json').read_text())
assert review['status']=='passed'
assert json.loads((run/'capture-validation.json').read_text())['status']=='passed'
trace=[json.loads(line) for line in (raw/'rose-flight.jsonl').read_text().splitlines()]
assert len(trace)>=2
first=trace[0];shot=[]
for row in trace:
    if row['from']!=first['from'] or row['to']!=first['to']:break
    shot.append(row)
assert len({tuple(row['cell']) for row in shot})>=2
flight=[raw/f"rose-flight-{row['frame']}.png" for row in shot]
bloom=[raw/f'aki-bloom-frame{f}.png' for f in range(4)]
assert len({p.read_bytes() for p in bloom})==4
assert review['afterBloomHp']<review['beforeBloomHp']
out=root/'analysis/previews/aki-vfx03';out.mkdir(exist_ok=True)
box=(227,196,547,484)
def publish(name,paths,durations):
    frames=[]
    for i,p in enumerate(paths):
        region=(323,292,515,420) if name.startswith('rose-flight') else box
        scale=3 if name.startswith('rose-flight') else 2
        im=Image.open(p).convert('RGB').crop(region).resize(((region[2]-region[0])*scale,(region[3]-region[1])*scale),Image.Resampling.NEAREST)
        im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
publish('rose-flight',flight,[220]*len(flight))
publish('rose-flight-speed',flight,[30]*len(flight))
publish('full-bloom',bloom+[raw/'aki-bloom-aftermath.png'],[260,260,350,550,1100])
publish('full-bloom-speed',bloom,[95]*4)
for rel,digest in json.loads((root/'analysis/native/aki-vfx01/preserved-files.json').read_text()).items():
    assert hashlib.sha256((root/'engine/campaign-crawl/crawl-ref/source'/rel).read_bytes()).hexdigest()==digest
html='''<!doctype html><meta charset="utf-8"><title>아키로젠탈 · 발사와 만개</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic";margin:24px;max-width:1000px}p{line-height:1.8}img{image-rendering:pixelated;max-width:100%}section,details{margin:25px 0;padding:20px;background:#1d2b3d}</style><h1>아키로젠탈 · 가시 발사와 만개</h1><p>실제 SDL 테스트 전투장 캡처를 확대·느리게 반복했습니다. 효과를 덧그리지 않았습니다. 높은 자원·고정 장비의 장면이며 일반 던전 영상은 아닙니다. 1성·장미 소환 도트·전투 계수와 공격 주기는 유지했습니다.</p><section><h2>3성 장미 · 실제 가시 발사</h2><p>초록 가시와 붉은 꽃잎이 실제 네이티브 투사체의 통과 칸을 따라 이동합니다. 소환할 때가 아니라 장미가 공격할 때 표시됩니다. 한 장미의 한 발을 느리게 반복합니다. 명중·빗나감은 기존 판정 그대로입니다.</p><img src="rose-flight.gif"></section><section><h2>5성 · 붉은 정원의 만개</h2><p>가시 소모 폭발을 사용하는 행동에 맞춰, 붉은 장미가 3×3→5×5→7×7 크기로 피어오르고 꽃잎이 퍼집니다. 크기 변화는 연출이며 피해가 순차적으로 발생하거나 추가되는 것이 아닙니다. 마지막은 확장된 정원이 남은 화면입니다.</p><img src="full-bloom.gif"></section><details><summary>설정 프레임 시간 · 발사30ms / 만개95ms</summary><img src="rose-flight-speed.gif"><img src="full-bloom-speed.gif"></details>'''
(out/'index.html').write_text(html,encoding='utf-8')
files=[*flight,*bloom,raw/'aki-bloom-aftermath.png']
result={'status':'passed','nativeReview':review,'projectileCells':shot,'rawFiles':[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'gallery':'analysis/previews/aki-vfx03/index.html'}
(run/'gallery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='rawFiles'},ensure_ascii=False,indent=2))
