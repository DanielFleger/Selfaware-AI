# -*- coding: utf-8 -*-
"""B-273 Schritt 0: Vorhersage-Tagebuch ohne Spiel pruefen (Soll je Fall vorher festgelegt).
Ein feindlicher Lord (Spieler 2) verliert Leben, zwei eigene Streitkolben (Typ 26) stehen bei ihm, einer schlaegt sichtbar.
Aufruf: python tagebuch_pruefen.py"""
import json
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import gefecht
import tagebuch as TB


def einheit(nr, sp, typ, x, y, leben, zustand=0, nahziel=-1):
    return nr, {"nr": nr, "besitzer": sp, "typ": typ, "x": x, "y": y, "leben": leben, "zustand": zustand, "zielart": 0,
                "zieleinheit": 0, "nahziel": nahziel}


def lauf(an):
    datei = os.path.join(tempfile.gettempdir(), "tagebuch_pruefen_%s.jsonl" % an)
    if os.path.exists(datei):
        os.remove(datei)
    tb = TB.Tagebuch(1, an=an, datei=datei)
    freunde, feind = {1}, (lambda b: b not in (0, 1))
    runden = [(1000, 300000), (1200, 290000), (1400, 290000)]       # Runde 2: 10.000 Leben in 200 Takten = 50 je Takt
    for t, leben in runden:
        L = dict([einheit(3, 2, 55, 100, 100, leben), einheit(10, 1, 26, 101, 100, 25000, zustand=106, nahziel=3),
                  einheit(11, 1, 26, 103, 100, 25000), einheit(12, 1, 26, 120, 100, 25000)])
        tb.lord_runde(t, L, freunde, feind)
    zeilen = [json.loads(z) for z in open(datei, encoding="utf-8")] if os.path.exists(datei) else []
    return tb, zeilen


if __name__ == "__main__":
    sch, _l, fern = gefecht.tabelle()
    soll_v = 2 * gefecht.dps(26, 55, sch, fern, 1)            # zwei Streitkolben bis 5 Felder, der dritte (20 Felder) nicht
    tb, z = lauf(True)
    e = z[0] if z else {}
    faelle = [
        ("genau ein Abgleich (nur Runde 2 hat Lebensverlust)", len(z) == 1),
        ("gemessen = 10.000 Leben / 200 Takte = 50 je Takt", e.get("gemessen") == 50.0),
        ("Vorhersage = 2 Streitkolben bis 5 Felder (%.1f)" % soll_v, e.get("vorhersage") == round(soll_v, 2)),
        ("Verhaeltnis gemessen/vorhergesagt", e.get("verhaeltnis") == round(50.0 / soll_v, 3)),
        ("sichtbar zuschlagend: 1 von 2", e.get("eingang", {}).get("schlagen_sichtbar") == 1),
    ]
    tb_aus, z_aus = lauf(False)
    faelle.append(("Schalter aus: keine Zeile", z_aus == []))
    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(ok for _, ok in faelle), len(faelle)))
    sys.exit(0 if all(ok for _, ok in faelle) else 1)
