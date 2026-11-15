# -*- coding: utf-8 -*-
"""Rolle je Einheit, jede Runde neu (B-182; Daniel 13.11.2026 23:07: "Ist das nicht einfach eine berechnung- Was macht der gegner
und wird verteidigung, raid oder angriff gebraucht? Und dann wird bestimt was pro einheit passiert. Ich persoenlich sehe in dem fall
keinen grund nicht zu raiden"; 23:14 "Ja, bauen"; Plan_Unit_Status_Log.md Abschnitt 10).

1. Bedrohung (bedrohungen): feindliche Truppen an unseren Gebaeuden - Ort bis BEI_GEBAEUDE oder Laufziel bis ZIEL_AM_GEBAEUDE Felder -
   und die Angreifer unserer Einheiten bis ANGREIFER_R Felder von unseren Gebaeuden. Das ist die Regel, mit der der Waechter seit
   12.10./19.10. seine Feinde findet; sie lebt jetzt hier, der Waechter ruft sie.
2. Verteidigung (verteilen): die kleinste Gruppe, mit der die Gefechtsrechnung gegen diese Bedrohung gewinnt
   (micro/zuweisung.kleinste_gruppe, die naechsten zuerst); ohne Bedrohung niemand.
3. Alle anderen Kandidaten raiden, wenn es einen Nahkampf-Raid gibt.
Offen (Frage an Daniel): Gewinnt keine Gruppe, bleiben alle beim Waechter - wie bisher, keine neue Regel.
Ohne Spiel pruefbar (tests/test_rollen.py).
"""
from selfaware.micro import zuweisung as ZW

NAHKAMPF = {24, 25, 26, 27, 28, 37, 55, 71, 73, 75}
FERNKAMPF = {22, 23, 70, 72, 74, 76}
TRUPPE = NAHKAMPF | FERNKAMPF
BEI_GEBAEUDE = 8         # Felder: ein feindlicher Soldat so nah an einem unserer Gebaeude ist eine Bedrohung (Waechter seit 12.10.)
ZIEL_AM_GEBAEUDE = 6     # Felder: sein Laufziel so nah an einem unserer Gebaeude ebenso
ANGREIFER_R = 40         # 19.10.: Angreifer unserer Einheiten zaehlen nur bis hierhin von unseren Gebaeuden (nicht draussen)
VERTEIDIGUNG, RAID, WAECHTER = "verteidigung", "raid", "waechter"


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def an_gebaeuden(L, gebaeude, sp):
    """{feind: (Abstand zum naechsten unserer Gebaeude, Einheit)} der feindlichen Truppen an unseren Gebaeuden ([(x, y)])."""
    feinde = {}
    for n, e in L.items():
        if e["besitzer"] in (0, sp) or e["typ"] not in TRUPPE:
            continue
        ort, ziel = (e["x"], e["y"]), (e["laufx"], e["laufy"])
        nah_ort = min((schach(ort, g) for g in gebaeude), default=999)
        nah_ziel = min((schach(ziel, g) for g in gebaeude), default=999) if ziel != (0, 0) and ziel[0] > 0 else 999
        if nah_ziel <= ZIEL_AM_GEBAEUDE or nah_ort <= BEI_GEBAEUDE:
            feinde[n] = (min(nah_ort, nah_ziel), e)
    return feinde


def angreifer(L, gebaeude, sp, geschuetzt):
    """Feindliche Truppen, deren Nahziel oder Schussziel eine unserer Einheiten aus geschuetzt ist, bis ANGREIFER_R Felder von
    unseren Gebaeuden."""
    return {n for n, e in L.items() if e["besitzer"] not in (0, sp) and e["typ"] in TRUPPE
            and (e.get("nahziel") in geschuetzt or e.get("zieleinheit") in geschuetzt)
            and min((schach((e["x"], e["y"]), g) for g in gebaeude), default=0) <= ANGREIFER_R}


def bedrohungen(L, gebaeude, sp, geschuetzt):
    """an_gebaeuden und die Angreifer (Abstand 0)."""
    feinde = an_gebaeuden(L, gebaeude, sp)
    for n in angreifer(L, gebaeude, sp, geschuetzt):
        feinde.setdefault(n, (0, L[n]))
    return feinde


def verteilen(L, gebaeude, sp, kandidaten, geschuetzt, raid=True):
    """-> ({Einheit: VERTEIDIGUNG | RAID | WAECHTER}, Text). kandidaten: Einheiten, die keinem anderen Modul gehoeren und die der
    Nahkampf-Raid fuehren kann; raid: gibt es einen Nahkampf-Raid? VERTEIDIGUNG und WAECHTER fuehrt beide der Waechter - WAECHTER
    heisst: keine Gruppe gewinnt, er entscheidet wie bisher selbst."""
    kandidaten = sorted(n for n in kandidaten if n in L)
    frei = RAID if raid else WAECHTER
    feinde = bedrohungen(L, gebaeude, sp, geschuetzt)
    if not feinde:
        return {n: frei for n in kandidaten}, "keine Bedrohung - %d %s" % (len(kandidaten), frei)
    sie = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=True) for _, e in feinde.values()]
    wir = [dict(nr=n, typ=L[n]["typ"], leben=L[n]["leben"], x=L[n]["x"], y=L[n]["y"]) for n in kandidaten]
    gewaehlt, gewinnt, text = ZW.kleinste_gruppe(wir, sie)
    if not gewinnt:
        return {n: WAECHTER for n in kandidaten}, "Bedrohung %d Feinde, keine Gruppe gewinnt (%s) - alle beim Waechter" % (
            len(feinde), text)
    rollen = {n: (VERTEIDIGUNG if n in gewaehlt else frei) for n in kandidaten}
    return rollen, "Bedrohung %d Feinde: %d verteidigen (%s), %d %s" % (
        len(feinde), len(gewaehlt), text, len(kandidaten) - len(gewaehlt), frei)
