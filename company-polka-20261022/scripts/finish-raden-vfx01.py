from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='raden-vfx01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev;s=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
for option in [0,1,2]:
 files=[b/f'native/shots/raden1-{option}-frame{f}.png' for f in range(2)]+[b/f'native/shots/raden1-{option}-active.png']
 frames=[Image.open(p).convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for p in files]
 frames[0].save(o/f'exhibit{option}.gif',save_all=True,append_images=frames[1:],duration=[450,450,1400],loop=0,optimize=False)
 if option==1:frames[2].save(o/'field.png')
p=r/'analysis/previews/raden-review01/index.html';page=p.read_text(encoding='utf-8')
page=page.replace('src="exhibit1.gif"','src="../raden-vfx01/exhibit1.gif"').replace('src="exhibit2.gif"','src="../raden-vfx01/exhibit2.gif"')
page=page.replace('기존 엔진에서 캡처한 시전 직후 두 프레임입니다. 새로 그린 효과나 전투 재현 영상은 아닙니다.','밝은 옥색 속과 금빛 테두리의 14×14px 전시 문양. 실제 게임에서 시전 직후와 유지 상태를 다시 캡처했습니다.')
page=page.replace('기존 실제 게임 캡처:','새 실제 게임 캡처:').replace('현재 실제 게임 초안','밝고 뚜렷하게 수정')
page=page.replace('현재 1성 표식은 세 작품을 개별 도트로 구분하지 않습니다. 이번에는 1성부터 외형을 검토합니다.','세 작품은 현재 공통 전시 문양을 사용합니다. 머리 오른쪽 위에 표시되며 캐릭터의 얼굴을 가리지 않습니다.')
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1])
d['raden']=[dict(tier=1,option=i,title='전시 · '+name,image=f'../{rev}/exhibit{i}.gif',kind='밝은 전시 문양 · 실제 시전·유지') for i,name in [(1,'조각'),(2,'공예')]]
t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=t.replace('src="clips/raden-tier1-option1-8.gif"',f'src="../{rev}/exhibit1.gif"');p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,currentGod='raden',currentVisualReviewGod='raden',currentVisualReviewTier=1,currentVisualReview='analysis/previews/raden-review01/index.html#tier1')
 if 'tierApprovals' in d:d['tierApprovals']['raden'].update(pendingRevision=rev,tier1Revision=rev,feedback='1성 표식 밝기·크기 개선, 사용자 확인 대기')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(s/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,nativeSize=[14,14],position=[18,0],combatNumbersChanged=False,saveFormatChanged=False,validation=v),indent=2))
note='# 라덴 1성 가시성 개선 / raden-vfx01 / 2026-10-28\n\n작은 점 모양 표식을 밝은 옥색·아이보리 속과 금빛 테두리의14×14px 전시 문양으로 교체. 머리 오른쪽 위32px 타일 내(18,0). 생성 원본과 배치 기록 assets/holocrawl/raden-vfx01. 실제 세 작품 전환·유지 화면 캡처 및 상태/RNG 불변 검사,22신 기능·새 프로세스 복원 검사 통과. 런타임 갱신. 전투 수치/저장 형식 변경 없음. 현재 라덴1성 피드백 대기.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Published',rev,digest)
