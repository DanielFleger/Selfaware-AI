# -*- coding: utf-8 -*-
"""Bierkette (Daniel 19.10.2026: "Bierbeliebtheit mitnehmen - Hopfen zu Brauerei zu Bier, Schenke ... und das auf jeder Map").

Warum: unsere Beliebtheit liegt meist schon bei 100 - der Haushalt (haushalt.py) stellt die Steuer so hoch, dass die
naechste Woche noch ueber dem Boden (95) liegt, und misst alles, was seine Tabelle nicht kennt, als "Rest". Bier hebt
diesen Rest -> hoehere Steuerstufe -> mehr Gold fuer Wirtschaft und Waffen.

Kartenunabhaengig: jeder Platz kommt vom Spiel selbst (plaetze(typ, kern, r) = Modulbefehl platzkarte, Bauregeln des
Spiels je Feld), nichts ist fuer eine Karte eingetragen. Ablauf je Runde (schritt):
  SOLL     10.11. (Daniel 21:52/21:54: "ohne feste Hopfenfarm-Grenze, einfach nach den gemessenen Werten", Schenke "erst wenn das
           erste Bier im Lager ist"): Schenken nach Einwohnern (eine je PRO_KETTE), Brauereien und Hopfenfarmen nach dem Lager:
           Brauerei, sobald Hopfen liegt, eine weitere, wenn sich Hopfen staut; Schenke, sobald Bier liegt, eine weitere, wenn sich
           Bier staut; Hopfenfarm, wenn die Brauereien ueber ein ganzes FENSTER ohne Hopfen bleiben und sich kein Bier staut.
           Die Zeilen REIHE unten galten bis dahin (feste Kette 1:1:1, hoechstens 4).
  REIHE    19.10. (Daniel, 1019a: "wir haben sogar schon Bier und noch keine Schenke - sobald das erste Bier geliefert ist,
           soll der erste Wirt losgehen koennen"; 1019a: die zweite Hopfenfarm scheiterte 20-mal, die Schenke kam nie dran):
           ENGPASS ZUERST - Schenke, solange es weniger Schenken als Brauereien gibt; Brauerei, solange weniger Brauereien
           als Hopfenfarmen (Kette 1:1:1 - Annahme, das Verhaeltnis ist nicht gemessen); sonst Hopfenfarm. Scheitert ein
           Bau, kommt in derselben Runde das naechste Glied dran. Je Runde hoechstens ein gesetzter Bau, nur mit Holz und
           Gold ueber der Ruecklage der Wirtschaft (wirt.ruecklage) und einem Arbeiter am Feuer.
  PLAETZE  Hopfen bis 45 Felder um das Lager (findet das Spiel dort nichts: 90, dann 150), Brauerei 20 um das Lager,
           Schenke 20 um den Kornspeicher (sonst Lager); je Art geholt und nach Fehlschlag oder alle 3.000 Ticks neu;
           abgelehnte Plaetze je Art; ein reservierter Hopfenplatz wird genau einmal versucht.
"""

import math

HOPFEN, BRAUEREI, SCHENKE, KORNSPEICHER, LAGER = 31, 18, 22, 19, 10


class Bierkette:
    PRO_KETTE = 30  # Einwohner je Schenke (Daniel: "30 Bevoelkerung ... bei einer Schenke")
    FENSTER = 1500  # Startwert, UNGEMESSEN: so viele Takte muss das Lager zeigen, dass ein Glied fehlt oder sich staut
    NEU_PLAETZE = 3000  # Ticks, nach denen die Platzliste neu vom Spiel geholt wird
    RADIUS = {HOPFEN: 45, BRAUEREI: 20, SCHENKE: 20}
    WEITER = (
        2,
        10.0 / 3,
    )  # 19.10. (1019a): findet das Spiel im Umkreis nichts, Umkreis x2, dann x3,3 (Hopfen 90, 150)
    RESERVE = 2  # Hopfenplaetze, die gleich beim Start fuer andere Bauten gesperrt werden (fruchtbarer Boden)

    def __init__(self, sp, baue, plaetze, preis):
        """baue(typ, x, y, r) -> Bauergebnis (wahr = gesetzt); plaetze(typ, kern, r) -> [(x, y)] vom Spiel;
        preis(typ, ware) -> Baukosten."""
        self.sp, self.baue, self.plaetze, self.preis = sp, baue, plaetze, preis
        self.merk = {}  # typ -> (Tick, [Plaetze])
        self.verworfen = {}  # typ -> {Plaetze}
        self.reserviert = []  # beim Start gesperrte Hopfenplaetze (setzt erstes_spiel) - werden zuerst genommen
        self.naechster = (
            None  # 19.10.: Art des naechsten faelligen Baus (fuer die Steinreserve des Lenkers)
        )
        self.verlauf = []  # 10.11.: (Takt, Hopfen, Bier) im Lager waehrend der letzten FENSTER Takte

    def _kern(self, G, typ):
        eig = [g for g in G.values() if g["besitzer"] == self.sp]
        wahl = [g for g in eig if g["typ"] == (KORNSPEICHER if typ == SCHENKE else LAGER)] or [
            g for g in eig if g["typ"] == LAGER
        ]
        if not wahl:
            return None
        return (sum(g["x"] for g in wahl) // len(wahl), sum(g["y"] for g in wahl) // len(wahl))

    def _platz(self, typ, G, t):
        if typ == HOPFEN and self.reserviert:
            return self.reserviert.pop(
                0
            )  # 19.10. (1019a: (52, 205) trug Hopfenfarm 1 und wurde 20-mal wieder versucht)
        kern = self._kern(G, typ)
        if kern is None:
            return None
        weg = self.verworfen.setdefault(typ, set())
        m = self.merk.get(typ)
        if m is None or t - m[0] >= self.NEU_PLAETZE or not [p for p in m[1] if p not in weg]:
            liste = []
            for f in (1,) + self.WEITER:
                liste = self.plaetze(typ, kern, int(self.RADIUS[typ] * f))
                if liste:
                    break
            self.merk[typ] = (t, liste)
            weg.clear()  # 19.10.: neue Platzliste vom Spiel - frueher Abgelehntes darf wieder (Laufwege wandern)
        frei = [p for p in self.merk[typ][1] if p not in weg]
        return frei[0] if frei else None

    def stein_bedarf(self):
        """19.10. (1019b: das Wirtshaus scheiterte 7-mal an 5-8 fehlendem Stein): Stein fuer den naechsten faelligen Bau -
        der Lenker haelt ihn vom Verkauf und vom Tausch gegen Holz zurueck."""
        return self.preis(self.naechster, "stein") if self.naechster else 0

    def soll(self, leute):
        """Schenken nach Einwohnern, eine je PRO_KETTE, ohne feste Obergrenze."""
        return 0 if leute < self.PRO_KETTE else int(math.ceil(leute / float(self.PRO_KETTE)))

    def _merken(self, st):
        t = st.get("t", 0)
        self.verlauf.append((t, st.get("hopfen", 0), st.get("bier", 0)))
        self.verlauf = [v for v in self.verlauf if t - v[0] <= self.FENSTER]

    def _fenster_voll(self):
        return (
            len(self.verlauf) >= 2
            and self.verlauf[-1][0] - self.verlauf[0][0] >= 0.9 * self.FENSTER
        )

    def _leer(self, i):
        """Ware i (1 Hopfen, 2 Bier) lag das ganze Fenster ueber nicht im Lager."""
        return self._fenster_voll() and all(v[i] == 0 for v in self.verlauf)

    def _staut(self, i):
        """Ware i lag schon am Anfang des Fensters im Lager und ist seither mehr geworden."""
        return self._fenster_voll() and self.verlauf[-1][i] > self.verlauf[0][i] > 0

    def reihe(self, st, zahl):
        """[(Art, Name)] der faelligen Glieder, dringendstes zuerst - nur nach Einwohnern und Lager, keine feste Zahl."""
        aus = []
        if (
            zahl[SCHENKE] < self.soll(st.get("leute", 0))
            and st.get("bier", 0) > 0
            and (zahl[SCHENKE] == 0 or self._staut(2))
        ):
            aus.append((SCHENKE, "Schenke"))
        if st.get("hopfen", 0) > 0 and (zahl[BRAUEREI] == 0 or self._staut(1)):
            aus.append((BRAUEREI, "Brauerei"))
        erste = zahl[HOPFEN] == 0 and st.get("leute", 0) >= self.PRO_KETTE
        hungrig = zahl[BRAUEREI] > 0 and self._leer(1) and not self._staut(2)
        if erste or hungrig:
            aus.append((HOPFEN, "Hopfenfarm"))
        return aus

    def schritt(self, st, G, ruecklage):
        aus = []
        self._merken(st)
        self.naechster = None
        if st.get("feuer", 0) < 1:
            return aus
        zahl = {
            typ: sum(1 for g in G.values() if g["besitzer"] == self.sp and g["typ"] == typ)
            for typ in (HOPFEN, BRAUEREI, SCHENKE)
        }
        n = self.soll(st.get("leute", 0))
        reihe = self.reihe(st, zahl)
        for typ, name in reihe:
            if self.naechster is None:
                self.naechster = typ
            holz, gold, stein = (
                self.preis(typ, "holz"),
                self.preis(typ, "gold"),
                self.preis(typ, "stein"),
            )
            # 19.10. (1019b): auch Stein - das Wirtshaus braucht ihn, das Spiel lehnte sonst jeden Bau ab ("fehlt stein 8")
            if (
                st.get("holz", 0) - ruecklage.get("holz", 0) < holz
                or st.get("gold", 0) - ruecklage.get("gold", 0) < gold
                or st.get("stein", 0) < stein
            ):
                return aus  # die Reihe wartet auf das dringendste Glied
            p = self._platz(typ, G, st.get("t", 0))
            if p is None:
                aus.append("BIER: kein Platz fuer %s (vom Spiel geprueft)" % name)
                continue
            ergebnis = self.baue(typ, p[0], p[1], 0)
            # 19.10. (1018w: der zweite Hopfenbau nahm denselben reservierten Platz noch einmal): gesetzt oder nicht - der
            # Platz ist fuer den naechsten Bau verbraucht
            self.verworfen.setdefault(typ, set()).add(p)
            aus.append(
                "BIER: %s Nr. %d bei %s (Einwohner %d, Schenken-Soll %d, Hopfen %d, Bier %d im Lager) -> %s"
                % (
                    name,
                    zahl[typ] + 1,
                    p,
                    st.get("leute", 0),
                    n,
                    st.get("hopfen", 0),
                    st.get("bier", 0),
                    ergebnis,
                )
            )
            if ergebnis:
                return aus  # hoechstens ein gesetzter Bau je Runde
        return aus
