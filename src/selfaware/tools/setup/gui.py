# -*- coding: utf-8 -*-
"""UCP3-GUI oeffnen und schliessen - mit eingebautem Test.

Warum es das gibt: Die UCP3-GUI schreibt ihren eigenen Stand in die
ucp-config.yml, sobald man aus ihr das Spiel startet (gemessen am 30.09.2026:
Config-Aenderung 20:21:34 = Spielstart aus der GUI, auf die Sekunde). Dabei
fliegt unser Modul 'villagestudio' heraus. Deshalb muss die GUI zu sein, bevor
wir testen - und das soll nie wieder Handarbeit sein.

Aufruf:
  uv run python -m selfaware.tools.setup.gui status       zeigt GUI, Spiel und Config-Zustand
  uv run python -m selfaware.tools.setup.gui schliessen   bittet die GUI zu schliessen und prueft, ob es geklappt hat
  uv run python -m selfaware.tools.setup.gui oeffnen      startet die GUI und prueft, dass die Config unberuehrt bleibt

Rueckgabe: 0 = geschafft, 1 = nicht geschafft (der Grund steht in der Ausgabe).
Erzwungen wird NIE: ein hartes Beenden wuerde ungespeicherte Aenderungen in der
GUI verwerfen. Klemmt sie, meldet das Werkzeug den Grund und hoert auf.
"""
import hashlib, os, subprocess, sys, time

GUI_EXE = os.path.expandvars(r"%LOCALAPPDATA%\UCP3-GUI\UCP3-GUI.exe")
CONFIG  = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme\ucp-config.yml"
WARTE   = 15  # Sekunden, die die GUI zum Schliessen bekommt


def ps(befehl):
    return subprocess.run(["powershell", "-NoProfile", "-Command", befehl],
                          capture_output=True, text=True, errors="replace").stdout.strip()


def gui_pids():
    aus = ps("(Get-Process -Name 'UCP3-GUI' -ErrorAction SilentlyContinue).Id")
    return [int(z) for z in aus.split() if z.strip().isdigit()]


def spiel_info():
    aus = ps("$p = Get-Process -Name 'Stronghold Crusader' -ErrorAction SilentlyContinue | "
             "Select-Object -First 1; if ($p) { '{0}|{1}' -f $p.Id, [bool]$p.Path }")
    if "|" not in aus:
        return None
    pid, lesbar = aus.split("|")
    return int(pid), lesbar.strip() == "True"


def config_zustand():
    daten = open(CONFIG, "rb").read()
    return (daten.count(b"villagestudio"),
            hashlib.sha256(daten).hexdigest()[:16],
            time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(CONFIG))))


def zeige_status():
    pids = gui_pids()
    print("GUI:    " + ("laeuft (PID %s)" % ", ".join(map(str, pids)) if pids else "geschlossen"))
    sp = spiel_info()
    if sp is None:
        print("Spiel:  laeuft nicht")
    else:
        print("Spiel:  laeuft (PID %d) - %s" % (sp[0], "gleiche Rechtestufe wie diese Sitzung" if sp[1]
              else "hoehere Rechtestufe - beenden mit src/selfaware/tools/setup/spiel.py (erhoehter Helfer, M2.11)"))
    n, h, t = config_zustand()
    print("Config: %d x villagestudio (soll 3), zuletzt geschrieben %s, Pruefsumme %s" % (n, t, h))
    return pids


def schliessen():
    pids = gui_pids()
    if not pids:
        print("GESCHAFFT: die GUI war schon geschlossen.")
        return 0
    vorher = config_zustand()
    # freundlich bitten: CloseMainWindow schickt dieselbe Nachricht wie ein Klick aufs X
    ps("Get-Process -Name 'UCP3-GUI' -ErrorAction SilentlyContinue | "
       "ForEach-Object { [void]$_.CloseMainWindow() }")
    ende = time.time() + WARTE
    while time.time() < ende and gui_pids():
        time.sleep(0.5)
    rest = gui_pids()
    nachher = config_zustand()
    if nachher[1] != vorher[1]:
        print("WARNUNG: die GUI hat beim Schliessen die Config geschrieben "
              "(%d -> %d x villagestudio)." % (vorher[0], nachher[0]))
    if rest:
        print("NICHT GESCHAFFT: die GUI laeuft nach %d s noch (PID %s)." % (WARTE, ", ".join(map(str, rest))))
        print("Wahrscheinlichster Grund: ein offener Dialog, z. B. 'ungespeicherte Aenderungen'.")
        print("Nicht erzwungen, damit nichts verloren geht - Daniel entscheidet.")
        return 1
    print("GESCHAFFT: die GUI ist geschlossen (%d Prozess(e) beendet), "
          "Config %s." % (len(pids), "unveraendert" if nachher[1] == vorher[1] else "VERAENDERT"))
    return 0


def oeffnen():
    if gui_pids():
        print("GESCHAFFT: die GUI laeuft schon.")
        return 0
    if not os.path.exists(GUI_EXE):
        print("NICHT GESCHAFFT: GUI nicht gefunden unter %s" % GUI_EXE)
        return 1
    vorher = config_zustand()
    subprocess.Popen([GUI_EXE], close_fds=True)
    ende = time.time() + 30
    while time.time() < ende and not gui_pids():
        time.sleep(0.5)
    if not gui_pids():
        print("NICHT GESCHAFFT: nach 30 s kein GUI-Prozess.")
        return 1
    time.sleep(10)  # der GUI Zeit geben, eine Config zu schreiben, falls sie es beim Oeffnen tut
    nachher = config_zustand()
    print("GESCHAFFT: die GUI ist offen. Config nach 10 s: %s (%d x villagestudio)."
          % ("unveraendert" if nachher[1] == vorher[1] else "VERAENDERT - beim Oeffnen geschrieben!", nachher[0]))
    print("Achtung: das Spiel NICHT aus der GUI starten - dabei faellt villagestudio aus der Config.")
    return 0


if __name__ == "__main__":
    was = sys.argv[1] if len(sys.argv) > 1 else "status"
    if was == "status":
        zeige_status(); sys.exit(0)
    if was == "schliessen":
        sys.exit(schliessen())
    if was == "oeffnen":
        sys.exit(oeffnen())
    print(__doc__); sys.exit(2)
