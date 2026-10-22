"""B-210: one deterministic territory rule, applied before planning and building.

Coordinates come from measured keeps. Enemy proximity remains a separate safety
constraint. No game I/O, guessed keep locations or mutable global state.
"""


def abstand(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def besitzer(punkt, burgen):
    if not burgen:
        raise ValueError("Gebietsaufteilung braucht gemessene Bergfriede")
    return min((int(sp) for sp in burgen), key=lambda sp: (abstand(punkt, burgen[sp]), sp))


def eigene_seite(info):
    """Return a predicate shared by all opening resource/placement candidates."""
    spieler = int(info.get("spieler", 1))
    burgen = {int(sp): tuple(b["eingang"]) for sp, b in info.get("freund_bergfried", {}).items()}
    burgen[spieler] = tuple(info["bergfried_eingang"])
    feinde = [tuple(b["eingang"]) for b in info.get("feind_bergfried", {}).values()]

    def erlaubt(p):
        return besitzer(p, burgen) == spieler and all(
            abstand(p, burgen[spieler]) < abstand(p, f) for f in feinde
        )

    return erlaubt
