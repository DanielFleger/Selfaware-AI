param([Parameter(Mandatory=$true)][string]$Game,[Parameter(Mandatory=$true)][int]$GamePid)
$ErrorActionPreference='Stop'
$gameRoot=[IO.Path]::GetFullPath($Game)
$gameKey=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($gameRoot.ToLowerInvariant())))).Replace('-','').Substring(0,16)
$state=Join-Path $env:LOCALAPPDATA "Selfaware AI\$gameKey"
New-Item -ItemType Directory -Path $state -Force | Out-Null
try {
    $archive=Join-Path $gameRoot 'ucp\villagestudio\runtime.zip'
    $stream=[IO.File]::OpenRead($archive)
    try { $version=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($stream))).Replace('-','').Substring(0,16) }
    finally { $stream.Dispose() }
    $runtime=Join-Path $state $version
    $lock=[IO.File]::Open((Join-Path $state 'bootstrap.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    try {
        if (-not (Test-Path -LiteralPath (Join-Path $runtime 'ready'))) {
            if (Test-Path -LiteralPath $runtime) { throw 'Incomplete runtime exists; preserving it for diagnosis' }
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [IO.Compression.ZipFile]::ExtractToDirectory($archive,$runtime)
            [IO.File]::WriteAllText((Join-Path $runtime 'ready'),$version)
        }
    } finally { $lock.Dispose() }
    $env:SHC_GAME_DIR=$gameRoot
    $env:SHC_GAME_PID=[string]$GamePid
    $env:SHC_PARTNER='ja'
    $env:SHC_STEUERE_MENSCH='nein'
    $python=Join-Path $runtime 'python\python.exe'
    $script=Join-Path $runtime 'Selfaware-AI\werkzeug\runtime_start.py'
    & $python -u $script *>> (Join-Path $state 'start.log')
    if ($LASTEXITCODE -ne 0) { throw "Controller exited with $LASTEXITCODE" }
} catch {
    $_ | Out-String | Add-Content -LiteralPath (Join-Path $state 'startfehler.log')
    exit 1
}
