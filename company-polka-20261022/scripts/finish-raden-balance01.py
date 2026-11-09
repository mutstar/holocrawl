from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,difflib
r=Path(__file__).resolve().parents[1];rev='raden-balance01';b=r/'analysis/native'/rev;o=r/'analysis/previews'/rev;s=r/'engine/campaign-crawl/crawl-ref/source'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');proof=read(b/'native/raden-balance.json');assert v['status']==proof['status']=='passed' and v['gods']==22
o.mkdir(parents=True,exist_ok=True)
for i in range(3):
 stem=f'raden-tier3-option{i}-review'
 frames=[Image.open(b/f'native/shots/{stem}-frame{f}.png').convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for f in range(3 if i==1 else 2)]
 frames[0].save(o/f'ability{i}.gif',save_all=True,append_images=frames[1:],duration=260,loop=0,optimize=False)
base=r/'analysis/previews/raden-review01';page=(base/'tier3-vfx04.html').read_text(encoding='utf-8').replace('../raden-three04/','../raden-balance01/')
replacements={
'2d(6+⌊I/3⌋)+4×채색 수':'2d(8+⌊I/2⌋)+6×채색 수',
'2d10+12 → 14~32':'2d14+18 → 20~46 · 평균33',
'2d(5+⌊I/3⌋)':'3d(6+⌊I/3⌋)+⌊I/2⌋',
'2d9 → 2~18':'3d10+6 → 9~36 · 평균22.5',
'10+⌊2I/3⌋ → I=12에서 <b>18</b>':'14+I → I=12에서 <b>26</b>',
'시전 완료 후5턴 유지하거나 보호량을 다 쓰면 소멸.':'시전 완료 후 6+⌊I/6⌋턴 → I=12에서 <b>8턴</b> 유지하거나 보호량을 다 쓰면 소멸.'}
for old,new in replacements.items():assert old in page,old;page=page.replace(old,new)
five='''<h2>5성 특별전 중 · 강화된 3성 수치</h2><p class="info">특별전: 신앙120 해금 · 최소 기도술 없음 · MP6·신앙12·1턴.<br>시전 완료 후 6+0.2I턴 → I12에서8.4턴. 종료 후 재사용 대기15턴.<br>특별전 중 세 전시의 가호를 함께 받고, 전시 선택과 관계없이 세 가지 3성 권능을 사용합니다. 각각 MP3·신앙3·1턴은 별도 지불합니다. 특별전 발동만으로 폭발·파동·보호막이 자동 발생하지는 않습니다.</p><table><tr><th>권능</th><th>5성 강화식</th><th>I=12 예시</th></tr><tr><td>회화</td><td>3d(8+⌊I/2⌋)+6×채색 수<br>범위 주변2칸 · 자폭 위험 유지</td><td>3중첩 3d14+18<br>21~60 · 평균40.5</td></tr><tr><td>조각</td><td>4d(6+⌊I/3⌋)+⌊I/2⌋<br>폭3줄·길이3칸, 밀치기2칸</td><td>4d10+6<br>10~46 · 평균28</td></tr><tr><td>공예</td><td>보호량22+⌊3I/2⌋<br>시전 완료 후8+⌊I/6⌋턴</td><td>40 흡수 · 10턴</td></tr></table><p>피해는 AC 적용 전. 공예의 독·혼란·감속·공포 완화 및 각 전시 회복 시간은 유지합니다. 공예 보호막의 남은 지속시간은 특별전 종료와 별개입니다. 5성 이펙트 외형 검토는 아직 진행하지 않았습니다.</p>'''
page=page.replace('</section>',five+'</section>')
for name in ['index.html','tier3.html','tier3-vfx04.html','tier3-balance01.html']:(base/name).write_text(page,encoding='utf-8')
(o/'index.html').write_text(page.replace('href="brush03.html#tier1"','href="../raden-review01/brush03.html"'),encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8').replace('../raden-three04/','../raden-balance01/').replace('../raden-review01/tier3.html#tier3','../raden-review01/tier3-balance01.html');t=t.replace('MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음.','MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음. I12: 회화3중첩 평균33 / 조각 평균22.5 / 보호막26·8턴.');p.write_text(t,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
numbers=dict(revision=rev,invocations12=dict(normal=dict(paintingMean3Stacks=33,sculptureMean=22.5,shield=26,shieldTurns=8),exhibition=dict(paintingMean3Stacks=40.5,sculptureMean=28,shield=40,shieldTurns=10)),proof=proof)
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(combatRevision=rev,playBinarySha256=digest,currentVisualReview='analysis/previews/raden-review01/tier3-balance01.html',radenBalance=numbers)
 if 'review' in d:d['review']='analysis/previews/raden-review01/tier3-balance01.html'
 if 'tierApprovals' in d:d['tierApprovals']['raden'].update(combatRevision=rev,tier3NumbersApproved=True,feedback='3성 제안 수치 적용 승인. 5성 강화식도 상향 적용. 현재 3성 검토 유지.')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for f in ['holo-batch-martial.cc','holo-batch.cc','holo-campaign-test.cc']:diff.extend(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(s/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',binarySha256=digest,combat=numbers,validation=v,artChanged=False,saveFormatChanged=False),ensure_ascii=False,indent=2),encoding='utf-8')
note='# 라덴 3성·5성 수치 보강 적용 / raden-balance01 / 2026-10-28\n\n3성: 회화2d(8+I/2)+6S, 조각3d(6+I/3)+I/2, 공예14+I·(6+I/6)턴. 5성 특별전 강화: 회화3d(8+I/2)+6S, 조각4d(6+I/3)+I/2, 공예22+3I/2·(8+I/6)턴. 정수 나눗셈 버림, 지속은 시전 완료 후 기준. 비용·회복·범위·밀치기·해제 효과 유지. 기도술0/6/12/18/27에서 일반/특별전 실제 피해·AC·보호량·지속·비용·밀치기 검증 및22신/새프로세스 복원 통과. 런타임/브라우저 수치 갱신. 새 링크 analysis/previews/raden-review01/tier3-balance01.html. 1성 확정 유지, 3성 수치 승인, 현재3성 검토 유지·5성 이펙트 미검토.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Published',rev,digest)
