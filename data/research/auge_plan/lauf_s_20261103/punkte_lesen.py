# -*- coding: utf-8 -*-
"""Lesehilfe fuer die Einzelpunkte von Lauf S: beliebige Felder einer Aufzeichnung Rahmen fuer Rahmen, ohne Zwischenspeicher (Lauf K: 38 GB)."""
import collections
import glob
import json
import os
import struct

import numpy as np

from selfaware.tools.analysis.auge_auswertung import Aufzeichnung
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte

HIER = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(HIER, "..", "laeufe")
karte = Feldkarte.laden(feldliste=FELDLISTE)
TYP = {1: "<i1", 2: "<i2", 4: "<i4"}


def neueste(szene):
    f = sorted(glob.glob(os.path.join(L, f"lauf_s_*_{szene}.auge")), key=os.path.getmtime)
    return f[-1] if f else None


def plan_von(p):
    pf = p + ".plan.json"
    return json.load(open(pf, encoding="utf-8")) if os.path.exists(pf) else {}


def stand(p, gruppe, felder, rein=True, jeder=1):
    """(Takt, {Name: Werte}) je Rahmen des Bereichs. felder: {Name: Feldname der Karte}. Einzelfelder kommen als Zahl, Listen als Array. Kartenebenen stehen nur in jedem 25. Rahmen."""
    auf = Aufzeichnung(p)
    i = auf.namen.index(gruppe)
    b0 = auf.bereiche[i][1]
    ad = {}
    for k, f in felder.items():  # ("feld", Versatz): ein Eintrag innerhalb des Feldes, z. B. Ware Nr. 4 je Spieler
        name, versatz = f if isinstance(f, tuple) else (f, 0)
        adr, g, schritt, anzahl = karte.adresse(gruppe, name)
        ad[k] = (adr + versatz, g, schritt, anzahl)
    n = 0
    for r, roh, _ in auf.staende():
        if r.bereich != i or (rein and not r.rein):
            continue
        n += 1
        if n % jeder:
            continue
        a = bytes(roh)
        aus = {}
        for k, (adr, g, schritt, anzahl) in ad.items():
            if anzahl and anzahl > 1:
                aus[k] = np.ndarray(shape=(anzahl,), dtype=TYP[g], buffer=a, offset=adr - b0, strides=(schritt,))
            else:
                aus[k] = struct.unpack_from({1: "<b", 2: "<h", 4: "<i"}[g], a, adr - b0)[0]
        yield r.takt, aus


def wechsel(reihe, schluessel=None):
    """Nur die Wechsel einer Folge (Takt, Wert)."""
    aus = []
    for t, w in reihe:
        if not aus or aus[-1][1] != w:
            aus.append((t, w))
    return aus


def urteil(punkt, wort, text):
    print(f"URTEIL {punkt} {wort}: {text}", flush=True)
