from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='hajime-rhythm02';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/rhythm.json');assert v['status']==proof['status']=='passed' and v['gods']==22 and proof['stacks']==[0,1,2,3,0]
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(b/f'native/shots/rhythm-{n}.png').convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for n in ['0','1','2','3','spent']]
frames[0].save(o/'rhythm.gif',save_all=True,append_images=frames[1:],duration=[800,900,900,1300,1100],loop=0,optimize=False)
frames[3].save(o/'three-stacks.png')
base=r/'analysis/previews/hajime-review01';page=(base/'tier1.html').read_text(encoding='utf-8')
page=page.replace('src="passive.png"','src="../hajime-rhythm02/rhythm.gif"').replace('하지메 박자 유지 상태의 기존 실제 게임 캡처','실제 이동으로 박자0→1→2→3 획득 후 근접 공격 시도에서 소모')
page=page.replace('머리 오른쪽 위 파랑·보라의 작은 리듬 표식이 박자가 있는 상태를 나타냅니다. 현재 표식 모양은 박자1·2·3개를 구분하지 않습니다.','밝은 하늘색·연보라 음표가 머리 위에1개→2개→3개로 늘어납니다. 박자를 쓰거나 만료되면 사라집니다. 기존 별도 작은 장식은 제거했습니다.')
page=page.replace('이 이미지는 기존 실제 엔진 캡처입니다. 이동·획득·소모의 연속 재생은 아직 아닙니다.','실제 게임의 오른쪽 이동→왼쪽 이동→오른쪽 이동으로 박자1·2·3을 쌓은 다음, 아래쪽 적에게 실제 근접 공격을 시도해 전부 소모하는 장면입니다. 표시만 임의로 채운 영상이 아닙니다. 빗나가도 박자는 소모됩니다.')
page=page.replace('기존 도트·전투 수치는 변경하지 않았습니다.','박자 표식의 가시성·개수 표시를 개선했습니다. 전투 수치는 유지합니다.')
for name in ['tier1.html','index.html','tier1-rhythm02.html']:(base/name).write_text(page,encoding='utf-8')
(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['hajime']=[dict(tier=1,option=0,title='반쵸의 스텝',image='../hajime-rhythm02/rhythm.gif',kind='실제 이동·박자1→2→3·근접 소모')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
t=t.replace('../hajime-review01/passive.png','../hajime-rhythm02/rhythm.gif').replace('기존 실제 박자 유지 캡처','실제 이동·박자1→2→3·근접 소모').replace('../hajime-review01/tier1.html','../hajime-review01/tier1-rhythm02.html');p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,playBinarySha256=digest,currentGod='hajime',currentVisualReviewGod='hajime',currentVisualReviewTier=1,currentVisualReview='analysis/previews/hajime-review01/tier1-rhythm02.html')
 if 'review' in d:d['review']='analysis/previews/hajime-review01/tier1-rhythm02.html'
 if 'tierApprovals' in d:d['tierApprovals']['hajime'].update(tier1Revision=rev,pendingRevision=rev,feedback='실제 박자 축적·소모 캡처 및 음표 개수 표시 개선, 확인 대기')
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for f in ['holo-visual.cc','tiledgnbuf.cc','holo-campaign-test.cc']:
 diff.extend(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,nativeProof=proof,validation=v),indent=2))
note='# 하지메1성 실제 박자 축적·소모 / hajime-rhythm02 / 2026-10-28\n\n실제 이동 명령 오른쪽→왼쪽→오른쪽으로 박자0→1→2→3, 실제 아래쪽 근접 공격 시도로0소모 검증·SDL 캡처. 박자 개수에 맞춰 밝은 음표1/2/3개 표시, 머리 위8px 배치. 별도 옛 장식 제거. 음표 원본/프롬프트 assets/holocrawl/hajime-rhythm02. 전투 수치 변경 없음.22신·새 프로세스 복원 검사 통과, 런타임/미리보기 갱신. 현재 하지메1성 피드백 대기. 라덴전체 확정 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Published Hajime rhythm',proof)

