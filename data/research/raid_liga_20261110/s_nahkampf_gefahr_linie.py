# -*- coding: utf-8 -*-
"""B-182 (11.11. 21:50): Ziele des Nahkampf-Raids vom 10.11. nach der neuen Regel der Wegfuehrung - mit Schusslinie und Tarnung.

Regel (micro/wegfuehrung.Gefahr, Plan_Wegfuehrung.md Nachtrag 11.11. 20:45): ein gegnerischer Schuetze zaehlt nur in Reichweite
(schussfeld.REICHWEITE) UND mit freier Linie - ein nicht flaches Gebaeude dazwischen sperrt (L79), wer auf Turm, Torhaus oder
Bergfried steht, schiesst frei; Tuerme selbst zaehlen nicht; Nahkaempfer bis raids.GEFAHR_NAH. Standplatz eines Nahkaempfers ist das
Ziel selbst: bei einem Arbeiter zaehlt nicht, was auf seinem Feld steht, bei einem Gebaeude sperrt es keine Linie zu sich selbst.
Zum Vergleich im selben Lauf die Kreis-Regel von S115 (Schuetze, Turm oder Nahkaempfer im Kreis). Partien wie s_taeter_alle.py.
Aufruf (im Arbeitsordner): python data/research/raid_liga_20261110/s_nahkampf_gefahr_linie.py [<Stempel-Anfang, z. B. 20261110>]
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s_nahkampf_gefahr as K  # noqa: E402  (Kreis-Regel, S115)
import s_taeter_alle as TA  # noqa: E402

import selfaware.services.schussfeld as SF  # noqa: E402
from selfaware.baukasten import wirkung as WK  # noqa: E402
from selfaware.micro import wegfuehrung as W  # noqa: E402
from selfaware.telemetry import lageprotokoll as LP  # noqa: E402

SP = K.SP


def gefahr(bild, typ, art, z, ort):
    """(Zahl aller Gefahren, davon Nahkaempfer) am Standplatz nach der neuen Regel."""
    arbeiter = art in ("Arbeiter", "e")
    aus_ort = ort if arbeiter else None
    gesamt = bild.an(ort, typ, ausser_ort=aus_ort, ausser_gebaeude=None if arbeiter else z)
    nah = sum(1 for q in bild.nah if q != aus_ort and SF.luftlinie2(q, ort) <= bild.nah_r * bild.nah_r)
    return gesamt, nah


def main():
    ungueltig = set(open(f"{TA.F}/raid_liga_20261110/ungueltige_partien.txt", encoding="utf-8").read().split())
    summe = collections.Counter()
    wissen = WK.Wissen()
    freie = []
    print("Stempel         | Zuweisungen Gebaeude/Arbeiter | in Gefahr Kreis-Regel | in Gefahr mit Schusslinie")
    for s, k, lage in TA.paare():
        name = os.path.basename(k)
        if lage is None or name in ungueltig or "gegnerki5" in name:
            continue
        zuw, erl = K.zuweisungen(k)
        if not zuw:
            continue
        je = collections.Counter()
        i = 0
        for t, _st, E, B in LP.runden(lage):
            if i >= len(zuw):
                break
            if t < zuw[i][0]:
                continue
            L = {e["nr"]: e for e in E}
            G = {b["nr"]: b for b in B}
            bild = W.Gefahr(L, G, SP)
            wissen.lernen(L, SP)
            while i < len(zuw) and zuw[i][0] <= t:
                _t0, n, typ, art, z, ort = zuw[i]
                kreis = bool(K.quellen(L, G, ort, art == "Arbeiter"))
                ges, nah = gefahr(bild, typ, art, z, ort)
                je[(art, "zuweisungen")] += 1
                je[(art, "kreis")] += kreis
                je[(art, "linie")] += ges > 0
                je[(art, "linie schuetze")] += ges - nah > 0
                je[(art, "linie nur nahkampf")] += ges > 0 and ges == nah
                je[(art, "erledigt linie gefahr" if ges else "erledigt linie frei")] += (n, z) in erl
                freie.append(sum(1 for zz in WK.ziele(L, G, SP)
                                 if wissen.am_ziel(typ, zz)[1] > 0
                                 and not gefahr(bild, typ, zz.schluessel[0], zz.schluessel[1], zz.ort)[0]))
                i += 1
        print("%s | %4d / %4d | %4d / %4d | %4d / %4d" % (
            s, je[("Gebaeude", "zuweisungen")], je[("Arbeiter", "zuweisungen")], je[("Gebaeude", "kreis")], je[("Arbeiter", "kreis")],
            je[("Gebaeude", "linie")], je[("Arbeiter", "linie")]))
        summe.update(je)
    print()
    for art in ("Gebaeude", "Arbeiter"):
        z = summe[(art, "zuweisungen")]
        if z:
            print("%-8s Zuweisungen %4d | Kreis-Regel in Gefahr %4d (%d %%) | mit Schusslinie in Gefahr %4d (%d %%): Schuetze mit freier "
                  "Linie %d, nur Nahkaempfer %d | erledigt (behauptet) in Gefahr %d, frei %d" % (
                      art, z, summe[(art, "kreis")], round(100 * summe[(art, "kreis")] / z), summe[(art, "linie")],
                      round(100 * summe[(art, "linie")] / z), summe[(art, "linie schuetze")], summe[(art, "linie nur nahkampf")],
                      summe[(art, "erledigt linie gefahr")], summe[(art, "erledigt linie frei")]))
    if freie:
        f = sorted(freie)
        print("Freie Ziele mit Wirkung > 0 je Zuweisung (Schusslinie): Median %d, Viertel %d / %d; mindestens eines frei %d von %d" % (
            f[len(f) // 2], f[len(f) // 4], f[3 * len(f) // 4], sum(1 for x in f if x), len(f)))


if __name__ == "__main__":
    main()
