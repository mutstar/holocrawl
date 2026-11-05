param([int]$PreferredPort=8797)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'OPEN_HOME_EXPLORER.ps1') -NoBrowser -PreferredPort $PreferredPort
$state=Get-Content -LiteralPath (Join-Path $PSScriptRoot '.home-preview/server-state.json') -Raw | ConvertFrom-Json
$nodePath=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if (-not (Test-Path -LiteralPath $nodePath)) { $nodePath=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node.exe' }
if (-not (Test-Path -LiteralPath $nodePath)) { $nodePath=(Get-Command node.exe -ErrorAction Stop).Source }
$previousPreviewURL=$env:HOLOCRAWL_PREVIEW_URL
try {
    $env:HOLOCRAWL_PREVIEW_URL="http://127.0.0.1:$($state.port)"
    Push-Location (Join-Path $PSScriptRoot 'holocrawl-0341')
    try {
        & $nodePath 'scripts/check-final-floor01.cjs'
        if ($LASTEXITCODE -ne 0) { throw 'Final floor layout checks failed.' }
        & $nodePath 'scripts/check-final-floor-crates01.cjs'
        if ($LASTEXITCODE -ne 0) { throw 'Crate checks failed.' }
        & $nodePath 'scripts/check-final-floor-exploration01.cjs'
        if ($LASTEXITCODE -ne 0) { throw 'Exploration checks failed.' }
    } finally { Pop-Location }
} finally { $env:HOLOCRAWL_PREVIEW_URL=$previousPreviewURL }
