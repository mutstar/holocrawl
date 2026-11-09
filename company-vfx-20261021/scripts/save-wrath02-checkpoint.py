"""Freeze the tested native wrath update, retaining the previous art checkpoint."""
from pathlib import Path
import datetime,difflib,hashlib,json,shutil
root=Path(__file__).resolve().parents[1]
out=root/'analysis/native/wrath02';out.mkdir(parents=True,exist_ok=True)
src=root/'engine/campaign-crawl/crawl-ref/source'
sdl=root/'engine/tiles-crawl/crawl-ref/source'
base=root/'engine/balance-crawl/crawl-ref/source'
previous=root/'analysis/native/combat-art01/checkpoint.json'
state=json.loads(previous.read_text(encoding='utf-8'))
core=root/'analysis/native/campaign-abilities01/wrath02-console02'
gui=root/'analysis/native/tiles01/wrath02-sdl01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for fixture in [core,gui]:
    for name in ['validation.json','tiles-model.json','reload.json','membership.json','membership.json.reload.json','manifest.json','wrath02-validation.json','wrath02-save.json']:
        assert read(fixture/name)['status']=='passed',(fixture,name)
    proof=read(fixture/'wrath02-validation.json')
    assert proof['nativeProfiles']==25 and proof['nativeAttackTrials']==800
    assert read(fixture/'wrath02-save.json')['nativeServantKinds']==5
assert read(out/'legacy-save/manifest.json')['nextWorldStepExact']
assert read(out/'fixed-combat-final.validation.json')['exactRows']==322
assert read(gui/'visual-capture.json')['screenshots']==14
assert read(core/'manifest.json')['buildSha256']==sha(src/'crawl.exe')
# Deploy the exact stripped bytes already exercised by the SDL fixtures.
shutil.copy2(gui/'tiles-engine.exe',root/'runtime/tiles01/HoloCrawl.exe')
assert sha(root/'runtime/tiles01/HoloCrawl.exe')==read(gui/'manifest.json')['binarySha256']
names=sorted(state['sourceSha256']);hashes={};changed=[];patch=[];delta=[]
for name in names:
    p=src/name;assert p.read_bytes()==(sdl/name).read_bytes(),name
    dest=out/'source_snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    hashes[name]=sha(p)
    if state['sourceSha256'][name]!=hashes[name]:
        changed.append(name)
        prior=previous.parent/'source_snapshot'/name
        delta.extend(difflib.unified_diff(prior.read_text(encoding='utf-8').splitlines(keepends=True),p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    if p.suffix!='.png':
        old=base/name
        before=old.read_text(encoding='utf-8').splitlines(keepends=True) if old.exists() else []
        patch.extend(difflib.unified_diff(before,p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='a/'+name if old.exists() else '/dev/null',tofile='b/'+name))
patchpath=root/'engine/patches/wrath02-source-from-balance01.patch'
patchpath.write_text(''.join(patch),encoding='utf-8',newline='\n')
(out/'wrath02-from-combat-art01.patch').write_text(''.join(delta),encoding='utf-8',newline='\n')
atlas=out/'generated_atlas_snapshot';atlas.mkdir(exist_ok=True)
for p in (sdl/'dat/tiles').glob('*.png'):shutil.copy2(p,atlas/p.name)
for p in (sdl/'rltiles').glob('tiledef-*'):
    if p.suffix in {'.h','.cc'}:shutil.copy2(p,atlas/p.name)
for name in ['save-wrath02-checkpoint.py','test-wrath02-legacy.ps1','verify-wrath02.py','test-campaign-abilities.ps1','test-campaign-tiles.ps1','prepare-tiles-source.py']:
    dest=out/'tool_snapshot'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(root/'scripts'/name,dest)
state.update(version='wrath02',phase='native-style-apostasy-wrath',savedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=hashes,changedFilesThisStage=changed,previousCheckpoint=previous.relative_to(root).as_posix(),incrementalPatch=patchpath.relative_to(root).as_posix(),incrementalPatchSha256=sha(patchpath),consoleBuildSha256=sha(src/'crawl.exe'),buildSha256=sha(src/'crawl.exe'),tilesBuildSha256=sha(sdl/'crawl.exe'),playBinarySha256=sha(root/'runtime/tiles01/HoloCrawl.exe'),consoleFixture=core.relative_to(root).as_posix(),tilesFixture=gui.relative_to(root).as_posix(),capture=gui.relative_to(root).as_posix(),combatRegression='analysis/native/wrath02/fixed-combat-final.validation.json',report='analysis/native/wrath02/RESULTS_KO.md',assetValidation='analysis/native/wrath02/render-validation.json',nativeWrathProfiles=25,nativeWrathAttackTrialsPerBackend=800,legacyWrathSave='analysis/native/wrath02/legacy-save/manifest.json',generatedAtlasSha256={p.name:sha(p) for p in atlas.glob('*.png')})
for p in [out/'checkpoint.json',root/'engine/campaign_status.json']:
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefix='# 배교 징벌 조정 — wrath02 / 2026-10-20\n\n0.24 원작 징벌을 기준으로 22신 배교 효과를 강화했다. 새 배교는 18~26회 또는 두 XL 구간 XP 빚을 남기고, 각 발동은 현재 XL을 사용한다. 소환수는 20~33.5턴 유지하며 후부키는 공격 여우와 미끼를 함께 소환한다. 계단으로 이미 나온 소환수가 지워지지 않는다. 이전 저장의 진행 중 효과와 남은 빚은 보존한다. 문자·SDL 각각 소환수 25프로필/실제 공격 800회, 5종 저장 복원, 이전 저장 이어하기, 기존 전투 322개 비교를 통과했다. 실행은 `PLAY_HOLOCRAWL.cmd`. 상세 수치·검증 범위는 `analysis/native/wrath02/RESULTS_KO.md`. 아래는 이전 이력이다.\n\n---\n\n'
for p in [root/n for n in ['START_HERE_CAMPAIGN.md','CONTINUE_HERE.md','START_HERE_COMPANY.md','HOLOCRAWL_DESIGN.md','engine/README.md']]+[root.parent.parent/'HoloCrawl/CONTINUE_HERE.md']:
    if p.exists() and not p.read_text(encoding='utf-8').startswith('# 배교 징벌 조정 — wrath02'):
        p.write_text(prefix+p.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps(dict(status='passed',changed=changed,playBinarySha256=state['playBinarySha256'])))
