# -*- coding: utf-8 -*-
"""Gegenprobe: B-Plantagen gelten erst nach echtem Gebäude und blockieren nie durch Phantom-Aufträge."""
import selfaware.macro.wirtschaft as W


def wirt(bauen):
    x = W.Wirtschaft({"aepfel": [], "lager": [0, 0]}, 1, bauen, [])
    x.A = [(10, 10)]
    x.B = [(20, 20), (30, 30), (40, 40)]
    x.B_offen = list(x.B)
    x.apfelbaum = 1
    x.stufe_a = lambda: W.REIF
    return x


def main():
    auftraege = []
    def bauen(_typ, x, y, _r):
        ort = (x + 1, y + 1)
        auftraege.append(ort)
        return ort
    x = wirt(bauen)
    st = {"t": 1000, "holz": 6, "gold": 30}
    G = {9: {"besitzer": 1, "typ": W.APFEL, "x": 10, "y": 10}}
    x.schritt(st, {}, G)
    p1 = len(auftraege) == 2 and len(x.B_offen) == 3
    G.update({
        1: {"besitzer": 1, "typ": W.APFEL, "x": 21, "y": 21},
        2: {"besitzer": 1, "typ": W.APFEL, "x": 31, "y": 31},
    })
    x.schritt({"t": 1010, "holz": 0, "gold": 0}, {}, G)
    p2 = x.B_offen == [(40, 40)]
    # Dritter Auftrag, aber noch kein Gebäude: bleibt offen; vor Frist kein Doppelauftrag, danach neuer Versuch.
    x.schritt({"t": 1020, "holz": 3, "gold": 15}, {}, G)
    x.schritt({"t": 1040, "holz": 3, "gold": 15}, {}, G)
    vor = len(auftraege) == 3
    x.schritt({"t": 1070, "holz": 3, "gold": 15}, {}, G)
    p3 = vor and len(auftraege) == 4 and x.B_offen == [(40, 40)]
    G[3] = {"besitzer": 1, "typ": W.APFEL, "x": 41, "y": 41}
    x.schritt({"t": 1080, "holz": 0, "gold": 0}, {}, G)
    p4 = not x.B_offen and x.B_tick == 1080 and x.ruecklage(G) == {"holz": 0, "gold": 0}
    pruefungen = [
        ("Bestand erlaubt nur zwei Auftraege; Auftraege allein schliessen nichts", p1),
        ("zwei echte Gebaeude schliessen genau zwei B-Plaetze", p2),
        ("fehlender Bau wird nach Frist neu beauftragt, bleibt bis dahin offen", p3),
        ("letztes echtes Gebaeude setzt B-Tick und hebt Ruecklage auf", p4),
    ]
    for text, ok in pruefungen:
        print(("OK  " if ok else "ROT ") + text)
    print("%d von %d gruen" % (sum(ok for _, ok in pruefungen), len(pruefungen)))
    return 0 if all(ok for _, ok in pruefungen) else 1


if __name__ == "__main__":
    raise SystemExit(main())
