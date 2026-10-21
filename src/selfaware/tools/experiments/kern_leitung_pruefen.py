"""B-145 S4a: die Leitung im Spiel pruefen (Instanz ueber SHC_INSTANZ).

  python -m selfaware.tools.experiments.kern_leitung_pruefen [Sekunden]

1. Angehalten: Weltbild aus dem gemeinsamen Speicher = Weltbild-Datei des Kerns (kern_lagebild.txt) im selben Takt.
2. Laufend: so viele Sekunden lesen - wie viele der vergangenen Takte sieht Python, groesste Luecke.
"""

import os
import sys
import time

from selfaware.game.kern_leitung import Leitung
from selfaware.tools.experiments.kern_vergleich import lesen

SPALTEN = (
    "besitzer",
    "typ",
    "x",
    "y",
    "leben",
    "zustand",
    "laufx",
    "laufy",
    "gruppe",
    "zielart",
    "zieleinheit",
)


def main(argv=None):
    from selfaware.game.ucp.laden import SPIEL, befehl

    argv = sys.argv[1:] if argv is None else argv
    sekunden = float(argv[0]) if argv else 3.0
    vs = os.path.join(SPIEL, "ucp", "villagestudio")
    befehl({"pause": True}, 1.0)
    befehl({"kern": {"welt": True}}, 1.5, bis="KERN welt")
    leitung = Leitung(SPIEL)
    w = leitung.lesen()
    t_datei, _, e = lesen(os.path.join(vs, "kern_lagebild.txt"), True)
    ab = [
        (nr, s, w.einheiten[nr][s], e[nr][s])
        for nr in e
        if nr in w.einheiten
        for s in SPALTEN
        if str(w.einheiten[nr][s]) != e[nr][s]
    ]
    fehlen = sorted(set(e) ^ set(w.einheiten))
    print(
        f"Speicher {leitung.name}: Takt {w.tick} (Datei {t_datei}), Kern {w.kern}, Epoche {w.epoche}"
    )
    print(
        f"angehalten: {len(w.einheiten)} Einheiten, nur in einer Quelle {len(fehlen)}, abweichend {len(ab)} {ab[:3]}"
    )
    befehl({"pause": False}, 1.0)
    gesehen, ende = [], time.time() + sekunden
    while time.time() < ende:
        b = leitung.lesen()
        if b is not None and (not gesehen or b.tick != gesehen[-1]):
            gesehen.append(b.tick)
    befehl({"pause": True}, 1.0)
    luecken = [b - a for a, b in zip(gesehen, gesehen[1:], strict=False)]
    vergangen = gesehen[-1] - gesehen[0] if len(gesehen) > 1 else 0
    print(
        f"laufend {sekunden:.0f} s: {len(gesehen)} verschiedene Takte gesehen, {vergangen} vergangen, "
        f"groesste Luecke {max(luecken) if luecken else '-'} Takte"
    )
    return 0 if not ab and not fehlen else 1


if __name__ == "__main__":
    sys.exit(main())
