"""B-145 S4a: Weltbild des SamurAI-Kerns aus dem gemeinsamen Speicher lesen - jeden Takt, ohne Dateikanal.

Der Kern (crates/samurai-kern/src/leitung.rs) schreibt in jedem neuen Spieltakt Kopf, Einheiten und Gebaeude in eine
benannte Speicherabbildung und legt ihren Namen in ucp/villagestudio/kern_leitung.txt ab. Ein Folgezaehler (ungerade =
wird gerade geschrieben) sorgt dafuer, dass nur ein vollstaendiges Bild genommen wird.
S4b: Python legt Auftraege in einen Ring im selben Speicher; der Kern arbeitet sie im naechsten Takt ab und schreibt je
Eintrag ein Ergebnis, spaeter auch den Fortgang (ERGEBNIS_NAMEN). P5: Eintraege tragen Vorrang, Frist und Auftraggeber.
B-169 (Aufbau 5): alles, was das Gehirn jeden Takt braucht (data/research/auge_plan/feldliste_gehirn.csv), dazu eigene Trupps
und alle Geschosse. Was die Sichtschranke nur fuer eigene Einheiten erlaubt (NUR_EIGEN), schwaerzt schon der Kern; hier fehlt
der Schluessel bei Fremden ganz, damit niemand eine 0 fuer einen echten Wert haelt.
"""

import mmap
import os
import struct
from dataclasses import dataclass, field
from operator import itemgetter

KENNUNG = int.from_bytes(b"SAMK", "little")
AUFBAU = 8  # 8 (14.11.2026, S148): Gebiet des Wegnetzes je Einheit, Datensatz 120 -> 124; 7 (S143): field320_0x413; 6 (S139)
KOPF, EINHEIT, GEBAEUDE, TRUPP, GESCHOSS = 64, 124, 20, 16, 40
MAX_EINHEITEN, MAX_GEBAEUDE, MAX_TRUPPS, MAX_GESCHOSSE = 2500, 2000, 1250, 3000
GEBAEUDE_START = KOPF + MAX_EINHEITEN * EINHEIT
TRUPP_START = GEBAEUDE_START + MAX_GEBAEUDE * GEBAEUDE
GESCHOSS_START = TRUPP_START + MAX_TRUPPS * TRUPP
VORRAT_START = GESCHOSS_START + MAX_GESCHOSSE * GESCHOSS
SPIELER, WAREN = 9, 25
RING_START = VORRAT_START + SPIELER * WAREN * 4
WARE_NAMEN = {
    2: "holz",
    3: "hopfen",
    4: "stein",
    6: "eisen",
    7: "pech",
    9: "weizen",
    10: "brot",
    11: "kaese",
    12: "fleisch",
    13: "apfel",
    14: "bier",
    15: "gold",
    16: "mehl",
    17: "bogen",
    18: "armbrust",
    19: "speer",
    20: "pike",
    21: "keule",
    22: "schwert",
    23: "leder",
    24: "ruestung",
}
RING_KOPF, RING_N, RING_EINTRAG = 16, 256, 32
# B-184 (15.11.2026): Ringkopf +8 = Plaetze, die SamurAI fuehrt, als Bitmaske (Bit p = Platz p); der Kern fuehrt nur deren Einheiten
EIGENE_PLAETZE = RING_START + 8
GROESSE = RING_START + RING_KOPF + RING_N * RING_EINTRAG
OFFEN = -(2**31)
UEBERNEHMEN, FREIGEBEN, LAUF, ANGRIFF_EINHEIT, ANGRIFF_GEBAEUDE = 1, 2, 17, 4, 9
AUSWEICHEN = 30  # B-174, B-178: a, b = Ziel, im Feld vorrang die Nummer des Trupps
# S155 (Kern 30, Daniel 15.11.2026 00:20 "Ja, Kern bauen"): ein Laufauftrag, den der Kern durchsetzt - kaempft die Einheit gegen einen
# anderen als den erlaubten Gegner (Zustand 106), legt er ihn jeden Takt neu in die Schlange; GEGNER_ERLAUBT: a = dieser Gegner, 0 = keiner
LAUF_DURCHSETZEN, GEGNER_ERLAUBT = 18, 19
DURCHSETZEN_AB = (
    30  # erste Kern-Version, die beide Arten kennt - ein aelterer lehnt sie als unbekannt ab
)
# S159 (Kern 32): an einen Laufauftrag haengt der Lenker die weiteren Wegpunkte (a, b = Ort) und zuletzt den Angriff (a = Ziel); der Kern
# gibt den naechsten Schritt im Takt, in dem die Einheit am jetzigen Wegpunkt ankommt
WEGPUNKT, DANACH_EINHEIT, DANACH_GEBAEUDE = 20, 21, 22
KETTE_AB = 32  # erste Kern-Version mit Wegpunktkette
VORRANG_REFLEX, VORRANG_FLUCHT, VORRANG_ANGRIFF, VORRANG_LAUFEN, VORRANG_ROUTINE = 1, 2, 3, 4, 5
ERG_DOPPELT, ERG_ANGENOMMEN, ERG_ABGESETZT, ERG_WIRKT, ERG_GEPARKT = 0, 1, 2, 3, 4
ERG_NICHT_UEBERNOMMEN, ERG_UNBEKANNT, ERG_FREMD = -4, -5, -6
ERG_VERFALLEN, ERG_FEHLER, ERG_EINHEIT_WEG, ERG_WIRKT_NICHT = -8, -9, -10, -11
ERGEBNIS_NAMEN = {
    ERG_DOPPELT: "doppelt",
    ERG_ANGENOMMEN: "angenommen",
    ERG_ABGESETZT: "abgesetzt",
    ERG_WIRKT: "wirkt",
    ERG_GEPARKT: "geparkt",
    ERG_NICHT_UEBERNOMMEN: "nicht uebergeben",
    ERG_UNBEKANNT: "unbekannte Art",
    ERG_FREMD: "fremde Einheit",
    ERG_VERFALLEN: "verfallen",
    ERG_FEHLER: "Fehler beim Absetzen",
    ERG_EINHEIT_WEG: "Einheit weg",
    ERG_WIRKT_NICHT: "wirkt nicht",
}
KOPF_FORMAT = "<IIIiIiIIIIIIiII"
EINHEIT_FORMAT = "<ii12h7i31h2x"
GEBAEUDE_FORMAT = "<i7h2x"
TRUPP_FORMAT = "<ii4h"
GESCHOSS_FORMAT = "<i10hiiff"
# Neue Felder (B-169) -> Feld des Spiels (units[].*)
EINHEIT_SPIELFELD = {
    "bild": "animationFrame",
    "bildzyklus": "animationCycleNumber",
    "schussziel_uid": "targetUID",
    "naechstesfeld": "nextTileUnk",
    "kletterstand": "climbingState",
    "zieluid": "targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID",
    "mauerfeld": "targetedBuildingTile",
    "feinx": "microXPosition",
    "feiny": "microYPosition",
    "gelaendehoehe": "terrainOrClimbHeight",
    "gebaeudehoehe": "buildingHeight",
    "schussx": "shootTargetMicroX",
    "schussy": "shootTargetMicroY",
    "schussz": "shootTargetZ",
    "wegindex": "currentIndexInPathPlan",
    "weglaenge": "totalSizeOfPathPlan",
    "feindabstand": "closestEnemyMicroDistance",
    "planx": "plannedDestinationX",
    "plany": "plannedDestinationY",
    "ziel": "target",
    "zielx": "targetX",
    "ziely": "targetY",
    "schusseinheit": "shootTargetedUnit",
    "tempo": "calculatedMovementSpeed",
    "wegbedarf": "destinationNeeded",
    "teilzustand": "substate",
    "nahangreifer": "attackedBy",
    "mauerx": "attackAtTileX",
    "mauery": "attackAtTileY",
    "getoetet": "killedFlagUnk",
    # S139 (Daniel 14.11.2026 20:56 "Ja, mitschreiben"): was giveTribeMoveInstruction je Einheit prueft, bevor es ihr ein Ziel gibt
    # (struct Unit, OpenSHC) - ein Laufbefehl, der nicht greift, zeigt damit seinen Grund
    "logikzustand": "logicalState",
    "laufmerker": "moveRelatedFlag",
    "sammelgang": "goToRallyPoint",
    "teleport": "usingTeleport",
    "sammelmerker": "rallyRelatedFlag",
    "beweglich": "moveableUnk",
    # S143 (Daniel 14.11.2026 22:48 "Ja, mitschreiben"): die letzte Bedingung des Marschbefehls, Bedeutung unbekannt - nur eigene
    "merker413": "field320_0x413",
}
# S148 (Daniel 14.11.2026 23:19 "Ja, mitschreiben"): Felder, die der Kern aus einer Kartenebene am Feld der Einheit liest -> Feld der
# Feldliste. gebiet: PathConnectionLayer an Feinposition / 8, wie logik.lua ZUGPRUEFUNG (Kartendaten, die jeder sieht)
EINHEIT_ABGELEITET = {"gebiet": "PathConnectionLayer[]"}
EINHEIT_FELDER = (
    "nr",
    "leben",
    "besitzer",
    "typ",
    "x",
    "y",
    "zustand",
    "laufx",
    "laufy",
    "gruppe",
    "zielart",
    "zieleinheit",
    "zielgebaeude",
    "nahziel",
    *EINHEIT_SPIELFELD,
    *EINHEIT_ABGELEITET,
)
# Sichtschranke: nur fuer eigene Einheiten (FAIRNESS R3, R4); Gegenprobe gegen die Liste in tests/test_kern_leitung.py
NUR_EIGEN = frozenset(
    {
        "schussziel_uid",
        "naechstesfeld",
        "zieluid",
        "mauerfeld",
        "schussx",
        "schussy",
        "schussz",
        "wegindex",
        "weglaenge",
        "feindabstand",
        "planx",
        "plany",
        "ziel",
        "zielx",
        "ziely",
        "schusseinheit",
        "tempo",
        "wegbedarf",
        "nahangreifer",
        "mauerx",
        "mauery",
        "laufmerker",
        "sammelgang",
        "teleport",
        "sammelmerker",
        "merker413",
    }
)
EINHEIT_BESITZER = EINHEIT_FELDER.index("besitzer")
EINHEIT_FREMD = tuple(n for n in EINHEIT_FELDER if n not in NUR_EIGEN)
_FREMDE_WERTE = itemgetter(*(i for i, n in enumerate(EINHEIT_FELDER) if n not in NUR_EIGEN))
GEBAEUDE_FELDER = (
    "nr",
    "typ",
    "besitzer",
    "x",
    "y",
    "leben",
    "feuer",
    "tor",
)  # feuer ab Kern 18 (B-150), vorher 0
TRUPP_FELDER = ("nr", "zielgebaeude_uid", "zustand", "zielx", "ziely", "zielgebaeude")
GESCHOSS_FELDER = (
    "nr",
    "typ",
    "zustand",
    "besitzer",
    "feinx",
    "feiny",
    "hoehe",
    "x",
    "y",
    "weg",
    "feuer",
    "feld",
    "richtung",
    "vcos",
    "vsin",
)


class FalscherAufbau(RuntimeError):
    """Kennung oder Aufbau-Fassung passen nicht zu diesem Leser."""


@dataclass(frozen=True)
class Weltbild:
    tick: int
    epoche: int
    ich: int
    kern: int
    graben_geplant: int
    graben_ausgehoben: int
    einheiten: dict
    gebaeude: dict
    vorrat: dict
    beschuss: int = 0
    trupps: dict = field(default_factory=dict)  # nur eigene (FAIRNESS F10)
    geschosse: dict = field(default_factory=dict)
    lord_feindabstand: int = 0  # eigener Lord


def _tabelle(format_, felder, puffer, start, schritt, anzahl):
    aus = {}
    for i in range(anzahl):
        werte = struct.unpack_from(format_, puffer, start + i * schritt)
        d = dict(zip(felder, werte, strict=True))
        aus[d["nr"]] = d
    return aus


def entpacken(puffer):
    """Bytes im Aufbau 6 -> Weltbild (vorrat: {spieler: {ware: menge}} fuer Spieler 1-8)."""
    kopf = struct.unpack_from(KOPF_FORMAT, puffer, 0)
    kennung, aufbau, _folge, tick, epoche, ich, ne, ng = kopf[:8]
    geplant, ausgehoben, kern, beschuss, lord_feindabstand, nt, nq = kopf[8:]
    if kennung != KENNUNG or aufbau != AUFBAU:
        raise FalscherAufbau(
            f"Kennung {kennung:#x} / Aufbau {aufbau}, erwartet {KENNUNG:#x} / {AUFBAU}"
        )
    einheiten = {}
    for i in range(min(ne, MAX_EINHEITEN)):
        werte = struct.unpack_from(EINHEIT_FORMAT, puffer, KOPF + i * EINHEIT)
        if werte[EINHEIT_BESITZER] == ich:
            e = dict(zip(EINHEIT_FELDER, werte, strict=True))
        else:
            e = dict(zip(EINHEIT_FREMD, _FREMDE_WERTE(werte), strict=True))
        einheiten[e["nr"]] = e
    gebaeude = _tabelle(
        GEBAEUDE_FORMAT, GEBAEUDE_FELDER, puffer, GEBAEUDE_START, GEBAEUDE, min(ng, MAX_GEBAEUDE)
    )
    trupps = _tabelle(TRUPP_FORMAT, TRUPP_FELDER, puffer, TRUPP_START, TRUPP, min(nt, MAX_TRUPPS))
    geschosse = _tabelle(
        GESCHOSS_FORMAT, GESCHOSS_FELDER, puffer, GESCHOSS_START, GESCHOSS, min(nq, MAX_GESCHOSSE)
    )
    vorrat = {}
    for sp in range(1, SPIELER):
        werte = struct.unpack_from(f"<{WAREN}i", puffer, VORRAT_START + sp * WAREN * 4)
        vorrat[sp] = {name: werte[w] for w, name in WARE_NAMEN.items()}
    return Weltbild(
        tick,
        epoche,
        ich,
        kern,
        geplant,
        ausgehoben,
        einheiten,
        gebaeude,
        vorrat,
        beschuss,
        trupps,
        geschosse,
        lord_feindabstand,
    )


class Leitung:
    """Leser fuer den gemeinsamen Speicher eines laufenden Spiels (Spielordner der Instanz)."""

    def __init__(self, spiel_ordner):
        self.pfad = os.path.join(spiel_ordner, "ucp", "villagestudio", "kern_leitung.txt")
        self.name = None
        with open(self.pfad, encoding="utf-8") as f:
            name, groesse = f.read().split()[:2]
        if int(groesse) != GROESSE:
            raise FalscherAufbau(f"Groesse {groesse}, erwartet {GROESSE}")
        self._verbinden(name)

    def _verbinden(self, name):
        self.name = name
        self.speicher = mmap.mmap(-1, GROESSE, tagname=name, access=mmap.ACCESS_WRITE)

    def neu_verbinden(self):
        """B-182 (Partie 12.11. 19:25): kern_leitung.txt nennt den Speicher des laufenden Spiels. Nach einem frischen Start schreibt der
        Kern sie erst mit der ersten Partie neu (19:25:42); Wache und Lenker hatten sie kurz davor gelesen, bekamen den Namen des alten
        Spielprozesses, und Windows legte unter ihm einen neuen, leeren Speicher an - sie lasen die ganze Partie nur Nullen, die
        Obergrenze lehnte alle 1.877 Werbungen ab. True, wenn die Datei einen anderen Namen nennt und neu verbunden wurde."""
        try:
            with open(self.pfad, encoding="utf-8") as f:
                name, groesse = f.read().split()[:2]
        except (OSError, ValueError):
            return False  # der Kern schreibt sie gerade
        if name == self.name or int(groesse) != GROESSE:
            return False
        self._verbinden(name)
        return True

    def folge(self):
        return struct.unpack_from("<I", self.speicher, 8)[0]

    def lesen(self, versuche=50):
        """Ein vollstaendiges Weltbild oder None, wenn der Kern in allen Versuchen gerade schrieb. Passt der Kopf nicht (leerer Speicher
        unter einem alten Namen), verbindet sie sich neu, wenn kern_leitung.txt inzwischen einen anderen Namen nennt."""
        try:
            return self._lesen(versuche)
        except FalscherAufbau:
            if not self.neu_verbinden():
                raise
            return self._lesen(versuche)

    def _lesen(self, versuche):
        for _ in range(versuche):
            vorher = self.folge()
            if vorher & 1:
                continue
            kopie = self.speicher[:]
            if self.folge() == vorher:
                return entpacken(kopie)
        return None

    def takt(self):
        """Spieltakt des Kerns; gegen ihn laufen die Fristen im Auftragsring."""
        return struct.unpack_from("<i", self.speicher, 12)[0]

    def eigene_plaetze_setzen(self, plaetze):
        """B-184 (15.11.2026): sagt dem Kern, welche Plaetze SamurAI fuehrt. Ohne das nimmt er den Platz des Menschen am Rechner
        und verweigert in einer Lobby-Partie (Mensch 1, SamurAI 2) jeden Befehl an SamurAIs Einheiten (Partie 34: 65.473-mal)."""
        maske = 0
        for p in plaetze:
            if not 1 <= int(p) <= 8:
                raise ValueError("Platz %r liegt nicht in 1..8" % (p,))
            maske |= 1 << int(p)
        if not maske:
            raise ValueError("keine Plaetze angegeben")
        struct.pack_into("<I", self.speicher, EIGENE_PLAETZE, maske)
        return maske

    def eigene_plaetze(self):
        """Die gesetzten Plaetze (leer = nicht gesetzt, der Kern nimmt dann den Platz des Menschen)."""
        maske = struct.unpack_from("<I", self.speicher, EIGENE_PLAETZE)[0]
        return [p for p in range(1, 9) if maske & (1 << p)]

    def auftrag(self, art, nr, a=0, b=0, vorrang=0, frist=0, auftraggeber=0):
        """Legt einen Auftrag in den Ring (Art UEBERNEHMEN/FREIGEBEN/LAUF/ANGRIFF_*); gibt seine Ring-Nummer zurueck.
        vorrang 0 = nach Art, frist 0 = ohne Frist (sonst Spieltakt), auftraggeber 0 = keiner benannt; bei UEBERNEHMEN steht
        der Auftraggeber in a. Ein Schreiber je Spiel: nur ein Python-Prozess darf Auftraege legen."""
        schreib = struct.unpack_from("<I", self.speicher, RING_START)[0]
        lese = struct.unpack_from("<I", self.speicher, RING_START + 4)[0]
        if (schreib - lese) % 2**32 >= RING_N:
            raise RuntimeError("Auftragsring voll - der Kern arbeitet nicht (Spiel angehalten?)")
        o = RING_START + RING_KOPF + (schreib % RING_N) * RING_EINTRAG
        struct.pack_into(
            "<8i", self.speicher, o, art, nr, a, b, OFFEN, vorrang, frist, auftraggeber
        )
        struct.pack_into("<I", self.speicher, RING_START, (schreib + 1) % 2**32)
        return schreib

    def lesbar(self, nummer):
        """Steht auf dem Platz dieses Auftrags noch er selbst? Der Ring ueberschreibt alte Eintraege."""
        schreib = struct.unpack_from("<I", self.speicher, RING_START)[0]
        return (schreib - nummer) % 2**32 <= RING_N

    def ergebnis(self, nummer):
        """Ergebnis eines Auftrags oder None, solange der Kern ihn noch nicht abgearbeitet hat."""
        lese = struct.unpack_from("<I", self.speicher, RING_START + 4)[0]
        if (lese - nummer) % 2**32 == 0 or (lese - nummer) % 2**32 > RING_N:
            return None
        o = RING_START + RING_KOPF + (nummer % RING_N) * RING_EINTRAG
        return struct.unpack_from("<i", self.speicher, o + 16)[0]


X = (1, 2)
