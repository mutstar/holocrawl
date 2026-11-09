from pathlib import Path
import json,hashlib,shutil,difflib,datetime
root=Path(__file__).resolve().parents[1]
out=root/'analysis/native/altars05';out.mkdir(parents=True,exist_ok=True)
src=root/'engine/campaign-crawl/crawl-ref/source';sdl=root/'engine/tiles-crawl/crawl-ref/source';base=root/'engine/balance-crawl/crawl-ref/source'
previous=root/'analysis/native/altars04/checkpoint.json'
state=json.loads(previous.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
names=sorted(set(state['sourceSha256'])|{p.relative_to(src).as_posix() for p in (src/'rltiles/holo').glob('*.png')})
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
patchpath=root/'engine/patches/altars05-source-from-balance01.patch'
patchpath.write_text(''.join(patch),encoding='utf-8',newline='\n')
gui=root/'analysis/native/tiles01/altars05-sdl'
for name in ['validation.json','tiles-model.json','reload.json','membership.json','membership.json.reload.json','visual-capture.json','manifest.json']:
    assert json.loads((gui/name).read_text(encoding='utf-8-sig'))['status']=='passed',name
assert sha(gui/'tiles-engine.exe')==sha(root/'runtime/tiles01/HoloCrawl.exe')
atlas=out/'generated_atlas_snapshot';atlas.mkdir(exist_ok=True)
for p in (sdl/'dat/tiles').glob('*.png'):shutil.copy2(p,atlas/p.name)
for p in (sdl/'rltiles').glob('tiledef-*'):
    if p.suffix in {'.h','.cc'}:shutil.copy2(p,atlas/p.name)
for name in ['import-holo-altars05.py','save-altars05-checkpoint.py']:
    dest=out/'tool_snapshot'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(root/'scripts'/name,dest)
state.update(version='altars05',phase='physical-comet-spirit-and-noh-mask-shrines',savedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=hashes,changedFilesThisStage=changed,previousCheckpoint=previous.relative_to(root).as_posix(),incrementalPatch=patchpath.relative_to(root).as_posix(),incrementalPatchSha256=sha(patchpath),consoleBuildSha256=sha(src/'crawl.exe'),buildSha256=sha(src/'crawl.exe'),tilesBuildSha256=sha(sdl/'crawl.exe'),playBinarySha256=sha(root/'runtime/tiles01/HoloCrawl.exe'),consoleFixture='analysis/native/campaign-abilities01/altars01-console',tilesFixture=gui.relative_to(root).as_posix(),capture=gui.relative_to(root).as_posix(),rgbaTiles=86,pixelArtScope='Physical altar architecture for Suisei comet and Mela onibi; Raden Noh mask shrine; 19 other altar sprites unchanged from altars04.',report='analysis/native/altars05/RESULTS_KO.md',assetValidation='analysis/native/altars05/asset-validation.json',generatedAtlasSha256={p.name:sha(p) for p in atlas.glob('*.png')})
for p in [out/'checkpoint.json',root/'engine/campaign_status.json']:p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((root/'assets/holocrawl/altars05/manifest.json').read_text(encoding='utf-8'))
from PIL import Image
for a in manifest['assets']:
    p=root/a['path'];im=Image.open(p)
    assert im.mode=='RGBA' and im.size==(32,32) and im.getchannel('A').getextrema()[0]==0 and sha(p)==a['sha256']
gallery=json.loads((gui/'god-altars.png.json').read_text(encoding='utf-8'))
assert gallery['boundAltars']==22 and gallery['seenCells']==225
proof=dict(status='passed',distinctAltarTiles=22,trackedSourceAndAssetFiles=len(names),sourceSnapshotsMatch=True,SDLSourceMatches=True,nativeGalleryBoundAltars=gallery['boundAltars'],playBinarySha256=state['playBinarySha256'])
(out/'asset-validation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
prefix='# 혜성·도깨비불·라덴 가면 제단 수정 — altars05 / 2026-10-20\n\n스이세이 혜성에 천문 제단을, 메라 도깨비불에 목제 감실을 붙였다. 라덴은 흰 노멘을 모신 녹색·금색 목제 제단이다. 나머지 19개는 altars04와 바이트 단위로 같다. 기존 메뉴 문양은 유지하며 저장된 신 ID로 새 제단을 선택한다. 실행은 기존 `PLAY_HOLOCRAWL.cmd`. 검사·화면·원화는 `analysis/native/altars05/RESULTS_KO.md`, `assets/holocrawl/altars05/` 참조. 아래는 이전 이력이다.\n\n---\n\n'
for path in [root/n for n in ['START_HERE_CAMPAIGN.md','CONTINUE_HERE.md','START_HERE_COMPANY.md','HOLOCRAWL_DESIGN.md','engine/README.md']]+[root.parent/'HoloCrawl/CONTINUE_HERE.md']:
    if path.exists() and not path.read_text(encoding='utf-8').startswith('# 혜성·도깨비불·라덴 가면 제단 수정'):
        path.write_text(prefix+path.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(proof))
