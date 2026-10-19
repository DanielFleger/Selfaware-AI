# Taskleiste beim Spielen ausblenden (Daniel 19.10. 19:30: "es nervt, dass ich unten die Taskleiste hab - schoen, wenn die immer
# aus waere, aber nur beim Spielen").
# Gemessen 19:31: das Fenster von Instanz 4 ist schon randlos und bildschirmgross (0,0 - 2560x1440, Stil WS_POPUP), trotzdem lag
# die Taskleiste darueber. Erster Versuch "immer im Vordergrund" (HWND_TOPMOST): Bildschirmfoto 19:31 - Taskleiste weiter sichtbar,
# zurueckgenommen. Jetzt der Weg, den Windows dafuer vorsieht: ITaskbarList2::MarkFullscreenWindow - das Fenster gilt fuer die
# Taskleiste als Vollbild, sie blendet sich aus, solange es aktiv ist. Keine Windows-Einstellung wird geaendert, nur dieses eine
# Fenster markiert. Rueckweg: -Aus; ein Neustart des Spiels (neues Fenster) hebt es ohnehin auf.
# ERGEBNIS 19:32 (Bildschirmfoto der unteren 160 Pixel): auch mit der Markierung blieb die Taskleiste sichtbar, obwohl das
# Spielfenster das Vordergrundfenster war - WIRKT NICHT, zurueckgenommen (-Aus). Ursache nicht gefunden (Spiel laeuft erhoeht?).
# Aufruf: powershell -File spielen_vorne.ps1 -Instanz 4 [-Aus]
param([int]$Instanz = 4, [switch]$Aus)
. "$PSScriptRoot\..\..\VillageStudio\werkzeug\instanz.ps1"
if (-not ([System.Management.Automation.PSTypeName]'SpielVollbild').Type) {
    Add-Type @"
using System; using System.Runtime.InteropServices;
[ComImport, Guid("602D4995-B13A-429b-A66E-1935E44F4317"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface ITaskbarList2 {
  void HrInit(); void AddTab(IntPtr h); void DeleteTab(IntPtr h); void ActivateTab(IntPtr h); void SetActiveAlt(IntPtr h);
  void MarkFullscreenWindow(IntPtr h, [MarshalAs(UnmanagedType.Bool)] bool vollbild);
}
[ComImport, Guid("56FDF344-FD6D-11d0-958A-006097C9A090")] class TaskbarListKlasse {}
public class SpielVollbild {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr nach, int x, int y, int b, int hh, uint f);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public static void Markiere(IntPtr h, bool an) {
    var t = (ITaskbarList2)new TaskbarListKlasse();
    t.HrInit();
    t.MarkFullscreenWindow(h, an);
  }
}
"@
}
$h = Get-InstanzFenster $Instanz
if (-not $h) { Write-Output "kein Spielfenster fuer Instanz $Instanz"; exit 1 }
$h = [IntPtr]([long]($h | Select-Object -First 1))
# "immer im Vordergrund" aus dem ersten Versuch zuruecknehmen (HWND_NOTOPMOST, ohne Bewegen/Groesse)
[SpielVollbild]::SetWindowPos($h, [IntPtr](-2), 0, 0, 0, 0, 0x13) | Out-Null
[SpielVollbild]::Markiere($h, -not $Aus)
if (-not $Aus) { [SpielVollbild]::SetForegroundWindow($h) | Out-Null }
Write-Output ("Instanz {0}: fuer die Taskleiste Vollbild = {1}" -f $Instanz, (-not $Aus))
