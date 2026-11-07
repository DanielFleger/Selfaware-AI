"""B-145 / L154: wie oft sieht wer das Spiel? (20.10.2026)

python -m selfaware.tools.experiments.takt_messen kern [Instanz]
    Abstaende der Zeilen "tick N einheiten" im Kern-Protokoll (samurai_kern.log, eine Zeile alle
    500 Takte) - genau 500 heisst: kein Takt fehlt.
python -m selfaware.tools.experiments.takt_messen runden <konsole> ...
    Takte zwischen zwei Runden des Python-Lenkers ("<tick> |"-Zeilen einer Mitschrift).
"""

import collections
import re
import statistics
import sys

SPIEL = r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz{}"
PROTOKOLL = r"\ucp\villagestudio\samurai_kern.log"


def kern(instanz="5"):
    pfad = SPIEL.format(instanz) + PROTOKOLL
    with open(pfad, encoding="utf-8", errors="replace") as f:
        t = [int(m.group(1)) for m in (re.match(r"tick (\d+) einheiten", z) for z in f) if m]
    d = [b - a for a, b in zip(t, t[1:], strict=False)]
    # groessere Spruenge und Rueckspruenge = Laden / neue Partie
    normal = [x for x in d if 0 < x < 1000]
    c = collections.Counter(normal)
    andere = sorted((k, n) for k, n in c.items() if k != 500)
    print(
        f"Kern-Protokoll Instanz {instanz}: {len(t)} Zeilen, {len(normal)} Abstaende im "
        f"Spielverlauf, davon genau 500 Takte: {c[500]}; andere: {andere}; "
        f"Spruenge (Laden/neue Partie): {len(d) - len(normal)}"
    )


def runden(dateien):
    for pfad in dateien:
        with open(pfad, encoding="utf-8", errors="replace") as f:
            t = [int(m.group(1)) for m in (re.match(r"^(\d+) \|", z) for z in f) if m]
        d = sorted(b - a for a, b in zip(t, t[1:], strict=False) if b > a)
        if d:
            print(
                f"{pfad}: {len(d)} Runden, Takte je Runde kleinste {d[0]}, "
                f"Median {statistics.median(d)}, groesste {d[-1]}"
            )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["kern"]:
        kern(*(argv[1:2] or ["5"]))
    elif argv[:1] == ["runden"] and len(argv) > 1:
        runden(argv[1:])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
