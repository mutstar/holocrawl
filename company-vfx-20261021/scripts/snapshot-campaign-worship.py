"""Freeze the verified campaign membership delta without touching balance01."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--run',default='native10')
ap.add_argument('--regression',default='combat-regression02')
a=ap.parse_args()
folder=ROOT/'analysis/native/worship01'
run=folder/a.run
proof=json.loads((run/'validation.json').read_text())
reload=json.loads((run/'validation.json.reload.json').read_text())
regression=json.loads((folder/(a.regression+'.validation.json')).read_text())
assert proof['status']==reload['status']==regression['status']=='passed'
assert proof['nativePlayerTagRoundtrips']==176 and reload['freshProcessRestore']
manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8-sig'))
assert manifest['binarySha256']==regression['binarySha256']
source=ROOT/'engine/campaign-crawl/crawl-ref/source'
base=ROOT/'engine/balance-crawl/crawl-ref/source'
names=['Makefile.obj','god-prayer.cc','religion.cc','main.cc','output.cc','tags.cc',
       'startup.cc','player.cc','chardump.cc','holo-worship.h','holo-worship.cc']
snapshot=folder/'source_snapshot'
assert not snapshot.exists(),'Preserve the previous source snapshot'
patch=ROOT/'engine/patches/worship01-from-balance01.patch'
assert not patch.exists(),'Preserve the previous source patch'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()
assert digest(source/'crawl.exe')==manifest['buildSha256'],'Rebuilt after tests'
lines=[]
for name in names:
    before=(base/name).read_text(encoding='utf-8').splitlines(keepends=True) if (base/name).exists() else []
    after=(source/name).read_text(encoding='utf-8').splitlines(keepends=True)
    assert before!=after,name
    path='crawl-ref/source/'+name
    lines.append(f'diff --git a/{path} b/{path}\n')
    if not before:
        lines.append('new file mode 100644\n')
    lines.extend(difflib.unified_diff(before,after,fromfile='a/'+path if before else '/dev/null',tofile='b/'+path))
patch.write_text(''.join(lines),encoding='utf-8',newline='\n')
subprocess.run(['git','apply','--check','--ignore-space-change',str(patch)],cwd=base.parents[1],check=True)
snapshot.mkdir()
for name in names:
    shutil.copy2(source/name,snapshot/name)
logs=folder/'build-logs'
logs.mkdir(exist_ok=True)
for path in ROOT.parent.glob('campaign-build*.log'):
    shutil.copy2(path,logs/path.name)
shutil.copy2(ROOT.parent/'extracted-integrity.log',folder/'extracted-integrity.log')
state=dict(version='worship01',phase='membership-save-foundation-verified',
           savedAtUtc=datetime.now(timezone.utc).isoformat(),
           sourceDirectory='engine/campaign-crawl/crawl-ref/source',
           originalBalanceSourcePreserved=True,transferredBaselineFilesVerified=91420,
           baseBalancePatchSha256='12EB0A3291D0A1478A74372E862DC66A42BD1B124E5964D2A6F2BC7D3BDBAB78',
           incrementalPatch='engine/patches/worship01-from-balance01.patch',
           incrementalPatchSha256=digest(patch),
           sourceSha256={name:digest(source/name) for name in names},
           buildSha256=manifest['buildSha256'],binarySha256=manifest['binarySha256'],
           validation=str((run/'validation.json').relative_to(ROOT)).replace('\\','/'),
           freshProcessValidation=str((run/'validation.json.reload.json').relative_to(ROOT)).replace('\\','/'),
           combatRegression=f'analysis/native/worship01/{a.regression}.validation.json',
           normalCombatAbilitiesConnected=False,pietyIncomeConnected=False,
           holoWrathDeliveryConnected=False,giftsConnected=False,
           nativeCoreEffectPersistenceConnected=False,
           next='Connect Noel manual abilities to authoritative saved effect/cooldown state; then level-local summons/hazards/debt and the other cores.')
(ROOT/'engine/campaign_status.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
exclusions=dict(failedOrStoppedRuns={
    'native01':'No Windows input console; no report produced.',
    'native02':'Harness used inverted 0.24 buffered EOF helper.',
    'native03':'Combat fixture MP200 exceeds native signed-byte saved maximum MP.',
    'native04':'Harness restored into existing player and accumulated native exercise lists.',
    'native05':'Fresh-player reset correctly rejected an open fixture memory package.',
    'native06':'Harness omitted the native CHR metadata required before TAG_YOU.',
    'native07':'Harness advanced its clock past native timers without executing a world step.',
    'native08':'176 tag roundtrips passed; stopped when lowercase y failed native uppercase confirmation.'},
    intermediatePassedRuns={'native09':'Before saved-game browser description fix; retained, superseded by final native10.',
                            'combat-regression01':'322 exact rows on the native09 binary; retained.'},
    finalRun=a.run,finalCombatRegression=a.regression)
(folder/'development_exclusions.json').write_text(json.dumps(exclusions,indent=2)+'\n',encoding='utf-8')
doc=ROOT/'START_HERE_CAMPAIGN.md'
text=doc.read_text(encoding='utf-8').replace('worship01/native09/','worship01/'+a.run+'/').replace('worship01/combat-regression01.','worship01/'+a.regression+'.')
text=text.replace('native01~08은 개발 중 실패/중단 자료로 보존했다.',
                  'native01~08은 개발 중 실패/중단 자료로 보존했다. native09는 저장 목록 표시 보완 이전의 통과본으로 별도 보존했다.')
doc.write_text(text,encoding='utf-8')
print(json.dumps(dict(status='saved',patch=state['incrementalPatch'],files=len(names),validation=state['validation']),indent=2))
