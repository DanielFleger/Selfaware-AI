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


def bericht(faelle):
    zeilen = []
    for art in ("STEHT NUR", "HAT ZIEL", "KAEMPFT"):
        f = faelle.get(art, [])
        typen = collections.Counter(t for _, _, t, _ in f)
        still = [s for _, _, _, s in f]
        mittel = statistics.median(still) if still else "-"
        zeilen.append(
            f"{art}: {len(f)} Meldungen, {len({n for _, n, _, _ in f})} Einheiten, "
            f"Typen {dict(typen.most_common(5))}, Standdauer Median {mittel} Takte"
        )
    return zeilen


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    with open(argv[0], encoding="utf-8", errors="replace") as f:
        zeilen = f.read().splitlines()
    ab = int(argv[1]) if len(argv) > 1 else 0
    for z in bericht(auswerten(zeilen[ab:])):
        print(z)


if __name__ == "__main__":
    main()
