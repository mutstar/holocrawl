from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/choco-vfx01';raw=run/'native/shots';src=root/'engine/campaign-crawl/crawl-ref/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation=json.loads((run/'capture-validation.json').read_text(encoding='utf-8-sig'));assert validation['status']=='passed'
review=json.loads((run/'native/choco-review.json').read_text());assert review['status']=='passed' and review['charmExpiry'] and review['mentalImmunityControl']
for f,h in json.loads((run/'preserved-files.json').read_text()).items():assert sha(src/f)==h,f
# Removing only visual records/callback must recover exact original combat code.
p=src/'holo-batch-resources.cc';s=p.read_text(encoding='utf-8')
s=s.replace('const coord_def kiss_pos=target->pos();const int hp_before_kiss=you.hp;\n                ','').replace('holo_visual::choco_kiss(kiss_pos,dealt,you.hp-hp_before_kiss);','')
assert s==(run/'before/holo-batch-resources.cc').read_text(encoding='utf-8'),'Combat logic changed'
write(run/'combat-hook-audit.json',{'status':'passed','originalCombatTextRecoveredAfterRemovingReadOnlyRecordsAndVisualCallback':True,'previousArtAndOtherGodCombatHashesPreserved':True})
out=root/'analysis/previews/choco-vfx01';out.mkdir(exist_ok=True)
box=(227,196,579,484)
def publish(name,paths,durations):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box).resize((704,576),Image.Resampling.NEAREST);im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
publish('tier1',[raw/'choco-before.png',*[raw/f'choco-stack{n}.png' for n in range(1,6)]],[800,*([600]*5)])
kiss=sorted(raw.glob('choco-kiss-1-frame?.png'));zero=sorted(raw.glob('choco-kiss-2-frame?.png'))
assert len(kiss)==4 and len(zero)==2
meta=[json.loads(p.with_suffix('.json').read_text()) for p in kiss]
assert all(m['healed']>0 for m in meta) and [m['absorption'] for m in meta]==[False,False,True,True]
assert all(json.loads(p.with_suffix('.json').read_text())['healed']==0 for p in zero)
publish('tier3',[*kiss,raw/'choco-kiss-after.png'],[260,260,260,260,800])
publish('tier3-no-heal',zero,[400,400])
publish('tier5',[raw/'choco-success-frame0.png',raw/'choco-success-frame1.png',raw/'choco-success-active.png',raw/'choco-success-expired.png'],[350,350,1300,800])
for name in ['failed','immune']:
    im=Image.open(raw/f'choco-{name}-state.png').convert('RGB').crop(box).resize((704,576),Image.Resampling.NEAREST);im.save(out/f'{name}.png')
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>초코 · 유혹과 입맞춤과 서큐버스의 밤</title><style>body{background:#111923;color:#eef2ff;font:17px "Malgun Gothic";margin:26px;max-width:1000px}section,details{background:#202b3b;padding:22px;margin:24px 0}p{line-height:1.8}img{max-width:100%;image-rendering:pixelated}a{color:#c6b5ff}</style><h1>초코 · 1성 / 3성 / 5성</h1><p>실제 SDL 게임 화면을 확대해 느리게 반복했습니다. 화면에 이펙트를 덧그리지 않았습니다. 높은 자원·고정 장비의 테스트 전투장이며 일반 던전 플레이 영상은 아닙니다. 피해·회복·매혹 확률·비용·지속시간은 유지했습니다.</p><section><h2>1성 · 달콤한 시선</h2><p>유혹 표식을 걸고 실제 직접 공격으로 중첩이 늘어납니다. 대상 머리 위 하트가 1→5중첩에 따라 커집니다. 캐릭터 몸체를 가리지 않게 머리 위에 두고, 다른 캐릭터와 겹치면 캐릭터가 위에 그려집니다. 중첩을 소비하거나 표식이 만료되면 사라집니다.</p><img src="tier1.gif"></section><section><h2>3성 · 위험한 입맞춤</h2><p>인접 적의 유혹을 소비해 피해를 주고 실제 회복량에 따라 HP를 회복합니다. 대상에 입맞춤 → 작은 하트가 시전자에게 이동합니다. 귀환 하트는 실제 HP가 회복된 경우에만 나옵니다.</p><img src="tier3.gif"></section><section><h2>5성 · 서큐버스의 밤</h2><p>매혹을 시도하면 박쥐 날개가 펼쳐지고, 실제 아군화에 성공하면 대상 머리 위 날개 하트 문양이 남습니다. 만료하면 사라집니다. 시전 연출과 매혹 성공 표시는 구분합니다.</p><img src="tier5.gif"></section><details><summary>실제 결과 대조 · 회복0 / 매혹 실패 / 정신 면역</summary><p>HP가 가득 찬 상태에서는 입맞춤만 표시하고 회복 입자는 만들지 않습니다.</p><img src="tier3-no-heal.gif"><p>다음 두 장면은 매혹 실패와 정신 면역 대상입니다. 성공 문양이 남지 않습니다. 면역 대조는 검사 목적의 유혹3중첩 사전 설정을 사용했습니다.</p><img src="failed.png"><img src="immune.png"></details></html>'''
(out/'index.html').write_text(doc,encoding='utf-8')
write(run/'gallery-validation.json',{'status':'passed','review':review,'healSequence':meta,'zeroHealFrames':len(zero),'nativeFiles':{p.name:sha(p) for p in raw.glob('*.png')},'gallery':'analysis/previews/choco-vfx01/index.html'})
patch=''
for p in (run/'before').rglob('*'):
    if p.is_file() and p.suffix!='.exe':
        rel=p.relative_to(run/'before');target=src/rel;q=run/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,q)
        patch+=''.join(difflib.unified_diff(p.read_text(encoding='utf-8').splitlines(True),target.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+rel.as_posix(),tofile='after/'+rel.as_posix()))
(run/'source.patch').write_text(patch,encoding='utf-8')
runtime=root/'runtime/tiles01/HoloCrawl.exe';assert sha(runtime)==sha(run/'before/HoloCrawl.exe');shutil.copy2(run/'capture-engine.exe',runtime);h=sha(runtime);assert h==validation['binarySha256'].lower()
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj.update(visualRevision='choco-vfx01',currentVisualReviewGod='choco',chocoVisualReview='analysis/previews/choco-vfx01/index.html',chocoVisualValidation='analysis/native/choco-vfx01/gallery-validation.json',chocoVisualFeedback='New stack hearts / actual-heal return particles / cast wings and success-only charm marker; awaiting user feedback',next='Await Choco feedback; Suisei/Miko/Aki/Fubuki/Ayame accepted. Do not move to other gods or bot work.')
    for key in ['playBinarySha256','tilesBuildSha256']:
        if key in obj:obj[key]=h.upper()
    write(p,obj)
p=root/'scripts/god-art-skills.json';obj=json.loads(p.read_text(encoding='utf-8'));obj['choco'][0][3]='유혹1~5중첩별 크기가 커지는 머리 위 하트 표식';obj['choco'][1][3]='입맞춤 후 실제 HP 회복 시 시전자에게 돌아오는 작은 하트';obj['choco'][2][3]='시전 시 박쥐 날개; 실제 매혹 성공 대상에만 지속 날개 하트 문양';write(p,obj)
note='# 최신: 초코 1·3·5성 전용 효과 — choco-vfx01 (2026-10-21)\n\n유혹1~5중첩에 따라 대상 머리 위 하트가 커진다. 실제 입맞춤 성공 지점/실제 HP 회복량을 기록해서 입맞춤과 회복 시에만 귀환 하트를 그린다.5성은 박쥐 날개 시전과 실제 아군화 성공 문양을 구분하고 만료 시 해제한다. 실제 공격으로 중첩, 회복0 대조, 독립 명시 시드의 매혹 성공·실패, 만료 및 정신 면역 대조를 검증했다. 면역 대조의 유혹3은 검사 사전 설정이다. 전체22신 권능/저장·별도 재로드 검사 통과 바이너리를 설치했다. 기존 전투 원문은 시각 기록/콜백을 제거하면 정확히 동일하고 이전 도트 해시도 유지했다. 고정 전투장 검증이며 일반 캠페인 클리어율 검증은 아니다.\n\n현재 보기: analysis/previews/choco-vfx01/index.html. 근거: analysis/native/choco-vfx01/gallery-validation.json, capture-validation.json, combat-hook-audit.json, source.patch. 도트는 built-in imagegen 제작. 원본/전체 프롬프트: assets/holocrawl/choco-vfx01/originals, inputs.json. 스이세이·미코·아키·후부키·아야메 승인 유지. 다음은 초코 피드백.\n\n---\n\n'
p=root/'START_HERE_HOME.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root.parent/'CURRENT_WORKSPACE.md';p.write_text('Current: HoloCrawl_HOME_2026-10-20. Choco VFX01 native-validated and installed. Await feedback: analysis/previews/choco-vfx01/index.html. Prior five gods accepted. See START_HERE_HOME.md.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
write(run/'checkpoint-manifest.json',{'status':'passed','revision':'choco-vfx01','runtimeSha256':h,'combatAndPriorArtPreserved':True,'feedback':'pending','prompts':'assets/holocrawl/choco-vfx01/inputs.json'})
print(out/'index.html')
