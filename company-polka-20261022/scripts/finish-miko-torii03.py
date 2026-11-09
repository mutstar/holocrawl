from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='miko-torii03';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/miko-review.json');v=read(b/'capture-validation.json')
assert proof['status']==v['status']=='passed'
assert read(b/'native/validation.json')['gods']==22
assert read(b/'native/reload.json')['status']=='passed'
raw=b/'native/shots';out=r/'analysis/previews'/rev
shutil.copytree(r/'analysis/previews/miko55701',out)
def publish(name,paths,durations):
    imgs=[Image.open(p).convert('RGB').crop((227,196,515,484)).resize((576,576),Image.Resampling.NEAREST) for p in paths]
    for i,im in enumerate(imgs):im.save(out/f'{name}-{i}.png')
    imgs[0].save(out/f'{name}.gif',save_all=True,append_images=imgs[1:],duration=durations,loop=0)
domain=[raw/f'miko-domain-frame{i}.png' for i in range(4)]
state=raw/'miko-tier5-option0-4-state.png'
publish('tier5',domain+[state],[260,260,350,550,1600])
publish('progression',[raw/'miko-tier1-option0-1-state.png',raw/'miko-tier3-option0-3-state.png',*domain,state],[1000,1000,220,220,300,450,1700])
publish('expiry',[state,raw/'miko-fire-expired.png',raw/'miko-domain-expired.png'],[1400,1400,1100])
page=(out/'index.html').read_text(encoding='utf-8')
page=page.replace('미코 · 5 / 5 / 7 성역','미코 · 금줄 토리이 신역')
page=page.replace('기존 승인 도트를 사용하며','새 토리이 도트와 기존 승인 도트를 사용하며')
page=page.replace('중앙의 결계가 퍼지고 중앙·모서리에 금빛 표식이 남습니다.','중앙의 결계가 퍼지고 7×7의 네 모서리에 금줄·흰 종이 장식이 달린 기존보다 약33% 커진 붉은 토리이가 세워집니다. 모서리 바닥 표식을 지우고 토리이를 조금 위로 띄워 금줄이 선명하게 보입니다. 중앙 금빛 표식은 유지합니다. 토리이는 시각 효과이며 통행이나 공격을 막지 않습니다.')
page=page.replace('</html>','<section><h2>불꽃 종료 → 신역 종료</h2><img src="expiry.gif"><p>불꽃이 먼저 꺼져도 토리이는 신역 종료까지 유지되며, 5성이 끝나면 사라집니다.</p></section></html>')
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe';assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime)
sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design=read(r/'analysis/design/miko55701.json')
design.update(date='2026-11-03',revision=rev,review=f'analysis/previews/{rev}/index.html',binarySha256=sha,art='Four generated32px torii rendered at4/3 scale,raised,corner floor glyph suppressed; with golden shimenawa and white shide at7x7 corners. Visual only; expire with tier5. Existing shrine,flame,expansion retained.')
(r/'analysis/design/miko-torii03.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentVisualReviewTier=5,currentVisualReview=design['review'],activeWork='miko-tier5-torii-review',playBinarySha256=sha,mikoCombatRevision=rev,mikoShrine557=design,lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=design['review']
    d['next']='Review Miko5-star four-corner torii native GIF. 5/5/7 footprints preserved. New tier2 kill-heal/overflow-shield remains proposal; Suisei1-5 preserved, Vivi/Sopia/Mela combat redesigns pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        f=r/'engine/campaign-crawl/crawl-ref/source'/key
        if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\miko-torii03\\index.html"\r\n',encoding='ascii')
note='# 미코5성 네 모서리 금줄 토리이 / 2026-11-03\n\n실제 SDL 렌더링: analysis/previews/miko-torii03/index.html. 5성 활성중7×7 네 모서리에 금줄·흰 종이 장식 토리이1칸씩 표시, 종료시 제거. 통행·전투수치 변경없음. 기존5/5/7 범위 유지. 네 모서리·내부 제외·종료·캡처 불변·22신 회귀·저장복원 통과. runtime=miko-torii03. 새2성 패시브는 아직 미구현. 이전ZIP은 최신변경 미포함.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
patch=''
for old in (b/'before').rglob('*'):
    if old.is_file():
        rel=old.relative_to(b/'before');new=r/'engine/campaign-crawl/crawl-ref/source'/rel
        patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),new.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,runtimeDeployed=True,binarySha256=sha,nativeProof=proof,validation=v,cornerMarkers=4,visualOnly=True),indent=2),encoding='utf-8')
print(json.dumps({'status':'passed','review':design['review'],'sha256':sha}))
