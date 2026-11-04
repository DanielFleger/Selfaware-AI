# -*- coding: utf-8 -*-
"""Trefferfenster und Teamregel direkt im Spiel: processEntityDamageToUnit 00531920 auf Instanz 2 rufen, Geschoss und Einheit vorher gesetzt.

Widerlegt das Modell: ein Treffer ausserhalb des Fensters, kein Treffer darin, ein Freund, der entgegen der Regel getroffen oder verschont wird. Schreibt nur in eine Probe-Einheit und einen freien Geschoss-Platz, stellt beides wieder her. Nichts davon geht in SamurAI.
Ausgabe: fenster_rufen.txt.
"""
import collections
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import flug_modell as fm  # noqa: E402
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte  # noqa: E402
from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz  # noqa: E402
from selfaware.tools.experiments.spielcode_rufen import Rufer  # noqa: E402

K = Feldkarte.laden(feldliste=FELDLISTE)
UNITS = 0x1387F38
TREFFER = 0x531920
U_F = ["unitType", "owner", "buildingHeight", "terrainOrClimbHeight", "health", "maxHealth", "dying", "tribeID", "logicalState"]
E_F = ["entityType", "height", "owner", "unitID_OR_seaGullID", "logicalState", "startingHeight", "targetZ", "velocityUnk", "field90_0xd0"]
ARTEN_ZIEL = [24, 22, 39, 40, 41, 58, 59, 60, 61, 77]


def main():
    aus = []
    with Rufer(pid_der_instanz(2)) as r:
        da = K.adresse("DAT_UnitsState", "units[].logicalState")
        lebend = [i for i in range(1, 2400) if r.lies_i(da[0] + i * da[2], da[1]) != 0]
        print("lebende Einheiten", len(lebend), flush=True)
        ed = K.adresse("DAT_EntityState", "entityArray[].logicalState")
        frei = next(i for i in range(2900, 25, -1) if r.lies_i(ed[0] + i * ed[2], ed[1]) == 0)
        u = lebend[0]

        def uf(n):
            a = K.adresse("DAT_UnitsState", "units[]." + n)
            return a[0] + u * a[2], a[1]

        def ef(n):
            a = K.adresse("DAT_EntityState", "entityArray[]." + n)
            return a[0] + frei * a[2], a[1]

        alt = {("u", n): r.lies(*uf(n)) for n in U_F}
        alt.update({("e", n): r.lies(*ef(n)) for n in E_F})
        ergebnis = collections.Counter()
        fehl = []
        gesichert = []
        try:
            for n, w in (("logicalState", 2), ("unitID_OR_seaGullID", 0), ("startingHeight", 8), ("targetZ", 8), ("field90_0xd0", 0)):
                r.setze_i(*(lambda a: (a[0], w, a[1]))(ef(n)))

            def probe(typ, art, h, abstand, gleiches_team):
                for n, w in (("unitType", typ), ("owner", 1), ("buildingHeight", 0), ("terrainOrClimbHeight", 8), ("health", 100000), ("maxHealth", 100000), ("dying", 0), ("tribeID", 0)):
                    a = uf(n)
                    r.setze_i(a[0], w, a[1])
                for n, w in (("entityType", art), ("height", h), ("owner", 1 if gleiches_team else 2), ("velocityUnk", 125)):
                    a = ef(n)
                    r.setze_i(a[0], w, a[1])
                ist_ = r.rufe(TREFFER, u, frei, abstand, this=UNITS) & 0xff
                gesichert.append({"typ": typ, "art": art, "h": h, "abstand": abstand, "team": gleiches_team, "ist": ist_})
                return ist_

            for typ in ARTEN_ZIEL:
                f0, f1 = fm.fenster(typ), fm.fenster_nachbar(typ)
                for abstand, f in ((0, f0), (1, f1)):
                    for h, soll in ((7, 0), (8, 1), (8 + f, 1), (9 + f, 0)):
                        ist = probe(typ, 1, h, abstand, False)
                        ergebnis[("Fenster", typ, abstand, f, "gleich" if ist == soll else "ABWEICHUNG")] += 1
                        if ist != soll:
                            fehl.append(("Fenster", "Art", typ, "Abstand", abstand, "Hoehe", h, "Spiel", ist, "Modell", soll))
                # Teamregel: Geschoss vom eigenen Team in der Fenstermitte
                for art in (1, 7, 33, 2, 3, 4, 20):
                    soll = 0
                    if art in (2, 3, 4) and typ not in (fm.UT_SCHILD, fm.UT_TURM, fm.UT_RAMME):
                        soll = 1  # Spieler 1 ist auf Instanz 2 Mensch, darum trifft auch sein Mangonel
                    ist = probe(typ, art, 8 + min(f0, 40) // 2, 0, True)
                    ergebnis[("Team", art, "gleich" if ist == soll else "ABWEICHUNG")] += 1
                    if ist != soll:
                        fehl.append(("Team", "Art", typ, "Geschoss", art, "Spiel", ist, "Modell", soll))
        finally:
            for (w, n), b in alt.items():
                a = uf(n) if w == "u" else ef(n)
                r.schreibe(a[0], b)
    aus.append("Aufrufe je Fall: " + str(sorted(ergebnis.items(), key=str)))
    aus.append("Abweichungen: " + str(len(fehl)))
    aus += ["  " + str(x) for x in fehl[:30]]
    text = chr(10).join(aus) + chr(10)
    open(os.path.join(HIER, "fenster_rufen.txt"), "w", encoding="utf-8").write(text)
    with open(os.path.join(HIER, "fenster_beispiele.json"), "w", encoding="utf-8") as f:
        json.dump(gesichert, f)
    print(text)


if __name__ == "__main__":
    main()
