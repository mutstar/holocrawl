from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];p=root/'preview/native-water01'
html=(p/'index.html').read_text(encoding='utf-8').replace('HOLOCRAWL / 철제 문 도트 검토','HOLOCRAWL / 물 도트 검토').replace('브라우저 도트 검토용 · 문 상태는 모양 확인용입니다.','브라우저 도트·물가 경계 검토용입니다.').replace('새로 그린 좁은 철제 문을 실제 지도에 배치한 모습','얕은 물과 깊은 물을 원본 지도에 표시한 모습')
(p/'index.html').write_text(html,encoding='utf-8')
note='''# 현재 검토: 도시의 얕은 물·깊은 물01 / 2026-11-04

사용자가 돌죽과 비슷하되 다르게 물 도트/경계 제작을 요청. 콘크리트 바닥이 비치는 얕은 고인 물, 어두운 청록색 깊은 수로 표면을 생성하여 원본 지형에 표시. 땅 경계·오목 모서리·깊이 전환 포함. 물 도트 승인 전.

http://127.0.0.1:8797/native-water01/
상세 design/CITY_WATER01.md. 위 웅덩이2개는 인공 경계 예시, 아래는0.34.1 원본6지도 그대로. 지도2/6에서 물 확인. 확정 네모 문12 유지(아치13 미적용). 원본 데이터/문 PNG 동일·6지도/모바일/오류 검사 통과. 실제 게임은 미적용. 다음은 물 재질·명도·경계 피드백.

---

'''
for f in [root/'README.md',root/'CONTINUE_HERE.md',root.parent/'CONTINUE_HERE.md']:
    t=f.read_text(encoding='utf-8')
    if not t.startswith('# 현재 검토: 도시의 얕은 물·깊은 물01'):
        f.write_text(note+t,encoding='utf-8')
f=root/'migration-status.json';s=json.loads(f.read_text(encoding='utf-8'));s.update({'activeWork':'browser-water-art-review01','currentVisualReview':'preview/native-water01/index.html','waterArtReview':'preview/native-water01/index.html','waterArtApproved':False,'doorArtApproved':True,'doorArtSelectedRevision':'native-door12','actualGameApplicationDeferred':True,'next':'Review shallow/deep water surfaces and banks in native-water01. Demo ponds labelled synthetic; native maps unchanged. Approved rectangular door12 preserved.'});f.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
    f=root.parent/'company-polka-20261022'/name;d=json.loads(f.read_text(encoding='utf-8'));d.update({'activeWork':s['activeWork'],'currentVisualReview':str(p/'index.html'),'next':s['next'],'lastArchiveIncludesLatest':False,'actualGameApplicationDeferred':True});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved water01 preview and progress.')
