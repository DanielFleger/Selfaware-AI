# -*- coding: utf-8 -*-
"""Ohne Spiel: Rechnet die Sklaven-Tour der Wirkungsrechnung auf einem gespeicherten Lagebild nach und zaehlt, wie viel ihres Werts auf Gebaeuden
liegt, die der Brandtrupp nie angreift (raids.gefaehrlich oder brennt schon). Aufruf: python s_replay_wirkung.py <lage.jsonl.gz> [jede n-te Runde]"""
import collections
import sys

from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import raids as RA
from selfaware.telemetry import lageprotokoll as LP

p, jede = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
W = WK.Wissen()
summe = collections.Counter()
for i, (t, st, E, B) in enumerate(LP.runden(p)):
    if i % jede:
        continue
    L, G = {e["nr"]: e for e in E}, {g["nr"]: g for g in B}
    c = collections.Counter(e["besitzer"] for e in E if e["typ"] == RA.SKLAVE and e["leben"] > 0)
    if not c:
        continue
    sp = c.most_common(1)[0][0]
    posten = [g for g in B if g["besitzer"] == sp and g["typ"] == 8]
    if not posten:
        continue
    W.lernen(L, sp)
    kand = W.kandidaten(RA.SKLAVE, [z for z in WK.ziele(L, G, sp) if z.schluessel[0] == "g"])
    sicher = {z.schluessel for z, _, _ in kand if not RA.gefaehrlich(z.ort, L, G, sp) and not G[z.schluessel[1]].get("feuer")}
    wert, weg = W.tour(RA.SKLAVE, (posten[0]["x"], posten[0]["y"]), kand)
    w_s = sum(z.wert * a for z, a in weg if z.schluessel in sicher)
    w_a = sum(z.wert * a for z, a in weg)
    summe["sicher"] += w_s
    summe["alle"] += w_a
    print("Takt %5d | eigene Sklaven %3d | Ziele %2d, davon greift der Brandtrupp an %2d | Tour %5.1f Punkte, davon auf gemiedenen %3.0f %%" % (
        t, c[sp], len(kand), len(sicher), wert, 100 * (1 - w_s / w_a) if w_a else 0))
print("SUMME: %.0f %% des Tourwerts liegt auf Gebaeuden, die der Brandtrupp meidet" % (100 * (1 - summe["sicher"] / summe["alle"]) if summe["alle"] else 0))
