param([Parameter(Mandatory=$true)][string]$Game,[Parameter(Mandatory=$true)][int]$GamePid)
$ErrorActionPreference='Stop'
$gameRoot=[IO.Path]::GetFullPath($Game)
$gameKey=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($gameRoot.ToLowerInvariant())))).Replace('-','').Substring(0,16)
$state=[IO.Path]::Combine($env:LOCALAPPDATA,"Selfaware AI\$gameKey")
[void][IO.Directory]::CreateDirectory($state)
$trace=[IO.Path]::Combine($state,"bootstrap-$GamePid.log")
try {
    [IO.File]::AppendAllText($trace,"Bootstrap started for game $GamePid`r`n")
    $archive=[IO.Path]::Combine($gameRoot,'ucp\villagestudio\runtime.zip')
    $stream=[IO.File]::OpenRead($archive)
    try { $version=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($stream))).Replace('-','').Substring(0,16) }
    finally { $stream.Dispose() }
    $runtime=[IO.Path]::Combine($state,$version)
    $lock=[IO.File]::Open([IO.Path]::Combine($state,'bootstrap.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    try {
        if (-not [IO.File]::Exists([IO.Path]::Combine($runtime,'ready'))) {
            if ([IO.Directory]::Exists($runtime)) { throw 'Incomplete runtime exists; preserving it for diagnosis' }
            [void][Reflection.Assembly]::LoadWithPartialName('System.IO.Compression.FileSystem')
            [IO.Compression.ZipFile]::ExtractToDirectory($archive,$runtime)
            [IO.File]::WriteAllText([IO.Path]::Combine($runtime,'ready'),$version)
        }
    } finally { $lock.Dispose() }
    $env:SHC_GAME_DIR=$gameRoot
    $env:SHC_GAME_PID=[string]$GamePid
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
    exit 1
}
