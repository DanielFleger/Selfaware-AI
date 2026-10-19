# -*- coding: utf-8 -*-
"""Nachschau gegen einen echten Gegner (SAI 11.10., Daniel: "jede kleinste Instabilitaet soll in die Entscheidung
einspielen"; Frage-Agent 16:02: die Lageprotokolle der Nomade-Laeufe sind schon da - erst auswerten, dann bauen).

Liest ein Lageprotokoll (data/research/lage_*.jsonl.gz, jede Runde der volle Abzug) und gibt je Zeitschritt aus:
  - Gegner-Lord: Ort und Leben; seine Wache = Gegner-Truppen bis 15 / bis 45 Felder um den Lord
  - Gegner-Truppen gesamt und davon in unserem Gebiet (bis 40 Felder um unseren Bergfried)
  - unsere Truppen, unsere Gebaeude, unser Lord-Leben, brennende Menschen (Typ 2) bei uns
Zum Schluss das Fenster mit der schwaechsten Wache (Kandidat fuer den fruehen Lord-Schlag).
Gezaehlt wird nach Art und Ort je Runde, nicht nach Nummer: Nummern werden neu vergeben (1011k: 300 von 484).
Aufruf: uv run python -m selfaware.tools.analysis.nomade_nachschau <protokoll.jsonl.gz> [schritt=1000] [wir=1] [gegner=2] [bergfried=141,269]"""
import sys

from selfaware.telemetry.lageprotokoll import runden
from selfaware.micro.tasks.waechter import TRUPPE, LORD

KAMPF = TRUPPE - {LORD}
BRENNENDER = 2


def abstand(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def auswerten(pfad, schritt=1000, wir=1, gegner=2, bergfried=(141, 269)):
    zeilen, naechste, schwach = [], 0, None
    for t, st, E, G in runden(pfad):
        lord_g = next((e for e in E if e["besitzer"] == gegner and e["typ"] == LORD), None)
        lord_w = next((e for e in E if e["besitzer"] == wir and e["typ"] == LORD), None)
        feind = [e for e in E if e["besitzer"] == gegner and e["typ"] in KAMPF]
        z = {"t": t, "lord_g": (lord_g["x"], lord_g["y"], lord_g["leben"]) if lord_g else None,
             "lord_w": lord_w["leben"] if lord_w else None, "feind": len(feind),
             "bei_uns": sum(1 for e in feind if abstand((e["x"], e["y"]), bergfried) <= 40),
             "wir_truppe": sum(1 for e in E if e["besitzer"] == wir and e["typ"] in KAMPF),
             "wir_geb": sum(1 for g in G if g["besitzer"] == wir),
             "brennend_bei_uns": sum(1 for e in E if e["typ"] == BRENNENDER and abstand((e["x"], e["y"]), bergfried) <= 40)}
        if lord_g:
            lp = (lord_g["x"], lord_g["y"])
            z["wache15"] = sum(1 for e in feind if abstand((e["x"], e["y"]), lp) <= 15)
            z["wache45"] = sum(1 for e in feind if abstand((e["x"], e["y"]), lp) <= 45)
            if t >= 2000 and (schwach is None or z["wache45"] < schwach["wache45"]):
                schwach = dict(z)
        if t >= naechste:
            zeilen.append(z)
            naechste = t + schritt
    return zeilen, schwach, z


def main():
    pfad = sys.argv[1]
    arg = dict(a.split("=", 1) for a in sys.argv[2:])
    bx, by = map(int, arg.get("bergfried", "141,269").split(","))
    zeilen, schwach, letzte = auswerten(pfad, int(arg.get("schritt", 1000)), int(arg.get("wir", 1)),
                                        int(arg.get("gegner", 2)), (bx, by))
    print("Tick   | Gegner-Lord (x,y,Leben)  Wache<=15 <=45 | Gegner-Truppen ges. / bei uns | wir: Truppen Gebaeude Lord-Leben brennend")
    for z in zeilen + ([letzte] if letzte is not zeilen[-1] else []):
        print("%6d | %-24s %5s %5s | %6d / %4d | %5d %5d %8s %3d" % (
            z["t"], z["lord_g"], z.get("wache15", "-"), z.get("wache45", "-"), z["feind"], z["bei_uns"],
            z["wir_truppe"], z["wir_geb"], z["lord_w"], z["brennend_bei_uns"]))
    if schwach:
        print("Schwaechste Wache ab Tick 2.000: Tick %d, %d bis 15 / %d bis 45 Felder, Lord %s, Gegner gesamt %d, bei uns %d" % (
            schwach["t"], schwach["wache15"], schwach["wache45"], schwach["lord_g"], schwach["feind"], schwach["bei_uns"]))


if __name__ == "__main__":
    main()
