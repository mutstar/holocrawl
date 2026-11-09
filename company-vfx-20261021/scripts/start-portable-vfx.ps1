param([switch]$SmokeTest)
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
