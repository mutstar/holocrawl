from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,re,difflib

r=Path(__file__).resolve().parents[1];run=r/'analysis/native/lamy-chill-vfx01';raw=run/'native/shots';out=r/'analysis/previews/lamy-chill-vfx01';src=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/lamy-caster.json','native/lamy-chill-vfx.json']:
    assert read(run/n)['status']=='passed',n
for n,h in read(run/'preserved-source.json').items():assert sha(src/n)==h.upper(),n
preserved_art=0
for item in read(r/'TRANSFER_MANIFEST.json')['files']:
    if item['path'].startswith('engine/campaign-crawl/crawl-ref/source/rltiles/holo/'):
        assert sha(r/item['path'])==item['sha256'].upper(),item['path']
        preserved_art+=1
old=(run/'before/holo-lamy.cc').read_text();new=(src/'holo-lamy.cc').read_text()
assert new.replace('        const auto pos=mon.pos();\n','').replace('        holo_visual::lamy_chill_burst(pos);\n','')==old,'Combat changed beyond render-only hook'
assert not out.exists(),'Preserve existing preview'
out.mkdir(parents=True)
start=(raw/'lamy3-cast2.png').stat().st_mtime_ns;end=(raw/'lamy3-cast3.png').stat().st_mtime_ns
bursts=[p for p in raw.glob('lamy3-burst*-frame0.png') if start<=p.stat().st_mtime_ns<=end]
assert len(bursts)==1,[(p.name,p.stat().st_mtime_ns) for p in bursts]
stem=bursts[0].name.replace('-frame0.png','')
seq=[('lamy3-before.png','취설의 마법 · 주문 적중으로 냉각 축적','취기20 이상 · 자동 가호 · 추가 비용 없음',800),
     ('lamy3-cast1.png','첫 주문 적중 · 냉각 1중첩','적 칸 오른쪽 위 눈꽃 1개',1100),
     ('lamy3-cast2.png','두 번째 주문 적중 · 냉각 2중첩','적 칸 오른쪽 위 눈꽃 2개',1100)]
seq += [(f'{stem}-frame{f}.png','세 번째 주문 적중 · 얼음 결정 파열','냉각 3중첩 소모 · 기도술12: 추가 냉기 2d5',140) for f in range(4)]
seq += [('lamy3-cast3.png','중첩 소모 후 · 이동 둔화','오른쪽 아래 눈꽃 · 2턴간 이동 시간 +50%',1400),('lamy3-slow-expired.png','둔화 종료 · 표식 소멸','새 주문으로 냉각을 다시 쌓을 수 있음',1000)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
frames=[];full=[]
for name,title,note,delay in seq:
    im=Image.open(raw/name).convert('RGB');full.append(im)
    card=Image.new('RGB',(672,572),'#101923');d=ImageDraw.Draw(card);d.text((12,6),title,font=font,fill='#d1f5ff');d.text((12,34),note,font=small,fill='#a6cbdc')
    card.paste(im.crop((291,276,515,436)).resize((672,480),Image.Resampling.NEAREST),(0,76));frames.append(card)
frames[0].save(out/'tier3.gif',save_all=True,append_images=frames[1:],duration=[x[3] for x in seq],loop=0)
full[0].save(out/'tier3-full.gif',save_all=True,append_images=full[1:],duration=[x[3] for x in seq],loop=0)
sheet=Image.new('RGB',(672*2,572*2),'#101923')
for slot,index in enumerate([1,2,4,7]):sheet.paste(frames[index],((slot%2)*672,(slot//2)*572))
sheet.save(out/'tier3-states.png')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>라미 3성 · 취설의 마법</title><style>body{background:#101923;color:#d8efff;font:18px system-ui;max-width:960px;margin:30px auto}img{max-width:100%;image-rendering:pixelated}a{color:#95dfff}</style><h1>라미 3성 · 취설의 마법</h1><p>자동 가호. 취기20 이상에서 직접 공격 주문이 피해를 주면 적마다 냉각1. 같은 시전 다단 적중은 적당1회.</p><p>냉각3을 소모하면 추가 냉기2d(3+⌊기도술/6⌋)와2턴간 이동 시간+50%. 기도술12에서는2d5. 냉각은 마지막 부여부터6턴 유지.</p><img src="tier3.gif"><p>실제 게임의 주문3회 → 냉각1/2 → 단일 대상 결정 파열 → 둔화 → 소멸. 확대만 적용한 SDL 캡처이며, 얼음이 주변으로 튀는 그림은 광역 피해 범위가 아닙니다.</p><p><a href="tier3-full.gif">실제 전체 화면</a> · <a href="tier3-states.png">단계별 정지 화면</a></p><p>원본 도트: 내장 image_gen. 원본·프롬프트는 assets/holocrawl/lamy-chill-vfx01/에 보존. 전투 수치 변경 없음. 3성 검토 중,5성 새 연출은 아직 검토 전.</p></html>'''
(out/'index.html').write_text(html,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';shutil.copy2(p,run/'before/integrated-index.html');s=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1))
for entry in d['lamy']:
    if entry['tier']==3:entry.update(image='../lamy-chill-vfx01/tier3.gif',kind='실제 공격 주문3회 · 냉각1/2중첩 → 3중첩 결정 파열 → 2턴 이동 둔화 · 기도술12 · 단일 대상 자동 가호')
s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):]
s=s.replace('1성 확인 중','3성 확인 중').replace('지금은1성 설국의 잔을 확인합니다.','1성 승인 완료. 지금은3성 취설의 마법을 확인합니다.')
s=s.replace("if(active.id==='lamy')sel.value='0'", "if(active.id==='lamy')sel.value='1'")
p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary);shutil.copy2(binary,r/'runtime/tiles01/HoloCrawl.exe')
changed=['holo-lamy.cc','holo-visual.cc','holo-visual.h','holo-campaign-test.cc','rltiles/dc-holo-feat.txt'];patch=''
for n in changed:
    snapshot=run/'source_snapshot'/n;snapshot.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,snapshot)
    patch+=''.join(difflib.unified_diff((run/'before'/n).read_text().splitlines(True),(src/n).read_text().splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
manifest=dict(status='passed',revision='lamy-chill-vfx01',numericChanges=False,combatRevision='lamy-caster01',combatHookOnly=True,preservedExistingArtFiles=preserved_art,runtimeSha256=digest,native=read(run/'native/lamy-chill-vfx.json'),reviewStatus='tier1 approved; tier3 pending user review; tier5 art pending',frames=[dict(file=n,sha256=sha(raw/n),durationMs=ms) for n,_,_,ms in seq],sourceHashes={n:sha(src/n) for n in changed})
(run/'checkpoint-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=r/name;d=read(p);backup=run/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
    d.update(visualRevision='lamy-chill-vfx01',playBinarySha256=digest,currentVisualReviewGod='lamy',currentVisualReviewTier=3,next='Wait for user feedback on Lamy tier3 actual chill stack/shatter GIF.',lamyReviewStatus='Tier1 approved. Tier3 chill stacks/shatter/slow native VFX pending user review. Tier5 art pending.',lamyVisualValidation='analysis/native/lamy-chill-vfx01/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 라미 3성 검토 · lamy-chill-vfx01

뭇별이 라미1성을 승인하고3성 검토를 요청했다. 3성 신규 도트와 실제 주문3회 캡처 완료. 냉각1/2는적칸우측상단눈꽃,3중첩소모결정파열4프레임,이동둔화는우측하단눈꽃. 전투수치·저장형식변경없음. 기존22신기능·저장재현검사통과. 도트의48px파열은연출이며광역피해추가없음.

현재 미리보기: analysis/previews/lamy-chill-vfx01/index.html
검증: analysis/native/lamy-chill-vfx01/checkpoint-manifest.json
원본/프롬프트: assets/holocrawl/lamy-chill-vfx01/
다음은3성피드백.3성/5성자동승인하지않는다. 아래는이전인계기록이다.

'''
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','HOME_RESUME.md','START_HERE_HOME.md','HOME_SESSION.md']:
    p=r/name;backup=run/'before'/name;shutil.copy2(p,backup);p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(dict(status='passed',review=str(out/'index.html'),burstSequence=stem,runtimeSha256=digest),ensure_ascii=False))
