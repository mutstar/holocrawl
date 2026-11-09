"""Publish the revised visual draft using the established native preview workflow."""
from pathlib import Path
source=Path(__file__).with_name('finish-miko-bloom01.py').read_text(encoding='utf-8')
changes={
    'miko-bloom01':'miko-bloom03',
    '작은 벚꽃 세 송이가 캐릭터에게 모이고 짧게 사라집니다.':'초록 십자가가 캐릭터 위로 떠오르고 작은 벚꽃 다섯 송이가 주변으로 모였다가 사라집니다.',
    '같은 벚꽃 회수 뒤 캐릭터 머리 오른쪽에 분홍 꽃무늬 방패가 남습니다. 몬스터와 바닥 표식에 섞이지 않도록 위쪽에 배치했습니다.':'회복 연출 뒤 캐릭터를 감싸는 연한 분홍색 원형 보호막이 남습니다. 가운데가 투명해 캐릭터가 그대로 보입니다.',
    'Generated sakura blossom travels to player; generated pink floral shield persists beside upper-right head in overflow draft.':'Green healing cross rises with five sakura blossoms; pale pink transparent-center circular barrier surrounds the character in overflow draft.',
    '벚꽃3개 이동→소멸 / 이동→분홍 꽃무늬 방패 표시':'초록 십자가+벚꽃5개→소멸 / 회복연출→캐릭터를 감싸는 연분홍 보호막',
    'blossom recovery/petal shield visual draft':'green-cross/blossom healing and enclosing pale-pink barrier visual draft',
    'if old.is_file():':"if old.is_file() and old.suffix!='.png':"
}
for old,new in changes.items():
    assert old in source,old
    source=source.replace(old,new)
exec(compile(source,str(__file__),'exec'))
