from pathlib import Path
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/start-vivi-attention01.py').read_text(encoding='utf-8-sig').replace('vivi-attention01','vivi-attention02').replace('tier1-attention01','tier1-attention02')
t=t.replace('이번 작업은 생성 보석 도트와 테스트 전용 시각 분기만 추가했습니다.','기존 메이크업 장식은 초안에서 숨기고 새 보석만 표시합니다. 이번 작업은 생성 보석 도트와 테스트 전용 시각 분기만 추가했습니다.')
# The design was already recorded in revision01; do not duplicate that section.
t=t.replace("p=r/'BALANCE_WORKPLAN.md';p.write_text(","p=r/'analysis/native/vivi-attention02/design-record.txt';p.write_text(")
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01'
(base/'tier1-attention01.html').write_text((base/'tier1-attention02.html').read_text(encoding='utf-8'),encoding='utf-8')
