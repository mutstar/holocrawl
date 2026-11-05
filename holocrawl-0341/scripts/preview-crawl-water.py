from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];out=root/'preview/native-water02';dest=out/'assets/crawl-water';dest.mkdir(exist_ok=True)
groups=[('기본 물','shallow_water','deep_water'),('탁한 물 도트','shallow_water_murky','deep_water_murky'),('해안 Shoals','shoals_shallow_water0','shoals_deep_water0')]
cards=[]
for title,shallow,deep in groups:
    for depth,name in [('얕은 물',shallow),('깊은 물',deep)]:
        shutil.copy2(root/'engine/upstream/crawl-ref/source/rltiles/dngn/water'/f'{name}.png',dest/f'{name}.png')
        cards.append(f'<article><h2>{title} · {depth}</h2><canvas width="256" height="256" data-name="{name}"></canvas></article>')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>돌죽0.34.1 물 도트 원본</title><style>:root{color-scheme:dark;font:15px system-ui;background:#161d20;color:#dfe8df}main{max-width:700px;margin:25px auto;padding:0 16px}h1{font-size:23px}p{color:#b8c8bc;line-height:1.7}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px}article{background:#222d2a;border:1px solid #526b60;padding:14px;border-radius:6px;min-width:0}h2{font-size:15px;margin:0 0 12px}canvas{display:block;width:256px;max-width:100%;height:auto;margin:auto;image-rendering:pixelated}a{color:#b4d9c2}@media(max-width:600px){.pair{grid-template-columns:1fr}}</style><main><h1>돌죽0.34.1 · 물 도트 원본</h1><p>왼쪽 얕은 물 / 오른쪽 깊은 물<br>원본32×32 PNG를 수정 없이4배 확대하여2×2칸으로 반복했습니다.</p>'''
for i in range(0,6,2):html+=f'<section class="pair" id="pair{i//2}">{cards[i]}{cards[i+1]}</section>'
html+='''<p><a href="index.html">우리 물 도트로 돌아가기 →</a></p></main><script>Promise.all(Array.from(document.querySelectorAll('canvas')).map(async c=>{const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/crawl-water/'+c.dataset.name+'.png';});const g=c.getContext('2d');g.imageSmoothingEnabled=false;for(let y=0;y<2;y++)for(let x=0;x<2;x++)g.drawImage(im,x*128,y*128,128,128);})).then(()=>window.ready=true);</script>'''
(out/'crawl-original-water.html').write_text(html,encoding='utf-8')
print('Prepared6 unmodified upstream water references.')
