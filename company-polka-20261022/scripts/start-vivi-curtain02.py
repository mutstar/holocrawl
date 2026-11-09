from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];shots=r/'analysis/native/vivi-curtain02/native/shots'
for frame in range(4):
 d=json.loads((shots/f'finale-burst{frame}.png-curtain.json').read_text(encoding='utf-8-sig'));assert d['status']=='passed' and d['anchors']==1 and d['span']==[3,3]
t=(r/'scripts/start-vivi-finale01.py').read_text(encoding='utf-8-sig')
for old,new in {
 'vivi-finale01':'vivi-curtain02','tier5-finale01':'tier5-curtain02',
 "'burst0','burst1','burst2','ended'":"'burst0','burst1','burst2','burst3','burst4','burst5','ended'",
 'duration=[800,450,450,650,650,160,160,90,220,220,1200]':'duration=[800,450,450,650,650,160,160,220,110,110,200,450,300,1200]',
 "frames[8].save(o/'burst.png')":"frames[11].save(o/'burst.png');frames[7].save(o/'curtain-open.png');frames[10].save(o/'curtain-closed.png')",
 '발동 → 적 조명 표식 → 다음 타격 예시 → 주변 펄 폭발 → 종료':'발동 → 적 조명 표식 → 다음 타격 예시 → 비비색 커튼이 내려옴 → 피날레 섬광 → 종료',
 '<tr><td>중앙 금빛·분홍 폭발</td><td>조명 표식이 터지는 대상</td></tr>':'<tr><td>분홍·보라 무대 천막과 내려오는 커튼</td><td>표식 대상 주변에 무대를 만들고 위에서 막이 내려오며 닫히는 피날레 연출</td></tr><tr><td>막이 닫힌 뒤 금빛·분홍 섬광</td><td>조명 표식이 터지는 순간</td></tr>',
 '중앙 폭발은18→28→26픽셀,주변 펄은10→16→14픽셀.전체를늘린한장의그림이아니라32×32개별타일로배치했습니다.':'커튼은96×96픽셀 캔버스에84×72픽셀 도트로 배치한3×3크기의무대한개입니다. 열린 천막→커튼 일부 하강→완전히 닫힘→섬광으로 소멸합니다. 잠깐 몹을 덮는 전경 연출이며 지형 변화는 없습니다. 중앙 섬광28픽셀·주변펄16픽셀,기존피해범위·수치유지.',
 '금빛 조명 표식→다음 주문 타격 예시→주변1칸펄폭발.':'금빛 조명 표식→다음 주문 타격 예시→분홍보라커튼하강→막닫힘·피날레섬광.',
 '실제 SDL 조명 표식·주변 폭발 초안':'실제 SDL 비비색 무대 커튼·피날레 초안',
 '현재5성시각검토중.':'현재5성커튼시각검토중.',
}.items():t=t.replace(old,new)
t=t.replace('周', '周')
t=t.replace('주변 작은 분홍·보라 펄', '분홍·보라 3×3 바닥과 몹 타격 섬광')
t=t.replace('주변1칸,최대3×3 폭발 범위. 아래 두 칸 떨어진 몹은 범위 밖', '막이 걷힌 직후 9칸 바닥이 밝아지고, 범위 안 몹 몸통에만 큰 섬광이 뜹니다. 아래 두 칸 떨어진 몹은 범위 밖으로 타격 섬광이 없습니다.')
t=t.replace('기존피해범위·수치유지.', '범위 안 몹에는28픽셀 타격 섬광, 빈 칸에는16픽셀 펄과 바닥 격자로 범위를 구분합니다. 타격 단계는 총0.75초로 늘렸습니다. 피해 범위·수치 설계 유지.')
t=t.replace("assets/holocrawl/vivi-curtain02/generation.json","assets/holocrawl/vivi-curtain01/generation.json")
exec(compile(t,str(Path(__file__)),'exec'))
base=r/'analysis/previews/vivi-review01'
(base/'tier5-finale01.html').write_text((base/'tier5-curtain02.html').read_text(encoding='utf-8'),encoding='utf-8')
note='# 비비5성 무대 커튼 피날레 / vivi-curtain02 / 2026-10-30\n\n사용자 피드백:커튼 이후3×3타격이 잘 안 보임. 막이 걷힌 뒤3×3바닥 하이라이트/범위 안 몹 큰 섬광/범위 밖 제외/타격 단계0.75초. 분홍커튼/보라안감/금색테두리의열린무대와닫힌커튼생성.두이미지를96캔버스/84×72도트로적용,열림→위40픽셀/64픽셀부분커튼합성→닫힘→금빛섬광→잔광.몹중심3×3의무대1개앵커/중복없음검증.피해/범위수치변경없음.표식·효과는여전히시각초안,새캐스터전투미구현/일반실행본su-five01유지.22신/복원통과. analysis/previews/vivi-review01/tier5-curtain02.html 현재5성시각검토중.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md']:
 p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')

