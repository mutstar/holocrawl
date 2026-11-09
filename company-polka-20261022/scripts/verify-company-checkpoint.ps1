param([switch]$Smoke)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.toolchain/msys64/mingw64/bin/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Bundled Python is missing. Extract the complete ZIP before verifying.' }
$helper = Join-Path $PSScriptRoot 'verify-company-checkpoint.py'
if ($Smoke) { & $pythonExe -X utf8 $helper --smoke }
else { & $pythonExe -X utf8 $helper }
if ($LASTEXITCODE -ne 0) { throw "Checkpoint verification failed: $LASTEXITCODE" }
