# Wer schiebt Stronghold nach hinten? (Daniel 19.10. 21:00: "das vorderste Fenster wird nach vorne gehauen bzw. Stronghold
# nach hinten, sofort"). Das Vordergrund-Protokoll (vordergrund_protokoll.ps1) sah nur WELCHES Fenster vorn ist, nicht WER es
# dorthin gebracht hat. Hier meldet Windows selbst jeden Vordergrundwechsel und jedes Minimieren samt dem Thread, der es
# ausgeloest hat (SetWinEventHook, ausserhalb der fremden Prozesse) - daraus der ausloesende Prozess. Dazu alle 50 ms die
# Lage des Spielfensters: wie viele sichtbare Fenster darueber liegen und welche. Nur lesen, aendert nichts.
# Aufruf: powershell -File fenster_ereignisse.ps1 -Sekunden 90 -Instanz 4 -Pfad <datei>
param([int]$Sekunden = 90, [int]$Instanz = 4, [string]$Pfad = "$env:TEMP\fenster_ereignisse.txt")
$spiel = Get-Process | Where-Object { $_.Path -like $(if ($Instanz -eq 1) { '*Extreme\Stronghold Crusader.exe' } else { "*Instanz$Instanz\Stronghold Crusader.exe" }) } | Select-Object -First 1
if (-not $spiel) { Write-Output "Instanz $Instanz laeuft nicht"; exit 1 }
Add-Type @"
using System; using System.Text; using System.Diagnostics; using System.Runtime.InteropServices; using System.Collections.Generic;
public class FensterEreignisse {
  public delegate void CB(IntPtr hook, uint ev, IntPtr hwnd, int idObject, int idChild, uint thread, uint zeit);
  public delegate bool EnumCB(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern IntPtr SetWinEventHook(uint min, uint max, IntPtr mod, CB cb, uint pid, uint tid, uint flags);
  [DllImport("user32.dll")] static extern bool UnhookWinEvent(IntPtr h);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumCB cb, IntPtr l);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("kernel32.dll")] static extern IntPtr OpenThread(uint zugriff, bool erben, uint id);
  [DllImport("kernel32.dll")] static extern uint GetProcessIdOfThread(IntPtr t);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct MSG { public IntPtr h; public uint msg; public IntPtr w; public IntPtr l; public uint t; public int x; public int y; }
  [DllImport("user32.dll")] static extern bool PeekMessage(out MSG m, IntPtr h, uint a, uint b, uint entfernen);
  [DllImport("user32.dll")] static extern bool TranslateMessage(ref MSG m);
  [DllImport("user32.dll")] static extern IntPtr DispatchMessage(ref MSG m);
  public static List<string> Aus = new List<string>();
  static CB festhalten = Ereignis;
  static string Name(uint pid) { try { return Process.GetProcessById((int)pid).ProcessName; } catch { return "?" + pid; } }
  static string Fenster(IntPtr h) {
    uint p; GetWindowThreadProcessId(h, out p);
    var t = new StringBuilder(60); GetWindowText(h, t, 60); var k = new StringBuilder(40); GetClassName(h, k, 40);
    return Name(p) + " [" + k + "] '" + t + "'";
  }
  static void Ereignis(IntPtr hook, uint ev, IntPtr hwnd, int idObject, int idChild, uint thread, uint zeit) {
    if (idObject != 0 || hwnd == IntPtr.Zero) return;
    uint tp = 0; IntPtr th = OpenThread(0x0800, false, thread);
    if (th != IntPtr.Zero) { tp = GetProcessIdOfThread(th); CloseHandle(th); }
    string art = ev == 3 ? "VORDERGRUND" : ev == 0x16 ? "MINIMIERT" : ev == 0x17 ? "WIEDERHERGESTELLT" : ev.ToString("X");
    Aus.Add(DateTime.Now.ToString("HH:mm:ss.fff") + " " + art + " " + Fenster(hwnd) + " - ausgeloest von " + (tp == 0 ? "?" : Name(tp)));
  }
  static string Lage(uint spielPid) {
    var ueber = new List<string>(); string ergebnis = "Spielfenster nicht gefunden";
    EnumWindows((h, l) => {
      if (!IsWindowVisible(h)) return true;
      uint p; GetWindowThreadProcessId(h, out p);
      if (p == spielPid) { ergebnis = "Spiel " + (GetForegroundWindow() == h ? "VORN" : "nicht vorn") + ", darueber " + ueber.Count + ": " + string.Join(", ", ueber); return false; }
      var k = new StringBuilder(40); GetClassName(h, k, 40); ueber.Add(Name(p) + "/" + k); return true;
    }, IntPtr.Zero);
    return ergebnis;
  }
  public static void Lauf(int sekunden, uint spielPid) {
    var h1 = SetWinEventHook(3, 3, IntPtr.Zero, festhalten, 0, 0, 0);          // EVENT_SYSTEM_FOREGROUND, ausserhalb
    var h2 = SetWinEventHook(0x16, 0x17, IntPtr.Zero, festhalten, 0, 0, 0);    // MINIMIZESTART/-END
    var ende = DateTime.Now.AddSeconds(sekunden); string vorher = ""; MSG m;
    while (DateTime.Now < ende) {
      while (PeekMessage(out m, IntPtr.Zero, 0, 0, 1)) { TranslateMessage(ref m); DispatchMessage(ref m); }
      string l = Lage(spielPid);
      if (l != vorher) { Aus.Add(DateTime.Now.ToString("HH:mm:ss.fff") + " LAGE " + l); vorher = l; }
      System.Threading.Thread.Sleep(50);
    }
    UnhookWinEvent(h1); UnhookWinEvent(h2);
  }
}
"@
[FensterEreignisse]::Lauf($Sekunden, [uint32]$spiel.Id)
[FensterEreignisse]::Aus | Set-Content -Path $Pfad -Encoding UTF8
Write-Output ("{0} Eintraege -> {1}" -f [FensterEreignisse]::Aus.Count, $Pfad)
