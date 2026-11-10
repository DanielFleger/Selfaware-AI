# -*- coding: utf-8 -*-
"""Ohne Spiel: Kauf nach Wirkung (geeicht) je Runde ohne und mit den eigenen Raid-Einheiten im Feld (B-182, Entwurf vorhanden). Je Runde ein
Schnappschuss: Ruecklage 0, keine vergebenen Ziele, im Feld = alle eigenen Sklaven, Berittenen, Schwertkaempfer (und Typ 70 bis Takt 15.000).
Aufruf: python s_replay_feld.py <lage> [jede n-te Runde]"""
import collections
import sys

from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import raid as RB
from selfaware.micro.tasks import nahkampf as NK
from selfaware.micro.tasks import raids as RA
from selfaware.telemetry import lageprotokoll as LP

p, jede = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
best = RB.RaidBestellungNachWirkung()
summe = {"ohne Feld": collections.Counter(), "mit Feld": collections.Counter()}
for i, (t, st, E, B) in enumerate(LP.runden(p)):
    if i % jede or "gold" not in st:
        continue
    L, G = {e["nr"]: e for e in E}, {g["nr"]: g for g in B}
    sp = 1
    posten = [g for g in B if g["besitzer"] == sp and g["typ"] == 8]
    if not posten:
        continue
    e = RB.RaidEinsatz(sp, (0, 0), lambda nr: 0, AF.Steckplaetze(AF.laden("raid_wirkung")["versionen"]))
    arten = {RA.SKLAVE, RA.PFERDEBOGEN, 75} | ({70} if t < 15000 else set())
    feld = tuple((x["typ"], (x["x"], x["y"])) for x in E if x["besitzer"] == sp and x["typ"] in arten and x["leben"] > 0)
    steuerbar = frozenset({RA.SKLAVE, RA.PFERDEBOGEN, RB.ASSASSINE} | set(NK.KANN) | ({70} if t < 15000 else set()))
    zeile = []
    for name, vh in (("ohne Feld", ()), ("mit Feld", feld)):
        lage = RB.Lage(runde=1, gold=st["gold"], ruecklage=0, ruecklage_soeldner=0, feuer=st.get("feuer", 0), endspurt=False, soeldner_erlaubt=True,
                       assassine_erlaubt=True, sklaven=0, reiter=0, schleuderer=0, L=L, G=G, sp=sp, start=(posten[0]["x"], posten[0]["y"]),
                       steuerbar=steuerbar, greift_an=e.greift_an, vorhanden=vh)
        k = dict(best.schritt(lage))
        summe[name].update(k)
        zeile.append("%s %s" % (name, k))
    print("Takt %5d Gold %5d im Feld %3d (Reiter %d) | %s" % (t, st["gold"], len(feld), sum(1 for a, _ in feld if a == 74), " | ".join(zeile)))
print("SUMME", {k: dict(v) for k, v in summe.items()})
