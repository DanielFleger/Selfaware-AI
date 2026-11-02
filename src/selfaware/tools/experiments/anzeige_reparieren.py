# -*- coding: utf-8 -*-
"""B-144: Repariert den Anzeigefehler in einem Spielstand. Daniel 02.11.2026: "es soll aus egal welchem Winkel normal aussehen".

Gebaeude, die per Befehl mit einem anderen Bildwert als 15 gebaut wurden, sehen nur in der Standardansicht richtig aus
(game/ucp/drehwert.py). Das Werkzeug laedt den Stand, setzt den Wert bei den betroffenen Gebaeuden auf 15, dreht die Karte einmal
im Kreis, weil das Spiel erst dabei neu zeichnet, speichert unter neuem Namen, laedt das Ergebnis und prueft es.
Der alte Stand bleibt unveraendert liegen. Jede Drehung laesst auch im angehaltenen Spiel einen Takt laufen (gemessen).
Ausgenommen: Werkstaetten rechnen ihren Wert selbst aus (Update...Workshop, alle 256 Takte), Tore und Zugbruecke haben eigene Regeln.

Aufruf: SHC_INSTANZ=2 python -m selfaware.tools.experiments.anzeige_reparieren "<Stand>" ["<neuer Name>"]
Instanz 5 lehnt das Werkzeug ab. Die Sperre der Instanz muss man vorher selbst holen.
"""
import collections
import os
import struct
import sys
import time

from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

GEBAEUDE, SCHRITT = 0xF98520, 0x32C
ZUSTAND, TYP, BESITZER, BILDWERT = 0xE4, 0xE6, 0xEA, 0x116
ANZAHL = 2000
DREHUNG, TICK, PAUSE = 0x01FE7AA4, 0x0117CADC, 0x01FEA054
NORMAL = 15
WERKSTAETTEN = {12, 13, 14, 15, 16, 17, 18}
TORE = {45, 46, 47, 49}


def gebaeude_lesen(roh):
    """Alle belegten Eintraege aus dem Speicherabzug der Gebaeudetabelle."""
    aus = []
    for i in range(1, len(roh) // SCHRITT):
        b = i * SCHRITT
        z, t, s, v = (struct.unpack_from("<h", roh, b + o)[0] for o in (ZUSTAND, TYP, BESITZER, BILDWERT))
        if z:
            aus.append({"nr": i, "typ": t, "sp": s, "v": v})
    return aus


def falsche(liste):
    return [e for e in liste if e["v"] != NORMAL and e["typ"] not in WERKSTAETTEN | TORE]


def neues_wort(alt):
    """Der Wert belegt 2 Bytes, poke schreibt 4: Das Nachbarfeld im oberen Teil bleibt, wie es ist."""
    neu = (alt & 0xFFFF0000) | NORMAL
    return neu - 2 ** 32 if neu >= 2 ** 31 else neu


def adresse(nr):
    return GEBAEUDE + nr * SCHRITT + BILDWERT


class Spiel:
    def __init__(self, instanz, befehl):
        self.q = ProzessQuelle(pid_der_instanz(instanz))
        self.befehl = befehl

    def wert(self, adr):
        return struct.unpack("<i", self.q.lies(adr, 4))[0]

    def gebaeude(self):
        return gebaeude_lesen(self.q.lies(GEBAEUDE, SCHRITT * ANZAHL))

    def berichtigen(self):
        if self.wert(PAUSE) != 1:
            raise RuntimeError("Das Spiel laeuft. Berichtigt wird nur im angehaltenen Spiel")
        betroffen = falsche(self.gebaeude())
        for e in betroffen:
            alt = struct.unpack("<I", self.q.lies(adresse(e["nr"]), 4))[0]
            self.befehl({"poke": adresse(e["nr"]), "wert": neues_wort(alt)}, 0.05)
        time.sleep(0.5)
        rest = falsche(self.gebaeude())
        if rest:
            raise RuntimeError(f"Noch falsch: {rest[:5]}")
        return betroffen

    def im_kreis_drehen(self, je_drehung=None):
        start = self.wert(DREHUNG)
        for _ in range(4):
            a = self.wert(DREHUNG)
            if je_drehung:
                je_drehung(a)
            self.befehl({"drehen": "links"}, 0.3)
            soll, ende = (a + 2) % 8, time.time() + 15  # Schutz gegen Haengen, keine Spielzeit
            while self.wert(DREHUNG) != soll and time.time() < ende:
                time.sleep(0.05)
            if self.wert(DREHUNG) != soll:
                raise RuntimeError(f"Drehung kam nicht an: {self.wert(DREHUNG)} statt {soll}")
            time.sleep(0.5)
        if self.wert(DREHUNG) != start:
            raise RuntimeError("Nicht zurueck bei der Startdrehung")


def main():
    from selfaware.game.ucp import laden, speichern

    stand = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else f"{stand} repariert"
    if name == stand:
        raise SystemExit("Der neue Name muss anders sein: Der alte Stand bleibt liegen")
    spiel = Spiel(int(os.environ["SHC_INSTANZ"]), laden.befehl)
    print("Geladen bei Takt", laden.lade_stand(stand, mit_bild=False))
    betroffen = spiel.berichtigen()
    print("Berichtigt:", len(betroffen), "Gebaeude, Arten", sorted({e["typ"] for e in betroffen}))
    spiel.im_kreis_drehen()
    speichern.speichere(name)
    laden.befehl({"pause": True}, 0.3)
    print("Neu geladen bei Takt", laden.lade_stand(name, mit_bild=False))
    liste = spiel.gebaeude()
    if falsche(liste):
        raise SystemExit(f"NICHT GESCHAFFT: nach dem Laden noch falsch: {falsche(liste)[:5]}")
    print("GESCHAFFT:", name, "je Wert", collections.Counter(e["v"] for e in liste).most_common())


if __name__ == "__main__":
    main()
