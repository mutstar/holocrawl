from pathlib import Path
from PIL import Image
import hashlib,json,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='lui-ganmo-sharp01';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
assert read(b/'native/reload.json')['status']=='passed'
for n,h in read(b/'preserved-files.json').items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
o=r/'analysis/previews'/rev;o.mkdir(parents=True,exist_ok=True);shots=b/'native/shots'
stems=sorted([p.stem.removesuffix('-frame0') for p in shots.glob('lui-tier1-option0-*-frame0.png')],key=lambda n:int(n.split('-')[-1]));assert len(stems)>=2
for i,stem in enumerate(stems[:2]):
 files=[shots/f'{stem}-frame0.png',shots/f'{stem}-frame1.png',shots/f'{stem}-state.png'];frames=[Image.open(p).convert('RGB').crop((275,244,499,420)).resize((448,352),Image.Resampling.NEAREST) for p in files]
 frames[0].save(o/f'tier1-{i}.gif',save_all=True,append_images=frames[1:],duration=[450,450,900],loop=0,optimize=False)
for n in ['altar','god']:shutil.copy2(s/f'rltiles/holo/{n}_lui.png',o/('altar.png' if n=='altar' else 'portrait.png'))
p=r/'analysis/previews/lui-review01/index.html';page=(r/'analysis/previews/lui-ganmo-compare01/previous-review.html').read_text(encoding='utf-8').replace('../lui-ganmo02/','../lui-ganmo-sharp01/').replace('까마귀','매').replace('검은 날개의 권속','매의 권속').replace('src="tier1-','src="../lui-ganmo01/tier1-').replace('루이 전투 수치·기존 도트 변경 없음.','전투 수치는 유지하고 소환수·활성 표식·제단·신앙 문양을 매로 교체했습니다.')
page=page.replace(' 갈색 날개·밝은 가슴·굽은 부리로 구분됩니다.','').replace('소환수·활성 표식·제단·신앙 문양을 매로 교체했습니다.','소환수·활성 표식·제단·신앙 문양을 간모 디자인으로 교체했습니다.')
page=page.replace('소환수·활성 표식·제단·신앙 문양을 간모 디자인으로 교체했습니다.','소환수·활성 표식·신앙 문양에 날카로운 B안을 적용했습니다.').replace('영상은 시전 이펙트 두 프레임과 소환 상태입니다.','영상은 실제 시전 이펙트와 소환 직후 상태입니다.')
page=page.replace('간모의 금색 눈·흰 털깃·자주색 망토로 구분됩니다.','선택한 B안의 날카로운 눈매·흰 깃·몸에 붙는 망토입니다.')
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);d=json.loads(m[1]);d['lui']=[dict(tier=1,option=0,title='매의 권속',image=f'../{rev}/tier1-0.gif',kind='실제 매 소환 직후 · B 도트/활성 표시')];txt=txt[:m.start(1)]+json.dumps(d,ensure_ascii=False)+txt[m.end(1):]
article=f'<article id="lui" data-god="lui"><h2>루이 <small>1성 · 간모 도트 검토 중</small></h2><select onchange="choose(this)"><option value="0">1성 · 매의 권속</option></select><p class="scene-note">실제 아군 매 소환 직후</p><img class="scene" src="../{rev}/tier1-0.gif"><p>MP3·신앙0·1턴.매1마리.기본2마리/신앙75부터3마리. 최소 기도술 없음·신앙30 해금.</p><p><a href="../lui-review01/index.html#tier1">매·제단·상세 수치 보기</a></p><label>피드백<textarea data-feedback="lui"></textarea></label></article>'
txt,n=re.subn(r'<article id="lui".*?</article>',lambda _:article,txt,count=1,flags=re.S);assert n==1;p.write_text(txt,encoding='utf-8')
p=r/'scripts/god-art-skills.json';d=read(p);d['lui'][0][0]='매의 권속';d['lui'][2][0]='매의 군세'
for row in d['lui']:
 for i,x in enumerate(row):row[i]=x.replace('../lui-ganmo01/','../lui-ganmo02/').replace('까마귀','매')
d['lui'][0][3]='매 소환수 도트·작은 매 활성 표시·매 문양 제단';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
p=r/'VFX_DRAFT_STATUS.json';d=read(p);d['tierApprovals']['lui'].update(pendingRevision=rev,tier1Revision=rev,visualSourceRevision=rev,feedback='현실 매 대신 공식 간모 디자인으로 교체 요청. 작게 찌그러지는 문제: alpha32 초과 실루엣 기준 자르기 후30px에 배치.');d.update(currentGod='lui',next='Review Lui hawk tier1 at analysis/previews/lui-review01/index.html#tier1');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,luiConceptRevision=rev,currentVisualReviewGod='lui',currentVisualReviewTier=1,currentVisualReview='analysis/previews/lui-review01/index.html#tier1',next='Review Lui hawk tier1: native summon, small buff mark and altar.')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 루이 B안 실제 적용 / lui-ganmo-sharp01\n\n루이 1성 매의 권속: 사용자가 선택한 B안: 날카로운 눈매·흰 깃·몸에 붙는 자주색 망토. 30px 이하 소환수, 양 프레임 같은 승인 자세 사용, 머리 옆12×14px 활성 표식. 신앙 문양/작은 표식 B안 적용. 제단은 기존 간모 제단 유지. 기존 매 콘셉트의 메뉴·설명·징벌 및 구 이름 호환을 유지. 이번 변경은 도트만 교체. 저장 포맷·내부ID·전투 수치 유지. 코요리 확정본 및 다른 신 도트 보존. B안 선택 완료, 실제 필드 확인 대기. 공식 참고: assets/holocrawl/lui-ganmo02/official-reference.png. 생성 프롬프트: 같은 폴더 generation.json.\n\n'
for name in ['CONTINUE_HERE.md','VFX_COMPANY_FEEDBACK.md','CURRENT_WORKSPACE.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
diff=[];changed={}
for p in (b/'before').rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(b/'before');after=s/rel;changed[str(rel)]=hashlib.sha256(after.read_bytes()).hexdigest()
 if p.suffix in ['.cc','.h','.txt']:diff.extend(difflib.unified_diff(p.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatNumbersChanged=False,saveFormatChanged=False,legacyNamesSupported=True,newNameAndLegacyMigrationChecked=True,koyoriAndOtherGodArtPreserved=True,visualApproved=False,nativeSourceStems=stems,changed=changed,validation=v),indent=2),encoding='utf-8');print('Lui hawk assets, native names and fresh field preview published.')




for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=r/name;d=read(p);d['luiPendingVariants']=dict(revision='lui-ganmo-compare01',selected='B',nativeApplied=True,appliedRevision=rev);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=read(b/'checkpoint-manifest.json');manifest.update(selectedVariant='B',spriteMatchesChosenTile=hashlib.sha256((s/'rltiles/holo/raven.png').read_bytes()).hexdigest()==hashlib.sha256((r/'assets/holocrawl/lui-ganmo-compare01/b-tile.png').read_bytes()).hexdigest(),altarPreserved=True,bodyFrames='approved standing pose');(b/'checkpoint-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
