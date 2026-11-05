from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'terrain.js';s=p.read_text(encoding='utf-8').replace('images.wallPipeHorizontal09','images.wallPipeElbows10');p.write_text(s,encoding='utf-8')
p=out/'boot.js';s=p.read_text(encoding='utf-8').replace("wallPipeHorizontal09:'assets/wall-pipe-horizontal09-96.png'", "wallPipeElbows10:'assets/wall-pipe-elbows10-96.png'");p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('wall-equipment09','pipe-elbows10');p.write_text(s,encoding='utf-8')
p=out/'wall-equipment-review.html';s=p.read_text(encoding='utf-8').replace('wall-pipe-horizontal09-field.png','wall-pipe-elbows10-field.png');p.write_text(s,encoding='utf-8')
p=root/'scripts/show-wall-equipment06.cjs';s=p.read_text(encoding='utf-8').replace('wall-pipe-horizontal09-field.png','wall-pipe-elbows10-field.png').replace("'가로 연결 배관'","'양끝 반대 꺾임 배관'");p.write_text(s,encoding='utf-8')
s=(root/'scripts/check-horizontal-pipes09.cjs').read_text(encoding='utf-8').replace('wall-pipe-horizontal09-field.png','wall-pipe-elbows10-field.png').replace('horizontal-pipes09-validation.json','pipe-elbows10-validation.json');(root/'scripts/check-pipe-elbows10.cjs').write_text(s,encoding='utf-8')
print('Pipe ends:left up/right down. Existing deterministic3–5tile span rules retained.')
