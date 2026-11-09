from pathlib import Path
import json,hashlib,shutil,difflib,datetime
root=Path(__file__).resolve().parents[1]
out=root/'analysis/native/combat-art01';out.mkdir(parents=True,exist_ok=True)
src=root/'engine/campaign-crawl/crawl-ref/source';sdl=root/'engine/tiles-crawl/crawl-ref/source';base=root/'engine/balance-crawl/crawl-ref/source'
previous=root/'analysis/native/altars05/checkpoint.json'
state=json.loads(previous.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
names=sorted(set(state['sourceSha256'])|{'tiledgnbuf.cc','rltiles/dc-player.txt','rltiles/dc-holo-player.txt'}|{p.relative_to(src).as_posix() for p in (src/'rltiles/holo').glob('*.png')})
hashes={};changed=[];patch=[]
for name in names:
    p=src/name;assert p.read_bytes()==(sdl/name).read_bytes(),name
    dest=out/'source_snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    hashes[name]=sha(p)
    if state['sourceSha256'].get(name)!=hashes[name]:changed.append(name)
    if p.suffix!='.png':
        original=base/name
        before=original.read_text(encoding='utf-8').splitlines(keepends=True) if original.exists() else []
        patch.extend(difflib.unified_diff(before,p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='a/'+name if original.exists() else '/dev/null',tofile='b/'+name))
patchpath=root/'engine/patches/combat-art01-source-from-balance01.patch'
patchpath.write_text(''.join(patch),encoding='utf-8',newline='\n')
gui=root/'analysis/native/tiles01/combat-art01-sdl-final03'
for name in ['validation.json','tiles-model.json','reload.json','membership.json','membership.json.reload.json','visual-capture.json','manifest.json']:
    assert json.loads((gui/name).read_text(encoding='utf-8-sig'))['status']=='passed',name
assert sha(gui/'tiles-engine.exe')==sha(root/'runtime/tiles01/HoloCrawl.exe')
atlas=out/'generated_atlas_snapshot';atlas.mkdir(exist_ok=True)
for p in (sdl/'dat/tiles').glob('*.png'):shutil.copy2(p,atlas/p.name)
for p in (sdl/'rltiles').glob('tiledef-*'):
    if p.suffix in {'.h','.cc'}:shutil.copy2(p,atlas/p.name)
for name in ['import-combat-art01.py','save-combat-art01-checkpoint.py','prepare-tiles-source.py','test-campaign-tiles.ps1']:
    dest=out/'tool_snapshot'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(root/'scripts'/name,dest)
core=root/'analysis/native/campaign-abilities01/combat-art01-console-final04'
assert json.loads((core/'manifest.json').read_text(encoding='utf-8-sig'))['buildSha256']==sha(src/'crawl.exe')
assert json.loads((out/'fixed-combat-final.validation.json').read_text())['exactRows']==322
state.update(version='combat-art01',phase='summons-effects-badges-human-avatar-and-faith-charms',savedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=hashes,changedFilesThisStage=changed,previousCheckpoint=previous.relative_to(root).as_posix(),incrementalPatch=patchpath.relative_to(root).as_posix(),incrementalPatchSha256=sha(patchpath),consoleBuildSha256=sha(src/'crawl.exe'),buildSha256=sha(src/'crawl.exe'),tilesBuildSha256=sha(sdl/'crawl.exe'),playBinarySha256=sha(root/'runtime/tiles01/HoloCrawl.exe'),consoleFixture='analysis/native/campaign-abilities01/combat-art01-console-final04',tilesFixture=gui.relative_to(root).as_posix(),capture=gui.relative_to(root).as_posix(),rgbaTiles=123,nativeScreenshots=14,combatArtTiles=74,combatRegression='analysis/native/combat-art01/fixed-combat-final.validation.json',pixelArtScope='5 creatures x2 frames, 16 sparse effects x2 frames, 8 corner status marks, 2 equipment-compatible human bases and 22 faith charms; previous altars retained.',report='analysis/native/combat-art01/RESULTS_KO.md',assetValidation='analysis/native/combat-art01/render-validation.json',generatedAtlasSha256={p.name:sha(p) for p in atlas.glob('*.png')})
for p in [out/'checkpoint.json',root/'engine/campaign_status.json']:p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((root/'assets/holocrawl/combat-art01/manifest.json').read_text(encoding='utf-8'))
from PIL import Image
for a in manifest['assets']:
    p=root/a['path'];im=Image.open(p)
    assert im.mode=='RGBA' and im.size==(32,32) and im.getchannel('A').getextrema()[0]==0 and sha(p)==a['sha256']
gallery=json.loads((gui/'god-altars.png.json').read_text(encoding='utf-8'))
assert gallery['boundAltars']==22 and gallery['seenCells']==225
proof=dict(status='passed',distinctAltarTiles=22,trackedSourceAndAssetFiles=len(names),sourceSnapshotsMatch=True,SDLSourceMatches=True,nativeGalleryBoundAltars=gallery['boundAltars'],playBinarySha256=state['playBinarySha256'])
(out/'asset-validation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
prefix='# 전투 도트·효과 통합 — combat-art01 / 2026-10-20\n\n소환물 5종 2프레임, 권능 범위 효과 16종 2프레임, 상태 아이콘 8개, 인간 기본 체형 2종과 22신 표식을 연결했다. 32×32 타일이며 장비·비인간 종족·변신의 원래 레이어를 유지한다. 제단은 이전 단계 그대로다. 실행은 기존 `PLAY_HOLOCRAWL.cmd`. 검사·화면·원화는 `analysis/native/combat-art01/RESULTS_KO.md`, `assets/holocrawl/combat-art01/` 참조. 아래는 이전 이력이다.\n\n---\n\n'
for path in [root/n for n in ['START_HERE_CAMPAIGN.md','CONTINUE_HERE.md','START_HERE_COMPANY.md','HOLOCRAWL_DESIGN.md','engine/README.md']]+[root.parent.parent/'HoloCrawl/CONTINUE_HERE.md']:
    if path.exists() and not path.read_text(encoding='utf-8').startswith('# 전투 도트·효과 통합'):
        path.write_text(prefix+path.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(proof))
