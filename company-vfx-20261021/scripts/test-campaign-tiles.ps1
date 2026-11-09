param([string]$Name=('sdl-'+(Get-Date -Format 'yyyyMMdd-HHmmss')),[string]$ConsoleFixture='')
$ErrorActionPreference='Stop'
if($Name -notmatch '^[a-zA-Z0-9_-]+$'){throw 'Use a simple run name.'}
$projectRoot=Split-Path -Parent $PSScriptRoot
$source=Join-Path $projectRoot 'engine/tiles-crawl/crawl-ref/source'
$output=Join-Path $projectRoot "analysis/native/tiles01/$Name"
if(Test-Path -LiteralPath $output){throw 'Choose a fresh run name.'}
New-Item -ItemType Directory -Path $output | Out-Null
$binary=Join-Path $output 'tiles-engine.exe'
Copy-Item -LiteralPath (Join-Path $source 'crawl.exe') -Destination $binary
& (Join-Path $projectRoot '.toolchain/msys64/mingw64/bin/strip.exe') $binary
if($LASTEXITCODE){throw 'Cannot strip native tiles snapshot.'}
$rc=Join-Path $output 'visual.rc'
@('tile_skip_title = true','tile_full_screen = false','tile_window_width = 1152','tile_window_height = 800','tile_cell_pixels = 32','show_more = false') | Set-Content -LiteralPath $rc -Encoding ascii
$oldPath=$env:PATH
$names=@('HOLOCRAWL_ENGINE_BENCH','HOLOCRAWL_CAMPAIGN_TEST','HOLOCRAWL_CAMPAIGN_OUTPUT','HOLOCRAWL_CAMPAIGN_RELOAD','HOLOCRAWL_VISUAL_CAPTURE','HOLOCRAWL_WORSHIP_TEST','HOLOCRAWL_WORSHIP_TEST_OUTPUT','HOLOCRAWL_WORSHIP_LOAD')
$previous=@{}
foreach($key in $names){$previous[$key]=[Environment]::GetEnvironmentVariable($key,'Process');[Environment]::SetEnvironmentVariable($key,$null,'Process')}
function Invoke-Sdl([string]$arguments){
 $p=Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc),$arguments) -WorkingDirectory $source -WindowStyle Hidden -PassThru -Wait
 if($p.ExitCode){throw "SDL fixture failed ($($p.ExitCode)). Run in a console to see native diagnostics."}
}
try{
 $env:PATH="$(Join-Path $projectRoot '.toolchain/msys64/mingw64/bin');$oldPath"
 Invoke-Sdl '-builddb'
 $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output;$env:HOLOCRAWL_VISUAL_CAPTURE='1'
 Invoke-Sdl '-test holocrawl-campaign -no-throttle'
 $env:HOLOCRAWL_VISUAL_CAPTURE=$null
 Invoke-Sdl '-test holocrawl-campaign -no-throttle'
 $env:HOLOCRAWL_CAMPAIGN_RELOAD='1';Invoke-Sdl '-test holocrawl-campaign -no-throttle'
 $env:HOLOCRAWL_CAMPAIGN_TEST=$null;$env:HOLOCRAWL_CAMPAIGN_RELOAD=$null
 $env:HOLOCRAWL_WORSHIP_TEST='1';$env:HOLOCRAWL_WORSHIP_TEST_OUTPUT=Join-Path $output 'membership.json'
 Invoke-Sdl '-test holocrawl-worship -no-throttle'
 $env:HOLOCRAWL_WORSHIP_LOAD='1';Invoke-Sdl '-test holocrawl-worship -no-throttle'
 foreach($proof in @('visual-capture.json','validation.json','tiles-model.json','reload.json','membership.json','membership.json.reload.json')){
  $check=Get-Content -LiteralPath (Join-Path $output $proof) -Raw | ConvertFrom-Json
  if($check.status -ne 'passed'){throw "Missing proof: $proof"}
 }
 if($ConsoleFixture){
  $cross=Join-Path $output 'console-save';New-Item -ItemType Directory $cross | Out-Null
  foreach($file in @('HoloWorship01.cs','membership.json','membership.json.next-rng')){Copy-Item -LiteralPath (Join-Path $ConsoleFixture $file) -Destination (Join-Path $cross $file)}
  $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT=Join-Path $cross 'membership.json';Invoke-Sdl '-test holocrawl-worship -no-throttle'
 }
 $captureCount=(Get-Content -LiteralPath (Join-Path $output 'visual-capture.json') -Raw | ConvertFrom-Json).screenshots
 @{status='passed';scope='SDL native 22-god power/info/model fixtures, framebuffer exports, native persistence and fresh process continuation; pixel QA is separate.';screenshots=$captureCount;binarySha256=(Get-FileHash -LiteralPath $binary).Hash;consoleSaveCompatibility=!!$ConsoleFixture} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding ascii
 Write-Output $output
}finally{
 $env:PATH=$oldPath;foreach($key in $names){[Environment]::SetEnvironmentVariable($key,$previous[$key],'Process')}
}
