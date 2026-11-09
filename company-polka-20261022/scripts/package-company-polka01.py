"""One portable ZIP: current game/source/art/previews and verified handoff."""
from pathlib import Path
import os,json,hashlib,shutil,subprocess,re,zipfile,datetime
r=Path(__file__).resolve().parents[1];name='HOLOCRAWL_COMPANY_2026-10-22_POLKA_REVIEW01';(r/'exports').mkdir(exist_ok=True);stage=r/'exports'/name;archive=r/'exports'/(name+'.zip');proofdir=r/'analysis/native/company-polka-handoff01';stage.mkdir();proofdir.mkdir()
company_readme='# 뭇별 회사 컴퓨터 이어하기 · 2026-10-22\n\nZIP 전체를 새 폴더에 풀고 이 파일부터 읽는다. 예전 프로젝트 위에 덮어쓰지 않는다.\n\n- OPEN_VFX_REVIEW.cmd: 현재 폴카 1·3·5성 검토 화면. 각 공연/대단원 선택지 설명 포함.\n- OPEN_GALLERY.cmd: 22신 통합 미리보기.\n- PLAY_HOLOCRAWL.cmd: 최신 Windows x64 플레이 실행본. 의존 DLL 포함, 컴파일러 없이 실행 가능.\n- VERIFY_HOME.cmd: 압축을 푼 파일들의 해시 검사.\n\n현재 승인 상태\n라미까지 13신의 전체 이펙트 승인. 라미 전투 버전은 lamy-tools05(도구·구름 냉각 지원), 5성 연출은 lamy-banquet-vfx05(격자 없이 옅은 서리 외곽·둥근 모서리).\n폴카는 아직 승인 전이다. polka-review01은 기존 실제 SDL 두 프레임 순간 효과를 선택지별로 모은 검토 페이지이며 새 폴카 도트·공연 완주·도약 전체 시퀀스를 제작한 상태가 아니다.\n다음 작업: 폴카 1성 오늘의 공연, 3성 공중곡예, 5성 불꽃 피날레/커튼콜/대혼란 피드백부터 이어간다. 라미를 다시 미승인으로 돌리거나 다음 신을 자동 진행하지 않는다.\n\n포함: 최신 실행본과 DLL, 현재 두 엔진 소스 체크아웃, 도트·원본·프롬프트, 승인 미리보기와 현재 초안, 스크립트, 검증 요약·패치·인계·최근 체크포인트.\n용량 절감 제외: .toolchain 컴파일러, 오브젝트/빌드 캐시, 과거 중복 실행파일, 대규모 조우 원시 데이터, 기존 플레이 세이브. 원본은 집 작업 폴더에 보존한다.\n재빌드 시 회사의 기존 MSYS2/MINGW64 .toolchain을 재사용해야 한다. 실행·HTML 피드백에는 컴파일러가 필요 없다.\n별도로 설치한 일반 DCSS 0.24의 사운드팩과 그 세이브는 홀로죽 전달본에 포함하지 않았다.\n\n회사에서 이어가기\n회사 대화에 이 ZIP 또는 압축을 푼 폴더를 제공하고 “START_HERE_COMPANY.md와 HOME_SESSION.md부터 읽고 폴카 이펙트 피드백 이어가자”라고 요청한다.\n정확한 소스/미리보기 상태는 VFX_DRAFT_STATUS.json과 HOME_HANDOFF_STATE.json을 확인한다. 문서의 과거 기록이나 예전 전달본 절대경로는 현재 실행 위치로 사용하지 않는다.\n전달 경로에서 22신 기능·새 프로세스 저장 재현 검사와 파일 해시를 확인한다. 캠페인 승률·모든 조건의 이펙트 완성을 검증한 것은 아니다.\n'
assert not archive.exists(),'Preserve existing archive'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(r/'analysis/native/lamy-banquet-vfx05/checkpoint-manifest.json')['status']=='passed'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(p,rel):
 q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def tree(folder,rel,predicate=lambda p:True):
 for cur,dirs,names in os.walk(folder):
  cur=Path(cur);dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','.pytest_cache','saves','morgue','downloads','node_modules'} and not(cur/d).is_symlink()]
  for n in names:
   p=cur/n
   if p.is_file() and predicate(p):copy(p,Path(rel)/p.relative_to(folder))
def source_ok(p):
 if p.suffix.lower() in {'.o','.d','.gch','.exe','.obj','.dll','.log','.zip','.7z','.tar','.xz','.gz','.db'} and p.name!='Makefile.obj':return False
 if p.name in {'.cflags','.lflags','.contrib-libs'}:return False
 if p.suffix=='.a' and 'install' not in p.parts:return False
 return True
for checkout in ['campaign-crawl','tiles-crawl']:
 folder=r/'engine'/checkout/'crawl-ref/source';tree(folder,Path('engine')/checkout/'crawl-ref/source',source_ok)
for folder in ['assets','scripts','analysis/previews','analysis/handoff-history','analysis/checkpoints']:tree(r/folder,folder,lambda p:p.suffix not in {'.pyc','.pyo'})
selected=set('suisei-vfx04 miko-vfx02 aki-vfx05 fubuki-vfx05 ayame-vfx02 choco-vfx02 choco-vfx03 korone-vfx09 okayu-vfx05 okayu-balance03 pekora-vfx02 pekora-balance01 noel-vfx04 noel-vfx05 noel-supply-sequence01 noel-balance01 watame-vfx02 watame-vfx03 towa-vfx03 towa-vfx04 towa-support05 towa-diagonal01 towa-crossfire02 lamy-hud01 lamy-caster01 lamy-chill-vfx01 lamy-tools05 lamy-banquet-vfx03 lamy-banquet-vfx04 lamy-banquet-vfx05 polka-review01'.split())
def evidence_ok(p):
 rel=p.relative_to(r/'analysis/native');parts=rel.parts
 if p.suffix.lower() in {'.exe','.dll','.o','.d','.db','.cs','.lua','.saf','.bones'}:return False
 if p.suffix.lower() in {'.png','.gif','.webp'}:return parts[0] in selected and not any(x.startswith('native-attempt') for x in parts)
 if p.suffix.lower() in {'.jsonl','.csv','.tsv'}:return p.stat().st_size<1024*1024
 return p.stat().st_size<8*1024*1024
tree(r/'analysis/native','analysis/native',evidence_ok)
for p in (r/'analysis').rglob('*.md'):
 if 'previews' not in p.parts:copy(p,p.relative_to(r))
for p in r.iterdir():
 if p.is_file() and p.suffix.lower() in {'.md','.json','.cmd','.ps1'} and p.name not in {'TRANSFER_MANIFEST.json','PORTABLE_VALIDATION.json','RUNTIME_DEPENDENCIES.json'}:copy(p,p.name)
copy(r/'TRANSFER_MANIFEST.json','analysis/handoff-history/original-import-TRANSFER_MANIFEST.json')
for p in (r/'engine').glob('*.json'):copy(p,p.relative_to(r))
copy(r/'runtime/tiles01/HoloCrawl.exe','runtime/tiles01/HoloCrawl.exe')
# Preserve root analysis runners and latest Polka native originals, whose local import omitted full PNGs.
for p in (r/'analysis').glob('*.py'):copy(p,p.relative_to(r))
polka=read(r/'analysis/native/polka-review01/validation.json')
for rel,h in polka['nativeFrameHashesVerified'].items():
 p=r/'analysis/native/night-vfx04'/rel
 if not p.exists():p=r.parent/'HoloCrawl_HOME_2026-10-20/exports/HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT/analysis/native/night-vfx04'/rel
 assert sha(p).lower()==h.lower()
 copy(p,Path('analysis/native/night-vfx04')/rel)
# Resolve every non-Windows PE import against this build's own compiler runtime.
bin_dir=r/'.toolchain/msys64/mingw64/bin';dlls={p.name.lower():p for p in bin_dir.glob('*.dll')};deps=stage/'runtime/deps';deps.mkdir();pending=[stage/'runtime/tiles01/HoloCrawl.exe'];done=set();system=[]
while pending:
 p=pending.pop();result=subprocess.run([str(bin_dir/'objdump.exe'),'-p',str(p)],capture_output=True,text=True,check=True)
 for dll in re.findall(r'DLL Name:\s*(\S+)',result.stdout):
  key=dll.lower()
  if key in done:continue
  done.add(key)
  if key in dlls:copy(dlls[key],Path('runtime/deps')/dlls[key].name);pending.append(deps/dlls[key].name)
  else:
   assert (Path(os.environ.get('WINDIR','C:/Windows'))/'System32'/dll).exists() or key.startswith(('api-ms-win-','ext-ms-win-')),dll
   system.append(dll)
write(stage/'RUNTIME_DEPENDENCIES.json',dict(bundled=[p.name for p in deps.glob('*.dll')],windowsSystem=system,compilerBundled=False,rebuild='Reuse existing home MSYS2/MINGW64 .toolchain; source and contrib install libraries included.'))
# Launchers are relative to the new extraction directory.
for n in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:(stage/n).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\polka-review01\\index.html"\r\n',encoding='ascii')
(stage/'VERIFY_HOME.cmd').write_text('@echo off\r\ncd /d "%~dp0"\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0VERIFY_TRANSFER.ps1"\r\nif errorlevel 1 pause\r\n',encoding='ascii')
copy(r/'scripts/start-portable-vfx.ps1','scripts/start-portable-vfx.ps1')
(stage/'START_HERE_COMPANY.md').write_text(company_readme,encoding='utf-8')
(stage/'README_FIRST.md').write_text(company_readme,encoding='utf-8')
(stage/'OPEN_VFX_REVIEW.cmd').write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\polka-review01\\index.html"\r\n',encoding='ascii')
(stage/'OPEN_GALLERY.cmd').write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\all-gods-vfx-draft04\\index.html"\r\n',encoding='ascii')
(stage/'START_HERE_CAMPAIGN.md').write_text('# Current entry\n\nUse START_HERE_HOME.md and PLAY_HOLOCRAWL.cmd.\n',encoding='utf-8')
print('Stage copied. Running relocated game using bundled DLLs only...',flush=True)
result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(stage/'scripts/start-portable-vfx.ps1'),'-SmokeTest'],capture_output=True,text=True)
(proofdir/'launcher.stdout.log').write_text(result.stdout,encoding='utf-8');(proofdir/'launcher.stderr.log').write_text(result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
smoke=stage/'runtime/portable-smoke03';assert read(smoke/'validation.json')['gods']==22 and read(smoke/'reload.json')['status']=='passed' and read(smoke/'lamy-caster.json')['status']=='passed'
write(stage/'PORTABLE_VALIDATION.json',dict(status='passed',bundledDependenciesOnly=True,relocatedNativeGame=True,gods=22,freshProcessReload=True,lamyCaster=read(smoke/'lamy-caster.json'),binarySha256=sha(stage/'runtime/tiles01/HoloCrawl.exe')))
# Every referenced local preview image must be present in the transfer.
gallery=stage/'analysis/previews/all-gods-vfx-draft04/index.html';html=gallery.read_text(encoding='utf-8');data=json.loads(re.search(r'const data=(.*?);function choose',html).group(1));images=[gallery.parent/entry['image'] for entries in data.values() for entry in entries];assert all(p.is_file() for p in images)
write(stage/'PREVIEW_LINK_VALIDATION.json',dict(status='passed',gods=len(data),images=len(images),currentGod='polka',currentTier=1,allImagesPresent=True))
# Generated caches and fixture saves are not part of the portable source snapshot.
def transfer_file(p):
 rel=p.relative_to(stage);parts=rel.parts
 if 'saves' in parts or 'morgue' in parts:return False
 if p.suffix.lower() in {'.db','.o','.d','.pyc'}:return False
 return True
# The Polka review and all referenced choices must survive relocation.
review=stage/'analysis/previews/polka-review01';pr=read(review/'provenance.json')
for e in pr['entries']:
 assert (review/e['image']).is_file() and sha(review/e['image']).lower()==e['sha256'].lower()
assert read(stage/'VFX_DRAFT_STATUS.json')['tierApprovals']['lamy']['approved']==[1,3,5]
files=sorted(p for p in stage.rglob('*') if p.is_file() and transfer_file(p));entries=[dict(path=p.relative_to(stage).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
write(stage/'TRANSFER_MANIFEST.json',dict(version='company-polka-review01',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),entry='START_HERE_COMPANY.md',source='engine/campaign-crawl/crawl-ref/source',review='analysis/previews/all-gods-vfx-draft04/index.html',next='Polka tiers1/3/5 feedback pending; Lamy fully approved',files=entries,excluded='Compiler junction, objects/caches, duplicate historical EXEs, large encounter raw datasets and test saves; originals retained in company workspace.'))
files.append(stage/'TRANSFER_MANIFEST.json');print(f'Packing {len(files)} files, {sum(p.stat().st_size for p in files)/1024**2:.1f} MiB...',flush=True)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for p in files:z.write(p,name+'/'+p.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(entries)+1
 for e in entries:
  h=hashlib.sha256()
  with z.open(name+'/'+e['path']) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest().upper()==e['sha256'],e['path']
proof=dict(status='passed',archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),files=len(files),allArchivedHashesVerified=True,crcVerified=True,relocatedNativeSmokePassed=True,previewImagesVerified=len(images))
write(proofdir/'transfer-validation.json',proof);print(json.dumps(proof,ensure_ascii=False,indent=2),flush=True)
