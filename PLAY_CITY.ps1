param([string]$Seed, [switch]$Legacy)
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'holocrawl-0341/engine/upstream/crawl-ref/source'
$installPath = Join-Path $PSScriptRoot 'holocrawl-0341/runtime/native-city107-install.json'
$using107 = $false
if (-not $Legacy -and (Test-Path -LiteralPath $installPath)) {
    $install = Get-Content -LiteralPath $installPath -Raw | ConvertFrom-Json
    if ($install.status -ne 'passed') { throw 'Latest native city installation is not validated.' }
    $source = Join-Path $PSScriptRoot $install.source
    if ((Get-FileHash -LiteralPath (Join-Path $source 'crawl.exe') -Algorithm SHA256).Hash -ne $install.binarySha256) { throw 'Native107 binary changed since validation. Revalidate before launching.' }
    $using107 = $true
}
$executable = Join-Path $source 'crawl.exe'
$runtime = Join-Path $PSScriptRoot $(if ($using107) { 'holocrawl-0341/runtime/city107' } else { 'holocrawl-0341/runtime/city77' })
if (-not (Test-Path -LiteralPath $executable)) { throw 'Run BUILD_CITY.ps1 first to build the native city engine.' }
if ($Seed -and $Seed -notmatch '^\d{1,20}$') { throw 'Seed must be an unsigned decimal integer.' }
foreach ($directory in @($runtime, (Join-Path $runtime 'saves'), (Join-Path $runtime 'morgue'))) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
$settings = Join-Path $runtime 'init.txt'
if (-not (Test-Path -LiteralPath $settings)) {
    $initialSettings = @'
name = HoloCity
species = Human
background = Fighter
weapon = long sword
remember_name = false
show_more = false
tile_full_screen = false
tile_window_width = 1280
tile_window_height = 900
tile_cell_pixels = 32
'@
    [IO.File]::WriteAllText($settings, $initialSettings, [Text.UTF8Encoding]::new($false))
}
$previousMode = $env:HOLOCRAWL_CITY77
$previousStreet = $env:HOLOCRAWL_STREET01_MAP
$env:HOLOCRAWL_CITY77 = '1'
$env:HOLOCRAWL_STREET01_MAP = $null
$saveDirectory = (Join-Path $runtime 'saves').Replace('\', '/') + '/'
$arguments = @('-rc', $settings, '-extra-opt-last', "save_dir = $saveDirectory", '-morgue', (Join-Path $runtime 'morgue'))
if ($Seed) {
    $arguments += @('-seed', $Seed)
}
Push-Location $source
try {
    $quotedArguments = $arguments | ForEach-Object { '"' + $_.Replace('"', '\"') + '"' }
    $game = Start-Process -FilePath $executable -ArgumentList $quotedArguments -WorkingDirectory $source -PassThru
    $game.WaitForExit()
    if ($game.ExitCode -ne 0) { throw "Native city exited with code $($game.ExitCode)." }
} finally {
    Pop-Location
    $env:HOLOCRAWL_CITY77 = $previousMode
    $env:HOLOCRAWL_STREET01_MAP = $previousStreet
}
