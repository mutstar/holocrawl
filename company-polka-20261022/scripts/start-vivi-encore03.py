from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/start-vivi-encore01.py').read_text(encoding='utf-8-sig')
for old,new in {
 'vivi-encore01':'vivi-encore03','tier3-encore01':'tier3-encore03',
 "'echo0','echo1','ended'":"'echo0','echo1','echo2','ended'",
 '분홍 겹친 잔상':'분홍·보라 펄 폭발','분홍 잔상':'분홍·보라 펄 폭발','분홍겹친잔상':'분홍보라펄폭발',
 '각 잔상은':'추가 타격 펄 폭발은','16×18→20×22':'16×16→24×24→22×22(잔광)','새초안20×22이내':'새초안24×24이내',
 'duration=[1100,650,650,180,180,230,450,1100]':'duration=[1100,650,650,180,180,90,170,200,1100]',
}.items():t=t.replace(old,new)
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01'
page=(base/'tier3-encore03.html').read_text(encoding='utf-8').replace('첫 주문 피해 뒤 추가 타격이 들어간다는 연출','몹 몸통에서 펑 터지는 펄 폭발. 분홍·보라 퍼프,흰빛·금빛 마름모 섬광,잔광으로 소멸. 검기·비행 궤적 없음')
page=page.replace('</html>','<p>디자인 참고: <a href="https://hololive.hololivepro.com/talents/kikirara-vivi/">홀로라이브 공식 비비 일러스트</a>의 분홍·보라 색감,마름모 반짝임과 화장품 금색 포인트.</p></html>')
for name in ['index.html','tier3-encore01.html','tier3-encore02.html','tier3-encore03.html']:(base/name).write_text(page,encoding='utf-8')
p=r/'analysis/native/vivi-encore03/checkpoint-manifest.json';d=json.loads(p.read_text(encoding='utf-8'));d['art']=json.loads((r/'assets/holocrawl/vivi-encore03/generation.json').read_text(encoding='utf-8'));p.write_text(json.dumps(d,indent=2),encoding='utf-8')
note='# 비비3성 공식 일러스트 기반 펄 폭발 / vivi-encore03 / 2026-10-29\n\n사용자 요청:공식일러나영상참조해조금더화려하게.공식전신일러의분홍/보라·마름모반짝임·화장품금색을참고.공식일러시각확인,영상재생확인주장없음.정지형펑폭발유지,퍼프에보라·흰금섬광추가,16→24→22픽셀잔광3프레임/32타일.새프레임testcapture연결,전투미적용·일반실행본su-five01유지.22신/복원검사통과. analysis/previews/vivi-review01/tier3-encore03.html 현재3성시각검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
