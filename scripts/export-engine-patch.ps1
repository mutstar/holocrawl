$ErrorActionPreference = 'Stop'
$workspaceDir = Split-Path -Parent $PSScriptRoot
$checkoutDir = Join-Path $workspaceDir 'engine/crawl'
$patchDir = Join-Path $workspaceDir 'engine/patches'
New-Item -ItemType Directory -Path $patchDir -Force | Out-Null
& git -C $checkoutDir add -N crawl-ref/source/holocrawl.h crawl-ref/source/holocrawl.cc crawl-ref/source/holo-sopia.h crawl-ref/source/holo-sopia.cc crawl-ref/source/holo-batch.h crawl-ref/source/holo-batch-internal.h crawl-ref/source/holo-batch.cc crawl-ref/source/holo-batch-martial.cc crawl-ref/source/holo-batch-resources.cc crawl-ref/source/holo-batch-space.cc crawl-ref/source/holo-batch-summons.cc
if ($LASTEXITCODE -ne 0) { throw 'Cannot include new module in patch.' }
& git -C $checkoutDir add -N crawl-ref/source/holo-batch-experiments.cc
if ($LASTEXITCODE -ne 0) { throw 'Cannot include experiments module in patch.' }
$patchFile = Join-Path $patchDir 'holocrawl-engine.patch'
& git -C $checkoutDir diff --binary --full-index "--output=$patchFile"
if ($LASTEXITCODE -ne 0) { throw 'Cannot export engine patch.' }
Write-Output $patchFile
