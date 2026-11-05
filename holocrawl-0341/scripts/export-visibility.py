from pathlib import Path
import subprocess,json,os,hashlib
r=Path(__file__).resolve().parents[1];out=r/'preview/street-vision01';out.mkdir(parents=True,exist_ok=True)
analysis=r/'analysis/visibility01';analysis.mkdir(parents=True,exist_ok=True)
exe=r/'runtime/visibility01/HoloCrawl-0341-visibility.exe'
env=os.environ.copy();env['PATH']=str(r/'runtime/base0341')+os.pathsep+env.get('PATH','')
def export(flag):
 p=subprocess.run([str(exe),flag],cwd=r,env=env,capture_output=True,timeout=60)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf-8',errors='replace'))
 return json.loads(p.stdout.decode('utf-8'))
table=export('-holo-los-table');fixtures=export('-holo-los-fixtures')
(out/'visibility-paths.json').write_text(json.dumps(table,separators=(',',':')),encoding='utf-8')
(out/'visibility-paths.js').write_text('globalThis.Crawl0341LOSPaths='+json.dumps(table,separators=(',',':'))+';if(typeof module!=="undefined"&&module.exports)module.exports=globalThis.Crawl0341LOSPaths;\n',encoding='utf-8')
(analysis/'native-fixtures.json').write_text(json.dumps(fixtures),encoding='utf-8')
meta={'engine':'0.34.1','radius':7,'maxRadius':8,'quadrantTargets':len(table['footprints']),'pathVariants':sum(len(t['paths']) for t in table['footprints']),'oracleFixtures':len(fixtures['cases']),'nativeLosSourceSha256':hashlib.sha256((r/'engine/upstream/crawl-ref/source/los.cc').read_bytes()).hexdigest(),'binarySha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'mechanism':'Native find_ray footprint export; fixtures from native losight. Native LOS algorithm unchanged.'}
(analysis/'export.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta))
