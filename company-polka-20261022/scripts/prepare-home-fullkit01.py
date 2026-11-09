from pathlib import Path
import json

r = Path(__file__).resolve().parents[1]
name = 'HOLOCRAWL_HOME_2026-10-30_FULLKIT01'
note = '''# 집에서 이어가기 — 2026-10-30 FULLKIT01

## 이번에 확정한 진행 기준

- 기존 22신의 1·3·5성 구성을 유지하고, 전체 성능을 먼저 비교한다.
- 이미 강한 구성에는 추가 패시브 1개, 애매하거나 부족한 구성에는 2개를 추가한다.
- 모든 신의 2·4성을 의무적으로 채우거나, 모든 신에게 같은 수의 권능을 주지 않는다.
- 여기서 1·3·5성은 핵심 해금 단계다. 기존에 자동 효과·선물인 권능을 액티브로 바꾸라는 뜻은 아니다.
- 기존 복합 효과, 비용, 재사용, 조건, 방어·회복·군중제어·소환까지 포함해 판단한다. 이미 강한 신의 추가 패시브는 화력 증가보다 편의·조건부 보조를 우선한다.
- 신별 1개/2개 배정과 구체 패시브는 아직 확정하지 않았다. 집에서 이어서 판단한다. 실제 승률로 검증된 강약 판정도 아니다.
- 스이세이의 기존 2개 후보는 미승인 참고안이다. 2개 모두 추가하기로 확정된 것이 아니다.

## 다음 세션 시작 순서

1. `FULLKIT_CORE_INVENTORY.md`에서 22신의 최신 핵심 구성을 읽는다.
2. 기존 순서대로 스이세이부터 전체 수치·비용·조건을 확인하고 패시브 추가 개수 1개/2개를 제안한다.
3. 사용자와 추가 효과·해금 신앙도·수치를 확정한 뒤 해당 신의 실제 전투, 이펙트 콜백, 저장 복원을 연결한다.
4. 피해·자원·행동 시간·중첩·면역·저장/재실행을 확인한 후 다음 신으로 넘어간다.
5. 기존 승인 도트는 활용한다. 새 패시브에 시각 표시가 필요할 때만 추가한다.

## 현재 완료와 남은 구현

- 22신의 1·3·5성 외형 검토 완료. 제단·소환수·효과 원화, GIF와 HTML, 최신 소스 및 검증 기록을 보존했다.
- 일반 실행본은 `runtime/tiles01/HoloCrawl.exe`의 **su-five01**이다. 새 패시브는 아직 구현하지 않았다.
- **비비:** 스포트라이트 / 앙코르 / 그랜드 피날레 마법 개편은 승인 설계·외형 단계. 일반 실행본은 기존 구성이다.
- **소피아:** MP 회복·주문 선물 / 기도술에 따른 3×3~7×7 중력장 / 주문 충전 빅뱅은 승인 설계·외형 단계. 새 전투 연결이 남았다.
- **메라:** 불씨 최대 3개 환산, 3성 폭 1·길이 5 직선, 5성 강화 길이 6 및 새 외형은 승인되었으나 실제 전투는 기존 불씨 6개·부채꼴이다.
- 위 새 GIF는 실제 SDL 엔진에서 준비한 시각 시퀀스다. 그것만으로 실제 피해·MP·신앙·충전·보호 효과가 구현됐다고 판단하지 않는다.
- 메라 직선 외형은 오른쪽 방향으로 검토했다. 실제 연결 시 나머지 방향의 회전·사선·벽 처리를 추가 확인한다.
- 스우의 실제 얕은 물·신도 물 페널티 면제·만조 구현은 보존한다.

## 열어볼 파일

- 전체 핵심 목록: `FULLKIT_CORE_INVENTORY.md`
- 최신 상태: `VFX_DRAFT_STATUS.json`, `HOME_HANDOFF_STATE.json`
- 세부 설계: `analysis/design/`와 각 신의 미리보기 설명. 비비 수치는 `VFX_DRAFT_STATUS.json`의 `viviCasterDraft`.
- 최신 메라 5성: `analysis/previews/mela-review01/tier5-dispatch01.html`
- 소피아: `analysis/previews/sopia-review01/tier1-teacher02.html`, `tier3-gravity04.html`, `tier5-bigbang02.html`
- 비비: `analysis/previews/vivi-review01/tier5-curtain02.html`
- 기존 상세 기획: `HOLOCRAWL_DESIGN.md` (변경 이력 포함. 구형 비비·소피아·메라 설명보다 위 최신 설계를 우선한다.)

## 새 PC에서 사용

ZIP을 새 폴더에 풀고 이 문서부터 코덱스에 읽힌다. `VERIFY_HOME.cmd`로 전송 무결성 확인, `PLAY_HOLOCRAWL.cmd`로 현재 일반 실행본을 실행한다. `OPEN_VFX_REVIEW.cmd`는 마지막 메라 5성 HTML을 연다.
컴파일러 전체와 빌드 중간 산출물·대용량 원시 로그·테스트 저장은 제외한다. 소스, 프로젝트 스크립트, 실행에 필요한 DLL, 원화·프롬프트·미리보기·설계·선별 검증 기록은 포함한다. 집의 MSYS2/MINGW64 경로는 재빌드 전에 확인한다.
예전 회사 PC의 절대 경로가 과거 기록에 남아 있을 수 있다. 새로 푼 폴더를 루트로 사용한다.
'''

rows = [
('스이세이','별자리 표식: 단일 표적 별 축적·처치 보상 [지정/자동]','궤도 절단: 별 소모 직선 관통','혜성 낙하: 지연 3×3 낙하'),
('미코','벚꽃 신사: 고정 성역·회복','액막이 불꽃 + 벚꽃 결계: 테두리 공격·원거리 완화','신역 전개: 성역 확대·감소·정화'),
('아키','장미의 씨앗: 정원·가시 축적','가시 장미: 정원 안 공격 장미','붉은 정원의 만개: 정원·장미 강화 및 가시 폭발'),
('후부키','흰 여우의 분신: 기만·협공','여우 바꿔치기: 교환 이동·여우불','백여우 행렬: 분신 수·기만·협공 강화'),
('아야메','귀인의 간격: 같은 적과 근접전 강화 [자동]','쌍섬: 한 번 공격 시간으로 2회 공격','백귀의 결투장: 결투 강화·처치 보상'),
('초코','달콤한 시선: 유혹 표식·직접 공격 중첩','위험한 입맞춤: 유혹 소모 피해·흡혈','서큐버스의 밤: 확률적 임시 아군화'),
('코로네','꺾이지 않는 근성: 근접·피격 중첩, 명중·살육 [자동]','놓치지 않아: 근성 소모 강타·추격','끝나지 않는 내구전: 추가 공격·근성 유지·피해 지연'),
('오카유','모구모구: 식사·처치 만복 및 보호막 [자동]','같이 낮잠 잘래: 졸음·감속·수면','꿈까지 먹어줄게: 만복·졸음 소모, 수면 대상 강화'),
('페코라','수상한 당근: 설치 폭탄·연쇄 폭발','도화선 조작: 즉시/예약 기폭','페코랜드 개장: 지정 지점 순차 폭격'),
('노엘','기사의 기량: 비마법 전투 스킬 강화','기사단의 보급: 처치 진척에 따른 장비 선물 [자동]','백은의 기사단장: 근접 피해·AC·SH 강화'),
('와타메','포근한 양털: 추가 재생 [자동]','양털 방벽 + 반격 박치기: 피해 완화·반격','끝나지 않은 노래: 재생 강화·치명상 버티기'),
('토와','악마의 조준: 원거리 명중·피해 [자동]','엄호사격: 구역 내 적 이동·공격에 반응 사격','악마의 교차포화: 엄호 구역 강화·별도 교차 사격'),
('라미','설국의 잔: 취기·공격 주문 위력, 과음 EV 페널티','취설의 마법: 직접 주문 냉각 축적·냉기 피해·이동 방해','눈의 연회: 취기 소모·직접 주문 적중 눈꽃 폭발'),
('폴카','오늘의 공연: 과제 완수·박수','공중곡예: 적 넘어 도약·다음 공격 강화','대단원: 불꽃 피날레/커튼콜/대혼란 선택'),
('코요리','실험 준비: 마법 실험 자원·시약','촉매 투입: 시약별 반응, 주변 3×3 효과·주문 사거리 +1','임계 실험: 강화 주문 4회·시약별 강화 반응'),
('루이','매 소환: 승인 B형 망토 도트·두 발 공격','사냥 지휘: 매의 집중 공격','매의 군세: 소환 수 증가·군세 강화, 등 뒤 날개'),
('라덴','이동 박물관: 회화/조각/공예 전환','소장품 발동: 채색 폭발/조각/공예, 상향 수치','특별전 개막: 세 분야 결합 강화'),
('하지메','반쵸의 스텝: 박자 축적','파고들기: 박자 활용 공격·이동','반쵸 타임: 이동 시 주변 1칸 공격 포함'),
('스우','물결의 흔적: 실제 얕은 물·신도 물 페널티 면제','밀려오는 파도: 물 경유 시 폭 확장·밀침','만조: 이동 물장판·지속 피해·파도 강화'),
('비비','스포트라이트: 직접 주문으로 주목 축적·주문 피해 강화','앙코르: 주목 소모·다음 주문 추가 피해','그랜드 피날레: 표적 반복 적중으로 3×3 폭발'),
('소피아','박사의 가르침: 직접 주문 처치 MP 회복·주문 선물 [자동]','중력 실험실: 기도술별 3×3/5×5/7×7, 주기 피해·끌기','빅뱅 가설: 직접 주문 충전 후 5×5 기폭·밀침'),
('메라','불조심의 가호: 화염 저항·불씨·반격 [자동]','화염 역분사: 불씨 소모 직선 관통 5칸','메라조 출동: 보호·불씨 충전·강화 직선 6칸'),
]
inventory = '''# 22신 기존 1·3·5성 구성 — 패시브 검토용 / 2026-10-30

이 표는 최신 승인 방향의 기능 요약이다. 모든 칸이 수동 액티브는 아니며, 자동·선물·복합 효과도 포함한다. 실제 구현 수치와 승인 설계의 차이는 `START_HERE_HOME.md`를 먼저 확인한다. 특히 마지막 비비·소피아·메라는 승인 설계 기준이며 일반 실행본에 새 전투가 연결되지 않았다.

| 신 | 1성 핵심 | 3성 핵심 | 5성 핵심 |
|---|---|---|---|
'''
inventory += '\n'.join('| ' + ' | '.join(row) + ' |' for row in rows)
inventory += '''

## 집에서 할 비교

현재 수식과 사용 비용을 펼쳐서 단일/광역 화력, 방어·회복, 제어·기동, 자원 수급, 초반 안정성, 기도술 투자, 조합 의존도를 함께 본다. 이 표만 보고 강약을 확정하지 않는다.
강한 구성은 추가 패시브 1개, 애매한 구성은 2개. 신별 개수·내용·해금 단계는 모두 미정이다. 기존 패시브를 새 추가분으로 중복 계산하지 않는다.

`analysis/design/suisei-fullkit01.json`의 집중 관측·별의 계승은 참고 후보이며 둘 다 채택한 상태가 아니다. 다음 세션은 스이세이부터 시작한다.
'''
(r/'FULLKIT_CORE_INVENTORY.md').write_text(inventory, encoding='utf-8')
for filename in ['START_HERE_HOME.md','HOME_RESUME.md','README_FIRST.md']:
    (r/filename).write_text(note,encoding='utf-8')
for filename in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','BALANCE_WORKPLAN.md']:
    p=r/filename
    p.write_text('# 최신 인계: 추가 패시브 1개/2개 차등 검토 확정 / 2026-10-30\n\n기존 1·3·5성 전체 성능을 비교하여 강한 신은 추가 패시브 1개, 애매한 신은 2개. 신별 배정·내용은 집에서 결정하며 아직 미정. 2·4성 의무 채우기 아님. START_HERE_HOME.md와 FULLKIT_CORE_INVENTORY.md부터 읽는다. 기존 스이세이 두 후보 미승인, 비비/소피아/메라 실제 전투 연결 미완료, 일반 실행본 su-five01 유지.\n\n'+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
policy={'status':'approved-workflow-only','strongKitAdditionalPassives':1,'unclearOrWeakKitAdditionalPassives':2,'mandatoryTier2And4':False,'assignmentsApproved':False,'nextGod':'suisei','nextWorkLocation':'home','inventory':'FULLKIT_CORE_INVENTORY.md'}
for filename in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
    p=r/filename; d=json.loads(p.read_text(encoding='utf-8-sig'))
    d['passiveExpansionPolicy']=policy
    d['activeWork']='home-handoff-fullkit-comparison-pending'
    d['next']='At home: review existing 1/3/5 kits starting with Suisei; strong kits add 1 passive, ambiguous kits add 2. Counts/content not assigned yet. Preserve pending Vivi/Sopia/Mela combat conversions.'
    d['archive']=name+'.zip'
    d['entryDocument']='START_HERE_HOME.md'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'analysis/design/suisei-fullkit01.json'; d=json.loads(p.read_text(encoding='utf-8-sig'))
d['workflow']='Compare existing 1/3/5 full kit first. Strong kits add 1 passive, unclear kits add 2. Candidate count and unlock tiers are not approved. Confirm per god before actual combat/VFX/save integration.'
d['passiveExpansionPolicy']=policy
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for launch in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:
    (r/launch).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\mela-review01\\tier5-dispatch01.html"\r\n',encoding='ascii')

# Reuse proven portable dependency resolution, relocated smoke tests and full ZIP hash verification.
t=(r/'scripts/package-home-lui06.py').read_text(encoding='utf-8-sig')
t=t.replace('HOLOCRAWL_HOME_2026-10-22_LUI_ATTACK06',name).replace('home-lui-handoff06','home-fullkit-handoff01')
t=t.replace("'assets','scripts','analysis/previews'", "'assets','scripts','analysis/design','analysis/previews'")
t=t.replace("def evidence_ok(p):", "selected.update(p.name for p in (r/'analysis/native').iterdir() if p.is_dir() and p.name.startswith(('raden-', 'hajime-', 'su-', 'vivi-', 'sopia-', 'mela-')))\n\ndef evidence_ok(p):")
t=t.replace("version='home-lui-attack06'", "version='home-fullkit01'")
t=t.replace("review='analysis/previews/lui-review01/index.html'", "review='analysis/previews/mela-review01/tier5-dispatch01.html'")
t=t.replace("next='Review Lui two-talon native attack GIF; then tier3 after approval. 15 gods approved.'", "next='At home compare 22 core kits: strong add 1 passive, ambiguous add 2; per-god counts/content undecided. Start Suisei. Pending Vivi/Sopia/Mela combat integration.'")
t=t.replace("currentGod='lui',currentTier=1", "currentGod='mela',currentTier=5")
t=t.replace("active=stage/'analysis/previews/lui-review01/index.html'", "active=stage/'analysis/previews/mela-review01/tier5-dispatch01.html'")
# Preserve full generated originals/GIFs for current revisions. Include current design files (absent from older packer).
anchor="files=sorted(p for p in stage.rglob('*')"
pos=t.index(anchor)
t=t[:pos]+"assert read(stage/'VFX_DRAFT_STATUS.json')['all22GodVisualsApproved'] is True\nassert read(stage/'VFX_DRAFT_STATUS.json')['passiveExpansionPolicy']['assignmentsApproved'] is False\nassert (stage/'analysis/design/mela-dispatch01.json').is_file()\nassert (stage/'FULLKIT_CORE_INVENTORY.md').is_file()\n"+t[pos:]
(r/'scripts/package-home-fullkit01.py').write_text(t,encoding='utf-8')
print('Handoff notes, core inventory, workflow policy and portable package script prepared.')
