from pathlib import Path
from PIL import Image
import json,difflib,hashlib
r=Path(__file__).resolve().parents[1];rev='miko-bloom01';b=r/'analysis/native'/rev
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
proof=read(b/'native/miko-bloom.json');assert proof['status']=='passed' and not proof['combatImplemented']
v=read(b/'capture-validation.json');assert v['status']=='passed'
assert read(b/'native/validation.json')['gods']==22
assert read(b/'native/reload.json')['status']=='passed'
out=r/'analysis/previews'/rev;out.mkdir(exist_ok=False)
for mode,name in [(1,'heal'),(2,'overflow-shield')]:
    images=[]
    for frame in range(7):
        p=b/f'native/shots/miko-bloom-{mode}-{frame}.png'
        im=Image.open(p).convert('RGB').crop((291,244,483,404)).resize((576,480),Image.Resampling.NEAREST)
        im.save(out/f'{name}-{frame}.png');images.append(im)
    images[0].save(out/f'{name}.gif',save_all=True,append_images=images[1:],duration=[750,220,220,220,350,1200,650],loop=0)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>미코2성 · 봉납의 벚꽃 이펙트 시안</title><style>body{background:#101923;color:#edf3ff;font:17px "Malgun Gothic",sans-serif;max-width:960px;margin:28px auto;padding:0 20px;line-height:1.8}section{background:#1d2b3d;padding:20px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}h1,h2{color:#ffcadc}</style><h1>미코2성 — 봉납의 벚꽃 [패시브] · 이펙트 시안</h1><p>실제 SDL 필드에 새 도트를 렌더링한 시안입니다. 적 처치·HP 회복·보호막 흡수 전투 처리는 아직 연결하지 않았습니다. 화면의 적은 위치 확인용으로 남아 있습니다. 프레임과 상태 표시만 검사장 전용 설정으로 제어합니다.</p><section><h2>회복 연출</h2><img src="heal.gif"><p>적 쪽에서 작은 벚꽃 세 송이가 캐릭터에게 모이고 짧게 사라집니다.</p></section><section><h2>초과 회복 → 벚꽃 보호막 연출</h2><img src="overflow-shield.gif"><p>같은 벚꽃 회수 뒤 캐릭터 머리 오른쪽에 분홍 꽃무늬 방패가 남습니다. 몬스터와 바닥 표식에 섞이지 않도록 위쪽에 배치했습니다.</p></section><section><h2>예정 수치 — 아직 미구현</h2><p>신앙50 해금 예정, 최소 기도술 없음, 추가 자원·행동 소모 없음. 자신과 적이 모두 성역 안일 때 경험치 대상 적을 직접 처치하면2+floor(기도술/6) HP 회복. 발동 간격20aut. 초과 회복 보호막 상한4+floor(기도술/3), 지속50aut, 성역 밖으로 나가면 해제.</p></section><p>일반 실행본은 승인된 miko-torii03을 유지합니다. 이번 결과는 전투 효과가 아닌 미리보기 전용입니다.</p></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
design=dict(status='native-visual-draft',combatImplemented=False,runtimeDeployed=False,date='2026-11-03',revision=rev,review=f'analysis/previews/{rev}/index.html',tier=2,type='passive',name='봉납의 벚꽃',art='Generated sakura blossom travels to player; generated pink floral shield persists beside upper-right head in overflow draft.',proposedPiety=50,heal='2+floor(Inv/6)',shieldCap='4+floor(Inv/3)',procIntervalAut=20,shieldDurationAut=50,proof=proof)
(r/'analysis/design/miko-bloom01.json').write_text(json.dumps(design,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update(d):
    d.update(currentGod='miko',currentVisualReviewGod='miko',currentVisualReviewTier=2,currentVisualReview=design['review'],activeWork='miko-tier2-bloom-visual-draft-review',mikoBloomDraft=design,lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=design['review']
    d['next']='Review Miko2-star blossom recovery/petal shield visual draft. No kill/heal/shield mechanics integrated yet. Approved normal runtime remains miko-torii03;5/5/7 and torii unchanged.'
    if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
    p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\miko-bloom01\\index.html"\r\n',encoding='ascii')
note='# 미코2성 봉납의 벚꽃 이펙트 시안 / 2026-11-03\n\nanalysis/previews/miko-bloom01/index.html. 실제SDL필드에서 검사장 전용 props로 벚꽃3개 이동→소멸 / 이동→분홍 꽃무늬 방패 표시. 회복·보호막 전투처리 미구현. 적은 위치표시용으로 남음. 일반runtime=miko-torii03 유지. 시안캡처 상태/RNG불변·22신 회귀·저장복원 통과. 다음은 시각 피드백 후2성 실제처리 연결.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
patch=''
for old in (b/'before').rglob('*'):
    if old.is_file():
        rel=old.relative_to(b/'before');new=r/'engine/campaign-crawl/crawl-ref/source'/rel
        patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),new.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(b/'source.patch').write_text(patch,encoding='utf-8')
(b/'checkpoint-manifest.json').write_text(json.dumps(dict(status='passed',revision=rev,runtimeDeployed=False,combatImplemented=False,binarySha256=hashlib.sha256((b/'capture-engine.exe').read_bytes()).hexdigest(),nativeProof=proof,validation=v),indent=2),encoding='utf-8')
print(json.dumps(dict(status='passed',review=design['review'],runtimeDeployed=False,combatImplemented=False)))
