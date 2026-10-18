# -*- coding: utf-8 -*-
"""Feldzug der Streitkolbenkaempfer (Daniel 18.10.2026: "maximal 20 Assassinen ... den Rest komplett in Wirtschaft und
Waffenproduktion ... 30 Streitkolben pro Nomade (Ueberlebende zaehlen auch) ... gestackt ... eins nach dem anderen ...
alle Einheiten sollten irgendwas Begruendetes machen, nicht nur sinnvoll rumstehen").

Ablauf je Runde (schritt):
  ZIEL     der naechste lebende feindliche Lord (Schach-Abstand zu unserem Bergfried); bleibt, bis er tot ist.
  SAMMELN  alle Streitkolben an einen Sammelpunkt auf der Linie Bergfried -> Ziel-Lord, so weit vorn wie moeglich, aber
           mehr als SICHER Felder von jedem feindlichen Fernkaempfer und Gebaeude (dort schiesst niemand). Wer dort steht und
           einen Feind in VERTEIDIGEN Feldern sieht, greift ihn an (statt zu stehen). Neu befohlen wird nur, wer nicht dort
           ist und nicht dorthin laeuft.
  ANGRIFF  sobald N am Sammelpunkt stehen (Ueberlebende zaehlen) und der Lord Schaden nimmt (ab LORD_SCHUTZ_BIS):
           19.10. (1018y, Daniel: "die Streitkolben lassen sich unnoetig von den Fernkaempfern ablenken und werden die
           ganze Zeit erschossen, weil sie nicht einfach auf den Lord gehen; von der Seite angreifen macht keinen Sinn -
           obenrum haetten die Bogenschuetzen sie erst am Ende erkannt"): als Haufen per LAUF-Befehl (laeuft an Feinden
           vorbei, klettert auf den Bergfried) ueber Wegpunkte des Weges mit dem geringsten Beschuss (wegplaner, wie bei
           den Assassinen); erst wer ANGRIFF_NAH am Lord steht, bekommt den Angriffsbefehl auf ihn.
           Ist der Lord tot: naechstes Ziel, die Ueberlebenden sammeln neu, aufgefuellt wird auf N.
Anwerben/Kaufen macht erstes_spiel.ruestung_kaufen (Ziel N lebende Streitkolben, nur Gold ueber der Ruecklage).
"""

STREITKOLBEN = 26
LORD = 55
FERN = {22, 23, 70, 72, 74, 76}
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Feldzug:
    N = 30                    # je Nomade (Daniel)
    SICHER = 50               # Felder Abstand des Sammelpunkts zu feindlichen Fernkaempfern (Reichweite 44 + Rand)
    GEB_ABSTAND = 30          # ... und zu feindlichen Gebaeuden (Tuerme, Mauern mit Schuetzen)
    AM_PUNKT = 10             # so nah am Sammelpunkt gilt als "da"
    VERTEIDIGEN = 18          # Feind so nah am Sammelpunkt -> angreifen
    WIEDERHOLEN = 5           # Runden zwischen zwei Angriffsbefehlen
    ANGRIFF_NAH = 4           # so nah am Lord: Angriffsbefehl statt Laufbefehl
    WEGPUNKT_NAH = 4          # so nah am Wegpunkt (Mitte des Haufens): naechster Wegpunkt

    def __init__(self, sp, heim, lord_schutz_bis=0, n=None):
        self.sp, self.heim, self.schutz_bis = sp, tuple(heim), lord_schutz_bis
        if n:
            self.N = n
        self.ziel = None            # Nr des Ziel-Lords
        self.phase = "sammeln"
        self.punkt = None
        self.runde = 0
        self.letzter_befehl = -99
        self.tote_lords = []
        self.verteidigt = {}
        self.wegplaner = None       # (L, G, start, ziel) -> [Wegpunkte, letzter = ziel]; setzt erstes_spiel
        self.weg, self.weg_i, self.weg_ziel = [], 0, None

    def _lords(self, L):
        return {n: e for n, e in L.items() if e["typ"] == LORD and e["besitzer"] not in (0, self.sp) and e["leben"] > 0}

    def _sammelpunkt(self, L, G, lord):
        """Auf der Linie Heim -> Lord von vorn nach hinten der erste Punkt, der SICHER Felder von jedem feindlichen
        Fernkaempfer und GEB_ABSTAND von jedem feindlichen Gebaeude entfernt ist."""
        fern = [(e["x"], e["y"]) for e in L.values() if e["besitzer"] not in (0, self.sp) and e["typ"] in FERN]
        geb = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] not in (0, self.sp)]
        h, z = self.heim, (lord["x"], lord["y"])
        d = max(1, schach(h, z))
        for k in range(d, -1, -2):
            q = (h[0] + (z[0] - h[0]) * k // d, h[1] + (z[1] - h[1]) * k // d)
            if all(schach(q, f) > self.SICHER for f in fern) and all(schach(q, b) > self.GEB_ABSTAND for b in geb):
                return q
        return h

    def schritt(self, st, L, G, befehl):
        """Gibt die Meldungen der Runde. befehl(dict, warte, bis=...) schickt einen Modulbefehl."""
        self.runde += 1
        aus = []
        t = st.get("t", 0)
        lords = self._lords(L)
        kolben = sorted(n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == STREITKOLBEN)
        if self.ziel is not None and self.ziel not in lords:
            self.tote_lords.append((self.ziel, t))
            aus.append("FELDZUG: Lord %d tot bei Tick %d - %d Streitkolben ueberlebten, naechstes Ziel" % (self.ziel, t, len(kolben)))
            self.ziel, self.phase, self.punkt = None, "sammeln", None
        if not lords:
            return aus
        if self.ziel is None:
            self.ziel = min(lords, key=lambda n: (schach(self.heim, (lords[n]["x"], lords[n]["y"])), n))
            self.phase = "sammeln"
            aus.append("FELDZUG: Ziel Lord %d (Spieler %d) bei (%d, %d), %d Felder vom Bergfried" % (
                self.ziel, lords[self.ziel]["besitzer"], lords[self.ziel]["x"], lords[self.ziel]["y"],
                schach(self.heim, (lords[self.ziel]["x"], lords[self.ziel]["y"]))))
        lord = lords[self.ziel]
        lp = (lord["x"], lord["y"])
        if not kolben:
            return aus
        if self.phase == "sammeln":
            if self.punkt is None or self.runde % 20 == 0:
                neu = self._sammelpunkt(L, G, lord)
                if neu != self.punkt:
                    self.punkt = neu
                    aus.append("FELDZUG: Sammelpunkt %s (%d Felder vor dem Lord %d)" % (neu, schach(neu, lp), self.ziel))
            p = self.punkt
            da = [n for n in kolben if schach((L[n]["x"], L[n]["y"]), p) <= self.AM_PUNKT]
            # Verteidigen statt stehen: feindliche Einheit nahe am Sammelpunkt -> die, die da sind, greifen sie an
            feind = min(((schach(p, (e["x"], e["y"])), n) for n, e in L.items()
                         if e["besitzer"] not in (0, self.sp) and e["typ"] in TRUPPE and schach(p, (e["x"], e["y"])) <= self.VERTEIDIGEN),
                        default=None)
            if feind and da:
                if self.verteidigt.get(feind[1], -99) < self.runde - self.WIEDERHOLEN:
                    befehl({"angriff": {"einheiten": da, "ziel": feind[1]}}, 1.0, bis="ANGRIFF")
                    self.verteidigt[feind[1]] = self.runde
                    aus.append("FELDZUG: %d Streitkolben greifen Einheit %d (Typ %d) %d Felder vor dem Sammelpunkt an" % (
                        len(da), feind[1], L[feind[1]]["typ"], feind[0]))
            hin = [n for n in kolben if n not in da and schach((L[n]["laufx"], L[n]["laufy"]), p) > 3]
            if hin:
                befehl({"angriff": {"einheiten": hin, "lauf": [p[0], p[1]]}}, 1.0, bis="ANGRIFF")
            if self.runde % 10 == 0:
                aus.append("FELDZUG sammeln: %d von %d am Sammelpunkt %s, %d Streitkolben leben, Lord %d Leben %d%s" % (
                    len(da), self.N, p, len(kolben), self.ziel, lord["leben"],
                    "" if t >= self.schutz_bis else " (Lord-Schutz bis Tick %d)" % self.schutz_bis))
            if len(da) >= self.N and t >= self.schutz_bis:
                self.phase = "angriff"
                self.letzter_befehl = -99
                self.weg, self.weg_i, self.weg_ziel = [], 0, None
                aus.append("FELDZUG ANGRIFF: %d Streitkolben gemeinsam auf Lord %d (Leben %d) bei Tick %d" % (
                    len(kolben), self.ziel, lord["leben"], t))
        if self.phase == "angriff":
            orte = sorted((L[n]["x"], L[n]["y"]) for n in kolben)
            mitte = (sorted(o[0] for o in orte)[len(orte) // 2], sorted(o[1] for o in orte)[len(orte) // 2])
            # Weg neu, wenn keiner da ist oder der Lord sich weit von seinem Ende entfernt hat
            if not self.weg or self.weg_ziel is None or schach(self.weg_ziel, lp) > 5:
                wp = list(self.wegplaner(L, G, mitte, lp)) if self.wegplaner else [lp]
                if not wp or tuple(wp[-1]) != tuple(lp):
                    wp.append(lp)
                self.weg, self.weg_i, self.weg_ziel = [tuple(p) for p in wp], 0, lp
                aus.append("FELDZUG Weg zum Lord %d: %d Wegpunkte %s" % (self.ziel, len(self.weg), self.weg[:6]))
            while self.weg_i < len(self.weg) - 1 and schach(mitte, self.weg[self.weg_i]) <= self.WEGPUNKT_NAH:
                self.weg_i += 1
            p = self.weg[self.weg_i] if self.weg_i < len(self.weg) - 1 else lp
            am_lord = [n for n in kolben if schach((L[n]["x"], L[n]["y"]), lp) <= self.ANGRIFF_NAH]
            if am_lord and self.runde - self.letzter_befehl >= self.WIEDERHOLEN:
                befehl({"angriff": {"einheiten": am_lord, "ziel": self.ziel}}, 1.0, bis="ANGRIFF")
                self.letzter_befehl = self.runde
            unterwegs = [n for n in kolben if n not in am_lord and schach((L[n]["laufx"], L[n]["laufy"]), p) > 2]
            if unterwegs:
                befehl({"angriff": {"einheiten": unterwegs, "lauf": [p[0], p[1]]}}, 1.0, bis="ANGRIFF")
            if self.runde % 5 == 0:
                abst = sorted(schach(o, lp) for o in orte)
                aus.append("FELDZUG Stand Tick %d: %d Streitkolben, Abstand zum Lord naechster %d / Mitte %d, Wegpunkt %d/%d, "
                           "am Lord %d, Lord %d Leben %d" % (t, len(kolben), abst[0], abst[len(abst) // 2], self.weg_i + 1,
                                                            len(self.weg), len(am_lord), self.ziel, lord["leben"]))
        return aus

    def einheiten(self, L):
        """19.10.: die Streitkolben des Feldzugs - der Waechter laesst sie in Ruhe (1018y: sein "Stapeln" holte sie heim)."""
        return {n for n, e in L.items() if e["besitzer"] == self.sp and e["typ"] == STREITKOLBEN}
