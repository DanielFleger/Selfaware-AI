param([string]$BuildType='Release',[string]$UCP3Path='')
$ErrorActionPreference='Stop'
& python "$PSScriptRoot\distribution\build_package.py"
if ($LASTEXITCODE -ne 0) { throw 'Selfaware runtime build failed' }
