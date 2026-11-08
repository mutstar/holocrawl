from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1]
for kind in ['street','market']:
 S=R/f'preview/city-{kind}119';O=R/f'preview/city-{kind}120';O.mkdir(exist_ok=True)
 for p in S.iterdir():
  if p.suffix in ['.js','.json','.html','.css'] and p.name not in ['validation.json','inputs.json']:shutil.copy2(p,O/p.name)
 p=O/'index.html';s=p.read_text(encoding='utf-8').replace('세로 벽면 부착 수정119','높인 벽 전면과 소품 크기120').replace('119','120')
 # Keep the previous implementation available for comparison, add the new bay.
 s=s.replace('../wall-mount120/mount120.js','../wall-mount119/mount119.js').replace('<script src="../wall-mount119/mount119.js"></script>','<script src="../wall-mount119/mount119.js"></script><script src="../wall-bay120/bay120.js"></script>')
 s=s.replace('../wall-mount120/all-nine-before-after.png','../wall-bay120/size-comparison120.png')
 if kind=='market':s=s.replace('진열창·셔터·포스터는 벽 윗면을 침범하지 않고 아래쪽 세로 벽면 안에 붙입니다. 바닥 소품의 크기와 접지·의류 색상은117 그대로입니다.','소품을 크게 되돌리고, 소품이 붙는 구간만 실제 벽 전면을 높여 받쳐주는 비교 시안입니다. 일반 벽과 바닥 소품은 유지합니다.')
 else:s=s.replace('진열창과 설비는 타일 아래쪽 세로 벽면 안에만 붙이고 윗면과 테두리는 비워둡니다.','진열창과 설비가 붙은 부분의 실제 벽 전면을 높여 소품 크기를 회복한 비교 시안입니다.')
 p.write_text(s,encoding='utf-8')
 if kind=='market':
  p=O/'app.js';p.write_text(p.read_text(encoding='utf-8').replace('WallMount119','WallBay120'),encoding='utf-8')
 else:
  s=(S/'review119.js').read_text(encoding='utf-8').replace('play119','play120').replace('WallMount119','WallBay120').replace('부착119','전면120')
  (O/'review120.js').write_text(s,encoding='utf-8');(O/'review119.js').unlink()
  p=O/'manifest.json';a=json.loads(p.read_text(encoding='utf-8'));a['revision']=120;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs={'revision':120,'nativeIntegrated':False,'studyOnly':True,'wallHeightChangedOnlyAtMounts':True,'geometryChanged':False,'sourceFiles':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['city-street119','city-market119','wall-mount119'] for p in (R/'preview'/name).iterdir() if p.suffix in ['.js','.json','.css','.html']}}
(R/'preview/wall-bay120/inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
print('Prepared120 localized taller wall-front size study;119 preserved.')
