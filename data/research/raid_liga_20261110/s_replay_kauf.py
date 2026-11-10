# -*- coding: utf-8 -*-
"""Ohne Spiel: Was haette RaidBestellungNachWirkung je Runde gekauft - ohne und mit der Frage an den Einsatz (B-182)? Je Runde ein Schnappschuss,
keine Nachbildung des Ablaufs: Ruecklage 0 und keine vergebenen Ziele (beides steht nicht im Lagebild), frischer Einsatz (nichts brennt, kein Schutz).
Aufruf: python s_replay_kauf.py <lage.jsonl.gz> [jede n-te Runde]"""
import collections
import sys

from selfaware.baukasten import aufstellung as AF
from selfaware.baukasten import raid as RB
from selfaware.micro.tasks import nahkampf as NK
from selfaware.micro.tasks import raids as RA
from selfaware.telemetry import lageprotokoll as LP

p, jede = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
MIT_FELD = "vorhanden" in RB.Lage.__dataclass_fields__  # Entwurf b182_vorhanden_entwurf.diff eingespielt? Sonst ist Spalte feld = mit
best = RB.RaidBestellungNachWirkung()
summe = {"ohne": collections.Counter(), "mit": collections.Counter(), "feld": collections.Counter()}
steuerbar = frozenset({RA.SKLAVE, RA.PFERDEBOGEN, 70, RB.ASSASSINE} | set(NK.KANN))
for i, (t, st, E, B) in enumerate(LP.runden(p)):
    if i % jede or "gold" not in st:
        continue
    L, G = {e["nr"]: e for e in E}, {g["nr"]: g for g in B}
    c = collections.Counter(e["besitzer"] for e in E if e["typ"] == RA.SKLAVE and e["leben"] > 0)
    if not c:
        continue
    sp = c.most_common(1)[0][0]
    posten = [g for g in B if g["besitzer"] == sp and g["typ"] == 8]
    if not posten:
        continue
    e = RB.RaidEinsatz(sp, (0, 0), lambda nr: 0, AF.Steckplaetze(AF.laden("raid_wirkung")["versionen"]))
    zeile = []
    feld = tuple((x["typ"], (x["x"], x["y"])) for x in E if x["besitzer"] == sp and x["typ"] in (71, 74, 75) and x["leben"] > 0)
    for name, ga, vh in (("ohne", None, ()), ("mit", e.greift_an, ()), ("feld", e.greift_an, feld)):
        lage = RB.Lage(runde=1, gold=st["gold"], ruecklage=0, ruecklage_soeldner=0, feuer=st.get("feuer", 0), endspurt=False, soeldner_erlaubt=True,
                       assassine_erlaubt=True, sklaven=0, reiter=0, schleuderer=0, L=L, G=G, sp=sp, start=(posten[0]["x"], posten[0]["y"]),
                       steuerbar=steuerbar, greift_an=ga, **({"vorhanden": vh} if MIT_FELD else {}))
        k = dict(best.schritt(lage))
        summe[name].update(k)
        zeile.append("%s %s" % (name, k))
    print("Takt %5d Gold %5d Feuer %3d | %s" % (t, st["gold"], st.get("feuer", 0), " | ".join(zeile)))
print("SUMME ohne Frage:", dict(summe["ohne"]), "| mit Frage:", dict(summe["mit"]), "| mit Frage und Feld:", dict(summe["feld"]))
