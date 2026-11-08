"""Seat explicit facility insets in approved22px wall; preserve all interior/door pixels."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];S=R/'preview/city-facilities106';OLD=R/'preview/city-doors102';O=R/'preview/facility-exteriors124';O.mkdir(exist_ok=True)
source=(R/'scripts/city_concrete_material92.py').read_text(encoding='utf-8')
code=source.replace('py>=18','py>=10').replace('py-18','py-10').replace('*3//13','*3//21').replace('y*32+18:y*32+32','y*32+10:y*32+32').replace('return a,wall,repaired',"return a,wall,repaired,front")
ns={};exec(compile(code,'frozen-material121-derived','exec'),ns);render=ns['render']
grain=np.array(Image.open(R/'preview/native-water02/assets/concrete-wall-surface256.png').convert('RGB'))
prior=json.loads((S/'manifest.json').read_text(encoding='utf-8'))
names={'holox':'holoX 연구소','theater':'2기생 극장','dev':'DEV_IS 쵸베리바 출장소','dining':'1기생 타라후쿠 저니','gamers':'게이머즈 폐역','fantasy':'3기생 도타바타 그라운드','wheel':'4기생 기적의 바퀴','market':'5기생 네포라보 마트','mountain':'0기생 페이스 마운틴'}
themes={'holox':(160,112,194),'theater':(177,117,81),'dev':(164,119,187),'dining':(177,132,92),'gamers':(116,168,157),'fantasy':(160,166,106),'wheel':(166,123,166),'market':(119,168,133),'mountain':(177,161,115)}
panels={'theater':[(24,3,232,29)],'dining':[(111,17,178,28)],'gamers':[(30,3,128,17),(194,4,232,20)],'market':[(104,17,184,28)]}
checks=[];maps=[]
for m in prior['maps']:
 id=m['facility'];o=m['origin'];w,h=o['width'],o['height'];x0,y0=o['x']*32,o['y']*32
 data=json.loads((S/m['map']).read_text(encoding='utf-8'));rows=data['rows'];local=[r[o['x']:o['x']+w] for r in rows[o['y']:o['y']+h]]
 visual=[list(r) for r in rows]
 for y in range(1,h-1):
  for x in range(1,w-1):
   if local[y][x] in '#G':visual[o['y']+y][o['x']+x]='.'
 before=np.array(Image.open(S/m['images']['new106']).convert('RGBA'));fresh,_,_,front=render(before,[''.join(r) for r in visual],grain)
 shell=np.zeros((h*32,w*32),bool)
 for y,row in enumerate(local):
  for x,c in enumerate(row):
   if c=='#' and (x in (0,w-1) or y in (0,h-1)):shell[y*32:(y+1)*32,x*32:(x+1)*32]=True
 region=(slice(y0,y0+h*32),slice(x0,x0+w*32));crop=before[region].copy();crop[shell]=fresh[region][shell]
 decal=np.zeros_like(crop);mask=np.zeros_like(shell);face=front[region]
 def paste_art(im,x,y,clip_face=True):
  a=np.array(im.convert('RGBA'));hh,ww=a.shape[:2];allowed=shell[y:y+hh,x:x+ww].copy()
  if clip_face:allowed &= face[y:y+hh,x:x+ww]
  allowed &= a[:,:,3]>0
  crop[y:y+hh,x:x+ww][allowed]=a[allowed];decal[y:y+hh,x:x+ww][allowed]=a[allowed];mask[y:y+hh,x:x+ww]|=allowed
 raw=Image.open(OLD/f'{id}-closed102.png').convert('RGBA').crop((x0,y0,x0+w*32,y0+h*32))
 for box in panels.get(id,[]):
  p=raw.crop(box);height=min(18,p.height);width=round(p.width*height/p.height);p=p.resize((width,height),Image.Resampling.NEAREST);paste_art(p,(box[0]+box[2]-width)//2,11+(20-height)//2)
 accent=themes[id]
 art=Image.new('RGBA',(w*32,h*32));d=ImageDraw.Draw(art)
 if id=='holox':
  for cx in [54,111,175,234]:
   d.rectangle((cx-9,14,cx+9,29),fill=(28,34,44));d.ellipse((cx-6,15,cx+6,27),fill=(99,61,143),outline=accent);d.rectangle((cx-2,17,cx+1,19),fill=(213,173,238))
 if id=='dev':
  for xa,xb,col in [(43,94,(199,125,172)),(192,245,(108,164,183))]:
   d.rectangle((xa,17,xb,25),fill=(26,34,42));d.line((xa+3,21,xb-3,21),fill=col,width=2)
 if id=='wheel':
  for cx,col in [(44,(214,169,128)),(88,(173,130,176)),(199,(204,159,117)),(240,(194,141,178))]:
   d.rectangle((cx-4,17,cx+4,26),fill=(35,38,47));d.rectangle((cx-2,19,cx+2,23),fill=col)
 for p in m['entrances'][:1]:
  x,y=p['x']-o['x'],p['y']-o['y']
  for lx in [x-1,x+1]:
   if not 0<=lx<w or local[y][lx]!='#':continue
   xa,sy=lx*32+10,y*32;d.rectangle((xa,sy+14,xa+11,sy+23),fill=(29,38,46),outline=accent)
   d.line((xa+3,sy+18,xa+8,sy+18),fill=accent,width=2)
 paste_art(art,0,0)
 # This intentional2-row sculpture is architecture, not a roof-mounted prop.
 if id=='mountain':paste_art(Image.fromarray(before[region]).crop((64,0,224,64)),64,0,False)
 assert np.array_equal(crop[~shell],before[region][~shell]),'interior changed'
 assert np.array_equal(crop[shell&~mask],fresh[region][shell&~mask]),'wall material changed'
 preserved=[]
 for member in m['memberDetails']:
  box=member.get('box')
  if not box and 'cell' in member:
   x,y=member['cell'];fw,fh=member['size'];box=[x*32,y*32,(x+fw)*32,(y+fh)*32]
  if box:
   x,y,xx,yy=box;assert np.array_equal(crop[y:yy,x:xx],before[region][y:yy,x:xx]),(id,member['id']);preserved.append(member['id'])
 Image.fromarray(decal).save(O/f'{id}-decal124.png')
 for state,filename in [('closed',m['images']['new106']),('open',m['openImage'])]:
  original=np.array(Image.open(S/filename).convert('RGBA'));a=original.copy();a[region][shell]=crop[shell]
  assert np.array_equal(a[region][~shell],original[region][~shell])
  # Replace ordinary walls outside facility, preserving original ordinary doors/floors.
  external=np.zeros(a.shape[:2],bool)
  for y,row in enumerate(rows):
   for x,c in enumerate(row):
    if c=='#' and not(o['x']<=x<o['x']+w and o['y']<=y<o['y']+h):external[y*32:(y+1)*32,x*32:(x+1)*32]=True
  a[external]=fresh[external];bounds=(x0-32,y0-32,x0+(w+1)*32,y0+(h+1)*32)
  im=Image.fromarray(a).crop(bounds).convert('RGB');im.save(O/f'{id}-{state}124.png');im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST).save(O/f'{id}-{state}124-2x.png')
 maps.append({**m,'name':names[id],'decal':f'{id}-decal124.png','closed':f'{id}-closed124-2x.png','open':f'{id}-open124-2x.png'})
 checks.append({'facility':id,'mapSha256':hashlib.sha256((S/m['map']).read_bytes()).hexdigest(),'perimeterPixels':int(shell.sum()),'decalPixels':int(mask.sum()),'allInteriorAndDoorPixelsPreserved':True,'memberBoxesExact':preserved,'ordinaryWall121OutsideExplicitInsets':True,'geometryUnchanged':True})
 print('Reseated facade:',id,flush=True)
manifest={'revision':124,'maps':maps,'normalWall':121,'frontHeight':22,'nativeIntegrated':False}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'validation.json').write_text(json.dumps({'status':'passed','revision':124,'facilities':9,'checks':checks,'scope':'Explicit exterior decals only; interior/doors/geometry frozen; browser hook uses approved wall121.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for group in range(3):
 sheet=Image.new('RGB',(2208,808),'#151e22');d=ImageDraw.Draw(sheet)
 for i,m in enumerate(maps[group*3:group*3+3]):
  x=i*736;d.text((x+16,10),m['name'],font=font,fill='#deebe5');im=Image.open(O/m['closed']);sheet.paste(im,(x+(736-im.width)//2,57))
 sheet.save(O/f'facilities-{group+1}124.png')
cards=''.join(f'<section><h2>{m["name"]}</h2><img src="{m["closed"]}"><details><summary>문을 연 모습</summary><img src="{m["open"]}"></details></section>' for m in maps)
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>고정지형9곳 · 새 벽22px 외벽124</title><style>body{background:#151e22;color:#dfebe5;font:16px system-ui;margin:24px}a{color:#9adac7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(370px,1fr));gap:20px}img{max-width:100%;image-rendering:pixelated}section{background:#202b30;padding:12px}h2{font-size:19px}</style><h1>고정지형9곳 · 외벽124</h1><p>승인한22px 벽면에 간판·조명·입구 표식을 맞췄습니다. 내부 멤버 장식·문 방향·통로 구조는 유지합니다.</p><p><a href="../city-street124/">실제 생성 지도에서 보기</a> · <a href="../city-market124/">4~7층 안전 배치</a></p><div class="grid">'+cards+'</div>',encoding='utf-8')
