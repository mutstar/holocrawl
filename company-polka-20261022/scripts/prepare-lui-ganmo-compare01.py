from pathlib import Path
from PIL import Image
import json,shutil
r=Path(__file__).resolve().parents[1];rev='lui-ganmo-compare01';a=r/'assets/holocrawl'/rev;o=r/'analysis/previews'/rev
a.mkdir(parents=True,exist_ok=True);o.mkdir(parents=True,exist_ok=True)
g=Path('C:/Users/071staff/.codex/generated_images/01a151bb-0451-7ca0-9c5c-46a9c60d09e0')
variants={'a':('exec-9b479468-7d11-4d0c-b422-fbd3d0512daa.png','A · 망토 없는 간모','망토 제거 · 흰 깃과 빨간 넥타이 유지'),'b':('exec-557d2df6-c222-4901-ab49-eaf5171cdc8e.png','B · 망토 + 날카로운 간모','좁은 몸통 · 날카로운 눈매와 깃 · 몸에 붙는 망토')}
for k,(fn,_,_) in variants.items():
 shutil.copy2(g/fn,a/f'{k}-source.png');im=Image.open(a/f'{k}-source.png').convert('RGBA');bounds=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox();im=im.crop(bounds);im.thumbnail((30,30),Image.Resampling.NEAREST)
 tile=Image.new('RGBA',(32,32));tile.alpha_composite(im,((32-im.width)//2,31-im.height));tile.save(a/f'{k}-tile.png');tile.save(o/f'{k}-tile.png')
 tile.resize((192,192),Image.Resampling.NEAREST).save(o/f'{k}-large.png')
shutil.copy2(r/'engine/campaign-crawl/crawl-ref/source/rltiles/holo/raven.png',o/'current-tile.png')
p=r/'analysis/previews/lui-review01/index.html';shutil.copy2(p,o/'previous-review.html');old=p.read_text(encoding='utf-8')
cards=''
for k,(_,title,desc) in variants.items():
 cards+=f'<article><h2>{title}</h2><p>{desc}</p><div class="sprite-large"><img src="../{rev}/{k}-tile.png" width="192" height="192" alt="{title} 6배 확대"></div><div class="sizes"><span>원래 타일 크기<br><img src="../{rev}/{k}-tile.png" width="32" height="32"></span><span>기존 필드 미리보기 배율<br><img src="../{rev}/{k}-tile.png" width="64" height="64"></span></div></article>'
css='body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1100px;margin:24px auto;padding:0 20px;line-height:1.65}h1{color:#dfc4ff}h2{color:#f5db9f;font-size:23px}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}article{background:#1b2736;border:1px solid #39485c;padding:20px;border-radius:10px}img{image-rendering:pixelated}.sprite-large{height:220px;display:flex;align-items:center;justify-content:center;background:#0a0c0f}.sizes{display:flex;justify-content:space-evenly;text-align:center;margin-top:14px;min-height:110px}.sizes span{min-width:180px}.note{color:#b9c6d7}a{color:#a6e9f4}.old{display:flex;align-items:center;gap:20px;margin-top:20px} @media(max-width:700px){.cards{grid-template-columns:1fr}.sizes span{min-width:120px}}'
page=f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>루이 · 간모 A/B 도트 비교</title><style>{css}</style><h1>루이 · 간모 두 버전</h1><p class="note">32×32 타일용 정지 도트 비교 · 같은 높이 30px · 확대는 최근접 보간</p><div class="cards">{cards}</div><div class="old"><img src="../{rev}/current-tile.png" width="64" height="64"><p>현재 적용된 기존 간모<br><span class="note">위 A/B는 선택 전 비교용 시안입니다.</span></p></div><p>1성 매의 권속 · 신앙 ★30 해금 · 최소 기도술 없음 · MP3 · 신앙 소모 0 · 행동 1턴</p><p><a href="../{rev}/previous-review.html#tier1">기존 실제 필드·상세 수치 보기</a></p></html>'
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 q=r/name;d=json.loads(q.read_text(encoding='utf-8-sig'));d['luiPendingVariants']={'revision':rev,'a':'cape removed','b':'cape retained, sharper silhouette','nativeApplied':False};q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 루이 간모 A/B 비교 / lui-ganmo-compare01\n\n사용자 요청으로 A 망토 제거, B 망토 유지+날카로운 실루엣 두 시안 생성. 32px 타일 및 원본은 assets/holocrawl/lui-ganmo-compare01. 현재 실행 파일은 lui-ganmo02 유지, 선택 전 비교 시안만 브라우저에 표시. 현재 링크 analysis/previews/lui-review01/index.html.\n\n'
for name in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 q=r/name;q.write_text(note+q.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Two Ganmo variants saved and comparison page published; native binary unchanged.')
