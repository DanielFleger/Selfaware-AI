param([string]$Game='')
$ErrorActionPreference='Stop'
if(-not $Game) {
    [void][Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
    $dialog=[Windows.Forms.FolderBrowserDialog]::new()
    $dialog.Description='Crusader-Spielordner fuer Selfaware AI auswaehlen (lokale Entwicklungsfassung)'
    if($dialog.ShowDialog() -ne 'OK') {exit 0}
    $Game=$dialog.SelectedPath
}
$gameRoot=[IO.Path]::GetFullPath($Game)
if(-not [IO.File]::Exists([IO.Path]::Combine($gameRoot,'Stronghold Crusader.exe'))) {throw 'Kein Crusader-Spielordner'}
$admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if(-not $admin) {
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=[IO.Path]::Combine($env:SystemRoot,'System32\WindowsPowerShell\v1.0\powershell.exe')
    $info.Arguments='-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$PSCommandPath+'" -Game "'+$gameRoot+'"'
    $info.UseShellExecute=$true;$info.Verb='runas';$info.WindowStyle='Hidden'
    $child=[Diagnostics.Process]::Start($info);$child.WaitForExit();exit $child.ExitCode
}
$archive=[IO.Path]::Combine($PSScriptRoot,'runtime.zip')
$key=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($gameRoot.ToLowerInvariant())))).Replace('-','').Substring(0,16)
$stream=[IO.File]::OpenRead($archive)
try {$version=([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($stream))).Replace('-','').Substring(0,16)} finally {$stream.Dispose()}
$runtime=[IO.Path]::Combine([Environment]::GetFolderPath('MyDocuments'),"Selfaware AI\$key\$version")
$legacy=[IO.Path]::Combine([Environment]::GetFolderPath('LocalApplicationData'),"Selfaware AI\$key\$version")
if(-not [IO.File]::Exists([IO.Path]::Combine($runtime,'ready'))) {
    if([IO.Directory]::Exists($runtime)) {throw 'Unvollstaendige Laufzeit vorhanden; fuer Diagnose erhalten.'}
    [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($runtime))
    if([IO.File]::Exists([IO.Path]::Combine($legacy,'ready'))) {
        Copy-Item -LiteralPath $legacy -Destination $runtime -Recurse
    } else {
        [void][Reflection.Assembly]::LoadWithPartialName('System.IO.Compression.FileSystem')
        [IO.Compression.ZipFile]::ExtractToDirectory($archive,$runtime)
        [IO.File]::WriteAllText([IO.Path]::Combine($runtime,'ready'),$version)
    }
}
& ([IO.Path]::Combine($runtime,'python\python.exe')) ([IO.Path]::Combine($PSScriptRoot,'local_setup.py')) $gameRoot --packages $PSScriptRoot
if($LASTEXITCODE -ne 0) {throw 'Lokale Selfaware-Einrichtung fehlgeschlagen'}
