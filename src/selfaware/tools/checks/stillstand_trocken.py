# -*- coding: utf-8 -*-
"""Trockenprobe fuer stillstand.py (SAI 11.10.): gestellte Lagen, kein Spiel. Rueckgabe 0 = alle Faelle wie erwartet.
Gegenprobe: mit 'sabotage' wird HANDELN_AB auf 10**9 gesetzt - dann MUSS Fall A rot werden, sonst prueft die Probe nichts.
Aufruf: uv run python -m selfaware.tools.checks.stillstand_trocken [sabotage]"""
import sys
import selfaware.runtime.live.stillstand as S

if "sabotage" in sys.argv:
    S.HANDELN_AB = 10 ** 9


def lauf(einheit, teile_mengen, dauer, lager_stopp=False, offen=False):
    gebaut = []
    G = {100 + i: {"besitzer": 1, "typ": 10} for i in range(len(teile_mengen))}
    G[999] = {"besitzer": 1, "typ": 19}
    w = S.Stillstand(1, lambda n: teile_mengen[n - 100], lambda: gebaut.append(1) or (150, 262), lambda: offen)
    L0 = {7: dict(einheit, besitzer=1)}
    w.schritt(1000, L0, G)
    L1 = {7: dict(L0[7], x=einheit["x"] + (1 if einheit.get("laeuft") else 0))}
    ev = w.schritt(1000 + dauer, L1, G, lager_stopp=lager_stopp)
    return len(gebaut), ev


BAUER = {"typ": 11, "x": 186, "y": 249, "zustand": 9, "ladung": 0, "arbeitsplatz": 27}     # gemessen: Zustand 9, Ladung 0
MUELLER = {"typ": 15, "x": 152, "y": 261, "zustand": 6, "ladung": 1, "arbeitsplatz": 28}
FAELLE = [
    ("A Getreidebauer wartet 300 mit Weizen, alle Teile belegt -> anbauen", BAUER, [48, 48, 10, 6], 300, {}, 1),
    ("B wie A, aber ein Teil leer -> nicht anbauen", BAUER, [48, 0, 10, 6], 300, {}, 0),
    ("C wie A, erst 200 Ticks -> nichts", BAUER, [48, 48, 10, 6], 200, {}, 0),
    ("D Mueller mahlt 700 mit Ware, alle Teile belegt -> nicht anbauen", MUELLER, [48, 48, 10, 6], 700, {}, 0),
    ("E Mueller steht 1.500 mit Ware, alle Teile belegt -> anbauen", MUELLER, [48, 48, 10, 6], 1500, {}, 1),
    ("F wie A, Endphase lager_stopp -> nicht anbauen", BAUER, [48, 48, 10, 6], 300, {"lager_stopp": True}, 0),
    ("G wie A, Lagerbau schon offen -> nicht anbauen", BAUER, [48, 48, 10, 6], 300, {"offen": True}, 0),
    ("H Bauer laeuft -> nichts", dict(BAUER, laeuft=True), [48, 48, 10, 6], 300, {}, 0),
    ("I Soldat ohne Arbeitsplatz -> nichts", dict(BAUER, arbeitsplatz=0), [48, 48, 10, 6], 1500, {}, 0),
    ("J Bauer bei der Feldarbeit (Zustand 3), 1.500 still -> nichts", dict(BAUER, zustand=3), [48, 48, 10, 6], 1500, {}, 0),
    ("L Holzfaeller Zustand 7 ohne Holz, alle Teile belegt -> nichts", {"typ": 3, "x": 176, "y": 263, "zustand": 7, "ladung": 0,
                                                                        "arbeitsplatz": 23}, [48, 48, 10, 6], 1500, {}, 0),
    ("M Holzfaeller Zustand 7 mit 18 Holz, alle Teile belegt -> anbauen", {"typ": 3, "x": 176, "y": 263, "zustand": 7, "ladung": 18,
                                                                         "arbeitsplatz": 23}, [48, 48, 10, 6], 300, {}, 1),
    ("K Ochse mit Stein 1.500 still, Lager hat Platz -> melden, nicht anbauen", {"typ": 9, "x": 87, "y": 266, "zustand": 1,
                                                                                 "ladung": 8, "arbeitsplatz": 36}, [48, 0, 10, 6], 1500, {}, 0),
]
fehler = 0
for name, e, teile, dauer, opt, soll in FAELLE:
    ist, ev = lauf(e, teile, dauer, **opt)
    ok = ist == soll and (not ev if name.startswith(("C", "D", "H", "I", "J", "L")) else True) and (bool(ev) if name.startswith(("A", "E", "F", "G", "K", "M")) else True)
    fehler += not ok
    print("%s  %s | gebaut %d (soll %d) | %s" % ("OK  " if ok else "ROT ", name, ist, soll, ev[0][:110] if ev else "-"))
print("ERGEBNIS: %d von %d wie erwartet" % (len(FAELLE) - fehler, len(FAELLE)))
raise SystemExit(1 if fehler else 0)
