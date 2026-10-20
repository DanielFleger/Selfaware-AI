"""B-145 S4a: Weltbild des SamurAI-Kerns aus dem gemeinsamen Speicher lesen - jeden Takt, ohne Dateikanal.

Der Kern (crates/samurai-kern/src/leitung.rs) schreibt in jedem neuen Spieltakt Kopf, Einheiten und Gebaeude in eine
benannte Speicherabbildung und legt ihren Namen in ucp/villagestudio/kern_leitung.txt ab. Ein Folgezaehler (ungerade =
wird gerade geschrieben) sorgt dafuer, dass nur ein vollstaendiges Bild genommen wird.
"""

import mmap
import os
import struct
from dataclasses import dataclass

KENNUNG = int.from_bytes(b"SAMK", "little")
AUFBAU = 1
KOPF, EINHEIT, GEBAEUDE = 64, 32, 16
MAX_EINHEITEN, MAX_GEBAEUDE = 2500, 2000
GROESSE = KOPF + MAX_EINHEITEN * EINHEIT + MAX_GEBAEUDE * GEBAEUDE
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


def entpacken(puffer):
    """Bytes im Aufbau 1 -> Weltbild."""
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
    return Weltbild(tick, epoche, ich, kern, geplant, ausgehoben, einheiten, gebaeude)


class Leitung:
    """Leser fuer den gemeinsamen Speicher eines laufenden Spiels (Spielordner der Instanz)."""

    def __init__(self, spiel_ordner):
        pfad = os.path.join(spiel_ordner, "ucp", "villagestudio", "kern_leitung.txt")
        with open(pfad, encoding="utf-8") as f:
            name, groesse = f.read().split()[:2]
        if int(groesse) != GROESSE:
            raise FalscherAufbau(f"Groesse {groesse}, erwartet {GROESSE}")
        self.name = name
        self.speicher = mmap.mmap(-1, GROESSE, tagname=name, access=mmap.ACCESS_READ)

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
