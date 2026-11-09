from pathlib import Path
import json,shutil,html,hashlib
root=Path(__file__).resolve().parents[1]
proof=json.loads((root/'analysis/native/god-vfx-capture05/gallery-validation.json').read_text(encoding='utf-8'))
assert proof['status']=='passed'
entries=sorted([e for e in proof['entries'] if e['god']=='choco'],key=lambda e:e['tier'])
assert [e['tier'] for e in entries]==[1,3,5]
out=root/'analysis/previews/choco-review01';out.mkdir(exist_ok=True)
skills=json.loads((root/'scripts/god-art-skills.json').read_text(encoding='utf-8'))['choco'];cards=[]
for e,power in zip(entries,skills):
    for rel in [e['gif'],*e['frames']]:shutil.copy2(root/'analysis/previews/god-vfx-ingame'/rel,out/Path(rel).name)
    # Trace each retained frame to the previously audited native framebuffer.
    for rel,h in zip(e['originals'],e['hashes']):
        original=(root/'analysis/previews/god-vfx-ingame'/rel).resolve();assert hashlib.sha256(original.read_bytes()).hexdigest().upper()==h
    name,kind,summary,visual=power
    note='권능 사용 직후의 순간 효과 두 프레임입니다. 지속 표식·중첩 변화 전체를 보여주는 영상은 아닙니다.'
    if e['tier']==5:note+=' 사용 연출 자체가 매혹 성공을 뜻하지는 않습니다. 성공 시 해당 몬스터 하나가 잠시 아군이 되고, 실패·정신 면역 대상에는 약화가 적용됩니다.'
    cards.append(f'<section><h2>{e["tier"]}성 · {html.escape(name)}</h2><p>{html.escape(summary)}</p><p><b>현재 화면:</b> {html.escape(visual)}</p><p class="note">{note}</p><img src="{Path(e["gif"]).name}"></section>')
doc='<!doctype html><html lang="ko"><meta charset="utf-8"><title>초코 · 1·3·5성 현재 이펙트</title><style>body{background:#111923;color:#eff2ff;font:17px "Malgun Gothic";margin:26px;max-width:1000px}section{background:#202b3b;padding:20px;margin:24px 0}p{line-height:1.8}img{image-rendering:pixelated;max-width:100%}.note{color:#b9c5d8}</style><h1>초코 · 현재 이펙트 점검</h1><p>아야메 VFX02 승인 완료. 기존 실제 SDL 캡처에서 초코의 현재 이펙트를 모았습니다. 신규 전용 연출을 제작한 상태는 아닙니다. 높은 자원·고정 장비의 테스트 전투장이며 일반 던전 플레이 영상은 아닙니다.</p>'+''.join(cards)+'</html>'
(out/'index.html').write_text(doc,encoding='utf-8')
(out/'provenance.json').write_text(json.dumps({'status':'passed','source':'analysis/native/god-vfx-capture05/gallery-validation.json','tiers':[1,3,5],'nativeOriginalHashesVerified':True,'historicalCapture':True},indent=2),encoding='utf-8')
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj.update(currentVisualReviewGod='choco',ayameVisualFeedback='User accepted Ayame VFX02 tier1/3/5 on 2026-10-21',chocoVisualReview='analysis/previews/choco-review01/index.html',next='Review Choco tier1/3/5 current native visuals. Suisei/Miko/Aki/Fubuki/Ayame accepted; do not alter approved visuals or restart bot work.')
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 최신: 아야메 VFX02 승인 / 다음 초코 (2026-10-21)\n\n뭇별이 아야메 1·3·5성 전용 이펙트를 승인했다. 다음은 초코의 현재 실제 SDL 보존 캡처 점검: analysis/previews/choco-review01/index.html. 원본 해시를 capture05 원장과 대조했다. 신규 초코 도트 제작 전이며 5성 시전 효과와 실제 매혹 성공은 구분한다. 스이세이·미코·아키·후부키·아야메 승인 유지. 다음은 초코 피드백.\n\n---\n\n'
p=root/'START_HERE_HOME.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root.parent/'CURRENT_WORKSPACE.md';p.write_text('Current: HoloCrawl_HOME_2026-10-20. Ayame VFX02 accepted; next Choco current native review at analysis/previews/choco-review01/index.html. Await feedback. See START_HERE_HOME.md.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
print(out/'index.html')
