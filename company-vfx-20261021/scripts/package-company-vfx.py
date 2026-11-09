"""Portable playable/source/art/review transfer; no compiler or simulation dumps."""
from pathlib import Path
import os,sys,json,hashlib,shutil,subprocess,re,zipfile,datetime
root=Path(__file__).resolve().parents[1];name='HOLOCRAWL_COMPANY_2026-10-21_VFX_DRAFT';exports=root/'exports';exports.mkdir(exist_ok=True);stage=exports/name;archive=exports/(name+'.zip')
assert not stage.exists() and not archive.exists(),'Preserve existing transfer outputs'
proof=json.loads((root/'analysis/native/night-vfx04/gallery-validation.json').read_text(encoding='utf-8'));assert proof['status']=='passed' and proof['abilityTiers']==66
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(p,rel):
    q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def copy_tree(folder,rel,predicate=lambda p:True):
    for cur,dirs,names in os.walk(folder):
        cur=Path(cur);dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','.pytest_cache','saves','morgue','downloads'} and not(cur/d).is_symlink()]
        for n in names:
            p=cur/n
            if p.is_file() and predicate(p):copy(p,Path(rel)/p.relative_to(folder))
stage.mkdir()
# Both source checkouts remain editable/rebuildable with the company's existing toolchain.
def source_ok(p):
    if p.suffix.lower() in {'.o','.d','.gch','.exe','.obj','.dll','.log','.zip','.7z','.tar','.xz','.gz','.db'} and p.name!='Makefile.obj':return False
    if p.name in {'.cflags','.lflags','.contrib-libs'}:return False
    if p.suffix=='.a' and 'install' not in p.parts:return False
    return True
for checkout in ['campaign-crawl','tiles-crawl']:
    p=root/'engine'/checkout/'crawl-ref/source';copy_tree(p,Path('engine')/checkout/'crawl-ref/source',source_ok)
copy(root/'runtime/tiles01/HoloCrawl.exe','runtime/tiles01/HoloCrawl.exe')
copy_tree(root/'assets','assets');copy_tree(root/'scripts','scripts',lambda p:p.suffix not in {'.pyc','.pyo'})
# All visual review pages, including previously approved sequences, stay linked.
copy_tree(root/'analysis/previews','analysis/previews')
selected_runs=['suisei-vfx04','miko-vfx02','aki-vfx05','fubuki-vfx05','ayame-vfx02','choco-vfx01','night-vfx01','night-vfx02','night-vfx03','night-vfx04']
for n in selected_runs:
    p=root/'analysis/native'/n
    if p.exists():copy_tree(p,Path('analysis/native')/n,lambda p:p.suffix.lower() not in {'.exe','.o','.d'} and 'before' not in p.relative_to(root/'analysis/native'/n).parts)
# Preserve final balance/worship/wrath reports, while large per-encounter files remain at home.
for p in (root/'analysis').rglob('*.md'):
    if 'previews' not in p.parts:copy(p,p.relative_to(root))
for p in root.iterdir():
    if p.is_file() and p.suffix.lower() in {'.md','.json','.cmd'} and p.name not in {'HOME_HANDOFF_MANIFEST.json','COMPANY_CHECKPOINT_MANIFEST.json','CHECKPOINT_MANIFEST.json'}:copy(p,p.name)
for p in (root/'engine').glob('*.json'):copy(p,p.relative_to(root))
# Recursively resolve non-system PE imports into a small runtime DLL folder.
bin_dir=root/'.toolchain/msys64/mingw64/bin';objdump=bin_dir/'objdump.exe';deps=stage/'runtime/deps';deps.mkdir(parents=True)
pending=[stage/'runtime/tiles01/HoloCrawl.exe'];done=set();system=[]
while pending:
    p=pending.pop();out=subprocess.run([str(objdump),'-p',str(p)],capture_output=True,text=True,check=True).stdout
    for dll in re.findall(r'DLL Name:\s*(\S+)',out):
        key=dll.lower()
        if key in done:continue
        done.add(key);candidate=bin_dir/dll
        if not candidate.exists():candidate=next((q for q in bin_dir.glob('*.dll') if q.name.lower()==key),candidate)
        if candidate.exists():copy(candidate,Path('runtime/deps')/candidate.name);pending.append(deps/candidate.name)
        else:
            assert (Path(os.environ.get('WINDIR','C:/Windows'))/'System32'/dll).exists() or key.startswith(('api-ms-win-','ext-ms-win-')),dll
            system.append(dll)
write(stage/'RUNTIME_DEPENDENCIES.json',{'bundled':[p.name for p in deps.glob('*.dll')],'windowsSystem':system,'compilerBundled':False,'rebuild':'Reuse existing MSYS2/MINGW64 .toolchain folder; static source contrib install libraries are retained.'})
# Fresh launch settings are relative to this extraction, never the home PC.
launcher=r'''param([switch]$SmokeTest)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$binary=Join-Path $root 'runtime/tiles01/HoloCrawl.exe'
$source=Join-Path $root 'engine/tiles-crawl/crawl-ref/source'
$env:PATH="$(Join-Path $root 'runtime/deps');$env:WINDIR\System32;$env:WINDIR"
foreach($entry in @(Get-ChildItem Env: | Where-Object {$_.Name -like 'HOLOCRAWL_*'})){Remove-Item -LiteralPath ('Env:'+$entry.Name)}
$save=Join-Path $root 'runtime/campaign01/saves';$morgue=Join-Path $root 'runtime/campaign01/morgue'
New-Item -ItemType Directory $save,$morgue -Force | Out-Null
$rc=Join-Path $root 'runtime/campaign01/tiles.rc'
$lines=@("save_dir = $($save.Replace([char]92,[char]47))","morgue_dir = $($morgue.Replace([char]92,[char]47))",'tile_skip_title = true','tile_full_screen = false','tile_cell_pixels = 48','tile_filter_scaling = false','show_more = false')
[IO.File]::WriteAllLines($rc,$lines,(New-Object System.Text.UTF8Encoding($false)))
$db=Start-Process $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-builddb') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $root 'runtime/db-build03.stdout.log') -RedirectStandardError (Join-Path $root 'runtime/db-build03.stderr.log') -Wait -PassThru
if($db.ExitCode){throw "Database build failed: $($db.ExitCode)"}
if($SmokeTest){
    $output=Join-Path $root 'runtime/portable-smoke03';New-Item -ItemType Directory $output -Force | Out-Null
    $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output
    foreach($phase in @('base','reload')){
        if($phase -eq 'reload'){$env:HOLOCRAWL_CAMPAIGN_RELOAD='1'}
        $p=Start-Process $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output "$phase.stdout.log") -RedirectStandardError (Join-Path $output "$phase.stderr.log") -Wait -PassThru
        if($p.ExitCode){throw "Portable $phase failed: $($p.ExitCode)"}
    }
    if((Get-Content (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Portable validation missing'}
    if((Get-Content (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Portable reload missing'}
    return
}
$game=Start-Process $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc)) -WorkingDirectory $source -WindowStyle Normal -Wait -PassThru
if($game.ExitCode){throw "Game exited: $($game.ExitCode)"}
'''
(stage/'scripts/start-portable-vfx.ps1').write_text(launcher,encoding='utf-8-sig')
(stage/'PLAY_HOLOCRAWL.cmd').write_text('@echo off\r\ncd /d "%~dp0"\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\\start-portable-vfx.ps1"\r\nif errorlevel 1 pause\r\n',encoding='ascii')
(stage/'OPEN_VFX_REVIEW.cmd').write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\all-gods-vfx-draft04\\index.html"\r\n',encoding='ascii')
(stage/'OPEN_GALLERY.cmd').write_bytes((stage/'OPEN_VFX_REVIEW.cmd').read_bytes())
(stage/'VERIFY_TRANSFER.ps1').write_text('''$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$m=Get-Content (Join-Path $root 'TRANSFER_MANIFEST.json') -Raw | ConvertFrom-Json
foreach($e in $m.files){$p=Join-Path $root $e.path;if(-not(Test-Path -LiteralPath $p)){throw "Missing $($e.path)"};if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $e.sha256){throw "Mismatch $($e.path)"}}
Write-Host "Transfer files verified: $($m.files.Count)"
''',encoding='utf-8-sig')
readme='''# 뭇별 회사 컴퓨터 이어하기 · 2026-10-21

1. ZIP 전체를 새 폴더에 푼다. 예전 프로젝트 위에 덮어쓰지 않는다.
2. OPEN_VFX_REVIEW.cmd:22신 이펙트 통합 미리보기. 권능 선택으로1·3·5성/선택 분기를 비교한다.
3. PLAY_HOLOCRAWL.cmd: 수정 실행본 플레이. Windows x64용 의존 DLL 포함. 첫 실행은 데이터베이스를 만든다.
4. 피드백은 VFX_COMPANY_FEEDBACK.md 또는 통합 페이지에 적고 JSON 저장 버튼으로 보관한다.
5. 회사 대화에 이 폴더 또는ZIP을 제공하고 “START_HERE_COMPANY.md부터 읽고 이어가자”라고 요청한다.

승인 유지: 스이세이·미코·아키·후부키·아야메. 초코는1성 타일 내부 우측 모서리 수정안(위 칸 몬스터 픽셀 대조 통과). 나머지16신은 전용 모티프/단계별 강조를 적용한 초안이며 아직 사용자 승인 전이다. 모티프 기반1차안이라 방향별 투사체/모든 반응/순차 소환 등의 세부 연출은 신별 한계에 적었다.

실제 고정 전투장 캡처와22신 권능·저장·새 프로세스 재로드·회사 전달 경로에서의 실행을 검사했다. 선택형 캡처에는 박수3·채색3·추가 적 배치·시약 준비 등의 명시된 검사 조건을 쓴다. 캠페인 클리어율/자연 신앙 수급 전체/모든 조건의 이펙트 완성 검증은 아니다. 전투 수치 변경 없음.

포함: 최신 플레이 실행본, 최소 런타임 DLL, 현재 소스2개 체크아웃, 도트 원본·프롬프트, 수정 스크립트, 승인 미리보기와 새 초안, 주요 검증·보고서·인계. 폴더 내 파일 검사는 VERIFY_TRANSFER.ps1.

용량 절감 제외: 컴파일러 전체(.toolchain), 오브젝트/빌드 캐시, 중복 과거 실행본, 과거 대규모 조우 JSONL 원시 데이터. 원본은 집 작업 폴더에 보존한다. 재빌드에는 회사의 기존 MSYS2/MINGW64 .toolchain을 이 프로젝트에 재사용하거나 별도 설치해야 한다. 실행과 HTML 피드백에는 컴파일러가 필요 없다. 음악·나머지 몬스터/플레이어 전체 스프라이트 제작은 이번 신 권능 이펙트 초안 작업 범위가 아니다.

현재 버전: wrath02 전투 기반 / night-vfx04 시각 초안. 기존 세이브는 이 전달본에 포함하지 않는다. 기존 세이브를 옮길 때는 별도 백업한다.
'''
(stage/'START_HERE_COMPANY.md').write_text(readme,encoding='utf-8')
(stage/'README_FIRST.md').write_text(readme,encoding='utf-8')
print('Portable stage ready; running native smoke test with only bundled DLLs and Windows PATH...',flush=True)
result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(stage/'scripts/start-portable-vfx.ps1'),'-SmokeTest'],capture_output=True,text=True)
(stage/'runtime/portable-smoke/launcher.stdout.log').write_text(result.stdout,encoding='utf-8');(stage/'runtime/portable-smoke/launcher.stderr.log').write_text(result.stderr,encoding='utf-8')
assert result.returncode==0,result.stderr
write(stage/'PORTABLE_VALIDATION.json',{'status':'passed','path':str(stage),'bundledDependenciesOnly':True,'gods':22,'freshProcessReload':True,'binarySha256':sha(stage/'runtime/tiles01/HoloCrawl.exe')})
files=[p for p in stage.rglob('*') if p.is_file()];entries=[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p).upper()} for p in sorted(files)]
manifest={'version':'company-vfx-draft04','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry':'START_HERE_COMPANY.md','review':'analysis/previews/all-gods-vfx-draft04/index.html','files':entries,'excludes':'Compiler/cache, duplicate binaries, old per-encounter simulation JSONL; preserved in home workspace.'}
write(stage/'TRANSFER_MANIFEST.json',manifest)
print(f'ZIP: {len(entries)} files, {sum(e["bytes"] for e in entries)/1024**2:.1f} MiB uncompressed',flush=True)
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
    for p in sorted(stage.rglob('*')):
        if p.is_file():z.write(p,name+'/'+p.relative_to(stage).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))==len(entries)+1
    for e in entries:
        h=hashlib.sha256()
        with z.open(name+'/'+e['path']) as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        assert h.hexdigest().upper()==e['sha256'],e['path']
proof={'status':'passed','archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(entries),'allArchivedHashesVerified':True,'crcVerified':True,'relocatedNativeSmokePassed':True}
write(root/'analysis/native/night-vfx04/transfer-validation.json',proof)
print(json.dumps(proof,indent=2),flush=True)
