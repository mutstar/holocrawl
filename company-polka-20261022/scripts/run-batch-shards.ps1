param(
    [Parameter(Mandatory)][ValidateSet('melee','ranged','magic')][string]$Build,
    [string]$Prefix='native-all-v2',
    [int]$TrialsPerShard=250,
    [int]$Shards=4,
    [int]$SeedStart=1000,
    [switch]$Resume
)
$ErrorActionPreference='Stop'
if ($Prefix -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Prefix must be a plain file stem.' }
if ($TrialsPerShard -lt 1 -or $Shards -lt 1) { throw 'Trials and shards must be positive.' }
$workspaceDir=Split-Path -Parent $PSScriptRoot
$pythonExe=Join-Path $workspaceDir '.toolchain/msys64/mingw64/bin/python.exe'
$currentHash=(Get-FileHash -LiteralPath (Join-Path $workspaceDir 'engine/crawl/crawl-ref/source/crawl.exe')).Hash
$sourceReference=$null
$designReference=$null
for ($shard=0; $shard -lt $Shards; $shard++) {
    $name='{0}-{1}-{2:00}' -f $Prefix,$Build,($shard+1)
    $seed=$SeedStart+$shard*$TrialsPerShard
    $result=Join-Path $workspaceDir ('runtime/results/'+$name+'.jsonl')
    $log=Join-Path $workspaceDir ('runtime/logs/'+$name+'.log')
    $summary=Join-Path $workspaceDir ('runtime/results/'+$name+'.summary.json')
    if (Test-Path -LiteralPath $result) {
        if (-not $Resume) { throw "Result already exists: $name" }
        $manifest=Get-Content -LiteralPath ($result -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
        if ($manifest.buildBinarySha256 -ne $currentHash -or $manifest.build -ne $Build -or $manifest.seedStart -ne $seed -or $manifest.trialsPerCase -ne $TrialsPerShard) {
            throw "Cannot resume a different binary or fixture: $name"
        }
    } else {
        Write-Output "Starting $name (seeds $seed through $($seed+$TrialsPerShard-1))"
        & (Join-Path $PSScriptRoot 'run-engine-bench.ps1') -Suite batch -Build $Build -Trials $TrialsPerShard -SeedStart $seed -Name $name *> $log
        if ($LASTEXITCODE -ne 0) { throw "Native execution failed: $name; see $log" }
    }
    $manifest=Get-Content -LiteralPath ($result -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
    if($manifest.buildBinarySha256 -ne $currentHash) { throw "Binary changed during this cohort: $name" }
    if($null -eq $sourceReference) { $sourceReference=$manifest.sourcePatchSha256;$designReference=$manifest.designSha256 }
    if($sourceReference -ne $manifest.sourcePatchSha256 -or $designReference -ne $manifest.designSha256) { throw "Source or design changed during this cohort: $name" }
    & $pythonExe (Join-Path $workspaceDir 'analysis/summarize_engine_bench.py') $result > (Join-Path $workspaceDir "runtime/logs/$name.summary.log")
    if ($LASTEXITCODE -ne 0) { throw "Incomplete or invalid native records: $name" }
    Write-Output "Validated $name"
}
