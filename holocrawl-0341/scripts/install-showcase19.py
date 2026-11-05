from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];out=root/'preview/city-doors17'
shutil.copyfile(root/'scripts/showcase-joint19.js',out/'showcase-joint.js')
p=out/'index.html';s=p.read_text(encoding='utf-8-sig')
if '<script src="showcase-joint.js' not in s:s=s.replace('<script src="boot.js','<script src="showcase-joint.js?v=20"></script><script src="boot.js')
p.write_text(s,encoding='utf-8');print('Installed wall showcase joins.')

