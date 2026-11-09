"""Die drei Arten von Einheitenbestellungen (B-177, docs/plans/Plan_Baukasten.md).

Daniel 09.11.2026: "er rekrutiert erstmal 100% nur raids ... schalte vorerst defence recruit und attack recruit aus".
Raid: Sklaven, Berittene Bogenschuetzen, Schleuderer als Deckung, Assassinen. Angriff: Streitkolbenkaempfer, das Heer, der Endspurt.
Verteidigung: die Notwerbung. Der Schalter bestellung=raid laesst nur Raids zu; ohne Schalter werben alle wie bisher.
"""

ARTEN = ("raid", "angriff", "verteidigung")


class Bestellung:
    """Das Tor vor jeder Rekrutierstelle: Welche Arten duerfen werben?"""

    def __init__(self, text="alle"):
        wahl = [t.strip() for t in str(text).split(",") if t.strip()]
        if wahl == ["alle"]:
            wahl = list(ARTEN)
        falsch = [t for t in wahl if t not in ARTEN]
        if falsch or not wahl:
            raise ValueError(f"bestellung={text}: erlaubt sind alle oder {', '.join(ARTEN)}")
        self.erlaubt = frozenset(wahl)

    def darf(self, art):
        if art not in ARTEN:
            raise ValueError(f"unbekannte Art der Bestellung: {art}")
        return art in self.erlaubt

    def __str__(self):
        return ", ".join(a for a in ARTEN if a in self.erlaubt)
