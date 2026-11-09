$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'engine/campaign-crawl/crawl-ref/source'
$binary = Join-Path $source 'crawl.exe'
if (-not (Test-Path -LiteralPath $binary)) { throw 'Build the campaign engine first with scripts/build-campaign-engine.sh.' }
$saveDir = Join-Path $projectRoot 'runtime/campaign01/saves'
$morgueDir = Join-Path $projectRoot 'runtime/campaign01/morgue'
New-Item -ItemType Directory -Path $saveDir,$morgueDir -Force | Out-Null
$rc = Join-Path $projectRoot 'runtime/campaign01/campaign.rc'
@("save_dir = $($saveDir.Replace('\','/'))", "morgue_dir = $($morgueDir.Replace('\','/'))") | Set-Content -LiteralPath $rc -Encoding utf8NoBOM
$oldPath = $env:PATH
$env:PATH = "$(Join-Path $projectRoot '.toolchain/msys64/mingw64/bin');$oldPath"
Push-Location $source
try {
    Write-Host 'playability01: 22 gods, powers, saved wrath and god descriptions. Press a for powers, ^ for religion, ? inside either menu for details; z in powers opens native abilities.'
    & $binary -dir $source -rc $rc -builddb
    if ($LASTEXITCODE -ne 0) { throw 'Native database initialization failed.' }
    & $binary -dir $source -rc $rc
    if ($LASTEXITCODE -ne 0) { throw "Campaign engine exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
    $env:PATH = $oldPath
}
