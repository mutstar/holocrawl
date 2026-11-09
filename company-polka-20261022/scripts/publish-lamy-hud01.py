from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,shutil,hashlib,difflib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-hud01';out=r/'analysis/previews/lamy-hud01';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/lamy-hud.json']:assert read(run/n)['status']=='passed',n
for n,h in read(run/'preserved-files.json').items():assert sha(src/n)==h,n
out.mkdir();raw=run/'native/shots';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
states=[('sober','맨정신 · 취기12/100','#c0c0c0'),('tipsy','적정 취기 · 취기40/100','#60ffff'),('drunk','과음 · 취기80/100','#ff7777'),('banquet','눈의 연회 · 남은6턴','#ff80ff')];cards=[]
for name,label,colour in states:
 im=Image.open(raw/f'lamy-{name}.png').convert('RGB');shutil.copy2(raw/f'lamy-{name}.png',out/f'{name}.png')
 card=Image.new('RGB',(640,288),'#101923');ImageDraw.Draw(card).text((12,5),label,font=font,fill=colour)
 card.paste(im.crop((259,228,483,452)),(0,48));card.paste(im.crop((736,0,1152,240)),(224,40));cards.append(card)
combined=Image.new('RGB',(1280,576),'#101923')
for i,im in enumerate(cards):combined.paste(im,((i%2)*640,(i//2)*288))
combined.save(out/'four-states.png')
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>라미 취기 상태 실제 게임 캡처</title><style>body{background:#101923;color:#ddd;font:18px sans-serif;margin:20px}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{max-width:100%;image-rendering:pixelated}a{color:#bff}</style><h1>라미 취기 상태 표시 · 실제 게임 UI</h1><p>예시 상태값을 설정한 네이티브 게임 캡처입니다. 기존 전투 규칙은 유지하며 새 마법 개편·EV−3는 아직 미적용입니다. 영어 표시는 현재 게임 폰트에 맞췄습니다.</p><main>'+''.join(f'<section><h2 style="color:{c}">{label}</h2><a href="{n}.png"><img src="{n}.png" alt="{label} 실제 게임 전체 화면"></a></section>' for n,label,c in states)+'</main>',encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));d['lamy'][0].update(image='../lamy-hud01/four-states.png',kind='실제 인게임 HUD 4종 · 왼쪽 위 맨정신12 / 오른쪽 위 적정40 / 왼쪽 아래 과음80 / 오른쪽 아래 연회6턴 · 예시 상태값으로 캡처,새 마법 개편·EV−3는 미적용');s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):]
a=s.index('<article id="lamy"');b=s.index('</article>',a);s=s[:b]+'<p><a href="../lamy-hud01/index.html" target="_blank">네 상태의 실제 게임 전체 화면 보기</a></p>'+s[b:];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,r/'runtime/tiles01/HoloCrawl.exe')
changed=['status.h','status.cc','holo-campaign.cc','holo-campaign-test.cc'];patch=''
for n in changed:
 p=run/'source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,p);patch+=''.join(difflib.unified_diff((run/'before'/n).read_text(encoding='utf-8').splitlines(True),(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8')
(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='lamy-hud01',runtimeSha256=digest,combatRedesignApplied=False,numericChanges=False,saveFormatChanged=False,allArtPreserved=True,existingThresholds='20..60 Tipsy; >60 Drunk, pending caster redesign',proof=read(run/'native/lamy-hud.json'),changedHashes={n:sha(src/n) for n in changed}),indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=r/name;d=read(p);d.update(visualRevision='lamy-hud01',playBinarySha256=digest,lamyHudRevision='lamy-hud01',lamyReviewStatus='Native HUD shows current intoxication/100 and banquet remaining turns. Four sample-state captures. Proposed caster mechanics and EV−3 not applied.');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['lamyHudRevision']='lamy-hud01';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='ラミ/라미 HUD표시(lamy-hud01): 전투화면상태줄 Sober12/100·Tipsy40/100·Drunk80/100·Banquet6t 실제4종캡처. 연회카운트다운/타신숨김/렌더링상태불변/22신/저장검사통과. 기존취기경계20~60/>60사용,새캐스터개편70경계와EV−3는아직미적용.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published native four-state Lamy HUD examples.')
