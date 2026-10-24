param([Parameter(Mandatory=$true)][string]$Game,[Parameter(Mandatory=$true)][int]$GamePid,
      [Parameter(Mandatory=$true)][string]$Runtime,[ValidateSet('file','memory')][string]$Transport='file')
$ErrorActionPreference='Stop'
$gameRoot=[IO.Path]::GetFullPath($Game)
$state=[IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Runtime))
[void][IO.Directory]::CreateDirectory($state)
$trace=[IO.Path]::Combine($state,"bootstrap-$GamePid.log")
try {
    [IO.File]::AppendAllText($trace,"Bootstrap started for game $GamePid`r`n")
    $runtime=[IO.Path]::GetFullPath($Runtime)
    $version=[IO.Path]::GetFileName($runtime)
    if (-not [IO.File]::Exists([IO.Path]::Combine($runtime,'ready'))) { throw 'External runtime is not installed; run local setup first' }
    $env:SHC_GAME_DIR=$gameRoot
    $env:SHC_GAME_PID=[string]$GamePid
    $env:SHC_TRANSPORT=$Transport
    $env:SHC_STATE_DIR=$state
    $env:SHC_PARTNER='ja'
    $env:SHC_STEUERE_MENSCH='nein'
    $env:SHC_START_LOG=[IO.Path]::Combine($state,"worker-$GamePid.log")
    $python=[IO.Path]::Combine($runtime,'python\python.exe')
    $script=[IO.Path]::Combine($runtime,'Selfaware-AI\werkzeug\runtime_start.py')
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=$python
    $info.Arguments='-u "'+$script+'"'
    $info.UseShellExecute=$false
    $info.CreateNoWindow=$true
    $info.WorkingDirectory=[IO.Path]::GetDirectoryName($script)
    $worker=[Diagnostics.Process]::Start($info)
    [IO.File]::AppendAllText($trace,"Worker started: $($worker.Id), runtime $version`r`n")
    $worker.WaitForExit()
    if ($worker.ExitCode -ne 0) { throw "Controller exited with $($worker.ExitCode); see $($env:SHC_START_LOG)" }
} catch {
    [IO.File]::AppendAllText($trace,($_.ToString()+"`r`n"))
    throw
}
