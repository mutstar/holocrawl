param([string]$Run='ayame-vfx01')
$ErrorActionPreference='Stop'
if($Run -notmatch '^[a-zA-Z0-9_-]+$'){throw 'Use a simple capture run name'}
$root=Split-Path -Parent $PSScriptRoot
$source=Join-Path $root 'engine/tiles-crawl/crawl-ref/source'
$base=Join-Path $root "analysis/native/$Run"
$binary=Join-Path $base 'capture-engine.exe'
$output=Join-Path $base 'native'
$shots=Join-Path $output 'shots'
if(Test-Path -LiteralPath $output){throw 'Capture output exists; preserve it and use a fresh run'}
New-Item -ItemType Directory -Path $shots -Force | Out-Null
$rc=Join-Path $output 'capture.rc'
@('tile_skip_title = true','tile_full_screen = false','tile_window_width = 1152','tile_window_height = 800','tile_cell_pixels = 32','show_more = false') | Set-Content -LiteralPath $rc -Encoding ascii
$keys=@('PATH','HOLOCRAWL_ENGINE_BENCH','HOLOCRAWL_CAMPAIGN_TEST','HOLOCRAWL_CAMPAIGN_OUTPUT','HOLOCRAWL_CAMPAIGN_RELOAD','HOLOCRAWL_VISUAL_CAPTURE','HOLOCRAWL_INVOCATION_CAPTURE','HOLOCRAWL_WORSHIP_TEST','HOLOCRAWL_AKI_REVIEW','HOLOCRAWL_SUISEI_REVIEW','HOLOCRAWL_MIKO_REVIEW','HOLOCRAWL_AKI_REVIEW','HOLOCRAWL_AYAME_REVIEW','HOLOCRAWL_FUBUKI_REVIEW') | Select-Object -Unique
$saved=@{}
foreach($k in $keys){$saved[$k]=[Environment]::GetEnvironmentVariable($k,'Process')}
try {
    foreach($k in $keys){if($k -ne 'PATH'){Remove-Item -LiteralPath ('Env:'+ $k) -ErrorAction SilentlyContinue}}
    $env:PATH="$(Join-Path $root '.toolchain/msys64/mingw64/bin');$env:PATH"
    $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output
    $env:HOLOCRAWL_INVOCATION_CAPTURE=$shots;$env:HOLOCRAWL_AYAME_REVIEW=$shots
    $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output 'stdout.log') -RedirectStandardError (Join-Path $output 'stderr.log') -Wait -PassThru
    if($p.ExitCode){throw "Native capture failed: $($p.ExitCode); see native/stderr.log"}
    $review=Get-Content -LiteralPath (Join-Path $output 'ayame-review.json') -Raw | ConvertFrom-Json
    if($review.status -ne 'passed'){throw 'Ayame phase validation missing'}
    Remove-Item Env:HOLOCRAWL_AYAME_REVIEW,Env:HOLOCRAWL_INVOCATION_CAPTURE -ErrorAction SilentlyContinue
    $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output 'regression.stdout.log') -RedirectStandardError (Join-Path $output 'regression.stderr.log') -Wait -PassThru
    if($p.ExitCode){throw '22-god native regression failed'}
    $v=Get-Content -LiteralPath (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json
    if($v.status -ne 'passed' -or $v.gods -ne 22){throw 'Missing native 22-god validation'}
    $env:HOLOCRAWL_INVOCATION_CAPTURE=$null;$env:HOLOCRAWL_CAMPAIGN_RELOAD='1'
    $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $output 'reload.stdout.log') -RedirectStandardError (Join-Path $output 'reload.stderr.log') -Wait -PassThru
    if($p.ExitCode){throw 'Native capture save reload failed'}
    if((Get-Content -LiteralPath (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Missing reload proof'}
    @{status='passed';scope='Ayame 1/3/5 tier-specific native VFX and delayed impact, plus 22-god power/save regression. Test arena, fixed equipment, boosted fixture resources; not a normal campaign playthrough.';binarySha256=(Get-FileHash -LiteralPath $binary).Hash;rawScreenshots=@(Get-ChildItem -LiteralPath $shots -Filter '*.png').Count;capturePreservesGameplayAndRng=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $base 'capture-validation.json') -Encoding ascii
    Write-Output $shots
} finally {foreach($k in $keys){if($null -eq $saved[$k]){Remove-Item -LiteralPath ('Env:'+ $k) -ErrorAction SilentlyContinue}else{[Environment]::SetEnvironmentVariable($k,$saved[$k],'Process')}}}
