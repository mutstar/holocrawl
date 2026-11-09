from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,difflib
r=Path(__file__).resolve().parents[1];rev='lui-wings01';b=r/'analysis/native'/rev;s=r/'engine/campaign-crawl/crawl-ref/source';o=r/'analysis/previews'/rev;read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
v=read(b/'capture-validation.json');assert v['status']=='passed' and v['gods']==22
for name,h in read(b/'preserved-art.json').items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==h,name
shots=b/'native/shots';proof=read(shots/'lui-army.json');assert proof['hawksActive']==6 and proof['hawksAfterExpiry']==3
o.mkdir(parents=True,exist_ok=True)
files=[shots/('lui-army-'+n+'.png') for n in ['before','cast0','cast1','active','ended']]
frames=[Image.open(p).convert('RGB').crop((275,228,531,436)).resize((512,416),Image.Resampling.NEAREST) for p in files]
frames[0].save(o/'army.gif',save_all=True,append_images=frames[1:],duration=[800,250,350,1500,1100],loop=0,optimize=False)
frames[3].save(o/'field.png')
for i in range(2):shutil.copy2(s/f'rltiles/holo/fx_night_lui5_{i}.png',o/f'emblem{i}.png')
p=r/'analysis/previews/lui-review01/index.html';old=p.read_text(encoding='utf-8');shutil.copy2(p,o/'previous-tier3.html');css=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>루이 · 5성 매의 군세</title><style>'''+css+'''</style><h1>루이 · 5성 매의 군세</h1><section id="tier5"><p class="info"><b>간모를 최대 6마리까지 보충하고, 군세 전체에 보호막·회피·이동속도 강화</b><br>해금: 신앙 ★★★★★120 · 최소 기도술 제한 없음<br>비용: MP7 · 신앙14 · 행동 1턴<br>종료 후 재사용 대기: 15턴</p><div class="cards"><article><h2>발동 → 6마리 군세 → 종료 · 실제 게임</h2><p>기존 세 마리에서 발동해 여섯 마리로 늘어나는 장면입니다. 등 뒤에서 펼쳐지는 흰 깃·금빛 날개이 군세 활성 상태를 나타냅니다.</p><img src="../lui-wings01/army.gif" alt="루이 5성 실제 발동, 여섯 간모, 버프 종료"><p>등 뒤 군세 날개 <img src="../lui-wings01/emblem1.png" width="64" height="64" alt="등 뒤 흰 깃 금빛 군세 날개"></p><p>추가 소환에 필요한 빈 바닥이 있어야 최대 여섯 마리가 됩니다. 이 테스트에서는 종료 뒤 기존 세 마리가 남고 추가 세 마리는 사라집니다. 기존 간모의 원래 수명이 끝났다면 더 적게 남을 수 있습니다.</p></article><article><h2>현재 수치 · 기도술 I=12 예시</h2><table><tr><th>항목</th><th>효과</th></tr><tr><td>시전 완료 후 지속</td><td>6+0.2I턴 → 8.4턴</td></tr><tr><td>소환 한도</td><td>기본 3마리 → 군세 중 6마리</td></tr><tr><td>보호막</td><td>간모마다 6+⌊I/3⌋ → 피해10 흡수<br>플레이어에게 주는 보호막은 아닙니다.</td></tr><tr><td>회피 EV</td><td>+4 → I12에서 18→22</td></tr><tr><td>이동</td><td>0.8턴 → 0.6턴</td></tr><tr><td>일반 공격 간격</td><td>1턴 유지 · 공격속도 증가는 없음</td></tr><tr><td>종료</td><td>보호막·회피·이동 강화 종료<br>추가 간모 소멸, 기존 간모는 남은 원래 수명에 따름</td></tr></table><p>3성과 구분: 3성은 적 하나에 즉시 집중 공격을 지시하고, 5성은 군세 수와 생존력·기동력을 강화합니다. 5성 사용 자체가 3성 지휘를 무료로 발동하는 것은 아닙니다.</p></article></div><p>실제 22신 기능·새 프로세스 복원 검사 통과. 전투 수치는 유지하고 5성 연출을 캐릭터 등 뒤 날개로 교체했습니다.</p><p><a href="../lui-command01/index.html#tier3">확정된 3성 사냥 지휘 보기</a> · <a href="../lui-attack06/index.html#tier1">확정된 1성·두 발 공격 보기</a></p><p>현재 5성 검토 중. 전체 22신 시각 작업 이후 중간 패시브/최종 성급 배치는 별도 재검토합니다.</p></section></html>'''
p.write_text(page,encoding='utf-8');(o/'index.html').write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';txt=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',txt);d=json.loads(m[1]);d['lui']=[dict(tier=5,option=0,title='매의 군세',image=f'../{rev}/army.gif',kind='실제 군세 발동·여섯 마리·종료')];txt=txt[:m.start(1)]+json.dumps(d,ensure_ascii=False)+txt[m.end(1):];article=f'<article id="lui" data-god="lui"><h2>루이 <small>5성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">5성 · 매의 군세</option></select><p class="scene-note">실제 군세 발동·유지·종료</p><img class="scene" src="../{rev}/army.gif"><p>MP7·신앙14·1턴. 신앙120 해금, 최소 기도술 없음.</p><p><a href="../lui-review01/index.html#tier5">효과·수치 보기</a></p><label>피드백<textarea data-feedback="lui"></textarea></label></article>';txt=re.sub(r'<article id="lui".*?</article>',lambda _:article,txt,count=1,flags=re.S);p.write_text(txt,encoding='utf-8')
shutil.copy2(b/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe');digest=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest()
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);d.update(visualRevision=rev,currentVisualReviewGod='lui',currentVisualReviewTier=5,currentVisualReview='analysis/previews/lui-review01/index.html#tier5',playBinarySha256=digest,next='Review Lui tier5 army activation and expiry. Tiers1/3 approved; tier5 pending.')
 if 'tierApprovals' in d:d['tierApprovals']['lui'].update(approved=[1,3],pending=[5],pendingRevision=rev,tier3Revision='lui-command01',tier5Revision=rev,visualSourceRevision=rev,feedback='3성 확정. 5성 6마리 군세·등 뒤 군세 날개·실제 종료 검토 중.')
 for key in d.get('sourceSha256',{}):
  if (s/key).is_file():d['sourceSha256'][key]=hashlib.sha256((s/key).read_bytes()).hexdigest().upper()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for f in (b/'before').glob('*.cc'):diff.extend(difflib.unified_diff(f.read_text(encoding='utf-8-sig').splitlines(True),(s/f.name).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f.name,tofile='after/'+f.name))
(b/'source.patch').write_text(''.join(diff),encoding='utf-8');(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,binarySha256=digest,combatNumbersChanged=False,saveFormatChanged=False,otherArtPreserved=True,army=proof,nativeFiles=[p.name for p in files],backWings=True,underActors=True,spreadSize=[46,30],validation=v),indent=2))
note='# 루이 5성 등 뒤 군세 날개 검토 / lui-wings01 / 2026-10-28\n\n사용자 3성 확정, 5성 진행. 기존 B안·두 발 공격·초록 우호 원 유지. 5성 머리 옆 표식을 등 뒤46×30px 흰 깃·금빛 날개로 변경. 접힘32×24→펼침46×30, 활성 중 펼침 유지, 종료 시 소멸. 캐릭터와 간모보다 아래 레이어. 64×64 캔버스/32px 렌더 배율로 플레이어 등 위치에 고정. 실제3→6마리 발동, 보호막/EV/이동 강화, 기간 종료 추가3마리 소멸·기존3마리 유지 검사. 전투 수치 변경 없음. 페이지 analysis/previews/lui-review01/index.html#tier5. 1·3성 승인, 5성 피드백 대기. 10/22 ZIP은 갱신하지 않았으므로 다음 인계 때 최신 폴더로 다시 묶기.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Lui tier5 published:',proof)

