from pathlib import Path
import subprocess,json,shutil,time
root=Path(__file__).resolve().parents[1];runtime=root/'runtime/base0341';exe=runtime/'HoloCrawl-0341-base.exe'
result={'tag':'0.34.1','checks':[],'nativeHolocrawlIntegrated':False}
def run(name,args,timeout=240):
 start=time.monotonic();p=subprocess.run([str(exe),*args],cwd=runtime,capture_output=True,timeout=timeout)
 output=(p.stdout+p.stderr).decode('utf-8',errors='replace');(root/'analysis'/f'{name}.log').write_text(output,encoding='utf-8')
 item={'name':name,'exitCode':p.returncode,'elapsedSeconds':round(time.monotonic()-start,2),'log':f'analysis/{name}.log'}
 if name=='native-version':item['versionConfirmed']='Crawl version 0.34.1' in output
 result['checks'].append(item);(root/'analysis/base-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(item),flush=True)
 if p.returncode:raise RuntimeError(output[-3000:])
 return output
version=run('native-version',['-version']);assert 'Crawl version 0.34.1' in version
run('native-builddb',['-headless','-dir','.','-rc','init.txt','-builddb'])
# Invoke the unchanged upstream Lua tests in script mode. This baseline build
# has DEBUG asserts but does not enable the extra DEBUG_TESTS C++ harness.
scripts=runtime/'scripts';scripts.mkdir(exist_ok=True)
for name in ['los_maps','los_symm','los_csc']:
 shutil.copy2(runtime/'test'/f'{name}.lua',scripts/f'{name}.lua')
 run(f'native-{name}',['-headless','-dir','.','-rc','init.txt','-script',name])
result['status']='passed';result['losTestInvocation']='Unmodified upstream Lua tests invoked through -script; not C++ diagnostic test harness.'
(root/'analysis/base-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Base engine and three upstream LOS scripts passed.',flush=True)
