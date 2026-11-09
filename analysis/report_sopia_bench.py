"""Report the native Sopia ring/full ablation and fixed-kit references."""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('summary',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
data=json.loads(args.summary.read_text(encoding='utf-8'))
assert data['pairing_verified']
rows={(r['scenario'],r['god']):r for r in data['summary']}
names={'early_ogre':'초기 오우거1','early_three_orcs':'초기 오크3',
    'mid_ettin':'중기 에틴1','mid_three_warriors':'중기 오크전사3',
    'late_stone_giant':'후기 돌거인1','late_two_stone_giants':'후기 돌거인2',
    'late_three_ettins':'후기 에틴3','late_three_warriors':'후기 오크전사3'}
variants=('no_god','noel_v2','sopia_ring','sopia_full')
counts={r['trials'] for r in data['summary']}
assert len(counts)==1
lines=['# 소피아 실제 엔진 전투 시험','',
    f"DCSS 0.24.0 엔진에서 {data['trials']:,}회. 각 상황·변형당 {next(iter(counts)):,}개 시드.",
    '노엘과 동일한 Human Fighter 고정 장비·HP/MP·기술·시작 신앙, 인접 적 배치로 비교했다.',
    '고리만은 1성만 사용하는 대조군이다. 전체는 해금된 고리·중력장·빅뱅을 사용한다. 새로운 수치 조정은 하지 않았다.','',
    '| 전투 | 무신앙 | 현재 노엘 | 소피아 고리만 | 소피아 전체 |',
    '|---|---:|---:|---:|---:|']
for scenario,label in names.items():
    values=' | '.join(f"{rows[scenario,god]['win_rate']:.1%}" for god in variants)
    lines.append(f'| {label} | {values} |')
lines+=['','## 권능 실제 사용량','',
    '| 전투 | 평균 고리 적중 | 평균 압축 적중 | 평균 당김 성공 | 평균 기폭 | 평균 권능 피해 |',
    '|---|---:|---:|---:|---:|---:|']
for scenario,label in names.items():
    m=rows[scenario,'sopia_full']['mean_effects']
    lines.append(f"| {label} | {m['ring_hits']:.2f} | {m['field_hits']:.2f} | {m['pulls']:.3f} | {m['detonations']:.3f} | {m['damage']:.2f} |")
lines+=['','## 구현 및 자동 조작','',
    '- 고리는 시전 완료10 aut 뒤부터10 aut마다, 중력장은 완료20 aut 뒤부터20 aut마다 물리 피해를 주며 각각 원본 AC를 적용한다.',
    '- 중력장은 고정 위치·거리순 처리·확률 판정·적별20 aut 당김 제한을 사용한다. 점유·벽·함정·생존 불가 칸으로 당기지 않고, 정지/촉수 생물은 이동시키지 않는다. 이동 면역도 압축 피해는 받는다.',
    '- 빅뱅은 응축0에서 기폭할 수 없고20 aut마다 최대3까지 응축한다. 수동 기폭 후 생존 적을 합법 칸으로2칸 밀치고, 장이 끝난 뒤150 aut 제한을 적용한다.',
    '- 자동 조작은 고리를 켜고, 5성이 있으면 강화 장을 생성하며, 없으면 일반 장을 설치한다. 응축3 또는 만료까지20 aut 이하이고 응축1 이상이면 기폭한다. 이후 접근/근접을 반복한다.',
    '- 시험 정책은 장을 자기 칸에 설치한다. 소스는 사거리4의 다른 바닥 중심도 지원하지만 최적 위치 탐색은 하지 않는다.',
    '- 원본 엔진의 몬스터 행동 후 월드 후처리 단계에서 경과한 모든 논리 틱을 처리한다. 짧은 aut 구간·긴 경과시간의 여러 틱 수·만료 우선순위를 검증했다. 긴 행동 안의 각 중간 시각에 몬스터 위치를 재구성하는 연속시간 모형은 아니다.',
    '- 정지 적 압축 피해, 아군 제외, 점유/벽 당김 차단, 중심 적 피해, 응축·기폭·밀침·비용·재사용 제한을 실제 몬스터 fixture에서 검사한다.',
    '- 실제 신앙 환급·자연 감소·배교/징벌·가입 UI·저장 연동은 미구현이다. 전투 중 신앙은 고정 시작 예산에서 비용만 차감한다.','',
    '## 해석 범위','',
    '인접 근접 전투의 승률이며 실제 던전 클리어율이 아니다. 원거리/마법 빌드·시작 거리·장 위치 최적화·도주·소모품 판단을 포함하지 않는다.',
    '고리만보다 전체가 낮다면 시전 시간·MP/신앙·사용 정책까지 포함한 결과다. 고리/중력장/빅뱅 자체가 항상 약하거나 강하다고 단정하지 않는다.',
    '기본 전투 능력·저항·명중·몬스터 AI·회복은 원본 엔진을 사용한다. 추방은 별도 종료이며 승리나 HP사망으로 바꾸지 않는다.',
    '개별 승률 Wilson95% 구간, 같은 시드 짝 비교, 자원/남은 HP/시간과 권능 사용량은 summary.json에 있다.',
    '현재 구현은 노엘·소피아 전투 코어이며 다른20신은 아직 미구현이다. 신 전부의 밸런스 확정 결과로 해석하지 않는다.']
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(args.output)
