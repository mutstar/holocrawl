from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];run=r/'analysis/native/lamy-banquet-vfx04';raw=run/'native/shots';out=r/'analysis/previews/lamy-banquet-vfx04';src=r/'engine/campaign-crawl/crawl-ref/source'
baseline=r/'analysis/native/lamy-banquet-vfx01';(run/'before').mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/lamy-cloud-reload.json','native/lamy-tools.json','native/lamy-banquet-vfx.json']:
    assert read(run/n)['status']=='passed',n
for n,h in read(baseline/'preserved-files.json').items():
    if n not in ['tiledgnbuf.cc','tiledgnbuf.h']:assert sha(src/n)==h.upper(),n
assert (src/'holo-lamy.cc').read_text().replace('holo_visual::lamy_banquet_burst(centre);','holo_visual::invocation("lamy",3,centre);')==(baseline/'before/holo-lamy.cc').read_text(),'Combat changed beyond render hook'
assert not out.exists(),'Preserve previous preview';out.mkdir(parents=True)
def sequence_between(before,after):
    a=(raw/before).stat().st_mtime_ns;b=(raw/after).stat().st_mtime_ns
    candidates=[p for p in raw.glob('lamy5-burst*-frame0.png') if a<=p.stat().st_mtime_ns<=b]
    assert len(candidates)==1,[p.name for p in candidates]
    stem=candidates[0].name.replace('-frame0.png','')
    for f in range(4):assert read(raw/f'{stem}-frame{f}-area.json')['visibleFloorCells']==9
    return stem
spell=sequence_between('lamy5-hit-before.png','lamy5-hit-after.png');tool=sequence_between('lamy5-tool-before.png','lamy5-tool-after.png')
wall_start=(raw/'lamy5-wall-before.png').stat().st_mtime_ns;wall=sorted([p for p in raw.glob('lamy5-burst*-frame0.png') if p.stat().st_mtime_ns>=wall_start],key=lambda p:p.stat().st_mtime_ns)[0].name.replace('-frame0.png','')
wall_cells=read(raw/f'{wall}-frame0-area.json')['visibleFloorCells'];assert wall_cells<9
seq=[('lamy5-before.png','눈의 연회 · 사용 전','취기40 필요 · MP6 / 신앙12 / 1턴',800)]
seq += [(f'lamy5-cast{f}.png','연회 시작 · 눈꽃 고리 전개','취기를 전부 소모 · 과음 해소',140) for f in range(4)]
seq += [('lamy5-active.png','연회 유지 · 발밑의 눈꽃 고리','기도술12 기준 시전 후8턴 · 주문 위력 +16%',1100),('lamy5-moved.png','이동해도 연회 고리가 따라옴','자동으로 주변에 피해를 주는 장판은 아님',800),('lamy5-hit-before.png','공격 주문 적중 직전','폭발의 중심은 플레이어가 아니라 적중 지점',500)]
seq += [(f'{spell}-frame{f}.png','하늘색3×3칸 안에 눈꽃 만개','중심 2d9 · 주변1칸 같은 굴림의50% · 기도술12',170) for f in range(4)]
seq += [('lamy5-hit-after.png','주변 적에게 피해와 냉각','범위 밖 적은 피해 없음 · 같은 사용 중첩 중복 없음',1100),('lamy5-tool-before.png','피해 도구로도 눈꽃 폭발','실제 불 마법봉 사용',500)]
seq += [(f'{tool}-frame{f}.png','도구 적중 지점에도 눈꽃 만개','사용당1회 · 10aut당1회 · 구름 사용 전체 최대1회',170) for f in range(4)]
seq += [('lamy5-tool-after.png','도구 적중 후에도 연회 유지','기존 도구 충전·비용과 냉각 판정 유지',900),('lamy5-expired.png','연회 종료 · 눈꽃 고리 소멸','종료 후15턴 재사용 대기 · 취기0',1400)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);frames=[];full=[]
for name,title,note,delay in seq:
    im=Image.open(raw/name).convert('RGB');full.append(im);card=Image.new('RGB',(640,524),'#101923');d=ImageDraw.Draw(card);d.text((12,7),title,font=font,fill='#d3f5ff');d.text((12,35),note,font=small,fill='#adcde0');card.paste(im.crop((259,228,579,452)).resize((640,448),Image.Resampling.NEAREST),(0,76));frames.append(card)
def gif(path,indices):
    chosen=[frames[i] for i in indices];chosen[0].save(path,save_all=True,append_images=chosen[1:],duration=[seq[i][3] for i in indices],loop=0)
gif(out/'tier5.gif',list(range(len(seq))));gif(out/'activation.gif',list(range(7)));gif(out/'spell-burst.gif',list(range(7,13)));gif(out/'tool-burst.gif',list(range(13,19)))
full[0].save(out/'tier5-full.gif',save_all=True,append_images=full[1:],duration=[x[3] for x in seq],loop=0)
sheet=Image.new('RGB',(1280,1048),'#101923')
for pos,i in enumerate([3,6,9,19]):sheet.paste(frames[i],((pos%2)*640,(pos//2)*524))
sheet.save(out/'tier5-states.png')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>라미 5성 · 눈의 연회</title><style>body{background:#101923;color:#def2ff;font:18px system-ui;max-width:960px;margin:28px auto;line-height:1.7}img{max-width:100%;image-rendering:pixelated}a{color:#9cdfff}button{padding:10px;background:#22344c;color:#def2ff;border:1px solid #6990af;margin:4px}.info{background:#172637;padding:18px}</style><h1>라미 5성 · 눈의 연회</h1><div class="info"><b>사용 조건·비용</b><br>신앙120 이상 · 취기40 이상 · 취기 전부 소모 · MP6 · 신앙12 · 시전1턴<br><b>유지 효과</b><br>시전 후6+⌊기도술/6⌋턴. 취기20으로 취급하며1·3성 가호 유지,과음 EV−3 해소. 발밑의 눈꽃 고리가 따라다님.<br><b>적중 효과</b><br>공격 주문·피해 도구·기록된 구름의 첫 피해 지점에 주변1칸(3×3) 눈꽃 폭발. 중심2d(5+⌊기도술/3⌋),주변은 같은 굴림의50%(버림). 사용당1회·10aut당1회. 같은 구름 사용 전체에서는 최대1폭발. 같은 사용의 냉각은 적마다 최대1.<br><b>기도술12 기준</b><br>시전 후8턴 · 중심2d9 · 주변절반 · 종료 후15턴 재사용 대기.1성 명목 주문 위력+16%는 피해+16%가 아니며 도구 위력 증가 효과도 아님.</div><p>연회 시작 → 발밑 고리 유지·이동 → 주문과 도구 적중 지점의 눈꽃 폭발 → 종료 순서입니다. 자동 주변 피해 장판이 아닙니다.</p><div><button onclick="show('tier5.gif')">전체 순서</button><button onclick="show('activation.gif')">연회 시작·이동</button><button onclick="show('spell-burst.gif')">주문 적중 시 효과</button><button onclick="show('tool-burst.gif')">도구 적중 시 효과</button></div><img id="scene" src="tier5.gif"><p>실제 SDL 게임 캡처를 확대·느리게 재생. 연한 하늘색 1픽셀 칸 테두리로 실제3×3범위를 표시합니다. 내부는투명하고선은눈꽃·몬스터아래에있어눈꽃을가리지않습니다. 벽/시야에맞춰범위를제한합니다. 전투 수치·판정 변경 없음. 라미1·3성 승인 유지,5성 검토 중.</p><p><a href="tier5-full.gif">전체 게임 화면</a> · <a href="tier5-states.png">단계별 비교</a> · <a href="../../../assets/holocrawl/lamy-banquet-vfx01/prompt.json">내장 imagegen 도트 제작 프롬프트</a></p><script>function show(file){document.querySelector('#scene').src=file+'?'+Date.now()}</script></html>'''
(out/'index.html').write_text(html,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';shutil.copy2(p,run/'before/integrated-index.html');s=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1))
for e in d['lamy']:
    if e['tier']==5:e.update(image='../lamy-banquet-vfx04/tier5.gif',kind='실제 연회 시작/유지·이동 → 주문·도구 적중 지점3×3 눈꽃 만개 → 종료 · 기도술12 · 몬스터 아래에 표시')
s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];s=s.replace("if(active.id==='lamy')sel.value='1'","if(active.id==='lamy')sel.value='2'").replace('3성 확인 중','5성 확인 중').replace('1성 승인 완료. 지금은3성 취설의 마법을 확인합니다.','1·3성 승인 완료. 지금은5성 눈의 연회를 확인합니다.');p.write_text(s,encoding='utf-8')
digest=sha(run/'capture-engine.exe');shutil.copy2(run/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');changed=['holo-lamy.cc','holo-visual.cc','holo-visual.h','tilereg-dgn.cc','tiledgnbuf.cc','tiledgnbuf.h','holo-campaign-test.cc','rltiles/dc-holo-feat.txt'];patch=''
for n in changed:
    dst=run/'source_snapshot'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,dst);patch+=''.join(difflib.unified_diff(((baseline/'before'/n) if (baseline/'before'/n).exists() else (run/'before'/n)).read_text().splitlines(True),(src/n).read_text().splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
manifest=dict(status='passed',revision='lamy-banquet-vfx04',numericChanges=False,combatRevision='lamy-tools05',renderHookOnly=True,runtimeSha256=digest,proof=read(run/'native/lamy-banquet-vfx.json'),spellSequence=spell,toolSequence=tool,openFloorCells=9,wallControlCells=wall_cells,reviewStatus='tiers1/3 approved; tier5 pending',sourceHashes={n:sha(src/n) for n in changed},scope='Native VFX, cost/damage geometry, save and 22-god regressions; not campaign winrate')
manifest['rangeOutline']=dict(rgb=[137,213,249],alpha=100,widthPixelsAt32pxTile=1,fill=False,belowSnowAndActors=True)
(run/'checkpoint-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name
    if not p.exists():continue
    backup=run/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup);d=read(p);d.update(visualRevision='lamy-banquet-vfx04',combatRevision='lamy-tools05',playBinarySha256=digest,currentVisualReviewGod='lamy',currentVisualReviewTier=5,lamyVisualValidation='analysis/native/lamy-banquet-vfx04/checkpoint-manifest.json',lamyReviewStatus='Tiers1/3 approved. Tier5 activation/following wreath/real spell and tool burst/expiry ready for user review.',next='Wait for Lamy tier5 VFX feedback; do not auto-approve or move to Polka.');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['lamy'].update(pendingRevision='lamy-banquet-vfx04',pendingTier5Revision='lamy-banquet-vfx04');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 라미 5성 연출 검토 · lamy-banquet-vfx04

뭇별이3성을승인하고5성연출검토를요청했다. 연회시작눈꽃고리4프레임,저장된five_end동안플레이어발밑고리유지·이동·종료,실제주문/마법봉적중지점3×3눈꽃만개4프레임을적용. 연한하늘색1px테두리로3×3칸표시.중앙은투명하며테두리는눈꽃·몬스터아래층.폭발도트는9개셀로분할해벽·LOS에맞춰몬스터아래표시. 기존1·3성도트보존. holo-lamy.cc는기존시각화호출만교체했고전투수치/판정은lamy-tools05그대로.

검토: analysis/previews/lamy-banquet-vfx04/index.html
검증: analysis/native/lamy-banquet-vfx04/checkpoint-manifest.json
원본·프롬프트: assets/holocrawl/lamy-banquet-vfx01/
실제연회비용/8턴/저장/일반이동/주문·도구폭발/중심·인접피해/범위밖무피해/냉각중복방지/고리종료/렌더링RNG보존/22신회귀/구름새프로세스저장재현통과. 캠페인승률검증아님.

라미1·3성승인,5성피드백대기.자동승인·폴카진행하지않음.아래는이전인계기록.

'''
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','HOME_RESUME.md','START_HERE_HOME.md','HOME_SESSION.md']:
    p=r/name;shutil.copy2(p,run/'before'/name);p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(dict(status='passed',spellSequence=spell,toolSequence=tool,wallCells=wall_cells,review=str(out/'index.html')),ensure_ascii=False))
