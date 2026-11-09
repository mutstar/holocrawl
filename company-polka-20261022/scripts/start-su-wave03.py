from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/start-su-wave02.py').read_text(encoding='utf-8-sig').replace('su-wave02','su-wave03').replace('tier3-wave02','tier3-wave03')
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/su-review01'
for name in ['index.html','tier3-review01.html','tier3-wave02.html','tier3-wave03.html']:
 p=base/name
 if name=='tier3-wave02.html':p.write_text((base/'tier3-wave03.html').read_text(encoding='utf-8'),encoding='utf-8')
 text=p.read_text(encoding='utf-8').replace('<h2>현재 수치</h2>','<p>파도 도트를20×24에서24×28픽셀로 조금 확대했습니다. 공격 범위와 피해는 동일합니다.</p><h2>현재 수치</h2>')
 p.write_text(text,encoding='utf-8')
note='# 스우3성 파도 소폭 확대 / su-wave03 / 2026-10-29\n\n사용자 요청으로 기존 생성 도트를20×24→24×28로 확대(가로20%,세로약17%).8방향32×32타일 유지,대각선은30×30안에맞춰잘림방지. 피해/범위/비용 변경 없음:2d(7+floor(I/3)),I12=2d11평균12(AC전),1칸밀치기;물에서폭1→3칸.실제SDL GIF 및22신·복원검사통과.현재스우3성검토중.페이지 analysis/previews/su-review01/tier3-wave03.html\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=r/'analysis/native/su-wave03/checkpoint-manifest.json';d=json.loads(p.read_text(encoding='utf-8'));d['artResize']=json.loads((r/'assets/holocrawl/su-wave03/generation.json').read_text(encoding='utf-8'));p.write_text(json.dumps(d,indent=2),encoding='utf-8')
