# -*- coding: utf-8 -*-
"""Einen Befehl an unser Modul schicken und die Antwort aus dem Log lesen.

Die Nummern-Regel ist fest eingebaut (Meilenstein M2.03): Das Modul
ueberspringt jeden Befehl, dessen 'id' es schon kennt. Darum vergibt dieses
Werkzeug jede Nummer nur einmal - stetig steigend ueber alle Laeufe hinweg,
die letzte vergebene steht in .letzte_id neben diesem Skript.

Aufruf:    python befehl.py '<json>' [wartesekunden]
Beispiel:  python befehl.py '{"player": 1, "tempo": 90}' 3
Als Baustein:  from befehl import sende; zeilen = sende({"zeit": True})

Zwei Spielinstanzen (05.10.2026): SHC_INSTANZ=2 waehlt die Spielkopie
"<Instanz 1> Instanz2" - mit eigener befehl.json, eigenem ucp3.log, eigener
Kanalsperre (.lauf2) und eigenem Nummernzaehler (.letzte_id2). Ohne Angabe gilt
Instanz 1, alles wie bisher. Dieselbe Ordner-Regel steht in
VillageStudio/werkzeug/instanz.py (spiel.py prueft, dass beide gleich sind). Andere Werkzeuge nehmen
SPIEL und ABZUG von hier, nie einen eigenen Pfad - sonst liest ein Lauf auf
Instanz 2 still die Lagebilder von Instanz 1.
"""
import io, json, os, re, sys, time

_ROH = os.environ.get("SHC_INSTANZ", "").strip() or "1"
if not _ROH.isdigit() or int(_ROH) < 1:
    raise RuntimeError("SHC_INSTANZ=%r ist keine Instanznummer (1, 2, ...)" % _ROH)
INSTANZ = int(_ROH)
_STAMM = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme"
SPIEL  = _STAMM if INSTANZ == 1 else "%s Instanz%d" % (_STAMM, INSTANZ)
if not os.path.isdir(SPIEL):
    raise RuntimeError("Instanz %d gibt es nicht: %s" % (INSTANZ, SPIEL))
_ENDUNG = "" if INSTANZ == 1 else str(INSTANZ)
BEFEHL = os.path.join(SPIEL, "ucp", "villagestudio", "befehl.json")
LOG    = os.path.join(SPIEL, "ucp3.log")
ABZUG  = os.path.join(SPIEL, "ucp", "villagestudio", "abzug")
MERKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".letzte_id" + _ENDUNG)


def neue_id():
    try:
        letzte = int(io.open(MERKER).read().strip())
    except (OSError, ValueError):
        letzte = 0
    nummer = max(int(time.time()), letzte + 1)
    io.open(MERKER, "w").write(str(nummer))
    return nummer


STRENG = False   # True (z. B. im Lenker): Modulfehler in der Antwort brechen sofort laut ab (Daniel 23:48)
# Lua-Fehler meldet das Modul als "logik: <ort>:<zeile>: <text>" (pcall), eine Befehlsliste mit
# "logik: <gut> von <alle> Befehlen ausgefuehrt" - weniger gut als alle heisst: mindestens einer ist gescheitert.
# Anlass 04.10.2026: eine globale Variable liess jeden Angriffsbefehl scheitern, vier Partien lang unbemerkt.
LUA_FEHLER = re.compile(r"logik: .*:\d+: ")
BILANZ = re.compile(r"logik: (\d+) von (\d+) Befehlen ausgefuehrt")

def pruefe(zeilen):
    for z in zeilen:
        b = BILANZ.search(z)
        if LUA_FEHLER.search(z) or (b and int(b.group(1)) < int(b.group(2))):
            raise RuntimeError("MODULFEHLER (Antwort des Moduls): " + z[:240])
    return zeilen

LAUF = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lauf" + _ENDUNG)   # Kanal belegt: "<pid>" - der Lenker frischt sie je Runde auf; je Instanz eine

def belege():
    """Der Lenker meldet sich als Besitzer des Kanals (je Runde aufrufen). 05.10.: eine Nebenabfrage aus einem zweiten
    Prozess lief mitten in Partie 9f in den Kanal - zwei Schreiber auf befehl.json verlieren Befehle."""
    io.open(LAUF, "w").write(str(os.getpid()))

def freigeben():
    try:
        if io.open(LAUF).read().strip() == str(os.getpid()):
            os.remove(LAUF)
    except OSError:
        pass

def _kanal_frei():
    try:
        pid = io.open(LAUF).read().strip()
        alter = time.time() - os.path.getmtime(LAUF)
    except OSError:
        return
    if pid != str(os.getpid()) and alter < 15:
        raise RuntimeError("KANAL BELEGT: ein Lauf (Prozess %s) benutzt den Befehlskanal von Instanz %d gerade (vor %.0f s gemeldet)" % (pid, INSTANZ, alter))

def sende(befehl, warte=3.0, bis=None):
    """Schickt den Befehl (dict) und gibt die neuen Modul-Logzeilen zurueck.
    bis = Text, auf den gewartet wird (alle 20 ms nachsehen, hoechstens <warte> s) - statt fest zu warten
    (04.10.2026: feste Wartezeit machte eine Lenker-Runde 1,1 s lang)."""
    _kanal_frei()
    # Lord-Sperre fuer jeden Befehlsweg (lordschutz.py; Daniels Regeln 11.10. 16:11 und 16:41)
    import lordschutz
    befehl, meld = lordschutz.filtern(befehl)
    for m in meld:
        print(m, flush=True)
    if befehl is None:
        return meld
    befehl = dict(befehl)
    befehl["id"] = neue_id()
    vorher = os.path.getsize(LOG)
    io.open(BEFEHL, "wb").write(json.dumps(befehl).encode("utf-8"))
    if bis is None:
        # Daniel 05.10. 23:01: "loesch das feste Zeit-Warten - Sekunden sind Killer". Die Logik quittiert jeden Befehl mit
        # "QUITTUNG <id>" (gleicher Tick); warte ist nur noch die Notbremse, falls keine Quittung kommt (z. B. Hauptmenue).
        bis = "QUITTUNG %s" % befehl["id"]
    ende = time.time() + warte
    while time.time() < ende:
        time.sleep(0.02)
        if os.path.getsize(LOG) > vorher:
            with io.open(LOG, encoding="utf-8", errors="replace") as f:
                f.seek(vorher)
                if bis in f.read():
                    break
    with io.open(LOG, encoding="utf-8", errors="replace") as f:
        f.seek(vorher)
        neu = f.read()
    zeilen = [z.split("| ", 1)[-1].strip() for z in neu.splitlines()
              if "villagestudio" in z and "ZUSTAND" not in z]
    return pruefe(zeilen) if STRENG else zeilen


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    zeilen = sende(json.loads(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 3.0)
    for z in zeilen:
        print(z)
    if not zeilen:
        print("(keine Antwort im Log)")
        sys.exit(1)
