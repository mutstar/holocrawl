from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];out=root/'preview/city-doors17'
shutil.copyfile(root/'scripts/glass-wall18.js',out/'glass-wall.js')
p=out/'index.html';s=p.read_text(encoding='utf-8-sig')
if '<script src="glass-wall.js' not in s:s=s.replace('<script src="boot.js','<script src="glass-wall.js?v=18"></script><script src="boot.js')
p.write_text(s,encoding='utf-8')
print('Installed dedicated glass wall renderer in current doors17 preview.')
