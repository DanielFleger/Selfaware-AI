# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S: Obergrenzen in Takten, daraus die erwartete Laufzeit. Jede Eingangsgroesse nennt ihre Quelle; was noch nicht gemessen ist, steht unter UNGEMESSEN.
Ein Durchgang endet, sobald alle seine Zellen fertig sind, die Takte sind also Obergrenzen. Die Sekunden sind keine Abbruchgrenze, sie sagen nur, was zu erwarten ist.
Nach der Probe und nach V1 rechnet das Programm die Grenzen mit den gemessenen Werten neu.

Vorher laufen lassen: karte_flaeche.py, zellen_je_art.py.
Aufruf: python data/research/auge_plan/lauf_s_plan/rechnung_dauer.py > data/research/auge_plan/lauf_s_plan/rechnung_dauer.txt
"""
import collections
import json
import math
import os

HIER = os.path.dirname(os.path.abspath(__file__))
Z = json.load(open(os.path.join(HIER, "zellen_je_art.json")))

# Gemessen
TAKT_S_T40 = 0.026       # s je Takt, streng auf Tempo 40 (Lauf K, Fenster t1 bis t9: 2.002 Takte in rund 52 s)
TAKTE_S_T200 = 200       # Stufenwert. Lauf F im Dorf: 199,46 (Ergebnis_Lauf_F.md)
TAKTE_S_T1000 = 766      # Takte je Sekunde im Kampf auf Tempo 1000 (Lauf K), dort rund 800 bis 1.400 belegte Plaetze
SCHUSS_ARMBRUST = 228    # Takte je Schuss (Editor 17.10., Handbuch), der langsamste gemessene Schuetze
ERSTER_TREFFER_SCHUSS = 411  # groesster Wert "erster Treffer nach dem Aufstellen" (Editor 17.10., Handbuch)
ERSTER_TREFFER_NAH = 251     # groesster Wert in den Duellen vom 18.10. (alte_schuesse.txt)
SCHUSS_KATAPULT = 123    # Takte je Stein (Lauf K, kampf_takt_t9.txt)
MUNITION_HOECHSTENS = 40 # spawnUnit: 40, 20 oder 10 Steine, je nach Spielart und Platz
# Aus tabellen.txt, Lauf K
STUFE = {"Tunnel": 1, "Bogen": 1, "Armbrust": 2, "Speer": 1, "Pike": 2, "Keule": 1, "Schwert": 3, "Ritter": 1, "Leiter": 1, "Ingenieur": 1, "Moench": 2, "aBogen": 1, "Sklave": 1, "Schleuder": 1, "Assassine": 1, "Pferdebogen": 1, "aSchwert": 2, "Feuerwerfer": 2, "Lord": 2}
STUFE_GERAET = {"Katapult": 6, "Feuerballiste": 5, "Schild": 4, "Ramme": 3, "Turm": 3}
MASKE = {"Tunnel": 127, "Bogen": 63, "Armbrust": 63, "Speer": 127, "Pike": 127, "Keule": 63, "Schwert": 127, "Ritter": 63, "Leiter": 255, "Ingenieur": 255, "Moench": 127, "aBogen": 63, "Sklave": 127, "Schleuder": 127, "Assassine": 127, "Pferdebogen": 63, "aSchwert": 127, "Feuerwerfer": 127, "Lord": 63}
MASKE_GERAET = {"Katapult": 127, "Trebuchet": 127, "Mangonel": 127, "Ballista": 63, "Feuerballiste": 63}  # Turm, Ramme, Schild: Maske 0, keine Pruefrunde laut updateUnits
FUSS_SCHUETZEN = ("Bogen", "Armbrust", "aBogen", "Schleuder", "Pferdebogen", "Feuerwerfer")

# UNGEMESSEN (die Probe misst sie, bis dahin Annahme)
ABRAEUMEN = 400          # Takte Steintod; so lange wartet das alte Werkzeug shc.py, gemessen ist nur "reicht"
TAKTE_JE_FELD_JE_STUFE = 12  # Register L80 fuer Stufe 1 und 2, darueber Annahme
MARSCH_LAST = 5000       # Takte je Versuch V6, siehe Plan
SCHLACHT = 30000         # Takte je Massenschlacht, siehe Plan
V7_JE = 3000             # Takte je Sonderfall V7


def zellen(art, bank):
    """Eine Zelle je Durchgang ist die Kontrolle."""
    n = len(Z[art][bank]) - 1
    assert n >= 1, (art, bank, "zu wenige Zellen")
    return n


def block(name, gruppen, art, bank, tempo):
    """gruppen: {Grenze in Takten: Anzahl Versuche}. Gleiche Grenzen laufen zusammen, damit kein kurzer Versuch auf einen langen wartet."""
    je = zellen(art, bank)
    takte = durchgaenge = versuche = 0
    for grenze, n in sorted(gruppen.items()):
        d = math.ceil(n / je)
        durchgaenge += d
        versuche += n
        takte += d * (grenze + ABRAEUMEN)
    s = takte * TAKT_S_T40 if tempo == 40 else takte / {200: TAKTE_S_T200, 1000: TAKTE_S_T1000}[tempo]
    print("%-34s %4d Versuche, %2d je Durchgang, %3d Durchgaenge, %7d Takte, Tempo %4d: %5.0f s" % (name, versuche, je, durchgaenge, takte, tempo, s))
    return s, takte


def gezaehlt(werte):
    return dict(collections.Counter(werte))


def v1(bank):
    gesamt = []
    gesamt.append(block("V1 Gehtempo Soldaten", gezaehlt(60 * s * TAKTE_JE_FELD_JE_STUFE * 2 for s in STUFE.values()), "bahn", bank, 200))
    gesamt.append(block("V1 Gehtempo Geraete", gezaehlt(60 * s * TAKTE_JE_FELD_JE_STUFE * 2 for s in STUFE_GERAET.values()), "geraet_bahn", bank, 200))
    # Fuenf Faelle je Art, je Grenze 2 Pruefrunden: Vorhersage auf den Takt genau (updateUnits Zeile 369), darum eine Probe je Fall
    gesamt.append(block("V1 Reaktion Soldaten, 5 Faelle", gezaehlt(2 * (m + 1) for m in MASKE.values() for _ in range(3)), "nah", bank, 40))
    gesamt.append(block("V1 Reaktion Soldaten, weit", gezaehlt(2 * (m + 1) for m in MASKE.values() for _ in range(2)), "bahn", bank, 40))
    gesamt.append(block("V1 Reaktion Geraete, 5 Faelle", gezaehlt(2 * (m + 1) for m in MASKE_GERAET.values() for _ in range(5)), "geraet", bank, 40))
    gesamt.append(block("V1 Reichweite Fussschuetzen", gezaehlt(60 * STUFE[n] * TAKTE_JE_FELD_JE_STUFE * 2 + ERSTER_TREFFER_SCHUSS for n in FUSS_SCHUETZEN), "weit", bank, 200))
    gesamt.append(block("V1 Reichweite Geraete, fahrend", gezaehlt(84 * STUFE_GERAET[n] * TAKTE_JE_FELD_JE_STUFE * 2 + ERSTER_TREFFER_SCHUSS for n in ("Katapult", "Feuerballiste")), "geraet_weit", bank, 200))
    gesamt.append(block("V1 Reichweite Geraete, stehend x 6", {ERSTER_TREFFER_SCHUSS * 2: 3 * 6}, "geraet_weit", bank, 40))
    return gesamt


GRENZE_NAH = ERSTER_TREFFER_NAH + 256  # groesste Pruefrunde: Maske 255
GRENZE_SCHUSS = ERSTER_TREFFER_SCHUSS + 2 * SCHUSS_ARMBRUST
GRENZE_LAUF = ERSTER_TREFFER_SCHUSS + 9 * SCHUSS_ARMBRUST
GRENZE_GERAET = MUNITION_HOECHSTENS * SCHUSS_KATAPULT
print("--- Abschnitt E, Editor")
e = v1("editor")
e.append(block("V2 Duelle (190 fuer 361 Zeilen)", {GRENZE_NAH: 190}, "nah", "editor", 40))
# Je Schuetze ein Ziel jeden Takt gelesen: Flugzeit und Schusstakt haengen vom Schuetzen ab. Der Rest auf Tempo 200: Treffer kommen hoechstens alle 56 Takte (Handbuch), gelesen wird rund alle 2 Takte.
e.append(block("V3 Fussschuetzen, Flugzeit", {GRENZE_SCHUSS: 6}, "nah", "editor", 40))
e.append(block("V3 Fussschuetzen, uebrige Ziele", {GRENZE_SCHUSS: 108}, "nah", "editor", 200))
e.append(block("V3 Geraete, Flugzeit", {GRENZE_SCHUSS: 3}, "geraet", "editor", 40))
e.append(block("V3 Geraete, uebrige Ziele", {GRENZE_SCHUSS: 54}, "geraet", "editor", 200))
e.append(block("V3 laufendes Ziel Fussschuetzen", {GRENZE_LAUF: 6}, "lauf", "editor", 40))
e.append(block("V3 laufendes Ziel Geraete", {GRENZE_LAUF: 3}, "geraet", "editor", 40))
e.append(block("V4b Fusstruppen", {GRENZE_NAH: 80}, "nah", "editor", 40))
e.append(block("V4 Belagerung", {GRENZE_GERAET: 492}, "geraet", "editor", 1000))
s = sum(x[0] for x in e)
sonder = [("V6 Angriff auf einen Punkt", 8 * (MARSCH_LAST + ABRAEUMEN) / TAKTE_S_T200, 8 * (MARSCH_LAST + ABRAEUMEN)),
          ("V7 Sonderfaelle", 11 * (V7_JE + ABRAEUMEN) * TAKT_S_T40, 11 * (V7_JE + ABRAEUMEN)),
          ("V5 Massenschlachten", 8 * (SCHLACHT + ABRAEUMEN) / TAKTE_S_T1000, 8 * (SCHLACHT + ABRAEUMEN))]
for n, sek, t in sonder:
    print("%-34s %7d Takte: %5.0f s" % (n, t, sek))
    s += sek
PHASEN = 11  # 5 x mit, 6 x ohne
WECHSEL = {40: 80, 100: 200, 200: 400, 500: 1000, 1000: 1000}
GROB = {1: 20, 10: 100}  # wie Lauf F: 3 Phasen. Bei so wenig Takten je Sekunde ist das Lesen in jeder Phase fertig, bevor der naechste Takt kommt
tt = sum(PHASEN * v for v in WECHSEL.values()) + sum(3 * v for v in GROB.values())
ts = sum(PHASEN * v / st for st, v in WECHSEL.items()) + sum(3 * v / st for st, v in GROB.items())
print("A4 Wechselprobe je Durchgang: %d Takte, %.0f s, zweimal (leere Karte, volle Last)" % (tt, ts))
s += 2 * ts
print("Abschnitt E zusammen: %.0f s = %.0f Minuten" % (s, s / 60))
print("--- Abschnitt G, Gegenprobe im Gefecht")
# Der Code fragt die Spielart beim Gehen ab (UpdateMaceman), nicht bei Pruefrunde und Schussweite (updateUnits, acquireShootTarget): Gehtempo ganz, Reaktion und Reichweite als Stichprobe
g = []
g.append(block("V1 Gehtempo Soldaten", gezaehlt(60 * s * TAKTE_JE_FELD_JE_STUFE * 2 for s in STUFE.values()), "bahn", "gefecht", 200))
g.append(block("V1 Gehtempo Geraete", gezaehlt(60 * s * TAKTE_JE_FELD_JE_STUFE * 2 for s in STUFE_GERAET.values()), "geraet_bahn", "gefecht", 200))
g.append(block("V1 Reaktion, je Maske eine Art", {2 * (m + 1): 5 for m in (63, 127, 255)}, "bahn", "gefecht", 40))
g.append(block("V1 Reichweite, Bogen und Katapult", {60 * 12 * 2 + ERSTER_TREFFER_SCHUSS: 1, 84 * 72 * 2 + ERSTER_TREFFER_SCHUSS: 1}, "geraet_weit", "gefecht", 200))
g.append(block("V2 Stichprobe", {GRENZE_NAH: 19}, "nah", "gefecht", 40))
g.append(block("V3 Stichprobe, 6 + 3", {GRENZE_SCHUSS: 9}, "geraet", "gefecht", 40))
g.append(block("V4 Stichprobe", {GRENZE_GERAET: 6}, "geraet", "gefecht", 1000))
g.append(block("V4b Stichprobe", {GRENZE_NAH: 10}, "nah", "gefecht", 40))
gs = sum(x[0] for x in g)
print("Abschnitt G zusammen: %.0f s = %.0f Minuten" % (gs, gs / 60))
print("Abschnitt K: 30.000 Takte auf Tempo 1000: %.0f s" % (30000 / TAKTE_S_T1000))
print("Obergrenze ohne Setzen, Laden, Kanal: %.0f Minuten" % ((s + gs + 30000 / TAKTE_S_T1000) / 60))
print("UNGEMESSEN: Abraeumen, Takte je Feld ab Stufe 3, Schusstakt der Geraete ausser Katapult, Takte je Sekunde bei 2.400 Einheiten (Lauf K hatte hoechstens rund 1.400)")
