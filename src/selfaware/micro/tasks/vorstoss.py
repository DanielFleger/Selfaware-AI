# -*- coding: utf-8 -*-
"""Frueher Vorstoss der Schuetzen (B-172, Plan_Gehirn Schritte 3 und 5; Daniel 08.11.2026 "ja fruehe raids").

Vorbild ist Daniels Partie vom 19.10. (L147: "Bogenschuetzen vor, mit Sklaven abgefackelt; penetrant vorgestuermt, nie
lockergelassen"). Gemessen in lage_20261019_224031_i4_sp2 bis Takt 14.000: 6 arab. Bogenschuetzen als eine Gruppe rueckten
von der eigenen Burg in Schritten auf den Gegner zu (Abstand 245 -> 124 Felder), standen in 85 % der Bilder still und toeteten
32 Soldaten, ohne einen Bogenschuetzen zu verlieren. Unsere Starttruppen standen derweil daheim: Speer und Bogen stellen 28 %
der eingesetzten Zeit und 2 % der Wirkung (data/research/wirkung_je_einheit.json).

Erster Lauf 08.11. (vorstoss_1108b): 5 Bogenschuetzen standen 32 Felder vor 7 feindlichen Schuetzen, beschossen 2.000 Takte
denselben Feuerwerfer ohne Schaden und fielen alle. Deshalb bleibt die Gruppe nie im Schussfeld einer Ueberzahl stehen, sucht
Arbeiter ohne Schuetzendeckung und gibt Ziele auf, die keinen Schaden nehmen.

Je Runde, in dieser Reihenfolge:
  ALARM    stehen ALARM_N feindliche Soldaten bis ALARM_R an unserer Burg: die Gruppe gibt ihre Schuetzen frei (Waechter),
           und nimmt sie zurueck, sobald es ruhig ist. Rollen wechseln mit der Lage.
  WEICHEN  Nahkaempfer (ohne Sklaven) bis RUECK_R an der Gruppe: zurueck, weg vom Feind. Bogenschuetzen sind schneller (L80).
  ABZIEHEN  im Schussfeld einer Ueberzahl an Schuetzen oder eines Turms: zurueck, weg von dieser Gefahr.
  SCHIESSEN  Feind bis SCHUSS Felder: alle auf denselben, Soldaten vor Arbeitern. Schuetzen laufen auf Angriffsbefehle nicht
           los (S9). Nimmt ein Ziel STUR_RUNDEN lang keinen Schaden, ist es fuer eine Weile tabu.
  VORRUECKEN  sonst bis zu SCHRITT Felder auf eine Schussstellung vor dem naechsten Arbeiter, die ausserhalb jeder Ueberzahl
           liegt; gibt es keinen, vor das naechste Gebaeude.
Alle Grenzen sind Startwerte (Plan_Gehirn 5.6), keine Messwerte. Schalter vorstoss=ja, aus ist der Standard.
"""

import collections

SCHUETZEN = {22, 23, 70}
# ohne Sklaven: die verfolgen, tun Schuetzen aber kaum etwas
NAHKAMPF = {24, 25, 26, 27, 28, 55, 73, 75}
SKLAVE = 71
FERN_FEIND = {22, 23, 70, 72, 74, 76}
ARBEITER = {1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 21, 31}
TUERME = {74, 75, 76, 77, 78}
ZIEL_GEBAEUDE = {1, 3, 8, 9, 11, 19, 26, 5, 13, 18, 32, 31, 33, 10}
SCHUSS = 38  # S9: Pfeile reichen 40 Felder
STAND = 30  # Abstand der Schussstellung vom Arbeiter
SCHRITT = 12
HALT_VOR = 30
RUECK_R = 9
RUECK_WEITE = 12
ALARM_R = 25
ALARM_N = 3
GEFAHR_SCHUSS = 44
GEFAHR_NAH = 14
UEBERMACHT = 0.5  # mehr feindliche Schuetzen je eigenem gelten als Ueberzahl
STUR_RUNDEN = 6
STUR_SPERRE = 30
NEU_ALLE = 4  # Runden zwischen zwei gleichen Befehlen: jeder neue Befehl startet die Wegsuche neu
KARTE = 399


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ort(e):
    return (e["x"], e["y"])


def _mitte(L, nummern):
    xs = sorted(L[n]["x"] for n in nummern)
    ys = sorted(L[n]["y"] for n in nummern)
    return (xs[len(xs) // 2], ys[len(ys) // 2])


def _schritt_auf(von, zu, weite):
    d = schach(von, zu)
    if d == 0:
        return von
    w = min(weite, d)
    return (von[0] + (zu[0] - von[0]) * w // d, von[1] + (zu[1] - von[1]) * w // d)


def _weg_von(von, feind, weite):
    dx, dy = von[0] - feind[0], von[1] - feind[1]
    n = max(abs(dx), abs(dy), 1)
    x = max(0, min(KARTE, von[0] + weite * dx // n))
    y = max(0, min(KARTE, von[1] + weite * dy // n))
    return (x, y)


def _grob(p):
    """Ziele auf Raster: Eine fliehende Gruppe rechnet jede Runde eine etwas andere Stelle aus."""
    return (p[0] // 8, p[1] // 8)


class Vorstoss:
    def __init__(self, sp, heim, bis=15000):
        self.sp, self.heim, self.bis = sp, tuple(heim), bis
        self.mitglieder = set()
        self.runde = 0
        self.letzter = {}  # Art des Befehls -> (Inhalt, Runde)
        self.alarm_an = False
        self.befehle = collections.Counter()
        self.ziel_leben = {}  # Ziel -> (Leben, Runde des letzten Schadens)
        self.stur = {}  # Ziel -> tabu bis zu dieser Runde

    def orte(self, L):
        return [ort(L[n]) for n in self.mitglieder if n in L]

    def _meine(self, L):
        return {
            n
            for n, e in L.items()
            if e["besitzer"] == self.sp and e["typ"] in SCHUETZEN and e.get("leben", 1) > 0
        }

    def _feinde(self, L, arten):
        return [
            (n, e)
            for n, e in L.items()
            if e["besitzer"] not in (0, self.sp) and e["typ"] in arten and e.get("leben", 1) > 0
        ]

    def _alarm(self, L):
        feinde = self._feinde(L, NAHKAMPF | FERN_FEIND | {SKLAVE})
        return sum(1 for _, e in feinde if schach(ort(e), self.heim) <= ALARM_R) >= ALARM_N

    def _sende(self, art, inhalt, befehl, nummern, auftrag):
        alt = self.letzter.get(art)
        if alt is not None and alt[0] == inhalt and self.runde - alt[1] < NEU_ALLE:
            return False
        befehl({"angriff": dict(einheiten=sorted(nummern), **auftrag)}, 1.0, bis="ANGRIFF")
        self.letzter[art] = (inhalt, self.runde)
        self.befehle[art] += 1
        return True

    def _schussfeld(self, stelle, L, G, eigene):
        """Ort der naechsten Gefahr, wenn an dieser Stelle eine Ueberzahl an Schuetzen oder ein Turm hinreicht, sonst None."""
        for g in G.values():
            if (
                g["typ"] in TUERME
                and g.get("besitzer") not in (0, self.sp)
                and schach(ort(g), stelle) <= GEFAHR_SCHUSS
            ):
                return ort(g)
        nah = [
            ort(e)
            for _, e in self._feinde(L, FERN_FEIND)
            if schach(ort(e), stelle) <= GEFAHR_SCHUSS
        ]
        if len(nah) > UEBERMACHT * eigene:
            return min(nah, key=lambda p: schach(p, stelle))
        return None

    def _sicher(self, stelle, L, G, eigene):
        if self._schussfeld(stelle, L, G, eigene) is not None:
            return False
        return not any(schach(ort(e), stelle) <= GEFAHR_NAH for _, e in self._feinde(L, NAHKAMPF))

    def _stellung(self, L, G, mitte, eigene):
        """Schussstellung vor dem naechsten Arbeiter ohne Deckung, sonst vor dem naechsten Gebaeude."""
        arbeiter = sorted(
            (ort(e) for _, e in self._feinde(L, ARBEITER)), key=lambda p: schach(p, mitte)
        )
        for p in arbeiter:
            stand = _schritt_auf(p, mitte, STAND)
            if self._sicher(stand, L, G, eigene):
                return stand, p
        haeuser = sorted(
            (
                ort(g)
                for g in G.values()
                if g.get("besitzer") not in (0, self.sp) and g["typ"] in ZIEL_GEBAEUDE
            ),
            key=lambda p: schach(p, mitte),
        )
        for p in haeuser:
            stand = _schritt_auf(p, mitte, HALT_VOR)
            if self._sicher(stand, L, G, eigene):
                return stand, p
        return None, None

    def _ist_stur(self, k, e):
        """Nimmt dieses Ziel seit STUR_RUNDEN keinen Schaden? (Mauer, Hoehe, Sichtlinie: Schiessen bringt dort nichts.)"""
        if self.stur.get(k, 0) > self.runde:
            return True
        alt = self.ziel_leben.get(k)
        if alt is None or e.get("leben", 0) < alt[0]:
            self.ziel_leben[k] = (e.get("leben", 0), self.runde)
            return False
        if self.runde - alt[1] >= STUR_RUNDEN:
            self.stur[k] = self.runde + STUR_SPERRE
            self.ziel_leben.pop(k, None)
            return True
        return False

    def schritt(self, t, L, G, befehl):
        self.runde += 1
        aus = []
        if t >= self.bis:
            if self.mitglieder:
                aus.append(
                    "VORSTOSS: Ende bei Takt %d, %d Schuetzen wieder frei"
                    % (t, len(self.mitglieder))
                )
                self.mitglieder = set()
            return aus
        meine = self._meine(L)
        if self._alarm(L):
            if not self.alarm_an:
                aus.append(
                    "VORSTOSS: Feinde an der Burg, %d Schuetzen gehen an die Abwehr" % len(meine)
                )
            self.alarm_an = True
            self.mitglieder = set()
            return aus
        if self.alarm_an:
            aus.append("VORSTOSS: Burg ruhig, Schuetzen wieder im Vorstoss")
        self.alarm_an = False
        self.mitglieder = meine
        if not meine:
            return aus
        mitte = _mitte(L, meine)
        nah = min(
            ((schach(ort(e), mitte), ort(e), e["typ"]) for _, e in self._feinde(L, NAHKAMPF)),
            default=None,
        )
        if nah is not None and nah[0] < RUECK_R:
            ziel = _weg_von(mitte, nah[1], RUECK_WEITE)
            if self._sende("weichen", _grob(ziel), befehl, meine, {"lauf": [ziel[0], ziel[1]]}):
                aus.append(
                    "VORSTOSS: weicht Typ %d in %d Feldern aus -> %s" % (nah[2], nah[0], ziel)
                )
            return aus
        gefahr = self._schussfeld(mitte, L, G, len(meine))
        if gefahr is not None:
            ziel = _weg_von(mitte, gefahr, RUECK_WEITE)
            if self._sende("abziehen", _grob(ziel), befehl, meine, {"lauf": [ziel[0], ziel[1]]}):
                aus.append("VORSTOSS: zieht aus dem Schussfeld bei %s ab -> %s" % (gefahr, ziel))
            return aus
        kand = sorted(
            (0 if e["typ"] not in ARBEITER else 1, schach(ort(e), mitte), n)
            for n, e in self._feinde(L, NAHKAMPF | FERN_FEIND | {SKLAVE} | ARBEITER)
            if schach(ort(e), mitte) <= SCHUSS
        )
        for _, d, k in kand:
            if self._ist_stur(k, L[k]):
                continue
            if self._sende("schuss", k, befehl, meine, {"ziel": k}):
                aus.append(
                    "VORSTOSS: %d Schuetzen schiessen auf Typ %d in %d Feldern"
                    % (len(meine), L[k]["typ"], d)
                )
            return aus
        stand, ziel = self._stellung(L, G, mitte, len(meine))
        if stand is None or schach(mitte, stand) == 0:
            return aus
        stelle = _schritt_auf(mitte, stand, SCHRITT)
        if not self._sicher(stelle, L, G, len(meine)):
            return aus
        if self._sende("vor", stelle, befehl, meine, {"lauf": [stelle[0], stelle[1]]}):
            aus.append("VORSTOSS: rueckt vor %s -> %s, Ziel %s" % (mitte, stelle, ziel))
        return aus

    def bericht(self):
        return "Vorstoss: Befehle %s" % dict(self.befehle)
