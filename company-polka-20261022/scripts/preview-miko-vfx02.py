"""Miko native SDL screenshots; no composited game effects."""
from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,os
root=Path(__file__).resolve().parents[1]
run=root/'analysis/native/miko-vfx02';raw=run/'native/shots'
review=json.loads((run/'native/miko-review.json').read_text())
assert review['status']=='passed'
assert json.loads((run/'capture-validation.json').read_text())['status']=='passed'
out=root/'analysis/previews/miko-vfx02';out.mkdir(exist_ok=True)
def group(tier,seq):
    stem=f'miko-tier{tier}-option0-{seq}'
    return [raw/(stem+'-'+n+'.png') for n in ['frame0','frame1','state']]
one,high,three,five=group(1,1),group(1,2),group(3,3),group(5,4)
domain=[raw/f'miko-domain-frame{f}.png' for f in range(4)]
for pair in [three,domain]:
    assert Image.open(pair[0]).tobytes()!=Image.open(pair[1]).tobytes()
assert len({Image.open(p).tobytes() for p in domain})==4
box=(227,196,515,484)
def publish(name,paths,durations=550):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box).resize((576,576),Image.Resampling.NEAREST)
        im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
publish('tier1',one[:2]);publish('tier1-high',high[:2]);publish('tier3',three[:2])
publish('tier5',domain+[five[2]],durations=[260,260,350,550,950])
publish('tier5-motion',domain,durations=[95]*4)
publish('tier5-expiry',[five[2],raw/'miko-fire-expired.png',raw/'miko-domain-expired.png'],durations=[1000]*3)
rel=lambda p:os.path.relpath(p,out).replace('\\','/')
sections=[(1,'벚꽃 신사','기존 효과 유지. 처음 해금할 때 3×3, 신앙75 이상에서는 5×5 성역.','tier1'),(3,'액막이 불꽃','성역의 실제 테두리 칸에 분홍·금색 액막이 불꽃이 올라옵니다. 불꽃 지속시간이 끝나면 사라집니다. 성역 내부는 타오르지 않습니다.','tier3'),(5,'신역 전개','중앙에서 분홍·금색 신사 결계가 3×3→5×5→7×7로 펼쳐집니다. 전개는 장식 연출이며 공격이 아닙니다. 신역이 유지되는 동안 모서리와 중앙은 금빛 표식으로 구분됩니다. 3성 불꽃이 남아 있으면 확장된 테두리로 함께 이동합니다.','tier5')]
parts=['<!doctype html><meta charset="utf-8"><title>미코 전용 3·5성 도트 점검</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic";margin:24px;max-width:1000px}p{line-height:1.8}img{image-rendering:pixelated;max-width:100%}section,details{margin:25px 0;padding:20px;background:#1d2b3d}a{color:#c9b4ff}</style><h1>미코 · 불꽃과 신역 전개</h1><p>실제 SDL 테스트 전투장 캡처를 확대·느리게 반복했습니다. 효과를 덧그리지 않았습니다. 고정 장비와 높은 자원을 사용하며 일반 던전 플레이 영상은 아닙니다. 전투 수치·범위·비용은 유지했습니다.</p>']
for tier,name,desc,gif in sections:
    parts.append(f'<section><h2>{tier}성 · {name}</h2><p>{desc}</p><img src="{gif}.gif"></section>')
parts.append('<details><summary>1성 고신앙 5×5</summary><img src="tier1-high.gif"></details><details><summary>5성 설정 프레임 시간</summary><img src="tier5-motion.gif"></details><details><summary>지속시간에 따른 차이: 불꽃+신역 → 불꽃 종료 → 신역 종료</summary><img src="tier5-expiry.gif"></details>')
(out/'index.html').write_text(''.join(parts),encoding='utf-8')
files=[*one,*high,*three,*five,*domain,raw/'miko-fire-expired.png',raw/'miko-domain-expired.png']
result={'status':'passed','nativeReview':review,'rawFiles':[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'gallery':'analysis/previews/miko-vfx02/index.html'}
(run/'gallery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Miko native gallery passed')
