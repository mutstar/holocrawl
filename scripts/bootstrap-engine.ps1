$ErrorActionPreference = 'Stop'
$workspaceDir = Split-Path -Parent $PSScriptRoot
$toolchain = Get-Content -LiteralPath (Join-Path $workspaceDir 'engine/toolchain.json') -Raw | ConvertFrom-Json
$upstream = Get-Content -LiteralPath (Join-Path $workspaceDir 'engine/upstream.json') -Raw | ConvertFrom-Json
$toolchainDir = Join-Path $workspaceDir '.toolchain'
$downloadDir = Join-Path $toolchainDir 'downloads'
$bashExe = Join-Path $toolchainDir 'msys64/usr/bin/bash.exe'
New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
if (-not (Test-Path -LiteralPath $bashExe)) {
    $archive = Join-Path $downloadDir 'msys2-base.tar.xz'
    if (-not (Test-Path -LiteralPath $archive)) { Invoke-WebRequest -Uri $toolchain.archive_url -OutFile $archive }
    if ((Get-FileHash -LiteralPath $archive).Hash -ne $toolchain.archive_sha256) { throw 'MSYS2 archive checksum mismatch.' }
    & tar -xf $archive -C $toolchainDir
    if ($LASTEXITCODE -ne 0) { throw 'Cannot unpack MSYS2.' }
}
$env:MSYSTEM = 'MINGW64'
$env:CHERE_INVOKING = '1'
if (-not (Test-Path -LiteralPath (Join-Path $toolchainDir 'msys64/mingw64/bin/g++.exe'))) {
    & $bashExe -lc 'pacman -Syu --noconfirm'
    # The runtime update can terminate the first shell; run the rest in a new one.
    & $bashExe -lc 'pacman -Su --noconfirm'
    if ($LASTEXITCODE -ne 0) { throw 'MSYS2 package update failed.' }
    & $bashExe -lc 'pacman -S --noconfirm --needed make perl bison flex diffutils git mingw-w64-x86_64-gcc mingw-w64-x86_64-python-yaml mingw-w64-x86_64-pkgconf'
    if ($LASTEXITCODE -ne 0) { throw 'Build dependency installation failed.' }
}
$checkoutDir = Join-Path $workspaceDir $upstream.checkout
if (-not (Test-Path -LiteralPath (Join-Path $checkoutDir '.git'))) {
    & git clone --depth 1 --branch $upstream.tag $upstream.repository $checkoutDir
    if ($LASTEXITCODE -ne 0) { throw 'Source checkout failed.' }
}
$actualCommit = & git -C $checkoutDir rev-parse HEAD
if ($actualCommit -ne $upstream.commit) { throw "Checkout is not the expected upstream commit: $actualCommit" }
& git -C $checkoutDir -c 'url.https://github.com/.insteadOf=git://github.com/' submodule update --init --depth 1 crawl-ref/source/contrib/lua crawl-ref/source/contrib/sqlite crawl-ref/source/contrib/pcre crawl-ref/source/contrib/zlib
if ($LASTEXITCODE -ne 0) { throw 'Source dependency checkout failed.' }
$patch = Join-Path $workspaceDir 'engine/patches/holocrawl-engine.patch'
if (Test-Path -LiteralPath $patch) {
    & git -C $checkoutDir apply --reverse --check $patch 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Output 'Local engine patch is already applied.' }
    else {
        & git -C $checkoutDir apply --check $patch
        if ($LASTEXITCODE -ne 0) { throw 'Existing source differs from both upstream and the exported patch; preserving it.' }
        & git -C $checkoutDir apply $patch
        if ($LASTEXITCODE -ne 0) { throw 'Could not apply local engine patch.' }
    }
}
Write-Output 'Source and compiler are ready. Run scripts/build-engine.ps1 next.'
