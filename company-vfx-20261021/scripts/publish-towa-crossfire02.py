from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/towa-crossfire02';out=r/'analysis/previews/towa-crossfire02';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/towa-crossfire.json']:assert read(run/n)['status']=='passed',n
for n,h in read(run/'preserved-files.json').items():assert sha(src/n)==h,n
proof=read(run/'native/towa-crossfire.json');assert [v['ammoAfter'] for v in proof['volleys']]==[6,4]
out.mkdir(exist_ok=True);raw=run/'native/shots';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
sequence=[('crossfire-before.png','3성 엄호 구역',600),('crossfire-cast0.png','5성 · 악마의 교차포화',260),('crossfire-cast1.png','작은 날개 + 교차한 화살',280),('crossfire-active.png','강화 완료 · 탄약 8발',600)]
for volley in range(2):
 for shot in range(2):
  index=volley*2+shot+1
  for f in range(3):sequence.append((f'towa-shot-{index}-flight{f}.png',f'{volley+1}턴째 · 지원사격 {shot+1}/2',180))
 sequence.append((f'crossfire-after{volley}.png',f'{volley+1}턴째 완료 · 탄약 {8-volley*2}→{6-volley*2}발',1100))
frames=[]
for name,label,duration in sequence:
 frame=Image.new('RGB',(352,448),'#101923');ImageDraw.Draw(frame).text((12,5),label,font=font,fill='#f2dcff');frame.paste(Image.open(raw/name).convert('RGB').crop((283,244,459,452)).resize((352,416),Image.Resampling.NEAREST),(0,32));frames.append(frame)
frames[0].save(out/'crossfire.gif',save_all=True,append_images=frames[1:],duration=[x[2] for x in sequence],loop=0)
frames[1].save(out/'cast.gif',save_all=True,append_images=[frames[2],frames[3]],duration=[280,280,1000],loop=0)
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['towa'][2].update(image='../towa-crossfire02/crossfire.gif',kind='5성 시전 문양: 밝은 보라색·폭44~48픽셀 · 5성 전용 날개 달린 쌍꼬리 화살 · 실제 교차포화: 적 둘의 이동으로 턴당2발×2턴 발사 → HP 감소·탄약8→6→4 · 시전 장식과 실제 사격을 이어서 캡처');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):];s=s.replace('화면은 기존5성 시전 초안이며,8발 연속 발사 전체를 보여주는 GIF는 아닙니다.','GIF는 실제5성 시전 후,적 둘의 이동으로 턴당2발씩2턴 동안 총4발을 쏘는 장면입니다. 탄약은8→6→4로 감소합니다.');p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,r/'runtime/tiles01/HoloCrawl.exe')
changed=['holo-visual.cc','rltiles/dc-holo-main.txt']+[f'rltiles/holo/fx_towa_crossfire_{n}.png' for n in ['e','ne','n','nw','w','sw','s','se']]
for n in changed:
 p=run/'source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p)
patch=''.join(difflib.unified_diff((run/'before/holo-visual.cc').read_text(encoding='utf-8').splitlines(True),(src/'holo-visual.cc').read_text(encoding='utf-8').splitlines(True),fromfile='before/holo-visual.cc',tofile='after/holo-visual.cc'));(run/'source.patch').write_text(patch,encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='towa-crossfire02',runtimeSha256=digest,numericChanges=False,saveFormatChanged=False,otherArtAndGameplaySourcePreserved=True,changedHashes={n:sha(src/n) for n in changed},crestWidths=[44,48],proof=proof,sequence=sequence,feedback='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=r/name;d=read(p);d.update(visualRevision='towa-crossfire02',playBinarySha256=digest,currentVisualReviewGod='towa',currentVisualReviewTier=5,towaVisualFeedback='Tier1/3 approved. Tier5 distinct winged bolt with twin lavender tail; real two shots per turn,8→6→4 ammo. Pending.',towaVisualValidation='analysis/native/towa-crossfire02/checkpoint-manifest.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['towa']['pendingRevision']='towa-crossfire02';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='토와5성검토(towa-crossfire02): 5성전용26x16px 날개달린 쌍꼬리투사체추가.3성승인화살유지.밝은연보라44/48px 시전문양유지. 실제적둘이동→턴당2발×2턴→탄약8→6→4와HP감소 캡처. 1·3성승인유지,5성미승인. 수치·저장형식변경없음,22신/저장/렌더링RNG검사통과.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published smaller lavender tier5 cast and native two-target crossfire GIF.')
