param([string]$Run='ayame-zanshin01')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$source=Join-Path $root 'engine/tiles-crawl/crawl-ref/source'
$base=Join-Path $root "analysis/native/$Run"
$binary=Join-Path $base 'capture-engine.exe'
$output=Join-Path $base 'native'
if(Test-Path $output){throw 'Preserve previous results; use fresh run.'}
$shots=Join-Path $output 'shots';$feature=Join-Path $output 'ayame'
New-Item -ItemType Directory -Path $shots,(Join-Path $feature 'ayame-save') -Force | Out-Null
$rc=Join-Path $output 'capture.rc'
@('tile_skip_title = true','tile_full_screen = false','tile_window_width = 1152','tile_window_height = 800','tile_cell_pixels = 32','show_more = false') | Set-Content $rc -Encoding ascii
$keys=@('PATH')+@(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*' | Select-Object -ExpandProperty Name)
$saved=@{};foreach($k in $keys){$saved[$k]=[Environment]::GetEnvironmentVariable($k,'Process')}
function Run-Native([string]$stem){
 $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output "$stem.stdout.log") -RedirectStandardError (Join-Path $output "$stem.stderr.log") -Wait -PassThru
 if($p.ExitCode){throw "Native $stem failed ($($p.ExitCode))"}
}
try {
 foreach($v in @(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*')){Remove-Item -LiteralPath ('Env:'+$v.Name)}
 $env:PATH="$(Join-Path $root '.toolchain/msys64/mingw64/bin');$env:PATH"
 $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_OUTPUT=$feature;$env:HOLOCRAWL_AYAME_ZANSHIN_REVIEW=$shots
 Run-Native 'ayame'
 Remove-Item Env:HOLOCRAWL_AYAME_ZANSHIN_REVIEW
 $env:HOLOCRAWL_AYAME_ZANSHIN_RELOAD='1';Run-Native 'ayame-reload';Remove-Item Env:HOLOCRAWL_AYAME_ZANSHIN_RELOAD
 $env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output;Run-Native 'regression'
 $env:HOLOCRAWL_CAMPAIGN_RELOAD='1';Run-Native 'regression-reload';Remove-Item Env:HOLOCRAWL_CAMPAIGN_RELOAD
 $p=Get-Content (Join-Path $feature 'ayame-zanshin.json') -Raw | ConvertFrom-Json
 $q=Get-Content (Join-Path $feature 'ayame-reload.json') -Raw | ConvertFrom-Json
 $v=Get-Content (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json
 $z=Get-Content (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json
 if($p.status -ne 'passed' -or $q.status -ne 'passed' -or $v.gods -ne 22 -or $z.status -ne 'passed'){throw 'Native proofs incomplete'}
 @{status='passed';gods=22;combatImplemented=$true;freshZanshinRestore=$true;binarySha256=(Get-FileHash $binary).Hash} | ConvertTo-Json | Set-Content (Join-Path $base 'capture-validation.json') -Encoding ascii
} finally {
 foreach($v in @(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*')){Remove-Item -LiteralPath ('Env:'+$v.Name)}
 foreach($k in $keys){if($null -eq $saved[$k]){Remove-Item -LiteralPath ('Env:'+$k) -ErrorAction SilentlyContinue}else{[Environment]::SetEnvironmentVariable($k,$saved[$k],'Process')}}
}
