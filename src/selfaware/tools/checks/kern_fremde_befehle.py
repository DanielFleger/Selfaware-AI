"""Fairness-Pruefung des Rust-Kerns (B-182, 10.11.2026): Hat der Kern Befehle an Einheiten fremder Spieler abgesetzt?

Anlass: Kern 24 behielt sein Auftragsbuch ueber Partiewechsel und nahm den Platz vom heutigen Besitzer der Einheit. In den Reihen 13 bis 16
setzte er so zehntausende alte Auftraege an gegnerische Einheiten ab (ein Lord lief quer ueber die Karte vor unsere Burg). Kern 25 leert das
Buch bei jeder neuen Partie und verweigert fremde Einheiten. Diese Pruefung liest samurai_kern.log der Instanz, teilt es an den
Epochenwechseln in Partien und zaehlt je Partie abgesetzte Befehle je Spieler und Verweigerungen.

Aufruf: python -m selfaware.tools.checks.kern_fremde_befehle [--instanz 2] [--ich 1] [--letzte 5]
Rueckgabe 1, wenn in einer der gezeigten Partien Befehle an Einheiten eines anderen Spielers als --ich abgesetzt wurden.
"""

import argparse
import collections
import os
import re
import sys

_ABGESETZT = re.compile(
    r"haende tick \d+: Gruppe \d+, \d+ von \d+ Einheiten von Spieler (\d+),.* - abgesetzt"
)
_EPOCHE = re.compile(r"^epoche \d+ tick")


def partien(zeilen):
    """[(Zeilennummer des Beginns, {Spieler: abgesetzte Befehle}, Verweigerungen)] - eine Partie je Epochenwechsel."""
    aus = [(0, collections.Counter(), 0)]
    for i, z in enumerate(zeilen):
        if _EPOCHE.match(z):
            aus.append((i, collections.Counter(), 0))
            continue
        m = _ABGESETZT.search(z)
        if m:
            aus[-1][1][int(m.group(1))] += 1
        elif "VERWEIGERT - " in z and "Einheiten von Spieler" in z:
            beginn, je, verw = aus[-1]
            aus[-1] = (beginn, je, verw + 1)
    return aus


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--instanz", type=int, default=int(os.environ.get("SHC_INSTANZ", "2")))
    a.add_argument("--ich", type=int, default=1)
    a.add_argument("--letzte", type=int, default=5)
    arg = a.parse_args(argv)
    os.environ["SHC_INSTANZ"] = str(arg.instanz)
    from selfaware.game.ucp import befehl  # erst hier: der Ordner haengt an SHC_INSTANZ

    pfad = os.path.join(befehl.SPIEL, "ucp", "villagestudio", "samurai_kern.log")
    with open(pfad, encoding="utf-8", errors="replace") as f:
        liste = partien(f)
    fremd = False
    for beginn, je, verw in liste[-arg.letzte :]:
        andere = {s: n for s, n in je.items() if s != arg.ich}
        fremd |= bool(andere)
        print(
            "ab Zeile %d: abgesetzt %s | an fremde Spieler %s | verweigert %d%s"
            % (
                beginn,
                dict(je),
                andere or "keine",
                verw,
                "  <- FAIRNESS VERLETZT" if andere else "",
            )
        )
    return 1 if fremd else 0


if __name__ == "__main__":
    sys.exit(main())
