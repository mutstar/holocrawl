from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
base=root/'runtime/base0341';out=root/'runtime/street01';source=root/'engine/upstream/crawl-ref/source'
out.mkdir(parents=True,exist_ok=True)
for name in ['dat','settings','test']:
    shutil.copytree(base/name,out/name,dirs_exist_ok=True)
for path in base.glob('*.dll'):shutil.copy2(path,out/path.name)
for path in (source/'dat/tiles').glob('*.png'):shutil.copy2(path,out/'dat/tiles'/path.name)
for name in ['saves','morgue','scripts']:(out/name).mkdir(exist_ok=True)
(out/'scripts/holo_street_native.lua').write_text('assert(crawl.holo_street_test())\n',encoding='utf-8')
(out/'init.txt').write_text('''name = HoloStreet
species = Human
background = Fighter
weapon = long sword
save_dir = saves/
morgue_dir = morgue/
remember_name = false
show_more = false
tile_full_screen = false
tile_window_width = 1280
tile_window_height = 900
tile_cell_pixels = 32
''',encoding='utf-8')
print('Prepared isolated street runtime; original baseline and saves untouched.')
