from pathlib import Path
import hashlib,json,os,subprocess

root=Path(__file__).resolve().parents[1];runtime=root/'runtime/street01';out=root/'analysis/street01';out.mkdir(parents=True,exist_ok=True)
node='C:/Program Files/nodejs/node.exe'
exe=runtime/'HoloCrawl-0341-street.exe'
env=os.environ.copy();env['PATH']=str(runtime)+os.pathsep+env['PATH']
process=subprocess.run([str(exe),'-headless','-dir','.', '-rc','init.txt','-builddb'],cwd=runtime,env=env,capture_output=True,timeout=180)
(out/'builddb.log').write_text((process.stdout+process.stderr).decode('utf-8',errors='replace'),encoding='utf-8')
assert process.returncode==0,'Street map database build failed; see builddb.log'
results=[]
for seed in ['CITY-NATIVE-001','CITY-NATIVE-002','CITY-NATIVE-003','CITY-NATIVE-004','CITY-NATIVE-005']:
    target=out/(seed+'.hcmap')
    subprocess.run([node,str(root/'scripts/export-street-map.cjs'),seed,str(target)],cwd=root,check=True,capture_output=True)
    env['HOLOCRAWL_STREET01_MAP']=str(target)
    process=subprocess.run([str(exe),'-headless','-dir','.', '-rc','init.txt','-script','holo_street_native'],cwd=runtime,env=env,capture_output=True,timeout=90)
    log=(process.stdout+process.stderr).decode('utf-8',errors='replace');(out/(seed+'.log')).write_text(log,encoding='utf-8')
    assert process.returncode==0,log[-4000:]
    result=next(json.loads(line)for line in log.splitlines()if line.startswith('{"status":'))
    assert result['status']=='passed' and result['terrainCells']==5600
    result['seed']=seed;results.append(result)
    print(seed+': native terrain/collision/opacity/tiles passed',flush=True)
# Refuse an invalid import rather than silently making an ordinary Crawl floor.
bad=out/'invalid.hcmap';text=(out/'CITY-NATIVE-001.hcmap').read_text(encoding='utf-8');bad.write_text(text.replace('80 70','79 70',1),encoding='utf-8')
env['HOLOCRAWL_STREET01_MAP']=str(bad)
process=subprocess.run([str(exe),'-headless','-dir','.', '-rc','init.txt','-script','holo_street_native'],cwd=runtime,env=env,capture_output=True,timeout=90)
assert process.returncode!=0,'Invalid map import was accepted'
result=dict(status='passed',nativeMaps=results,nativeTerrainCellsChecked=sum(r['terrainCells']for r in results),invalidDimensionsRejected=True,
            binarySha256=hashlib.sha256(exe.read_bytes()).hexdigest(),scope='Native imported D:1 prototype; not multi-floor campaign.',floorTravelImplemented=False)
(out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Native street validation passed.',flush=True)
