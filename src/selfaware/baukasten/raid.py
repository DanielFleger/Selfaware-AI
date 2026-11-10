"""Der Raid als eigenes Modul (B-176, B-179, docs/plans/Plan_Baukasten.md, Schritt 4).

RaidEinsatz steuert Vorstoss, Deckung, Brandtrupp und Reiterjagd. RaidBestellung entscheidet, welche Raid-Einheiten eine Runde gekauft werden.
Beide sind Steckplaetze (raideinsatz, raidbestellung), eine Aufstellung kann also andere Versionen einsetzen.

RaidBestellung kauft wie vor B-179: erst die Assassine, dann die Soeldner, beide mit dem Gold vom Rundenanfang. In der Partie raid_frueh vom 09.11. kamen so
von 13 bestellten Berittenen Bogenschuetzen nur 3 an (data/research/raid_frueh_20261109/Ergebnis_Raid_frueh.md).
RaidBestellungMitKasse gibt das Gold einer Runde nur einmal aus und kauft in einer festen Reihenfolge: Was fehlt, geht vor, auch wenn das Gold erst spaeter reicht.
RaidBestellungNachWirkung hat keine feste Reihenfolge: Gekauft wird, was gegen die sichtbaren Ziele am meisten Wirkung je Gold hat (B-181).
"""

import dataclasses

from selfaware.baukasten import einheiten as EH
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import raids as RA

ASSASSINE, ASSASSINE_GOLD = 73, 70  # SOELDNER_GOLD in erstes_spiel.py
# Daniel 09.11.: erst Sklaven, dann Berittene, dann Assassinen. Die Schleuderer stehen wie in raids.werbung vor den Reitern, mit deckung_soll 0 sind sie aus.
REIHENFOLGE = ("sklaven", "schleuderer", "reiter", "assassinen")
# B-182: Was das Modul einer Art angreift - g Gebaeude, e Einheiten. In Reihe 1 (10.11.) traute die Rechnung Sklaven Arbeiter zu, die der
# Brandtrupp nie jagt, und kaufte darum nur Sklaven. Nahkaempfer des Nahkampf-Raids und Assassinen greifen beides an.
ZIELARTEN = {RA.SKLAVE: "g", RA.PFERDEBOGEN: "e", RA.SCHLEUDER: "e", 70: "e", ASSASSINE: "ge"}
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
    L: dict | None = None  # Lagebild und Gebaeude: nur die Bestellung nach Wirkung braucht sie
    G: dict | None = None
    sp: int = 1
    start: tuple | None = None  # Soeldnerposten, dort entstehen die Einheiten
    steuerbar: frozenset = frozenset()  # Arten, die ein Einsatz-Modul gerade fuehren kann
    belegt: frozenset = frozenset()  # Ziele, die schon eine eigene Einheit hat


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


class RaidBestellungNachWirkung(RaidBestellung):
    """Kauf nach Wirkung (B-181, Daniel 10.11.: keine feste Reihenfolge). In jeder ungeraden Runde die Art mit dem meisten Wert je Gold gegen
    die sichtbaren Ziele (baukasten/wirkung.py), bis Kasse, Leute am Feuer oder offene Ziele ausgehen. In Frage kommen nur Arten, die ein Modul
    auch fuehren kann, die am Soeldnerposten nur Gold kosten und die raiden duerfen; der Lord nie. Ziele, die schon jemand hat, zaehlen nicht."""

    def __init__(self, reihenfolge=REIHENFOLGE):
        super().__init__(reihenfolge)
        self.begruendung = []
        self._wissen = None

    @property
    def wissen(self):
        if self._wissen is None:
            self._wissen = WK.Wissen()
        return self._wissen

    def schritt(self, b):
        self.begruendung = []
        if b.L is None or b.G is None or b.start is None or b.endspurt or b.runde % 2 == 0:
            return []
        self.wissen.lernen(b.L, b.sp)
        preise = {}
        for typ in sorted(b.steuerbar):
            if not (EH.kaufbar_am_posten(typ) and EH.darf(typ, "raid")):
                continue
            if (typ == ASSASSINE and b.assassine_erlaubt) or (
                typ != ASSASSINE and b.soeldner_erlaubt
            ):
                preise[typ] = EH.ARTEN[typ].gold
        ziele = [z for z in WK.ziele(b.L, b.G, b.sp) if z.schluessel not in b.belegt]
        bleibt = {t: 0 if t == ASSASSINE else RA.FEUER_MIN for t in preise}
        kaeufe, self.begruendung = WK.kaufen(
            self.wissen,
            b.gold - b.ruecklage,
            b.feuer,
            preise,
            b.start,
            ziele,
            bleibt,
            {ASSASSINE: 1},
            ZIELARTEN,
        )
        return kaeufe


class RaidEinsatz:
    """Eine Runde Steuerung, Reihenfolge wie bisher: Vorstoss, Deckung, Brandtrupp, Reiterjagd, dazu der Nahkampf-Raid (B-181). Der Brandtrupp
    meidet, was Deckung und Vorstoss abdecken. Der Nahkampf-Raid fuehrt nur Einheiten, die fuer den Raid bestellt wurden."""

    def __init__(self, sp, bergfried, feuer, steck, vorstoss_bis=None, gelaende=None):
        self.brand = steck.klasse("brandtrupp")(sp, feuer)
        self.reiter = steck.klasse("reiterjagd")(sp)
        self.deckung = steck.klasse("deckung")(sp, bergfried)
        self.nahkampf = steck.klasse("nahkampfraid")(sp, gelaende)
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
        aus += self.nahkampf.schritt(L, G, befehl)
        return aus
