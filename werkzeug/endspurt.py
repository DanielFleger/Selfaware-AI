# -*- coding: utf-8 -*-
"""Endspurt (Daniel 19.10. 16:49: "richtig nice, wenn eine KI merkt, ah ich bin down, ich investiere all mein Gold in
Schwertkaempfer und versuche den Gegner zu rushen"; 16:51 zu 1018k: "die Wirtschaft von Orange ist am Arsch, aber er hat so
20 arabische Schwertkaempfer mit Bogenschuetzen - er koennte jetzt einsehen, ok ich bin schon verloren, lass versuchen den
Gegner zu rushen"; 16:57 "ja bau in der Reihenfolge").

Erkennen: der Partievergleich (partie_vergleich.py) laeuft waehrend der Partie mit - jede Runde bekommt er dieselben
Gebaeude- und Einheitentabellen wie das Lageprotokoll. Alle PRUEF_TICKS fragt er: hat sich bei liefernden Betrieben oder
Gebaeuden ein EINBRUCH gegen einen Gegner ereignet (Staerke mindestens SCHWELLE) und liegen wir dort jetzt noch hinten?
Dann ist die Wirtschaft verloren - ab da Endspurt, ohne Rueckweg (wer ihn nicht will: Schalter endspurt=nein).

SCHWELLE gemessen 19.10. 17:10 (Nachspiel Runde fuer Runde mit nur dem eigenen Lageprotokoll, wie im Spiel - der Gegner
liefert keine Statuszeile): beim SIEGER erreichte der Ausloeser in 1018i/j/k hoechstens 0,01 / 0,15 / 0,30, beim VERLIERER
zuendet 1,0 bei Tick 21.024 (1018i, Niederlage ~39.880), 19.001 (1018j, 73.239) und 33.047 (1018k, 48.984); liefernde
Betriebe dort 7,7 zu 18,7 / 2,3 zu 14,0 / 14,2 zu 23,3.

Was der Lenker im Endspurt tut (erstes_spiel.py): alle Waren ausser Nahrung verkaufen (5 Holz bleiben fuer einen
Kornspeicher-Nachbau), alles Gold in arab. Schwertkaempfer (Typ 75, 100 Gold, L63) - so viele, wie Bauern am Feuer stehen,
die Heimwache zieht mit, der Feldzug greift an, sobald die Haelfte des Heeres (mindestens Feldzug.MIN_ANGRIFF) am
Sammelpunkt steht, ohne auf die Gefechtsrechnung zu warten, die Assassinen gehen auf den Lord; keine neuen Betriebe, keine
Waffenproduktion.
Pruefung ohne Spiel: werkzeug/endspurt_pruefen.py."""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import partie_vergleich as PV
from lageprotokoll import _tabelle

SCHWELLE = 1.0
KENNZAHLEN = ("liefernd", "gebaeude")     # die der Lenker auch beim Gegner sieht (Gebaeudetabelle)
PRUEF_TICKS = 1000
SCHWERT = 75
SCHWERT_GOLD = 100                        # L63, gemessen 12.10. (erstes_spiel.SOELDNER_GOLD)
HOLZ_BLEIBT = 5                           # ein Kornspeicher-Nachbau (kosten(19) = 5 Holz)


class Endspurt:
    def __init__(self, sp, ertrag_pfad=None):
        self.sp = sp
        self.ertrag_pfad = ertrag_pfad
        self.lauf = PV.Lauf()
        self.naechst = PRUEF_TICKS
        self.aktiv_seit = None
        self.grund = ""

    @property
    def aktiv(self):
        return self.aktiv_seit is not None

    def runde(self, t, st, roh_einheiten, roh_gebaeude):
        """Je Runde mit den Rohtexten, die auch ins Lageprotokoll gehen (Lageprotokoll.schreibe gibt sie zurueck)."""
        self.runde_tabellen(t, st, _tabelle(roh_einheiten, 1), _tabelle(roh_gebaeude, 0))

    def runde_tabellen(self, t, st, E, G):
        self.lauf.runde(t, st, E, G, sp_st=self.sp)

    def pruefen(self, t):
        """Alle PRUEF_TICKS: Einbruch der Wirtschaft? Gibt Ereignistexte (einmal beim Zuenden)."""
        if self.aktiv or t is None or t < self.naechst or self.lauf.erste_t is None:
            return []
        self.naechst = t + PRUEF_TICKS
        lauf = self.lauf
        if self.ertrag_pfad and os.path.exists(self.ertrag_pfad):
            lauf.summen.clear()
            lauf.mit_ertrag.clear()
            lauf.ertrag(PV.lies_ertrag(self.ertrag_pfad), self.sp)
        befund = []
        for q in sorted(lauf.spieler - {self.sp}):
            for g in KENNZAHLEN:
                rp, rq = PV.reihe(lauf, self.sp, g), PV.reihe(lauf, q, g)
                if not rp or not rq:
                    continue
                a, b = PV.glatt(rp), PV.glatt(rq)
                e = PV.einbruch(rp, rq)
                if e and e[1] >= SCHWELLE and a[-1][1] < b[-1][1]:
                    befund.append((e[1], q, g, e[0], a[-1][1], b[-1][1]))
        if not befund:
            return []
        s, q, g, w, wir, sie = max(befund)
        self.aktiv_seit = t
        self.grund = "%s gegen Spieler %d: Einbruch ab Tick %d (Staerke %.2f), jetzt %.1f zu %.1f" % (
            PV.NAME[g], q, w * PV.FENSTER, s, wir, sie)
        return ["ENDSPURT ab Tick %d: Wirtschaft verloren - %s. Ab jetzt: Waren ausser Nahrung verkaufen, alles Gold in arab. "
                "Schwertkaempfer, Heimwache zieht mit, Feldzug greift an, sobald die Haelfte am Sammelpunkt steht, Assassinen "
                "auf den Lord, keine neuen Betriebe" % (t, self.grund)]


def schwertkaempfer(gold, feuer):
    """So viele arab. Schwertkaempfer jetzt anwerben: alles Gold, aber nur so viele, wie Bauern am Feuer stehen."""
    return max(0, min(int(gold) // SCHWERT_GOLD, int(feuer)))
