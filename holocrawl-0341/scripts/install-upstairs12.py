from pathlib import Path
from PIL import Image
import sys, json, shutil

root = Path(__file__).resolve().parents[1]
out = root/'preview/stairs-up12'
out.mkdir(parents=True, exist_ok=True)
shutil.copy2(sys.argv[1], out/'stairs-up12-original.png')
image = Image.open(out/'stairs-up12-original.png').convert('RGBA')
box = image.getchannel('A').point(lambda x: 255 if x > 200 else 0).getbbox()
assert box and image.getchannel('A').getextrema()[0] == 0
image.crop(box).resize((32,32), Image.Resampling.NEAREST).save(out/'stairs-up12-32.png')
shutil.copy2(root/'preview/stairs-up11/stairs-up11-32.png', out/'stairs-up08-32.png')
shutil.copy2(root/'preview/street-vision01/assets/cement-reference.png', out/'cement.png')
(out/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>올라가는 원형 계단 12</title><style>body{background:#171b1e;color:#e7e8e4;font:16px system-ui;margin:0;padding:28px}h1{font-size:21px}p{color:#bdc4c5}main{display:flex;flex-wrap:wrap;gap:24px}section{background:#22282b;padding:20px;border:1px solid #475052;border-radius:10px}h2{font-size:17px}canvas{image-rendering:pixelated;max-width:100%;height:auto}small{display:block;color:#b3bab9;margin-top:14px}</style><h1>올라가는 계단 · 꼭대기 계단 연결 수정</h1><p>같은 32×32 크기 · 회색 시멘트 · 손잡이 없는 회전 계단</p><main><section><h2>이전 11 · 꼭대기 접합부</h2><canvas id="old" width="320" height="320"></canvas></section><section><h2>새 버전 12 · 윗단을 이어서</h2><canvas id="new" width="320" height="320"></canvas></section></main><small>4배 확대 비교 · 기존 거리 미리보기는 승인된 08 유지</small><script>const load=s=>new Promise((r,j)=>{let i=new Image;i.onload=()=>r(i);i.onerror=j;i.src=s});Promise.all([load('cement.png'),load('stairs-up08-32.png'),load('stairs-up12-32.png')]).then(([f,a,b])=>{for(const [id,s] of [['old',a],['new',b]]){let c=document.getElementById(id).getContext('2d');c.imageSmoothingEnabled=false;for(let y=0;y<3;y++)for(let x=0;x<3;x++)c.drawImage(f,270,150,32,32,x*128-32,y*128-32,128,128);c.drawImage(s,96,96,128,128)}window.ready=true});</script></html>''', encoding='utf-8')
(out/'generation.json').write_text(json.dumps({'mode':'built-in image_gen','variant':'upstairs12-top-connection','size':32,'approved':False,'replacesApprovedAsset':False,'source':str(out/'stairs-up12-original.png')},indent=2)+'\n', encoding='utf-8')
print(out)
