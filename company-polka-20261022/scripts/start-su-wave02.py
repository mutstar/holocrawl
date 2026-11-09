from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
b=r/'analysis/native/su-wave02/native/shots'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for scene,expected in [('dry',[1,1,1,1,1]),('wet',[1,3,3,3,3])]:
 trace=[read(b/f'wave-{scene}-cast{n}.png-front.json') for n in range(5)]
 assert [f['lanes'] for f in trace]==expected
 assert all(f['nativeTileSpan']==1 and f['direction']==0 for f in trace)
template=(r/'scripts/start-su-wave01.py').read_text(encoding='utf-8-sig')
replacements={
 'su-wave01':'su-wave02',
 'tier3-review01.html':'tier3-wave02.html',
 "['before','cast0','cast1','after']":"['before','cast0','cast1','cast2','cast3','cast4','after']",
 'duration=[1100,400,400,1500]':'duration=[1000,230,230,230,230,230,1400]',
 'frames[2].save':'frames[3].save',
 '실제 엔진 권능 실행 전 → 현재 시전 이펙트2프레임 → 피해·밀치기 결과입니다. 두 번째 장면의 물은 실제 일반 근접공격으로 생성했습니다. 이후 적을 비교 위치로 배치했습니다. 원형 물보라는 현재 시전 장식이며, 공격 범위를 나타내는 원이 아닙니다. 파도가 경로를 따라 이동하는 연속 애니메이션은 아직 없습니다.':'실제 엔진 캡처: 시전 전 → 한 칸씩 전진하는 파도5프레임 → 피해·밀치기 결과. 두 번째 장면의 두 칸 앞 물은 실제 일반 근접공격으로 생성했습니다. 첫 칸은 좁은 파도, 두 번째 물 칸부터 양옆으로 넓어져 총3칸 폭으로 전진합니다. 피해·밀치기 판정은 즉시 처리되며, 각 연출 프레임이 별도의 공격 턴은 아닙니다.',
 '원형 장식은 공격 범위 표시가 아닙니다.':'파도가 실제 공격 경로를 따라 전진하며, 물에서 폭1칸→3칸으로 확장됩니다.',
 '기존 시전 장식이며 경로 이동 애니메이션은 없음. 전투·아트 유지,검증 fixture 추가 실행본 갱신.':'한 칸씩 전진하는 생성 파도 도트로 교체. 물을 만나는2번째 칸부터 폭1→3칸 확장.8방향32px타일,표시/RNG검증 포함.전투 수치 유지,아트/렌더러/fixture 및실행본 갱신.',
 '현재 원형 물보라는':'현재 파도 이펙트는',
 'combatChanged=False,artChanged=False':'combatChanged=False,artChanged=True',
 '3성 파도 검토 /':'3성 전진 파도 초안 /',
}
for old,new in replacements.items():template=template.replace(old,new)
# Keep all modified renderer/atlas sources in the reviewable checkpoint patch.
template=template.replace("f='holo-campaign-test.cc';(b/'source.patch').write_text(''.join(difflib.unified_diff((b/'before'/f).read_text(encoding='utf-8-sig').splitlines(True),(r/'engine/campaign-crawl/crawl-ref/source'/f).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+f,tofile='after/'+f)),encoding='utf-8')", """patch=''
for old in (b/'before').iterdir():
 new=r/'engine/campaign-crawl/crawl-ref/source'/('rltiles/'+old.name if old.suffix=='.txt' else old.name)
 patch+=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+old.name,tofile='after/'+old.name))
(b/'source.patch').write_text(patch,encoding='utf-8')""")
exec(compile(template,str(Path(__file__)),'exec'))
# Existing links should also display the newest comparison.
base=r/'analysis/previews/su-review01'
(base/'tier3-review01.html').write_text((base/'tier3-wave02.html').read_text(encoding='utf-8'),encoding='utf-8')
