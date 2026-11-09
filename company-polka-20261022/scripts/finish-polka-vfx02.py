from pathlib import Path
from PIL import Image
import hashlib, json, re, shutil

root = Path(__file__).resolve().parents[1]
base = root / 'analysis/native/polka-vfx02'
src = root / 'engine/campaign-crawl/crawl-ref/source'
proof = json.loads((base / 'capture-validation.json').read_text(encoding='utf-8-sig'))
assert proof['status'] == 'passed' and proof['freshProcessRestore']
for name, digest in json.loads((base / 'preserved-files.json').read_text()).items():
    assert hashlib.sha256((src / name).read_bytes()).hexdigest() == digest, name
preview = root / 'analysis/previews/polka-vfx02'
preview.mkdir(parents=True, exist_ok=True)
shots = base / 'native/shots'
used = {}
for option in (1, 2, 3):
    files = sorted(shots.glob(f'polka-tier1-option{option}-*-frame0.png'))
    assert files, option
    first = files[0]
    frames = [Image.open(first.with_name(first.name.replace('frame0', f'frame{f}'))).convert('RGB') for f in range(2)]
    # Preserve the native dungeon pixels; nearest-neighbour enlargement only.
    frames = [im.crop((283, 244, 459, 452)).resize((352, 416), Image.Resampling.NEAREST) for im in frames]
    frames[0].save(preview / f'polka-tier1-option{option}.gif', save_all=True, append_images=frames[1:], duration=450, loop=0, optimize=False)
    used[option] = first.name
page = root / 'analysis/previews/polka-review01/index.html'
s = page.read_text(encoding='utf-8').replace('../polka-vfx01/', '../polka-vfx02/').replace('밝은 분홍·크림색 광대 모자와 금빛 방울', '원본 의상의 빨강·파랑·검정 광대 모자와 금빛 방울')
for option in (1, 2, 3):
    s = re.sub(rf'polka-tier1-option{option}-\d+\.gif', f'../polka-vfx02/polka-tier1-option{option}.gif', s)
s = s.replace('기존 실제 SDL 캡처를 모았습니다. 이번 단계에서 새 도트를 만든 것은 아니며, 순간 효과 두 프레임을 반복하는 미리보기입니다.', '1성은 원본 의상의 빨강·파랑·검정 광대 모자와 금빛 방울로 교체하고 실제 게임에서 다시 캡처했습니다. 순간 효과 두 프레임을 반복합니다. 3·5성은 기존 검토본입니다.')
page.write_text(s, encoding='utf-8')
gallery = root / 'analysis/previews/all-gods-vfx-draft04/index.html'
s = gallery.read_text(encoding='utf-8').replace('../polka-vfx01/', '../polka-vfx02/')
m = re.search(r'const data=(.*?);function choose', s)
data = json.loads(m[1])
for entry in data['polka']:
    if entry['tier'] == 1:
        entry['image'] = f"../polka-vfx02/polka-tier1-option{entry['option']}.gif"
        entry['kind'] = '밝은 광대 모자 · 새 실제 SDL 캡처 · polka-vfx02'
s = s[:m.start(1)] + json.dumps(data, ensure_ascii=False) + s[m.end(1):]
# Replace the initially displayed image as well as the selection data.
s = re.sub(r'clips/polka-tier1-option1-\d+\.gif', '../polka-vfx02/polka-tier1-option1.gif', s)
gallery.write_text(s, encoding='utf-8')
shutil.copy2(base / 'capture-engine.exe', root / 'runtime/tiles01/HoloCrawl.exe')
digest = hashlib.sha256((base / 'capture-engine.exe').read_bytes()).hexdigest()
status = root / 'VFX_DRAFT_STATUS.json'
d = json.loads(status.read_text(encoding='utf-8-sig'))
d['tierApprovals']['polka'].update(pendingRevision='polka-vfx02', tier1Revision='polka-vfx02', feedback='1성 가시성 개선: 원본 의상의 빨강·파랑·검정 광대 모자와 금색 방울. 사용자 검토 대기.')
status.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for name in ('HOME_HANDOFF_STATE.json', 'engine/campaign_status.json'):
    p = root / name
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    d.update(visualRevision='polka-vfx02', playBinarySha256=digest, next='Review brighter Polka tier1; tiers1/3/5 pending user approval.')
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
note = '# 폴카 1성 가시성 개선 · polka-vfx02\n\n원본 의상의 빨강·파랑·검정 광대 모자와 금빛 방울. 32×32 타일 안 15×15 / 16×16 표시. 공연 세 종류 실제 SDL 재캡처, 렌더링 상태/RNG 불변·22신·새 프로세스 저장 복원 통과. 전투 소스·수치·라미 승인본 보존. 폴카 승인은 대기 중. 검토: analysis/previews/polka-review01/index.html#tier1\n\n아래는 이전 기록입니다.\n\n'
for name in ('CONTINUE_HERE.md', 'CURRENT_WORKSPACE.md', 'VFX_COMPANY_FEEDBACK.md', 'HOME_SESSION.md'):
    p = root / name
    if p.exists():
        p.write_text(note + p.read_text(encoding='utf-8-sig'), encoding='utf-8')
manifest = dict(status='passed', revision='polka-vfx02', numericChanges=False, gameplaySourcePreserved=True, otherArtPreserved=True, saveFormatChanged=False, binarySha256=digest, nativeFrames=used, validation=proof, review='analysis/previews/polka-review01/index.html#tier1', approved=False)
(base / 'checkpoint-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(manifest, ensure_ascii=False, indent=2))
