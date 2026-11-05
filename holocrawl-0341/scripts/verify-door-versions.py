from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
import hashlib,json

root=Path(__file__).resolve().parents[1]
out=root/'analysis/door-version-check'
out.mkdir(parents=True,exist_ok=True)
jobs=[(version,state) for version in ['0.24.0','0.34.1'] for state in ['closed','open']]
def fetch(job):
    version,state=job
    url=f'https://raw.githubusercontent.com/crawl/crawl/{version}/crawl-ref/source/rltiles/dngn/doors/{state}_door.png'
    with urlopen(Request(url,headers={'User-Agent':'HoloCrawl-source-check'}),timeout=25) as response:
        raw=response.read()
    assert raw.startswith(b'\x89PNG\r\n\x1a\n')
    path=out/f'{version}-{state}.png'
    path.write_bytes(raw)
    return {'version':version,'state':state,'source':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'file':path.name}
with ThreadPoolExecutor(max_workers=4) as pool:
    files=list(pool.map(fetch,jobs))
same={state:next(f['sha256'] for f in files if f['version']=='0.24.0' and f['state']==state)==next(f['sha256'] for f in files if f['version']=='0.34.1' and f['state']==state) for state in ['closed','open']}
result={'versions':['0.24.0','0.34.1'],'source':'Official crawl/crawl release tags','identicalFiles':same,'scope':'Default single-cell closed/open door artwork only; does not assert every themed or multi-cell gate sprite is unchanged.','files':files}
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
