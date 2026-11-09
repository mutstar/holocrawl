from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,re,html,difflib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/night-vfx01';src=root/'engine/campaign-crawl/crawl-ref/source';raw=run/'native/shots';cr=run/'native-choco/shots'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=json.loads((run/'capture-validation.json').read_text(encoding='utf-8-sig'));assert v['status']=='passed' and v['gods']==22
for f,h in json.loads((run/'preserved-files.json').read_text()).items():assert sha(src/f)==h,f
before=(run/'before/holo-campaign.cc').read_text(encoding='utf-8');after=(src/'holo-campaign.cc').read_text(encoding='utf-8')
normalized=after.replace('holo_visual::invocation("noel",3,drop);\n    ','').replace('holo_visual::invocation(g,tier,aim?*aim:target?target->pos():you.pos(),option);','holo_visual::invocation(g,tier,aim?*aim:target?target->pos():you.pos());')
assert normalized==before,'Combat/campaign changed beyond visual-only arguments/hooks'
# Strict corner placement and actual upper-cell monster visibility control.
im=Image.open(cr/'choco-corner-upper.png').convert('RGB');control=Image.open(cr/'choco-corner-upper-no-marker.png').convert('RGB')
upper=(387,292,419,324);target=(387,324,419,356)
assert im.crop(upper).tobytes()==control.crop(upper).tobytes(),'Upper monster pixels changed'
assert im.crop(target).tobytes()!=control.crop(target).tobytes(),'Corner marker invisible'
write(run/'corner-native-validation.json',{'status':'passed','upperCellPixelsIdentical':True,'targetCellHasVisibleMarker':True,'upperBox':upper,'targetBox':target})
write(run/'combat-hook-audit.json',{'status':'passed','otherCombatFilesHashPreserved':True,'campaignSourceEquivalentAfterRemovingVisualOnlyGiftHookAndOptionForwarding':True,'approvedArtPreservedExceptAuthorizedChocoCorner':True})
out=root/'analysis/previews/all-gods-vfx-draft01';out.mkdir(exist_ok=True);clips=out/'clips';clips.mkdir(exist_ok=True)
box=(227,196,579,484)
def clip(name,paths,durations=None):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box).resize((704,576),Image.Resampling.NEAREST);im.save(clips/f'{name}-{i}.png');frames.append(im)
    if len(frames)>1:
        frames[0].save(clips/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations or [450]*len(frames),loop=0);return 'clips/'+name+'.gif'
    return f'clips/{name}-0.png'
skills=json.loads((root/'scripts/god-art-skills.json').read_text(encoding='utf-8'));mapping=json.loads((root/'analysis/previews/current-god-art/mapping.json').read_text(encoding='utf-8'))
names={r['god']:r['name'] for r in mapping['rows']};gods=list(skills)
old=json.loads((root/'analysis/native/god-vfx-capture05/gallery-validation.json').read_text(encoding='utf-8'))['entries']
descriptions={(e['god'],e['tier'],e['option']):e['title'] for e in old}
entries={g:[] for g in gods}
for p in sorted(raw.glob('*-frame0.png')):
    m=re.fullmatch(r'(\w+)-tier(-?\d+)-option(-?\d+)-(\d+)-frame0.png',p.name)
    if not m:continue
    g,t,o,n=m.groups();t=int(t);o=int(o);stem=p.name[:-11]
    paths=[raw/(stem+'-frame0.png'),raw/(stem+'-frame1.png')];assert all(p.is_file() for p in paths)
    entries[g].append({'tier':t,'option':o,'title':descriptions.get((g,t,o),skills[g][(1,3,5).index(t)][0] if t in (1,3,5) else '수동 기폭'),'image':clip(stem,paths),'kind':'실제 권능 직후 · 두 프레임 비교'})
for g in ['korone','okayu','watame','towa','hajime','su','mela']:
    entries[g].insert(0,{'tier':1,'option':0,'title':skills[g][0][0],'image':clip(g+'-passive',[raw/(g+'-passive1.png')]),'kind':'실제 자동 가호/상태 · 시전 애니메이션 아님'})
entries['noel'].append({'tier':3,'option':0,'title':skills['noel'][1][0],'image':clip('noel-gift',[raw/'noel-supply3.png']),'kind':'실제 선물 생성 완료 · 검사 보급 진척208 사전 설정'})
entries['koyori'].append({'tier':3,'option':0,'title':skills['koyori'][1][0],'image':clip('koyori-catalyst',[raw/'koyori-catalyst3.png']),'kind':'실제 무료 촉매 켜기 상태 · 유료 시전 아님'})
# Preserve reviewed full sequences for approved gods, including original timings.
approved={
 'suisei':('suisei-vfx04',['tier1-ingame.gif','tier3-ingame.gif','tier5-sequence.gif']),
 'miko':('miko-vfx02',['tier1.gif','tier3.gif','tier5.gif']),
 'aki':('aki-vfx05',[None,'rose-flight.gif','full-bloom.gif']),
 'fubuki':('fubuki-vfx05',[None,'swap-fire.gif','fox-arrival.gif']),
 'ayame':('ayame-vfx02',['tier1.gif','tier3.gif','tier5.gif'])}
for g,(folder,files) in approved.items():
    base=list(entries[g]);entries[g]=[]
    for tier,file in zip((1,3,5),files):
        if file:
            assert (root/'analysis/previews'/folder/file).exists(),(g,file)
            entry={'tier':tier,'option':0,'title':skills[g][(1,3,5).index(tier)][0],'image':'../'+folder+'/'+file,'kind':'뭇별 승인본 · 기존 실제 게임 시퀀스 보존'}
        else:entry=next(e for e in base if e['tier']==tier)
        entries[g].append(entry)
# Latest Choco control uses actual two-monster scene and unchanged kiss/charm logic.
entries['choco']=[
 {'tier':1,'option':0,'title':skills['choco'][0][0],'image':clip('choco-corner',[cr/'choco-before.png',*[cr/f'choco-stack{i}.png' for i in range(1,6)],cr/'choco-corner-upper.png'],[700,*([450]*5),1100]),'kind':'타일 내부 우측 위 · 마지막 장면은 바로 위 몬스터 대조'},
 {'tier':3,'option':0,'title':skills['choco'][1][0],'image':clip('choco-kiss',[*[cr/f'choco-kiss-1-frame{i}.png' for i in range(4)],cr/'choco-kiss-after.png'],[250,250,250,250,700]),'kind':'실제 HP 회복이 있을 때만 귀환 하트'},
 {'tier':5,'option':0,'title':skills['choco'][2][0],'image':clip('choco-charm',[cr/'choco-success-frame0.png',cr/'choco-success-frame1.png',cr/'choco-success-active.png',cr/'choco-success-expired.png'],[350,350,1100,700]),'kind':'매혹 성공 문양 → 실제 만료'}]
draft_gods=list(json.loads((root/'assets/holocrawl/night-vfx01/inputs.json').read_text())['prompts'])
for g in draft_gods:assert {1,3,5} <= {e['tier'] for e in entries[g]},g
limits={g:'전용 모티프를 상태 표시·중간 시전·큰 시전으로 나눈 1차 초안. 시전 문양은 실제 피해 범위나 명중 성공 표시가 아니다. 지속 장판과 소환물은 기존 실제 상태 표시를 유지한다.' for g in draft_gods}
limits.update({
 'noel':'3성은 실제 장비 선물 완료 장면이다. 테스트에서 보급 진척을 미리 설정했다. 가짜 수동3성 권능을 만들지 않았다.',
 'koyori':'3성은 실제 무료 촉매 켜기 상태다. 시약 제조·투척과 임계 준비는 같은 실험 모티프를 공유한다. 개별 반응의 별도 투사체·폭발 애니메이션은 후속 피드백 대상.',
 'pekora':'예약/설치에는 작은 알림과 기존 실제 범위 경고를 유지한다. 당근 폭발 모티프는 실제 폭발 콜백에서만 재생한다.',
 'sopia':'고리/중력장 위치는 기존 실제 상태 표시를 유지한다. 큰 모티프는 빅뱅 준비와 실제 기폭 캡처를 구분해서 확인한다.',
 'polka':'5성 불꽃·커튼콜·혼란은 선택값을 전달해 서로 구분한다. 커튼콜/혼란 초안은 기존 하트/서커스 아트를 재사용했다.',
 'raden':'3성 회화·조각·공예 분기는 서로 다른 모티프를 사용한다. 조각/공예는 기존 충격/보호 아트를 재사용한 초안.',
 'lamy':'서리 모티프의 크기는 시전 강조다. 실제 부채꼴 피해 판정·폭은 변경하지 않았으며 정밀한 방향별 숨결은 후속 점검 대상.',
 'lui':'실제 까마귀 개체 수/공격/집중 지휘는 그대로이며 새 깃털 모티프를 추가했다. 후부키처럼 한 마리씩 등장하는 별도 소환 연출은 아직 추가하지 않았다.',
 'su':'실제 웅덩이·만조 장판은 유지한다. 새 물결 문양은 시전 알림이며 직선 파도의 이동 경로 애니메이션은 후속 점검 대상.'})
cards=[]
for g in gods:
    status='승인 유지' if g in approved else '초코 모서리 수정안' if g=='choco' else '초안 · 회사 피드백 대기'
    options=''.join(f'<option value="{i}">{e["tier"]}성 · {html.escape(e["title"])} · 선택{e["option"]}</option>' for i,e in enumerate(entries[g]))
    power=''.join(f'<p><b>{tier}성 · {html.escape(p[0])}</b> ({p[1]})<br>{html.escape(p[2])}</p>' for tier,p in zip((1,3,5),skills[g]))
    note=limits.get(g,'승인본을 그대로 유지했다.' if g in approved else '1성 하트만 대상 칸 우측 모서리로 옮겼다.3·5성 판정/연출은 유지했다.')
    cards.append(f'<article id="{g}" data-god="{g}"><h2>{html.escape(names[g])} <small>{status}</small></h2><select onchange="choose(this)">{options}</select><p class="scene-note">{html.escape(entries[g][0]["kind"])}</p><img loading="lazy" class="scene" src="{entries[g][0]["image"]}"><details><summary>권능 효과 / 초안 한계</summary>{power}<p class="limit">{html.escape(note)}</p></details><label>회사에서 이어갈 피드백<textarea data-feedback="{g}" placeholder="1성 / 3성 / 5성 · 가림, 크기, 색, 속도, 컨셉, 범위"></textarea></label></article>')
js='''function choose(s){const a=s.closest('article'),e=data[a.dataset.god][s.value];a.querySelector('.scene').src=e.image;a.querySelector('.scene-note').textContent=e.kind}document.querySelectorAll('textarea').forEach(t=>{try{t.value=localStorage.getItem('holo-vfx-'+t.dataset.feedback)||''}catch(e){}t.oninput=()=>{try{localStorage.setItem('holo-vfx-'+t.dataset.feedback,t.value)}catch(e){}}});function saveFeedback(){const o={};document.querySelectorAll('textarea').forEach(t=>o[t.dataset.feedback]=t.value);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(o,null,2)],{type:'application/json'}));a.download='HOLOCRAWL_VFX_FEEDBACK.json';a.click()}'''
doc='<!doctype html><html lang="ko"><meta charset="utf-8"><title>홀로죽22신 · 승인본과 회사 피드백용 초안</title><style>body{background:#101923;color:#eff3ff;font:16px "Malgun Gothic";margin:24px}p{line-height:1.75}header{max-width:1100px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:20px}article{background:#202d40;border:1px solid #455875;padding:18px;border-radius:12px;align-self:start}h2 small{font-size:13px;color:#b8ceef}select,textarea,button{background:#111e31;color:#edf2ff;border:1px solid #607695;padding:9px;max-width:100%}select,textarea{width:100%;box-sizing:border-box}textarea{height:110px;margin-top:8px}.scene{width:100%;max-width:704px;image-rendering:pixelated}details{margin:18px 0}.limit,.scene-note{color:#c4cce0}a{color:#b4caff}</style><header><h1>홀로죽22신 · 회사 피드백용 통합 초안</h1><p>스이세이·미코·아키·후부키·아야메는 승인본 유지. 초코는1성 하트의 타일 내부 우측 모서리 수정안. 나머지16신은 전용 모티프와 단계별 시전 강조를 적용한 첫 초안이며 사용자 승인 완료가 아닙니다.</p><p>실제 SDL 전투장 화면만 사용하며 이미지에 이펙트를 덧그리지 않았습니다. 반복 GIF는 점검을 위해 느리게 재생하며 일반 던전 플레이 영상이 아닙니다. 자동 가호/무료 설정/선물은 해당 실제 상태 화면으로 구분했습니다. 시전 문양의 크기는 피해 범위를 보증하지 않습니다. 전투 수치·확률·저장 포맷은 유지했습니다.</p><p><button onclick="saveFeedback()">22신 피드백 JSON 저장</button> · 입력은 가능한 경우 이 브라우저에 저장됩니다. 회사 이동 전 버튼으로 파일도 저장하세요.</p><p><a href="../../../../START_HERE_COMPANY.md">회사 시작 안내</a></p></header><main>'+''.join(cards)+'</main><script>const data='+json.dumps(entries,ensure_ascii=False)+';'+js+'</script></html>'
(out/'index.html').write_text(doc,encoding='utf-8')
coverage={g:sorted({e['tier'] for e in entries[g]}) for g in gods};assert all({1,3,5}<=set(t) for t in coverage.values())
write(run/'gallery-validation.json',{'status':'passed','gods':22,'abilityTiers':66,'coverage':coverage,'approvedGods':list(approved),'draftGods':draft_gods,'entries':entries,'limits':limits,'nativeFrames':{p.relative_to(run).as_posix():sha(p) for p in run.rglob('*.png') if 'native' in p.relative_to(run).parts[0]},'gallery':'analysis/previews/all-gods-vfx-draft01/index.html'})
# Contact sheets are resized native screenshots only, with labels outside them.
for page,start in enumerate(range(0,16,4),1):
    sheet=Image.new('RGB',(1024,930),'#111923');d=ImageDraw.Draw(sheet)
    for j,g in enumerate(draft_gods[start:start+4]):
        e=next(e for e in entries[g] if e['tier']==5);p=out/e['image'];im=Image.open(p).convert('RGB');im.thumbnail((490,400),Image.Resampling.NEAREST)
        x=(j%2)*512;y=(j//2)*465;sheet.paste(im,(x,y+28));d.text((x+8,y+5),g+' tier5 DRAFT',fill='white')
    sheet.save(out/f'native-contact-{page}.png')
write(out/'review-data.json',{'entries':entries,'limits':limits,'approval':{g:('approved' if g in approved else 'corner-revision' if g=='choco' else 'draft') for g in gods}})
review='#22신 이펙트 회사 피드백\n\n승인 유지: 스이세이·미코·아키·후부키·아야메. 초코1성 위치 수정, 나머지16신은 초안.\n\n'
for g in gods:review+=f'## {names[g]} ({g})\n\n-1성:\n-3성:\n-5성:\n-가림/크기/색/속도/컨셉/범위:\n\n'
(root/'VFX_COMPANY_FEEDBACK.md').write_text(review,encoding='utf-8')
patch=''
for p in (run/'before').rglob('*'):
    if p.is_file() and p.suffix!='.exe':
        rel=p.relative_to(run/'before');q=run/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,q)
        patch+=''.join(difflib.unified_diff(p.read_text(encoding='utf-8').splitlines(True),(src/rel).read_text(encoding='utf-8').splitlines(True),fromfile='before/'+rel.as_posix(),tofile='after/'+rel.as_posix()))
(run/'source.patch').write_text(patch,encoding='utf-8')
runtime=root/'runtime/tiles01/HoloCrawl.exe';assert sha(runtime)==sha(run/'before/HoloCrawl.exe');shutil.copy2(run/'capture-engine.exe',runtime);h=sha(runtime);assert h==v['binarySha256'].lower()
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj.update(visualRevision='night-vfx01',currentVisualReviewGod='all22-drafts',integratedVfxReview='analysis/previews/all-gods-vfx-draft01/index.html',integratedVfxValidation='analysis/native/night-vfx01/gallery-validation.json',next='Company feedback on Choco corner and16 draft gods. Preserve5 accepted gods. No numerical balancing or music work requested.')
    for key in ['playBinarySha256','tilesBuildSha256']:
        if key in obj:obj[key]=h.upper()
    write(p,obj)
skills['choco'][0][3]='대상 타일 내부 우측 위 모서리의 중첩 하트(최대12px)'
for g in draft_gods:
    for i,tier in enumerate([1,3,5]):skills[g][i][3]='전용 모티프 초안 · '+('실제 상태/작은 시전 표시' if tier==1 else '중간 시전 강조' if tier==3 else '큰 시전 강조')+' · 기존 실제 장판/소환물 유지'
write(root/'scripts/god-art-skills.json',skills)
write(run/'checkpoint-manifest.json',{'status':'passed','revision':'night-vfx01','runtimeSha256':h,'approvedGods':list(approved),'draftGods':draft_gods,'cornerNativePixels':'corner-native-validation.json','combatAudit':'combat-hook-audit.json','gallery':'analysis/previews/all-gods-vfx-draft01/index.html','package':'pending'})
print('Published22-god integrated review; native/asset/combat/corner checks passed. Runtime '+h)
