# -*- coding: utf-8 -*-
"""Gegenprobe "Waffenlager nie voll" (Daniel 11.10. 14:29) ohne Spiel: vorrat, Bauen und Anwerben werden ersetzt.
Soll je Fall vorher festgelegt; Aufruf: python waffenlager_pruefen.py"""
import erstes_spiel as E

# Liga-Preise (liga_ai.json; Waffenlager steht in keiner Balance-Datei: 5 Holz) - sonst fragt preis() das Spiel
E._KOSTEN_SPIEL.update({11: {"holz": 5, "stein": 0, "gold": 0}, 9: {"holz": 0, "stein": 12, "gold": 0}})


class Buch:
    def __init__(self, offen=()):
        self.offen = list(offen)


def fall(name, drin_keule, drin_leder, lager, kaserne, gold=500, holz=20, stein=20, feuer=10, ziel=100, t26=0,
         im_bau=False, soll_lager=False, soll_werben=0, soll_kaserne=False):
    gebaut, geworben = [], []
    E.vorrat = lambda sp=1: {"keule": drin_keule, "leder": drin_leder}
    E.baue_schnell = lambda typ, x, y, r, **k: gebaut.append(typ) or (x, y)
    E.kaserne_am_feuer = lambda G: gebaut.append(9) or (1, 1)
    E.anwerbewelle = lambda st, L, marken, aus, kas, werben: geworben.append(min(5, werben)) or min(5, werben)
    E.BUCH = Buch([{"typ": 11}] if im_bau else [])
    p = E.Produktion.__new__(E.Produktion)
    p.ziel, p.marken = ziel, {}
    eig = {i: {"typ": 11, "x": 100 + i, "y": 100} for i in range(lager)}
    if kaserne:
        eig[99] = {"typ": 9, "x": 1, "y": 1}
    waffenlager = [g for g in eig.values() if g["typ"] == 11]
    p.waffenlager_nie_voll({"t": 1000, "T26": t26}, {}, eig, waffenlager, gold, holz, stein, feuer)
    ok = ((11 in gebaut) == soll_lager and (9 in gebaut) == soll_kaserne and sum(geworben) == soll_werben)
    print("%s %-55s Lager %s, Kaserne %s, angeworben %d" % ("OK  " if ok else "FEHL", name, 11 in gebaut, 9 in gebaut, sum(geworben)))
    return ok


erg = [
    fall("1 Lager, 30 belegt: nichts tun", 15, 15, 1, True),
    fall("1 Lager, 36 belegt (14 frei): zweites Lager, kein Gold", 18, 18, 1, True, soll_lager=True),
    fall("1 Lager, 47 belegt (3 frei): Lager + 5 Paare anwerben", 24, 23, 1, True, soll_lager=True, soll_werben=5),
    fall("2 Lager, 47 belegt (53 frei): nichts tun", 24, 23, 2, True),
    fall("1 Lager voll, ohne Kaserne: Kaserne bauen", 25, 25, 1, False, soll_lager=True, soll_kaserne=True),
    fall("1 Lager voll, Lager schon im Bau: nur anwerben", 25, 25, 1, True, im_bau=True, soll_werben=5),
    fall("1 Lager voll, nur 1 Bauer frei: 1 anwerben", 25, 25, 1, True, feuer=1, soll_lager=True, soll_werben=1),
    fall("1 Lager voll, Ziel schon erreicht: nicht anwerben", 25, 25, 1, True, t26=100, soll_lager=True),
]
print("%d von %d gruen" % (sum(erg), len(erg)))
raise SystemExit(0 if all(erg) else 1)
