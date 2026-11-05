from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'terrain.js';s=p.read_text(encoding='utf-8').replace('images.wallPipe07','images.wallPipe08').replace('images.wallCabinet07','images.wallCabinet08');p.write_text(s,encoding='utf-8')
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace("wallPipe07:'assets/wall-pipe07-32.png',wallCabinet07:'assets/wall-cabinet07-32.png'", "wallPipe08:'assets/wall-pipe08-32.png',wallCabinet08:'assets/wall-cabinet08-32.png'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('wall-equipment07','wall-equipment08');p.write_text(s,encoding='utf-8')
print('Pipe bundle and low electrical box connected; accepted AC/vent and gameplay unchanged.')
