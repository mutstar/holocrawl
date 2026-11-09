param([switch]$RebuildDatabase)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'engine/tiles-crawl/crawl-ref/source'
$binary = Join-Path $projectRoot 'runtime/tiles01/HoloCrawl.exe'
if(-not (Test-Path -LiteralPath $binary)){$binary=Join-Path $source 'crawl.exe'}
if (-not (Test-Path -LiteralPath $binary)) { throw 'Build the tiles engine with scripts/build-campaign-tiles.sh first.' }
$saveDir = Join-Path $projectRoot 'runtime/campaign01/saves'
$morgueDir = Join-Path $projectRoot 'runtime/campaign01/morgue'
New-Item -ItemType Directory -Path $saveDir,$morgueDir -Force | Out-Null
$rc = Join-Path $projectRoot 'runtime/campaign01/tiles.rc'
if (-not (Test-Path -LiteralPath $rc)) {
    $rcLines = @("save_dir = $($saveDir.Replace('\','/'))", "morgue_dir = $($morgueDir.Replace('\','/'))",'tile_skip_title = true','tile_full_screen = false','tile_cell_pixels = 48','tile_filter_scaling = false')
    [System.IO.File]::WriteAllLines($rc,$rcLines,(New-Object System.Text.UTF8Encoding($false)))
}
$oldPath = $env:PATH
try {
    $env:PATH = "$(Join-Path $projectRoot '.toolchain/msys64/mingw64/bin');$oldPath"
    foreach ($name in @('HOLOCRAWL_CAMPAIGN_TEST','HOLOCRAWL_VISUAL_CAPTURE','HOLOCRAWL_ENGINE_BENCH','HOLOCRAWL_WORSHIP_TEST')) { [Environment]::SetEnvironmentVariable($name,$null,'Process') }
    $dbStamp = Join-Path $projectRoot 'runtime/campaign01/tiles-db-path.txt'
    if($RebuildDatabase -or -not (Test-Path -LiteralPath $dbStamp) -or (Get-Content -LiteralPath $dbStamp -Raw).Trim() -ne $source) {
        $build = Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-builddb') -WorkingDirectory $source -WindowStyle Hidden -PassThru -Wait
        if($build.ExitCode) { throw "Tile database initialization failed: $($build.ExitCode)" }
        [System.IO.File]::WriteAllText($dbStamp,$source,(New-Object System.Text.UTF8Encoding($false)))
    }
    Write-Host 'HoloCrawl tiles01: a = powers, ^ = religion, ? in those menus = god details. Existing campaign saves are shared.'
    $game = Start-Process -FilePath $binary -ArgumentList @('-dir',('"{0}"' -f $source),'-rc',('"{0}"' -f $rc)) -WorkingDirectory $source -WindowStyle Normal -PassThru -Wait
    if($game.ExitCode) { throw "HoloCrawl tiles exited with code $($game.ExitCode)" }
} finally { $env:PATH = $oldPath }
