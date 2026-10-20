"""B-145 S4a: Weltbild des SamurAI-Kerns aus dem gemeinsamen Speicher lesen - jeden Takt, ohne Dateikanal.

Der Kern (crates/samurai-kern/src/leitung.rs) schreibt in jedem neuen Spieltakt Kopf, Einheiten und Gebaeude in eine
benannte Speicherabbildung und legt ihren Namen in ucp/villagestudio/kern_leitung.txt ab. Ein Folgezaehler (ungerade =
wird gerade geschrieben) sorgt dafuer, dass nur ein vollstaendiges Bild genommen wird.
S4b (Aufbau 2): Python legt Auftraege in einen Ring im selben Speicher; der Kern arbeitet sie im naechsten Takt ab und
schreibt je Eintrag ein Ergebnis (1 angenommen, 0 doppelt, -4 nicht uebergeben, -5 unbekannte Art).
"""

import mmap
import os
import struct
from dataclasses import dataclass

KENNUNG = int.from_bytes(b"SAMK", "little")
AUFBAU = 3
KOPF, EINHEIT, GEBAEUDE = 64, 32, 16
MAX_EINHEITEN, MAX_GEBAEUDE = 2500, 2000
VORRAT_START = KOPF + MAX_EINHEITEN * EINHEIT + MAX_GEBAEUDE * GEBAEUDE
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
RING_KOPF, RING_N, RING_EINTRAG = 16, 256, 20
GROESSE = RING_START + RING_KOPF + RING_N * RING_EINTRAG
OFFEN = -(2**31)
UEBERNEHMEN, FREIGEBEN, LAUF, ANGRIFF_EINHEIT, ANGRIFF_GEBAEUDE = 1, 2, 17, 4, 9
KOPF_FORMAT = "<IIIiIiIIIII"
EINHEIT_FORMAT = "<ii12h"
GEBAEUDE_FORMAT = "<i6h"
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
)
GEBAEUDE_FELDER = ("nr", "typ", "besitzer", "x", "y", "leben", "_frei")


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


def entpacken(puffer):
    """Bytes im Aufbau 3 -> Weltbild (vorrat: {spieler: {ware: menge}} fuer Spieler 1-8)."""
    kopf = struct.unpack_from(KOPF_FORMAT, puffer, 0)
    kennung, aufbau, _folge, tick, epoche, ich, ne, ng, geplant, ausgehoben, kern = kopf
    if kennung != KENNUNG or aufbau != AUFBAU:
        raise FalscherAufbau(f"Kennung {kennung:#x} / Aufbau {aufbau}, erwartet {KENNUNG:#x} / {AUFBAU}")
    einheiten = {}
    for i in range(min(ne, MAX_EINHEITEN)):
        werte = struct.unpack_from(EINHEIT_FORMAT, puffer, KOPF + i * EINHEIT)
        e = dict(zip(EINHEIT_FELDER, werte, strict=True))
        einheiten[e["nr"]] = e
    start = KOPF + MAX_EINHEITEN * EINHEIT
    gebaeude = {}
    for i in range(min(ng, MAX_GEBAEUDE)):
        werte = struct.unpack_from(GEBAEUDE_FORMAT, puffer, start + i * GEBAEUDE)
        g = dict(zip(GEBAEUDE_FELDER, werte, strict=True))
        g.pop("_frei")
        gebaeude[g["nr"]] = g
    vorrat = {}
    for sp in range(1, SPIELER):
        werte = struct.unpack_from(f"<{WAREN}i", puffer, VORRAT_START + sp * WAREN * 4)
        vorrat[sp] = {name: werte[w] for w, name in WARE_NAMEN.items()}
    return Weltbild(tick, epoche, ich, kern, geplant, ausgehoben, einheiten, gebaeude, vorrat)


class Leitung:
    """Leser fuer den gemeinsamen Speicher eines laufenden Spiels (Spielordner der Instanz)."""

    def __init__(self, spiel_ordner):
        pfad = os.path.join(spiel_ordner, "ucp", "villagestudio", "kern_leitung.txt")
        with open(pfad, encoding="utf-8") as f:
            name, groesse = f.read().split()[:2]
        if int(groesse) != GROESSE:
            raise FalscherAufbau(f"Groesse {groesse}, erwartet {GROESSE}")
        self.name = name
        self.speicher = mmap.mmap(-1, GROESSE, tagname=name, access=mmap.ACCESS_WRITE)

    def folge(self):
        return struct.unpack_from("<I", self.speicher, 8)[0]

    def lesen(self, versuche=50):
        """Ein vollstaendiges Weltbild oder None, wenn der Kern in allen Versuchen gerade schrieb."""
        for _ in range(versuche):
            vorher = self.folge()
            if vorher & 1:
                continue
            kopie = self.speicher[:]
            if self.folge() == vorher:
                return entpacken(kopie)
        return None

    def auftrag(self, art, nr, a=0, b=0):
        """Legt einen Auftrag in den Ring (Art UEBERNEHMEN/FREIGEBEN/LAUF/ANGRIFF_*); gibt seine Ring-Nummer zurueck.
        Ein Schreiber je Spiel: nur ein Python-Prozess darf Auftraege legen."""
        schreib = struct.unpack_from("<I", self.speicher, RING_START)[0]
        lese = struct.unpack_from("<I", self.speicher, RING_START + 4)[0]
        if (schreib - lese) % 2**32 >= RING_N:
            raise RuntimeError("Auftragsring voll - der Kern arbeitet nicht (Spiel angehalten?)")
        o = RING_START + RING_KOPF + (schreib % RING_N) * RING_EINTRAG
        struct.pack_into("<iiiii", self.speicher, o, art, nr, a, b, OFFEN)
        struct.pack_into("<I", self.speicher, RING_START, (schreib + 1) % 2**32)
        return schreib

    def ergebnis(self, nummer):
        """Ergebnis eines Auftrags oder None, solange der Kern ihn noch nicht abgearbeitet hat."""
        lese = struct.unpack_from("<I", self.speicher, RING_START + 4)[0]
        if (lese - nummer) % 2**32 == 0 or (lese - nummer) % 2**32 > RING_N:
            return None
        o = RING_START + RING_KOPF + (nummer % RING_N) * RING_EINTRAG
        return struct.unpack_from("<i", self.speicher, o + 16)[0]
