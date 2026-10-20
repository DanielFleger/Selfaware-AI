"""B-145 / L154: wie oft sieht wer das Spiel? (20.10.2026)

  python werkzeug/takt_messen.py kern  [Instanz]        Abstaende der Zeilen im Kern-Protokoll (samurai_kern.log, eine Zeile
                                                        alle 500 Takte) - genau 500 heisst: der Kern laeuft in jedem Takt
  python werkzeug/takt_messen.py runden <konsole> ...   Takte zwischen zwei Runden des Python-Lenkers ("<tick> |"-Zeilen)
"""
import collections
import re
import statistics
import sys


def kern(instanz="5"):
    pfad = (r"C:\Program Files (x86)\Steam\steamapps\common\Stronghold Crusader Extreme Instanz%s\ucp\villagestudio"
            r"\samurai_kern.log" % instanz)
    t = [int(m.group(1)) for m in (re.match(r"tick (\d+)", z) for z in open(pfad)) if m]
    d = [b - a for a, b in zip(t, t[1:])]
    normal = [x for x in d if 0 < x < 1000]          # groessere Spruenge und Rueckspruenge = Laden / neue Partie
    c = collections.Counter(normal)
    print("Kern-Protokoll Instanz %s: %d Zeilen, %d Abstaende im Spielverlauf, davon genau 500 Takte: %d; andere: %s; "
          "Spruenge (Laden/neue Partie): %d" % (instanz, len(t), len(normal), c[500],
                                                  sorted((k, n) for k, n in c.items() if k != 500), len(d) - len(normal)))


def runden(dateien):
    for f in dateien:
        t = [int(m.group(1)) for m in (re.match(r"^(\d+) \|", z) for z in open(f, encoding="utf-8", errors="replace")) if m]
        d = sorted(b - a for a, b in zip(t, t[1:]) if b > a)
        if d:
            print("%s: %d Runden, Takte je Runde kleinste %d, Median %s, groesste %d" % (f, len(d), d[0], statistics.median(d), d[-1]))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "kern":
        kern(*(sys.argv[2:3] or ["5"]))
    elif len(sys.argv) > 2 and sys.argv[1] == "runden":
        runden(sys.argv[2:])
    else:
        print(__doc__)
