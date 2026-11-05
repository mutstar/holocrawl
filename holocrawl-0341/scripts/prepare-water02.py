from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];src=root/'preview/native-water01';dst=root/'preview/native-water02';dst.mkdir(exist_ok=True)
for name in ['app.js','index.html','style.css','native-maps.js','native-maps.json','art-manifest.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
app=(dst/'app.js').read_text(encoding='utf-8').replace('c.globalAlpha=deep?1:.62','c.globalAlpha=deep?1:.90')
(dst/'app.js').write_text(app,encoding='utf-8')
html=(dst/'index.html').read_text(encoding='utf-8').replace('얕은 물과 잠긴 수로','물빛과 파문이 보이는 얕은 물').replace('얕은 물은 시멘트 바닥이 비치고, 깊은 물은 짙은 청록색으로 보입니다. 물가와 깊이 경계를 함께 확인해 보세요.','얕은 물의 회색 바닥 무늬를 줄이고 청록색 물빛과 짧은 반사 물결을 살렸습니다. 깊은 물 표면은 이전 버전을 유지했습니다.').replace('app.js?v=water01','app.js?v=water02')
(dst/'index.html').write_text(html,encoding='utf-8')
script=(root/'scripts/install-check-water01.cjs').read_text(encoding='utf-8').replace('native-water01','native-water02').replace("for(const state of ['shallow','deep'])","for(const state of ['shallow'])")
script=script.replace("const b=await chromium.launch", "assert.deepStrictEqual(fs.readFileSync(path.join(out,'assets/water-deep128.png')),fs.readFileSync(path.join(out,'../native-water01/assets/water-deep128.png')));const b=await chromium.launch")
script=script.replace('approvedDoor12Unchanged:true,','approvedDoor12Unchanged:true,deepSurfaceUnchanged:true,')
(root/'scripts/install-check-water02.cjs').write_text(script,encoding='utf-8')
print('Prepared shallow-water02; deep water and door12 preserved.')
