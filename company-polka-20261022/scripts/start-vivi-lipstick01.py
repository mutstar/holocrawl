from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];record=r/'analysis/native/vivi-lipstick01/design-record.txt';record.write_text('',encoding='utf-8')
t=(r/'scripts/start-vivi-attention01.py').read_text(encoding='utf-8-sig').replace('vivi-attention01','vivi-lipstick01').replace('tier1-attention01','tier1-lipstick01').replace('보석','립스틱').replace('8×10','7×12').replace('gem visuals','lipstick visuals')
t=t.replace('립스틱의 흰 반짝임으로 어두운 바닥과 구분합니다.','분홍 끝·금색 통·검은 밑부분으로 립스틱 모양을 구분합니다.').replace('이번 작업은 생성 립스틱 도트와 테스트 전용 시각 분기만 추가했습니다.','기존 메이크업 장식은 숨기고 새 립스틱만 표시합니다. 이번 변경은 주목 보석을 립스틱 도트로 교체한 시각 초안입니다.')
t=t.replace("p=r/'BALANCE_WORKPLAN.md';p.write_text(","p=r/'analysis/native/vivi-lipstick01/design-record.txt';p.write_text(")
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01';page=(base/'tier1-lipstick01.html').read_text(encoding='utf-8')
page=page.replace('</body>','')
page=page.replace('</html>','<p>디자인 참고: <a href="https://hololive.hololivepro.com/talents/kikirara-vivi/">홀로라이브 공식 비비 전신 일러스트</a></p></html>')
for name in ['index.html','tier1.html','tier1-attention01.html','tier1-attention02.html','tier1-lipstick01.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/native/vivi-lipstick01/checkpoint-manifest.json';d=json.loads(p.read_text(encoding='utf-8'));d['art']=json.loads((r/'assets/holocrawl/vivi-lipstick01/generation.json').read_text(encoding='utf-8'));p.write_text(json.dumps(d,indent=2),encoding='utf-8')
