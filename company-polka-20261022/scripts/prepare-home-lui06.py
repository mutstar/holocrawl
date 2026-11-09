from pathlib import Path
import json,hashlib,datetime
r=Path(__file__).resolve().parents[1];rev='lui-attack06';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
summary='''# 집에서 이어하기 · 2026-10-22 · 루이 두 발 공격

이 파일은 최신 상태 요약이다. 아래의 과거 인계 기록보다 이 요약과 VFX_DRAFT_STATUS.json을 우선 확인한다.

## 시작 방법

1. ZIP 전체를 새 폴더에 풀기. 이전 폴더에 덮어쓰지 않기.
2. OPEN_VFX_REVIEW.cmd: 현재 루이 1성 실제 공격 GIF와 권능 설명/수치.
3. OPEN_GALLERY.cmd: 기존 22신 통합 미리보기. 현재 캐릭터만 표시하는 설정 유지.
4. PLAY_HOLOCRAWL.cmd: 전달된 Windows x64 실행본으로 플레이. 필요한 DLL 포함.
5. VERIFY_HOME.cmd: 압축 파일에 들어간 파일 해시 확인.

브라우저 피드백은 HTML 파일로 바로 열 수 있다. localhost:8766은 회사 서버 주소이므로 집에서 그대로 쓰지 않는다. 압축을 푼 폴더의 HTML을 열거나 집 환경에서 서버를 새로 띄운다.

## 확정/검토 상태

15신의 1·3·5성 승인 유지: 스이세이, 미코, 아키, 후부키, 아야메, 초코, 코로네, 오카유, 페코라, 노엘, 와타메, 토와, 라미, 폴카, 코요리.

현재 루이 1성 검토 중. 간모 B안 외형은 사용자가 선택하여 실제 게임에 적용했다. 최신 두 발 동시 공격 모션은 구현·캡처 완료 후 사용자 최종 확인 대기이며 1·3·5성 전체 승인을 받은 상태는 아니다.

남은 순서: 루이 → 라덴 → 하지메 → 스우 → 비비 → 소피아 → 메라. 사용자 승인 없이 성급/다음 신으로 넘어가지 않는다.

## 이번 세션에서 한 작업

- 폴카: 1성 모자 도트 정리, 3성 실제 도약/착지, 5성 세 대단원 구분 및 크기 축소까지 승인. 최종 1성 polka-vfx05 / 3성 polka-leap02 / 5성 polka-vfx07.
- 코요리: 마법형 개편 실제 적용. 3성 사거리 +1, 반응 피해 15% 감소 반영(combatRevision koyori-caster02). 1성 짧은 시험관, 3성 반응별 색상·주변 3×3 바닥/타격, 5성 작은 표식과 강화 네 번 소모·위치·색상 정리 후 전체 승인. 최종 1성 koyori-tube02 / 3성 koyori-tier3-border01 / 5성 koyori-five-critical04.
- 루이: 까마귀를 매 콘셉트로 변경. 현실적인 매 도트는 폐기하고 공식 간모(がんも)를 참고했다. 공식 참고 https://shop.hololivepro.com/products/takanelui_bd2022
- 간모 원본의 투명 노이즈가 축소 범위에 포함되어 찌그러지던 문제를 alpha>32 실루엣 기준 자르기로 해결. 기본 32×32 타일 안 최대30px.
- A 망토 제거 / B 망토 유지+좁은 몸통·날카로운 눈매 두 시안을 비교했고 사용자가 B 선택. B 서 있는 도트, 작은 활성 표식·신앙 문양 실제 적용(lui-ganmo-sharp01). 제단은 이전 간모 제단 유지.
- 일반 근접 공격 시 전용 자세 → 명중 표시 → 서 있는 자세 복귀. 빗나가면 명중 표시는 생략. 오른쪽/왼쪽 반전 도트 포함. 서 있는 도트는 승인된 B안 그대로.
- 공격 중 몸체를 숨길 때 초록 우호 원까지 없어지던 문제 수정: 기본 타일 인덱스만 제거하고 우호/상태 플래그 유지.
- 공격 도트의 세 번째 발 제거 후, 최종 사용자 요청에 따라 두 발 모두 앞으로 뻗어 동시에 할퀴는 자세로 변경. 최신 버전 lui-attack06. 발을 딛는 한 발 공격은 이전 버전이며 재적용하지 않기.

## 최신 실제 자료

- 현재 미리보기: analysis/previews/lui-review01/index.html
- 실제 일반 공격 GIF: analysis/previews/lui-attack06/attack.gif
- 브라우저 확인: analysis/previews/lui-attack06/browser-proof.png
- 공격 도트 원본/프롬프트: assets/holocrawl/lui-attack06/
- 승인된 B 서 있는 원본: assets/holocrawl/lui-ganmo-sharp01/body-source.png
- A/B 비교: analysis/previews/lui-ganmo-compare01/index.html
- native 원본 캡처/검증/패치: analysis/native/lui-attack06/
- 우호 원 전 프레임 검사: analysis/previews/lui-attack06/friendly-halo-validation.json

## 소스 및 구현 주의점

- 권위 소스: engine/campaign-crawl/crawl-ref/source
- SDL 빌드용 사본: engine/tiles-crawl/crawl-ref/source. scripts/prepare-tiles-source.py로 권위 소스에서 동기화한다.
- 최신 실행본: runtime/tiles01/HoloCrawl.exe. SHA256은 HOME_HANDOFF_STATE.json / TRANSFER_MANIFEST.json 참조.
- 일반 공격 호출: melee-attack.cc → holo_visual::hawk_attack. friendly 간모만 재생한다. 공격 판정/HP/시간/RNG는 변경하지 않는다.
- holo-visual.cc/h: 공격 오버레이, 좌우 도트 선택, 명중 표시와 상태 불변 검사. tilereg-dgn.cc: 공격 도중 native 우호/상태 플래그 보존.
- 도트: rltiles/holo/raven.png, raven_1.png는 B 서 있는 자세. lui_attack.png, lui_attack_left.png가 최신 두 발 공격. 내부 raven ID/파일명은 저장 호환 때문에 유지. 화면 이름은 Holo hawk, 과거 Holo raven도 지원.
- 루이 3성 사냥 지휘의 직접 타격은 일반 근접 공격과 다른 호출 경로다. 3성 검토 때 공격 모션 연결 여부를 별도 확인한다. 3성/5성 기존 큰 깃털 고리는 아직 간모 전용 새 도트로 승인된 것이 아니다.

## 검증 결과와 한계

- 최신 native 22신 기능 검사 통과, 새 프로세스 저장 복원 통과, 코요리 복원 검사 통과.
- 루이 1성 신앙30 실제 일반 공격으로 피해2 확인(테스트 1회 예시이며 고정 피해 수치가 아님).
- 공격 연출 전후 전투 상태/RNG 불변 검사 통과. 공격 모든 프레임의 초록 우호 원 확인.
- 이전 실패 시도 lui-attack01~03은 최신 적용본이 아니다. 0피해 명중도 가능한데 최초 테스트가 첫 명중 즉시 피해를 요구하여 실패했던 조건을 수정했다. 최신 테스트는 실제 피해가 들어갈 때까지 제한 횟수 내 확인한다.
- 봇 승률 백테스트/실플레이 전체 클리어 검증은 이번 범위가 아니다.

## 집 코덱스에 붙여넣을 문장

“START_HERE_HOME.md와 CONTINUE_HERE.md, HOME_HANDOFF_STATE.json을 읽고 이어가자. 최신은 lui-attack06, 루이는 날카로운 간모 B안이고 두 발로 동시에 공격하며 초록 우호 원이 유지된다. 실제 필드 공격 GIF부터 보여주고 확인한 뒤 루이 3성 사냥 지휘로 이어가자. 폴카·코요리를 포함한 기존 15신 승인은 유지해.”

## 전달 범위

소스 두 사본, 최신 Windows 실행본과 DLL, 도트·원본·프롬프트, 기존 승인 미리보기와 최신 초안, 최신 native 증거, 제작/빌드/검사 스크립트를 포함한다. 컴파일러 .toolchain, 오브젝트·빌드 캐시, 과거 중복 실행파일, 테스트 세이브·실제 플레이 세이브는 제외한다. 실행과 미리보기에는 컴파일러가 필요 없다. 재빌드는 집의 기존 MSYS2/MINGW64 .toolchain을 사용하거나 새 환경에서 설정한다. 스크립트의 회사 절대경로는 과거 생성 기록이며 새 작업 경로로 교체한다.
'''
for n in ['START_HERE_HOME.md','HOME_SESSION.md','HOME_RESUME.md','README_FIRST.md']:(r/n).write_text(summary,encoding='utf-8')
for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md']:
 p=r/n;p.write_text(summary+'\n\n---\n\n이하 과거 기록(최신 요약 우선)\n\n'+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
(r/'START_HERE_COMPANY.md').write_text('# 최신 전달본\n\nSTART_HERE_HOME.md부터 읽는다. 현재 루이1성, 최신 lui-attack06.\n',encoding='utf-8')
for n,target in [('OPEN_VFX_REVIEW.cmd','lui-review01'),('OPEN_GALLERY.cmd','all-gods-vfx-draft04')]:
 (r/n).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\'+target+'\\index.html"\r\n',encoding='ascii')
for n in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json','engine/campaign_status.json','engine/implementation_status.json']:
 p=r/n;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(savedAtUtc=now,entryDocument='START_HERE_HOME.md',currentVisualReviewGod='lui',currentVisualReviewTier=1,visualRevision=rev,next='Review latest two-talon ordinary attack GIF, then Lui tier3 only after user approval.',currentVisualReview='analysis/previews/lui-review01/index.html',playBinarySha256=hashlib.sha256((r/'runtime/tiles01/HoloCrawl.exe').read_bytes()).hexdigest())
 if n=='HOME_HANDOFF_STATE.json':d.update(version='home-lui-attack06',gameVersion=rev,visualVersion=rev,visualValidation='analysis/native/lui-attack06/checkpoint-manifest.json')
 if 'tierApprovals' in d:
  d.update(revision=rev,review='analysis/previews/lui-review01/index.html',archive='HOLOCRAWL_HOME_2026-10-22_LUI_ATTACK06.zip')
  d['tierApprovals']['lui']['feedback']='B안 외형 선택 및 적용. 최신 두 발 동시 공격/우호 원 유지 구현 완료. 최신 모션 사용자 확인 대기.'
  d['tierApprovals']['polka']['feedback']='1·3·5성 전체 승인. 최종 5성 polka-vfx07.'
  d['tierApprovals']['koyori']['feedback']='1·3·5성 전체 승인. 최종 5성 koyori-five-critical04.'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Latest home handoff documents and entry points updated.')
