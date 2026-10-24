# -*- coding: utf-8 -*-
"""Code-Kennung: ein kurzer Fingerabdruck ueber allen Code, der eine Partie steuert (Daniel 05.10. 20:46: "lass bitte als
Test immer sofort erkennen, ob es den neuen Test benutzt oder ob es noch einen alten benutzt - am besten mit einer
einmaligen Kennung").

Hineingerechnet werden:
  - jede Python-Datei aus werkzeug/, die erstes_spiel.py laden KANN: alle import-Anweisungen im Quelltext, auch die in
    Funktionen (der Planer laedt farmen_mischen erst spaeter), rekursiv - eine Liste, die man nicht pflegen muss;
  - die logik.lua der gewaehlten Instanz (befehl.SPIEL), die das Modul im Spiel laedt;
  - daten/ertrag_startwerte_*.json (Startwerte aendern das Spiel wie Code).
Gleicher Stand = gleiche Kennung; eine geaenderte Zeile irgendwo darin = andere Kennung. Zeilenenden zaehlen nicht.

Aufruf:  python kennung.py     -> Kennung des aktuellen Stands mit der Kennung je Datei
"""
import ast, hashlib, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
START = "erstes_spiel.py"


def python_dateien(start=START):
    """Alle Dateien aus werkzeug/, die start ueber import erreicht (rekursiv, auch Importe in Funktionen)."""
    gesehen, offen = set(), [start]
    while offen:
        f = offen.pop()
        if f in gesehen:
            continue
        gesehen.add(f)
        baum = ast.parse(open(os.path.join(HIER, f), encoding="utf-8").read())
        for knoten in ast.walk(baum):
            namen = []
            if isinstance(knoten, ast.Import):
                namen = [a.name.split(".")[0] for a in knoten.names]
            elif isinstance(knoten, ast.ImportFrom) and knoten.module and not knoten.level:
                namen = [knoten.module.split(".")[0]]
            for n in namen:
                if os.path.exists(os.path.join(HIER, n + ".py")):
                    offen.append(n + ".py")
    return sorted(gesehen)


def dateien():
    sys.path.insert(0, HIER)
    import befehl
    aus = [os.path.join(HIER, f) for f in python_dateien()]
    lua = (os.path.join(HIER,"logik_menue_backend.lua") if os.environ.get('SHC_GAME_PID') else
           os.path.join(befehl.SPIEL, "ucp", "villagestudio", "logik.lua"))
    if os.path.exists(lua):
        aus.append(lua)
    d = os.path.join(HIER, "..", "daten")
    aus += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.startswith("ertrag_startwerte_") and f.endswith(".json")]
    return aus


def kennung():
    """(kennung, {datei: kurz}) - Kennung = 8 Zeichen sha1 ueber Name und Inhalt aller Dateien."""
    gesamt, einzeln = hashlib.sha1(), {}
    for p in dateien():
        roh = open(p, "rb").read().replace(b"\r\n", b"\n")
        einzeln[os.path.basename(p)] = hashlib.sha1(roh).hexdigest()[:6]
        gesamt.update(os.path.basename(p).encode() + b"\0" + roh + b"\0")
    return gesamt.hexdigest()[:8], einzeln


def zeile():
    k, e = kennung()
    return "CODE-KENNUNG %s (%d Dateien: %s)" % (k, len(e), ", ".join("%s %s" % kv for kv in sorted(e.items())))


if __name__ == "__main__":
    print(zeile())
