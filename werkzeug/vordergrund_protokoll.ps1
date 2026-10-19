# Wer holt sich das aktive Fenster? (Daniel 19.10. 20:46: "wenn es vorne ist, ist offensichtlich ein Programm von dir offen,
# dass es nach vorne holt - normalerweise ist es naemlich nicht vorne"). Schreibt jeden Wechsel des Vordergrundfensters mit
# Prozess und Titel, dazu neu gestartete Prozesse. Nur lesen, aendert nichts.
# Aufruf: powershell -File vordergrund_protokoll.ps1 -Sekunden 60 -Pfad <datei>
param([int]$Sekunden = 60, [string]$Pfad = "$env:TEMP\vordergrund.txt")
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class Vg {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
}
"@
$aus = New-Object System.Collections.Generic.List[string]
$vorher = $null
$bekannt = @{}; Get-Process | ForEach-Object { $bekannt[$_.Id] = 1 }
$ende = (Get-Date).AddSeconds($Sekunden)
while ((Get-Date) -lt $ende) {
    $h = [Vg]::GetForegroundWindow(); $p = 0; [void][Vg]::GetWindowThreadProcessId($h, [ref]$p)
    $sb = New-Object System.Text.StringBuilder 200; [void][Vg]::GetWindowText($h, $sb, 200)
    $name = (Get-Process -Id $p -ErrorAction SilentlyContinue).ProcessName
    $z = "$name | $($sb.ToString())"
    if ($z -ne $vorher) { $t = Get-Date -Format "HH:mm:ss.fff"; $aus.Add("$t VORN $z"); $vorher = $z }
    foreach ($q in Get-Process) { if (-not $bekannt.ContainsKey($q.Id)) { $bekannt[$q.Id] = 1; $t = Get-Date -Format "HH:mm:ss.fff"; $aus.Add("$t NEU  $($q.ProcessName) ($($q.Id))") } }
    Start-Sleep -Milliseconds 100
}
$aus | Set-Content -Path $Pfad -Encoding UTF8
Write-Output ("{0} Eintraege -> {1}" -f $aus.Count, $Pfad)
