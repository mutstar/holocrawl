from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];old=root.parent/'company-polka-20261022'
inventory=json.loads((root/'analysis/legacy-inventory.json').read_text(encoding='utf-8'))
validation=json.loads((root/'analysis/base-validation.json').read_text(encoding='utf-8'))
assert validation['status']=='passed'
assert hashlib.sha256((old/'runtime/tiles01/HoloCrawl.exe').read_bytes()).hexdigest()==inventory['legacyRuntimeSha256']
state={'updated':'2026-11-04','targetVersion':'0.34.1','targetCommit':inventory['upstreamCommit'],'activeProject':str(root),'legacyProject':str(old),'phase':'base-engine-validated','baseBuildPassed':True,'baseValidationPassed':True,'legacyRuntimeUnchanged':True,'legacyCustomFiles':27,'legacyCoreHookFiles':42,'godCount':22,'godsIntegrated':False,'worshipIntegrated':False,'godSaveIntegrated':False,'pietyIntegrated':False,'abilitiesIntegrated':False,'customDungeonIntegrated':False,'previewCopied':True,'stairsApproved':True,'next':'Port ordinary worship and save persistence into 0.34.1, then shared combat hooks and god abilities.','migrationComplete':False}
(root/'migration-status.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n in ['HOME_HANDOFF_STATE.json','VFX_DRAFT_STATUS.json']:
 p=old/n;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(activeProject=str(root),targetEngineVersion='0.34.1',activeWork='engine-0341-migration',migrationStatus=str(root/'migration-status.json'),lastArchiveIncludesLatest=False,next=state['next']);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 새 기반 0.34.1로 전환 / 2026-11-04\n\n사용자 확정: 최신 안정판0.34.1 기반. 새 작업 폴더는 '+str(root)+' 이며 README.md/CONTINUE_HERE.md/migration-status.json을 먼저 읽는다. 공식 원본 빌드·데이터 생성·LOS3종 검증 완료, 기존 홀로신 소스27개와 코어 연결파일42개 목록 및 확정 거리·계단 자산 보존. 홀로신 숭배·저장·권능/새 던전은 아직 이식 전. 기존0.24 runtime ayame-zanshin02와 해시 유지. 다음은0.34.1 일반 숭배·저장 연결.\n\n'
for p in [root.parent/'CONTINUE_HERE.md',*[old/n for n in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','START_HERE_HOME.md']]]:
 p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps(state,ensure_ascii=False))
