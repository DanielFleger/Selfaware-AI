# -*- coding: utf-8 -*-
"""B-182 Wegfuehrung (11.11.): Wie viele Ziele des Nahkampf-Raids lagen bei der Zuweisung in Gefahr nach der Regel der Wegfuehrung?

Regel (micro/wegfuehrung.py): Der Standplatz eines Nahkaempfers ist das Ziel selbst. Gefahr = ein sichtbarer gegnerischer Schuetze
(Reichweite wie schussfeld.REICHWEITE), Nahkaempfer (raids.GEFAHR_NAH) oder Turm erreicht ihn - als Kreis; bei einem
Arbeiter zaehlt nur, was nicht auf seinem eigenen Feld steht. Je Zuweisung (Mitschrift: "NAHKAMPF-RAID: n (Typ t) -> ... bei (x, y)")
die erste Lage-Runde ab ihrem Takt. Partien wie s_taeter_alle.py: ohne ungueltige_partien.txt und ohne die Attrappe KI 5.
"Erledigt" sind die Erfolgszeilen des Moduls - behauptet, nicht belegt (S111).
Aufruf (im Arbeitsordner): python data/research/raid_liga_20261110/s_nahkampf_gefahr.py [<Stempel-Anfang, z. B. 20261110>]
Seit 11.11. 21:50 rechnet die Wegfuehrung mit Schusslinie und Tarnung; dieses Skript zaehlt weiter nach der Kreis-Regel (S115),
die neue Regel zaehlt s_nahkampf_gefahr_linie.py (S116).
"""
import collections
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s_taeter_alle as TA  # noqa: E402

import selfaware.services.schussfeld as SF  # noqa: E402
from selfaware.baukasten import wirkung as WK  # noqa: E402
from selfaware.micro.tasks import raids as RA  # noqa: E402
from selfaware.telemetry import lageprotokoll as LP  # noqa: E402

SP = 1
ZUW = re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ (\d+)\) -> (Gebaeude|Arbeiter) (\d+) \(Typ \d+\) bei \((\d+), (\d+)\)")
ERL = re.compile(r"NAHKAMPF-RAID: (\d+) \(Typ \d+\) hat (Gebaeude|Arbeiter) (\d+) erledigt")


def zuweisungen(konsole):
    zuw, erl = [], set()
    for zeile in open(konsole, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(\d+) \|", zeile)
        if not m:
            continue
        t = int(m.group(1))
        for n, typ, art, z, x, y in ZUW.findall(zeile):
            zuw.append((t, int(n), int(typ), art, int(z), (int(x), int(y))))
        for n, _art, z in ERL.findall(zeile):
            erl.add((int(n), int(z)))
    return sorted(zuw), erl


def quellen(L, G, zielort, arbeiter):
    """Welche Arten von Gefahr den Standplatz erreichen (Turm, Schuetze, Nahkaempfer)."""
    def weg_vom_ziel(liste):
        return [g for g in liste if tuple(g[0]) != zielort] if arbeiter else liste
    turm_r = max(SF.REICHWEITE.values())
    tuerme = [((g["x"], g["y"]), turm_r) for g in G.values() if g.get("besitzer") not in (0, SP) and g.get("typ") in RA.TUERME]
    schuetzen = list(SF.schuetzen(L, SP))
    nah = [((e["x"], e["y"]), RA.GEFAHR_NAH) for e in L.values()
           if e.get("besitzer") not in (0, SP) and e.get("typ") in RA.NAH and e.get("leben", 1) > 0]
    aus = set()
    for name, liste in (("Turm", tuerme), ("Schuetze", schuetzen), ("Nahkaempfer", nah)):
        if SF.gefahr_am(zielort, weg_vom_ziel(liste)):
            aus.add(name)
    return aus


def main():
    ungueltig = set(open(f"{TA.F}/raid_liga_20261110/ungueltige_partien.txt", encoding="utf-8").read().split())
    summe = collections.Counter()
    besitzer = set()
    wissen = WK.Wissen()
    freie = []  # je Zuweisung: Zahl der Ziele, an denen diese Art etwas ausrichtet (Wirkung > 0) und die frei von Gefahr waren
    abstand = []  # Luftlinie zum naechsten gegnerischen Schuetzen, je Zuweisung mit Ziel in Gefahr
    print("Stempel         | Gegner        | Zuweisungen Gebaeude/Arbeiter | davon in Gefahr | erledigt (behauptet): in Gefahr / frei")
    for s, k, lage in TA.paare():
        name = os.path.basename(k)
        if lage is None or name in ungueltig or "gegnerki5" in name:
            continue
        zuw, erl = zuweisungen(k)
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
            besitzer |= {e["besitzer"] for e in E} | {b["besitzer"] for b in B}
            while i < len(zuw) and zuw[i][0] <= t:
                _t0, n, _typ, art, z, ort = zuw[i]
                wissen.lernen(L, SP)
                q = quellen(L, G, ort, art == "Arbeiter")
                je[(art, "zuweisungen")] += 1
                je[(art, "gefahr")] += bool(q)
                for name_q in q:
                    je[(art, "quelle " + name_q)] += 1
                je[(art, "erledigt gefahr" if q else "erledigt frei")] += (n, z) in erl
                d = [math.hypot(e["x"] - ort[0], e["y"] - ort[1]) for e in E if e["besitzer"] not in (0, SP) and e["typ"] in SF.REICHWEITE]
                if q and d:
                    abstand.append(min(d))
                # B: gab es daneben freie Ziele? (Wirkung > 0 fuer diese Art, Regel wie oben)
                freie.append(sum(1 for zz in WK.ziele(L, G, SP)
                                 if wissen.am_ziel(_typ, zz)[1] > 0 and not quellen(L, G, zz.ort, zz.schluessel[0] == "e")))
                i += 1
        gegner = re.search(r"(gegnerki\d+|_gn_i2|_pp_|_bf_|_bb_)", name)
        print("%s | %-13s | %4d / %4d | %4d / %4d | %d / %d" % (
            s, gegner.group(1) if gegner else "-", je[("Gebaeude", "zuweisungen")], je[("Arbeiter", "zuweisungen")],
            je[("Gebaeude", "gefahr")], je[("Arbeiter", "gefahr")],
            je[("Gebaeude", "erledigt gefahr")] + je[("Arbeiter", "erledigt gefahr")],
            je[("Gebaeude", "erledigt frei")] + je[("Arbeiter", "erledigt frei")]))
        summe.update(je)
    print()
    print("Besitzer im Lageprotokoll: %s (0 = niemand, %d = wir)" % (sorted(besitzer), SP))
    if abstand:
        a = sorted(abstand)
        print("Ziel in Gefahr: naechster gegnerischer Schuetze Median %.1f Felder Luftlinie, Viertel %.1f / %.1f, n = %d" % (
            a[len(a) // 2], a[len(a) // 4], a[3 * len(a) // 4], len(a)))
    if freie:
        f = sorted(freie)
        print("Freie Ziele mit Wirkung > 0 je Zuweisung: Median %d, Viertel %d / %d; Zuweisungen mit mindestens einem freien Ziel %d von %d" % (
            f[len(f) // 2], f[len(f) // 4], f[3 * len(f) // 4], sum(1 for x in f if x), len(f)))
    for art in ("Gebaeude", "Arbeiter"):
        z, g = summe[(art, "zuweisungen")], summe[(art, "gefahr")]
        if z:
            print("%-8s Zuweisungen %4d, davon Ziel in Gefahr %4d (%d %%); Quelle Turm %d, Schuetze %d, Nahkaempfer %d; "
                  "erledigt (behauptet) in Gefahr %d, frei %d" % (
                      art, z, g, round(100 * g / z), summe[(art, "quelle Turm")], summe[(art, "quelle Schuetze")],
                      summe[(art, "quelle Nahkaempfer")], summe[(art, "erledigt gefahr")], summe[(art, "erledigt frei")]))


if __name__ == "__main__":
    main()
