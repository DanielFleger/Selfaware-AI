# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Obergrenzen in Takten und daraus die Laufzeit. Jede Eingangsgroesse nennt ihre Quelle; was noch nicht gemessen ist, steht unter UNGEMESSEN.
Die Grenzen sind Obergrenzen: Ein Durchgang endet, sobald alle seine Zellen fertig sind. Nach Probe und V1 rechnet das Programm sie mit den gemessenen Werten neu.

Aufruf: python data/research/auge_plan/lauf_s_plan/rechnung_dauer.py > data/research/auge_plan/lauf_s_plan/rechnung_dauer.txt
"""
import math

# Gemessen
TAKT_S_T40 = 0.026       # s je Takt, streng auf Tempo 40 (Lauf K, Fenster t1 bis t9: 2.002 Takte in rund 52 s)
TAKTE_S_T1000 = 766      # Takte je Sekunde im Kampf auf Tempo 1000 (Lauf K)
TAKTE_S_T200 = 200       # Stufenwert. Ob die Massenschlacht ihn haelt, misst A4
SCHUSS_ARMBRUST = 228    # Takte je Schuss (Editor 17.10., Handbuch), der langsamste gemessene Schuetze
ERSTER_TREFFER_SCHUSS = 411  # groesster Wert "erster Treffer nach dem Aufstellen" (Editor 17.10., Handbuch)
ERSTER_TREFFER_NAH = 251     # groesster Wert in den Duellen vom 18.10. (data/research/editor_duell_20261018_124723.jsonl)
SCHUSS_KATAPULT = 123    # Takte je Stein (Lauf K, kampf_takt_t9.txt)
MUNITION_HOECHSTENS = 40 # spawnUnit: 40, 20 oder 10 Steine, je nach Spielart und Spielerplatz
ZELLEN_60, ZELLEN_100 = 11 - 1, 5 - 1  # karte_flaeche.txt: Kern 12 bei Abstand 60, Kern 24 bei Abstand 80; je eine Zelle ist die Kontrolle ohne Befehl

# UNGEMESSEN (die Probe misst sie, bis dahin Annahme)
ABRAEUMEN = 400          # Takte Steintod; so lange wartet das alte Werkzeug shc.py, gemessen ist nur "reicht"
MARSCH_LAST = 5000       # Takte je Versuch V6, siehe Plan
SCHLACHT = 30000         # Takte je Massenschlacht, siehe Plan
V7_JE = 3000             # Takte je Sonderfall V7


def zeile(name, versuche, je_durchgang, grenze, tempo):
    d = math.ceil(versuche / je_durchgang)
    takte = d * (grenze + ABRAEUMEN)
    if tempo == 40:
        s = takte * TAKT_S_T40
    elif tempo == 200:
        s = takte / TAKTE_S_T200
    else:
        s = takte / TAKTE_S_T1000
    print("%-26s %4d Versuche, %2d je Durchgang, %3d Durchgaenge, Grenze %5d + %d, %7d Takte, Tempo %4d: %5.0f s" % (name, versuche, je_durchgang, d, grenze, ABRAEUMEN, takte, tempo, s))
    return s


s = 0
print("--- Abschnitt E, Editor")
s += zeile("V1 Reaktion, 3 Proben", 27 * 3, ZELLEN_60, 256 + 150, 40)       # groesste Maske 255, dazu Anmarsch 150 Takte
s += zeile("V1 Gehtempo, 30 Felder", 27, ZELLEN_60, 30 * 72 * 2, 200)       # Tempo 6 (Katapult), je Stufe gemessen rund 12 Takte je Feld (Register L80), mal 2 Sicherheit
s += zeile("V2 Duelle (190 von 361)", 190, ZELLEN_60, 2 * ERSTER_TREFFER_NAH, 40)
s += zeile("V3 Fussschuetzen", 6 * 19, ZELLEN_60, ERSTER_TREFFER_SCHUSS + 2 * SCHUSS_ARMBRUST, 40)
s += zeile("V3 Geraete", 3 * 19, ZELLEN_100, ERSTER_TREFFER_SCHUSS + 2 * SCHUSS_ARMBRUST, 40)  # Schusstakt der Geraete ungemessen: V1 misst ihn, dann neu
s += zeile("V3 laufendes Ziel, 10 Schuss", 9, ZELLEN_100, ERSTER_TREFFER_SCHUSS + 9 * SCHUSS_ARMBRUST, 40)
s += zeile("V4b Fusstruppen", 80, ZELLEN_60, 2 * ERSTER_TREFFER_NAH, 40)
s += zeile("V4 Belagerung", 492, ZELLEN_100, MUNITION_HOECHSTENS * SCHUSS_KATAPULT, 1000)
s += zeile("V6 Angriff auf einen Punkt", 8, 1, MARSCH_LAST, 200)
s += zeile("V7 Sonderfaelle", 11, 1, V7_JE, 40)
s += zeile("V5 Massenschlachten", 8, 1, SCHLACHT, 1000)
TREPPE = 3 * (20 / 1 + 100 / 10 + 1000 / 40 + 1000 / 100 + 1000 / 200 + 1000 / 500 + 1000 / 1000)  # Stufen und Takte wie Lauf F, ohne/mit/wieder ohne Lesen
print("A4 Tempotreppe je Durchgang %.0f s, zweimal (leere Karte, groesste Schlacht)" % TREPPE)
s += 2 * TREPPE
e = s
print("Abschnitt E zusammen: %.0f s = %.0f Minuten" % (e, e / 60))
print("--- Abschnitt G, Gegenprobe im Gefecht")
g = 0
g += zeile("V1 Reaktion, 3 Proben", 27 * 3, ZELLEN_60, 256 + 150, 40)
g += zeile("V1 Gehtempo", 27, ZELLEN_60, 30 * 72 * 2, 200)
g += zeile("V2 Stichprobe", 19, ZELLEN_60, 2 * ERSTER_TREFFER_NAH, 40)
g += zeile("V3 Stichprobe", 9, ZELLEN_60, ERSTER_TREFFER_SCHUSS + 2 * SCHUSS_ARMBRUST, 40)
g += zeile("V4 Stichprobe", 6, ZELLEN_100, MUNITION_HOECHSTENS * SCHUSS_KATAPULT, 1000)
g += zeile("V4b Stichprobe", 10, ZELLEN_60, 2 * ERSTER_TREFFER_NAH, 40)
print("Abschnitt G zusammen: %.0f s = %.0f Minuten" % (g, g / 60))
print("Obergrenze ohne Setzen, Laden, Kanal: %.0f Minuten" % ((e + g) / 60))
