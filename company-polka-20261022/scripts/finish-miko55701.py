from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1]
b=r/'analysis/native/miko55701';raw=b/'native/shots'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/miko-review.json');validation=read(b/'capture-validation.json')
assert proof['status']==validation['status']=='passed'
assert [proof[k] for k in ['lowFaithWidth','highFaithWidth','domainWidth']]==[5,5,7]
assert read(b/'native/validation.json')['gods']==22
assert read(b/'native/reload.json')['status']=='passed'
out=r/'analysis/previews/miko55701';out.mkdir(exist_ok=False)
def frames(tier,seq):
    return [raw/f'miko-tier{tier}-option0-{seq}-{s}.png' for s in ['frame0','frame1','state']]
one=frames(1,1);three=frames(3,3);five=frames(5,4)
domain=[raw/f'miko-domain-frame{i}.png' for i in range(4)]
def publish(name,paths,durations):
    imgs=[Image.open(p).convert('RGB').crop((227,196,515,484)).resize((576,576),Image.Resampling.NEAREST) for p in paths]
    for i,im in enumerate(imgs):im.save(out/f'{name}-{i}.png')
    imgs[0].save(out/f'{name}.gif',save_all=True,append_images=imgs[1:],duration=durations,loop=0)
publish('tier1',one[:2],650)
publish('tier3',three[:2],550)
publish('tier5',domain+[five[2]],[260,260,350,550,1100])
publish('progression',[one[2],three[2],*domain,five[2]],[1300,1300,220,220,300,450,1400])
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>미코 · 5 / 5 / 7 성역</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:960px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#ffcadc}</style><h1>미코 · 성역 5×5 → 5×5 → 7×7</h1><p>실제 SDL 검사장 화면. 기존 승인 도트를 사용하며 처음 1성부터 회복·상태 완화·신앙 보상·바닥 표시가 5×5로 적용됩니다. 고정 장비와 높은 자원의 검사장으로, 일반 던전 플레이 영상은 아닙니다.</p><section><h2>전체 변화</h2><img src="progression.gif"></section><section><h2>1성 — 벚꽃 신사 [액티브] · 5×5</h2><img src="tier1.gif"><p>MP3 / 1턴 / 신앙 소모 없음. 최소 기도술 없음. 지속20+0.5×기도술 턴. 설치 완료2턴 뒤부터2턴마다1+기도술/12 HP 회복. 새 독·혼란·감속·공포의 지속시간25% 감소. 위치 고정.</p></section><section><h2>3성 — 액막이 불꽃 [액티브] / 벚꽃 결계 [패시브] · 5×5</h2><img src="tier3.gif"><p>범위를 넓히는 대신 테두리에 분홍·금색 불꽃이 붙습니다. 불꽃: MP3 / 신앙3 / 1턴, 지속5+0.2×기도술 턴. 피해1d(5+floor(기도술/4)), 화염저항 적용. 결계: 자신은 안, 적은 밖일 때 원거리 피해10+floor(기도술/3)% 감소. 최소 기도술 없음. 신앙75 해금.</p></section><section><h2>5성 — 신역 전개 [액티브] · 7×7</h2><img src="tier5.gif"><p>중앙의 결계가 퍼지고 중앙·모서리에 금빛 표식이 남습니다. 활성 불꽃은 새 바깥 테두리로 이동합니다. MP6 / 신앙10 / 1턴, 지속6+0.2×기도술 턴. 피해15+floor(기도술/3)% 감소, 새 상태이상 지속시간50% 감소, 대상 상태 하나 즉시 정화. 종료 후10턴 재사용 제한. 최소 기도술 없음. 신앙120 해금.</p></section><p>새 2성 ‘봉납의 벚꽃’ 처치 회복·초과 회복 보호막은 수치 제안 단계이며 이번 변경에 포함되지 않았습니다.</p></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
runtime=r/'runtime/tiles01/HoloCrawl.exe'
assert not (b/'previous-runtime.exe').exists()
shutil.copy2(runtime,b/'previous-runtime.exe');shutil.copy2(b/'capture-engine.exe',runtime)
sha=hashlib.sha256(runtime.read_bytes()).hexdigest()
design={'status':'implemented-native-validated','date':'2026-11-03','revision':'miko55701','widths':[5,5,7],'art':'Reused approved Miko pixel effects; actual SDL capture.','review':'analysis/previews/miko55701/index.html','tier2Passive':'Proposal only: heal2+Inv/6, overflow shield cap4+Inv/3. Not implemented.','binarySha256':sha}
(r/'analysis/design/miko55701.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='miko',currentVisualReviewGod='miko',currentVisualReviewTier=1,currentVisualReview=design['review'],currentDesignGod='miko',activeWork='miko557-native-gif-review',playBinarySha256=sha,mikoCombatRevision='miko55701',mikoShrine557=design,lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=design['review']
    d['next']='Review Miko5/5/7 native effects. Tier2 kill-heal/overflow-shield remains proposal; do not claim implemented. Suisei1-5 preserved. Vivi/Sopia/Mela combat redesigns remain pending.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
    for key in d.get('sourceSha256',{}):
        f=r/'engine/campaign-crawl/crawl-ref/source'/key
        if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\miko55701\\index.html"\r\n',encoding='ascii')
p=r/'HOLOCRAWL_DESIGN.md';text=p.read_text(encoding='utf-8-sig')
text=text.replace('- ★ 3×3, ★★★ 도달 시 5×5로 상시 확대. 이미 설치한 성역도 즉시 확대.','- 2026-11-03 승인·실제 적용: ★부터5×5, ★★★에서도5×5 유지. ★★★★★ 신역 전개 중7×7. 처음부터 중심 기준 반경2칸.')
p.write_text(text,encoding='utf-8')
note='# 미코 성역5/5/7 실제 적용 / 2026-11-03\n\n1성부터5×5, 3성5×5에 불꽃·결계, 5성7×7. 기존 도트 재사용한 실제SDL GIF: analysis/previews/miko55701/index.html. 범위·화염·종료·22신·저장복원 검사 통과, runtime=miko55701. 새2성 처치회복/초과보호막은 제안이며 아직 미구현. 기존ZIP은 이번 변경 미포함.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
    new=r/'engine/campaign-crawl/crawl-ref/source'/old.name
    patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),new.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',runtimeDeployed=True,binarySha256=sha,nativeProof=proof,validation=validation),indent=2),encoding='utf-8')
print(json.dumps({'status':'passed','review':design['review'],'sha256':sha}))
