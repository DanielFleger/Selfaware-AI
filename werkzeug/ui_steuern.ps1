# Spielfenster per Skript bedienen (Daniel 19.10. 20:31: "spiel starten im Menue klicken bzw. es wie klicken per Skript bis du ins
# Menue kommst, dann nach Ratte schauen, diese auswaehlen, Map auswaehlen, Platz auswaehlen und dann Spiel starten").
# Geht nur, wenn das Spiel NICHT mit Administratorrechten laeuft (gemessen 20:32: mit spiel_starten.ps1 gestartet -> Pfad lesbar,
# also nicht erhoeht). Bewegt Daniels Maus.
#   -Aktion foto  [-Pfad x.png]          Bild des Hauptschirms, halbe Groesse (Klick-Koordinaten = Bildpunkt x 2)
#   -Aktion klick -X 100 -Y 200          Linksklick an Bildschirmpunkt (volle Aufloesung)
#   -Aktion taste -Text "{ENTER}"        Taste(n) an das Spielfenster (SendKeys-Schreibweise)
param([string]$Aktion = "foto", [int]$X = 0, [int]$Y = 0, [string]$Text = "", [string]$Pfad = "", [int]$Instanz = 4)
. "$PSScriptRoot\..\..\VillageStudio\werkzeug\instanz.ps1"
if (-not ([System.Management.Automation.PSTypeName]'UiSteuer').Type) {
    Add-Type @"
using System; using System.Runtime.InteropServices;
public class UiSteuer {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, IntPtr e);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr p);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool an);
}
"@
}
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
function Vorne {
    $h = [IntPtr]([long](Get-InstanzFenster $Instanz | Select-Object -First 1))
    if ($h -eq [IntPtr]::Zero) { return }
    if ([UiSteuer]::GetForegroundWindow() -eq $h) { return }
    $v = [UiSteuer]::GetWindowThreadProcessId([UiSteuer]::GetForegroundWindow(), [IntPtr]::Zero)
    $m = [UiSteuer]::GetCurrentThreadId()
    $a = [UiSteuer]::AttachThreadInput($m, $v, $true)
    [void][UiSteuer]::SetForegroundWindow($h)
    if ($a) { [void][UiSteuer]::AttachThreadInput($m, $v, $false) }
    Start-Sleep -Milliseconds 300
}
switch ($Aktion) {
    "foto" {
        $b = New-Object System.Drawing.Bitmap 2560, 1440
        $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0, 0, 0, 0, $b.Size); $g.Dispose()
        $k = New-Object System.Drawing.Bitmap $b, 1280, 720
        if (-not $Pfad) { $Pfad = Join-Path $env:TEMP "ui_foto.png" }
        $k.Save($Pfad, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose(); $k.Dispose()
        Write-Output $Pfad
    }
    "klick" {
        Vorne
        [void][UiSteuer]::SetCursorPos($X, $Y); Start-Sleep -Milliseconds 120
        [UiSteuer]::mouse_event(0x2, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 60
        [UiSteuer]::mouse_event(0x4, 0, 0, 0, [IntPtr]::Zero)
        Write-Output "Klick ($X,$Y)"
    }
    "taste" {
        Vorne
        [System.Windows.Forms.SendKeys]::SendWait($Text)
        Write-Output "Taste $Text"
    }
}
