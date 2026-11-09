param(
    [int]$Trials = 10,
    [int]$SeedStart = 1000,
    [string]$Name = 'native-noel-smoke',
    [switch]$ReverseVariants,
    [ValidateSet('noel','sopia','batch','batch-dev')][string]$Suite='noel',
    [ValidateSet('melee','ranged','magic')][string]$Build='melee'
)
$ErrorActionPreference = 'Stop'
if ($Name -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Name must be a plain file stem.' }
$workspaceDir = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $workspaceDir 'engine/crawl/crawl-ref/source'
$engineExe = Join-Path $sourceDir 'crawl.exe'
if (-not (Test-Path -LiteralPath $engineExe)) { throw 'Build the engine first.' }
$binaryDir = Join-Path $workspaceDir 'runtime/bin'
New-Item -ItemType Directory -Path $binaryDir -Force | Out-Null
$runExe = Join-Path $binaryDir ($Name + '.exe')
if (Test-Path -LiteralPath $runExe) { throw "Run binary already exists: $runExe" }
$stripExe = Join-Path $workspaceDir '.toolchain/msys64/mingw64/bin/strip.exe'
& $stripExe --strip-debug -o $runExe $engineExe
if ($LASTEXITCODE -ne 0) { throw 'Cannot snapshot the benchmark binary.' }
$resultDir = Join-Path $workspaceDir 'runtime/results'
New-Item -ItemType Directory -Path $resultDir -Force | Out-Null
$resultPath = Join-Path $resultDir ($Name + '.jsonl')
if (Test-Path -LiteralPath $resultPath) { throw "Result already exists: $resultPath" }
$manifestPath = Join-Path $resultDir ($Name + '.manifest.json')
$patchSnapshot = Join-Path $resultDir ($Name + '.engine.patch')
$snapshotMutex = [Threading.Mutex]::new($false,'Local\HoloCrawlEngineSnapshot')
$snapshotAcquired = $false
try {
    $snapshotAcquired = $snapshotMutex.WaitOne(60000)
    if (-not $snapshotAcquired) { throw 'Another benchmark is still snapshotting source.' }
    & (Join-Path $PSScriptRoot 'export-engine-patch.ps1') | Out-Null
    Copy-Item -LiteralPath (Join-Path $workspaceDir 'engine/patches/holocrawl-engine.patch') -Destination $patchSnapshot
} finally {
    if ($snapshotAcquired) { $snapshotMutex.ReleaseMutex() }
    $snapshotMutex.Dispose()
}
$designSnapshot = Join-Path $resultDir ($Name + '.design.md')
Copy-Item -LiteralPath (Join-Path $workspaceDir 'HOLOCRAWL_DESIGN.md') -Destination $designSnapshot
@{
    engineCommit = 'a7d21def0a8b0b39c6825b643a3b51f371b73583'
    binarySha256 = (Get-FileHash -LiteralPath $runExe).Hash
    buildBinarySha256 = (Get-FileHash -LiteralPath $engineExe).Hash
    binary = $runExe
    designSha256 = (Get-FileHash -LiteralPath (Join-Path $workspaceDir 'HOLOCRAWL_DESIGN.md')).Hash
    trialsPerCase = $Trials
    seedStart = $SeedStart
    reverseVariants = [bool]$ReverseVariants
    suite = $Suite
    build = $Build
    sourcePatchSha256 = (Get-FileHash -LiteralPath $patchSnapshot).Hash
    scenarios = @('early_ogre','early_three_orcs','mid_ettin','mid_three_warriors','late_stone_giant','late_two_stone_giants','late_three_ettins','late_three_warriors')
    variants = $(if ($Suite -eq 'sopia') { @('no_god','noel_v2','sopia_ring','sopia_full') } elseif ($Suite -like 'batch*') { @((Get-Content -LiteralPath (Join-Path $workspaceDir 'engine/batch_registry.json') -Raw | ConvertFrom-Json).variants) } else { @('no_god','noel_v1','noel_v2') })
    explorationTraps = $false
    randomSpawns = $false
    banishmentPolicy = 'Ends the fixed encounter as a separate banished outcome; not a win or HP death.'
    scope = $(if ($Suite -like 'batch*') { '22 native combat cores plus no-god; fixed build and deterministic ability policy; no campaign progression, gifts, piety income, wrath, worship UI or save integration. Timers drain after the native monster phase using that phase positions.' } elseif ($Suite -eq 'sopia') { 'No-god, current Noel, Sopia ring-only and Sopia full combat core; fixed melee kits; no campaign progression.' } else { 'No-god versus Noel combat core v1/v2; fixed equipment, no gift progression.' })
    startingGeometry = $(if ($Build -eq 'melee') { 'Adjacent enemies at (1,0),(0,1),(-1,0), matching verified melee references.' } else { 'Distant enemies at (6,0),(5,2),(-6,0); compare against the no-god reference of the same build.' })
    initialGodResources = 'No prebuffs/preparation; Polka applause0; Koyori stock0; Okayu fullness30 and full initial shield; other combat resources0.'
    results = $resultPath
} | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding utf8
$env:HOLOCRAWL_ENGINE_BENCH = '1'
$env:HOLOCRAWL_TRIALS = [string]$Trials
$env:HOLOCRAWL_SEED_START = [string]$SeedStart
$env:HOLOCRAWL_RESULTS = $resultPath
$env:HOLOCRAWL_REVERSE_VARIANTS = [string][int][bool]$ReverseVariants
$env:HOLOCRAWL_SUITE = $Suite
$env:HOLOCRAWL_BUILD = $Build
Push-Location $sourceDir
try {
    # First-time map compilation must happen outside -test: 0.24 map scripts
    # treat test mode as an already started game while validating portal maps.
    & $runExe -dir $sourceDir -builddb
    if ($LASTEXITCODE -ne 0) { throw "Engine database build failed: $LASTEXITCODE" }
    & $runExe -dir $sourceDir -test holocrawl -no-throttle
    if ($LASTEXITCODE -ne 0) { throw "Native benchmark failed: $LASTEXITCODE" }
} finally {
    Pop-Location
    $env:HOLOCRAWL_ENGINE_BENCH = $null
    $env:HOLOCRAWL_RESULTS = $null
    $env:HOLOCRAWL_TRIALS = $null
    $env:HOLOCRAWL_SEED_START = $null
    $env:HOLOCRAWL_REVERSE_VARIANTS = $null
    $env:HOLOCRAWL_SUITE = $null
    $env:HOLOCRAWL_BUILD = $null
}
Write-Output $resultPath
