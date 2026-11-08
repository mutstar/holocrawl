"""Run native107 generation/runtime suites with logs and independent output dirs."""
from pathlib import Path
import argparse,subprocess,os,json,hashlib,time
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'analysis/native-play107-01';S=RUN/'engine/crawl-ref/source'
p=argparse.ArgumentParser();p.add_argument('mode',choices=['smoke','suite']);p.add_argument('--attempt',default='01');a=p.parse_args()
target=RUN/f'{a.mode}-{a.attempt}';target.mkdir(exist_ok=False)
rc=target/'test-init.txt';rc.write_text(f'save_dir = {(target/"saves").as_posix()}/\nmorgue_dir = {(target/"morgue").as_posix()}/\n')
env=os.environ.copy();env['HOLOCRAWL_CITY77']='1';env['PATH']=str(S)+os.pathsep+env.get('PATH','')
for key in ['HOLOCRAWL_CITY_REVIEW_SEED','HOLOCRAWL_STREET01_MAP','HOLOCRAWL_CITY_FACILITY_REVIEW94','HOLOCRAWL_FACILITY107','HOLOCRAWL_SEED107']:env.pop(key,None)
def run(out,extra):
    out.mkdir(exist_ok=False);e={**env,**extra};started=time.monotonic()
    with (out/'native.log').open('wb') as log:r=subprocess.run([str(S/'crawl.exe'),'-headless','-dir',str(S),'-rc',str(rc),'-script','holo_city77',out.as_posix()],cwd=S,env=e,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    (out/'exit.json').write_text(json.dumps({'returncode':r.returncode,'seconds':round(time.monotonic()-started,3)},indent=2)+'\n')
    if r.returncode:raise RuntimeError(f'Native command failed: {out}, code{r.returncode}; retained log')
    v=json.loads((out/'validation.json').read_text());assert v['status']=='passed'
    for f in out.glob('probe-*.json'):assert json.loads(f.read_text())['status']=='passed'
    print('Native completed:',out.name,flush=True)
with (target/'builddb.log').open('wb') as log:
    result=subprocess.run([str(S/'crawl.exe'),'-headless','-dir',str(S),'-rc',str(rc),'-builddb'],cwd=S,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
assert result.returncode==0,'Map database failed; log preserved'
if a.mode=='smoke':run(target/'forced-mountain',{'HOLOCRAWL_FACILITY107':'mountain','HOLOCRAWL_SEED107':'10787001'})
else:
    plan=json.loads((RUN/'plan.json').read_text())
    run(target/'random168',{})
    for id,seed in zip(plan['forcedFacilities'],plan['forcedSeeds']):run(target/f'forced-{id}',{'HOLOCRAWL_FACILITY107':id,'HOLOCRAWL_SEED107':str(seed)})
    assert len(list((target/'random168').glob('map-*.json')))==168
    assert len(list(target.glob('forced-*/map-*.json')))==9
    (target/'generation-validation.json').write_text(json.dumps({'status':'passed','randomFloors':168,'forcedFloors':9,
      'totalFloors':177,'binarySha256':hashlib.sha256((S/'crawl.exe').read_bytes()).hexdigest(),'forcedSamplesAreFrequencyTests':False},indent=2)+'\n')
print('Native107 '+a.mode+' complete.',flush=True)
