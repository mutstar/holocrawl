from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-caster01';out=r/'analysis/previews/lamy-caster01';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['capture-validation.json','native/validation.json','native/reload.json','native/lamy-caster.json','native/lamy-hud.json']:assert read(run/n)['status']=='passed',n
proof=read(run/'native/lamy-caster.json');assert proof['baseSpellPower']>0 and proof['buffSpellPower']>proof['baseSpellPower']
for n,h in read(run/'preserved-files.json').items():assert sha(src/n)==h,n
out.mkdir(exist_ok=True);raw=run/'native/shots';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
seq=[('before','음주 전 · 취기0 · 주문 강화 없음',1200),('cast0','설국의 잔 · MP2 / 신앙1 / 1턴',230),('cast1','설국의 잔 시전',230),('proper','한잔 · 취기40 · 주문 위력+16%',2000),('over','1턴 후 한잔 더 · 취기79 · EV-3',2200)]
frames=[]
for key,label,delay in seq:
 im=Image.open(raw/f'lamy1-{key}.png').convert('RGB');shutil.copy2(raw/f'lamy1-{key}.png',out/f'{key}.png');card=Image.new('RGB',(640,288),'#101923');ImageDraw.Draw(card).text((10,5),label,font=font,fill='#c0efff');card.paste(im.crop((259,228,483,452)),(0,48));card.paste(im.crop((736,0,1152,240)),(224,40));frames.append(card)
frames[0].save(out/'tier1.gif',save_all=True,append_images=frames[1:],duration=[x[2] for x in seq],loop=0)
comparison=Image.new('RGB',(640,864),'#101923')
for row,i in enumerate([0,3,4]):comparison.paste(frames[i],(0,row*288))
comparison.save(out/'tier1-states.png')
infos={
 1:dict(cost='MP2 · 신앙1 · 시전1턴 · 취기+40(최대100) · 연회 중 음주 불가',effect='취기20 이상이면 직접 공격 주문의 주문 위력이 증가합니다. 취기20~69는 적정 취기,70 이상은 과음으로 EV−3입니다. 과음해도 위력은 더 오르지 않으며,명중·주문 실패율 페널티는 없습니다.',scaling='주문 위력 +[12+⌊기도술/3⌋]%. 기도술12면+16%입니다. 주문별 위력 상한은 유지되며 피해+16%와는 다릅니다. 취기는 매1턴1씩 줄어듭니다. 시전 직후40,행동 시간이 흐르면39가 됩니다. 소환·구름·지속 피해 주문은 강화 대상에서 제외합니다.'),
 3:dict(cost='자동 가호 · 추가 MP·신앙·행동 시간 소모 없음 · 기존 서리의 숨결 사용 기술은 제거',effect='취기20 이상에서 직접 공격 주문이 피해를 주면 적마다 냉각1을 쌓습니다. 같은 주문의 다단 적중은 적당1회입니다. 냉각3을 모으면 소모해 추가 냉기 피해와2턴간 이동 시간+50%를 줍니다.',scaling='냉각은 마지막 부여부터6턴 유지. 추가 피해2d(3+⌊기도술/6⌋),기도술12면2d5입니다. 냉기 저항 적용. 이동 방해는 공격·주문 속도에 영향을 주지 않습니다. 추가 피해가 라미 효과를 재발동시키지 않습니다.'),
 5:dict(cost='취기40 이상 필요 · MP6 · 신앙12 · 시전1턴 · 취기 전부 소모 · 종료 후 재사용 대기15턴',effect='연회 동안 취기20으로 취급해1·3성 효과를 유지하고 과음 EV−3를 해소합니다. 직접 공격 주문이 처음 적중한 곳에 눈꽃 폭발이 발생합니다. 주문당1회·10aut당1회,주변1칸 적에게 피해와 냉각을 줍니다.',scaling='시전 후6+⌊기도술/6⌋턴,기도술12면8턴. 중심 피해2d(5+⌊기도술/3⌋),기도술12면2d9. 주변은 같은 굴림의50%(버림). 동일 주문의 직접 적중과 폭발은 적당 냉각 최대1. 연쇄 재발동 없음. 종료 후 취기0.')}
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8');shutil.copy2(p,run/'before/integrated-index.html');m=re.search(r'const data=(.*?);function choose',s);d=json.loads(m.group(1));old=d['lamy'];d['lamy']=[dict(tier=1,option=0,title='설국의 잔',image='../lamy-caster01/tier1.gif',kind='마법 개편 적용 · 실제1성 음주 전→시전→취기40/P+16%→한잔 추가/취기79/EV−3 · 기도술12 · P는주문위력이며피해배율과다름'),dict(tier=3,option=0,title='취설의 마법',image=old[-2]['image'],kind='3성은자동냉각가호로개편완료. 이 이미지는구버전숨결도트로,개편후3성연출은다음검토대상'),dict(tier=5,option=0,title='눈의 연회',image=old[-1]['image'],kind='5성은주문적중눈꽃폭발로개편완료. 현재이미지는구버전시전도트이며개편후실제폭발연출은다음검토대상')];s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False)+s[m.end(1):]
s=s.replace('function updateSkillInfo(article,entry){','const lamySkillInfo='+json.dumps(infos,ensure_ascii=False)+';\nfunction updateSkillInfo(article,entry){',1).replace("article.dataset.god==='towa'?towaSkillInfo[tier]:null","article.dataset.god==='towa'?towaSkillInfo[tier]:article.dataset.god==='lamy'?lamySkillInfo[tier]:null")
s=s.replace('라미 <small>기존 초안 · 마법 중심 개편 검토</small>','라미 <small>마법 개편 적용 · 1성 확인 중</small>').replace('지금은 라미의 마법 중심 개편 방향을 확인합니다.','라미 마법 개편 적용 완료. 지금은1성 설국의 잔을 확인합니다.')
a=s.index('<article id="lamy"');b=s.index('</article>',a);part=s[a:b].replace('3성 · 서리의 숨결','3성 · 취설의 마법').replace('술로 취기 축적; 적정 취기에서 냉기 공격 보너스','음주로 공격 주문 위력 증가; 과음 시EV−3').replace('전방 부채꼴 냉기 공격·냉각 축적','직접 공격 주문으로 냉각 축적;3중첩 시 냉기 피해·이동 방해').replace('취기 소모; 주변 적에게 주기적 냉기 피해·냉각','취기 소모; 직접 공격 주문 적중 시 눈꽃 폭발').replace('네 상태의 실제 게임 전체 화면 보기','이전 HUD 네 상태 전체 화면(구버전 수치)');s=s[:a]+part+s[b:];p.write_text(s,encoding='utf-8')
binary=run/'capture-engine.exe';digest=sha(binary).upper();shutil.copy2(binary,r/'runtime/tiles01/HoloCrawl.exe');patch='';changed=read(run/'changed-files.json')
for n in changed:
 target=run/'source_snapshot'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/n,target);before=run/'before'/n;patch+=''.join(difflib.unified_diff(before.read_text(encoding='utf-8').splitlines(True) if before.exists() else [],(src/n).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+n,tofile='after/'+n))
(run/'source.patch').write_text(patch,encoding='utf-8');(run/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision='lamy-caster01',numericChanges=True,saveFormatChanged=False,allArtAndOtherSourcePreserved=True,runtimeSha256=digest,proof=proof,changedHashes={n:sha(src/n) for n in changed},visualFeedback='Tier1 pending; tier3/5 mechanics applied, art pending',scope='Native feature/damage/save regressions; no campaign winrate claim'),ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
 p=r/name;d=read(p);d.update(visualRevision='lamy-caster01',combatRevision='lamy-caster01',playBinarySha256=digest,currentVisualReviewGod='lamy',currentVisualReviewTier=1,lamyReviewStatus='Caster mechanics implemented and verified. Reviewing tier1 drink HUD/VFX. Tier3 passive and tier5 spell burst mechanics applied; art review pending.',lamyCombatValidation='analysis/native/lamy-caster01/checkpoint-manifest.json');d['buildRoleDirection']['implemented']=['lamy'];d['buildRoleDirection']['status']='Lamy caster mechanics implemented; Sophia/Koyori/Vivi remain accepted directions';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['lamy']=dict(approved=[],pending=[1,3,5],combatRevision='lamy-caster01',pendingRevision='lamy-caster01');d['buildRoleDirection']['implemented']=['lamy'];d['next']='Review Lamy tier1 drink, then passive chill and spell burst visuals';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='라미 마법 개편 적용(lamy-caster01): 음주MP2/신앙1/+40,취기1/턴감소,20~69적정/70+EV−3,공격주문위력12+I/3%,상한유지. 3성자동냉각3중첩2d(3+I/6)·이동150%2턴. 5성취기40이상전부소모/MP6신앙12/1턴/시전후6+I/6턴,주문첫적중중심2d(5+I/3)·주변절반/1시전·10aut당1폭발,냉각중복없음/종료후15턴쿨. 구명중/실패/물리보너스/rC/자동장판제거. 기존신앙수급유지(적정경계69반영). 실제주문위력·광역시전/다단/제외경로/냉각·폭발/저장/22신검사통과. 모든도트보존.1성음주GIF검토중,3·5성개편연출미검토.\n\n'
for name in ['CURRENT_WORKSPACE.md','CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md','BALANCE_WORKPLAN.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Published caster mechanics and native tier1 drink preview.',proof)
