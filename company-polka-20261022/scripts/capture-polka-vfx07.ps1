$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$source=Join-Path $root 'engine/tiles-crawl/crawl-ref/source'
$base=Join-Path $root 'analysis/native/polka-vfx07'
$binary=Join-Path $base 'capture-engine.exe'
$output=Join-Path $base 'native'
$shots=Join-Path $output 'shots'
if(Test-Path -LiteralPath $output){throw 'Preserve previous results; use a fresh capture folder.'}
New-Item -ItemType Directory -Path $shots,(Join-Path $output 'saves') -Force | Out-Null
$rc=Join-Path $output 'capture.rc'
@("save_dir = $($output.Replace('\','/'))/saves",'tile_skip_title = true','tile_full_screen = false','tile_window_width = 1152','tile_window_height = 800','tile_cell_pixels = 32','show_more = false') | Set-Content -LiteralPath $rc -Encoding ascii
$keys=@('PATH')+@(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*' | Select-Object -ExpandProperty Name)
$saved=@{};foreach($k in $keys){$saved[$k]=[Environment]::GetEnvironmentVariable($k,'Process')}
function Run-Capture([string]$argsText,[string]$stem){
 $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),$argsText) -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output "$stem.stdout.log") -RedirectStandardError (Join-Path $output "$stem.stderr.log") -Wait -PassThru
 if($p.ExitCode){throw "Capture $stem failed ($($p.ExitCode)); inspect stderr."}
}
try {
 foreach($v in @(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*')){Remove-Item -LiteralPath ('Env:'+$v.Name)}
 $env:PATH="$(Join-Path $root '.toolchain/msys64/mingw64/bin');$env:PATH"
 Run-Capture '-builddb' 'builddb'

 $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output
 $env:HOLOCRAWL_INVOCATION_CAPTURE=$shots;$env:HOLOCRAWL_NIGHT_REVIEW=$shots;$env:HOLOCRAWL_OKAYU_REVIEW=$shots
 Run-Capture '-test holocrawl-campaign -no-throttle' 'choco'
 Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE,Env:HOLOCRAWL_NIGHT_REVIEW,Env:HOLOCRAWL_OKAYU_REVIEW
 if((Get-Content (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json).gods -ne 22){throw 'Missing 22-god checks.'}
 $env:HOLOCRAWL_CAMPAIGN_RELOAD='1';Run-Capture '-test holocrawl-campaign -no-throttle' 'reload'
 if((Get-Content (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Fresh-process restore failed.'}
 @{status='passed';gods=22;chocoControls=$false;freshProcessRestore=$true;rawScreenshots=@(Get-ChildItem $shots -Filter '*.png').Count;binarySha256=(Get-FileHash $binary).Hash;scope='VFX and native state controls, not campaign winrate.'} | ConvertTo-Json | Set-Content (Join-Path $base 'capture-validation.json') -Encoding ascii
} finally {
 foreach($v in @(Get-ChildItem Env: | Where-Object Name -Like 'HOLOCRAWL_*')){Remove-Item -LiteralPath ('Env:'+$v.Name)}
 foreach($k in $keys){if($null -eq $saved[$k]){Remove-Item -LiteralPath ('Env:'+$k) -ErrorAction SilentlyContinue}else{[Environment]::SetEnvironmentVariable($k,$saved[$k],'Process')}}
}