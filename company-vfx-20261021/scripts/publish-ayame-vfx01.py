from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/ayame-vfx01';raw=run/'native/shots';src=root/'engine/campaign-crawl/crawl-ref/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation=json.loads((run/'capture-validation.json').read_text(encoding='utf-8-sig'));assert validation['status']=='passed'
review=json.loads((run/'native/ayame-review.json').read_text());assert review['status']=='passed' and review['afterStrikeHp']<review['beforeStrikeHp'] and review['duelWidth']==5
for f,h in json.loads((run/'preserved-files.json').read_text()).items():assert sha(src/f)==h,f
out=root/'analysis/previews/ayame-vfx01';out.mkdir(exist_ok=True)
box=(227,196,579,484)
def publish(name,paths,durations):
    frames=[]
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB').crop(box).resize((704,576),Image.Resampling.NEAREST);im.save(out/f'{name}-{i}.png');frames.append(im)
    frames[0].save(out/f'{name}.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
publish('tier1',[raw/'ayame-before.png',raw/'ayame-aura-frame0.png',raw/'ayame-aura-frame1.png',raw/'ayame-aura-expired.png'],[800,450,450,800])
three=sorted(raw.glob('ayame-tier3-*-frame?.png'));five=sorted(raw.glob('ayame-tier5-*-frame?.png'));assert len(three)==len(five)==2
assert three[0].read_bytes()!=three[1].read_bytes(),'Two slash directions not distinct'
three_state=next(raw.glob('ayame-tier3-*-state.png'))
publish('tier3',[raw/'ayame-aura-expired.png',*three,three_state],[650,250,250,650])
publish('tier5',[three_state,*five,raw/'ayame-duel-active.png',raw/'ayame-duel-expired.png'],[700,300,300,1100,700])
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>아야메 · 검기와 백귀 결투장</title><style>body{background:#111923;color:#eef2ff;font:17px "Malgun Gothic";margin:26px;max-width:1000px}section{background:#202b3b;padding:22px;margin:24px 0}p{line-height:1.8}img{max-width:100%;image-rendering:pixelated}a{color:#b4c7ff}</style><h1>아야메 · 1성 / 3성 / 5성</h1><p>실제 SDL 게임 화면을 확대해 느리게 반복했습니다. 캡처 위에 효과를 덧그리지 않았습니다. 높은 자원·고정 장비의 테스트 전투장이며 일반 던전 플레이 영상은 아닙니다. 기존 피해·비용·지속시간은 그대로입니다.</p><section><h2>1성 · 귀인의 간격</h2><p>같은 적과 근접전을 이어갈 때 명중·살육·회피 강화. 실제 근접 공격으로 가호가 생기면 몸체 양옆에 붉은 검기 잔광이 보입니다. 지정 상대가 살아 있고 인접하며 유지시간이 남을 때만 표시합니다. 끝에서는 만료 후 잔광이 사라집니다.</p><img src="tier1.gif"></section><section><h2>3성 · 쌍섬</h2><p>일반 근접 공격 한 번의 시간으로 두 번 공격합니다. 대상 위치에 붉은 칼날이 서로 다른 방향으로 연속 교차합니다. 참격 이미지는 공격 동작 표시이며 주변 칸을 추가로 타격하지 않습니다. 두 번의 동작이 모두 명중했다는 표시는 아닙니다.</p><img src="tier3.gif"></section><section><h2>5성 · 백귀의 결투장</h2><p>지정 상대와의 결투 강화 및 처치 보상. 실제 저장된 시전 위치 중심 5×5 영역에 붉은 뿔과 오니 문양을 유지합니다. 문양은 모든 캐릭터 아래에 그립니다. 벽이나 다른 적이 있어도 통과 불가 벽을 생성하는 기술은 아닙니다. 마지막은 지속시간 만료 후입니다.</p><img src="tier5.gif"></section></html>'''
(out/'index.html').write_text(doc,encoding='utf-8')
write(run/'gallery-validation.json',{'status':'passed','review':review,'preservedPriorArtAndCombatHashes':True,'nativeFrames':{p.name:sha(p) for p in raw.glob('*.png')},'gallery':'analysis/previews/ayame-vfx01/index.html'})
# Package a source diff before installing the exact validated executable.
patch=''
for p in (run/'before').rglob('*'):
    if p.is_file() and p.suffix!='.exe':
        rel=p.relative_to(run/'before');target=src/rel;q=run/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,q)
        patch+=''.join(difflib.unified_diff(p.read_text(encoding='utf-8').splitlines(True),target.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+rel.as_posix(),tofile='after/'+rel.as_posix()))
(run/'source.patch').write_text(patch,encoding='utf-8')
runtime=root/'runtime/tiles01/HoloCrawl.exe';assert sha(runtime)==sha(run/'before/HoloCrawl.exe')
shutil.copy2(run/'capture-engine.exe',runtime);h=sha(runtime);assert h==validation['binarySha256'].lower()
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj.update(visualRevision='ayame-vfx01',currentVisualReviewGod='ayame',ayameVisualReview='analysis/previews/ayame-vfx01/index.html',ayameVisualValidation='analysis/native/ayame-vfx01/gallery-validation.json',ayameVisualFeedback='New passive aura / twin slash /5x5 duel seal ready for user review',next='Await Ayame visual feedback; Suisei/Miko/Aki/Fubuki accepted. Do not move to other gods or bot work.')
    for key in ['playBinarySha256','tilesBuildSha256']:
        if key in obj:obj[key]=h.upper()
    write(p,obj)
p=root/'scripts/god-art-skills.json';obj=json.loads(p.read_text(encoding='utf-8'));obj['ayame'][0][3]='실제 근접 가호 유지 중 몸체 양옆 붉은 검기 잔광';obj['ayame'][1][3]='대상 위치에 붉은 참격 두 방향 연속 교차';obj['ayame'][2][3]='시전 위치 중심5×5 붉은 뿔·오니 문양, 모든 캐릭터 아래';write(p,obj)
note='# 최신: 아야메 1·3·5성 전용 이펙트 — ayame-vfx01 (2026-10-21)\n\n후부키 VFX05 승인 유지. 아야메는 실제 근접 가호 조건의 붉은 검기, 쌍섬 두 방향 연속 참격, 실제 시전 중심5×5 결투 문양을 추가했다. 문양은 캐릭터 아래이며 실제 상태 만료와 함께 사라진다. 기존 모든 도트와 전투 구현 원문 해시 유지. 실제 근접/쌍섬/결투·만료·캡처 상태/RNG 보존과 전체22신 권능/저장 및 별도 프로세스 재로드를 검증한 바이너리를 설치했다. 고정 테스트 전투장이며 일반 캠페인 승률 검증은 아니다.\n\n현재 보기: analysis/previews/ayame-vfx01/index.html. 근거: analysis/native/ayame-vfx01/gallery-validation.json, capture-validation.json, preserved-files.json, source.patch. 생성 방식: built-in imagegen. 도트 원본과 전체 프롬프트: assets/holocrawl/ayame-vfx01/originals와 inputs.json. 다음은 아야메 사용자 피드백. 스이세이·미코·아키·후부키 승인 유지.\n\n---\n\n'
p=root/'START_HERE_HOME.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root.parent/'CURRENT_WORKSPACE.md';p.write_text('Current: HoloCrawl_HOME_2026-10-20, Ayame VFX01 native-validated and installed. Await user feedback at analysis/previews/ayame-vfx01/index.html. Suisei/Miko/Aki/Fubuki accepted. See START_HERE_HOME.md.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
write(run/'checkpoint-manifest.json',{'status':'passed','revision':'ayame-vfx01','runtimeSha256':h,'combatAndPriorArtPreserved':True,'feedback':'pending','prompts':'assets/holocrawl/ayame-vfx01/inputs.json'})
print(out/'index.html')
