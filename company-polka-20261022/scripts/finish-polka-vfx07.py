from pathlib import Path
from PIL import Image
import json, hashlib, re, shutil

r = Path(__file__).resolve().parents[1]
base = r / 'analysis/native/polka-vfx07'
src = r / 'engine/campaign-crawl/crawl-ref/source'
proof = json.loads((base/'capture-validation.json').read_text(encoding='utf-8-sig'))
assert proof['status'] == 'passed' and proof['freshProcessRestore']
for name, digest in json.loads((base/'preserved-files.json').read_text()).items():
    assert hashlib.sha256((src/name).read_bytes()).hexdigest() == digest, name
out = r/'analysis/previews/polka-vfx07'
out.mkdir(parents=True, exist_ok=True)
shots = base/'native/shots'
for option in range(3):
    first = sorted(shots.glob(f'polka-tier5-option{option}-*-frame0.png'))[0]
    frames = []
    for f in range(2):
        p = first.with_name(first.name.replace('frame0',f'frame{f}'))
        frames.append(Image.open(p).convert('RGB').crop((275,244,499,436)).resize((448,384),Image.Resampling.NEAREST))
    frames[0].save(out/f'polka5-option{option}.gif',save_all=True,append_images=frames[1:],duration=420,loop=0,optimize=False)
p = r/'analysis/previews/polka-review01/index.html'
s = p.read_text(encoding='utf-8').replace('../polka-vfx06/', '../polka-vfx07/').replace('5성은 불꽃·커튼·소용돌이로 나누고 크기를 줄인 새 검토본입니다.', '5성 불꽃·커튼·소용돌이를 이전보다 약 15% 더 줄인 검토본입니다.')
for option in range(3):
    s = re.sub(rf'polka-tier5-option{option}-\d+\.gif',f'../polka-vfx07/polka5-option{option}.gif',s)
s = s.replace('3·5성은 기존 검토본입니다.','1·3성 승인 완료. 5성 불꽃·커튼·소용돌이 전체 크기를 VFX06보다 약 15% 더 줄인 검토본입니다.')
s = s.replace('아래 시연은 박수3을 미리 준비한 시험 장면입니다.','불꽃 피날레는 작은 불꽃 폭발과 색종이, 커튼콜은 열린 붉은 커튼과 회복 반짝임, 대혼란은 보라·파랑 회전 화살표로 구분했습니다. 아래 시연은 박수3을 미리 준비한 시험 장면입니다.')
p.write_text(s,encoding='utf-8')
p = r/'analysis/previews/all-gods-vfx-draft04/index.html'
s = p.read_text(encoding='utf-8').replace('../polka-vfx06/', '../polka-vfx07/').replace('5성은 불꽃·커튼·소용돌이로 나누고 크기를 줄인 새 검토본입니다.', '5성 불꽃·커튼·소용돌이를 이전보다 약 15% 더 줄인 검토본입니다.'); m = re.search(r'const data=(.*?);function choose',s);d = json.loads(m[1])
for e in d['polka']:
    if e['tier'] == 5:
        e['image'] = f"../polka-vfx07/polka5-option{e['option']}.gif"
        e['kind'] = '5성 전용 소형 연출 · 불꽃/커튼/혼란 구분 · 실제 SDL 새 캡처'
s = s[:m.start(1)] + json.dumps(d,ensure_ascii=False) + s[m.end(1):];p.write_text(s,encoding='utf-8')
shutil.copy2(base/'capture-engine.exe',r/'runtime/tiles01/HoloCrawl.exe')
digest = hashlib.sha256((base/'capture-engine.exe').read_bytes()).hexdigest()
p = r/'VFX_DRAFT_STATUS.json';d = json.loads(p.read_text(encoding='utf-8-sig'))
d['tierApprovals']['polka'].update(pendingRevision='polka-vfx07',tier5Revision='polka-vfx07',approved=[1,3],pending=[5])
d['next'] = 'Review Polka tier5 compact fireworks, curtain heal and confusion effects.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(visualRevision='polka-vfx07',playBinarySha256=digest,next='Polka tier5 VFX06 review; tiers1/3 approved.');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 폴카 5성 축소·구분 / polka-vfx07\n\n불꽃 피날레는 고리 대신 불꽃·색종이 폭발, 커튼콜은 열린 붉은 커튼·회복 반짝임, 대혼란은 보라·파랑 회전 화살표와 별. 160px 캔버스 안 실제 도트 54~65px로 추가 축소 (VFX06 대비 약 15%). 실제 판정 범위·전투 소스 불변, 1·3성 승인 유지. 5성 사용자 검토 대기. 검토: analysis/previews/polka-review01/index.html#tier5\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
manifest=dict(status='passed',revision='polka-vfx07',numericChanges=False,sourceAndUnrelatedArtPreserved=True,binarySha256=digest,validation=proof,approvedTiers=[1,3],pendingTiers=[5])
(base/'checkpoint-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
