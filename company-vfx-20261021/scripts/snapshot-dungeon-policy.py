"""Save the completed policy comparison, preserving dungeon-pilot01."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/native/dungeon-pilot02'
SRC=ROOT/'engine/campaign-crawl/crawl-ref/source'
BASE=ROOT/'engine/balance-crawl/crawl-ref/source'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
proof=read(OUT/'final-comparison.json');assert proof['status']=='passed'
audit=read(OUT/'final-validation.json');assert audit['status']=='passed' and audit['cases']==81
control=read(OUT/'final-control-validation.json');assert control['status']=='passed' and control['cases']==3
reg=ROOT/'analysis/native/campaign-abilities01/dungeon-policy-regression03'
for n in ['validation.json','reload.json','membership.json','membership.json.reload.json','manifest.json']:
 assert read(reg/n)['status']=='passed'
manifest=read(reg/'manifest.json')
fixed=read(OUT/'fixed-combat-regression03.validation.json')
assert fixed['status']=='passed' and fixed['exactRows']==322 and fixed['binarySha256']==manifest['binarySha256']
assert sha(SRC/'crawl.exe')==proof['compiledBuildSha256']==audit['compiledBuildSha256']==control['compiledBuildSha256']==manifest['buildSha256']
old=read(ROOT/'analysis/native/dungeon-pilot01/checkpoint.json')
changed=[n for n,h in old['sourceSha256'].items() if sha(SRC/n)!=h]
assert changed==['holo-dungeon-test.cc'],changed
snapshot=OUT/'source_snapshot';assert not snapshot.exists()
snapshot.mkdir()
for n in old['sourceSha256']:shutil.copy2(SRC/n,snapshot/n)
patch=ROOT/'engine/patches/dungeon-pilot02-from-balance01.patch'
assert not patch.exists()
lines=[]
for n in sorted(old['sourceSha256']):
 before=(BASE/n).read_text(encoding='utf-8').splitlines(keepends=True) if (BASE/n).exists() else []
 after=(SRC/n).read_text(encoding='utf-8').splitlines(keepends=True)
 path='crawl-ref/source/'+n
 lines.append(f'diff --git a/{path} b/{path}\n')
 if not before:lines.append('new file mode 100644\n')
 lines.extend(difflib.unified_diff(before,after,fromfile='a/'+path if before else '/dev/null',tofile='b/'+path))
patch.write_text(''.join(lines),encoding='utf-8',newline='\n')
git=shutil.which('git') or str(ROOT/'.toolchain/msys64/usr/bin/git.exe')
subprocess.run([git,'apply','--check','--ignore-space-change',str(patch)],cwd=BASE.parents[1],check=True)
(OUT/'build-logs').mkdir()
for p in ROOT.glob('dungeon-policy-*.log'):shutil.copy2(p,OUT/'build-logs'/p.name)
for n in ['analysis/run_dungeon_pilot.py','analysis/audit_dungeon_pilot.py','analysis/compare_dungeon_policies.py','scripts/snapshot-dungeon-policy.py']:
 p=OUT/'tool_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
shutil.copy2(ROOT/'engine/campaign_status.json',OUT/'previous-campaign-status.json')
state=dict(old)
state.update(version='dungeon-pilot02',phase='equipment-retreat-policy-audited',savedAtUtc=datetime.now(timezone.utc).isoformat(),
 previousCheckpoint='analysis/native/dungeon-pilot01/checkpoint.json',
 buildSha256=manifest['buildSha256'],pilotMainBuildSha256=manifest['buildSha256'],
 incrementalPatch=str(patch.relative_to(ROOT)).replace('\\','/'),incrementalPatchSha256=sha(patch),
 sourceSha256={n:sha(SRC/n) for n in old['sourceSha256']},
 pilotValidation='analysis/native/dungeon-pilot02/final-validation.json',
 policyComparison='analysis/native/dungeon-pilot02/final-comparison.json',
 policyReport='analysis/native/dungeon-pilot02/RESULTS_POLICY02_KO.md',
 pilotPanels=['analysis/native/dungeon-pilot02/'+n for n in ['all22-03','natural-03','baseline-control04']],
 fixtureRegression='analysis/native/campaign-abilities01/dungeon-policy-regression03',
 combatRegression='analysis/native/dungeon-pilot02/fixed-combat-regression03.validation.json',
 realDungeonD1PilotCases=84,primaryPilotCases=81,baselineControlCases=3,activeStateSaveCases=0,
 priorActiveSaveValidation='analysis/native/dungeon-pilot01/active-save-validation.json',
 policy='equipment-retreat01',policySourceFilesChanged=changed,
 latestPilotResults=proof['improved'],nativeCampaignClearRatesValidated=False,
 next='Improve risk reassessment and re-engagement when safe routes are exhausted, plus consumable and power policy; broaden seeds and builds before god balance inference. God-specific wrath remains separate.')
# The previous active-save proof used the previous build, not this policy.
state.pop('activeSaveValidation',None)
for p in [OUT/'checkpoint.json',ROOT/'engine/campaign_status.json']:
 p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'development_exclusions.json').write_text(json.dumps(dict(
 smoke01='First equipment/retreat prototype: excessive retreat against weak groups and staircase loops. Completed raw traces retained; not final.',
 smoke02='Threshold and staircase correction smoke: 7 cases, before final invisible-occupant and distortion-unwield safety refinements. Not final.',
 baseline_control01='Pre-final-build reproduction: 3 exact controls, superseded by baseline-control04 on final build.',
 failedBuild='build01 missing item-status-flag include; repaired and compiled successfully.',
 all22_01='Prototype final panel stopped on native armour interruption prompt. Failed case and partial data retained; final runner answers only these prompts No through the native Lua hook.',
 natural_01='Completed before the armour-interruption hook; superseded on the final build.',
 baseline_control02='Exact baseline reproduction on the prior build; superseded on final build.',
 all22_02='Completed initial 81-case comparison in comparison.json and validation.json; danger cells were excluded as goals but could be traversed en route. Retained as initial comparison, not final policy.',
 finalPolicy='all22-03 + natural-03, 81 cases',finalControl='baseline-control04, 3 cases'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['START_HERE_CAMPAIGN.md','CONTINUE_HERE.md','START_HERE_COMPANY.md','engine/README.md']:
 p=ROOT/name;rel='../' if name.startswith('engine/') else ''
 r=proof['improved'];oc=r['outcomes'];b=proof['baseline']['outcomes']
 prefix=f'''# 최신 봇 보강 재검사 — dungeon-pilot02 / 2026-10-20

장비 교체·위험도 퇴각을 보강하고 같은 시드의81회 진행을 재검사했다. D:5 이상 도달은 이전 {b.get('target_reached',0)}회 → 수정 {oc.get('target_reached',0)}회, 사망 {oc.get('death',0)}회, 행동한도 {oc.get('action_limit',0)}회, 정체/경로 소진 {oc.get('policy_stalled',0)}회다. 별도 같은 빌드의 이전 봇 대조3회는 과거 결과와 정확히 일치했다. 구덩이로 D:5를 건너뛴 진행도 도달에 포함하며, 층 정리·전체 던전 클리어율·신 밸런스 확정 검사가 아니다.

[상세 결과]({rel}analysis/native/dungeon-pilot02/RESULTS_POLICY02_KO.md), [비교 감사]({rel}analysis/native/dungeon-pilot02/final-comparison.json)를 먼저 확인한다. 최신 소스는 `engine/campaign-crawl/crawl-ref/source`, 상태는 `engine/campaign_status.json`이다. 일반 플레이 실행은 `./scripts/start-campaign.ps1`이다. 아래는 보존된 이전 단계 이력이다.

---

'''
 p.write_text(prefix+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
(OUT/'running-status.json').write_text(json.dumps(dict(status='completed',checkpoint='checkpoint.json',comparison='final-comparison.json'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='saved',cases=84,sourceFiles=len(old['sourceSha256']),policyFiles=changed,results=proof['improved']),ensure_ascii=False))
