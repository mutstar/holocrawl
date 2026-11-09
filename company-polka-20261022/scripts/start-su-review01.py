from pathlib import Path
import json,re,shutil
r=Path(__file__).resolve().parents[1];review='analysis/previews/su-review01/tier1.html';o=r/Path(review).parent;o.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
shutil.copy2(r/'analysis/previews/all-gods-vfx-draft04/clips/su-passive-0.png',o/'passive.png')
css=re.search(r'<style>(.*?)</style>',(r/'analysis/previews/hajime-review01/index.html').read_text(encoding='utf-8'),re.S).group(1)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>스우 · 1성 물결의 흔적</title><style>'''+css+'''</style><h1>스우 · 1성 물결의 흔적</h1><p class="info"><b>직접 공격으로 피해를 주면 대상 위치에 웅덩이를 남겨 적의 이동을 방해합니다.</b><br>해금: 신앙★30 · 최소 기도술 제한 없음<br>자동 패시브 · MP/신앙 소모 없음 · 별도 시전 버튼 없음</p><div class="cards"><article><h2>현재 실제 게임 초안</h2><img src="passive.png" alt="스우1성 웅덩이가 생성된 기존 실제 게임 캡처"><p>머리 옆 작은 물결 표식은1성 가호 준비 표시이고, 실제 이동 방해는 대상 위치의 웅덩이에서 적용됩니다. 이 이미지는 기존 실제 엔진 캡처이며, 공격 전후·물에서 벗어나는 연속 재생은 아직 아닙니다.</p></article><article><h2>효과와 기도술 수치</h2><table><tr><th>항목</th><th>현재 적용</th></tr><tr><td>발생 조건</td><td>직접 공격이 실제 피해를 주고 대상 위치가 일반 바닥이면 생성. 피해0이면 생성하지 않음</td></tr><tr><td>지속</td><td>생성 시점부터5+0.1I턴<br>I12에서6.2턴. 공격 행동 처리 시간도 이 타이머에 포함</td></tr><tr><td>이동 방해</td><td>적의 이동·수영 행동 비용 ×1.25, 정수 올림<br>기본10이면13으로 증가</td></tr><tr><td>공격 속도</td><td>변화 없음. 적이 제자리에서 공격할 때는 느려지지 않음</td></tr><tr><td>추가 피해</td><td>1성 웅덩이 자체 피해 없음</td></tr><tr><td>본인 이동</td><td>플레이어에게 같은 이동 페널티를 주지 않음</td></tr><tr><td>웅덩이 수</td><td>최대12개. 같은 위치를 다시 적중하면 지속 갱신, 초과 시 오래된 웅덩이부터 제거</td></tr></table><p>I는 기도술입니다. 기도술은1성 웅덩이 지속시간을 늘리고, 이동 방해 비율은 바꾸지 않습니다. 신앙 수치에 따른 추가 배율은 없습니다.</p><p>비행·수생·양서류 및 일부 이동 방해 면역 적은 적용 제외. 이미 감속 상태인 적에게 웅덩이 이동 비용을 추가로 중첩하지 않습니다.</p></article></div><p>이후3성 파도는 웅덩이를 지나면 폭이 넓어지는 연계가 있습니다. 지금은1성 표식·웅덩이 가시성을 먼저 검토합니다.</p><p>하지메1·3·5성 확정 유지. 현재 스우1성 검토 중, 기존 도트·전투·실행본 변경 없음.</p></html>'''
for name in ['tier1.html','index.html']:(o/name).write_text(page,encoding='utf-8')
p=r/'analysis/previews/all-gods-vfx-draft04/index.html';t=p.read_text(encoding='utf-8');m=re.search(r'const data=(.*?);function choose',t);d=json.loads(m[1]);d['su']=[dict(tier=1,option=0,title='물결의 흔적',image='../su-review01/passive.png',kind='기존 실제1성 웅덩이 캡처')];t=t[:m.start(1)]+json.dumps(d,ensure_ascii=False)+t[m.end(1):]
article='<article id="su" data-god="su"><h2>스우 <small>1성 · 검토 중</small></h2><select onchange="choose(this)"><option value="0">1성 · 물결의 흔적</option></select><p class="scene-note">기존 실제1성 웅덩이 캡처</p><img class="scene" src="../su-review01/passive.png"><p>피해를 준 대상 위치에 웅덩이. 적 이동 비용25% 증가, 공격 속도 변화 없음. 신앙30 해금, 최소 기도술 없음. MP·신앙 소모 없음.</p><p><a href="../su-review01/tier1.html">효과·조건·상세 수치</a></p><label>피드백<textarea data-feedback="su"></textarea></label></article>'
t=re.sub(r'<article id="su".*?</article>',lambda _:article,t,count=1,flags=re.S);t=t.replace("location.hash.slice(1)||'hajime'","location.hash.slice(1)||'su'");p.write_text(t,encoding='utf-8')
def update(d):
 d.update(currentGod='su',currentVisualReviewGod='su',currentVisualReviewTier=1,currentVisualReview=review,next='Review Su tier1. Remaining Su, Vivi, Sopia, Mela; Hajime fully approved.')
 if 'review' in d:d['review']=review
 if 'tierApprovals' in d:d['tierApprovals'].setdefault('su',{}).update(approved=[],pending=[1,3,5],pendingRevision='su-review01')
 if isinstance(d.get('vfxDraftHandoff'),dict):update(d['vfxDraftHandoff'])
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/name;d=read(p);update(d);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 스우1성 검토 시작 / 2026-10-29\n\n사용자 진행(rrrrrr)으로 스우1성 물결의 흔적 검토 시작. 기존 실제 캡처와 현재 소스 수치를 analysis/previews/su-review01/tier1.html 에 정리. 피해가 있는 직접 공격 위치에 웅덩이,5+0.1I턴, 적 이동비용125% 올림(10→13), 공격속도/추가피해 변화 없음. 도트/전투/실행본 변경 없음. 완료18신, 스우→비비→소피아→메라 남음.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Su tier1 ready:',review)
