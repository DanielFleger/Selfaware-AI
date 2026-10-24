# -*- coding: utf-8 -*-
"""Pruefung ohne Spiel fuer gefahrenschutz.py (B-217, 24.10.2026: Sklaven starben 22-40 Felder vor Bogenschuetzen, das Modell
rechnete dort mit den Assassinen-Baendern L73 = 0,06 je Schuetze und Takt; gemessen 0,5-1,8; Tode wurden nie gelernt).
Vorher festgelegt:
  1. Lerner: eine Einheit verschwindet unter Beschuss -> ihr Restleben ist Verlust, im Band ihres naechsten Schuetzen
  2. Lerner: Band = Abstand zum NAECHSTEN Schuetzen in Reichweite, Schuetzen-Takte = alle in Reichweite x Takte
  3. Lage.baender: Band mit >= BAND_MIN Schuetzen-Takten gilt gemessen, darunter L73 x Faktor; "alle gemessen" nur wenn alle
  4. Lage.plan: gelerntes fernes Band 1,3 statt 0,06 -> Verlust fuer Typ 71 um ein Vielfaches hoeher als ohne Lernen; Typ 74
     (keine Baender) rechnet wie vorher (L73 x Faktor); das Gitter von typ None ist das rohe L73
  5. schreiben: Baender werden in die Datei addiert, nicht ueberschrieben
Aufruf: python werkzeug/gefahrenschutz_pruefen.py (Rueckgabe 0 = gruen)"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gefahrenschutz as GS

ok = []


def pruefe(nr, text, bed):
    ok.append(bool(bed))
    print("%s %d %s" % ("OK  " if bed else "ROT ", nr, text))


REICH = {22: 44}
feind = lambda b: b == 3


def e(typ, sp, x, y, leben, zustand=101):
    return {"typ": typ, "besitzer": sp, "x": x, "y": y, "leben": leben, "zustand": zustand}


# 1 + 2: Lerner mit Tod und Band
L0 = {1: e(71, 1, 100, 100, 9000), 2: e(71, 1, 100, 160, 15000),
      10: e(22, 3, 130, 100, 5000), 11: e(22, 3, 140, 100, 5000), 12: e(22, 3, 100, 170, 5000)}
L1 = {2: e(71, 1, 100, 161, 14000), 10: e(22, 3, 130, 100, 5000), 11: e(22, 3, 140, 100, 5000), 12: e(22, 3, 100, 170, 5000)}
ln = GS.Lerner(1, (71,))
ln.SCHREIB_ALLE = 10 ** 9
ln.runde(1000, L0, GS.Lage(L0, {}, feind, REICH, raten={}))
ln.runde(1050, L1, GS.Lage(L1, {}, feind, REICH, raten={}))
b = ln.neu.get(71, {}).get("baender", {})
pruefe(1, "Tod gelernt: Band 44 Verlust %s (erwartet 9000 Restleben, naechster Schuetze 30 Felder)" % b.get("44"),
       b.get("44", {}).get("verlust") == 9000 and b["44"]["schuss_takte"] == 2 * 50)
pruefe(2, "Band des naechsten Schuetzen: Band 15 %s (Einheit 2: Schuetze 10 Felder, 1 in Reichweite, -1000)" % b.get("15"),
       b.get("15", {}).get("verlust") == 1000 and b["15"]["schuss_takte"] == 50)

# 3: baender gemessen / ungemessen
raten = {71: {"verlust": 10000.0, "vorhersage": 1000.0, "felder": 1000, "takte": 12000,
              "baender": {"44": {"verlust": 2600.0, "schuss_takte": 2000}, "15": {"verlust": 100.0, "schuss_takte": 10}}}}
lage = GS.Lage(L1, {}, feind, REICH, raten=raten)
bd, alle = lage.baender(71)
bd = dict(bd)
pruefe(3, "Baender 71: %s alle gemessen %s (44 gemessen 1,3; 15 ungemessen 0,56 x 10)" % (
    {k: round(v, 2) for k, v in bd.items()}, alle), abs(bd[44] - 1.3) < 1e-9 and abs(bd[15] - 5.6) < 1e-9 and not alle)

# 4: plan mit gelerntem Band gegen plan ohne Lernen
L4 = {10: e(22, 3, 130, 100, 5000), 11: e(22, 3, 140, 100, 5000)}
ohne = GS.Lage(L4, {}, feind, REICH, raten={71: {"verlust": 10000.0, "vorhersage": 1000.0, "felder": 1000, "takte": 12000}})
mit = GS.Lage(L4, {}, feind, REICH, raten=raten)
p_o = ohne.plan((100, 100), (100, 100), 71, 15000)
p_m = mit.plan((100, 100), (100, 100), 71, 15000)
p74 = mit.plan((100, 100), (100, 100), 74, 15000)
p74_o = ohne.plan((100, 100), (100, 100), 74, 15000)
roh = float(mit.gitter(None)[100, 100])
pruefe(4, "Verweilen auf (100,100), 2 Schuetzen 30/40 Felder: 71 ohne Lernen %.0f, mit %.0f (gemessen %s); 74 %.0f = %.0f; "
          "L73 roh %.2f" % (p_o["verlust"], p_m["verlust"], p_m["gemessen"], p74["verlust"], p74_o["verlust"], roh),
       abs(p_o["verlust"] - 2 * 0.06 * 10 * 211) < 1e-6 and abs(p_m["verlust"] - 2 * 1.3 * 211) < 1e-6
       and not p_m["gemessen"] and abs(p74["verlust"] - p74_o["verlust"]) < 1e-9 and abs(roh - 0.12) < 1e-9)

# 5: schreiben addiert Baender
tmp = tempfile.mkdtemp()
alt = GS.RATEN
GS.RATEN = os.path.join(tmp, "verlust_raten.json")
try:
    json.dump({"typen": {"71": {"verlust": 1.0, "vorhersage": 1.0, "felder": 0, "takte": 0,
                                "baender": {"44": {"verlust": 100.0, "schuss_takte": 10}}}}}, open(GS.RATEN, "w"))
    ln.schreiben()
    r = GS.raten_laden()[71]["baender"]
    pruefe(5, "Datei nach schreiben: Band 44 %s (100+9000 / 10+100), Band 15 %s" % (r.get("44"), r.get("15")),
           r["44"]["verlust"] == 9100 and r["44"]["schuss_takte"] == 110 and r["15"]["verlust"] == 1000)
finally:
    GS.RATEN = alt

print("%d von %d gruen" % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
