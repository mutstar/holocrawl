from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
note = '''# 현재 검토: A·B·C 구조 비교07 / 2026-11-04

사용자: 비교 구조의 차이가 적다고 피드백. B를 A의 확장형 대신 별도 생성기로 교체. 큰 구역3~4개 + 주변 작은 공간9~14개 + 짧은 골목. A/C와 이전06 보존. 새 B는 아직 승인 전.

http://127.0.0.1:8797/city-layout07/layouts.html
B 거리: http://127.0.0.1:8797/city-layout07/index.html?layout=balanced&seed=LAYOUT-001&view=focus

상세 design/CITY_MIXED_REVIEW07.md. 각60개 총180지도 연결성·결정성·B 주요 계단 길3칸 보호·A/C 동일성·브라우저49칸 이동·모바일 검사 통과. 소품20종·84명 진열 유지. 회사에서는 브라우저 도트·구조·배치만 진행. 실제 게임 실행·적용은 미룸. 다음은 B의 공간 크기·골목 비중 검토.

---

'''
for target in [root/'README.md', root/'CONTINUE_HERE.md', root.parent/'CONTINUE_HERE.md']:
    content = target.read_text(encoding='utf-8')
    if not content.startswith('# 현재 검토: A·B·C 구조 비교07'):
        target.write_text(note + content, encoding='utf-8')

status_path = root/'migration-status.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status.update({
    'activeWork': 'browser-independent-mixed-layout-review07',
    'currentVisualReview': 'preview/city-layout07/layouts.html',
    'cityLayoutPreview': 'preview/city-layout07/index.html',
    'balancedLayoutReview': 'Independent B generator added after insufficient visual difference feedback; awaiting user review.',
    'balancedLayoutMapCases': 60,
    'layoutReviewMapCases': 180,
    'actualGameApplicationDeferred': True,
    'next': 'Review independent B quarters and side alleys in A/B/C layout07. Browser-only art/layout work; native game remains deferred.'
})
status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json', 'VFX_DRAFT_STATUS.json']:
    target = root.parent/'company-polka-20261022'/name
    data = json.loads(target.read_text(encoding='utf-8'))
    data.update({
        'activeWork': status['activeWork'],
        'currentVisualReview': str(root/'preview/city-layout07/layouts.html'),
        'next': status['next'],
        'lastArchiveIncludesLatest': False,
        'actualGameApplicationDeferred': True
    })
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

target = root/'preview/city-layout07/index.html'
html = target.read_text(encoding='utf-8').replace('같은 도트로 큰 공간·방 연결·골목망을 다르게 생성합니다. 공간을 겹쳐 이어 만들고, 벽 덩어리 사이에 넓은 순환 길을 남깁니다.', 'B는 큰 구역3~4개를 넓은 길로 잇고, 가장자리에 작은 공간과 짧은 골목을 붙입니다. A·B·C 구조를 바꿔 비교할 수 있습니다.')
target.write_text(html, encoding='utf-8')
print('Saved layout07 review and continuation pointers.')
