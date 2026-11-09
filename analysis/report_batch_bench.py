"""Audit and report complete native all-god cohorts, preserving build boundaries."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev

p = argparse.ArgumentParser()
p.add_argument('output', type=Path)
p.add_argument('inputs', type=Path, nargs=3)
args = p.parse_args()
names = dict(zip(
    ['suisei','miko','aki','fubuki','ayame','choco','korone','okayu','pekora','noel_v2','watame',
     'towa','lamy','polka','koyori','lui','raden','hajime','su','vivi','sopia_full','mela'],
    ['스이세이','미코','아키','후부키','아야메','초코','코로네','오카유','페코라','노엘','와타메',
     '토와','라미','폴카','코요리','루이','라덴','하지메','스우','비비','소피아','메라']))
build_names = {'melee':'근접','ranged':'원거리','magic':'주문'}
reports = {}
source = None
for path in args.inputs:
    manifest = json.loads(path.with_suffix('.manifest.json').read_text(encoding='utf-8-sig'))
    assert hashlib.sha256(path.with_suffix('.engine.patch').read_bytes()).hexdigest().upper()==manifest['sourcePatchSha256']
    assert hashlib.sha256(path.with_suffix('.design.md').read_bytes()).hexdigest().upper()==manifest['designSha256']
    build = manifest['build']
    assert build in build_names and build not in reports, 'Duplicate/unknown build'
    invariant = tuple(manifest[k] for k in ['engineCommit','buildBinarySha256','sourcePatchSha256','designSha256'])
    if source is None:
        source = invariant
    assert invariant == source, 'Different source, binary, or design between cohorts'
    variants, scenarios = manifest['variants'], manifest['scenarios']
    assert set(variants) == {'no_god',*names} and len(variants)==23 and len(scenarios)==8
    n, start = manifest['trialsPerCase'], manifest['seedStart']
    seen = set()
    outcome = defaultdict(Counter)
    cases = defaultdict(Counter)
    clusters = defaultdict(Counter)
    effects = defaultdict(Counter)
    wins_hp = defaultdict(list)
    duration = Counter()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for line in stream:
            digest.update(line)
            row = json.loads(line)
            god, scenario, seed = row['god'], row['scenario'], row['seed']
            key = scenario, seed, god
            assert key not in seen and god in variants and scenario in scenarios and start<=seed<start+n
            assert row['build']==build and row['outcome'] in ('win','loss','timeout','banished')
            assert row['outcome']!='loss' or row['hp']<=0, 'Synthetic death record'
            assert row['outcome']!='win' or row['hp']>0, 'Victory without a living player'
            assert row['mp']>=0 and row['piety']>=0
            assert all(v>=0 for v in row['effects'].values())
            if god in ('no_god','noel_v2'):
                assert not any(row['effects'].values()), 'Custom effects leaked into controls'
            seen.add(key)
            outcome[god][row['outcome']]+=1
            cases[scenario,god][row['outcome']]+=1
            clusters[seed][god]+=row['outcome']=='win'
            effects[god].update(row['effects'])
            duration[god]+=row['aut']
            if row['outcome']=='win':
                wins_hp[god].append(row['hp']/row['max_hp'])
    assert len(seen)==len(variants)*len(scenarios)*n, 'Missing or duplicate native encounters'
    cohort = {}
    for god in variants:
        differences = [(clusters[seed][god]-clusters[seed]['no_god'])/len(scenarios) for seed in range(start,start+n)]
        delta = mean(differences)*100
        margin = 1.95996398454*stdev(differences)/math.sqrt(n)*100 if n>1 else 0
        cohort[god] = dict(outcome[god], encounters=n*len(scenarios), win_rate=outcome[god]['win']/(n*len(scenarios)),
            difference_pp=delta, difference_cluster95_pp=[delta-margin,delta+margin],
            mean_winning_hp_fraction=mean(wins_hp[god]) if wins_hp[god] else None,
            mean_aut=duration[god]/(n*len(scenarios)),effects_mean={k:v/(n*len(scenarios)) for k,v in effects[god].items()})
    reports[build] = dict(input=path.name,sha256=digest.hexdigest().upper(),encounters=len(seen),
        trials_per_case=n,seed_start=start,gods=cohort,
        cases={scenario:{god:dict(cases[scenario,god],win_rate=cases[scenario,god]['win']/n) for god in variants} for scenario in scenarios})

assert set(reports)==set(build_names)
args.output.mkdir(parents=True,exist_ok=True)
payload=dict(engine='DCSS 0.24.0',upstream_commit=source[0],build_sha256=source[1],source_patch_sha256=source[2],
    design_sha256=source[3],encounters=sum(b['encounters'] for b in reports.values()),builds=reports)
(args.output/'all-gods-summary.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 22신 실제 엔진 일괄 전투 — 1차 비교','',
    f"DCSS 0.24.0에서 최종 집계에 **{payload['encounters']:,}회**의 고정 조우를 사용했다. 신22명과 무신앙을 근접·원거리·주문 빌드별로 비교했다.",
    '각 수치는8개 고정 상황의 승률 평균이며 괄호는 같은 빌드 무신앙 대비 승률 차이(%p)다. 처치·회복·명중·AC·방패·몬스터 행동·주문 실패는 실제 엔진을 사용했다.','',
    '| 신 | 근접 | 원거리 | 주문 |','|---|---:|---:|---:|']
def cell(build,god):
    r=reports[build]['gods'][god]
    return f"{r['win_rate']*100:.2f}% ({r['difference_pp']:+.2f})"
lines.append('| 무신앙 | '+' | '.join(f"{reports[b]['gods']['no_god']['win_rate']*100:.2f}%" for b in build_names)+' |')
for god,label in names.items():
    lines.append('| '+label+' | '+' | '.join(cell(b,god) for b in build_names)+' |')
lines+=['','## 해석 범위','',
    '- 근접은 기존 노엘·소피아 검증과 같은 인접 배치다. 원거리·주문은6칸 거리에서 시작하므로 빌드 사이 비교는 각자의 무신앙 기준 차이로 읽는다.',
    '- 각 상황은 빈 준비 상태에서 시작한다. 폴카 박수0·코요리 시약0·오카유 만복30, 사전 설치·사전 버프가 없다. 전투 사이에 저장하는 자원과 사전 준비의 가치는 이번 집계에 포함되지 않는다.',
    '- 동일 시드와 동일 장비를 사용하고 각 신의 정해진 자동 행동 순서로 싸운다. 정책의 자원 사용·설치 위치·재사용 선택도 승률에 반영되므로 이 수치만으로 신의 최적 운용 성능을 확정하지 않는다.',
    '- 근접은 검/갑옷/방패, 원거리는 활/화살80개/가죽 갑옷, 주문은 로브/단검/화염 주문을 사용한다. 주문은 실제 cast_a_spell 경로로 비용·실패·오발·허기를 처리한다. MP 부족 시 하위 주문 또는 일반 공격으로 전환한다.',
    '- 신앙 자연 수급·선물·징벌·층 진행·일반 숭배 UI·저장 통합은 이번 전투 코어 범위 밖이다. 전투 중 신앙과 MP 비용 및 자연 회복은 적용한다.',
    '- 시간 효과는 원작 몬스터 단계가 끝난 위치로 미도래 주기를 모두 처리한다. 긴 행동 사이의 중간 위치와 동시 공격을 별도로 복원하지 않는 제한이 있다.',
    '- 동료는 실제 원작 몬스터 객체에 수치·비행·행동 지연·피해 처리를 붙였다. 아키 식물은 실제 투사체를 발사하고 루이 까마귀는 자기 이동 에너지와 일반 근접 공격을 사용한다.',
    '- effects의 batch_damage 등은 모듈이 직접 집계하는 추가 효과 값이다. 일반 무기 공격·추가 일반 공격·동료 평타 전체 피해의 합계가 아니다.','',
    '## 실행 상태','',
    '| 빌드 | 전투 | 사망 | 추방 | 시간초과 |','|---|---:|---:|---:|---:|']
for build,label in build_names.items():
    r=reports[build]
    lines.append(f"| {label} | {r['encounters']:,} | {sum(g.get('loss',0) for g in r['gods'].values()):,} | {sum(g.get('banished',0) for g in r['gods'].values()):,} | {sum(g.get('timeout',0) for g in r['gods'].values()):,} |")
lines+=['','추방과 시간초과는 별도 결과로 보존했다. 승리는 모든 적과 보류 피해·매료·예약 공격의 종료까지 확인한 뒤 기록한다.','',
    '승률 차이의95% 구간은 같은 시드의8개 상황을 한 묶음으로 취급해 계산했다. 상황별 수치·효과 집계·해시와 구간은 `all-gods-summary.json`에 보존했다.','']
(args.output/'RESULTS_ALL_GODS.md').write_text('\n'.join(lines),encoding='utf-8')
print(f"Audited {payload['encounters']:,} native encounters across all three builds; report and JSON saved.")
