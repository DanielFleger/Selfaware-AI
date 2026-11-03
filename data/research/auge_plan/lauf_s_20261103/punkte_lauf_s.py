# -*- coding: utf-8 -*-
"""Die 75 Punkte der Checkliste (Abschnitt Lauf S) gegen alle Aufzeichnungen von Lauf S. Das Werkzeug sagt je Punkt: gesehen, bestaetigt, Zahl weicht ab, nicht gesehen.
Danach die Gesamtproben A1, A2, A3, A4, A7, A9, A10 an den drei groessten Szenen.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/punkte_lauf_s.py > data/research/auge_plan/lauf_s_20261103/punkte_lauf_s.txt
"""
import glob
import json
import os
import sys

from selfaware.tools.analysis import auge_auswertung as aa
from selfaware.tools.analysis import auge_punkte
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(HIER, "..", "laeufe")
CHECK = os.path.join(HIER, "..", "Checkliste_Auge.md")
SZENEN = ("nahkampf", "laufen", "beschuss", "schlacht_20", "schlacht_1000", "schlacht_schuetzen", "schlacht_araber", "last", "schlacht_streng", "laufen_trupp", "reichweite", "schussweite", "schussweite_pfeil", "laufziel",
          "haltung", "haltung2", "besatzung", "geraete_weite", "belagerung", "gebaeude_nah", "punkt", "sonder1", "sonder2", "laufen_g", "nahkampf_g", "beschuss_g", "laufen_trupp_g", "reichweite_g", "sonder_g", "lord_g", "sonder2_g", "sonder3", "sonder3_g", "sonder4_g", "sonder5", "sonder5_g", "sonder6_g", "sonder7_g")


def neueste(s):
    f = sorted(glob.glob(os.path.join(L, f"lauf_s_*_{s}.auge")), key=os.path.getmtime)
    return f[-1] if f else None


karte = Feldkarte.laden(feldliste=FELDLISTE)
pfade = {s: neueste(s) for s in SZENEN}
print("fehlt:", [s for s, p in pfade.items() if p is None], flush=True)
auf = [aa.Aufzeichnung(p) for p in pfade.values() if p]
e = auge_punkte.auswerten(CHECK, auf, karte, lauf="S")
auge_punkte.schreiben(e, os.path.join(HIER, "punkte_lauf_s.json"))
print(auge_punkte.bericht(e), flush=True)
for s in ("punkt", "sonder_g", "schlacht_1000"):
    print("===", s, flush=True)
    a = aa.Aufzeichnung(pfade[s])
    e1 = aa.a1_aenderungsmelder(a, karte)
    aus = [e1, aa.a2_nie_gesehen(karte, e1.daten["gesehen"]), aa.a3_takttreue(a), aa.a4_lesedauer(a), aa.a7_zufall(a), aa.a9_befehle(a), aa.a10_lebenslauf(a, aa.echte_listen(karte), aa.echte_grenzen(karte))]
    print(aa.bericht(aus)[:3000], flush=True)
sys.exit(0)
