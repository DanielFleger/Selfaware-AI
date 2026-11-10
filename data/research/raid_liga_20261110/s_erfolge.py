# -*- coding: utf-8 -*-
"""Je Zuweisung: wie lange von der Zuweisung bis zum Erfolg, und wie viele Zuweisungen enden mit Erfolg? (B-182 Eichung)
Paart in der Mitschrift die Zuweisungszeile eines Moduls mit seiner Erfolgszeile fuer dieselbe Einheit und dasselbe Ziel.
Brandtrupp schreibt beides seit B-129, Reiterjagd und Nahkampf-Raid die Erfolge seit B-182. Ohne Erfolgszeilen: nur Zuweisungen.
Aufruf: python s_erfolge.py <konsole> [...]"""
import collections
import re
import statistics
import sys

import selfaware.services.spielwerte as SW

MUSTER = {
    ("Brandtrupp", "g"): (re.compile(r"BRANDTRUPP: Sklave (\d+) -> Gebaeude (\d+) \(Typ \d+\) bei \(\d+, \d+\), (\d+) Felder"),
                          re.compile(r"BRANDTRUPP: Sklave (\d+) hat Gebaeude (\d+) \(Typ \d+\) angezuendet"), 71),
    ("Reiterjagd", "e"): (re.compile(r"REITERJAGD: Reiter (\d+) jagt Arbeiter (\d+) \(Typ \d+\) in (\d+) Feldern"),
                          re.compile(r"REITERJAGD: Reiter (\d+) hat Arbeiter (\d+) erledigt"), 74),
    ("Nahkampf", "g"): (re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) -> Gebaeude (\d+) \(Typ \d+\) bei \(\d+, \d+\), \d+ Wegpunkte(?:, (\d+) Felder)?"),
                        re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) hat Gebaeude (\d+) erledigt"), 75),
    ("Nahkampf", "e"): (re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) -> Arbeiter (\d+) \(Typ \d+\) bei \(\d+, \d+\), \d+ Wegpunkte(?:, (\d+) Felder)?"),
                        re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) hat Arbeiter (\d+) erledigt"), 75),
}
for k in sys.argv[1:]:
    print("==", k.split("aufstellung_")[-1][:60])
    offen, dauer, weg, zuw, erfolg = {}, collections.defaultdict(list), collections.defaultdict(list), collections.Counter(), collections.Counter()
    for zeile in open(k, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(\d+) \|", zeile)
        if not m:
            continue
        t = int(m.group(1))
        for schl, (rz, re_erfolg, typ) in MUSTER.items():
            for x in rz.finditer(zeile):
                offen[(schl, x.group(1))] = (x.group(2), t, int(x.group(3) or 0))
                zuw[schl] += 1
            for x in re_erfolg.finditer(zeile):
                o = offen.pop((schl, x.group(1)), None)
                if o and o[0] == x.group(2):
                    erfolg[schl] += 1
                    dauer[schl].append(t - o[1])
                    weg[schl].append(o[2])
    for schl, (_, _, typ) in MUSTER.items():
        if not zuw[schl]:
            continue
        tempo = SW.takte_je_feld(typ, "trupp")
        z = "   %-10s %s: %4d Zuweisungen, %4d Erfolge (%3.0f %%)" % (schl[0], schl[1], zuw[schl], erfolg[schl], 100.0 * erfolg[schl] / zuw[schl])
        if dauer[schl]:
            am_ziel = [d - w * tempo for d, w in zip(dauer[schl], weg[schl])]
            z += " | Takte bis Erfolg Median %d | Weg Median %d Felder (%.1f Takte je Feld) | am Ziel Median %d" % (
                statistics.median(dauer[schl]), statistics.median(weg[schl]), tempo, statistics.median(am_ziel))
        print(z)
