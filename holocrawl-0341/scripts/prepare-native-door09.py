from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
src=root/'preview/native-layout08'
dst=root/'preview/native-door09'
(dst/'assets').mkdir(parents=True,exist_ok=True)
for name in ['native-maps.js','native-maps.json']:
    shutil.copy2(src/name,dst/name)
print('Prepared door09 with unchanged native terrain snapshots.')
