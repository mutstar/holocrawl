param([string]$Version='v2',[string]$ReplayVersion='05')
$ErrorActionPreference='Stop'
$workspaceDir=Split-Path -Parent $PSScriptRoot
$pythonExe=Join-Path $workspaceDir '.toolchain/msys64/mingw64/bin/python.exe'
$directory=Join-Path $workspaceDir 'analysis/native/batch'
$state=Get-Content -LiteralPath (Join-Path $directory 'job_state.json') -Raw | ConvertFrom-Json
if($state.version -ne $Version) { throw 'The requested dataset version does not match the active cohort state.' }
if(@($state.jobs | Where-Object { $_.status -ne 'complete' -or $_.exitCode -ne 0 }).Count) { throw 'Wait for every native controller to complete successfully.' }
$binaryHash=(Get-FileHash -LiteralPath (Join-Path $workspaceDir 'engine/crawl/crawl-ref/source/crawl.exe')).Hash
if($binaryHash -ne $state.buildBinarySha256) { throw 'The engine binary changed after the final cohorts started.' }
$outputs=@()
$replays=@()
foreach($build in @('melee','ranged','magic')) {
    $inputs=@()
    foreach($half in @('head','tail')) {
        foreach($shard in @('01','02')) {
            $stem="native-$half-$Version-$build-$shard"
            $inputPath=Join-Path $workspaceDir "runtime/results/$stem.jsonl"
            $manifest=Get-Content -LiteralPath ($inputPath -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
            if($manifest.buildBinarySha256 -ne $binaryHash -or $manifest.sourcePatchSha256 -ne $state.sourcePatchSha256 -or $manifest.designSha256 -ne $state.designSha256) { throw "Final shard has a different source, binary, or design: $stem" }
            & $pythonExe (Join-Path $workspaceDir 'analysis/summarize_engine_bench.py') $inputPath > (Join-Path $workspaceDir "runtime/logs/$stem.summary.log")
            if($LASTEXITCODE -ne 0) { throw "Invalid final shard: $stem" }
            $inputs+=$inputPath
        }
    }
    $outputPath=Join-Path $directory "final-all-$build-1000-$Version.jsonl"
    if(-not (Test-Path -LiteralPath $outputPath)) {
        & $pythonExe (Join-Path $workspaceDir 'analysis/merge_engine_bench.py') $outputPath @inputs
        if($LASTEXITCODE -ne 0) { throw "Cannot merge $build" }
    }
    $finalManifest=Get-Content -LiteralPath ($outputPath -replace '\.jsonl$','.manifest.json') -Raw | ConvertFrom-Json
    if($finalManifest.trialsPerCase -ne 1000 -or $finalManifest.seedStart -ne 1000 -or $finalManifest.build -ne $build -or $finalManifest.buildBinarySha256 -ne $binaryHash) { throw "Unexpected merged cohort: $build" }
    & $pythonExe (Join-Path $workspaceDir 'analysis/summarize_engine_bench.py') $outputPath > (Join-Path $workspaceDir "runtime/logs/final-all-$build-1000-$Version.summary.log")
    if($LASTEXITCODE -ne 0) { throw "Invalid merged cohort: $build" }
    foreach($order in @('check','reverse')) {
        $sample=Join-Path $workspaceDir "runtime/results/batch-$build-$order-$ReplayVersion.jsonl"
        $comparison=& $pythonExe (Join-Path $workspaceDir 'analysis/compare_engine_replays.py') $sample $outputPath
        if($LASTEXITCODE -ne 0) { throw "Final/sample replay differs: $build $order" }
        $replays+=@{build=$build;order=$order;comparison=$comparison}
    }
    $outputs+=$outputPath
}
$legacy=@()
foreach($reference in @('analysis/native/final-noel-1000.jsonl','analysis/native/sopia/final-sopia-1000.jsonl')) {
    $comparison=& $pythonExe (Join-Path $workspaceDir 'analysis/compare_engine_replays.py') (Join-Path $workspaceDir $reference) $outputs[0] --combat-only
    if($LASTEXITCODE -ne 0) { throw "Legacy melee baseline changed: $reference" }
    $legacy+=@{reference=$reference;comparison=$comparison}
}
& $pythonExe (Join-Path $workspaceDir 'analysis/report_batch_bench.py') $directory @outputs
if($LASTEXITCODE -ne 0) { throw 'Final three-build audit failed.' }
$report=Get-Content -LiteralPath (Join-Path $directory 'all-gods-summary.json') -Raw | ConvertFrom-Json
if($report.encounters -ne 552000) { throw 'Final audited encounter count is wrong.' }
@{
    status='passed';version=$Version;encounters=$report.encounters;builds=3;scenarios=8;variants=23;seedsPerCase=1000
    nativeControllerExitCodes=@($state.jobs | ForEach-Object exitCode)
    sourcePatchSha256=$state.sourcePatchSha256;buildBinarySha256=$binaryHash;designSha256=$state.designSha256
    nativeChecks='20 modules plus charm/debt/resource/resistance/water/reagent/companion/zero-damage-hit/duel-kill regressions passed'
    replays=$replays;legacyReferences=$legacy
    timingPhase='Native post-monster phase; due logical ticks use current phase positions'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $directory 'validation.json') -Encoding utf8
Write-Output 'All final native cohorts, controls, replays, hashes, and counts passed.'
