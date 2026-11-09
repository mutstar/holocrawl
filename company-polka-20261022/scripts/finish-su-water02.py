from pathlib import Path
from PIL import Image
import json, hashlib, shutil, difflib, re
r=Path(__file__).resolve().parents[1]
rev='su-water02';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/water.json');reload=read(b/'native/su-water-reload.json')
assert v['status']==proof['status']==reload['status']=='passed' and v['gods']==22
o.mkdir(exist_ok=True,parents=True)
frames=[Image.open(b/f'native/shots/water-{n}.png').convert('RGB').crop((243,196,563,452)).resize((640,512),Image.Resampling.NEAREST) for n in ['before','hit','water','player','ended']]
frames[0].save(o/'water.gif',save_all=True,append_images=frames[1:],duration=[900,800,1200,1200,900],loop=0)
frames[2].save(o/'water.png')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스우1성 · 실제 얕은 물</title><style>body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1050px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#bcefff}img{max-width:100%;image-rendering:pixelated}b{color:#ffe09d}td,th{padding:9px;border-bottom:1px solid #39485c;text-align:left}</style><h1>스우1성 · 실제 얕은 물</h1><p><b>공격으로 피해를 준 일반 바닥을 돌죽 기본 얕은 물로 바꿉니다.</b><br>신앙30 해금 · 최소 기도술 제한 없음 · 자동 패시브 · MP/신앙 소모 없음</p><img src="../su-water02/water.gif"><p>실제 엔진 캡처: 공격 전 → 적중·물 생성 → 적이 떠난 물 → 플레이어가 물에 선 모습 → 물 소멸. 장면 사이 이동은 검증용 배치이며, 이동 애니메이션이 아닙니다.</p><table><tr><th>항목</th><th>현재 적용</th></tr><tr><td>생성</td><td>피해가 있는 직접 공격. 일반 바닥 또는 스우의 기존 물 위에서 생성·갱신. 자연 물과 다른 임시 지형은 변경하지 않음</td></tr><tr><td>지속</td><td>생성부터5+0.1I턴. I12에서6.2턴, 공격 처리 시간 포함</td></tr><tr><td>최대 수</td><td>1성 웅덩이12개. 초과 시 가장 오래된 웅덩이 복구</td></tr><tr><td>적</td><td>기본 얕은 물 판정. 물에 서툰 몹은 이동 비용+6, 근접공격25% 헛손질. 수영·비행·큰 체격 등은 기본 예외 적용</td></tr><tr><td>플레이어</td><td>기본 얕은 물 판정. 물에 서툰 캐릭터는 이동 비용 증가, 근접공격37.5% 헛손질. 스우 전용 면역 없음</td></tr><tr><td>별도 이동 감속</td><td>기존 ×1.25 추가 비용 제거. 기본 물 효과와 중첩하지 않음</td></tr><tr><td>추가 피해</td><td>1성 물 자체 피해 없음</td></tr><tr><td>3성·5성</td><td>3성은 실제 물을 지날 때 폭 확장. 5성 영역도 실제 얕은 물로 변경되며 이동 시 영역 밖의 5성 물은 복구. 자연 물은 유지</td></tr><tr><td>복원·저장</td><td>기본 임시 지형 시스템으로 만료·저장·불러오기 처리. 겹친1·5성 물은 각 지속시간 보존</td></tr></table><p>I는 기도술. 일반 지형 타일을 사용하며 기존 물결 바닥 오버레이는 제거했습니다. 22신 회귀 검증, 스우 물 생성·양측 헛손질·만료·5성 이동·자연 물 보존·별도 프로세스 저장 복원 통과.</p><p>스우1성 검토 중. 이번 변경이 승률 향상을 보장하지는 않으며, 실플레이 밸런스 평가는 별도입니다.</p></html>'''
base=r/'analysis/previews/su-review01'
for name in ['index.html','tier1.html','tier1-water02.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['su']=[dict(tier=1,option=0,title='물결의 흔적 · 기본 얕은 물',image='../su-water02/water.gif',kind='실제 얕은 물 생성·플레이어 진입·만료')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="su" data-god="su"><h2>스우 <small>1성 · 검토 중</small></h2><img class="scene" src="../su-water02/water.gif"><p>직접 피해를 준 바닥을 기본 얕은 물로 변경. 신앙30 해금, 최소 기도술 없음. MP·신앙 소모 없음. 물에 서툰 적과 플레이어 모두 기본 물 페널티 적용.</p><p><a href="../su-review01/tier1-water02.html">현재 효과·수치</a></p><label>피드백<textarea data-feedback="su"></textarea></label></article>'
t=re.sub(r'<article id="su".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review='analysis/previews/su-review01/tier1-water02.html'
def update(d):
 d.update(currentGod='su',currentVisualReviewGod='su',currentVisualReviewTier=1,currentVisualReview=review,playBinarySha256=digest,suCombatRevision=rev)
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('su',{}).update(approved=[],pending=[1,3,5],pendingRevision=rev)
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/old.name
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(revision=rev,binarySha256=digest,nativeProof=proof,reload=reload,validation=v),indent=2),encoding='utf-8')
note='# 스우 기본 얕은 물 전환 / su-water02 / 2026-10-29\n\n사용자 요청으로 스우1성 웅덩이·5성 영역을 실제 DNGN_SHALLOW_WATER로 전환. 기존 별도 이동비용125% 및 물결 바닥 오버레이 제거. 양측 기본 물 페널티 적용(서툰 적 근접25%, 플레이어37.5% 헛손질; 기본 예외 유지). 스우 전용 임시지형 유형2개를 enum 끝에 추가, 기본 지형 저장/만료 사용. 1성 생성5+0.1I턴/최대12개 유지,5성 이동영역 복구·1성 겹침 보존, 자연 물·다른 임시지형 변경 제외. 3성 실제 물 인식. 22신/일반·코요리 복원 및 스우 별도프로세스 지형복원 검증 통과. 런타임 갱신. '+review+' 에 실제 SDL 생성/진입/소멸 GIF·현재 수치. 스우1성 검토 중, 완료18신 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su native water deployed:',digest)

