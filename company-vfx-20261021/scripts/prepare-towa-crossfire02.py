from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/towa-crossfire02';run.mkdir();(run/'before').mkdir()
changed=['holo-visual.cc','rltiles/dc-holo-main.txt']
for n in changed:
 p=run/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if str(p.relative_to(src)).replace('\\','/') not in changed};(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
asset=r/'assets/holocrawl/towa-crossfire02';asset.mkdir(parents=True);shutil.copy2('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0/exec-6e16a9b8-7191-4f20-b32c-10ba5028daf2.png',asset/'winged-bolt.png')
im=Image.open(asset/'winged-bolt.png').convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>128 else 0);im.putalpha(a);im=im.crop(a.getbbox()).resize((26,16),Image.Resampling.NEAREST)
names=['E','NE','N','NW','W','SW','S','SE']
for i,n in enumerate(names):
 b=im.rotate(45*i,resample=Image.Resampling.NEAREST,expand=True);t=Image.new('RGBA',(32,32));t.alpha_composite(b,((32-b.width)//2,(32-b.height)//2));t.save(src/f'rltiles/holo/fx_towa_crossfire_{n.lower()}.png')
p=src/'rltiles/dc-holo-main.txt';p.write_text(p.read_text(encoding='utf-8')+'\n'+''.join(f'fx_towa_crossfire_{n.lower()} HOLO_TOWA_CROSSFIRE_{n}\n' for n in names),encoding='utf-8')
p=src/'holo-visual.cc';s=p.read_text(encoding='utf-8');old='tiles.add_overlay(p,TILE_HOLO_TOWA_BULLET_E+direction);';new='''const int projectile=holo_batch::s.five_end>you.elapsed_time?TILE_HOLO_TOWA_CROSSFIRE_E:TILE_HOLO_TOWA_BULLET_E;
            tiles.add_overlay(p,projectile+direction);''';assert old in s;p.write_text(s.replace(old,new),encoding='utf-8')
s=(r/'scripts/capture-towa-crossfire01.ps1').read_text(encoding='utf-8').replace('towa-crossfire01','towa-crossfire02');(r/'scripts/capture-towa-crossfire02.ps1').write_text(s,encoding='utf-8')
s=(r/'scripts/publish-towa-crossfire01.py').read_text(encoding='utf-8').replace('towa-crossfire01','towa-crossfire02')
s=s.replace("changed=['holo-campaign-test.cc']+[f'rltiles/holo/fx_night_towa5_{f}.png' for f in range(2)]","changed=['holo-visual.cc','rltiles/dc-holo-main.txt']+[f'rltiles/holo/fx_towa_crossfire_{n}.png' for n in ['e','ne','n','nw','w','sw','s','se']]")
s=s.replace("run/'before/holo-campaign-test.cc'","run/'before/holo-visual.cc'").replace("src/'holo-campaign-test.cc'","src/'holo-visual.cc'").replace("fromfile='before/holo-campaign-test.cc',tofile='after/holo-campaign-test.cc'","fromfile='before/holo-visual.cc',tofile='after/holo-visual.cc'")
s=s.replace('실제 교차포화: 적 둘의 이동으로','5성 전용 날개 달린 쌍꼬리 화살 · 실제 교차포화: 적 둘의 이동으로').replace('Tier5 smaller bright lavender wing/crossed-arrow cast crest;','Tier5 distinct winged bolt with twin lavender tail;').replace('밝은연보라44/48px 날개+교차화살 시전문양으로 축소.','5성전용26x16px 날개달린 쌍꼬리투사체추가.3성승인화살유지.밝은연보라44/48px 시전문양유지.')
(r/'scripts/publish-towa-crossfire02.py').write_text(s,encoding='utf-8')
