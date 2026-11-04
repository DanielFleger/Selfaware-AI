# -*- coding: utf-8 -*-
"""B-142: Gefecht mit Buendnis (P001, P185, P187). Dazu: Stehen einzeln befohlene Einheiten auf einem Feld (sonder17)?

  PYTHONPATH="src;data/research/auge_plan/lauf_s_20261103" python data/research/auge_plan/lauf_s_20261103/punkte_rechnen_b.py > data/research/auge_plan/lauf_s_20261103/punkte_rechnung_b.txt
"""
import collections
import glob
import os
import struct

import numpy as np

import punkte_lesen as pl
from selfaware.tools.analysis.auge_auswertung import Aufzeichnung

K = pl.karte


def stapel():
    p = pl.neueste("sonder17")
    plan = pl.plan_von(p)
    wer = [e for e in plan["einheiten"] if e.get("posten") == "turm_voll"]
    letzt = None
    for t, u in pl.stand(p, "DAT_UnitsState", {"mx": "units[].microXPosition", "my": "units[].microYPosition"}):
        letzt = [(int(u["mx"][e["nr"]]) // 8, int(u["my"][e["nr"]]) // 8) for e in wer]
    print("Einzeln befohlen, ein Zielfeld, sonder17 am Ende:", collections.Counter(letzt).most_common())


def buendnis():
    f = sorted(glob.glob(os.path.join(pl.L, "buendnis_k_*.auge")), key=os.path.getsize)
    if not f:
        print("kein Lauf")
        return
    p = f[-1]
    print("Datei", os.path.basename(p))
    auf = Aufzeichnung(p)
    basis = {b[0]: b[1] for b in auf.bereiche}
    g = "DAT_GameState"
    te = K.adresse(g, "mapAndTime.playerTeams[]")
    st = K.adresse(g, "playerDataArray[].currentResources[]")
    r1 = K.adresse(g, "playerDataArray[].requestedGoodsArray1Unk[]")
    r2 = K.adresse(g, "playerDataArray[].requestedGoodsArray2Unk[]")
    teams = None
    alt = None
    t0 = None
    paare = []
    bitten = {}
    zahl = collections.Counter()
    for r, roh, _ in auf.staende():
        if not r.rein or auf.namen[r.bereich] != g:
            continue
        t0 = t0 if t0 is not None else r.takt
        t = r.takt - t0
        b = basis[g]
        if teams is None:
            teams = struct.unpack_from("<9i", roh, te[0] - b)
            print("P001 playerTeams:", teams)
        gold = [struct.unpack_from("<i", roh, st[0] + sp * st[2] + 4 * 15 - b)[0] for sp in range(9)]
        if alt is not None:
            d = [x - y for x, y in zip(gold, alt)]
            for a in range(1, 9):
                if d[a] <= -20:
                    freunde = [c for c in range(1, 9) if c != a and teams[c] == teams[a]]
                    fremd = [c for c in range(1, 9) if c not in freunde and c != a]
                    plus = [(c, d[c]) for c in freunde if d[c] > 0]
                    if plus and sum(x for _, x in plus) >= -d[a] * 0.5:
                        paare.append((t, a, d[a], plus))
        alt = gold
        for sp in range(1, 9):
            for name, q in (("art", r1), ("menge", r2)):
                w = tuple(struct.unpack_from("<9h" if q[1] == 2 else "<9i", roh, q[0] + sp * q[2] - b))
                if bitten.get((sp, name)) != w:
                    if (sp, name) in bitten and any(w):
                        zahl[name] += 1
                        if zahl[name] <= 6:
                            print("   P187 Takt", t, "Spieler", sp, name, w)
                    bitten[(sp, name)] = w
    print("P185 Gold geht an Verbuendete, Anzahl", len(paare), "Beispiele (Takt, Geber, Aenderung, [(Empfaenger, Aenderung)]):", paare[:8])
    print("P187 Wechsel:", dict(zahl))


if __name__ == "__main__":
    for f in (stapel, buendnis):
        try:
            f()
        except Exception as e:
            import traceback
            print("FEHLER", f.__name__, repr(e))
            traceback.print_exc(limit=2)
