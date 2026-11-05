from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-floor-final01'
out.mkdir(exist_ok=True)
for name in ['app.js','boot.js','terrain.js','grounding.js','native-d1.json','native-d1.js','index.html']:
 shutil.copyfile(root/'preview/city-explore01'/name,out/name)
shutil.copytree(root/'preview/city-explore01/assets',out/'assets',dirs_exist_ok=True)
shutil.copyfile(root/'scripts/final-floor-layout01.js',out/'final-layout.js')
shutil.copyfile(root/'scripts/wall-volume01.js',out/'wall-volume.js')
p=out/'app.js';s=p.read_text(encoding='utf-8');a=s.index('function generate(i){');b=s.index('\nlet player=',a)
s=s[:a]+'function generate(i){return generateFinalFloor(i);}\n'+s[b:]
s=s.replace('holocrawl-city-explore01','holocrawl-city-floor-final01')
s=s.replace(".map(p=>p.x+','+p.y));}\nfunction canWalk", ".concat(fences).map(p=>p.x+','+p.y));}\nfunction canWalk")
s=s.replace('placementSeed,fixtures,visible:', 'placementSeed,fixtures,fences,visible:')
s=s.replace("drawLoot(t);", "for(const p of fences)if(explored[p.y*m.w+p.x])ctx.drawImage(images.fence,p.x*t,p.y*t+t*10/32,t,t*22/32);\ndrawLoot(t);")
s=s.replace("message=floorProps().has(x+','+y)?'진열대나 소품이 놓여 있습니다. 옆으로 돌아가세요.':'벽이 막고 있습니다.';", "message=fences.some(p=>p.x===x&&p.y===y)?'펜스가 막고 있습니다. 옆으로 돌아가세요.':floorProps().has(x+','+y)?'진열대나 소품이 놓여 있습니다. 옆으로 돌아가세요.':'벽이 막고 있습니다.';")
p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 1층 · 직접 탐험','잔향도시 1층 · 최종 배치안').replace('입구에서 출발해서 길과 계단을 찾아보세요.','확정 도트와 벽 장식·두 종류의 상점·셔터·펜스·배송 상자를 배치했습니다. 입구에서 출발해서 길과 계단을 찾아보세요.').replace('<script src="boot.js', '<script src="final-layout.js"></script><script src="boot.js');p.write_text(s,encoding='utf-8')
p.write_text(s.replace('잔향도시 1층 · 최종 배치안','잔향도시 1층 · 확정 벽 탐험').replace('<script src="final-layout.js"></script>', '<script src="final-layout.js?v=trash02"></script><script src="wall-volume.js?v=13"></script>'),encoding='utf-8')
manifest={'date':'2026-11-05','status':'final floor layout candidate for user review','nativeGeometry':'three existing native DCSS0.34.1 D:1 exports; terrain rows unchanged','shops':'one acrylic wall showcase + shirt front; one shirt wall showcase + other goods front','shutters':['closed','half-open'],'crates':[2,3],'rubbish':1,'fence':'one2–3tile short section, does not disconnect map','walls':'approved AC, vent, small cabinet08, opposite-elbow horizontal pipes10 random3–5tiles','stairs':'approved unaltered DCSS original horizontal reflection','saveNamespace':'separate from city-explore01','enemies':False,'nativeIntegration':False}
manifest['trashBagsVisibleSize']=[30,30]
manifest['wallStyle']='user-approved dark upper mass and brown exposed faces for thick and thin walls; local refinement13'
manifest['wallStyleApproved']=True
(out/'layout-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)











