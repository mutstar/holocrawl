from pathlib import Path
from PIL import Image
import json,hashlib,shutil,difflib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/choco-vfx02'
src=root/'engine/campaign-crawl/crawl-ref/source';sdl=root/'engine/tiles-crawl/crawl-ref/source'
raw=run/'native/shots';out=root/'analysis/previews/choco-vfx02';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert read(run/'capture-validation.json')['status']=='passed'
for name in ['validation.json','reload.json','choco-review.json']:
    assert read(run/'native'/name)['status']=='passed'
for rel,digest in read(run/'preserved-files.json').items():assert sha(src/rel)==digest,rel
changed=[f'rltiles/holo/fx_chocoheart{n}_{f}.png' for n in range(1,6) for f in range(2)]+['holo-campaign-test.cc']
for rel in changed:
    assert (src/rel).read_bytes()==(sdl/rel).read_bytes(),rel
    p=run/'source_snapshot'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,p)
patch=''.join(difflib.unified_diff((run/'before/holo-campaign-test.cc').read_text(encoding='utf-8').splitlines(True),(src/'holo-campaign-test.cc').read_text(encoding='utf-8').splitlines(True),fromfile='before/holo-campaign-test.cc',tofile='after/holo-campaign-test.cc'))
(run/'source.patch').write_text(patch,encoding='utf-8')
# Compare adjacent actor pixels separately from background pixels: the raised
# marker intentionally extends a few pixels across the target tile's top edge.
upper=(387,292,419,324)
marked=Image.open(raw/'choco-corner-upper.png').convert('RGB').crop(upper)
control=Image.open(raw/'choco-corner-upper-no-marker.png').convert('RGB').crop(upper)
empty=Image.open(raw/'choco-raised-no-upper-no-marker.png').convert('RGB').crop(upper)
body=[a!=b for a,b in zip(control.getdata(),empty.getdata())]
delta=[a!=b for a,b in zip(marked.getdata(),control.getdata())]
affected=sum(a and b for a,b in zip(body,delta));total=sum(body)
assert total>0 and affected/total<0.02,(affected,total)
write(run/'adjacent-actor-validation.json',dict(status='passed',upperActorMaskPixels=total,upperActorPixelsOverlapped=affected,upperActorFractionUnchanged=(total-affected)/total,backgroundChangesAllowed=True,scope='This fixed adjacent-orc scene retains >98% of upper actor pixels; not a guarantee for every monster silhouette.'))
paths=[raw/'choco-before.png',*[raw/f'choco-stack{n}.png' for n in range(1,6)],raw/'choco-corner-upper.png']
def gif(name,box,size):
    frames=[Image.open(p).convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST) for p in paths]
    frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[700,650,650,650,650,900,1500],loop=0)
gif('tier1.gif',(227,196,579,484),(704,576))
gif('tier1-close.gif',(323,275,467,387),(576,448))
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>초코센 1성 · 채운 하트와 높이 수정</title><style>body{background:#101923;color:#eff3ff;font:17px "Malgun Gothic";margin:24px;max-width:1150px}p{line-height:1.8}img{image-rendering:pixelated;max-width:100%}section{background:#202d40;border:1px solid #455875;border-radius:12px;padding:18px;margin:22px 0}a{color:#bbcdff}</style><h1>초코센 1성 · 달콤한 시선</h1><p>빈 테두리를 속이 찬 분홍 하트로 바꾸고, 기존보다 게임 픽셀 6칸 위로 올렸습니다. 우측 위치와 중첩별 크기 변화는 유지하며 대상 머리 윗부분에 하트 아래쪽만 살짝 걸칩니다. 최종 승인 전 수정안입니다.</p><section><h2>수정안 · 가까이 보기</h2><p>표식 없음 → 실제 공격으로 유혹 1~5중첩 → 바로 위 몬스터가 있는 경우. 원본 SDL 캡처를 최근접 확대했으며 이펙트를 덧그리지 않았습니다.</p><img src="tier1-close.gif"></section><section><h2>원래 필드 배율 비교</h2><img src="tier1.gif"></section><section><h2>이전 빈 하트 / 낮은 위치</h2><img src="../all-gods-vfx-draft04/clips/choco-corner.gif"></section><p><a href="../all-gods-vfx-draft04/index.html#choco">22신 통합 미리보기 · 초코로 돌아가기</a></p></html>'''
(out/'index.html').write_text(doc,encoding='utf-8')
# Retain the import's original HTML, then route only Choco tier1 to this result.
p=root/'analysis/previews/all-gods-vfx-draft04/index.html';s=p.read_text(encoding='utf-8')
shutil.copy2(p,run/'before/integrated-index.html')
assert s.count('clips/choco-corner.gif')==2
s=s.replace('clips/choco-corner.gif','../choco-vfx02/tier1.gif')
s=s.replace('초코는1성 하트의 타일 내부 우측 모서리 수정안','초코는1성 채운 하트를 6픽셀 올린 수정안')
s=s.replace('타일 내부 우측 위 · 마지막 장면은 바로 위 몬스터 대조','속이 찬 하트 · 6픽셀 위 · 마지막은 위 칸 몬스터 대조')
p.write_text(s,encoding='utf-8')
# Deploy exactly the executable used by native controls and 22-god regression.
binary=run/'capture-engine.exe';assert sha(binary).upper()==read(run/'capture-validation.json')['binarySha256']
shutil.copy2(binary,root/'runtime/tiles01/HoloCrawl.exe')
runtime_hash=sha(binary).upper()
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/name;v=read(p);v.update(visualRevision='choco-vfx02',currentVisualReviewGod='choco',chocoVisualReview='analysis/previews/choco-vfx02/index.html',chocoVisualValidation='analysis/native/choco-vfx02/checkpoint-manifest.json',chocoVisualFeedback='Solid filled heart, raised 6 native pixels; awaiting user feedback.',next='Continue Choco feedback, then tier3/tier5. Preserve other god art and combat values.')
    v['playBinarySha256']=runtime_hash
    if 'tilesBuildSha256' in v:v['tilesBuildSha256']=sha(sdl/'crawl.exe').upper()
    write(p,v)
p=root/'scripts/god-art-skills.json';v=read(p);v['choco'][0][3]='속이 찬 분홍 유혹 하트; 우측 상단에서 기존보다 6픽셀 위, 중첩별 크기 변화';write(p,v)
note='# 최신 초코센 1성 수정 — choco-vfx02 / 2026-10-21\n\n사용자 요청으로 유혹 하트를 속이 찬 분홍색으로 교체하고 표시 중심을 (57,39)→(57,33), 게임 픽셀 6칸 위로 옮겼다. 기존 우측 위치·중첩별 크기 변화·렌더 순서는 유지했다. 10개 하트 PNG와 검사 전용 캡처만 변경했으며 다른 전투 소스/신 아트는 해시 그대로다. native 22신 권능/저장/새 프로세스 재로드와 초코 실제 공격 중첩·회복0·매혹 성공/실패/면역/만료 대조를 통과했다. 근접 확대 GIF는 실제 SDL 캡처다. 위 칸 오크 대조의 몸체 마스크 613픽셀 중8픽셀은 하트와 겹치며98.7%는 보존된다. 모든 몬스터 실루엣에 대한 무겹침 보장은 아니다. 사용자 승인 전이다.\n\n보기: `analysis/previews/choco-vfx02/index.html`, 통합 페이지의 초코1성도 같은 수정안이다. 원화·프롬프트: `assets/holocrawl/choco-vfx02/`. 근거: `analysis/native/choco-vfx02/`. 다음은 초코 피드백이며3·5성 효과와 다른 신 도트는 이번에 수정하지 않았다. 최초 전달 파일 검증 원장은 보존했으며 수정 뒤의 현재 상태는 새 체크포인트로 확인한다.\n\n---\n\n'
for name in ['CURRENT_WORKSPACE.md','START_HERE_COMPANY.md','CONTINUE_HERE.md']:
    p=root/name;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
write(run/'checkpoint-manifest.json',dict(status='passed',revision='choco-vfx02',runtimeSha256=runtime_hash,changedAssets=changed[:-1],testOnlySource='holo-campaign-test.cc',numericChanges=False,otherSourceAndGodArtHashesPreserved=True,feedback='pending',review='analysis/previews/choco-vfx02/index.html',nativeScreenshots=len(list(raw.glob('*.png'))),sourceSha256={n:sha(src/n) for n in changed},generatedAtlasSha256={p.name:sha(p) for p in (sdl/'dat/tiles').glob('*.png')},prompt='assets/holocrawl/choco-vfx02/generation.json'))
print(json.dumps(dict(status='passed',runtimeSha256=runtime_hash,upperActorPixelsOverlapped=affected,review=str(out/'index.html')),ensure_ascii=False))
