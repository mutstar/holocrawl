$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$m=Get-Content (Join-Path $root 'TRANSFER_MANIFEST.json') -Raw | ConvertFrom-Json
foreach($e in $m.files){$p=Join-Path $root $e.path;if(-not(Test-Path -LiteralPath $p)){throw "Missing $($e.path)"};if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne $e.sha256){throw "Mismatch $($e.path)"}}
Write-Host "Transfer files verified: $($m.files.Count)"
