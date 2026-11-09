from pathlib import Path
import json,re,hashlib,shutil,html
r=Path.cwd();run=r/'analysis/native/polka-review01';out=r/'analysis/previews/polka-review01'
run.mkdir(exist_ok=True);out.mkdir(exist_ok=True);(run/'before').mkdir(exist_ok=True)
assert not (out/'index.html').exists(), 'Review already published'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(r/'analysis/native/night-vfx04/gallery-validation.json');assert proof['status']=='passed'
verified={}
for rel,h in proof['nativeFrames'].items():
 if '/polka-' in rel:
  f=r/'analysis/native/night-vfx04'/rel
  if not f.exists():f=r.parent/'HoloCrawl_HOME_2026-10-20/exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT/analysis/native/night-vfx04'/rel
  assert hashlib.sha256(f.read_bytes()).hexdigest()==h
  verified[rel]=h
assert verified
page=r/'analysis/previews/all-gods-vfx-draft04/index.html';text=page.read_text(encoding='utf-8');data=json.loads(re.search(r'const data=(.*?);function choose',text).group(1))
entries=[];seen=set()
names={(1,1):'오늘의 공연 · 일점집중',(1,2):'오늘의 공연 · 외줄타기',(1,3):'오늘의 공연 · 저글링',(3,0):'공중곡예',(5,0):'대단원 · 불꽃 피날레',(5,1):'대단원 · 커튼콜',(5,2):'대단원 · 대혼란'}
desc={(1,1):'강한 표적을 지정하고, 해당 표적에게 유효 피해를 3회 이상 준 뒤 처치하면 공연 성공.',(1,2):'지정 표적에게 피해를 준 뒤 두 번 이상 자발적으로 이동하고, 표적을 처치하면 성공.',(1,3):'유효한 서로 다른 적 3명 이상에게 피해를 주고, 공연 중 적을 처치하면 성공.',(3,0):'인접 적을 넘어 반대편 빈 바닥으로 도약. 3턴 안의 다음 공격 피해 +20%. 박수 1 추가 사용을 선택하면 착지 주변 적의 명중을 4턴 동안 5 낮춤.',(5,0):'지정한 지점 주변 2칸에 화염 피해. 피해량 2d(8+⌊기도술/3⌋)+4×소비 박수. 벽과 경로의 영향을 받음.',(5,1):'HP를 8+⌊기도술/2⌋+4×소비 박수 회복. 3+소비 박수 턴 동안 새로 적용되는 혼란·감속·공포·중독 지속시간 50%.',(5,2):'자신 주변 2칸의 적을 1칸 밀치고 혼란 판정. 정신 면역·명료화 대상에게 혼란은 적용되지 않음.'}
for e in data['polka']:
 key=(e['tier'],e['option'])
 if key in seen:continue
 seen.add(key);src=(page.parent/e['image']).resolve();stem=src.stem
 assert any(Path(k).stem==stem+'-frame0' for k in verified),stem
 shutil.copy2(src,out/src.name)
 poster=page.parent/'clips'/(stem+'-0.png')
 if poster.exists():shutil.copy2(poster,out/poster.name)
 entries.append(dict(tier=key[0],option=key[1],title=names[key],description=desc[key],image=src.name,sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
assert len(entries)==7
cards=[]
for tier in [1,3,5]:
 sub=[]
 for e in entries:
  if e['tier']!=tier:continue
  sub.append('<article><h3>'+html.escape(e['title'])+'</h3><p>'+html.escape(e['description'])+'</p><img src="'+e['image']+'" alt="'+html.escape(e['title'])+' 실제 게임 캡처"></article>')
 note={1:'MP1 · 준비 0.5턴. 성공하면 박수 1~2(최대 6), 신앙 +1, 6턴 동안 명중 +3·일반 공격 피해 +10%. 영상은 시작 연출이며 과제 완수 과정은 포함하지 않습니다.',3:'MP3 · 신앙2 · 1턴 · 재사용 4턴. 현재 영상은 사용 직후의 두 장면이며, 도약 궤적이나 강화 공격 전체를 이어 보여주는 영상은 아닙니다. 박수 추가 사용의 별도 영상은 아직 없습니다.',5:'MP6 · 신앙10 · 박수3~6 · 1턴 · 재사용16턴. 아래 시연은 박수3을 미리 준비한 시험 장면입니다. 박수의 자연 획득 과정이나 모든 표적 결과를 보여주지는 않습니다.'}[tier]
 cards.append(f'<section id="tier{tier}"><h2>{tier}성</h2><p class="info">{note}</p><div class="cards">'+''.join(sub)+'</div></section>')
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>폴카 · 1·3·5성 이펙트 검토</title><style>body{background:#101722;color:#edf2ff;font:17px "Malgun Gothic",sans-serif;max-width:1250px;margin:28px auto;padding:0 20px;line-height:1.75}h1{color:#ffd69d}h2{color:#f9b9df}nav{position:sticky;top:0;background:#101722ee;padding:12px;z-index:1}a{color:#b8e5ff;margin-right:22px}section{scroll-margin-top:70px;margin:38px 0}article{background:#1b2736;padding:18px;border-radius:12px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}img{max-width:100%;image-rendering:pixelated}.info{color:#d3dfef;background:#202b3e;padding:16px;border-radius:10px}.limit{color:#bcc9dc}h3{margin-top:0}</style><h1>폴카 · 서커스와 박수</h1><p>뭇별 승인: 라미 1·3·5성 완료. 다음은 폴카의 현재 전용 모티프 초안을 검토합니다.</p><p class="info">1성 공연 과제로 박수 획득 → 3성 곡예로 전투 운용 → 5성 선택형 대단원.<br>기존 실제 SDL 캡처를 모았습니다. 이번 단계에서 새 도트를 만든 것은 아니며, 순간 효과 두 프레임을 반복하는 미리보기입니다.</p><nav><a href="#tier1">★ 오늘의 공연</a><a href="#tier3">★★★ 공중곡예</a><a href="#tier5">★★★★★ 대단원</a></nav>'''+''.join(cards)+'''<p class="limit">현재 전용 서커스 문양 초안입니다. 그림의 크기는 실제 피해 범위와 같다는 뜻이 아닙니다. 성공·실패·면역, 박수의 자연 수입, 공연 완주, 도약 궤적의 전체 연출은 이 영상으로 검증하지 않습니다. 라미 승인본과 전투 수치는 변경하지 않았습니다.</p></html>'''
(out/'index.html').write_text(doc,encoding='utf-8')
manifest={'status':'passed','source':'analysis/native/night-vfx04/gallery-validation.json','historicalCapture':True,'newArtCreated':False,'entries':entries,'nativeFrameHashesVerified':verified,'nativeFrameArchiveFallback':'../HoloCrawl_HOME_2026-10-20/exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT/analysis/native/night-vfx04','numericChanges':False,'reviewStatus':'Polka tiers1/3/5 pending; Lamy approved','scope':'Verified existing native captures and current-source ability descriptions; not a new gameplay or animation regression run.'}
(run/'validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(out/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
feedback='ㅇㅇ좋다 라미는 이걸로하고 다음 폴카 1성 3성 5성 이펙트 보자'
for rel in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/rel;dest=run/'before'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);d=read(p)
 if rel=='VFX_DRAFT_STATUS.json':
  if 'lamy' not in d['approvedGods']:d['approvedGods'].append('lamy')
  d['draftGods']=[g for g in d['draftGods'] if g!='lamy'];d.update(currentGod='polka',next='Review Polka tier1/3/5 existing native VFX, all options')
  d['tierApprovals']['lamy'].update(approved=[1,3,5],pending=[],tier5Revision='lamy-banquet-vfx05',pendingRevision=None,pendingTier5Revision=None,tier5Feedback=feedback)
  d['tierApprovals']['polka']={'approved':[],'pending':[1,3,5],'pendingRevision':'polka-review01','visualSourceRevision':'night-vfx04'}
 else:d.update(currentVisualReviewGod='polka',currentVisualReviewTier=1,lamyReviewStatus='All tiers approved; tier5 lamy-banquet-vfx05',lamyVisualFeedback=feedback,polkaVisualReview='analysis/previews/polka-review01/index.html',next='Review Polka tier1/3/5 current visuals; Polka pending, Lamy approved.')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(page,run/'before/integrated-index.html')
text=text.replace("const id=location.hash.slice(1)||'lamy'","const id=location.hash.slice(1)||'polka'")
text=text.replace('1·3성 승인 완료. 지금은5성 눈의 연회를 확인합니다.','라미 전체 승인 완료. 지금은 폴카 1·3·5성을 확인합니다.')
page.write_text(text,encoding='utf-8')
note='# 최신: 라미 전체 승인 / 폴카 이펙트 검토 (2026-10-22)\n\n라미 5성 lamy-banquet-vfx05를 뭇별이 승인했다. 1·3성 승인도 유지한다. 다음은 폴카의 1·3·5성 현재 이펙트: analysis/previews/polka-review01/index.html. 1성 과제 세 종류와 5성 대단원 세 종류를 나누고 현재 엔진 권능 설명을 추가했다. 기존 night-vfx04 실제 SDL 프레임 해시를 검증해 모은 검토본이며 새 도트 제작이나 새 게임 검증 실행이 아니다. 폴카는 승인 대기이며 다음 신으로 자동 진행하지 않는다.\n\n'
for rel in ['HOME_SESSION.md','HOME_RESUME.md','CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md']:
 p=r/rel;shutil.copy2(p,run/'before'/rel);p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print('Polka review ready:',out/'index.html','verified native frames:',len(verified))
