param([int]$Jobs = 8)
$ErrorActionPreference = 'Stop'
$workspaceDir = Split-Path -Parent $PSScriptRoot
$bashExe = Join-Path $workspaceDir '.toolchain/msys64/usr/bin/bash.exe'
if (-not (Test-Path -LiteralPath $bashExe)) { throw 'Project-local MSYS2 is missing.' }
$env:MSYSTEM = 'MINGW64'
$env:CHERE_INVOKING = '1'
$env:HOLOCRAWL_BUILD_JOBS = [string]$Jobs
Push-Location $workspaceDir
try {
    & $bashExe -lc 'bash scripts/build-engine.sh'
    if ($LASTEXITCODE -ne 0) { throw "Engine build failed: $LASTEXITCODE" }
} finally { Pop-Location }
