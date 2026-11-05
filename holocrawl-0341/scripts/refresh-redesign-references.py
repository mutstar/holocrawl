from pathlib import Path
import json,shutil,re
r=Path(__file__).resolve().parents[1];old=r.parent/'company-polka-20261022';p=r/'design/gods0341.json';data=json.loads(p.read_text(encoding='utf-8'))
refs=r/'design/redesign-references';refs.mkdir(exist_ok=True)
for name in ['sopia-caster01.json','mela-heat3-01.json','mela-dispatch01.json']:shutil.copy2(old/'analysis/design'/name,refs/name)
for name in ['tier1-lipstick01.html','tier3-encore04.html','index.html']:
 source=old/'analysis/previews/vivi-review01'/name
 text=re.sub(r'<style.*?</style>','',source.read_text(encoding='utf-8'),flags=re.S)
 (refs/('vivi-'+name+'.txt')).write_text(re.sub('<[^>]+>',' ',text),encoding='utf-8')
revisions={
 'vivi':{1:('스포트라이트','passive','공격 주문 적중으로 주목3중첩까지 축적하고 다음 주문 피해 보조. 립스틱으로 표시.'),3:('앙코르','active','주목을 모두 소모해 다음 공격 주문의 추가 타격을 예약. 피해만 추가하고 상태·소환·지형은 복제하지 않음.'),5:('그랜드 피날레','active','공격 주문으로 조명 표식 부여, 같은 적을 다음 주문으로 맞히면 주변1칸 폭발. 커튼 연출.')} ,
 'sopia':{1:('박사의 가르침','passive','직접 공격 주문 처치 시 사용MP 범위 내 일부 회복. 신앙 이정표마다 주문 선물 선택.'),3:('중력 실험실','active','기도술에 따라3×3/5×5/7×7 중력장. 낮은 지속 피해와 끌어당김.'),5:('빅뱅 가설','active','공격 주문으로 충전한 뒤 별빛·빅뱅 효과로 방출하는 마법형 권능.')} ,
 'mela':{1:('불조심의 가호·불씨 반격','passive','피격·화염 접촉으로 불씨를 최대3개 축적하고 반격에 사용. 기존6불씨 구현과 구분.'),3:('화염 역분사','active','불씨를 사용한 직선 관통 화염 분사. 이전 부채꼴 설계는 교체 대상.'),5:('메라조 출동!','active','일정 시간 자동 불씨 충전, 주변 화염 보호 및 강화 직선 분사.')}
}
for god in data['gods']:
 if god['id'] not in revisions:continue
 for a in god['ability_slots']:
  if a['tier'] in revisions[god['id']]:
   a['name'],a['kind'],a['summary']=revisions[god['id']][a['tier']]
   a['design_status']='approved_redesign_reference_requires_0341_review'
   a['reference']='design/redesign-references/'
   a.pop('legacy_activation_label',None)
 god['reference']='design/redesign-references/'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Preserved latest Vivi/Sopia/Mela designs, separate from legacy live combat.')
