param(
    [Parameter(Mandatory)][ValidateSet('melee','ranged','magic')][string]$Build,
    [string]$Version='03',
    [int]$Trials=3,
    [int]$SeedStart=1661
)
$ErrorActionPreference='Stop'
$workspaceDir=Split-Path -Parent $PSScriptRoot
$pythonExe=Join-Path $workspaceDir '.toolchain/msys64/mingw64/bin/python.exe'
$names=@("batch-$Build-check-$Version","batch-$Build-reverse-$Version")
for ($i=0; $i -lt 2; $i++) {
    $name=$names[$i]
    $log=Join-Path $workspaceDir "runtime/logs/$name.log"
    & (Join-Path $PSScriptRoot 'run-engine-bench.ps1') -Suite batch-dev -Build $Build -Trials $Trials -SeedStart $SeedStart -Name $name -ReverseVariants:([bool]$i) *> $log
    if ($LASTEXITCODE -ne 0) { throw "Native replay failed: $name" }
    & $pythonExe (Join-Path $workspaceDir 'analysis/summarize_engine_bench.py') (Join-Path $workspaceDir "runtime/results/$name.jsonl") > (Join-Path $workspaceDir "runtime/results/$name.summary.json")
    if ($LASTEXITCODE -ne 0) { throw "Incomplete replay: $name" }
}
$forward=Join-Path $workspaceDir "runtime/results/$($names[0]).jsonl"
$reverse=Join-Path $workspaceDir "runtime/results/$($names[1]).jsonl"
$manifest=Get-Content -LiteralPath ($forward -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
$reverseManifest=Get-Content -LiteralPath ($reverse -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
foreach($field in @('engineCommit','buildBinarySha256','sourcePatchSha256','designSha256','build','scope','startingGeometry','initialGodResources')) {
    if($manifest.$field -ne $reverseManifest.$field) { throw "Replay source/fixture changed between runs: $field" }
}
$comparison=& $pythonExe (Join-Path $workspaceDir 'analysis/compare_engine_replays.py') $forward $reverse
if ($LASTEXITCODE -ne 0) { throw 'Variant-order dependence detected.' }
$directory=Join-Path $workspaceDir 'analysis/native/batch/validation'
New-Item -ItemType Directory -Path $directory -Force | Out-Null
@{
    status='passed';build=$Build;trialsPerCase=$Trials;seedStart=$SeedStart
    comparedEncounters=$Trials*8*23;comparison=$comparison
    forwardResultsSha256=(Get-FileHash -LiteralPath $forward).Hash
    reverseResultsSha256=(Get-FileHash -LiteralPath $reverse).Hash
    buildBinarySha256=$manifest.buildBinarySha256
    sourcePatchSha256=$manifest.sourcePatchSha256
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $directory "$Build-replay-$Version.json") -Encoding utf8
Write-Output "$Build replay passed: $comparison"
