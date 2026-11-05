from pathlib import Path
import subprocess,os,json,hashlib
r=Path(__file__).resolve().parents[1];exe=r/'runtime/structure01/HoloCrawl-0341-structure.exe'
env=os.environ.copy();env['PATH']=str(r/'runtime/base0341')+os.pathsep+env.get('PATH','')
out=r/'analysis/structure01';out.mkdir(parents=True,exist_ok=True)
def run(name,args,expected=0):
 p=subprocess.run([str(exe),*args],env=env,cwd=r,capture_output=True,timeout=30)
 text=(p.stdout+p.stderr).decode('utf-8',errors='replace');(out/f'{name}.log').write_text(text,encoding='utf-8')
 if p.returncode!=expected:raise RuntimeError(f'{name}: {p.returncode}: {text}')
 return text
catalog=json.loads(run('catalog',['-holo-structure']))
assert catalog==json.loads((r/'design/gods0341.json').read_text(encoding='utf-8'))
test=json.loads(run('native-tests',['-holo-structure-test']))
assert test['status']=='passed' and test['gods']==22 and test['slots']==110
fixture=out/'native-property-fixture.bin'
written=json.loads(run('fresh-write',['-holo-state-write',str(fixture)]))
restored=json.loads(run('fresh-read',['-holo-state-read',str(fixture)]))
assert written==restored and restored['historyGods']==22 and restored['stars']==3
bad=out/'fixture-with-trailing-bytes.bin';bad.write_bytes(fixture.read_bytes()+b'bad')
run('trailing-data-rejected',['-holo-state-read',str(bad)],1)
result={**test,'catalogMatchesEditableSource':True,'nativePropertySerialization':True,'freshProcessRestore':True,'trailingDataRejected':True,'fixtureSha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'binarySha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'scope':'Structure and native property adapter only; ordinary game worship/altar/menu/full-player-save hooks and combat effects are NOT connected.'}
(out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
