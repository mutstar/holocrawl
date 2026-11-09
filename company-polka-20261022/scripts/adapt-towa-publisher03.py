from pathlib import Path
p=Path(__file__).with_name('publish-towa-support02.py');s=p.read_text(encoding='utf-8').replace('towa-support02','towa-support03')
s=s.replace("changed=['holo-visual.h','holo-visual.cc','holo-batch-space.cc','holo-campaign-test.cc']","changed=['holo-visual.cc','rltiles/dc-holo-main.txt']")
s=s.replace('Native TILE_BOLT_MAGIC_DART overlay at actual support shot callback; no separate bolt damage simulation','Generated silver/brass bullet with short magenta tracer, 8 directional main-atlas tiles; native support callback')
s=s.replace('자주색 탄환','은빛 탄두·짧은 자주색 궤적').replace('자주색기존탄환타일','은빛탄두+짧은자주색궤적 전용8방향타일')
Path(__file__).with_name('publish-towa-support03.py').write_text(s,encoding='utf-8')
