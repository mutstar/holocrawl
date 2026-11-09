from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re
r=Path(__file__).resolve().parents[1];rev='raden-vfx03';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev;s=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
for name,digest in read(b/'preserved.json').items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==digest,name
proof=read(b/'native/shots/raden-badges.json');assert proof['distinctExhibits']==3
o.mkdir(parents=True,exist_ok=True)
def crop(p):return Image.open(p).convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST)
for i in range(3):
 frames=[crop(b/f'native/shots/raden1-{i}-frame{f}.png') for f in range(2)]+[crop(b/f'native/shots/raden1-{i}-active.png')]
 frames[0].save(o/f'exhibit{i}.gif',save_all=True,append_images=frames[1:],duration=[450,450,1400],loop=0,optimize=False)
 if i==0:frames[2].save(o/'field.png')
frames=[crop(b/'native/shots/raden1-default.png')]+[crop(b/f'native/shots/raden1-{i}-active.png') for i in [1,2,0]]
frames[0].save(o/'transitions-brush03.gif',save_all=True,append_images=frames[1:],duration=1200,loop=0,optimize=False)
p=r/'analysis/previews/raden-review01/index.html';page=p.read_text(encoding='utf-8').replace('../raden-vfx02/','../raden-vfx03/').replace('붉은 액자','붉은 손잡이 붓').replace('raden-vfx03/transitions.gif','raden-vfx03/transitions-brush03.gif')
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';page=p.read_text(encoding='utf-8').replace('../raden-vfx02/','../raden-vfx03/').replace('회화: 붉은 액자','회화: 붉은 손잡이 붓');p.write_text(page,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,currentGod='raden',currentVisualReviewGod='raden',currentVisualReviewTier=1,currentVisualReview='analysis/previews/raden-review01/index.html#tier1')
 if 'tierApprovals' in d:d['tierApprovals']['raden'].update(pendingRevision=rev,tier1Revision=rev,feedback='회화 표식을 액자에서 붓으로 변경, 1성 확인 대기')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,painting='red-handled brush',nativeSize=[14,14],position=[18,0],otherExhibitsPreserved=True,combatNumbersChanged=False,saveFormatChanged=False,validation=v,exhibitProof=proof),indent=2))
note='# 라덴 회화 표식 붓 변경 / raden-vfx03 / 2026-10-28\n\n사용자 요청으로 회화 액자를 붉은 손잡이·금색 연결부·밝은 붓털의 대각선 붓으로 교체. 기존14×14px 배치 유지. 조각·공예와 전환 로직/전투 수치는 그대로. 실제 전환·유지 재캡처,22신 기능·새 프로세스 복원 검사 통과. 미리보기/런타임 갱신, 라덴1성 피드백 대기.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Published',rev,digest)
