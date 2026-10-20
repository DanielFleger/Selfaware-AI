# -*- coding: utf-8 -*-
"""Haushalt: Steuer und Rationen so, dass die Beliebtheit NIE unter eine Grenze faellt (Daniel 07.10. 23:34: 25
Streitkolbenkaempfer, "niemals unter 50 Beliebtheit"; Strategie-Rat 23:50 in Plan_Streitkolben.md).

Gemessen (Lauf 69, lage_20261007_015455_i1): die Beliebtheit springt etwa alle 200 Ticks ("Woche") um GENAU die Summe
der Liga-Tabellenwerte in Hundertsteln - Stufe 2 bei normalen Rationen +25 (Tabelle +25), Stufe 11 ohne Rationen -1250
(Tabelle -1000 - 250). Darum rechnet der Regler die naechste Woche voraus, statt zu raten:

    naechste = jetzt + Steuer[Stufe] + Rationen[Stufe] + Vielfalt[Sorten] + Rest

Rest = alles, was die Tabelle hier nicht kennt (Gute Dinge, Bier, Kirche, Fehler im Modell). Er wird bei jedem Schritt
gemessen: Schritt - (Steuer + Rationen + Vielfalt) der Woche davor. Gekappte Schritte (bei 0 oder 100) zaehlen nicht.
Gewaehlt wird die hoechste Stufe, bei der die naechste Woche noch >= Boden ist; reicht nicht einmal Stufe 2, wird
bestochen (Stufe 1/0) - lieber Gold als die Regel brechen.
"""

STEUER_BEL = [225, 125, 25, -25, -75, -125, -200, -275, -375, -500, -750, -1000]   # liga_ai.json taxation/popularity
STEUER_GOLD = [-1.5, -0.5, 0.0, 0.25, 0.5, 0.7, 1.0, 1.3, 1.65, 2.0, 2.75, 4.0]     # Gold je Kopf und Monat (Bestechung negativ)
RATION_BEL = {0: -250, 1: -125, 2: 0, 3: 125, 4: 250}                            # food/ration_bonuses (normal = 0)
VIELFALT_BEL = {0: 0, 1: 0, 2: 25, 3: 75, 4: 125}                                # food/variety_bonuses (2/3/4 Sorten)
SORTEN = ("apfel", "brot", "kaese", "fleisch")


def sorten(st):
    return sum(1 for w in SORTEN if st.get(w, 0) > 0)


def essen(st):
    return sum(st.get(w, 0) for w in SORTEN)


class Haushalt:
    def __init__(self, rand=650, doppelt=True):
        self.rand = rand                 # Abstand ueber der Grenze 50 (Hundertstel): faengt einen Einbruch ab, bevor der Rest neu gemessen ist
        self.doppelt = doppelt           # doppelte Rationen, sobald genug Nahrung da ist
        self.stufe = None                # zuletzt gesetzte Steuerstufe
        self.ration = None               # zuletzt gesetzte Ration
        self.rest = 0                    # gemessener Rest je Woche (Hundertstel); 0, bis ein Schritt ihn zeigt
        self.rest_gemessen = 0
        self.vor = None                  # (Tick, Beliebtheit, Stufe, Ration wirksam, Sorten) der letzten Runde
        self.schritte = []               # (Tick, Schritt, erwartet, Rest, Stufe, Ration, Sorten)
        self.min_bel = None
        self.entschieden = -10 ** 6      # Tick der letzten Entscheidung
        self.schritt_jetzt = False

    def ration_wirksam(self, st):
        return 0 if essen(st) == 0 else (self.ration if self.ration is not None else 2)

    def beobachte(self, st):
        """Jede Runde. Erkennt den Wochenschritt und misst den Rest. Gibt Text oder None.
        Lauf s25/1 (07.10. 23:55): die Stufe der vergangenen Runde ist self.stufe (zu Beginn der Runde, vor der neuen
        Entscheidung) - vorher stand hier die Stufe von VOR der letzten Entscheidung, eine Runde zu spaet."""
        t, bel = st.get("t", 0), st.get("beliebt", 0)
        self.min_bel = bel if self.min_bel is None else min(self.min_bel, bel)
        text, self.schritt_jetzt = None, False
        if self.vor is not None and bel != self.vor[1] and self.stufe is not None:
            schritt = bel - self.vor[1]
            r_eff = 0 if self.vor[2] == 0 else (self.ration if self.ration is not None else 2)
            erwartet = STEUER_BEL[self.stufe] + RATION_BEL[r_eff] + VIELFALT_BEL[self.vor[3]]
            gekappt = bel >= 10000 or bel <= 0
            if not gekappt:
                self.rest = schritt - erwartet
                self.rest_gemessen += 1
            self.schritt_jetzt = True
            self.schritte.append((t, schritt, erwartet, None if gekappt else self.rest, self.stufe, r_eff, self.vor[3]))
            text = "HAUSHALT Woche: Beliebtheit %.2f -> %.2f (Schritt %+d, Tabelle %+d, Rest %s; Stufe %d, Ration %d, Sorten %d, Nahrung %d)" % (
                self.vor[1] / 100.0, bel / 100.0, schritt, erwartet, "gekappt" if gekappt else "%+d" % self.rest,
                self.stufe, r_eff, self.vor[3], self.vor[2])
        self.vor = (t, bel, essen(st), sorten(st))
        return text

    def vorhersage(self, st, stufe, ration):
        """Beliebtheit nach dem naechsten Wochenschritt bei dieser Stufe und Ration (Nahrung von jetzt)."""
        r_eff = 0 if essen(st) == 0 else ration
        return st.get("beliebt", 0) + STEUER_BEL[stufe] + RATION_BEL[r_eff] + VIELFALT_BEL[sorten(st)] + self.rest

    def jetzt_entscheiden(self, st, regel_boden):
        """Einmal je Woche (gleich nach dem Schritt oder 200 Ticks nach der letzten Entscheidung) - Lauf s25/1 wechselte
        Rationen und Stufe fast jede Runde, weil die Nahrung um die Schwelle pendelte. Ausser der Reihe nur bei Gefahr:
        die laufende Einstellung braechte die naechste Woche unter die Regelgrenze."""
        t = st.get("t", 0)
        if self.stufe is None or self.ration is None or self.schritt_jetzt or t - self.entschieden >= 200:
            return True
        return self.vorhersage(st, self.stufe, self.ration) < regel_boden

    def waehle_ration(self, st, puffer):
        """Doppelt, solange die Nahrung ueber dem Puffer liegt (gemessen 05.10.: 10 Leute essen bei normalen Rationen 1
        Stueck je 1.000 Ticks); sonst normal."""
        return 4 if self.doppelt and essen(st) >= puffer else 2

    def waehle_stufe(self, st, boden, ration, not_boden=5100):
        """Hoechste Steuerstufe (2..11), bei der die naechste Woche >= boden bleibt (Kasse: 50 + Rand, Wachstum: 95).
        Haelt keine Stufe den Boden, bleibt es bei Stufe 2 (keine Steuer), solange die Vorhersage ueber not_boden liegt.
        Bestochen (Stufe 1/0, kostet bis 1,50 Gold je Kopf und Monat) wird nur, wenn sonst die Regelgrenze 50 droht - der
        Rand ist fuer Unvorhergesehenes da, nicht fuer Bekanntes (Lauf s25/1 bestach, um 95 zu halten)."""
        for s in range(11, 1, -1):
            if self.vorhersage(st, s, ration) >= boden:
                return s
        for s in (2, 1, 0):
            if self.vorhersage(st, s, ration) >= not_boden:
                return s
        return 0

    def bericht(self):
        gem = [s for s in self.schritte if s[3] is not None]
        return "Haushalt: %d Wochenschritte, %d mit gemessenem Rest (letzter %+d), tiefste Beliebtheit %.2f" % (
            len(self.schritte), len(gem), self.rest, (self.min_bel or 0) / 100.0)
