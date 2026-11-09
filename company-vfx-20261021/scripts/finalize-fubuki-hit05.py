from pathlib import Path
import json,hashlib,shutil,difflib
root=Path(__file__).resolve().parents[1];run=root/'analysis/native/fubuki-vfx05';src=root/'engine/campaign-crawl/crawl-ref/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((run/'gallery-validation.json').read_text(encoding='utf-8'))['status']=='passed'
old=(run/'before/holo-batch-summons.cc').read_text(encoding='utf-8')
new=(src/'holo-batch-summons.cc').read_text(encoding='utf-8')
start=new.index('std::vector<coord_def> hit_positions;');end=new.index('s.three_ready=now+5+30;',start)
normalized=new[:start]+'for(mid_t id:enemies(old,1)) { monster *mon=monster_by_mid(id);if(mon && mon->alive()) foxfire(*fox,*mon,roll_dice(1,6+s.inv/3),true); }\n                    '+new[end:]
normalized=normalized.replace('holo_visual::fox_swap(old,dest,hit_positions);','holo_visual::fox_swap(old,dest);')
assert normalized==old,'Combat source changed outside read-only HP/position capture'
write(run/'combat-hook-audit.json',{'status':'passed','combatSourceEquivalentAfterRemovingHitRecording':True,'damageRollCallAndArgumentsUnchanged':True,'hitCueRequiresActualHpDecrease':True,'existingArtHashesPreserved':True})
patch=''
for p in (run/'before').rglob('*'):
    if p.is_file() and p.suffix!='.exe':
        rel=p.relative_to(run/'before');target=src/rel
        out=run/'source_snapshot'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,out)
        patch+=''.join(difflib.unified_diff(p.read_text(encoding='utf-8').splitlines(True),target.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+rel.as_posix(),tofile='after/'+rel.as_posix()))
(run/'source.patch').write_text(patch,encoding='utf-8')
binary=run/'capture-engine.exe';runtime=root/'runtime/tiles01/HoloCrawl.exe'
assert sha(runtime)==sha(run/'before/HoloCrawl.exe'),'Runtime changed during capture'
shutil.copy2(binary,runtime);h=sha(runtime);assert h==sha(binary)
for rel in ['HOME_HANDOFF_STATE.json','engine/campaign_status.json']:
    p=root/rel;obj=json.loads(p.read_text(encoding='utf-8'));obj['visualRevision']='fubuki-vfx05';obj['fubukiVisualReview']='analysis/previews/fubuki-vfx05/index.html';obj['fubukiVisualValidation']='analysis/native/fubuki-vfx05/gallery-validation.json';obj['fubukiVisualFeedback']='Actual damaged enemies receive foreground blue foxfire; floor range retained; awaiting user visual approval.'
    for key in ['playBinarySha256','tilesBuildSha256']:
        if key in obj:obj[key]=h.upper()
    write(p,obj)
p=root/'scripts/god-art-skills.json';s=p.read_text(encoding='utf-8').replace('실제 교환 두 자리의 흰 연기 → 출발점 주변 푸른 여우불','실제 교환 두 자리의 흰 연기 → 출발점 주변 푸른 여우불 + 실제 피해 대상 위 여우불');p.write_text(s,encoding='utf-8')
for rel in ['analysis/previews/fubuki-review01/index.html','analysis/previews/god-vfx-ingame/index.html']:
    p=root/rel;s=p.read_text(encoding='utf-8').replace('fubuki-vfx04','fubuki-vfx05');p.write_text(s,encoding='utf-8')
note='''# 최신: 후부키 실제 피해 대상 여우불 — fubuki-vfx05 (2026-10-21)

뭇별의 적에게도 여우불 표시 요청을 반영했다. 3성 바꿔치기 직후 HP가 실제 감소한 적 좌표만 기록해 기존 푸른 여우불 도트를 전경에 표시한다. 기존 바닥 반경1 표시는 유지한다. 새 지속 화상/추가 피해가 아니며, 피해 주사위·비용·시간·소환 규칙은 이전 원문 대조로 보존했다. 기존 도트도 변경하지 않았다.

실제 SDL 캡처에서 대상1, HP10000→9997과 여우4/등장 순서를 확인하고 22신 권능·저장 및 별도 프로세스 재로드 검사를 통과한 동일 바이너리를 설치했다. 장면 중 상태/RNG 보존도 확인했다. 고정 전투장 시각 검증이며 일반 캠페인 클리어율 검증은 아니다.

미리보기: analysis/previews/fubuki-vfx05/index.html. 근거: analysis/native/fubuki-vfx05/gallery-validation.json, capture-validation.json, combat-hook-audit.json, source.patch. 이전04와 그 이전 실패 원본은 보존했다. 다음은 후부키 피드백이며 스이세이·미코·아키 승인 유지. 다른 신/봇 작업은 시작하지 않는다.

---

'''
p=root/'START_HERE_HOME.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=root.parent/'CURRENT_WORKSPACE.md';s=p.read_text(encoding='utf-8');p.write_text('# Current visual review: Fubuki VFX05\n\nActive: HoloCrawl_HOME_2026-10-20. Actual enemy HP-loss foxfire overlay implemented and native validated. See START_HERE_HOME.md and analysis/previews/fubuki-vfx05/index.html. Await user feedback; Suisei/Miko/Aki accepted.\n\n---\n\n'+s,encoding='utf-8')
write(run/'checkpoint-manifest.json',{'status':'passed','revision':'fubuki-vfx05','runtimeSha256':h,'combatAudit':'combat-hook-audit.json','nativeValidation':'capture-validation.json','galleryValidation':'gallery-validation.json','feedback':'pending','scope':'Visual target hit cue only; no new damage or burn status'})
print('Installed tested Fubuki VFX05 '+h)
