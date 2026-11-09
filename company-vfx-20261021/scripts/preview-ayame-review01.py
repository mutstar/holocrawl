from pathlib import Path
import json,shutil,html,hashlib
root=Path(__file__).resolve().parents[1]
base=root/'analysis/native/god-vfx-capture05'
proof=json.loads((base/'gallery-validation.json').read_text(encoding='utf-8'))
assert proof['status']=='passed'
entries=sorted([e for e in proof['entries'] if e['god']=='ayame'],key=lambda e:e['tier'])
assert [e['tier'] for e in entries]==[3,5]
out=root/'analysis/previews/ayame-review01';out.mkdir(exist_ok=True)
clips=root/'analysis/previews/god-vfx-ingame/clips'
for e in entries:
    for rel in [e['gif'],*e['frames']]:
        shutil.copy2(clips/Path(rel).name,out/Path(rel).name)
shutil.copy2(out/Path(entries[0]['frames'][2]).name,out/'tier1-no-dedicated-effect.png')
skills=json.loads((root/'scripts/god-art-skills.json').read_text(encoding='utf-8'))['ayame']
cards=[]
for tier,power in zip((1,3,5),skills):
    name,kind,summary,visual=power
    img='tier1-no-dedicated-effect.png' if tier==1 else Path(next(e['gif'] for e in entries if e['tier']==tier)).name
    note='1성은 자동 가호이며 전용 이펙트가 아직 없습니다. 아래는 순간 권능 효과를 지운 참고 화면으로, 1성 발동 순간이나 강화 중첩을 입증하는 캡처는 아닙니다.' if tier==1 else '실제 성공한 권능 직후의 두 프레임을 느리게 반복한 보존 캡처입니다. 전체 공격 과정 영상은 아닙니다.'
    cards.append(f'<section><h2>{tier}성 · {html.escape(name)} · {kind}</h2><p>{html.escape(summary)}</p><p><b>현재 표시:</b> {html.escape(visual)}</p><p class="note">{note}</p><img src="{img}"></section>')
doc='<!doctype html><html lang="ko"><meta charset="utf-8"><title>아야메 1·3·5성 현재 이펙트</title><style>body{background:#111923;color:#eff2ff;font:17px "Malgun Gothic";margin:26px;max-width:1000px}p{line-height:1.7}section{background:#202b3b;padding:20px;margin:24px 0}img{image-rendering:pixelated;max-width:100%}.note{color:#b9c5d8}</style><h1>아야메 · 현재 이펙트 점검</h1><p>후부키 VFX05 승인 완료. 다음 아야메의 현재 화면을 확인합니다. 이 페이지는 기존 실제 SDL 테스트 전투장 캡처를 모았습니다. 아야메 전용 신규 연출을 만든 상태는 아닙니다. 높은 자원·고정 장비를 사용한 테스트이며 일반 던전 플레이 영상과 다릅니다.</p>'+''.join(cards)+'</html>'
(out/'index.html').write_text(doc,encoding='utf-8')
ledger={'status':'passed','kind':'existing-native-capture-review','source':'analysis/native/god-vfx-capture05/gallery-validation.json','noDedicatedTier1Effect':True,'tier1ImageIsReferenceOnly':True,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}}
(out/'provenance.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj.update(currentVisualReviewGod='ayame',fubukiVisualFeedback='User accepted Fubuki VFX05 including damaged-enemy foxfire on 2026-10-21',ayameVisualReview='analysis/previews/ayame-review01/index.html',next='Review Ayame tier1/3/5 current native visuals. Suisei/Miko/Aki/Fubuki accepted; do not alter approved visuals or restart bot work.')
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 최신: 후부키 VFX05 승인 / 아야메 현재 이펙트 점검 (2026-10-21)\n\n뭇별이 후부키 적 피격 여우불을 포함한 VFX05를 승인했다. 다음 아야메 1·3·5성 현재 화면은 analysis/previews/ayame-review01/index.html. 기존 capture05 실제 SDL 자료를 모았으며 1성은 전용 효과가 없어 효과 제거 후 참고 화면만 제공한다. 3·5성은 현재 효과이고 신규 제작 전이다. 스이세이·미코·아키·후부키 승인 유지. 다음은 아야메 피드백이다.\n\n---\n\n'
p=root/'START_HERE_HOME.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
print(out/'index.html')
