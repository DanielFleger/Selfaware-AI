# -*- coding: utf-8 -*-
"""B-142: Was beantworten die Aufzeichnungen von Lauf K schon, ohne das Spiel zu starten? Nur lesen. Geprueft werden Regeln statt einzelner Zeilen der Versuchsliste:
1. Nahkampf: Der Lebensverlust eines Opfers mit genau einem Schlaeger ist der Tabellenwert Schlaeger gegen Opfer.
2. Pruefrunde: Der Abstand zum naechsten Feind aendert sich nur auf Takten, wo totalGameTicksUnk & Maske gleich fixedRng & Maske ist (updateUnits Zeile 369).

Aufruf aus dem Arbeitsbaum:
  PYTHONPATH=src python data/research/auge_plan/lauf_s_plan/regeln_aus_lauf_k.py t1 t6 t7 t8 t9 > data/research/auge_plan/lauf_s_plan/regeln_aus_lauf_k.txt
"""
import collections
import os
import sys

import numpy as np

from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
karte = Feldkarte.laden(feldliste=FELDLISTE)
SCHRITT = karte.adresse("DAT_UnitsState", "units[].logicalState")[2]
PLAETZE = 2500
FELDER = {"da": ("logicalState", "<i2"), "typ": ("unitType", "<i2"), "besitzer": ("owner", "<i2"), "leben": ("health", "<i4"), "schlaegt": ("attackedUnitID", "<i2"),
          "abstand": ("closestEnemyMicroDistance", "<i2"), "rng": ("fixedRng", "<i4"), "maske": ("enemyNoticeFrequencyUnk", "<i4")}
T_ADR = karte.adresse("DAT_GameState", "mapAndTime.totalGameTicksUnk")[0]
ANGST = karte.adresse("DAT_GameState", "playerDataArray[].fearFactorLevel")
TAB = karte.adresse("DAT_UnitPropertiesDefinedData", "DAT_MELEE_DAMAGE")[0]
pruefrunde = collections.Counter()
treffer = collections.Counter()
paare = collections.Counter()
daneben = collections.Counter()
n_rahmen = 0
for fenster in sys.argv[1:]:
    auf = Aufzeichnung(os.path.join(HIER, "..", "laeufe", "lauf_k_20261102_234952_%s.auge" % fenster))
    iu, ig, id_ = auf.namen.index("DAT_UnitsState"), auf.namen.index("DAT_GameState"), auf.namen.index("datenblock")
    bu, bg, bd = auf.bereiche[iu][1], auf.bereiche[ig][1], auf.bereiche[id_][1]
    O = {k: karte.adresse("DAT_UnitsState", "units[]." + f)[0] - bu for k, (f, _) in FELDER.items()}
    tabelle = None
    spiel = None
    vor = None
    takt_vor = None
    for r, p, _ in auf.staende():
        if r.bereich == id_ and tabelle is None:
            tabelle = np.frombuffer(bytes(p), dtype="<i4", offset=TAB - bd, count=6400).copy().reshape(80, 80)
        if r.bereich == ig:
            spiel = bytes(p)
        if r.bereich != iu or not r.rein or spiel is None or tabelle is None:
            continue
        a = bytes(p)
        n_rahmen += 1
        s = {k: np.ndarray(shape=(PLAETZE,), dtype=FELDER[k][1], buffer=a, offset=O[k], strides=(SCHRITT,)).copy() for k in FELDER}
        s["leben"] = s["leben"].astype(np.int64)
        t = int(np.frombuffer(spiel, dtype="<u4", offset=T_ADR - bg, count=1)[0])
        if vor is not None and r.takt == takt_vor + 1:
            lebt = (s["da"] != 0) & (vor["da"] != 0) & (s["typ"] == vor["typ"])
            lebt[0] = False  # Platz 0 ist ein Merkplatz
            # Regel 2
            wechsel = np.nonzero(lebt & (s["abstand"] != vor["abstand"]) & (s["maske"] > 0))[0]
            for i in wechsel:
                m = int(s["maske"][i])
                for versatz in (-2, -1, 0, 1, 2):  # gelesen wird nach dem Takt, der Zaehler kann in der Rechnung schon weiter oder noch zurueck sein
                    if ((t + versatz) & m) == (int(s["rng"][i]) & m):
                        pruefrunde[versatz] += 1
                pruefrunde["alle"] += 1
            # Regel 1
            verlust = vor["leben"] - s["leben"]
            opfer = np.nonzero(lebt & (verlust > 0) & (s["leben"] > 0))[0]
            sch = s["schlaegt"]
            zahl = np.bincount(sch[(sch > 0) & (sch < PLAETZE) & (s["da"] != 0)], minlength=PLAETZE)
            wer = np.zeros(PLAETZE, dtype=np.int64)
            for j in np.nonzero((sch > 0) & (sch < PLAETZE) & (s["da"] != 0))[0]:
                wer[sch[j]] = j
            for v in opfer:
                if zahl[v] != 1:
                    continue
                w = int(wer[v])
                ta, tv = int(s["typ"][w]), int(s["typ"][v])
                soll = int(tabelle[ta, tv])
                angst = int(np.frombuffer(spiel, dtype="<i4", offset=ANGST[0] + int(s["besitzer"][w]) * ANGST[2] - bg, count=1)[0])
                d = int(verlust[v])
                if ta == 55:
                    art = "gleich" if d == soll else "anders"
                else:
                    art = "gleich" if d == soll else ("mit Angstfaktor" if soll and abs(d - soll) <= soll * 0.25 else "anders")
                treffer[art] += 1
                paare[(ta, tv)] += 1
                if art != "gleich":
                    daneben[(ta, tv, soll, d, angst)] += 1
        vor, takt_vor = s, r.takt
print("Fenster", sys.argv[1:], "Rahmen", n_rahmen)
print("Regel Pruefrunde, Aenderungen des Abstands:", dict(pruefrunde))
print("Regel Nahkampf, Opfer mit genau einem Schlaeger:", dict(treffer))
print("Verschiedene Paare Schlaeger gegen Opfer:", len(paare), "davon unter den 19 Kampfarten:", sum(1 for a, v in paare if a in (5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 55, 70, 71, 72, 73, 74, 75, 76) and v in (5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 37, 55, 70, 71, 72, 73, 74, 75, 76)), "von 361")
print("Haeufigste Abweichungen (Schlaeger, Opfer, Tabelle, gemessen, Angstfaktor des Schlaegers):", daneben.most_common(14))
