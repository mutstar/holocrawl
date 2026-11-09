from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='koyori-tier3-review01';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
assert read(b/'native/koyori-caster.json')['status']=='passed'
assert read(b/'native/koyori-reload.json')['status']=='passed'
for n,h in read(b/'preserved-files.json').items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
out=r/'analysis/previews'/rev;out.mkdir(parents=True,exist_ok=True);shots=b/'native/shots'
titles=['폭발 반응','열충격','점액 반응'];pairs=[3,5,4]
mix=['독성 표식 + 발열 주문','발열 표식 + 냉각 주문','냉각 표식 + 독성 주문']
desc=['대상과 주변 1칸의 적에게 화염 피해. I=12: ⌊2d8 × 0.85⌋.','대상 한 명에게 물리 피해. I=12: ⌊3d9 × 0.85⌋, AC를 절반만 적용.','대상과 주변 1칸의 적에게 피해 + 3턴간 이동 시간 35% 증가. I=12: ⌊2d5 × 0.85⌋.']
cards=[]
for i,pair in enumerate(pairs):
 files=[shots/f'koyori3-{i}-before.png']+[shots/f'koyori-reaction-pair{pair}-{i+1}-frame{f}.png' for f in range(2)]+[shots/f'koyori3-{i}-after.png']
 frames=[Image.open(p).convert('RGB').crop((291,252,515,428)).resize((448,352),Image.Resampling.NEAREST) for p in files]
 frames[0].save(out/f'koyori3-{i}.gif',save_all=True,append_images=frames[1:],duration=[900,300,300,1000],loop=0,optimize=False)
 cards.append(f'<article><h2>{titles[i]}</h2><p><b>{mix[i]}</b></p><p>{desc[i]}</p><img src="../{rev}/koyori3-{i}.gif" alt="{titles[i]} 실제 주문 반응"><p>표식 준비 → 주문 적중·반응 → 표식 소모</p></article>')
css='body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1250px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#ffb8df}h2{color:#a6e9f4;font-size:22px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}article{background:#1b2736;padding:18px;border-radius:12px}img{max-width:100%;image-rendering:pixelated}.info{background:#202b3e;padding:16px;border-radius:10px}b{color:#ffe09d}a{color:#abe7ff}'
page='<!doctype html><html lang="ko"><meta charset="utf-8"><title>코요리 · 3성 촉매 반응</title><style>'+css+'</style><h1>코요리 · 3성 촉매 반응 / 마법 전달</h1><section id="tier3"><p class="info"><b>공격 주문 사거리 +1 · 다른 시약이 만나면 자동 반응</b><br>해금: 신앙 ★★★(75) · 최소 기도술 제한 없음 · 별도 버튼·추가 MP/신앙 소모 없음.<br>원래 주문의 MP는 그대로 소모합니다. 사거리는 시야를 넘지 않으며 폭발 범위는 늘지 않습니다. 자신 대상·인접 전용·일부 고정 범위 주문은 제외됩니다.</p><p>캐릭터 옆 시험관 = 이번 주문에 실릴 시약 / 몹 옆 시험관 = 남아 있는 표식.<br>서로 다른 시약이 반응하면 기존 표식을 소모합니다. 조합은 순서와 관계없이 같습니다.</p><div class="cards">'+''.join(cards)+'</div><p class="info"><b>반응 피해는 기존 초안에서 15% 줄인 수치(×0.85)입니다.</b><br>폭발: ⌊2d(5+⌊I/4⌋) × 0.85⌋ · 열충격: ⌊3d(6+⌊I/4⌋) × 0.85⌋ · 점액: ⌊2d(3+⌊I/6⌋) × 0.85⌋.<br>I는 기도술. 피해식은 저항·방어 적용 전입니다. 한 주문당 반응 중심은 최대 한 곳이며, 광역 주문의 나머지 대상에는 단일 시약이 붙습니다. 주변 피해는 적에게만 적용되고 벽을 통과하지 않습니다.<br>점액은 이동만 늦추며 공격·주문 시전 속도는 그대로입니다.</p><p>영상: 실제 게임 엔진에서 신앙 90·기도술 12, 기존 표식을 준비한 뒤 일반 마법의 다트(MP1)로 반응을 일으킨 장면입니다. 두 번째 몹으로 광역/단일 대상 차이를 보여줍니다. 시험 장면은 독립 실행이며 반응 첫 발견 시 신앙 보상을 받을 수 있습니다.</p><p><a href="../koyori-tube02/index.html#tier1">확정한 1성 보기</a></p></section></html>'
(out/'index.html').write_text(page,encoding='utf-8');(r/'analysis/previews/koyori-review01/index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);d=json.loads(m[1]);d['koyori']=[dict(tier=3,option=i+1,title=titles[i],image=f'../{rev}/koyori3-{i}.gif',kind='실제 주문 적중 · 시약 반응') for i in range(3)];txt=txt[:m.start(1)]+json.dumps(d,ensure_ascii=False)+txt[m.end(1):]
article='<article id="koyori" data-god="koyori"><h2>코요리 <small>3성 · 검토 중</small></h2><select onchange="choose(this)">'+''.join(f'<option value="{i}">3성 · {titles[i]}</option>' for i in range(3))+f'</select><p class="scene-note">실제 주문 적중 · 시약 반응</p><img class="scene" src="../{rev}/koyori3-0.gif"><p>공격 주문 사거리+1(시야 상한). 다른 시약을 맞히면 자동 반응·표식 소모. 추가 MP/신앙 없음. 최소 기도술 없음. ★★★(75) 해금.</p><p><a href="../koyori-review01/index.html#tier3">세 반응과 상세 수치 보기</a></p><label>피드백<textarea data-feedback="koyori"></textarea></label></article>'
txt,n=re.subn(r'<article id="koyori".*?</article>',lambda _:article,txt,count=1,flags=re.S);assert n==1
info=dict(effect='공격 주문 사거리+1(시야 상한). 서로 다른 시약이 만나 폭발/열충격/점액 반응. 기존 표식 소모. 주문당 반응 중심1곳.',cost='자동 · 추가 MP/신앙 없음 · 최소 기도술 없음 · 신앙75 해금',scaling='반응 피해×0.85. 폭발2d(5+I/4), 열충격3d(6+I/4)·AC절반, 점액2d(3+I/6)·이동+35%/3턴. 나눗셈 버림.')
txt,n=re.subn(r'const koyoriCasterInfo=.*?;\nfunction updateSkillInfo',lambda _:'const koyoriCasterInfo='+json.dumps(info,ensure_ascii=False)+';\nfunction updateSkillInfo',txt,count=1);assert n==1;p.write_text(txt,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['koyori'].update(approved=[1],pending=[3,5],tier1Revision='koyori-tube02',tier3Revision=rev,pendingRevision=rev,visualSourceRevision=rev,feedback='1성 시험관 크기 승인, 3성 검토로 진행.');d['next']='Review Koyori tier3 reactions.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,currentVisualReviewGod='koyori',currentVisualReviewTier=3,next='Review analysis/previews/koyori-review01/index.html#tier3');
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 코요리 3성 반응 검토 / '+rev+'\n\n1성 koyori-tube02 승인. 3성 폭발/열충격/점액의 실제 주문 발동 캡처 및 일반 던전 반응 연출 연결. 전투 수치 그대로, 신규 도트 생성 없음. 현재 브라우저 #tier3. 3·5성 승인 대기.\n\n'
for name in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
diff=[]
for p in (b/'before').iterdir():diff.extend(difflib.unified_diff(p.read_text().splitlines(True),(s/p.name).read_text().splitlines(True),fromfile='before/'+p.name,tofile='after/'+p.name))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,combatNumbersChanged=False,otherSourceAndAllArtPreserved=True,tier1Approved=True,tier3Approved=False,binarySha256=digest,validation=v),indent=2),encoding='utf-8');print('Published native tier3 review; tier1 approval saved.')
