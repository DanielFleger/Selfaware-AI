# -*- coding: utf-8 -*-
"""Eine gemessene Lage in data/research/lagen_belegt.json eintragen (Grundlage fuer bedrohung.bedarf).

Belegt ist die kleinste Gruppengroesse, die in ALLEN Wiederholungen gewonnen hat und ab der auch jede groessere
gemessene Groesse in allen Wiederholungen gewonnen hat (eine Luecke darueber wuerde die Zahl unsicher machen).
Der Fingerabdruck kommt aus der ersten Protokollrunde eines Laufs dieser Lage (alle Einheiten und Gebaeude);
dazu das Startleben der belegten Gruppe (die Gruppe war jeweils die gesuendeste).

Aufruf: uv run python -m selfaware.tools.analysis.lage_eintragen name="Trainingsstand 2026-10-06 T24521" ergebnis=a.json,b.json
"""

from selfaware import workspace as _workspace
import glob
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

from selfaware.services.bedrohung import LAGEN, fingerabdruck, lagen_laden

D = os.path.join(_workspace.DATA)


def erste_runde(protokoll):
    for z in open(os.path.join(D, protokoll), encoding="utf-8"):
        d = json.loads(z)
        if d.get("art") == "runde":
            return d
    raise RuntimeError("keine Runde in %s" % protokoll)


def belegte_mindestzahl(laeufe):
    je = {}
    for r in laeufe:
        je.setdefault(r["groesse"], []).append(r["sieg"])
    groessen = sorted(je)
    for i, g in enumerate(groessen):
        if all(all(je[h]) for h in groessen[i:]) and len(je[g]) >= 3:
            return g, {h: "%d/%d" % (sum(je[h]), len(je[h])) for h in groessen}
    return None, {h: "%d/%d" % (sum(je[h]), len(je[h])) for h in groessen}


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    laeufe = []
    for f in arg["ergebnis"].split(","):
        laeufe += json.load(open(os.path.join(D, f), encoding="utf-8"))["laeufe"]
    mindest, uebersicht = belegte_mindestzahl(laeufe)
    if mindest is None:
        raise SystemExit("keine belegte Mindestzahl: %s" % uebersicht)
    lauf = next(r for r in laeufe if r["groesse"] == mindest)
    r0 = erste_runde(lauf["protokoll"])
    L = {e["nr"]: e for e in r0["einheiten"]}
    G = {g["nr"]: g for g in r0["gebaeude"]}
    fa = fingerabdruck(L, G)
    gruppe_leben = sum(a["leben"] for a in r0["angreifer"])
    lagen = [l for l in lagen_laden() if l["name"] != arg["name"]]
    lagen.append({"name": arg["name"], "mindest": mindest, "gruppe_leben": gruppe_leben, "uebersicht": uebersicht,
                  "beleg": arg["ergebnis"], "fingerabdruck": fa})
    json.dump(lagen, open(LAGEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("eingetragen: %s -> mindest %d (Gruppenleben %d), Uebersicht %s" % (arg["name"], mindest, gruppe_leben, uebersicht))
    print("Fingerabdruck:", json.dumps(fa, ensure_ascii=False))


if __name__ == "__main__":
    main()
