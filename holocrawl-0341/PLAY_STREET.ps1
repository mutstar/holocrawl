param([string]$Seed)
$ErrorActionPreference='Stop'
$streetRoot=$PSScriptRoot
$streetRuntime=Join-Path $streetRoot 'runtime/street01'
$streetExe=Join-Path $streetRuntime 'HoloCrawl-0341-street.exe'
$streetMap=Join-Path $streetRuntime 'maps/current.hcmap'
if (-not (Test-Path -LiteralPath $streetExe)) { throw 'Build first with BUILD_STREET.ps1.' }
if (-not $Seed) { $Seed='CITY-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss') }
& 'C:/Program Files/nodejs/node.exe' (Join-Path $streetRoot 'scripts/export-street-map.cjs') $Seed $streetMap
if ($LASTEXITCODE -ne 0) { throw 'Street layout export failed.' }
$oldStreetMap=$env:HOLOCRAWL_STREET01_MAP
try {
    $env:HOLOCRAWL_STREET01_MAP=$streetMap
    Start-Process -FilePath $streetExe -WorkingDirectory $streetRuntime -ArgumentList '-dir','.','-rc','init.txt'
} finally { $env:HOLOCRAWL_STREET01_MAP=$oldStreetMap }
