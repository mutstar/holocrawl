param([string]$Name = ('worship01-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
if ($Name -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Use a simple unique run name.' }
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'engine/campaign-crawl/crawl-ref/source'
$tools = Join-Path $projectRoot '.toolchain/msys64/mingw64/bin'
$output = Join-Path $projectRoot "analysis/native/worship01/$Name"
if (Test-Path -LiteralPath $output) { throw 'A run with this name exists; choose a fresh name.' }
New-Item -ItemType Directory -Path $output | Out-Null
$binary = Join-Path $output 'worship-engine.exe'
Copy-Item -LiteralPath (Join-Path $source 'crawl.exe') -Destination $binary
& (Join-Path $tools 'strip.exe') $binary
if ($LASTEXITCODE -ne 0) { throw 'Cannot strip the test snapshot.' }
$oldPath = $env:PATH
$oldTest = $env:HOLOCRAWL_WORSHIP_TEST
$oldOutput = $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT
$oldBench = $env:HOLOCRAWL_ENGINE_BENCH
$oldLoad = $env:HOLOCRAWL_WORSHIP_LOAD
Push-Location $source
try {
    $env:PATH = "$tools;$oldPath"
    $env:HOLOCRAWL_ENGINE_BENCH = $null
    $env:HOLOCRAWL_WORSHIP_TEST = $null
    & $binary -dir $source -builddb *> (Join-Path $output 'builddb.log')
    if ($LASTEXITCODE -ne 0) { throw 'Map/database initialization failed; see builddb.log.' }
    $env:HOLOCRAWL_WORSHIP_TEST = '1'
    $env:HOLOCRAWL_WORSHIP_LOAD = $null
    $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT = Join-Path $output 'validation.json'
    & $binary -dir $source -test holocrawl-worship -no-throttle *> (Join-Path $output 'native.log')
    if ($LASTEXITCODE -ne 0) { throw 'Native worship/save checks failed; see native.log.' }
    if (-not (Test-Path -LiteralPath (Join-Path $output 'validation.json'))) { throw 'No validation report was produced. Run this script in a console terminal; see native.log.' }
    $validation = Get-Content -LiteralPath (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json
    if ($validation.status -ne 'passed' -or -not $validation.publicSaveRestore) { throw 'Missing public save/restore proof.' }
    $env:HOLOCRAWL_WORSHIP_LOAD = '1'
    & $binary -dir $source -test holocrawl-worship -no-throttle *> (Join-Path $output 'fresh-process.log')
    if ($LASTEXITCODE -ne 0) { throw 'Fresh-process restore failed; see fresh-process.log.' }
    $reload = Get-Content -LiteralPath (Join-Path $output 'validation.json.reload.json') -Raw | ConvertFrom-Json
    if ($reload.status -ne 'passed' -or -not $reload.freshProcessRestore) { throw 'Missing fresh-process restore proof.' }
    @{
        version = 'worship01'
        status = 'passed'
        binarySha256 = (Get-FileHash -LiteralPath $binary).Hash
        buildSha256 = (Get-FileHash -LiteralPath (Join-Path $source 'crawl.exe')).Hash
        completedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        scope = 'Membership/renunciation and native player save/restore regression. Campaign powers and income are checked separately by test-campaign-abilities.ps1.'
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding utf8
} finally {
    Pop-Location
    $env:PATH = $oldPath
    $env:HOLOCRAWL_WORSHIP_TEST = $oldTest
    $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT = $oldOutput
    $env:HOLOCRAWL_ENGINE_BENCH = $oldBench
    $env:HOLOCRAWL_WORSHIP_LOAD = $oldLoad
}
Write-Output $output
