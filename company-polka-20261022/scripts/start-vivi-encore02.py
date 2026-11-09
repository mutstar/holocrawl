from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/start-vivi-encore01.py').read_text(encoding='utf-8-sig')
for old,new in {
 'vivi-encore01':'vivi-encore02','tier3-encore01':'tier3-encore02',
 '분홍 겹친 잔상':'분홍 팝 폭발','분홍 잔상':'분홍 팝 폭발','분홍겹친잔상':'분홍팝폭발',
 '각 잔상은':'추가 타격 폭발은','16×18→20×22':'14×14→22×22','새초안20×22이내':'새초안22×22이내',
 'duration=[1100,650,650,180,180,230,450,1100]':'duration=[1100,650,650,180,180,100,240,1100]',
}.items():t=t.replace(old,new)
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01'
page=(base/'tier3-encore02.html').read_text(encoding='utf-8').replace('첫 주문 피해 뒤 추가 타격이 들어간다는 연출','몹 몸통에서 짧게 팡 터지는 추가 타격. 검기·비행 궤적 없음')
for name in ['index.html','tier3-encore01.html','tier3-encore02.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/native/vivi-encore02/checkpoint-manifest.json';d=json.loads(p.read_text(encoding='utf-8'));d['art']=json.loads((r/'assets/holocrawl/vivi-encore02/generation.json').read_text(encoding='utf-8'));p.write_text(json.dumps(d,indent=2),encoding='utf-8')
note='# 비비3성 앙코르 몸통 팝 폭발 수정 / vivi-encore02 / 2026-10-29\n\n사용자 피드백:검기처럼 날아가는 느낌 대신 몹에펑터지는표시.분홍초승달/베기형상을작은분홍팝폭발로교체.같은몹중앙에14×14→22×22/32타일,짧은100+240ms표시.립스틱예약표시유지.피해/전투코드미구현상태유지,단계별실제SDL초안만.22신/복원검사통과.현재3성시각검토중. analysis/previews/vivi-review01/tier3-encore02.html\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
