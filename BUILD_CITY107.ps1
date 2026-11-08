param([int]$Jobs = 8, [string]$BashPath)
$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$engine = Join-Path $project 'holocrawl-0341/analysis/native-play107-01/engine'
$snapshot = Join-Path $project 'holocrawl-0341/migration/engine0341-play107'
if (-not $BashPath) { $BashPath = $env:HOLOCRAWL_BASH }
if (-not $BashPath) {
    $candidates = @(
        (Join-Path $project '.toolchain/msys64/usr/bin/bash.exe'),
        'C:/msys64/usr/bin/bash.exe'
    )
    $candidates += @(Get-ChildItem -Path (Join-Path (Split-Path $project) '*/.toolchain/msys64/usr/bin/bash.exe') -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
    $BashPath = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $BashPath) { throw 'MSYS2 compiler not found. Set HOLOCRAWL_BASH to the MSYS2 usr/bin/bash.exe path.' }
if (-not (Test-Path -LiteralPath (Join-Path $engine '.git'))) {
    git clone --depth 1 --branch 0.34.1 https://github.com/crawl/crawl.git $engine
    if ($LASTEXITCODE -ne 0) { throw 'Cannot restore the 0.34.1 source.' }
}
$base = git -C $engine rev-parse HEAD
if ($base -ne '1eebc1a2892e1c89776a0d7a10691f8dac8d9796') { throw 'Engine source is not the reviewed 0.34.1 commit.' }
$patch = Join-Path $snapshot 'tracked.patch'
git -C $engine apply --reverse --check $patch 2>$null
if ($LASTEXITCODE -ne 0) {
    git -C $engine apply --check $patch
    if ($LASTEXITCODE -ne 0) { throw 'Existing engine source differs. Preserved existing files.' }
    git -C $engine apply $patch
    if ($LASTEXITCODE -ne 0) { throw 'Cannot apply native107 engine patch.' }
}
$manifest = Get-Content -LiteralPath (Join-Path $snapshot 'manifest.json') -Raw | ConvertFrom-Json
foreach ($entry in $manifest.overlay) {
    $existing = Join-Path $engine $entry.path
    if ((Test-Path -LiteralPath $existing) -and (Get-FileHash -LiteralPath $existing -Algorithm SHA256).Hash -ne $entry.sha256) {
        throw "Existing engine overlay differs and was preserved: $($entry.path)"
    }
}
Get-ChildItem -LiteralPath (Join-Path $snapshot 'overlay') | Copy-Item -Destination $engine -Recurse -Force
git -C $engine submodule update --init --depth 1 crawl-ref/source/contrib/lua crawl-ref/source/contrib/pcre crawl-ref/source/contrib/sqlite crawl-ref/source/contrib/zlib crawl-ref/source/contrib/fonts crawl-ref/source/contrib/freetype crawl-ref/source/contrib/libpng crawl-ref/source/contrib/sdl2 crawl-ref/source/contrib/sdl2-image
if ($LASTEXITCODE -ne 0) { throw 'Cannot restore compiler dependencies.' }
$env:MSYSTEM = 'MINGW64'
$env:CHERE_INVOKING = '1'
$env:HOLOCRAWL_CITY_SOURCE = Join-Path $engine 'crawl-ref/source'
$env:HOLOCRAWL_BUILD_JOBS = [string]$Jobs
& $BashPath -lc 'cd "$(cygpath -u "$HOLOCRAWL_CITY_SOURCE")" && make -j"$HOLOCRAWL_BUILD_JOBS" TILES=1 DEBUG=1 CFOPTIMIZE=-O1 NO_PKGCONFIG=1 EXTERNAL_DEFINES=-DDEBUG_TESTS crawl.exe'
if ($LASTEXITCODE -ne 0) { throw "City engine build failed with exit code $LASTEXITCODE." }
Write-Output 'Native107 build ready. Run suites in design/NATIVE_PLAY107_REVIEW.md before installing; original engine preserved.'
