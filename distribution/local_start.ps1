param([Parameter(Mandatory=$true)][string]$Game,[Parameter(Mandatory=$true)][string]$Runtime)
$ErrorActionPreference='Stop'
$gameRoot=[IO.Path]::GetFullPath($Game)
$runtimeRoot=[IO.Path]::GetFullPath($Runtime)
$state=[IO.Path]::GetDirectoryName($runtimeRoot)
$trace=[IO.Path]::Combine($state,'local-start.log')
try {
    $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $admin) {
        $elevate=[Diagnostics.ProcessStartInfo]::new()
        $elevate.FileName=[IO.Path]::Combine($env:SystemRoot,'System32\WindowsPowerShell\v1.0\powershell.exe')
        $elevate.Arguments='-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$PSCommandPath+'" -Game "'+$gameRoot+'" -Runtime "'+$runtimeRoot+'"'
        $elevate.UseShellExecute=$true;$elevate.Verb='runas';$elevate.WindowStyle='Hidden'
        [void][Diagnostics.Process]::Start($elevate)
        exit 0
    }
    [void][IO.Directory]::CreateDirectory($state)
    $deadline=[DateTime]::UtcNow.AddSeconds(30)
    $lease=$null
    while ($null -eq $lease) {
        try {$lease=[IO.File]::Open([IO.Path]::Combine($state,'local-start.lock'),'OpenOrCreate','ReadWrite','None')}
        catch [IO.IOException] {if ([DateTime]::UtcNow -gt $deadline) {throw 'Der vorherige Spielstart laeuft noch.'};[Threading.Thread]::Sleep(200)}
    }
    try {
        foreach($p in [Diagnostics.Process]::GetProcessesByName('Stronghold Crusader')) {
            try {$same=$p.MainModule.FileName -ieq [IO.Path]::Combine($gameRoot,'Stronghold Crusader.exe')} catch {$same=$false}
            if($same) {throw 'Diese Crusader-Spielkopie laeuft bereits. Bitte dort weiterspielen oder sie zuerst beenden.'}
        }
        $exe=[IO.Path]::Combine($gameRoot,'Stronghold Crusader.exe')
        if (-not [IO.File]::Exists($exe)) {throw 'Crusader wurde nicht gefunden.'}
        if (-not [IO.File]::Exists([IO.Path]::Combine($runtimeRoot,'python\python.exe'))) {throw 'Die lokale Selfaware-Laufzeit fehlt.'}
        $ipc=[IO.Path]::Combine($gameRoot,'ucp\villagestudio')
        [void][IO.Directory]::CreateDirectory($ipc)
        [IO.File]::WriteAllText([IO.Path]::Combine($ipc,'befehl.json'),'{}')
        $info=[Diagnostics.ProcessStartInfo]::new()
        $info.FileName=$exe;$info.Arguments='--ucp-no-security';$info.WorkingDirectory=$gameRoot
        $info.UseShellExecute=$true
        $started=[DateTime]::UtcNow
        $gameProcess=[Diagnostics.Process]::Start($info)
        [IO.File]::AppendAllText($trace,"Game started: $($gameProcess.Id); external runtime $runtimeRoot`r`n")
        $log=[IO.Path]::Combine($gameRoot,'ucp3.log');$ready=$false
        $deadline=[DateTime]::UtcNow.AddSeconds(30)
        while ([DateTime]::UtcNow -lt $deadline) {
            if($gameProcess.HasExited) {throw 'Crusader wurde vor dem Start der Spielanbindung beendet.'}
            if([IO.File]::Exists($log) -and [IO.File]::GetLastWriteTimeUtc($log) -ge $started) {
                $f=[IO.File]::Open($log,'Open','Read','ReadWrite')
                try {$reader=[IO.StreamReader]::new($f);$text=$reader.ReadToEnd()} finally {$f.Dispose()}
                if($text.Contains('Selfaware AI local development bridge ready')) {$ready=$true;break}
            }
            [Threading.Thread]::Sleep(200)
        }
        if(-not $ready) {throw 'Die lokale Selfaware-Spielanbindung ist nicht bereit. Bitte ucp3-error-log.log pruefen.'}
        & ([IO.Path]::Combine($PSScriptRoot,'bootstrap.ps1')) -Game $gameRoot -GamePid $gameProcess.Id -Runtime $runtimeRoot
    } finally {$lease.Dispose()}
} catch {
    [IO.File]::AppendAllText($trace,($_.ToString()+"`r`n"))
    [void][Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
    [void][Windows.Forms.MessageBox]::Show($_.ToString()+"`r`nProtokoll: "+$trace,'Selfaware AI: Startfehler')
    exit 1
}
