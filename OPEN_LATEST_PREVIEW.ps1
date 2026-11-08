param([switch]$NoBrowser,[int]$PreferredPort=8797)
$ErrorActionPreference='Stop'
$bundleRoot=$PSScriptRoot
$previewRoot=Join-Path $bundleRoot 'holocrawl-0341/preview'
$serverScript=Join-Path $bundleRoot 'scripts/serve-home-preview.py'
$stateDir=Join-Path $bundleRoot '.home-preview'
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
$pythonPath=$null
$pythonPrefix=@()
$bundledPython=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (Test-Path -LiteralPath $bundledPython) { $pythonPath=$bundledPython }
if (-not $pythonPath) {
    $pyCommand=Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyCommand) { $pythonPath=$pyCommand.Source; $pythonPrefix=@('-3') }
}
if (-not $pythonPath) {
    $pyCommand=Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCommand -and $pyCommand.Source -notmatch 'WindowsApps') { $pythonPath=$pyCommand.Source }
}
if (-not $pythonPath) { throw 'Python 3 was not found. Open this folder in Codex or install Python 3, then retry.' }
$port=$PreferredPort
$running=$false
for ($attempt=0;$attempt -lt 20;$attempt++) {
    try {
        $health=Invoke-RestMethod -Uri "http://127.0.0.1:$port/__holocrawl_home_health.json" -TimeoutSec 1
        if ($health.app -eq 'HoloCrawl-home-20261104' -and $health.root -eq $previewRoot) { $running=$true; break }
    } catch {}
    $listener=[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,$port)
    try { $listener.Start(); $listener.Stop(); break } catch { $listener.Stop(); $port++ }
}
if (-not $running) {
    $launchArguments=@($pythonPrefix)+@('-u',('"'+$serverScript+'"'),'--root',('"'+$previewRoot+'"'),'--port',"$port")
    $serverProcess=Start-Process -FilePath $pythonPath -ArgumentList $launchArguments -WorkingDirectory $bundleRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $stateDir 'server.stdout.log') -RedirectStandardError (Join-Path $stateDir 'server.stderr.log')
    $ready=$false
    for ($poll=0;$poll -lt 30;$poll++) {
        try { $health=Invoke-RestMethod -Uri "http://127.0.0.1:$port/__holocrawl_home_health.json" -TimeoutSec 1; if ($health.root -eq $previewRoot) { $ready=$true; break } } catch {}
        Start-Sleep -Milliseconds 150
    }
    if (-not $ready) { throw "Preview server failed. Read $stateDir/server.stderr.log" }
    $processId=$serverProcess.Id
} else { $processId=$null }
$url="http://127.0.0.1:$port/city-street124/"
@{url=$url;port=$port;processId=$processId;root=$previewRoot} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stateDir 'server-state.json') -Encoding UTF8
Write-Output $url
if (-not $NoBrowser) { Start-Process $url }
