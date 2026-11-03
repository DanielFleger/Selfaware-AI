# -*- coding: utf-8 -*-
"""Die Starttruppen im Gefecht kommen bei Takt 202 und 403, geraeumt wurde bis 22:41 davor. Haben sie in den Gefecht-Szenen getroffen, was ich den Taetern der Szene zugeschrieben habe? Je Szene: fremde Einheiten (nicht im Plan), die eine Einheit des Plans schlagen oder beschiessen.

  PYTHONPATH=src python data/research/auge_plan/lauf_s_20261103/stoerung_starttruppen.py > data/research/auge_plan/lauf_s_20261103/stoerung_starttruppen.txt
"""
import collections
import glob
import json
import os
import sys

import numpy as np

from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

L = "data/research/auge_plan/laeufe/"
karte = Feldkarte.laden(feldliste=FELDLISTE)
HOECHSTENS = 2  # Dateien je Szene: die letzten


def nachsehen(p):
    plan = json.load(open(p + ".plan.json", encoding="utf-8"))
    im_plan = {e["nr"]: e for e in plan["einheiten"] if "nr" in e}
    auf = Aufzeichnung(p)
    iu = auf.namen.index("DAT_UnitsState")
    bu = auf.bereiche[iu][1]
    schritt = karte.adresse("DAT_UnitsState", "units[].logicalState")[2]
    o = {k: karte.adresse("DAT_UnitsState", "units[]." + ar.FELDER[k][0])[0] - bu for k in ("da", "typ", "schlaegt", "besitzer", "leben", "mx", "my")}
    ziele = np.array(sorted(im_plan), dtype=np.int16)
    start, fremd_schlaegt, fremd_erster = None, collections.Counter(), {}
    fremde = {}
    for r, roh, _ in auf.staende():
        if r.bereich != iu or not r.rein:
            continue
        a = bytes(roh)
        s = {k: np.ndarray(shape=(ar.PLAETZE,), dtype=ar.FELDER[k][1], buffer=a, offset=o[k], strides=(schritt,)) for k in o}
        start = r.takt if start is None else start
        da = s["da"] != 0
        for i in np.nonzero(np.r_[False, da[1:]] & (s["besitzer"] > 0) & (s["besitzer"] <= 2) & np.isin(s["schlaegt"], ziele) & ~np.isin(np.arange(ar.PLAETZE), ziele))[0]:
            k = (int(s["typ"][i]), int(s["besitzer"][i]), im_plan[int(s["schlaegt"][i])].get("posten"), im_plan[int(s["schlaegt"][i])]["rolle"])
            fremd_schlaegt[k] += 1
            fremd_erster.setdefault(k, r.takt - start)
        da[0] = False  # Platz 0 ist die Kopie der gerade laufenden Einheit
        for i in np.nonzero(da & (s["besitzer"] > 0) & (s["besitzer"] <= 2) & ~np.isin(np.arange(ar.PLAETZE), ziele))[0]:
            fremde.setdefault((int(s["typ"][i]), int(s["besitzer"][i])), set()).add(int(i))
    g = ar.geschosse_lesen(p, karte)
    pfeile = collections.Counter()
    for x in g:
        if x["schuetze"] not in im_plan and x["ziel"] in im_plan:
            pfeile[(x["art"], x["besitzer"], im_plan[x["ziel"]].get("posten"), im_plan[x["ziel"]]["rolle"])] += 1
    alle_fremd = collections.Counter(x["art"] for x in g if x["schuetze"] not in im_plan)
    alle_plan = collections.Counter(x["art"] for x in g if x["schuetze"] in im_plan)
    print("==", os.path.basename(p), "Beginn", start, "Takte", plan["bis"] - plan["von"])
    print("   fremde Einheiten (Art, Spieler: Anzahl):", {k: len(v) for k, v in sorted(fremde.items()) if k[0] != 1})
    print("   fremde Schlaeger auf den Plan (Art, Spieler, Posten, Rolle: Rahmen, erster Takt):", {str(k): (v, fremd_erster[k]) for k, v in fremd_schlaegt.items()} or "keine")
    print("   fremde Geschosse auf den Plan (Art, Spieler, Posten, Rolle):", {str(k): v for k, v in pfeile.items()} or "keine")
    print("   alle Geschosse: fremde", dict(alle_fremd), "vom Plan", dict(alle_plan))
    sys.stdout.flush()


for szene in sys.argv[1:] or ("sonder_g", "sonder2_g", "sonder3_g", "sonder4_g", "sonder5_g", "sonder6_g", "sonder7_g", "laufen_g", "nahkampf_g", "beschuss_g", "laufen_trupp_g", "reichweite_g", "lord_g"):
    for p in sorted(glob.glob(L + f"*_{szene}.auge"), key=os.path.getmtime)[-HOECHSTENS:]:
        if not os.path.exists(p + ".plan.json"):
            print("==", os.path.basename(p), "kein Plan")
            continue
        try:
            nachsehen(p)
        except Exception as e:
            print("==", os.path.basename(p), "FEHLER", repr(e))
