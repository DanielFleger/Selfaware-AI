# -*- coding: utf-8 -*-
"""B-142 Plan Lauf S, kurze Fassung: Obergrenze je Szene in Takten, daraus die Laufzeit. Setzen und Laden sind nicht gemessen und nicht enthalten.

Aufruf: python data/research/auge_plan/lauf_s_plan/rechnung_szenen.py > data/research/auge_plan/lauf_s_plan/rechnung_szenen.txt
"""
TAKTE_JE_S = {40: 1 / 0.026, 100: 100, 200: 200, 500: 500, 1000: 766}  # 40 und 1000: Lauf K, gemessen. 200 und 500: Stufenwert, Lauf F im Dorf gemessen. Bei 2.400 Einheiten ungemessen
SZENEN = [
    ("1 Laufen: 24 Arten, ein Besitzer, 20 Felder", [(200, 20 * 72 * 2)]),  # Tempo-Wert 6 (Katapult) je rund 12 Takte (L80), Annahme; mal 2
    ("2 Nahkampf: 190 Paare dicht", [(40, 251 + 256)]),  # groesster erster Treffer 18.10. plus groesste Pruefrunde
    ("3a Beschuss: 171 Paare", [(40, 411 + 2 * 228)]),  # erster Treffer plus 2 Schuesse Armbrust
    ("3b Reichweite: alle Schuetzen auf je eine Ramme", [(200, 32 * 72 * 2)]),  # Start 10 Felder hinter Tabellenwert 57; bis 32 Felder Weg, Katapult
    ("3c Laufendes Ziel, 5 Schuss", [(200, 411 + 4 * 228)]),
    ("4 Haltung: 3 Arten, 5 Faelle", [(200, 2 * 512)]),  # 2 Pruefrunden der groessten Maske
    ("5a Fusstruppen gegen Gebaeude: 80 Paare", [(40, 251 + 256)]),
    ("5b Belagerung: 82 Ziele Katapult, je Geraet 6 Klassen", [(1000, 40 * 123)]),  # hoechstens 40 Steine, 123 Takte je Stein (Lauf K)
    ("6a Angriff auf einen Punkt: 8 zugleich", [(200, 5000)]),
    ("6b Sonderfaelle: 11 zugleich", [(40, 3000)]),
    ("7a Schlachten: 20, 1000, 500 Schuetzen, 500 Araber", [(1000, 4 * 10000)]),
    ("7b Lesen unter Last, 2.400 Einheiten", [(1000, 11 * 1000), (500, 3 * 1000), (200, 3 * 400), (100, 3 * 200), (40, 3 * 80)]),
    ("8a Gegenprobe Gefecht: Szenen 1, 2, 3a, 5b", [(200, 20 * 72 * 2), (40, 251 + 256), (40, 411 + 2 * 228), (1000, 40 * 123)]),
    ("8b Lauf-K-Stand, laufende KI", [(1000, 30000)]),
]
summe = 0
for name, teile in SZENEN:
    s = sum(t / TAKTE_JE_S[v] for v, t in teile)
    summe += s
    print("%-55s %7d Takte  %4.0f s" % (name, sum(t for _, t in teile), s))
print("Zusammen %.0f s = %.1f Minuten, ohne Setzen und Laden. Die Takte sind Obergrenzen: Eine Szene endet, sobald sie fertig ist." % (summe, summe / 60))
