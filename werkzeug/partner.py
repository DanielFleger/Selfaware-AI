# -*- coding: utf-8 -*-
"""18.10. (1v1 1018b/c/d, Daniel 22:22 "bitte fixe diese und alle moeglichen auftretenden Fehlermeldungen"): zwei Lenker
teilen sich EIN Spiel. Bisher hielt jeder Abbruch eines Lenkers das Spiel an (Regel 50, Absturz, Ende Phase 2) - der andere
sah die Spielzeit stehen und brach nach 30 s ebenfalls ab. 1018b und 1018d endeten so nach einem Regelbruch, 1018c nach einem
Kanalfehler (IndexError) beim Partner.

Drei Bausteine, ohne Spiel pruefbar (partner_pruefen.py):
  Ende      jeder Lenker hinterlegt beim Aufhoeren eine Ende-Meldung (Art, Grund, Tick); der andere liest sie je Runde.
            Art "regelbruch"/"niederlage" = der andere hat gewonnen und hoert ebenfalls auf; "absturz"/"ende" = er spielt
            weiter. Angehalten wird das Spiel erst, wenn beide aufgehoert haben oder die Partie vorbei ist.
  Serie     ein Fehler in einer Runde wird gemeldet und die naechste Runde beginnt; aufgegeben wird erst, wenn GRENZE_S
            Sekunden lang keine Runde mehr vollstaendig durchlief (dann steuert der Lenker ohnehin nichts mehr).
  Stillstand  steht die Spielzeit, obwohl kein Lenker aufgehoert hat, setzt der Lenker das Spiel fort (hoechstens
            FORTSETZEN_MAX Mal hintereinander) statt abzubrechen.
"""
import glob
import json
import os
import time
import traceback

# so lange ohne eine vollstaendige Runde -> aufgeben. Wie die 30 s des Stillstand-Abbruchs; gemessen 1018d (Logzeilen
# "ZEITEN nach 100/200/300/400 Runden" 22:22:56-22:23:58): eine Runde 0,15-0,27 s - 30 s sind weit ueber 100 Runden in Folge
GRENZE_S = 30.0
FORTSETZEN_MAX = 3       # so oft hintereinander fortsetzen, wenn die Spielzeit 30 s steht
SIEG_DURCH = ("regelbruch", "niederlage")     # Ende-Arten des Partners, die die Partie fuer uns entscheiden


def ende_datei(hier, instanz, sp):
    return os.path.join(hier, ".eins_gegen_eins_ende%s_sp%d.json" % ("" if instanz == 1 else instanz, sp))


class Ende:
    """Ende-Meldungen beider Lenker einer Instanz. start: Prozessstart - aeltere Meldungen gehoeren zu einem frueheren Lauf."""

    def __init__(self, hier, instanz, sp, start):
        self.hier, self.instanz, self.sp, self.start = hier, instanz, sp, start
        self.eigene = None
        self.gesehen = None

    def melde(self, art, grund, tick=None):
        """Erste Meldung gilt - ein spaeterer Folgefehler ueberschreibt den eigentlichen Grund nicht."""
        if self.eigene is not None:
            return self.eigene
        self.eigene = {"sp": self.sp, "art": art, "grund": grund, "tick": tick, "pid": os.getpid(), "zeit": time.time()}
        ziel = ende_datei(self.hier, self.instanz, self.sp)
        with open(ziel + ".neu", "w", encoding="utf-8") as f:
            json.dump(self.eigene, f, ensure_ascii=False)
        os.replace(ziel + ".neu", ziel)        # ganz oder gar nicht - der Partner liest nie eine halbe Datei
        return self.eigene

    def partner(self):
        """Ende-Meldung eines anderen Lenkers dieses Laufs oder None."""
        muster = ende_datei(self.hier, self.instanz, 0).replace("_sp0.json", "_sp*.json")
        for pfad in sorted(glob.glob(muster)):
            if pfad == ende_datei(self.hier, self.instanz, self.sp):
                continue
            try:
                if os.path.getmtime(pfad) < self.start - 1:
                    continue
                with open(pfad, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError):
                continue                       # gerade im Austausch - naechste Runde
        return None

    def neu_vom_partner(self):
        """Die Partner-Meldung genau einmal (beim ersten Sehen), sonst None."""
        m = self.partner()
        if m is None or self.gesehen is not None:
            return None
        self.gesehen = m
        return m

    def anhalten_erlaubt(self, vorbei=False):
        """Das Spiel anhalten darf nur, wer als Letzter aufhoert - oder wenn die Partie ohnehin vorbei ist."""
        return vorbei or self.partner() is not None


class Serie:
    """Fehler je Runde: melden, weitermachen; aufgeben erst nach GRENZE_S ohne vollstaendige Runde."""

    def __init__(self, grenze_s=GRENZE_S, uhr=time.time):
        self.grenze_s, self.uhr = grenze_s, uhr
        self.letzte_gute = uhr()
        self.gesamt = 0
        self.arten = {}

    def gut(self):
        self.letzte_gute = self.uhr()

    def fehler(self, ex, runde=None, tick=None):
        """-> (Meldezeile, aufgeben, erstes Auftreten dieser Art)"""
        self.gesamt += 1
        tb = traceback.extract_tb(ex.__traceback__) if ex.__traceback__ is not None else []
        ort = "%s:%d" % (os.path.basename(tb[-1].filename), tb[-1].lineno) if tb else "?"
        art = "%s @ %s" % (type(ex).__name__, ort)
        erstes = art not in self.arten
        self.arten[art] = self.arten.get(art, 0) + 1
        ohne = self.uhr() - self.letzte_gute
        aufgeben = ohne >= self.grenze_s
        zeile = "FEHLER Runde %s Tick %s: %s: %s (%s, %d. Mal; %.0f s ohne vollstaendige Runde%s)" % (
            runde, tick, type(ex).__name__, str(ex)[:200], ort, self.arten[art], ohne,
            " - GEBE AUF" if aufgeben else " - naechste Runde")
        return zeile, aufgeben, erstes

    def bericht(self):
        if not self.gesamt:
            return "FEHLER gesamt: keine"
        return "FEHLER gesamt: %d (%s)" % (self.gesamt, ", ".join(
            "%s %dx" % kv for kv in sorted(self.arten.items(), key=lambda kv: -kv[1])))


def stillstand(sekunden, versuche, partner_modus):
    """Spielzeit steht seit <sekunden>; <versuche> = wie oft schon hintereinander fortgesetzt.
    -> "warten" | "fortsetzen" | "abbruch". Ohne Partner bleibt es beim alten Abbruch nach 30 s."""
    if sekunden < 30:
        return "warten"
    if partner_modus and versuche < FORTSETZEN_MAX:
        return "fortsetzen"
    return "abbruch"
