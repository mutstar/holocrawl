param([string]$Run='night-vfx01')
$ErrorActionPreference='Stop'
if($Run -notmatch '^[a-zA-Z0-9_-]+$'){throw 'Use a simple run name'}
$root=Split-Path -Parent $PSScriptRoot
$source=Join-Path $root 'engine/tiles-crawl/crawl-ref/source'
$base=Join-Path $root "analysis/native/$Run"
$binary=Join-Path $base 'capture-engine.exe'
$keys=@('PATH','HOLOCRAWL_ENGINE_BENCH','HOLOCRAWL_CAMPAIGN_TEST','HOLOCRAWL_CAMPAIGN_OUTPUT','HOLOCRAWL_CAMPAIGN_RELOAD','HOLOCRAWL_VISUAL_CAPTURE','HOLOCRAWL_INVOCATION_CAPTURE','HOLOCRAWL_WORSHIP_TEST','HOLOCRAWL_SUISEI_REVIEW','HOLOCRAWL_MIKO_REVIEW','HOLOCRAWL_AKI_REVIEW','HOLOCRAWL_FUBUKI_REVIEW','HOLOCRAWL_AYAME_REVIEW','HOLOCRAWL_CHOCO_REVIEW','HOLOCRAWL_NIGHT_REVIEW')
$saved=@{};foreach($k in $keys){$saved[$k]=[Environment]::GetEnvironmentVariable($k,'Process')}
function Run-Native([string]$Output,[string]$Stem){
    $env:HOLOCRAWL_CAMPAIGN_OUTPUT=$Output
    $rc=Join-Path $Output 'capture.rc'
    if(-not(Test-Path $rc)){@('tile_skip_title = true','tile_full_screen = false','tile_window_width = 1152','tile_window_height = 800','tile_cell_pixels = 32','show_more = false') | Set-Content $rc -Encoding ascii}
    $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),'-test holocrawl-campaign -no-throttle') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $Output "$Stem.stdout.log") -RedirectStandardError (Join-Path $Output "$Stem.stderr.log") -Wait -PassThru
    if($p.ExitCode){throw "Native $Stem failed: $($p.ExitCode)"}
}
try {
    foreach($k in $keys){if($k -ne 'PATH'){Remove-Item -LiteralPath ('Env:'+$k) -ErrorAction SilentlyContinue}}
    $env:PATH="$(Join-Path $root '.toolchain/msys64/mingw64/bin');$env:PATH"
    $env:HOLOCRAWL_CAMPAIGN_TEST='1'
    $all=Join-Path $base 'native';$choco=Join-Path $base 'native-choco'
    if((Test-Path $all) -or (Test-Path $choco)){throw 'Preserve existing outputs; choose fresh run'}
    New-Item -ItemType Directory (Join-Path $all 'shots'),(Join-Path $choco 'shots') -Force | Out-Null
    $env:HOLOCRAWL_INVOCATION_CAPTURE=Join-Path $all 'shots';$env:HOLOCRAWL_NIGHT_REVIEW=$env:HOLOCRAWL_INVOCATION_CAPTURE
    Run-Native $all 'all-gods'
    $v=Get-Content (Join-Path $all 'validation.json') -Raw | ConvertFrom-Json
    if($v.status -ne 'passed' -or $v.gods -ne 22){throw 'Missing22-god native validation'}
    Remove-Item Env:HOLOCRAWL_INVOCATION_CAPTURE,Env:HOLOCRAWL_NIGHT_REVIEW -ErrorAction SilentlyContinue
    $env:HOLOCRAWL_CAMPAIGN_RELOAD='1';Run-Native $all 'reload'
    if((Get-Content (Join-Path $all 'reload.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Reload mismatch'}
    Remove-Item Env:HOLOCRAWL_CAMPAIGN_RELOAD -ErrorAction SilentlyContinue
    $env:HOLOCRAWL_INVOCATION_CAPTURE=Join-Path $choco 'shots';$env:HOLOCRAWL_CHOCO_REVIEW=$env:HOLOCRAWL_INVOCATION_CAPTURE
    Run-Native $choco 'choco-corner'
    if((Get-Content (Join-Path $choco 'choco-review.json') -Raw | ConvertFrom-Json).status -ne 'passed'){throw 'Choco control failed'}
    @{status='passed';gods=22;nativeValidation='native/validation.json';reload='native/reload.json';choco='native-choco/choco-review.json';binarySha256=(Get-FileHash $binary).Hash;rawScreenshots=@(Get-ChildItem $base -Recurse -Filter '*.png').Count;scope='Native fixed test arena, existing boosted fixtures; VFX drafts and regression, not campaign win rates'} | ConvertTo-Json | Set-Content (Join-Path $base 'capture-validation.json') -Encoding ascii
} finally {
    foreach($k in $keys){if($null -eq $saved[$k]){Remove-Item -LiteralPath ('Env:'+$k) -ErrorAction SilentlyContinue}else{[Environment]::SetEnvironmentVariable($k,$saved[$k],'Process')}}
}
