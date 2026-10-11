# -*- coding: utf-8 -*-
"""Gegenprobe fuer sichere Fuenferwellen, ohne ein Spiel zu starten."""
import os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import erstes_spiel as E


def bauer(zustand=0, arbeitsplatz=0):
    return {"besitzer": E.SP, "typ": 1, "arbeitsplatz": arbeitsplatz, "zustand": zustand}


def main():
    pruefungen = []

    L = {10: bauer(109), 11: bauer(7, 5), 12: bauer(8, 5)}
    pruefungen.append(("Bergfriednummer 5 und Zustand 109 blockieren die echte Feuerzahl nicht",
                       not E.abwanderer_zuerst(L)))

    gesendet, alt = [], E.befehl
    E.befehl = lambda b, *a, **k: gesendet.append(b) or ["WERBE"]
    try:
        marken, aus = {}, []
        n = E.anwerbewelle({"t": 100, "T26": 10}, L, marken, aus, 77, 5)
        pruefungen.append(("Echte Feuerzahl sendet die volle Welle und merkt ihr exaktes Ziel",
                           n == 5 and len(gesendet) == 5 and marken["_werben_offen"]["ziel"] == 15))
        pruefungen.append(("Teilankunft gibt keine neue Welle frei",
                           not E.werbung_freigegeben({"t": 250, "T26": 14}, marken, [])))
        pruefungen.append(("Erst die vollstaendige Welle gibt die naechste frei",
                           E.werbung_freigegeben({"t": 300, "T26": 15}, marken, []) and "_werben_offen" not in marken))

        gesendet[:] = []
        marken, aus = {}, []
        n = E.anwerbewelle({"t": 350, "T26": 15}, {1: bauer(7, 5), 99: bauer(110, 5)}, marken, aus, 77, 5)
        pruefungen.append(("Irgendein sichtbarer Abwanderer sperrt die ganze neue Welle",
                           n == 0 and not gesendet and "_werben_offen" not in marken))

        gesendet[:] = []
        marken, aus = {}, []
        L5 = {i: bauer() for i in range(20, 27)}
        n = E.anwerbewelle({"t": 400, "T26": 48}, L5, marken, aus, 77, 2)
        pruefungen.append(("Restziel zwei sendet genau zwei statt fuenf",
                           n == 2 and len(gesendet) == 2 and marken["_werben_offen"]["ziel"] == 50))

        marken = {"_werben_offen": {"t": 0, "t26": 10, "menge": 5, "ziel": 15}}
        try:
            E.werbung_freigegeben({"t": 1200, "T26": 14}, marken, [])
            hart = False
        except RuntimeError:
            hart = True
        pruefungen.append(("Unvollstaendige Welle wird nie blind erneut gesendet", hart and "_werben_offen" in marken))

        # SAI 11.10. (Lauf 50,100 Tick 27.267: zweiter Befehl ohne Bauern kostete nichts - Gold nur einmal -20)
        marken, aus = {"_werben_offen": {"t": 0, "t26": 65, "menge": 2, "ziel": 67}}, []
        frei = E.werbung_freigegeben({"t": 1200, "T26": 66, "feuer": 0}, marken, aus)
        pruefungen.append(("Unvollstaendige Welle ohne Bauern am Feuer wird mit Meldung freigegeben",
                           frei and "_werben_offen" not in marken and any("unvollstaendig freigegeben" in a for a in aus)))
        marken = {"_werben_offen": {"t": 0, "t26": 65, "menge": 2, "ziel": 67}}
        try:
            E.werbung_freigegeben({"t": 1200, "T26": 66, "feuer": 3}, marken, [])
            hart = False
        except RuntimeError:
            hart = True
        pruefungen.append(("Unvollstaendige Welle MIT Bauern am Feuer bleibt harter Abbruch", hart))

        # SAI 11.10. Nomade-Lauf 1011j: im Kampf koennen Rekruten fallen - Freigabe mit Meldung statt Abbruch
        E.GEGNER_ERWARTET = "Nomade"
        marken, aus = {"_werben_offen": {"t": 0, "t26": 13, "menge": 5, "ziel": 18}}, []
        frei = E.werbung_freigegeben({"t": 1200, "T26": 17, "feuer": 3}, marken, aus)
        pruefungen.append(("Im Kampf (Nomade) wird 4/5 mit Bauern am Feuer freigegeben, mit Meldung",
                           frei and "_werben_offen" not in marken and any("Kampf gegen Nomade" in a for a in aus)))
        E.GEGNER_ERWARTET = ""
    finally:
        E.befehl = alt
        E.GEGNER_ERWARTET = ""

    for text, ok in pruefungen:
        print(("OK  " if ok else "ROT ") + text)
    print("%d von %d gruen" % (sum(ok for _, ok in pruefungen), len(pruefungen)))
    return 0 if all(ok for _, ok in pruefungen) else 1


if __name__ == "__main__":
    raise SystemExit(main())
