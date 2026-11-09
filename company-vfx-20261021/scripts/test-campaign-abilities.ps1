param([string]$Name = ('campaign-abilities01-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
$ErrorActionPreference = 'Stop'
if ($Name -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Use a simple unique run name.' }
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'engine/campaign-crawl/crawl-ref/source'
$tools = Join-Path $projectRoot '.toolchain/msys64/mingw64/bin'
$output = Join-Path $projectRoot "analysis/native/campaign-abilities01/$Name"
if (Test-Path -LiteralPath $output) { throw 'A run with this name exists; choose a fresh name.' }
New-Item -ItemType Directory -Path $output | Out-Null
$binary = Join-Path $output 'abilities-engine.exe'
Copy-Item -LiteralPath (Join-Path $source 'crawl.exe') -Destination $binary
& (Join-Path $tools 'strip.exe') $binary
if ($LASTEXITCODE -ne 0) { throw 'Cannot strip the test snapshot.' }
$oldPath = $env:PATH
$oldTest = $env:HOLOCRAWL_CAMPAIGN_TEST
$oldOutput = $env:HOLOCRAWL_CAMPAIGN_OUTPUT
$oldBench = $env:HOLOCRAWL_ENGINE_BENCH
$oldLoad = $env:HOLOCRAWL_CAMPAIGN_RELOAD
$oldWorship = $env:HOLOCRAWL_WORSHIP_TEST
$oldWorshipOutput = $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT
$oldWorshipLoad = $env:HOLOCRAWL_WORSHIP_LOAD
Push-Location $source
try {
    $env:PATH = "$tools;$oldPath"
    $env:HOLOCRAWL_ENGINE_BENCH = $null
    $env:HOLOCRAWL_CAMPAIGN_TEST = $null
    & $binary -dir $source -builddb *> (Join-Path $output 'builddb.log')
    if ($LASTEXITCODE -ne 0) { throw 'Map/database initialization failed; see builddb.log.' }
    $env:HOLOCRAWL_CAMPAIGN_TEST = '1'
    $env:HOLOCRAWL_CAMPAIGN_RELOAD = $null
    $env:HOLOCRAWL_CAMPAIGN_OUTPUT = $output
    & $binary -dir $source -test holocrawl-campaign -no-throttle *> (Join-Path $output 'native.log')
    if ($LASTEXITCODE -ne 0) { throw 'Native campaign power/save checks failed; see native.log.' }
    if (-not (Test-Path -LiteralPath (Join-Path $output 'validation.json'))) { throw 'No validation report was produced. Run this script in a console terminal; see native.log.' }
    $validation = Get-Content -LiteralPath (Join-Path $output 'validation.json') -Raw | ConvertFrom-Json
    if ($validation.status -ne 'passed') { throw 'Missing campaign power validation.' }
    $playability = Get-Content -LiteralPath (Join-Path $output 'playability.json') -Raw | ConvertFrom-Json
    if ($playability.status -ne 'passed' -or $playability.readOnlyInfoGods -ne 22 -or $playability.wrathDispatchGods -ne 22) { throw 'Missing playability / wrath proof.' }
    $env:HOLOCRAWL_CAMPAIGN_RELOAD = '1'
    & $binary -dir $source -test holocrawl-campaign -no-throttle *> (Join-Path $output 'fresh-process.log')
    if ($LASTEXITCODE -ne 0) { throw 'Fresh-process restore failed; see fresh-process.log.' }
    $reload = Get-Content -LiteralPath (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json
    if ($reload.status -ne 'passed' -or -not $reload.nextWorldStepExact) { throw 'Missing fresh-process native world continuation proof.' }
    # Re-run membership on these exact executable bytes as well.
    $env:HOLOCRAWL_CAMPAIGN_TEST = $null
    $env:HOLOCRAWL_WORSHIP_TEST = '1'
    $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT = Join-Path $output 'membership.json'
    $env:HOLOCRAWL_WORSHIP_LOAD = $null
    & $binary -dir $source -test holocrawl-worship -no-throttle *> (Join-Path $output 'membership.log')
    if ($LASTEXITCODE -ne 0) { throw 'Membership regression failed; see membership.log.' }
    $membership = Get-Content -LiteralPath (Join-Path $output 'membership.json') -Raw | ConvertFrom-Json
    if ($membership.status -ne 'passed' -or $membership.nativePlayerTagRoundtrips -ne 176) { throw 'Membership regression proof missing.' }
    $env:HOLOCRAWL_WORSHIP_LOAD = '1'
    & $binary -dir $source -test holocrawl-worship -no-throttle *> (Join-Path $output 'membership-reload.log')
    if ($LASTEXITCODE -ne 0) { throw 'Membership fresh-process regression failed.' }
    $membershipReload = Get-Content -LiteralPath (Join-Path $output 'membership.json.reload.json') -Raw | ConvertFrom-Json
    if ($membershipReload.status -ne 'passed' -or -not $membershipReload.freshProcessRestore) { throw 'Membership reload proof missing.' }
    @{
        version = 'campaign-abilities01'
        status = 'passed'
        binarySha256 = (Get-FileHash -LiteralPath $binary).Hash
        buildSha256 = (Get-FileHash -LiteralPath (Join-Path $source 'crawl.exe')).Hash
        completedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        scope = '22 manual powers, 22 read-only description screens, 22 wrath dispatchers, natural kill income, native saves and fresh-process world continuation with active wrath.'
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding utf8
} finally {
    Pop-Location
    $env:PATH = $oldPath
    $env:HOLOCRAWL_CAMPAIGN_TEST = $oldTest
    $env:HOLOCRAWL_CAMPAIGN_OUTPUT = $oldOutput
    $env:HOLOCRAWL_ENGINE_BENCH = $oldBench
    $env:HOLOCRAWL_CAMPAIGN_RELOAD = $oldLoad
    $env:HOLOCRAWL_WORSHIP_TEST = $oldWorship
    $env:HOLOCRAWL_WORSHIP_TEST_OUTPUT = $oldWorshipOutput
    $env:HOLOCRAWL_WORSHIP_LOAD = $oldWorshipLoad
}
Write-Output $output

