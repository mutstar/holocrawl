"""Put ordinary street/market wall fixtures on material92's actual front."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1]
M=R/'preview/city-market119';S=R/'preview/city-market117';M.mkdir(exist_ok=True)
for p in S.iterdir():
 if p.suffix in ('.html','.js','.css','.json') and p.name not in ('validation.json','inputs.json'):shutil.copy2(p,M/p.name)
p=M/'app.js';s=p.read_text(encoding='utf-8').replace('Scene112.draw(ctx,shop,map,images,t,stockMix)','WallMount119.drawFixture(ctx,shop,map,images,t,stockMix)');p.write_text(s,encoding='utf-8')
p=M/'index.html';s=p.read_text(encoding='utf-8').replace('쇼핑백 접지·의류 진열 수정117','세로 벽면 부착 수정119').replace('상점가117','상점가119').replace('app.js?v=117','app.js?v=119').replace('<script src="scene117.js"></script>','<script src="scene117.js"></script><script src="../wall-mount119/mount119.js"></script>')
s=s.replace('쇼핑백은 바닥 접촉부에 그림자를 붙이고, 티셔츠·후드는 원래 의류 면에 멤버색을 입혔습니다. 기존 크기와 다른 소품의 그림자는 유지합니다.','진열창·셔터·포스터는 벽 윗면을 침범하지 않고 아래쪽 세로 벽면 안에 붙입니다. 바닥 소품의 크기와 접지·의류 색상은117 그대로입니다.')
s=s.replace('<div class="reviewbar">','<div class="reviewbar"><a href="../city-street119/">1~3층 거리 보기</a><a href="../wall-mount119/all-nine-before-after.png">벽 부착9종 전후 비교</a>')
p.write_text(s,encoding='utf-8')
T=R/'preview/city-street119';B=R/'preview/city-street118';T.mkdir(exist_ok=True)
for name in ['index.html','manifest.json','wall92.json','ambient118.js']:shutil.copy2(B/name,T/name)
p=T/'index.html';s=p.read_text(encoding='utf-8').replace('거리 소품 재연결118','세로 벽면 부착 수정119').replace('review118.js','review119.js').replace('<script src="ambient118.js">','<script src="../wall-mount119/mount119.js"></script><script src="ambient118.js">')
s=s.replace('<button id="streetShops">','<a href="../city-market119/">4~7층 상점가 보기</a><a href="../wall-mount119/all-nine-before-after.png">벽 부착9종 전후 비교</a><button id="streetShops">')
s=s.replace('상점가보다 드문 진열과 벽 설비를 확인해 보세요.','진열창과 설비는 타일 아래쪽 세로 벽면 안에만 붙이고 윗면과 테두리는 비워둡니다.')
p.write_text(s,encoding='utf-8')
p=T/'manifest.json';a=json.loads(p.read_text(encoding='utf-8'));a['revision']=119;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=(B/'review118.js').read_text(encoding='utf-8').replace('window.play118=','window.play119=')
s=s.replace('Scene112.draw(q,p,stock,images,32,0)','WallMount119.drawFixture(q,p,{...m,...stock},images,32,0)')
start=s.index('  for(const p of plan.infra)clipped(');end=s.index('  for(const p of plan.floor)',start)
s=s[:start]+'  for(const p of plan.infra)clipped(p,p.length,1,q=>WallMount119.drawUtility(q,p,m,utility118,32));\n'+s[end:]
s=s.replace('초반 소품118 검토','세로 벽면 부착119 검토')
# Expose read-only references for the per-pixel render audit, not gameplay state.
s=s.replace('window.play119={','window.play119={getWallUnits:()=>utility118,getPropImages:()=>propImages,')
(T/'review119.js').write_text(s,encoding='utf-8')
inputs={'revision':119,'nativeIntegrated':False,'sourceFiles':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in [S,B] for p in folder.iterdir() if p.suffix in ('.js','.json','.html','.css')},'wallFront':[18,31],'mountBounds':[19,30],'backgroundChanged':False,'geometryChanged':False,'floorPropsChanged':False}
(R/'preview/wall-mount119/inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
print('Prepared street119 (1-3F) and market119 (4-7F); previous versions preserved.')
