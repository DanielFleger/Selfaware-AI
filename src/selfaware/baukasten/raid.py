"""Der Raid als eigenes Modul (B-176, B-179, docs/plans/Plan_Baukasten.md, Schritt 4).

RaidEinsatz steuert Vorstoss, Deckung, Brandtrupp und Reiterjagd. RaidBestellung entscheidet, welche Raid-Einheiten eine Runde gekauft werden.
Beide sind Steckplaetze (raideinsatz, raidbestellung), eine Aufstellung kann also andere Versionen einsetzen.

RaidBestellung kauft wie vor B-179: erst die Assassine, dann die Soeldner, beide mit dem Gold vom Rundenanfang. In der Partie raid_frueh vom 09.11. kamen so
von 13 bestellten Berittenen Bogenschuetzen nur 3 an (data/research/raid_frueh_20261109/Ergebnis_Raid_frueh.md).
RaidBestellungMitKasse gibt das Gold einer Runde nur einmal aus und kauft in einer festen Reihenfolge: Was fehlt, geht vor, auch wenn das Gold erst spaeter reicht.
"""

import dataclasses

from selfaware.micro.tasks import raids as RA

ASSASSINE, ASSASSINE_GOLD = 73, 70  # SOELDNER_GOLD in erstes_spiel.py
# Daniel 09.11.: erst Sklaven, dann Berittene, dann Assassinen. Die Schleuderer stehen wie in raids.werbung vor den Reitern, mit deckung_soll 0 sind sie aus.
REIHENFOLGE = ("sklaven", "schleuderer", "reiter", "assassinen")
EINHEITEN = {
    "sklaven": (RA.SKLAVE, RA.SKLAVE_GOLD),
    "schleuderer": (RA.SCHLEUDER, RA.SCHLEUDER_GOLD),
    "reiter": (RA.PFERDEBOGEN, RA.PFERD_GOLD),
    "assassinen": (ASSASSINE, ASSASSINE_GOLD),
}


def reihenfolge_lesen(text):
    """Die Reihenfolge aus dem Schalter raid_reihenfolge. Jede Art genau einmal, sonst faellt es vor dem Start auf."""
    r = tuple(t.strip() for t in text.split(","))
    if sorted(r) != sorted(EINHEITEN):
        raise ValueError(
            f"raid_reihenfolge={text!r}: jede Art genau einmal aus {sorted(EINHEITEN)}"
        )
    return r


@dataclasses.dataclass(frozen=True)
class Lage:
    """Was die Bestellung einer Runde wissen muss. Die Bedingungen anderer Teile (Planer, Loewen am Posten, Ziele der Assassinen) rechnet der Lenker."""

    runde: int
    gold: int
    ruecklage: int
    ruecklage_soeldner: int
    feuer: int
    endspurt: bool
    soeldner_erlaubt: bool
    assassine_erlaubt: bool
    sklaven: int
    reiter: int
    schleuderer: int


class RaidBestellung:
    """Kauft wie vor B-179: Assassine und Soeldner rechnen getrennt mit dem Gold vom Rundenanfang, die Soeldner nur in ungeraden Runden und nicht im Endspurt."""

    def __init__(self, reihenfolge=REIHENFOLGE):
        self.reihenfolge = tuple(reihenfolge)

    def schritt(self, b):
        """[(Typ, Anzahl)] dieser Runde, in der Reihenfolge des Kaufs."""
        kaeufe = []
        if b.assassine_erlaubt and b.gold >= ASSASSINE_GOLD + b.ruecklage and b.feuer >= 1:
            kaeufe.append((ASSASSINE, 1))
        if b.soeldner_erlaubt and not b.endspurt and b.runde % 2 == 1:
            kaeufe += RA.werbung(
                b.gold - b.ruecklage_soeldner, b.feuer, b.sklaven, b.reiter, b.schleuderer
            )
        return kaeufe


class RaidBestellungMitKasse(RaidBestellung):
    """Eine Kasse fuer alle Raid-Einheiten: Was gekauft wird, fehlt dem naechsten. Fehlt eine Art weiter vorn, wartet alles dahinter, damit das Gold fuer sie zusammenkommt."""

    def _offen(self, art, b):
        """(wie viele fehlen, ob sie in dieser Runde gekauft werden duerfen). Soeldner, die gerade gar nicht geworben werden, halten niemanden auf."""
        if art == "assassinen":
            return (1, True) if b.assassine_erlaubt else (0, False)
        if not b.soeldner_erlaubt or b.endspurt:
            return 0, False
        soll, ist = {
            "sklaven": (RA.SKLAVEN_SOLL, b.sklaven),
            "schleuderer": (RA.DECKUNG_SOLL, b.schleuderer),
            "reiter": (RA.REITER_SOLL, b.reiter),
        }[art]
        return max(0, soll - ist), b.runde % 2 == 1

    def schritt(self, b):
        frei, feuer, kaeufe = b.gold - b.ruecklage, b.feuer, []
        for art in self.reihenfolge:
            fehlt, jetzt = self._offen(art, b)
            if not fehlt:
                continue
            if not jetzt:
                break
            typ, preis = EINHEITEN[art]
            bleibt_am_feuer = 0 if art == "assassinen" else RA.FEUER_MIN
            n = max(0, min(fehlt, frei // preis, feuer - bleibt_am_feuer))
            if n:
                kaeufe.append((typ, n))
                frei -= n * preis
                feuer -= n
            if n < fehlt:
                break
        return kaeufe


class RaidEinsatz:
    """Eine Runde Steuerung, Reihenfolge wie bisher: Vorstoss, Deckung, Brandtrupp, Reiterjagd. Der Brandtrupp meidet, was Deckung und Vorstoss abdecken."""

    def __init__(self, sp, bergfried, feuer, steck, vorstoss_bis=None):
        self.brand = steck.klasse("brandtrupp")(sp, feuer)
        self.reiter = steck.klasse("reiterjagd")(sp)
        self.deckung = steck.klasse("deckung")(sp, bergfried)
        self.vorstoss = (
            None
            if vorstoss_bis is None
            else steck.klasse("vorstoss")(sp, bergfried, bis=vorstoss_bis)
        )

    def schritt(self, t, L, G, befehl):
        aus = []
        if self.vorstoss is not None:
            self.vorstoss.plaetze_setzen(self.brand.im_ausweichen)
            aus += self.vorstoss.schritt(t, L, G, befehl)
        self.brand.schutz = self.deckung.orte(L) + (
            self.vorstoss.orte(L) if self.vorstoss is not None else []
        )
        aus += self.deckung.schritt(L, G, befehl, self.brand)
        aus += self.brand.schritt(L, G, befehl)
        aus += self.reiter.schritt(L, G, befehl)
        return aus
