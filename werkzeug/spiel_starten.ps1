# Stronghold einer Instanz starten - OHNE Fenster zu schieben (Daniel 19.10. 20:21: "kannst du bitte erst das starten_hinten
# ausschalten zukuenftig"; 20:16: "irgendwas forced alle 1-2 Sekunden jedes andere Fenster und damit auch die Taskleiste nach
# vorne"). Ursache: VillageStudio werkzeug/start_hinten.ps1 hebt bis zu 40 s nach dem Start immer wieder alle anderen Fenster
# ueber das Spiel (fuer Testlaeufe im Hintergrund gebaut). Gemessen 20:18: danach 0 Aenderungen der Fensterreihenfolge in 10 s.
# Dieses Skript startet nur: kein Schieben, kein Fokus-Zurueckgeben. Das Spiel kommt nach vorn wie bei einem normalen Start.
# Aufruf: powershell -ExecutionPolicy Bypass -File werkzeug\spiel_starten.ps1 -Instanz 4
param([int]$Instanz = 4)
. "$PSScriptRoot\..\..\VillageStudio\werkzeug\instanz.ps1"
$ordner = Get-InstanzOrdner $Instanz
if (-not (Test-Path $ordner)) { Write-Output "Instanz $Instanz fehlt: $ordner"; exit 1 }
# ein stehengebliebener Auftrag wuerde beim Start sofort feuern (wie in start_hinten.ps1) - ASCII, ohne BOM
[System.IO.File]::WriteAllText((Join-Path $ordner "ucp\villagestudio\befehl.json"), "{}", (New-Object System.Text.ASCIIEncoding))
$p = Start-Process -FilePath (Join-Path $ordner "Stronghold Crusader.exe") -ArgumentList "--ucp-no-security" -WorkingDirectory $ordner -PassThru
Write-Output ("Instanz {0} gestartet: Prozess {1} (ohne Fensterschieben)" -f $Instanz, $p.Id)
$log = Join-Path $ordner "ucp3.log"
$ende = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $ende) {
    if ((Test-Path $log) -and (Select-String -Path $log -Pattern "villagestudio aktiv" -Quiet)) {
        Write-Output "villagestudio aktiv"
        # 20:56 AUS: spielen_vorne.ps1 (Spiel "immer im Vordergrund") wird nicht mehr aufgerufen - Daniel: "es liegt an einem
        # Skript, das du gemacht hast, bitte ausschalten". Das Spiel startet wie bei einem normalen Start.
        exit 0
    }
    Start-Sleep -Milliseconds 500
}
Write-Output "villagestudio nach 60 s nicht aktiv - ucp3.log ansehen"
exit 2
