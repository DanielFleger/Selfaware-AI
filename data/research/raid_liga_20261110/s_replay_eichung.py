# -*- coding: utf-8 -*-
"""Ohne Spiel: Kauf nach Wirkung je Runde ungeeicht gegen geeicht (raid_eichung.json), beide mit der Frage an den Einsatz. Je Runde ein Schnappschuss
(Ruecklage 0, keine vergebenen Ziele, Arabische Bogenschuetzen nur bis Takt 15.000 wie im Lenker). Aufruf: python s_replay_eichung.py <lage> [jede n-te Runde]"""
import collections
import sys

from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import raid as RB
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import nahkampf as NK
from selfaware.micro.tasks import raids as RA
from selfaware.telemetry import lageprotokoll as LP

p, jede = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
varianten = {"ungeeicht": RB.RaidBestellungNachWirkung(), "geeicht": RB.RaidBestellungNachWirkung()}
varianten["ungeeicht"]._wissen = WK.Wissen(eichung={})
varianten["geeicht"]._wissen = WK.Wissen()
summe = {k: collections.Counter() for k in varianten}
for i, (t, st, E, B) in enumerate(LP.runden(p)):
    if i % jede or "gold" not in st:
        continue
    L, G = {e["nr"]: e for e in E}, {g["nr"]: g for g in B}
    sp = 1
    posten = [g for g in B if g["besitzer"] == sp and g["typ"] == 8]
    if not posten:
        continue
    e = RB.RaidEinsatz(sp, (0, 0), lambda nr: 0, AF.Steckplaetze(AF.laden("raid_wirkung")["versionen"]))
    steuerbar = frozenset({RA.SKLAVE, RA.PFERDEBOGEN, RB.ASSASSINE} | set(NK.KANN) | ({70} if t < 15000 else set()))
    zeile = []
    for name, best in varianten.items():
        lage = RB.Lage(runde=1, gold=st["gold"], ruecklage=0, ruecklage_soeldner=0, feuer=st.get("feuer", 0), endspurt=False, soeldner_erlaubt=True,
                       assassine_erlaubt=True, sklaven=0, reiter=0, schleuderer=0, L=L, G=G, sp=sp, start=(posten[0]["x"], posten[0]["y"]),
                       steuerbar=steuerbar, greift_an=e.greift_an)
        k = dict(best.schritt(lage))
        summe[name].update(k)
        zeile.append("%s %s" % (name, k))
    print("Takt %5d Gold %5d | %s" % (t, st["gold"], " | ".join(zeile)))
print("SUMME", {k: dict(v) for k, v in summe.items()})
