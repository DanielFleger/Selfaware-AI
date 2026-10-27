# -*- coding: utf-8 -*-
"""B-277 Zielboerse, Reiter-Verteilung, Neubau-Wechsel der Jaeger, Direktlauf nach abgelehnter Wegkette, ehrliche Gruende.
Soll vorher festgelegt (Plan_Haende_Zielboerse.md, Daniel 23:16 "ja"):
  1. erste Runde meldet nichts; ein neues Feindgebaeude in der zweiten Runde steht in NEU und in einer NEUBAU-Zeile
  2. ein neues eigenes/verbuendetes Gebaeude steht NICHT in NEU
  3. AN = False -> NEU leer, keine Zeile
  4. zwei Reiter, zwei Arbeiter -> zwei verschiedene Ziele (225742: 310 und 311 jagten beide 369)
  5. zwei Reiter, ein Arbeiter -> beide auf ihn, mit Zeile "teilt Ziel"
  6. Assassine jagt einen Arbeiter 60 Felder weg, Neubau beim Feind, freies Gebaeude 10 Felder weg -> NEUBAU-WECHSEL, Ziel Gebaeude
  7. dasselbe ohne Neubau -> die Jagd bleibt
  8. Wegkette einer Einheit abgelehnt -> ihre naechste Wegkette geht als Direktlauf zum SELBEN Endpunkt; die andere Einheit im
     selben Befehl behaelt die Wegkette
  9. Befehle ohne Wegkette (Angriff auf Ziel) bleiben unberuehrt
 10. die Ablehnungszeile nennt, was auffaellt (Ziel an einem Gebaeude)
 11. C: liefert das Gefahrenraster keinen Weg, heisst der Grund "kein Weg im groben Gefahrenraster", nicht "lohnt nicht"
Aufruf: python zielboerse_pruefen.py"""
import copy
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import parteien
parteien.setzen(1, {1})
import zielboerse as Z
import besitzbuch as B
import raids as R
import assassinen as A
from funde_pruefen import neu, einheit


def befehle():
    liste = []

    def sende(b, warte=1.0, bis=None):
        liste.append(b)
        return []
    return liste, sende


def main():
    faelle = []
    feind = lambda b: b not in (1, 0, None)
    # 1-3
    Z.reset()
    G1 = {5: {"besitzer": 2, "typ": 3, "x": 50, "y": 50, "uid": 11}}
    r1 = list(Z.runde(G1, feind))
    G2 = dict(G1); G2.update({6: {"besitzer": 2, "typ": 30, "x": 60, "y": 50, "uid": 12}, 7: {"besitzer": 1, "typ": 3, "x": 9, "y": 9, "uid": 13}})
    r2 = list(Z.runde(G2, feind))
    faelle.append(("1 erste Runde still, Neubau 6 erkannt", r1 == [] and [v[0] for v in r2] == [6]
                   and any("NEUBAU" in m and "Gebaeude 6" in m for m in Z.MELDUNGEN)))
    faelle.append(("2 eigenes Gebaeude 7 nicht gemeldet", all(v[0] != 7 for v in r2)))
    Z.AN = False
    G3 = dict(G2); G3[8] = {"besitzer": 2, "typ": 3, "x": 70, "y": 50, "uid": 14}
    r3 = list(Z.runde(G3, feind))
    Z.AN = True
    faelle.append(("3 AN=False -> nichts", r3 == [] and Z.MELDUNGEN == []))
    # 4-5 Reiter
    from raids_pruefen import RATEN
    rj = R.Reiterjagd(1, raten=RATEN)
    L4 = {20: einheit(74, 1, 100, 100, leben=15000), 21: einheit(74, 1, 100, 104, leben=15000),
          700: einheit(3, 2, 115, 100, leben=1000), 701: einheit(3, 2, 115, 104, leben=1000)}
    b4, s4 = befehle()
    aus4 = rj.schritt(L4, {}, s4)
    ziel4 = {}
    for b in b4:
        a = b.get("angriff", {})
        for n in a.get("einheiten", []):
            ziel4[n] = a.get("ziel") or tuple(a.get("lauf") or ())
    faelle.append(("4 zwei Reiter, zwei Arbeiter -> verschiedene Ziele %s" % ziel4,
                   len(ziel4) == 2 and ziel4.get(20) != ziel4.get(21)))
    rj5 = R.Reiterjagd(1, raten=RATEN)
    L5 = {20: einheit(74, 1, 100, 100, leben=15000), 21: einheit(74, 1, 100, 104, leben=15000), 700: einheit(3, 2, 115, 100, leben=1000)}
    b5, s5 = befehle()
    aus5 = rj5.schritt(L5, {}, s5)
    z5 = {n: b["angriff"].get("ziel") for b in b5 for n in b["angriff"].get("einheiten", [])}
    faelle.append(("5 ein Arbeiter -> beide, mit 'teilt Ziel' %s" % z5, z5.get(20) == 700 and z5.get(21) == 700
                   and any("teilt Ziel 700" in z for z in aus5)))

    # 6-7 Assassine: Jagd + Neubau
    def jaeger(mit_neubau):
        t = neu()
        L = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000), 700: einheit(3, 2, 160, 100, leben=1000)}
        G = {900: {"besitzer": 2, "typ": 3, "x": 110, "y": 100, "leben": 100, "uid": 1, "erreichbar": 1}}
        t.aufnehmen([100])
        t.jagd[100] = 700
        Z.NEU[:] = [(900, 3, 110, 100)] if mit_neubau else []
        erg, _b = t.schritt(L, G, sichere_orte=[(50, 50)], tick=10000)
        Z.NEU[:] = []
        return t, erg
    t6, e6 = jaeger(True)
    faelle.append(("6 Neubau: Jaeger wechselt aufs Gebaeude (Ziel %s, Jagd %s)" % (t6.ziel.get(100), t6.jagd.get(100)),
                   t6.ziel.get(100) == 900 and 100 not in t6.jagd and any("NEUBAU-WECHSEL 100" in z for z in e6)))
    t7, e7 = jaeger(False)
    faelle.append(("7 ohne Neubau: Jagd bleibt (Ziel %s, Jagd %s)" % (t7.ziel.get(100), t7.jagd.get(100)),
                   t7.ziel.get(100) is None and not any("NEUBAU-WECHSEL" in z for z in e7)))

    # 8-10 Besitzbuch: Direktlauf nach abgelehnter Wegkette, Ursache
    B.LETZTER.clear(); B.ABGELEHNT.clear(); B.KETTE_ABGELEHNT.clear(); B._STILL.clear()
    kette = {"befehle": [{"player": 1, "id": 1, "angriff": {"einheiten": [30, 31], "lauf": [110, 100], "danach": [[120, 100], [130, 90]],
                                                         "trupp": 1}}]}
    LZ = {30: {"besitzer": 1, "typ": 74, "x": 100, "y": 100, "zustand": 1, "laufx": 100, "laufy": 100},
          31: {"besitzer": 1, "typ": 74, "x": 100, "y": 104, "zustand": 1, "laufx": 101, "laufy": 104}}
    B.steh_runde(5000, LZ, 1, {74})
    B.merken(copy.deepcopy(kette))
    abl = B.steh_runde(5100, LZ, 1, {74})
    b8, m8 = B.filtern(copy.deepcopy(dict(kette, befehle=[dict(kette["befehle"][0], angriff=dict(kette["befehle"][0]["angriff"],
                                                                                                   lauf=[111, 100]))])))
    ang = [c["angriff"] for c in (b8 or {}).get("befehle", [])]
    direkt = [a for a in ang if a["einheiten"] == [30]]
    rest = [a for a in ang if a["einheiten"] == [31]]
    faelle.append(("8 Wegkette von 30 abgelehnt -> Direktlauf %s, 31 behaelt Kette %s" % (direkt, rest),
                   direkt and direkt[0]["lauf"] == [130, 90] and "danach" not in direkt[0]
                   and rest and rest[0].get("danach") and any("Direktlauf" in m for m in m8)))
    b9, m9 = B.filtern({"angriff": {"einheiten": [30], "ziel": 777}})
    faelle.append(("9 Angriff auf Ziel unberuehrt", b9 == {"angriff": {"einheiten": [30], "ziel": 777}} and m9 == []))
    LU = {32: {"besitzer": 1, "typ": 74, "x": 100, "y": 100, "zustand": 1, "laufx": 100, "laufy": 100},
          888: {"besitzer": 2, "typ": 3, "x": 120, "y": 100, "zustand": 1}}
    B.steh_runde(5200, LU, 1, {74})
    B.merken({"angriff": {"einheiten": [32], "ziel": 888}})
    abl10 = B.steh_runde(5300, LU, 1, {74}, {44: {"besitzer": 2, "typ": 3, "x": 121, "y": 100}})
    faelle.append(("10 Ablehnung nennt Auffaelliges: %s" % [z[-90:] for z in abl10 if "ABGELEHNT 32" in z],
                   any("ABGELEHNT 32" in z and "auffaellig" in z and "Gebaeude" in z for z in abl10)
                   and any("ABGELEHNT 30" in z and "Wegkette" in z for z in abl)))

    # 11 C: Gefahrenraster ohne Weg
    t11 = neu()

    class OhneWeg:
        def risiko_von(self, ort, tempo):
            return {}

        def zelle_von(self, p):
            return (p[0] // 4, p[1] // 4)
    t11._gitter = lambda L, G=None: OhneWeg()
    L11 = {100: einheit(73, 1, 100, 100), 500: einheit(55, 2, 390, 390, leben=30000)}
    G11 = {900: {"besitzer": 2, "typ": 3, "x": 110, "y": 100, "leben": 100, "uid": 1, "erreichbar": 1}}
    t11.aufnehmen([100])
    try:
        e11, _ = t11.schritt(L11, G11, sichere_orte=[(50, 50)], tick=10000)
        grund = (t11._ablehnung.get(100) or {}).get(900, (None, None, ""))[2]
    except Exception as ex:
        e11, grund = [], "FEHLER %r" % (ex,)
    faelle.append(("11 kein Rasterweg ehrlich benannt: %r" % grund, grund.startswith("kein Weg im groben Gefahrenraster")
                   and any("kein Rasterweg" in z for z in e11)))

    for name, ok in faelle:
        print("%s %s" % ("OK  " if ok else "ROT ", name))
    print("%d von %d gruen" % (sum(bool(ok) for _, ok in faelle), len(faelle)))
    return all(ok for _, ok in faelle)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
