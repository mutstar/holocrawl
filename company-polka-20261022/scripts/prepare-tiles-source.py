from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];src=root/'engine/campaign-crawl/crawl-ref/source';dst=root/'engine/tiles-crawl/crawl-ref/source'
if not dst.exists():
 shutil.copytree(src,dst,ignore=shutil.ignore_patterns('*.o','*.d','*.exe','*.elf','saves','morgue','.cflags','.lflags','.contrib-libs'))
else:
 files=[p for p in src.iterdir() if p.suffix in {'.h','.cc'} and p.name not in {'build.h','compflag.h'}]+[src/'Makefile.obj']
 files+=list((src/'rltiles/holo').glob('*.png'))+[src/'rltiles'/n for n in ['dc-main.txt','dc-feat.txt','dc-holo-main.txt','dc-holo-feat.txt','dc-player.txt','dc-holo-player.txt']]
 for p in files:
  target=dst/p.relative_to(src)
  if not target.exists() or p.read_bytes()!=target.read_bytes():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
print('Tile checkout synchronized from campaign source; generated tile metadata and objects are kept separate.')
