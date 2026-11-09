from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='lui-attack04';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source';o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(b/'capture-validation.json')['status']=='passed';assert read(b/'native/reload.json')['status']=='passed'
for name,digest in read(b/'preserved-art.json').items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==digest,name
shots=b/'native/shots';result=read(shots/'lui-attack-result.json');assert result['damage']>0 and result['piety']==30
metas=[p for p in shots.glob('lui-attack-*.json') if re.fullmatch(r'lui-attack-\d+',p.stem) and p.stat().st_mtime<=(shots/'lui-attack-result.json').stat().st_mtime and read(p)['hit']]
meta=max(metas,key=lambda p:int(p.stem.split('-')[-1]));stem=meta.stem
o.mkdir(parents=True,exist_ok=True)
files=[shots/f'{stem}-ready.png']+[shots/f'{stem}-frame{i}.png' for i in range(3)]+[shots/'lui-attack-result.png']
frames=[Image.open(p).convert('RGB').crop((275,244,499,420)).resize((448,352),Image.Resampling.NEAREST) for p in files]
assert ImageChops.difference(frames[0],frames[1]).getbbox(),'Attack pose not visible'
frames[0].save(o/'attack.gif',save_all=True,append_images=frames[1:],duration=[240,110,150,130,800],loop=0,optimize=False)
for name in ['altar','god']:shutil.copy2(s/f'rltiles/holo/{name}_lui.png',o/('altar.png' if name=='altar' else 'portrait.png'))
p=r/'analysis/previews/lui-review01/index.html';page=p.read_text(encoding='utf-8');shutil.copy2(p,o/'previous-summon.html')
page=page.replace('소환 직후 실제 필드','일반 공격 · 실제 필드').replace('../lui-ganmo-sharp01/tier1-0.gif','../lui-attack04/attack.gif').replace('루이 1성 실제 매 소환 직후','루이 간모 실제 근접 공격').replace('왼쪽 위 새가 실제 아군 매입니다. 선택한 B안의 날카로운 눈매·흰 깃·몸에 붙는 망토입니다. 캐릭터 옆 작은 문양은 권속 활성 표시입니다.','플레이어 오른쪽 간모가 적을 근접 공격합니다. 공격 자세 → 명중 표시 → 서 있는 자세로 복귀합니다. 빗나가면 타격 표시는 생략됩니다.').replace('캐릭터 주위 빈 바닥에 소환됩니다. 영상은 실제 시전 이펙트와 소환 직후 상태입니다.',f'실제 일반 공격으로 체력 {result["damage"]} 감소를 확인했습니다. 공격당 행동 시간·피해 계산은 유지합니다.').replace('소환수·활성 표식·신앙 문양에 날카로운 B안을 적용했습니다.','날카로운 B안에 일반 근접 공격 모션을 연결했습니다.')
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);data=json.loads(m[1]);data['lui']=[dict(tier=1,option=0,title='간모 일반 공격',image=f'../{rev}/attack.gif',kind='실제 근접 공격 · 공격 자세/명중/복귀')];txt=txt[:m.start(1)]+json.dumps(data,ensure_ascii=False)+txt[m.end(1):];txt=txt.replace('../lui-ganmo-sharp01/tier1-0.gif',f'../{rev}/attack.gif');p.write_text(txt,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(currentVisualReviewGod='lui',currentVisualReviewTier=1,currentVisualReview='analysis/previews/lui-review01/index.html#tier1',visualRevision=rev,playBinarySha256=digest,luiAttackRevision=rev)
 if 'tierApprovals' in d:d['tierApprovals']['lui'].update(pendingRevision=rev,tier1Revision=rev,visualSourceRevision=rev,feedback='B안 선택. 일반 근접 공격 모션 추가 및 실제 공격 캡처 검토 대기.')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for p in (b/'before').rglob('*'):
 if p.is_file():diff.extend(difflib.unified_diff(p.read_text().splitlines(True),(s/p.relative_to(b/'before')).read_text().splitlines(True),fromfile='before/'+str(p.relative_to(b/'before')),tofile='after/'+str(p.relative_to(b/'before'))))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,nativeAttackStem=stem,attackResult=result,combatNumbersChanged=False,saveFormatChanged=False,standingAndOtherGodArtPreserved=True,visualRngStateGuard=True,validation=read(b/'capture-validation.json')),indent=2))
note='# 루이 일반 공격 모션 / lui-attack04\n\nB안 서 있는 도트 유지. 일반 근접 공격 시 앞쪽으로 숙인 전용 공격 자세, 명중 시 작은 타격 표시, 복귀. 좌우 반전 도트 포함. 공격 시도 후 판정 결과에 맞춰 화면만 재생하며 시간·피해·RNG 변경 없음 검사. native 테스트 기도술/신앙 1성 실제 공격 및 체력 감소 확인, GIF attack.gif. 현재 루이1성 공격 모션 검토.\n\n'
for name in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md','CURRENT_WORKSPACE.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Native attack animation published:',stem,result)

