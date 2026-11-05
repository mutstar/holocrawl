$ErrorActionPreference='Stop'
$migrationRoot=$PSScriptRoot
$msysRoot=Join-Path $migrationRoot '../company-polka-20261022/.toolchain/msys64'
$env:MSYSTEM='MINGW64'
$env:CHERE_INVOKING='1'
Push-Location $migrationRoot
try {
    & "$msysRoot/usr/bin/bash.exe" -lc 'bash scripts/build-street.sh'
    if ($LASTEXITCODE -ne 0) { throw "Street build failed: $LASTEXITCODE" }
} finally { Pop-Location }


