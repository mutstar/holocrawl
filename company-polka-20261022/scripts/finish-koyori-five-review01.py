from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='koyori-five-review01';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
assert read(b/'native/koyori-five-review.json')['status']=='passed'
assert read(b/'native/koyori-caster.json')['status']=='passed' and read(b/'native/koyori-reload.json')['status']=='passed'
for n,h in read(b/'preserved-files.json').items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
o=r/'analysis/previews'/rev;o.mkdir(parents=True,exist_ok=True);shots=b/'native/shots'
def frame(p):return Image.open(p).convert('RGB').crop((291,252,515,428)).resize((448,352),Image.Resampling.NEAREST)
def gif(name,files,times):
 imgs=[frame(p) for p in files];imgs[0].save(o/name,save_all=True,append_images=imgs[1:],duration=times,loop=0,optimize=False)
activation=[shots/'koyori5-before.png',shots/'koyori5-activate0.png',shots/'koyori5-activate1.png',shots/'koyori5-ready.png']
gif('activation.gif',activation,[700,300,300,900]);allfiles=list(activation);dur=[700,220,220,600]
pairs=[5,3,4,5];names=['열충격','폭발','점액','열충격'];cards=[]
for i,pair in enumerate(pairs):
 stem=shots/f'koyori5-cast{i}';effects=[shots/f'koyori5-reaction-pair{pair}-{i+4}-frame{f}.png' for f in range(4)]
 for f in range(4):
  area=read(effects[f].with_name(effects[f].stem+'-area.json'));assert area['impactCells']==(1 if pair==5 else 9) and area['visibleFloorCells']==(1 if pair==5 else 9)
 files=[Path(str(stem)+'-before.png')]+effects+[Path(str(stem)+'-after.png')];times=[500,200,200,200,250,700]
 gif(f'cast{i}.gif',files,times);allfiles+=files;dur+=times
 cards.append(f'<article><h2>{i+1}회 · 강화 {names[i]}</h2><p>강화 횟수 <b>{4-i} → {3-i}</b></p><img src="../{rev}/cast{i}.gif" alt="실제 강화 {names[i]} 주문"><p>{"마지막 횟수 소모 · 시약 고리 종료" if i==3 else "다음 반응: "+names[i+1]}</p></article>')
gif('four-casts.gif',allfiles,dur)
css='body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1250px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#ffb8df}h2{color:#a6e9f4;font-size:22px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}article{background:#1b2736;padding:18px;border-radius:12px}img{max-width:100%;image-rendering:pixelated}.info{background:#202b3e;padding:16px;border-radius:10px}b{color:#ffe09d}a{color:#abe7ff}'
page='<!doctype html><html lang="ko"><meta charset="utf-8"><title>코요리 · 5성 임계 실험</title><style>'+css+'</style><h1>코요리 · 5성 임계 실험</h1><section id="tier5"><p class="info"><b>표식 준비 없이 두 시약 동시 주입 → 강화 반응</b><br>해금: 신앙 ★★★★★(120) · 최소 기도술 제한 없음.<br>발동: MP6·신앙10·0.5턴 / 지속: 발동 후 8턴 또는 피해를 준 공격 주문 4회 중 먼저 끝날 때까지.<br>재사용: 발동 시점부터 20턴. 이후 주문의 원래 MP는 따로 소모합니다.</p><div class="cards"><article><h2>발동과 강화 상태</h2><p>캐릭터 주위의 세 시약 고리가 강화 상태를 표시합니다. 남은 횟수·시간·다음 조합은 게임 상태창에도 표시됩니다.</p><img src="../'+rev+'/activation.gif" alt="임계 실험 실제 발동"><p>열충격 → 폭발 → 점액 → 열충격 순서</p></article><article><h2>발동부터 4회 소모까지</h2><p>기존 표식 없이 발동합니다. 같은 주문의 다단히트·광역 적중은 강화 횟수 하나만 소모합니다.</p><img src="../'+rev+'/four-casts.gif" alt="임계 실험 네 번의 실제 주문"><p>3성보다 두 번 맥동하는 강화 연출. 폭발·점액의 3×3 색상 테두리와 주변 타격도 유지됩니다.</p></article></div><p class="info"><b>3성과 비교한 강화 효과</b><br>열충격: 피해 +50%, AC 완전 무시 · 대상 한 명.<br>폭발·점액: 피해 +35% · 대상과 주변 1칸(3×3)의 적.<br>강화 점액: 이동 시간 +50%를 4턴간 적용. 공격·시전 속도는 그대로입니다.<br>기도술 12 예시: 열충격 ⌊3d9 × 0.85 × 1.5⌋ / 폭발 ⌊2d8 × 0.85 × 1.35⌋ / 점액 ⌊2d5 × 0.85 × 1.35⌋. 피해 배율은 합쳐서 한 번만 버립니다.</p><div class="cards">'+''.join(cards)+'</div><p>실제 게임 엔진의 일반 마법의 다트로 촬영한 고정 시험 장면입니다. 기본 턴 경과를 생략해 네 번의 반응을 이어 보여주며, 실제 플레이에서는 8턴 제한도 함께 적용됩니다. 빗나감·0피해에는 강화 횟수를 쓰지 않지만 주문 MP·행동 시간은 정상 소모합니다. 반응 중심은 주문당 최대 한 곳. 주변 피해는 적에게만 적용되며 벽을 통과하지 않습니다.</p><p><a href="../koyori-tier3-border01/index.html#tier3">확정한 3성 보기</a></p></section></html>'
(o/'index.html').write_text(page,encoding='utf-8');(r/'analysis/previews/koyori-review01/index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);d=json.loads(m[1]);d['koyori']=[dict(tier=5,option=1,title='임계 실험 · 발동과 강화 주문4회',image=f'../{rev}/four-casts.gif',kind='실제 5성 발동·일반 주문 적중·강화 횟수 소모')];txt=txt[:m.start(1)]+json.dumps(d,ensure_ascii=False)+txt[m.end(1):]
article=f'<article id="koyori" data-god="koyori"><h2>코요리 <small>5성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">5성 · 임계 실험</option></select><p class="scene-note">발동과 강화 주문4회</p><img class="scene" src="../{rev}/four-casts.gif"><p>MP6·신앙10·0.5턴.8턴 또는4회.재사용20턴.두 시약 동시 주입·강화 반응.</p><p><a href="../koyori-review01/index.html#tier5">발동·네 번의 반응·상세 수치 보기</a></p><label>피드백<textarea data-feedback="koyori"></textarea></label></article>'
txt,n=re.subn(r'<article id="koyori".*?</article>',lambda _:article,txt,count=1,flags=re.S);assert n==1
info=dict(effect='두 시약 동시 주입. 열충격→폭발→점액→열충격. 8턴 또는 피해를 준 공격 주문4회.',cost='MP6 · 신앙10 · 0.5턴 · 발동부터 재사용20턴 · 해금120 · 최소 기도술 없음',scaling='열충격×1.5·AC무시, 폭발/점액×1.35. 강화점액 이동+50%/4턴. 3성×0.85는 유지.')
txt,n=re.subn(r'const koyoriCasterInfo=.*?;\nfunction updateSkillInfo',lambda _:'const koyoriCasterInfo='+json.dumps(info,ensure_ascii=False)+';\nfunction updateSkillInfo',txt,count=1);assert n==1;p.write_text(txt,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['koyori'].update(approved=[1,3],pending=[5],tier1Revision='koyori-tube02',tier3Revision='koyori-tier3-border01',tier5Revision=rev,pendingRevision=rev,visualSourceRevision=rev,feedback='3성 최종 색상 테두리 승인, 5성 검토로 진행.');d['next']='Review Koyori tier5 Critical Experiment.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,currentVisualReviewGod='koyori',currentVisualReviewTier=5,next='Review analysis/previews/koyori-review01/index.html#tier5')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 코요리 5성 검토 / '+rev+'\n\n1·3성 승인. 3성 최종본 koyori-tier3-border01 보존. 5성 발동 고리 30px, 강화 상태 고리 표시, 강화 반응 두 번 맥동. 실제 일반 주문으로 네 번의 강화 횟수 소모 캡처. 전투 수치 변경 없음. 현재 #tier5, 5성 승인 대기.\n\n'
for name in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
diff=[]
for p in (b/'before').rglob('*'):
 if p.is_file():
  rel=p.relative_to(b/'before');diff.extend(difflib.unified_diff(p.read_text().splitlines(True),(s/rel).read_text().splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,combatNumbersChanged=False,otherSourceAndPreviousTierArtPreserved=True,approvedTiers=[1,3],tier5Approved=False,binarySha256=digest,validation=v,nativeFourCasts=read(b/'native/koyori-five-review.json')),indent=2),encoding='utf-8');print('Koyori tier5 published; tier3 approval saved.')
