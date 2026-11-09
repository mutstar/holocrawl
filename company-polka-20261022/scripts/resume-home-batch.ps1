param(
    [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Version = 'v3',
    [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$ReplayVersion = 'home01'
)
$ErrorActionPreference = 'Stop'
$workspaceDir = Split-Path -Parent $PSScriptRoot
$stateDir = Join-Path $workspaceDir 'analysis/native/batch'
$statePath = Join-Path $stateDir 'job_state.json'
$previous = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
if ($previous.version -eq $Version) { throw 'This version already has state; preserve it and choose a fresh version.' }
$backupPath = Join-Path $stateDir "job_state-before-$Version.json"
if (Test-Path -LiteralPath $backupPath) { throw 'State backup already exists; refusing to overwrite it.' }
$binaryHash = (Get-FileHash -LiteralPath (Join-Path $workspaceDir 'engine/crawl/crawl-ref/source/crawl.exe')).Hash
$patchHash = (Get-FileHash -LiteralPath (Join-Path $workspaceDir 'engine/patches/holocrawl-engine.patch')).Hash
$designHash = (Get-FileHash -LiteralPath (Join-Path $workspaceDir 'HOLOCRAWL_DESIGN.md')).Hash
foreach ($build in @('melee','ranged','magic')) {
    $replayPath = Join-Path $stateDir "validation/$build-replay-$ReplayVersion.json"
    $replay = Get-Content -LiteralPath $replayPath -Raw | ConvertFrom-Json
    if ($replay.status -ne 'passed' -or $replay.comparedEncounters -ne 552 -or $replay.buildBinarySha256 -ne $binaryHash -or $replay.sourcePatchSha256 -ne $patchHash) {
        throw "Fresh-machine replay is missing or differs from frozen inputs: $build"
    }
    foreach ($half in @('head','tail')) {
        foreach ($shard in @('01','02')) {
            $existing = Join-Path $workspaceDir "runtime/results/native-$half-$Version-$build-$shard.manifest.json"
            if (Test-Path -LiteralPath $existing) { throw "Run already exists: $existing" }
        }
    }
}
Copy-Item -LiteralPath $statePath -Destination $backupPath
$jobs = @()
foreach ($half in @('head','tail')) {
    foreach ($build in @('melee','ranged','magic')) {
        $jobs += [ordered]@{
            status='pending';prefix="native-$half-$Version";build=$build
            seedStart=$(if ($half -eq 'head') {1000} else {1500})
            shards=2;trialsPerShard=250;processId=$null;exitCode=$null
        }
    }
}
$state = [ordered]@{
    phase='home-full-cohorts-running';version=$Version;nativeSourceFrozen=$true
    targetEncounters=552000;sourcePatchSha256=$patchHash;buildBinarySha256=$binaryHash
    designSha256=$designHash;replayVersion=$ReplayVersion;replayExactMatches=1656
    seedStart=1000;seedsPerCase=1000;scenarios=8;variants=23;jobs=$jobs
    startedAtUtc=[DateTime]::UtcNow.ToString('o');updatedAtUtc=[DateTime]::UtcNow.ToString('o')
    finalDatasetComplete=$false;previousState=$backupPath
}
function Save-HomeState {
    $state.updatedAtUtc = [DateTime]::UtcNow.ToString('o')
    $temporary = "$statePath.tmp"
    [IO.File]::WriteAllText($temporary, ($state | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $statePath -Force
}
Save-HomeState
$processes = @()
$pwsh = (Get-Process -Id $PID).Path
foreach ($job in $jobs) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $pwsh
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.WorkingDirectory = $workspaceDir
    foreach ($argument in @('-NoProfile','-File',(Join-Path $PSScriptRoot 'run-batch-shards.ps1'),'-Build',$job.build,'-Prefix',$job.prefix,'-Shards','2','-TrialsPerShard','250','-SeedStart',[string]$job.seedStart)) {
        $info.ArgumentList.Add($argument)
    }
    $process = [Diagnostics.Process]::Start($info)
    $job.processId = $process.Id
    $job.status = 'running'
    $processes += $process
    Save-HomeState
}
Write-Output 'Six fresh native cohorts launched. Frozen source/design/binary; no balance edits during execution.'
$watch = [Diagnostics.Stopwatch]::StartNew()
$lastReport = -30
while (@($jobs | Where-Object { $_.status -eq 'running' }).Count) {
    for ($i=0; $i -lt $jobs.Count; $i++) {
        if ($jobs[$i].status -eq 'running' -and $processes[$i].HasExited) {
            $processes[$i].WaitForExit()
            $jobs[$i].exitCode = $processes[$i].ExitCode
            $jobs[$i].status = $(if ($processes[$i].ExitCode -eq 0) {'complete'} else {'failed'})
            Write-Output ("Finished {0}/{1}: exit {2}" -f $jobs[$i].prefix,$jobs[$i].build,$jobs[$i].exitCode)
            Save-HomeState
        }
    }
    if ($watch.Elapsed.TotalSeconds - $lastReport -ge 30) {
        $lastReport = $watch.Elapsed.TotalSeconds
        $complete = @($jobs | Where-Object { $_.status -eq 'complete' }).Count
        Write-Output ("Native controllers complete: {0}/6; elapsed {1:N0}s" -f $complete,$watch.Elapsed.TotalSeconds)
        Save-HomeState
    }
    Start-Sleep -Seconds 1
}
if (@($jobs | Where-Object { $_.status -ne 'complete' -or $_.exitCode -ne 0 }).Count) {
    $state.phase = 'home-cohort-failure'
    Save-HomeState
    throw 'At least one cohort failed. Preserved all logs and partial results; finalization was not run.'
}
$state.phase='home-final-audit-running'
Save-HomeState
& (Join-Path $PSScriptRoot 'finalize-batch.ps1') -Version $Version -ReplayVersion $ReplayVersion
if ($LASTEXITCODE -ne 0) { throw 'Final audit returned a failure.' }
$validation = Get-Content -LiteralPath (Join-Path $stateDir 'validation.json') -Raw | ConvertFrom-Json
if ($validation.status -ne 'passed' -or $validation.encounters -ne 552000 -or $validation.version -ne $Version) {
    throw 'Final validation artifact is incomplete or from a different version.'
}
$state.phase='home-final-validation-complete'
$state.finalDatasetComplete=$true
$state.completedAtUtc=[DateTime]::UtcNow.ToString('o')
Save-HomeState
Write-Output 'PASS: complete, audited 552,000 encounters with fresh-machine replays and legacy controls.'
