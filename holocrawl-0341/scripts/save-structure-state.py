from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];old=r.parent/'company-polka-20261022'
proof=json.loads((r/'analysis/structure01/validation.json').read_text(encoding='utf-8'));assert proof['status']=='passed' and proof['catalogMatchesEditableSource'] and proof['freshProcessRestore']
p=r/'migration-status.json';d=json.loads(p.read_text(encoding='utf-8'));d.update(phase='god-structure-scaffold',godStructureRegistered=22,abilitySlotsDefined=110,allSlotsMandatory=False,frameworkStateImplemented=True,nativePropertyAdapterImplemented=True,nativeStructureChecks=proof['checks'],freshFrameworkProcessRestore=True,worshipIntegrated=False,godSaveIntegrated=False,pietyIntegrated=False,abilitiesIntegrated=False,implementedCombatHandlers=0,structureReview='preview/gods/index.html',next='Review and revise god structure, then connect ordinary worship/altar/menu/player-save hooks and individual effects.',migrationComplete=False)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 22신 공통 구조 마련 / 2026-11-04\n\n현재0.34.1 새 프로젝트에서 구조 먼저 작성하고 개별 수정하는 방침. design/gods0341.json에22신·110자리,1/3/5기존권능+2/4선택적패시브. 전부5개효과를 주기로 확정한 것은 아님. design/GOD_FRAMEWORK.md와 preview/gods/index.html(http://127.0.0.1:8797/gods/) 참조. C++등록표·분리자원·신앙단계·전환·임시상태정리·버전속성저장 어댑터 구현. 582구조검사/원본설계표와네이티브일치/새프로세스속성복원/22프로필화면 통과. 일반게임 제단·권능메뉴·전체캐릭터저장/전투효과는 아직 미연결. 비비·소피아·메라는 최신개편안으로 참고표 갱신. BUILD_STRUCTURE.ps1 사용, baseline0.34.1 실행파일 보존.\n\n'
for p in [r/'README.md',r/'CONTINUE_HERE.md',r.parent/'CONTINUE_HERE.md',*[old/n for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md']]]:
 p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for n in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
 p=old/n;state=json.loads(p.read_text(encoding='utf-8-sig'));state.update(activeWork='god-structure-first',activeProject=str(r),godStructureReview=str(r/'preview/gods/index.html'),godStructureCount=22,abilitySlotsDefined=110,allAbilitySlotsMandatory=False,lastArchiveIncludesLatest=False,next=d['next']);p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved structure-first checkpoint; live gameplay hooks remain pending.')
