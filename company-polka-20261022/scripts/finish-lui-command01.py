from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='lui-command01';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source';o=r/'analysis/previews'/rev;read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
validation=read(b/'capture-validation.json');assert validation['status']=='passed' and validation['gods']==22
for name,digest in read(b/'preserved-art.json').items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==digest,name
shots=b/'native/shots';proof=read(shots/'lui-command.json');assert proof['status']=='passed' and proof['hawks']==3
first=shots/'lui-command-before.png';last=shots/'lui-command-after.png'
metas=sorted([p for p in shots.glob('lui-attack-*.json') if re.fullmatch(r'lui-attack-\d+',p.stem) and first.stat().st_mtime<=p.stat().st_mtime<=last.stat().st_mtime],key=lambda p:int(p.stem.split('-')[-1]))
assert len(metas)==3,('Expected three real command strikes',len(metas))
files=[first];durations=[800]
for p in metas:
 files += [shots/f'{p.stem}-ready.png']+[shots/f'{p.stem}-frame{i}.png' for i in range(3)]
 durations += [170,140,180,120]
files += [last];durations += [1000]
o.mkdir(parents=True,exist_ok=True)
frames=[Image.open(p).convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for p in files]
frames[0].save(o/'command.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
frames[-2].save(o/'field.png')
p=r/'analysis/previews/lui-review01/index.html';old=p.read_text(encoding='utf-8');shutil.copy2(p,o/'previous-tier1.html');css=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>루이 · 3성 사냥 지휘</title><style>'''+css+'''</style><h1>루이 · 3성 사냥 지휘</h1><section id="tier3"><p class="info"><b>적 하나를 지정 → 주변 간모들이 적의 인접 칸으로 재배치 → 각자 즉시 공격</b><br>해금: 신앙 ★★★75 · 최소 기도술 제한 없음<br>비용: MP3 · 신앙3 · 행동 1턴<br>대상 지정 거리: 플레이어에게서 5칸 · 참여하는 간모는 적에게서 4칸 이내<br>재사용: 시전 시작 기준 5턴(시전 1턴이 지난 직후에는 4턴 남음)</p><div class="cards"><article><h2>간모 3마리 집중 공격 · 실제 게임</h2><p>기존 B안과 두 발 동시 공격 모션을 유지했습니다. 한 행동 안에서 참여 간모의 공격 장면이 차례로 재생됩니다.</p><img src="../lui-command01/command.gif" alt="루이 3성 간모 세 마리 실제 재배치 및 집중 공격"><p>현재 이동은 인접 칸으로 즉시 재배치됩니다. 이 GIF는 실제 이동 전 상태·각 간모의 공격·최종 상태를 캡처한 것으로, 중간 비행 경로 애니메이션은 포함하지 않습니다.</p></article><article><h2>효과와 수치</h2><p>I = 기도술. 예시는 I=12.</p><table><tr><th>항목</th><th>현재 구현</th></tr><tr><td>참여 조건</td><td>적과 4칸 이내·가려지지 않은 경로·도착 가능한 인접 빈 칸</td></tr><tr><td>즉시 공격</td><td>참여 간모마다 명중 판정 후 1회</td></tr><tr><td>공격 굴림</td><td>1d(5+⌊I/3⌋)+3+⌊I/6⌋<br>I=12: 1d9+5</td></tr><tr><td>명중 기준값</td><td>21+I → 33</td></tr><tr><td>시야 방해 패시브</td><td>지난 3턴 내 적중한 서로 다른 간모마다, 적의 플레이어 대상 명중 -2 · 최대 -6</td></tr><tr><td>공격 이후</td><td>지휘를 받은 간모는 즉시 일반 행동을 한 번 더 하지 않도록 행동 간격 적용</td></tr></table><p>간모 소환 자체는 1성 권능으로 먼저 사용합니다. 새 간모를 공짜로 추가 소환하는 권능은 아닙니다.</p></article></div><p>'''+f"이 캡처의 실제 총 피해: {proof['damage']}. 한 번의 테스트 결과이며 고정 피해 수치가 아닙니다."+'''</p><p><a href="../lui-attack06/index.html#tier1">확정한 1성 소환수·두 발 일반 공격 보기</a></p><p>전투 수치는 유지하고 3성 직접 타격에도 기존 공격 모션을 연결했습니다. 전체 22신의 기존 시각 작업을 완료한 뒤, 중간 성급 패시브와 최종 권능 배치를 별도로 재설계합니다.</p></section></html>'''
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);d=json.loads(m[1]);d['lui']=[dict(tier=3,option=0,title='사냥 지휘',image=f'../{rev}/command.gif',kind='실제 세 간모 재배치·집중 공격')];txt=txt[:m.start(1)]+json.dumps(d,ensure_ascii=False)+txt[m.end(1):];article=f'<article id="lui" data-god="lui"><h2>루이 <small>3성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">3성 · 사냥 지휘</option></select><p class="scene-note">실제 세 간모 집중 공격</p><img class="scene" src="../{rev}/command.gif"><p>MP3·신앙3·1턴. 신앙75 해금, 최소 기도술 없음.</p><p><a href="../lui-review01/index.html#tier3">효과·수치 보기</a></p><label>피드백<textarea data-feedback="lui"></textarea></label></article>';txt=re.sub(r'<article id="lui".*?</article>',lambda _:article,txt,count=1,flags=re.S);p.write_text(txt,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,currentVisualReviewGod='lui',currentVisualReviewTier=3,currentVisualReview='analysis/previews/lui-review01/index.html#tier3',playBinarySha256=digest,next='Review Lui tier3 actual command sequence. Keep tier5 pending; finish all 22 visual reviews before intermediate passive redesign.',futureGrowthPlan='Complete current 1/3/5 visuals first, then per-god passive/utility additions and optional capstone relocation.')
 if 'tierApprovals' in d:d['tierApprovals']['lui'].update(approved=[1],pending=[3,5],pendingRevision=rev,tier3Revision=rev,visualSourceRevision=rev,feedback='1성 B안 및 두 발 공격 확정. 3성 실제 집중 공격 검토 중.')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for f in (b/'before').glob('*.cc'):diff.extend(difflib.unified_diff(f.read_text().splitlines(True),(s/f.name).read_text().splitlines(True),fromfile='before/'+f.name,tofile='after/'+f.name))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatNumbersChanged=False,saveFormatChanged=False,artPreserved=True,command=proof,captureSequences=[p.stem for p in metas],captureHashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},validation=validation),indent=2))
note='# 루이 3성 사냥 지휘 검토 / lui-command01 / 2026-10-28\n\n사용자 ㄱㄱ로 루이 1성 확정, 3성 진행. B안 서 있는 도트·두 발 공격·초록 우호 원 유지. 3성 직접 공격에도 일반 공격 모션 연결. 실제 세 마리 재배치/타격 캡처. 비용·거리·피해·쿨다운 수치 유지. 중간 비행 경로 애니메이션은 아직 없음. 페이지 analysis/previews/lui-review01/index.html#tier3. 22신 시각 작업부터 완료한 뒤 중간 패시브/최종 성급 배치 재검토 계획 유지. 현재 루이 3성 피드백 대기, 5성 미승인.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Lui tier3 published:',proof,[p.stem for p in metas])
