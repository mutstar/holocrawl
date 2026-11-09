from pathlib import Path
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/start-vivi-encore03.py').read_text(encoding='utf-8-sig').replace('vivi-encore03','vivi-encore04').replace('tier3-encore03','tier3-encore04').replace('16×16→24×24→22×22','18×18→28×28→26×26').replace('새초안24×24이내','새초안28×28이내').replace('16→24→22픽셀','18→28→26픽셀')
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01'
page=(base/'tier3-encore04.html').read_text(encoding='utf-8').replace('</html>','<p>크기 조정: 최대24→28픽셀(약17% 확대). 색감·반짝임·위치·연출 시간은 유지했습니다.</p></html>')
for name in ['index.html','tier3-encore01.html','tier3-encore02.html','tier3-encore03.html','tier3-encore04.html']:(base/name).write_text(page,encoding='utf-8')
note='# 비비3성 펄 폭발 소폭 확대 / vivi-encore04 / 2026-10-29\n\n사용자「크기좀만더키워줄래」.최대24→28픽셀(가로/세로약17%)확대.시작18·최대28·잔광26/32타일,기존분홍보라·금빛마름모·몸통위치·표시시간유지.전투미구현/일반실행본su-five01유지.실제SDL시각확인 및기존22신/복원검사통과. analysis/previews/vivi-review01/tier3-encore04.html 현재3성시각검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
