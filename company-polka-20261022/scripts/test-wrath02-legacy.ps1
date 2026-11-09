param([string]$Binary='analysis/native/campaign-abilities01/wrath02-console02/abilities-engine.exe')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$source=Join-Path $projectRoot 'engine/campaign-crawl/crawl-ref/source'
$previous=Join-Path $projectRoot 'analysis/native/campaign-abilities01/combat-art01-console-final04'
$output=Join-Path $projectRoot 'analysis/native/wrath02/legacy-save'
if(Test-Path -LiteralPath $output){throw 'Legacy proof already exists.'}
New-Item -ItemType Directory -Path $output | Out-Null
foreach($name in @('HoloAbilities01.cs','expected-step.txt')){
 Copy-Item -LiteralPath (Join-Path $previous $name) -Destination (Join-Path $output $name)
}
$names=@('PATH','HOLOCRAWL_CAMPAIGN_TEST','HOLOCRAWL_CAMPAIGN_RELOAD','HOLOCRAWL_CAMPAIGN_OUTPUT','HOLOCRAWL_ENGINE_BENCH')
$saved=@{};foreach($name in $names){$saved[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
try {
 $env:PATH="$(Join-Path $projectRoot '.toolchain/msys64/mingw64/bin');$env:PATH"
 $env:HOLOCRAWL_CAMPAIGN_TEST='1';$env:HOLOCRAWL_CAMPAIGN_RELOAD='1'
 $env:HOLOCRAWL_CAMPAIGN_OUTPUT=$output;$env:HOLOCRAWL_ENGINE_BENCH=$null
 & (Join-Path $projectRoot $Binary) -dir $source -test holocrawl-campaign -no-throttle *> (Join-Path $output 'native.log')
 if($LASTEXITCODE){throw 'Legacy native save continuation failed.'}
 $proof=Get-Content -LiteralPath (Join-Path $output 'reload.json') -Raw | ConvertFrom-Json
 if($proof.status -ne 'passed' -or -not $proof.nextWorldStepExact){throw 'Missing legacy proof.'}
 @{status='passed';previousCheckpoint='combat-art01';legacyActiveWrath='noel';nativeCompanions=6;nextWorldStepExact=$true;binarySha256=(Get-FileHash -LiteralPath (Join-Path $projectRoot $Binary)).Hash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding utf8
} finally {foreach($name in $names){[Environment]::SetEnvironmentVariable($name,$saved[$name],'Process')}}
