"""Einheiten-Katalog (B-181): jede Art mit Herkunft, Preis, Rollen und Kampfart.

Gold der arabischen Soeldner: SOELDNER_GOLD im Lenker (gemessen 12.10.). Streitkolbenkaempfer: KAEMPFER_GOLD (Liga goldCost).
Das Anwerbegold der uebrigen europaeischen Arten ist nicht gemessen (None). Sie brauchen dazu Kaserne und Waffen, darum kauft der Raid sie heute nicht.
Der Lord ist nie kaufbar und darf nur verteidigen, nie raiden oder angreifen (Daniel 10.11.2026).
Leben und Schaden stehen nicht hier, sondern kommen gemessen aus baukasten/wirkung.py.
"""

import dataclasses

ROLLEN = ("raid", "angriff", "verteidigung")
ALLE = frozenset(ROLLEN)
LORD = 55


@dataclasses.dataclass(frozen=True)
class Art:
    typ: int
    name: str
    herkunft: str  # soeldnerposten, kaserne, gilde, kathedrale, keine
    gold: int | None  # None: nicht gemessen
    waren: tuple  # Waffen und Ruestung fuer die Kaserne
    rollen: frozenset
    kampf: str  # nah, fern, geraet


ARTEN = {
    a.typ: a
    for a in (
        Art(22, "Bogenschuetze", "kaserne", None, ("bogen",), ALLE, "fern"),
        Art(23, "Armbrustschuetze", "kaserne", None, ("armbrust", "lederruestung"), ALLE, "fern"),
        Art(24, "Speertraeger", "kaserne", None, ("speer",), ALLE, "nah"),
        Art(25, "Pikenier", "kaserne", None, ("pike", "metallruestung"), ALLE, "nah"),
        Art(
            26,
            "Streitkolbenkaempfer",
            "kaserne",
            20,
            ("streitkolben", "lederruestung"),
            ALLE,
            "nah",
        ),
        Art(27, "Schwertkaempfer", "kaserne", None, ("schwert", "metallruestung"), ALLE, "nah"),
        Art(28, "Ritter", "kaserne", None, ("schwert", "metallruestung", "pferd"), ALLE, "nah"),
        Art(29, "Leitertraeger", "gilde", None, (), frozenset({"angriff"}), "geraet"),
        Art(30, "Ingenieur", "gilde", None, (), frozenset({"angriff", "verteidigung"}), "geraet"),
        Art(5, "Tunnelgraeber", "gilde", None, (), frozenset({"angriff"}), "geraet"),
        Art(37, "Moench", "kathedrale", None, (), ALLE, "nah"),
        Art(70, "Arabischer Bogenschuetze", "soeldnerposten", 60, (), ALLE, "fern"),
        Art(71, "Sklave", "soeldnerposten", 5, (), ALLE, "nah"),
        Art(72, "Schleuderer", "soeldnerposten", 12, (), ALLE, "fern"),
        Art(73, "Assassine", "soeldnerposten", 70, (), ALLE, "nah"),
        Art(74, "Berittener Bogenschuetze", "soeldnerposten", 75, (), ALLE, "fern"),
        Art(75, "Arabischer Schwertkaempfer", "soeldnerposten", 100, (), ALLE, "nah"),
        Art(76, "Feuerwerfer", "soeldnerposten", 125, (), ALLE, "fern"),
        Art(LORD, "Lord", "keine", None, (), frozenset({"verteidigung"}), "nah"),
    )
}


def darf(typ, rolle):
    """Darf diese Art diese Rolle uebernehmen? Unbekannte Arten duerfen nichts."""
    art = ARTEN.get(typ)
    return art is not None and rolle in art.rollen


def kaufbar_am_posten(typ):
    """Kann der Soeldnerposten diese Art jetzt nur mit Gold anwerben?"""
    art = ARTEN.get(typ)
    return art is not None and art.herkunft == "soeldnerposten" and art.gold is not None


def name(typ):
    art = ARTEN.get(typ)
    return art.name if art else "Typ %d" % typ
