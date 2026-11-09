"""Record the VFX-only checkpoint after a successful native SDL fixture run."""
from pathlib import Path
from PIL import Image
import datetime, hashlib, json, shutil

root = Path(__file__).resolve().parents[1]
out = root/'analysis/native/god-vfx01'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest().upper()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert not (out/'validation.json').exists(), 'Preserve existing final verification'
source = root/'engine/campaign-crawl/crawl-ref/source'
tiles = root/'engine/tiles-crawl/crawl-ref/source'
fixture = root/'analysis/native/tiles01/god-vfx01-sdl01'
native = read(fixture/'manifest.json')
assert native['status']=='passed'
assert native['binarySha256']==sha(root/'runtime/tiles01/HoloCrawl.exe')
for name in ['validation.json','reload.json','membership.json','membership.json.reload.json','visual-capture.json']:
    assert read(fixture/name)['status']=='passed', name
status = read(root/'engine/campaign_status.json')
changed=[]
for name, expected in status['sourceSha256'].items():
    if sha(source/name)!=expected: changed.append(name)
assert set(changed)=={'holo-visual.cc','holo-visual.h','rltiles/dc-holo-feat.txt'}, changed
for name in changed:
    assert (source/name).read_bytes()==(tiles/name).read_bytes()
art=read(root/'assets/holocrawl/god-vfx01/manifest.json')
assert len(art['assets'])==20
for a in art['assets']:
    p=root/a['path']; image=Image.open(p)
    assert image.mode=='RGBA' and image.size==(32,32)
    assert sha(p)==a['sha256'] and a['centerOpaqueFraction']<0.35
    assert p.read_bytes()==(tiles/p.relative_to(source)).read_bytes()
gallery=read(root/'analysis/previews/current-god-art/mapping.json')
assert gallery['godCount']==22 and gallery['sharedImpactGods']==[]
assert read(root/'analysis/previews/current-god-art/skills-validation.json')['allTextFits']
proof=dict(status='passed',version='god-vfx01',baseGameVersion='wrath02',
    checkedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    themedGods=10,transparentFrames=20,allFramesDistinct=len({a['sha256'] for a in art['assets']})==20,
    changedPriorSourceFiles=changed,otherPriorSourceHashesRetained=True,
    nativeFixture=fixture.relative_to(root).as_posix(),nativeFixtureManifest=native,
    originalBinaryPreserved='analysis/native/god-vfx01/before/HoloCrawl.exe',
    binarySha256=sha(root/'runtime/tiles01/HoloCrawl.exe'),
    castingCueIsNotDamageFootprint=True,gardenReadyFloorConditionsMatched=True,
    galleryGods=22,skillSummaries=66,report='analysis/native/god-vfx01/VFX_REVIEW_KO.md',
    bespokePerAbilityAnimationsCompleted=False,invocationsIntensityScalingImplemented=False,
    campaignClearRateValidated=False,botWinrateWorkResumed=False)
write(out/'validation.json',proof)
shutil.copy2(root/'engine/campaign_status.json',out/'before/campaign_status.json')
shutil.copy2(root/'HOME_HANDOFF_STATE.json',out/'before/HOME_HANDOFF_STATE.json')
status.update(visualVersion='god-vfx01',visualCheckpoint=proof['report'],
    visualValidation='analysis/native/god-vfx01/validation.json',
    tilesBuildSha256=sha(tiles/'crawl.exe'),playBinarySha256=proof['binarySha256'],
    tilesFixture=fixture.relative_to(root).as_posix())
# Retain wrath02's sourceSha256 as the historical baseline; the VFX manifest
# records the new file hashes separately, rather than pretending it was unchanged.
write(root/'engine/campaign_status.json',status)
state=read(root/'HOME_HANDOFF_STATE.json')
state.update(visualVersion='god-vfx01',playBinarySha256=proof['binarySha256'],
    visualValidation='analysis/native/god-vfx01/validation.json',
    next='Manual play and VFX feedback. Per-ability/performance visual candidates are in VFX_REVIEW_KO.md; bot win-rate work remains deferred.')
write(root/'HOME_HANDOFF_STATE.json',state)
paths=[root/'scripts'/n for n in ['import-god-vfx01.py','finalize-god-vfx01.py','build-campaign-tiles.sh','prepare-tiles-source.py','package-home-wrath02.py','preview-current-god-art.py','god-art-skills.json']]
paths += [source/n for n in changed]+[root/a['path'] for a in art['assets']]+[root/'runtime/tiles01/HoloCrawl.exe']
write(out/'checkpoint-manifest.json',dict(version='god-vfx01',files=[dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]))
print(json.dumps(proof,ensure_ascii=False,indent=2))
