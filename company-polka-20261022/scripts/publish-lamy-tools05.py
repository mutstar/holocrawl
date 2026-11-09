from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];run=r/'analysis/native/lamy-tools05';before=r/'analysis/native/lamy-tools01/before';src=r/'engine/campaign-crawl/crawl-ref/source';out=r/'analysis/previews/lamy-tools05'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
for rel in ['capture-validation.json','native/validation.json','native/reload.json','native/lamy-caster.json','native/lamy-tools.json','native/lamy-cloud-reload.json']:
    assert read(run/rel)['status']=='passed',rel
assert read(run/'native/lamy-tools.json')['splashLaterCloudDedup']
for name in ['holo-visual.cc','holo-visual.h']:
    assert sha(src/name)==sha(r/'analysis/native/lamy-chill-vfx01/source_snapshot'/name),name
out.mkdir()
names=[('wand-stack.png','실제 불 마법봉 적중 · 냉각1'),('lamp-stack.png','실제 화염 램프 적중 · 냉각1'),('cloud-stack.png','실제 냉기 구름 첫 피해 · 냉각1')]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);cards=[]
for name,title in names:
    p=run/'native/shots'/name;im=Image.open(p).convert('RGB');shutil.copy2(p,out/name)
    card=Image.new('RGB',(672,536),'#101923');ImageDraw.Draw(card).text((12,10),title,font=font,fill='#cef4ff');card.paste(im.crop((291,276,515,436)).resize((672,480),Image.Resampling.NEAREST),(0,56));cards.append(card)
cards[0].save(out/'tools.gif',save_all=True,append_images=cards[1:],duration=1800,loop=0)
rules='''<section id="tool-rules"><h2>도구·구름 적용</h2><ul><li>취기20 이상. 직접 공격 주문뿐 아니라 피해를 주는 마법봉·화염 램프 등 도구도 대상마다 사용1회당 냉각1.</li><li>한 번의 시전·도구 사용에서 만든 구름 전체와 확산된 구름은 같은 사용으로 취급. 적마다 첫 실제 피해에만 냉각1. 같은 구름 안에서 이동하거나 계속 맞아도 추가 중첩 없음.</li><li>같은 사용의 직접 타격·구름·연회 폭발은 같은 적에게 냉각을 중복으로 주지 않음. 별도로 다시 사용해 만든 구름은 새 중첩 가능.</li><li>면역·피해0·아군/소환수·신 권능·독 자체의 후속 지속 피해는 제외. 업데이트 전에 생성된 출처 기록 없는 구름은 소급 적용하지 않음.</li><li>3중첩 피해·둔화와 도트는 그대로. 1성 주문 위력 보너스는 기존 주문 대상이며 도구 위력을 올리는 효과는 추가하지 않음.</li><li>5성 연회도 새 도구·구름 적중 판정을 공유. 같은 구름 사용 전체에서 눈꽃 폭발은 최대1회이며 기존10aut 제한 유지.</li></ul><p>실제 불 마법봉·화염 램프·냉기 구름 캡처:</p><img src="../lamy-tools05/tools.gif"><p>구름 확산·칸 이동·별도 재사용·면역·저장 후 새 프로세스 재현과22신 회귀 검사 통과. 캠페인 승률 검증은 아님.</p></section>'''
page=r/'analysis/previews/lamy-chill-vfx01/index.html';shutil.copy2(page,run/'before-chill-index.html');s=page.read_text(encoding='utf-8').replace('직접 공격 주문이 피해를 주면 적마다 냉각1. 같은 시전 다단 적중은 적당1회.','공격 주문·피해 도구·구름 첫 피해로 적마다 냉각1. 같은 사용의 다단 적중과 구름은 적당1회.')
s=s.replace('</body>',rules+'</body>') if '</body>' in s else s+rules
page.write_text(s,encoding='utf-8')
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>라미 도구·구름 적용</title><style>body{background:#101923;color:#d8efff;font:18px system-ui;max-width:900px;margin:30px auto;line-height:1.7}img{max-width:100%;image-rendering:pixelated}</style>'+rules,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';shutil.copy2(p,run/'before-integrated-index.html');s=p.read_text(encoding='utf-8');m=re.search(r'const lamySkillInfo=(.*?);\s*function updateSkillInfo',s);d=json.loads(m.group(1))
d['3']['effect']='취기20 이상에서 공격 주문·피해 도구로 적마다 사용당 냉각1. 같은 사용에서 만든 구름 전체와 확산 구름은 적마다 첫 실제 피해에만1개. 직접 타격·구름 중복 없음.3중첩 소모 시 추가 냉기 피해와2턴간 이동 시간+50%.'
d['3']['scaling']+=' 도구 충전·원래 비용 유지. 구름 지속 피해 반복으로는 쌓이지 않고 별도 재사용은 가능.면역·피해0·소환수·신 권능·독 후속 지속 피해 제외.'
d['5']['effect']='연회 동안 취기20으로 취급. 공격 주문·피해 도구·출처가 기록된 구름의 첫 적중에 눈꽃 폭발.사용당1회·10aut당1회.같은 구름 사용 전체는 최대1폭발.주변1칸 적에게 피해와냉각,동일사용의직접타격·구름·폭발은적당냉각최대1.'
s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
p=r/'scripts/god-art-skills.json';shutil.copy2(p,run/'before-god-art-skills.json');d=read(p);d['lamy']=[['설국의 잔','사용','취기+40; 취기20 이상 공격 주문 위력 증가,과음 EV−3','1성 승인 유지. 도구 위력 증가 효과는 아님.'],['취설의 마법','자동','공격 주문·피해 도구·같은 사용 구름의 첫 피해로 냉각1;3중첩 소모 냉기 피해·이동 둔화','사용당·적당1중첩.구름확산/이동/반복틱 중복 없음.'],['눈의 연회','사용','취기 소모; 공격 주문·피해 도구·구름 최초 피해에 눈꽃 폭발','기존 수치 유지.같은 구름 사용 최대1폭발.새5성연출 검토 전.']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary);shutil.copy2(binary,r/'runtime/tiles01/HoloCrawl.exe')
changed=['holo-lamy.h','holo-lamy.cc','holo-campaign.cc','spl-cast.cc','evoke.cc','cloud.cc','holo-campaign-test.cc'];patch=''
for n in changed:
    p=run/'source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
    patch+=''.join(difflib.unified_diff((before/n).read_text().splitlines(True),(src/n).read_text().splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
manifest=dict(status='passed',revision='lamy-tools05',native=read(run/'native/lamy-tools.json'),cloudReload=read(run/'native/lamy-cloud-reload.json'),runtimeSha256=digest,visualsUnchanged=True,tier1ScalingUnchanged=True,nativeSaveSchemaChanged=False,saveMetadata='Native serialized per-level env.properties: use ids, cells, target MID claims and banquet use claims',priorFailuresPreserved=['lamy-tools01','lamy-tools02'],supersedes='lamy-tools03; adds splash/later-cloud dedup; lamy-tools04 build-only',sourceHashes={n:sha(src/n) for n in changed},scope='Native tool/cloud feature, save, and 22-god regression checks; not campaign winrate')
(run/'checkpoint-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name
    if not p.exists():continue
    backup=run/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup);d=read(p)
    d.update(combatRevision='lamy-tools05',playBinarySha256=digest,lamyToolsValidation='analysis/native/lamy-tools05/checkpoint-manifest.json',lamyReviewStatus='Tier1 approved; tier3 tool/cloud extension implemented and native-tested; tier3 visual feedback pending; tier5 art pending',next='Wait for Lamy tier3 feedback; do not automatically approve or advance to tier5.')
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['lamy'].update(combatRevision='lamy-tools05',tier3ToolSupport=True,pending=[3,5],approved=[1]);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# 라미 도구·구름 지원 · lamy-tools05

뭇별 승인에 따라 피해 도구 사용과 구름을 냉각에 포함했다. 같은 사용의 직접 피해·구름 전체·확산·5성 폭발은 적마다 냉각1. 같은 구름 반복/이동으로 중첩 불가, 별도 재사용은 새 사용. 5성은 같은 구름 사용 전체 최대1회와기존10aut제한. 피해0/면역/소환수/신권능/독후속DoT제외. 이전미기록구름소급없음. 1성위력증가대상/수치와기존3성도트유지. 도구충전/비용유지. 네이티브저장형식변경없이레벨properties로출처/소비대상저장.

실제불마법봉·화염램프,구름이동·확산·재사용·3중첩폭발·5성중복차단·면역/비대상·새프로세스구름재현·기존22신검사통과. 실패01/02와GDB로그보존.03은당시검사통과이나인접폭발후구름중복검사를추가한05로대체.04는빌드만완료. 캠페인승률재검증아님.

검증: analysis/native/lamy-tools05/checkpoint-manifest.json
검토: analysis/previews/lamy-chill-vfx01/index.html
도구증거: analysis/previews/lamy-tools05/index.html
라미1성승인.3성연출피드백대기,5성새연출검토전.아래는이전기록.

'''
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','HOME_RESUME.md','START_HERE_HOME.md','HOME_SESSION.md','HOLOCRAWL_DESIGN.md']:
    p=r/name;backup=run/'before'/name;shutil.copy2(p,backup);p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
(run/'RESULTS_KO.md').write_text(note,encoding='utf-8')
print(json.dumps(dict(status='passed',runtimeSha256=digest,review=str(page)),ensure_ascii=False))
