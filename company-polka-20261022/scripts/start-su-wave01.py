from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='su-wave01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/shots/wave.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
for scene in ['dry','wet']:
 frames=[Image.open(b/f'native/shots/wave-{scene}-{n}.png').convert('RGB').crop((211,196,627,484)).resize((832,576),Image.Resampling.NEAREST) for n in ['before','cast0','cast1','after']]
 frames[0].save(o/f'{scene}.gif',save_all=True,append_images=frames[1:],duration=[1100,400,400,1500],loop=0,optimize=False)
 frames[2].save(o/f'{scene}.png')
base=r/'analysis/previews/su-review01'
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스우3성 · 파도</title><style>body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1100px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#bcefff}img{max-width:100%;image-rendering:pixelated}b{color:#ffe09d}td,th{padding:9px;border-bottom:1px solid #39485c;text-align:left}.info{background:#202b3e;padding:16px;border-radius:10px}</style><h1>스우3성 · 파도</h1><p class="info"><b>최대5칸으로 파도를 보내 피해를 주고 적을1칸 밀어냅니다. 물을 만나면 그 지점부터 폭이3줄로 넓어집니다.</b><br>해금: 신앙75 · 최소 기도술 제한 없음<br>비용: MP3·신앙3·행동1턴<br>재사용: 사용 시작부터4턴, 시전 완료 후3턴</p><h2>마른 바닥 · 가운데 줄만 타격</h2><img src="../su-wave01/dry.gif"><h2>1성으로 만든 물을 통과 · 옆줄까지 타격</h2><img src="../su-wave01/wet.gif"><p>실제 엔진 권능 실행 전 → 현재 시전 이펙트2프레임 → 피해·밀치기 결과입니다. 두 번째 장면의 물은 실제 일반 근접공격으로 생성했습니다. 이후 적을 비교 위치로 배치했습니다. 원형 물보라는 현재 시전 장식이며, 공격 범위를 나타내는 원이 아닙니다. 파도가 경로를 따라 이동하는 연속 애니메이션은 아직 없습니다.</p><h2>현재 수치</h2><table><tr><th>항목</th><th>적용</th></tr><tr><td>피해</td><td>2d(7+⌊I/3⌋). 기도술I12:2d11,2~22·평균12. 적 AC 적용, 별도 명중 굴림 없음</td></tr><tr><td>밀치기</td><td>진행 방향1칸. 벽·다른 개체·함정·이동 불가 등으로 막히면 이동하지 않음</td></tr><tr><td>방향·거리</td><td>선택 위치 방향의8방향 중 하나, 최대5칸. 벽·시야 차단에서 중심 경로 중단</td></tr><tr><td>물 연계</td><td>1성 웅덩이 또는 자연 물을 지나면 해당 지점부터 양옆1줄 추가. 물을 소모하지 않음</td></tr><tr><td>보호</td><td>이 권능은 보이는 적대 몹만 피해 대상으로 선택</td></tr><tr><td>1성 확정</td><td>실제 얕은 물 생성 유지. 스우 신도는 자연/생성 얕은 물의 이동 지연·근접 헛손질 면제</td></tr></table><h2>이번 실제 결과</h2><table><tr><th>조건</th><th>중앙 적 피해</th><th>옆줄 적 피해</th><th>밀치기</th></tr>'''
for s in proof['scenes']:
 page+=f"<tr><td>{'물 통과' if s['water'] else '마른 바닥'}</td><td>{s['mainDamage']}</td><td>{s['sideDamage']}</td><td>중앙1칸{'·옆줄1칸' if s['water'] else '·옆줄유지'}</td></tr>"
page+='''</table><p>범위 밖 몹은 두 경우 모두 피해·이동 없음. 위 피해는 이번 한 번의 난수·AC 적용 결과이며 평균 피해가 아닙니다. 비용·재사용·물 확장·밀치기·캡처 상태/RNG 보존 및22신 회귀·저장 복원 검사 통과. 현재3성 검토 중.</p><p><a href="tier1-grace01.html">확정된 스우1성 상세</a></p></html>'''
for name in ['index.html','tier3-review01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['su']=[dict(tier=3,option=i,title=title,image=f'../su-wave01/{scene}.gif',kind='실제 파도 피해·밀치기 결과') for i,(title,scene) in enumerate([('파도 · 마른 바닥','dry'),('파도 · 물 확장','wet')])];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="su" data-god="su"><h2>스우 <small>3성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">파도 · 마른 바닥</option><option value="1" selected>파도 · 물 확장</option></select><p class="scene-note">실제 파도 피해·밀치기 결과</p><img class="scene" src="../su-wave01/wet.gif"><p>MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음. I12:2d11(평균12·AC 전),1칸 밀치기. 물을 지나면 폭3줄. 원형 장식은 공격 범위 표시가 아닙니다.</p><p><a href="../su-review01/tier3-review01.html">효과·수치·두 조건 비교</a></p><label>피드백<textarea data-feedback="su"></textarea></label></article>'
t=re.sub(r'<article id="su".*?</article>',lambda _:article,t,count=1,flags=re.S);p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
review='analysis/previews/su-review01/tier3-review01.html'
def update(d):
 d.update(currentGod='su',currentVisualReviewGod='su',currentVisualReviewTier=3,currentVisualReview=review,playBinarySha256=digest,next='Review Su tier3. Su tier1 approved; tiers3/5 pending. 18 gods complete.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('su',{}).update(approved=[1],pending=[3,5],tier1Revision='su-grace01',tier3Preview=rev,pendingRevision=rev,feedback='오키 그다음')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
 for key in d.get('sourceSha256',{}):
  f=r/'engine/campaign-crawl/crawl-ref/source'/key
  if f.is_file():d['sourceSha256'][key]=hashlib.sha256(f.read_bytes()).hexdigest().upper()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatChanged=False,artChanged=False,nativeProof=proof,validation=v),indent=2),encoding='utf-8')
note='# 스우1성 확정·3성 파도 검토 / su-wave01 / 2026-10-29\n\n스우1성 su-grace01 승인. 3성 마른 바닥/실제1성 웅덩이 통과 조건을 나눠 실제 권능 피해·1칸 밀치기·옆줄 포함/제외 검증·캡처. I12:2d11(평균12·AC 전),MP3/신앙3/1턴,사용시작4턴 재사용(시전후3턴),물부터 폭3줄. 현재 원형 물보라는 기존 시전 장식이며 경로 이동 애니메이션은 없음. 전투·아트 유지,검증 fixture 추가 실행본 갱신.22신/일반·코요리·스우 지형 복원 통과. '+review+' 현재3성 검토 중.3·5성 미승인,완료18신 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su tier3 ready:',proof)
