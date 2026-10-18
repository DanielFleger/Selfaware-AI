# -*- coding: utf-8 -*-
"""Bierkette (Daniel 19.10.2026: "Bierbeliebtheit mitnehmen - Hopfen zu Brauerei zu Bier, Schenke ... und das auf jeder Map").

Warum: unsere Beliebtheit liegt meist schon bei 100 - der Haushalt (haushalt.py) stellt die Steuer so hoch, dass die
naechste Woche noch ueber dem Boden (95) liegt, und misst alles, was seine Tabelle nicht kennt, als "Rest". Bier hebt
diesen Rest -> hoehere Steuerstufe -> mehr Gold fuer Wirtschaft und Waffen.

Kartenunabhaengig: jeder Platz kommt vom Spiel selbst (plaetze(typ, kern, r) = Modulbefehl platzkarte, Bauregeln des
Spiels je Feld), nichts ist fuer eine Karte eingetragen. Ablauf je Runde (schritt):
  SOLL     eine Kette (Hopfenfarm + Brauerei + Schenke) je PRO_KETTE Einwohner, hoechstens HOECHSTENS; erst ab PRO_KETTE.
  REIHE    Hopfenfarm zuerst (braucht am laengsten), dann Brauerei, dann Schenke - je Runde hoechstens ein Bau, nur mit
           Holz und Gold ueber der Ruecklage der Wirtschaft (wirt.ruecklage) und einem Arbeiter am Feuer.
  PLAETZE  Hopfen bis 45 Felder um das Lager, Brauerei 20 um das Lager, Schenke 20 um den Kornspeicher (sonst Lager);
           je Art einmal geholt und nach Fehlschlag oder alle 3.000 Ticks neu.
"""
import math

HOPFEN, BRAUEREI, SCHENKE, KORNSPEICHER, LAGER = 31, 18, 22, 19, 10


class Bierkette:
    PRO_KETTE = 30            # Einwohner je Kette (Daniel: "30 Bevoelkerung ... bei einer Schenke")
    HOECHSTENS = 4
    NEU_PLAETZE = 3000        # Ticks, nach denen die Platzliste neu vom Spiel geholt wird
    RADIUS = {HOPFEN: 45, BRAUEREI: 20, SCHENKE: 20}
    RESERVE = 2               # Hopfenplaetze, die gleich beim Start fuer andere Bauten gesperrt werden (fruchtbarer Boden)

    def __init__(self, sp, baue, plaetze, preis):
        """baue(typ, x, y, r) -> Bauergebnis (wahr = gesetzt); plaetze(typ, kern, r) -> [(x, y)] vom Spiel;
        preis(typ, ware) -> Baukosten."""
        self.sp, self.baue, self.plaetze, self.preis = sp, baue, plaetze, preis
        self.merk = {}            # typ -> (Tick, [Plaetze])
        self.verworfen = set()
        self.reserviert = []      # beim Start gesperrte Hopfenplaetze (setzt erstes_spiel) - werden zuerst genommen

    def _kern(self, G, typ):
        eig = [g for g in G.values() if g["besitzer"] == self.sp]
        wahl = [g for g in eig if g["typ"] == (KORNSPEICHER if typ == SCHENKE else LAGER)] or \
               [g for g in eig if g["typ"] == LAGER]
        if not wahl:
            return None
        return (sum(g["x"] for g in wahl) // len(wahl), sum(g["y"] for g in wahl) // len(wahl))

    def _platz(self, typ, G, t):
        if typ == HOPFEN:
            frei = [p for p in self.reserviert if p not in self.verworfen]
            if frei:
                return frei[0]
        kern = self._kern(G, typ)
        if kern is None:
            return None
        m = self.merk.get(typ)
        if m is None or t - m[0] >= self.NEU_PLAETZE or not [p for p in m[1] if p not in self.verworfen]:
            self.merk[typ] = (t, self.plaetze(typ, kern, self.RADIUS[typ]))
            self.verworfen.clear()       # 19.10.: neue Platzliste vom Spiel - frueher Abgelehntes darf wieder (Laufwege wandern)
        frei = [p for p in self.merk[typ][1] if p not in self.verworfen]
        return frei[0] if frei else None

    def soll(self, leute):
        return 0 if leute < self.PRO_KETTE else min(self.HOECHSTENS, int(math.ceil(leute / float(self.PRO_KETTE))))

    def schritt(self, st, G, ruecklage):
        aus = []
        n = self.soll(st.get("leute", 0))
        if not n or st.get("feuer", 0) < 1:
            return aus
        zahl = {typ: sum(1 for g in G.values() if g["besitzer"] == self.sp and g["typ"] == typ)
                for typ in (HOPFEN, BRAUEREI, SCHENKE)}
        for typ, name in ((HOPFEN, "Hopfenfarm"), (BRAUEREI, "Brauerei"), (SCHENKE, "Schenke")):
            if zahl[typ] >= n:
                continue
            holz, gold = self.preis(typ, "holz"), self.preis(typ, "gold")
            if st.get("holz", 0) - ruecklage.get("holz", 0) < holz or st.get("gold", 0) - ruecklage.get("gold", 0) < gold:
                return aus                   # die Reihe wartet: nicht die Brauerei vor der Hopfenfarm
            p = self._platz(typ, G, st.get("t", 0))
            if p is None:
                aus.append("BIER: kein Platz fuer %s (vom Spiel geprueft)" % name)
                continue
            ergebnis = self.baue(typ, p[0], p[1], 0)
            # 19.10. (1018w: der zweite Hopfenbau nahm denselben reservierten Platz noch einmal): gesetzt oder nicht - der
            # Platz ist fuer den naechsten Bau verbraucht
            self.verworfen.add(p)
            aus.append("BIER: %s %d/%d bei %s (Einwohner %d) -> %s" % (name, zahl[typ] + 1, n, p, st.get("leute", 0), ergebnis))
            return aus                       # hoechstens ein Bau je Runde
        return aus
