from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/night-vfx04'
v=json.loads((run/'gallery-validation.json').read_text(encoding='utf-8'));assert v['status']=='passed' and v['abilityTiers']==66
note='''# 최신 인계 ·22신 이펙트 통합 초안 (2026-10-21)

뭇별 요청: 초코1성 하트를 몬스터 칸 우측 모서리로 옮기고, 남은 신들의 이펙트 초안을 진행해 승인본과 합쳐 회사에서 피드백을 이어간다.

현재 시각 버전: night-vfx04. 통합 보기: analysis/previews/all-gods-vfx-draft04/index.html.22신66단계에 실제 권능/상태/무료 설정/선물 화면을 연결했다. 스이세이·미코·아키·후부키·아야메는 승인 유지. 초코는1성 위치 수정안, 나머지16신은 사용자 승인 전 모티프 기반 초안이다. 방향별 투사체·모든 시약 반응·순차 소환 등 세부 연출은 신별 한계에 명시했다. 그 한계를 숨기고 완성본으로 부르지 않는다.

초코 하트는 타일 내부 우측 상단 최대12px. 실제 바로 위 칸 몬스터 대조에서 위 칸 픽셀 동일/대상 칸 표식 표시를 확인했다. 회복0·매혹 실패·정신 면역·만료 대조도 유지했다. 소피아는 무시되는 새 조준점이 아니라 실제 저장된 중력장 중심에서 강화 문양을 표시한다. 페코라는 준비/예약과 실제 폭발을 구분한다. 선택형 대조에는 박수3·채색3·추가 적 등 명시된 검사 준비가 포함된다.

22신 권능·저장22회·별도 프로세스 재로드, 전체370개 실제 SDL 원본 화면과 전투 원문/기존 아트 대조를 통과했다. 전투 수치·확률·저장 형식 변경 없음. 고정 테스트 전투장이며 캠페인 클리어율/모든 조건의 완성 검증은 아니다.

로컬 근거: analysis/native/night-vfx04/capture-validation.json, gallery-validation.json, combat-hook-audit.json, corner-native-validation.json, source.patch.01은 기본 검증 통과 후 노엘 메뉴1성 캡처 누락을 보강했고02는 장전 전 지연기폭을 시도한 검사 실패로 원본/GDB 스택을 보존했다.03은 검증을 통과한 중간안,04는 소피아 중심 정렬 수정 및 동일 검증을 통과한 최종 초안이다.

도트: built-in imagegen. 새16신 원본/전체 프롬프트는 assets/holocrawl/night-vfx01(originals, inputs.json, ACTUAL_PROMPT_OVERRIDES.json). 초코 원본은 assets/holocrawl/choco-vfx01. 회사 피드백 입력: VFX_COMPANY_FEEDBACK.md 또는 통합 페이지 JSON 저장.

회사 전달 파일: exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT.zip. 새 폴더에 압축을 풀고 START_HERE_COMPANY.md를 먼저 읽는다. 실행본·의존 DLL·수정 소스·아트·기획·승인본·새 초안·검증을 포함한다. 큰 컴파일러/빌드 캐시/과거 조우 원시 데이터는 로컬 보존하고 전달본에서는 제외한다. 재빌드는 회사의 기존 MSYS2/MINGW64 .toolchain을 재사용한다. 최종 이동 경로 실행/ZIP 전수 해시는 analysis/native/night-vfx04/transfer-validation.json에서 확인한다.

다음: 회사에서 신별 이펙트 피드백. 승인된5신을 임의 변경하지 않는다. 새로운 밸런스 시뮬레이션/음악/전체 플레이어·몬스터 아트 제작을 시작하지 않는다.

---

'''
for name in ['START_HERE_HOME.md','START_HERE_COMPANY.md','HOME_SESSION.md','HOME_RESUME.md','CONTINUE_HERE.md']:
    p=root/name;p.write_text(note+(p.read_text(encoding='utf-8-sig') if p.exists() else ''),encoding='utf-8')
(root/'CURRENT_WORKSPACE.md').write_text(note,encoding='utf-8')
p=root.parent/'CURRENT_WORKSPACE.md';p.write_text('Active: C:/Users/IN/Documents/ChatGPT/Game/HoloCrawl_HOME_2026-10-20. Latest night-vfx04;22-god integrated VFX drafts complete, company transfer at exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT.zip. Await company feedback. See project START_HERE_COMPANY.md.\n\n'+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
state={'revision':'night-vfx04','approvedGods':v['approvedGods'],'cornerRevision':'choco','draftGods':v['draftGods'],'abilityTiers':66,'nativeScreenshots':370,'review':'analysis/previews/all-gods-vfx-draft04/index.html','next':'Company visual feedback','numericChanges':False,'archive':'exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT.zip'}
(root/'VFX_DRAFT_STATUS.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['HOME_HANDOFF_STATE.json','engine/implementation_status.json']:
    p=root/name
    if p.exists():
        obj=json.loads(p.read_text(encoding='utf-8-sig'));obj['vfxDraftHandoff']=state;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Latest home/company handoff and approval/draft statuses written.')
