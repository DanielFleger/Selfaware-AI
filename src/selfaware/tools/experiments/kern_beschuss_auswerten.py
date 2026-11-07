"""B-145: Beschusswache auswerten - wie oft und wie lange stehen eigene Kaempfer unter Beschuss herum?

  python -m selfaware.tools.experiments.kern_beschuss_auswerten <samurai_kern.log> [ab_zeile]

Zaehlt die "beschuss"-Meldungen (Kern ab Version 15) nach Art (KAEMPFT / HAT ZIEL / STEHT NUR) und Einheitentyp und gibt
fuer STEHT NUR die Standdauer bei Beginn der Meldung an. Das ist die Grundzahl, an der Verbesserungen des Feldzugs gemessen
werden ("STEHT NUR" soll gegen 0 gehen).
"""

import collections
import re
import statistics
import sys

MUSTER = re.compile(
    r"^beschuss tick (\d+): (KAEMPFT|HAT ZIEL|STEHT NUR) - Einheit (\d+) \(Typ (\d+), Zustand (-?\d+), "
    r"Zielart (-?\d+), Nahziel (-?\d+)\) bei \((-?\d+),(-?\d+)\) steht seit (\d+) Takten"
)


def auswerten(zeilen):
    """Zeilen des Kern-Protokolls -> {art: [(tick, nr, typ, still)]}."""
    faelle = collections.defaultdict(list)
    for z in zeilen:
        m = MUSTER.match(z)
        if m:
            tick, art, nr, typ, still = (
                int(m.group(1)),
                m.group(2),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(10)),
            )
            faelle[art].append((tick, nr, typ, still))
    return faelle


ENDE = re.compile(r"^beschuss tick (\d+): Einheit (\d+) - Ende")


def dauern(zeilen):
    """B-146: wie lange dauert jede Meldung (Beginn bis Ende)? -> {art: [takte]}, {art: Zahl ohne Ende}.
    Ohne Ende bleibt eine Meldung, wenn die Einheit stirbt oder das Protokoll vorher aufhoert - die Wache meldet dann kein
    Ende, ihre Dauer ist unbekannt und wird nicht geraten."""
    offen, fertig, ohne = {}, collections.defaultdict(list), collections.Counter()
    for z in zeilen:
        m = MUSTER.match(z)
        if m:
            nr = int(m.group(3))
            if nr in offen:
                ohne[offen[nr][1]] += 1
            offen[nr] = (int(m.group(1)), m.group(2))
            continue
        m = ENDE.match(z)
        if m and int(m.group(2)) in offen:
            beginn, art = offen.pop(int(m.group(2)))
            fertig[art].append(int(m.group(1)) - beginn)
    for _, art in offen.values():
        ohne[art] += 1
    return fertig, ohne


def bericht(faelle, dauer=None):
    fertig, ohne = dauer if dauer else ({}, {})
    zeilen = []
    for art in ("STEHT NUR", "HAT ZIEL", "KAEMPFT"):
        f = faelle.get(art, [])
        typen = collections.Counter(t for _, _, t, _ in f)
        still = [s for _, _, _, s in f]
        mittel = statistics.median(still) if still else "-"
        d = fertig.get(art, [])
        zeilen.append(
            f"{art}: {len(f)} Meldungen, {len({n for _, n, _, _ in f})} Einheiten, "
            f"Typen {dict(typen.most_common(5))}, Standdauer Median {mittel} Takte"
            + (
                f" | unter Beschuss bis Ende: Summe {sum(d)} Takte, Median {statistics.median(d) if d else '-'}, "
                f"laengste {max(d) if d else '-'}, ohne Ende (tot/Protokollende) {ohne.get(art, 0)}"
                if dauer
                else ""
            )
        )
    return zeilen


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    with open(argv[0], encoding="utf-8", errors="replace") as f:
        zeilen = f.read().splitlines()
    ab = int(argv[1]) if len(argv) > 1 else 0
    bis = int(argv[2]) if len(argv) > 2 else len(zeilen)
    for z in bericht(auswerten(zeilen[ab:bis]), dauern(zeilen[ab:bis])):
        print(z)


if __name__ == "__main__":
    main()
