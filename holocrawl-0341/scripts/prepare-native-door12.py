from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1];src=root/'preview/native-door11';dst=root/'preview/native-door12';dst.mkdir(exist_ok=True)
for name in ['native-maps.js','native-maps.json','app.js','style.css','wall-material-manifest.json','wall-processing.json']:
    shutil.copy2(src/name,dst/name)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
for state in ['closed','open']:
    shutil.copy2(src/f'assets/fire-door-{state}32.png',dst/f'assets/previous-fire-door-{state}32.png')
css=(dst/'style.css').read_text(encoding='utf-8')+'\n.comparisons{grid-template-columns:1fr 1fr;max-width:760px}.comparisons article:nth-child(2){border-color:#a9c494}.comparisons article:nth-child(3){border-color:#526b60}@media(max-width:720px){.comparisons{grid-template-columns:1fr}}\n'
(dst/'style.css').write_text(css,encoding='utf-8')
print('Prepared door12, preserved all previous door versions.')
