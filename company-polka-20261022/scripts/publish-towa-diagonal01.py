from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,hashlib,shutil,difflib
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';run=root/'analysis/native/towa-diagonal01';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/towa-support.json']:assert read(run/n)['status']=='passed',n
for n,d in read(run/'preserved-files.json').items():assert sha(src/n)==d,n
raw=run/'native/shots';out=root/'analysis/previews/towa-diagonal01';out.mkdir(exist_ok=True)
sequences={}
for distance in [1,2]:
 sequences[distance]=[f'towa-demo-{distance}-zone.png',f'towa-demo-{distance}-moved.png',f'towa-shot-{distance}-flight0.png',f'towa-shot-{distance}-flight1.png',f'towa-shot-{distance}-flight{distance}.png',f'towa-demo-{distance}-after.png']
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);frames=[];durations=[700,500,180,230,230,1600]
for i in range(6):
 panel=Image.new('RGB',(704,448),'#101923');draw=ImageDraw.Draw(panel)
 for distance,x in [(1,0),(2,352)]:
  draw.text((x+110,3),f'대각선 {distance}칸 ↗',font=font,fill='#f2d4ff')
  shot=Image.open(raw/sequences[distance][i]).convert('RGB').crop((283,244,459,452)).resize((352,416),Image.Resampling.NEAREST);panel.paste(shot,(x,32))
 frames.append(panel)
frames[0].save(out/'support-1-2-tiles.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
for distance in [1,2]:
 f=[im.crop((0 if distance==1 else 352,0,352 if distance==1 else 704,448)) for im in frames]
 f[0].save(out/f'support-{distance}-tile.gif',save_all=True,append_images=f[1:],duration=durations,loop=0)
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['towa'][1].update(image='../towa-diagonal01/support-1-2-tiles.gif',kind='왼쪽 대각선1칸 / 오른쪽 대각선2칸 · 플레이어 직접 사격 없이 적 이동으로 엄호사격 발동 → 크고 두꺼운 연보라색 악마 화살 → 실제 HP 감소·탄약4→3 · 동일 조건의 실제 전투 캡처');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
for tile in (src/'rltiles/holo').glob('fx_towa_bullet_*.png'):
 target=run/'source_snapshot/rltiles/holo'/tile.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(tile,target)
changed=['holo-campaign-test.cc'];patch=''
for n in changed:
 outpath=run/'source_snapshot'/n;outpath.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,outpath)
 patch+=''.join(difflib.unified_diff((run/'before'/n).read_text(encoding='utf-8').splitlines(True),(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='towa-diagonal01',runtimeSha256=digest,numericChanges=False,saveFormatChanged=False,allArtAndOtherSourcePreserved=True,changedHashes={n:sha(src/n) for n in changed},visual='Generated short purple devil arrow with hooked spearhead, 8 directional main-atlas tiles; native support callback',sequences=sequences,captionOutsideNativePixels=True,proof='native/towa-support.json',regression='native/validation.json',freshRestore='native/reload.json',feedback='pending'),indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=root/name;d=read(p);d.update(visualRevision='towa-diagonal01',playBinarySha256=digest,towaVisualFeedback='Tier1 approved. Tier3 actual support fire:1/2-tile enemy distance, native enemy movement, projectile overlay,HP loss/ammo4→3. Pending review.',towaVisualValidation='analysis/native/towa-diagonal01/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['towa']['pendingRevision']='towa-diagonal01';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='토와3성 실제지원사격 GIF(towa-diagonal01): 플레이어기준 적대각선1칸/2칸 상황 나란히,적실제이동→발동→크고두꺼운연보라색악마화살 전용8방향타일→HP40→30·탄약4→3. 기존계산에 렌더링콜백만추가,피해/명중/탄약/타이밍 수치변경없음. RNG불변/22신/저장검사통과. 검토중.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md']:
 p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root/'VFX_COMPANY_FEEDBACK.md';s=p.read_text(encoding='utf-8');a=s.index('## 토와');b=s.find('\n## ',a+5);b=len(s) if b<0 else b;s=s[:a]+s[a:b].replace('- 3성:','- 3성: towa-diagonal01 실제이동발동 지원사격1칸/2칸 비교GIF 추가. 실제HP/탄약소모확인. 현재검토중. ',1)+s[b:];p.write_text(s,encoding='utf-8')
print('Published native support-fire distance1/2 comparison and runtime projectile visuals.')
manifest=run/'checkpoint-manifest.json';d=read(manifest);d['projectileSize']=[24,12];d['visibility']='Thicker shaft, broad pale lavender core and larger hooked head for separation from magenta zone';manifest.write_text(json.dumps(d,indent=2),encoding='utf-8')
manifest=run/'checkpoint-manifest.json';d=read(manifest);d['changedHashes'].update({str(p.relative_to(src)).replace('\\','/'):sha(p) for p in (src/'rltiles/holo').glob('fx_towa_bullet_*.png')});d['artSlotNote']='Historical bullet slot names retained for stable atlas IDs; art is now a short purple devil arrow.';manifest.write_text(json.dumps(d,indent=2),encoding='utf-8')
