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

Schalter ausweichen=ja (B-174, B-178, aus ist der Standard): Unter Beschuss fuehrt der Rust-Kern Vorruecken und Abziehen im Zickzack,
damit Pfeile daneben gehen. Dicht aufgestellt faengt der Nachbar den verfehlten Pfeil, darum laeuft die Gruppe breit: bis zu TRUPPS Plaetze
mit LUECKE Feldern Abstand, jeder Platz sein eigener Trupp beim Kern (gemessen im Gefecht, data/research/auge_plan/
zickzack_20261108/Ergebnis_Zickzack.md: ab 12 Feldern 87 % Treffer gerade, 38 bis 61 % im Zickzack dicht, 4,5 % im Zickzack
breit). Jeden anderen Befehl gibt der Vorstoss vorher frei, damit nie zwei Stellen dieselbe Einheit fuehren.
"""

import collections
import math

from selfaware.baukasten import formation
from selfaware.baukasten.ausweichen import Schussfeld
from selfaware.micro.tasks.raids import SPERRE_RUNDEN
from selfaware.micro.unit_log import Action, point, unit
from selfaware.services.schussfeld import REICHWEITE

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
# B-182 (Partie 11.11. 23:49, Fehlerwache F2): 14 Schleuderer lagerten 45 Felder vor der Burg - der Vorstoss zog sich achtmal vor
# ihnen zurueck (fuer ihn traf jeder feindliche Fernkaempfer 44 Felder weit) und schoss nie, obwohl Schleuderer nur 22 Felder weit
# treffen (schussfeld.REICHWEITE, gemessen P3 08.11.) und unsere Schuetzen 40. Jetzt gilt die Gefahr je Art wie in der Wegfuehrung;
# wen wir so ueberreichen, den nimmt der Vorstoss auch weiter weg aufs Korn. Startwerte, nicht gemessen:
UEBERREICHT = 28  # Gefahr hoechstens so weit: Schleuderer (22), Feuerwerfer (15)
ANGRIFF_WEIT = 60  # so weit von der Gruppe nimmt der Vorstoss ueberreichte Schuetzen aufs Korn
# B-182 (Partie 11.11. 23:53, Fehlerwache F2): die Gruppe (9 Schuetzen) stand 1.000 Takte vorn - jedes Ziel in 38 Feldern war gedeckt
# (1-2 Armbrustschuetzen am Standplatz), der Vorstoss probierte sie der Reihe nach und gab sie auf; fuer 29 bis 35 von 34 bis 40
# feindlichen Einheiten fand die Wegfuehrung aber einen sicheren Standplatz. Startwert, nicht gemessen:
FERNZIEL_MAX = 120  # so weit sucht der Vorstoss ein Ziel, das er sicher beschiessen kann
SCHUETZE_PRUEF = (
    70  # fuer diese Art fragt er die Wegfuehrung (erfassen: 22, 23 und 70 je 40 Felder)
)
# B-182 (Partie 11.11. 23:40, Fehlerwache F3): Startwerte, nicht gemessen - so weit vom Treffpunkt gilt ein Schuetze als
# Nachzuegler; so weit darf der Treffpunkt wandern, bevor er neu gilt
SAMMELN_AB = 15
TREFF_WANDERT = 8
STUR_RUNDEN = 6
STUR_SPERRE = 30
NEU_ALLE = 4  # Runden zwischen zwei gleichen Befehlen: jeder neue Befehl startet die Wegsuche neu
KARTE = 399
# Laeufe unter Pfeilen, die der Kern im Zickzack fuehrt. Weichen vor Nahkaempfern bleibt gerade: Dort geht es um jedes Feld.
AUSWEICHEN_BEI = {"vor", "abziehen"}
# #361 (Daniel 16.11.2026 00:27): die Gruppe zieht auch zu einem Ziel, das ein Feind deckt, wenn die Gefechtsrechnung am Platz vor dem
# Ziel einen Sieg erwartet - mit Beschuss auf dem geraden Weg dorthin (Daniel 15.11.2026 23:28 "beim erwarteten beschuss von anderen die
# auf dem weg noch dazukommen"). Startwerte, nicht gemessen:
WEG_PROBE = 8  # Felder zwischen zwei Prueforten auf dem Weg (wie assassinen.WEG_PROBE)
STAND_VOR = 4  # so viele Felder innerhalb der eigenen Schussweite steht die Gruppe vor dem Ziel (wie wegfuehrung.FERN_STAND)
LUECKE = 5  # Gefahrenkarte zickzack_abstand.txt: quer zur Schussrichtung bei 2 und 3 Feldern bis 23 %, ab 5 Feldern unter 2 %
TRUPPS = 8  # Einzelbefehle je Feld, die im Lauf zickzack2_g alle rechtzeitig kamen; ein neunter daneben kam in 18 % statt 6 % der Faelle zu spaet
SPALTEN = 4  # 8 Plaetze in 2 Reihen, so gemessen


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


def _luft(a, b):
    """Luftlinie in Feldern - so misst das Spiel die Schussweite (acquireShootTarget, S9)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _grob(p):
    """Ziele auf Raster: Eine fliehende Gruppe rechnet jede Runde eine etwas andere Stelle aus."""
    return (p[0] // 8, p[1] // 8)


class Vorstoss:
    def __init__(self, sp, heim, bis=15000, kern=None):
        self.sp, self.heim, self.bis = sp, tuple(heim), bis
        # None = ohne Zickzack, sonst der Kernweg (zickzack, freigeben, aufraeumen)
        self.kern = kern
        self.platz = {}  # Einheit -> Platz in der breiten Aufstellung
        self.plaetze = (
            TRUPPS  # so viele Plaetze darf der Vorstoss gerade belegen (der Brandtrupp geht vor)
        )
        self.lage = {}
        self.schuss = Schussfeld(sp)  # B-178: Vorruecken nur unter Beschuss im Zickzack
        self.mitglieder = set()
        self.runde = 0
        self.letzter = {}  # Art des Befehls -> (Inhalt, Runde)
        self.alarm_an = False
        self.befehle = collections.Counter()
        self.ziel_leben = {}  # Ziel -> (Leben, Runde des letzten Schadens)
        self.stur = {}  # Ziel -> tabu bis zu dieser Runde
        self.weg = (
            None  # B-182: gemeinsame Wegfuehrung (micro/wegfuehrung.py), setzt der Raid-Einsatz
        )
        self.gefuehrt = None  # Ziel, zu dem die Wegfuehrung die Schuetzen gerade fuehrt
        self.gesperrt = {}  # Ziel -> Runde: die Wegfuehrung fand fuer keinen Schuetzen Angriff oder Weg
        self.vor_ort = None  # Stelle, zu der die Wegfuehrung die Schuetzen beim Vorruecken fuehrt
        self.vor_bis = (
            -1
        )  # bis zu dieser Runde kein Vorruecken (die Wegfuehrung fand die Stelle nicht sicher)
        self._treff = None  # B-182: Treffpunkt der Nachzuegler
        self._nachzuegler = set()
        self.absicht = {}  # B-182 Logbuch je Einheit: Schuetze -> (Aktion, Ziel, Grund, Werte) dieser Runde

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

    def _loslassen(self, nummern):
        """B-182: ein Fuehrer je Einheit - bevor der Vorstoss selbst befiehlt oder die Schuetzen abgibt, laesst die Wegfuehrung sie los."""
        if self.weg is not None:
            for n in nummern:
                self.weg.loslassen(n)
        self.gefuehrt = None
        self.vor_ort = None

    def _aufgeben(self, aus):
        """B-182: Meldet die Wegfuehrung fuer jeden gefuehrten Schuetzen "gefahr" oder "kein_weg", sperrt der Vorstoss das Ziel."""
        if self.weg is None or self.gefuehrt is None:
            return
        st = {self.weg.status(n) for n in self.mitglieder if self.weg.fuehrt(n)}
        if st and st <= {"gefahr", "kein_weg"}:
            self.gesperrt[self.gefuehrt] = self.runde + SPERRE_RUNDEN
            aus.append("VORSTOSS: gibt Ziel %d auf (%s)" % (self.gefuehrt, "/".join(sorted(st))))
            self._loslassen(self.mitglieder)

    def _sende(self, art, inhalt, befehl, nummern, auftrag):
        self._loslassen(nummern)  # B-182: Vorruecken und Ausweichen fuehrt der Vorstoss selbst
        alt = self.letzter.get(art)
        if alt is not None and alt[0] == inhalt and self.runde - alt[1] < NEU_ALLE:
            return False
        if not self._im_ausweichen(art, nummern, auftrag):
            befehl({"angriff": dict(einheiten=sorted(nummern), **auftrag)}, 1.0, bis="ANGRIFF")
        self.letzter[art] = (inhalt, self.runde)
        self.befehle[art] += 1
        return True

    def _im_ausweichen(self, art, nummern, auftrag):
        """True, wenn der Kern diesen Lauf im Zickzack fuehrt. Sonst fuehrt das Modul, und der Kern gibt die Einheiten vorher her."""
        if self.kern is None:
            return False
        feuer = art == "abziehen" or any(self.schuss.unter_feuer(n, self.lage[n]) for n in nummern)
        plan = (
            self._aufstellung(nummern, auftrag["lauf"]) if art in AUSWEICHEN_BEI and feuer else []
        )
        if plan and all([self.kern.ausweichen(e, z, t) for e, z, t in plan]):
            return True
        self._frei(nummern)
        return False

    def _aufstellung(self, nummern, ziel):
        """(Einheiten, Ziel, Trupp) je Platz: nebeneinander quer zum Weg, hintereinander in Reihen, mit LUECKE Feldern Abstand. Die Plaetze
        bleiben, solange die Gruppe dieselbe ist: Der Kern merkt sich je Trupp den Ort, eine Einheit im falschen Trupp liefe quer durch die Gruppe."""
        mitte = _mitte(self.lage, nummern)
        n = min(len(nummern), self.plaetze)
        if n == 0:
            return []
        if set(self.platz) != set(nummern) or len(set(self.platz.values())) != n:
            quer = formation.querachse(mitte, ziel)
            geordnet = sorted(nummern, key=lambda k: (self.lage[k][quer], k))
            self.platz = {k: i * n // len(geordnet) for i, k in enumerate(geordnet)}
        return [
            (
                sorted(k for k, v in self.platz.items() if v == p),
                (max(0, min(KARTE, x)), max(0, min(KARTE, y))),
                p + 1,
            )
            for p, (x, y) in enumerate(formation.breit(mitte, ziel, n, LUECKE, SPALTEN))
        ]

    def _frei(self, nummern):
        if self.kern is not None and nummern:
            self.kern.freigeben(sorted(nummern))

    def _melde(self, nummern, aktion, ziel, grund, **werte):
        """B-182 Logbuch je Einheit: eine Absicht fuer die ganze Gruppe (Nachzuegler meldet _sammeln danach als GATHER)."""
        for n in nummern:
            self.absicht[n] = (aktion, ziel, grund, werte)

    def _sammeln(self, L, meine, mitte, aus):
        """B-182 (Partie 11.11. 23:40, Fehlerwache F3): kann der Vorstoss nicht sicher vorruecken, holt er Nachzuegler zur Gruppe -
        A_ARCHER 70 Nr. 422 stand 2.000 Takte zu Hause, 53 Felder hinter seiner Gruppe, die vorn wartete. Treffpunkt ist die Mitte
        (Median, Nachzuegler verschieben sie kaum; die Wegfuehrung rueckt sie aufs naechste begehbare Feld); sie bleibt, solange sie
        nicht mehr als TREFF_WANDERT Felder wandert."""
        if self.weg is None or not meine:
            return
        treff = mitte
        if self._treff is not None and schach(self._treff, treff) <= TREFF_WANDERT:
            treff = self._treff
        self._treff = treff
        weit = sorted(n for n in meine if schach(ort(L[n]), treff) > SAMMELN_AB)
        for n in weit:
            self.weg.fuehre(n, "ort", treff, "vorstoss")
            self.absicht[n] = (
                Action.GATHER,
                point(treff),
                "straggler",
                {"dist": schach(ort(L[n]), treff)},
            )
        if set(weit) - self._nachzuegler:
            aus.append("VORSTOSS: holt %d Nachzuegler zur Gruppe bei %s" % (len(weit), treff))
        self._nachzuegler = set(weit)

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
            if _luft(ort(e), stelle) <= REICHWEITE.get(e["typ"], GEFAHR_SCHUSS)
        ]
        # Daniel 15.11.2026 23:28 ("auch bogenschuetzen von uns gegen ihre - wenn wir gegen sie gewinnen koennen dann lieber engagen, dann
        # haben andere nahkaempfer wieder mehr platz zum raiden. natuerlich nur bei erwartetem gewinn"): eine Ueberzahl ist nur Gefahr,
        # wenn die Gefechtsrechnung keinen Sieg erwartet (vorher reichte UEBERMACHT x eigene Schuetzen fuer den Rueckzug)
        if len(nah) > UEBERMACHT * eigene and not self._gewinnt(stelle, L):
            return min(nah, key=lambda p: schach(p, stelle))
        return None

    def _gewinnt(self, stelle, L, von=None):
        """Gefechtsrechnung (services/gefecht.py): unsere Schuetzen an stelle gegen alle feindlichen Schuetzen, die stelle in ihrer
        Reichweite haben (aktiv, nicht geschaetzt), und alle feindlichen Nahkaempfer bis GEFAHR_NAH. True bei Sieg mit mindestens
        gefecht.BEHALTEN unseres Lebens. von (#361): dazu jeder feindliche Schuetze, der den geraden Weg von dort nach stelle trifft (alle
        WEG_PROBE Felder geprueft). Je Runde gemerkt."""
        merk = getattr(self, "_gewinnt_merk", None)
        if merk is None or merk[0] != (self.runde, id(L)):
            merk = self._gewinnt_merk = ((self.runde, id(L)), {})
        schl = (tuple(stelle), tuple(von) if von is not None else None)
        if schl not in merk[1]:
            merk[1][schl] = self._gewinnt_rechnen(stelle, L, von)
        return merk[1][schl]

    def _gewinnt_rechnen(self, stelle, L, von):
        import selfaware.services.gefecht as gefecht

        proben = [stelle]
        if von is not None and schach(von, stelle) > WEG_PROBE:
            proben += [
                _schritt_auf(von, stelle, w) for w in range(0, schach(von, stelle), WEG_PROBE)
            ]
        # #361: mit von startet die Gruppe in der Rechnung dort und laeuft hin - so schiessen die Schuetzen am Weg wirklich mit (an stelle
        # gesetzt waeren sie ausser Reichweite und zaehlten nicht; wie assassinen._stapel_rechnung, wo der Stapel am eigenen Ort startet)
        start = von if von is not None else stelle
        wir = [
            dict(typ=L[n]["typ"], leben=L[n].get("leben", 1), x=start[0], y=start[1])
            for n in sorted(self.mitglieder)
            if n in L
        ]
        if not wir:
            return False
        sie = []
        for _, e in self._feinde(L, FERN_FEIND | NAHKAMPF):
            q = ort(e)
            if e["typ"] in FERN_FEIND and any(
                _luft(q, p) <= REICHWEITE.get(e["typ"], GEFAHR_SCHUSS) for p in proben
            ):
                sie.append(dict(typ=e["typ"], leben=e.get("leben", 1), x=q[0], y=q[1], steht=True))
            elif e["typ"] in NAHKAMPF and schach(q, stelle) <= GEFAHR_NAH:
                sie.append(dict(typ=e["typ"], leben=e.get("leben", 1), x=q[0], y=q[1]))
        if not sie:
            return True
        try:
            r_wir, _r_sie, _t, sieg = gefecht.simuliere(wir, sie)
        except Exception:  # ohne Rechnung kein Gefecht - wie bisher zurueck
            return False
        return bool(sieg) and r_wir >= gefecht.BEHALTEN * sum(w["leben"] for w in wir)

    def _darf(self, k, L, G, mitte):
        """ "sicher" (die Wegfuehrung findet einen Platz, an dem niemand trifft), "sieg" (die Gruppe gewinnt am Platz vor dem Ziel, Beschuss
        auf dem Weg mitgerechnet) oder None. Daniel 15.11.2026 23:28: Schuetze gegen Schuetze bei erwartetem Sieg; #361 (16.11. 00:27
        "das androhen ist schon meist genug ... die bogenschuetzen koennten extrem gut wirtschaft stoeren"): jedes Ziel, auch ein
        gedeckter Arbeiter - vorher nur feindliche Schuetzen und gerechnet an der Gruppenmitte statt vor dem Ziel."""
        if self._sicher_zu_beschiessen(k, L, G, mitte):
            return "sicher"
        if self.weg is None:
            return None
        stand = _schritt_auf(ort(L[k]), mitte, max(1, SCHUSS - STAND_VOR))
        return "sieg" if self._gewinnt(stand, L, von=mitte) else None

    def _darf_beschiessen(self, k, L, G, mitte):
        return self._darf(k, L, G, mitte) is not None

    def _weitester_sicherer(self, mitte, stand, L, G, eigene):
        """Daniel 15.11.2026 23:29 ("die bogenschuetzen laufen nicht direkt vor sondern warten und stocken"): Probe 23:29 - je Runde nur
        SCHRITT (12) Felder vor, dann Stillstand bis zur naechsten Runde, die Stellung ~170 Felder weg. Jetzt der weiteste Punkt Richtung
        Stellung, bis zu dem jeder Zwischenpunkt (alle SCHRITT Felder) nach derselben Regel sicher ist; der erste unsichere beendet den
        Weg. Ist schon der erste unsicher, bleibt es der erste (der Aufrufer meldet dann advance_unsafe wie bisher)."""
        d = min(
            schach(mitte, stand), getattr(self, "vor_max", None) or 10**6
        )  # Daniel 00:21: nach "gefahr" hoechstens vor_max
        erster = _schritt_auf(mitte, stand, SCHRITT)
        if not self._sicher(erster, L, G, eigene):
            return erster
        bis = erster
        for w in range(2 * SCHRITT, d + SCHRITT, SCHRITT):
            p = _schritt_auf(mitte, stand, min(w, d))  # nie ueber d (nach "gefahr": vor_max) hinaus
            if not self._sicher(p, L, G, eigene):
                break
            bis = p
        return bis

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

    def _sicher_zu_beschiessen(self, k, L, G, mitte):
        """B-182: Faende die Wegfuehrung einen Standplatz in Reichweite von k, an dem niemand trifft (oder Freigabe)? Ohne Wegfuehrung
        wie bisher: ja."""
        return self.weg is None or self.weg.schuss_moeglich(
            SCHUETZE_PRUEF, mitte, ort(L[k]), L, G, "vorstoss"
        )

    def _fernziel(self, L, G, mitte):
        """B-182: der naechste Feind bis FERNZIEL_MAX, den die Gruppe sicher beschiessen kann - (Nummer, Abstand) oder None."""
        if self.weg is None:
            return None
        kand = sorted(
            (_luft(ort(e), mitte), n)
            for n, e in self._feinde(L, NAHKAMPF | FERN_FEIND | {SKLAVE} | ARBEITER)
            if _luft(ort(e), mitte) <= FERNZIEL_MAX
        )
        for d, k in kand:
            if self.stur.get(k, 0) > self.runde or self.gesperrt.get(k, -1) > self.runde:
                continue
            if self._darf_beschiessen(k, L, G, mitte):  # #361: auch bei erwartetem Sieg
                return k, d
        return None

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

    def fuehrt(self, t):
        """True, solange der Vorstoss Schuetzen fuehrt; ab bis gibt schritt sie frei. B-182 Reihe 6: Der Kauf nach Wirkung kaufte Arabische
        Bogenschuetzen (Typ 70) nur fuer den Vorstoss, gegen den BierKoenig aber 42 von 46 Kaufzeilen nach Takt 15.000 - fuer niemanden."""
        return t < self.bis

    def anspruch(self, t, L):
        """Die Schuetzen, die der Vorstoss in dieser Runde fuehrt oder gleich aufnimmt - fuer die Module, die VOR ihm laufen.
        13.11.2026 Partie 6: in der ersten Runde war mitglieder noch leer, der Posten-Befehl des Waechters ging an alle 12 Truppen,
        der Vorstoss nahm die 5 Bogenschuetzen im selben Takt (674) - Bogenschuetze 310 lief nie zum Posten, die Kettenpruefung hielt
        die Partie bei Takt 1127 an."""
        if not self.fuehrt(t) or self.alarm_an:
            return set(self.mitglieder)
        return set(self.mitglieder) | self._meine(L)

    def schritt(self, t, L, G, befehl):
        self.runde += 1
        self.lage = L
        self.schuss.neue_runde(L, G)
        aus = []
        self.absicht = {}
        if t >= self.bis:
            if self.mitglieder:
                self._melde(
                    self.mitglieder,
                    Action.HOLD_POST,
                    None,
                    "advance_ended_back_to_guard",
                    until=self.bis,
                )
                aus.append(
                    "VORSTOSS: Ende bei Takt %d, %d Schuetzen wieder frei"
                    % (t, len(self.mitglieder))
                )
                self._loslassen(self.mitglieder)
                self._frei(self.mitglieder)
                self.mitglieder = set()
            return aus
        meine = self._meine(L)
        if self._alarm(L):
            if not self.alarm_an:
                aus.append(
                    "VORSTOSS: Feinde an der Burg, %d Schuetzen gehen an die Abwehr" % len(meine)
                )
            self.alarm_an = True
            self._melde(self.mitglieder | meine, Action.DEFEND, None, "alarm_released_to_guard")
            self._loslassen(self.mitglieder | meine)
            self._frei(self.mitglieder)
            self.mitglieder = set()
            return aus
        if self.alarm_an:
            aus.append("VORSTOSS: Burg ruhig, Schuetzen wieder im Vorstoss")
        self.alarm_an = False
        self.mitglieder = meine
        if self.kern is not None:
            self.kern.aufraeumen(meine)
        if not meine:
            return aus
        mitte = _mitte(L, meine)
        nah = min(
            ((schach(ort(e), mitte), ort(e), e["typ"]) for _, e in self._feinde(L, NAHKAMPF)),
            default=None,
        )
        if nah is not None and nah[0] < RUECK_R:
            ziel = _weg_von(mitte, nah[1], RUECK_WEITE)
            self._melde(meine, Action.FLEE, point(ziel), "melee_near", typ=nah[2], dist=nah[0])
            # Wegfuehrung frei: Flucht - weg vom Nahkaempfer an der Gruppe
            if self._sende("weichen", _grob(ziel), befehl, meine, {"lauf": [ziel[0], ziel[1]]}):
                aus.append(
                    "VORSTOSS: weicht Typ %d in %d Feldern aus -> %s" % (nah[2], nah[0], ziel)
                )
            return aus
        gefahr = self._schussfeld(mitte, L, G, len(meine))
        if gefahr is not None:
            ziel = _weg_von(mitte, gefahr, RUECK_WEITE)
            self._melde(
                meine, Action.RETREAT, point(ziel), "outnumbered_or_tower", at=point(gefahr)
            )
            # Wegfuehrung frei: Flucht - aus dem Schussfeld einer Uebermacht oder eines Turms
            if self._sende("abziehen", _grob(ziel), befehl, meine, {"lauf": [ziel[0], ziel[1]]}):
                aus.append("VORSTOSS: zieht aus dem Schussfeld bei %s ab -> %s" % (gefahr, ziel))
            return aus
        # B-182 (Fehlerwache 10.11. 23:28): Schiessen prueft Luftlinie (S9, services/spielwerte), nicht Schach. Arbeiter 307 lag im
        # Schachmass 38 Felder weg, nach Luftlinie 40,9: die Schuetzen standen mit ihm als Ziel und trafen nie (Leben blieb 2.500)
        kand = sorted(
            (0 if e["typ"] not in ARBEITER else 1, _luft(ort(e), mitte), n)
            for n, e in self._feinde(L, NAHKAMPF | FERN_FEIND | {SKLAVE} | ARBEITER)
            if _luft(ort(e), mitte) <= SCHUSS
            or (
                e["typ"] in FERN_FEIND
                and REICHWEITE.get(e["typ"], GEFAHR_SCHUSS) <= UEBERREICHT
                and _luft(ort(e), mitte) <= ANGRIFF_WEIT
            )
        )
        self._aufgeben(aus)
        fern = None
        if self.weg is not None and not any(
            not (self._ist_stur(k, L[k]) or self.gesperrt.get(k, -1) > self.runde)
            and self._darf_beschiessen(k, L, G, mitte)
            for _, _d, k in kand
        ):
            fern = self._fernziel(L, G, mitte)
            if fern is not None:
                kand = [(0, fern[1], fern[0])]
        # B-186 #81 (Daniel 15.11.2026 13:06 "warum springen die bogenschuetzen noch so hin und her"; 23:29 "warten und stocken"): das
        # Ziel der Vorrunde zuerst - die Gruppe behaelt es, solange es geht, statt jede Runde das naechste zu nehmen
        kand = sorted(kand, key=lambda x: x[2] != self.gefuehrt)
        for _, d, k in kand:
            if self._ist_stur(k, L[k]) or self.gesperrt.get(k, -1) > self.runde:
                continue
            darf = self._darf(k, L, G, mitte) if self.weg is not None else "sicher"
            if darf is None:
                continue  # B-182: gedeckt - nicht erst probieren und aufgeben (ausser Sieg erwartet, Daniel 23:28)
            self._melde(
                meine,
                Action.ATTACK_UNIT,
                unit(k),
                "far_safe_target" if fern is not None else "safe_target_in_range",
                typ=L[k]["typ"],
                dist=int(d),
            )
            if self.weg is not None:
                # B-182 (Plan_Wegfuehrung.md): jeden Schuetzen fuehrt die Wegfuehrung bis in seine eigene Reichweite, jede Runde neu
                self._frei(meine)  # der Zickzack des Kerns gibt sie vorher her - nie zwei Fuehrer
                for art in ("vor", "weichen", "abziehen"):
                    self.letzter.pop(
                        art, None
                    )  # der naechste eigene Lauf geht danach sofort hinaus, nicht erst nach NEU_ALLE
                for n in sorted(meine):
                    # #361: gewinnt die Gruppe, haelt die Gefahr am Platz des Einzelnen ihn nicht auf - alle gehen zusammen
                    self.weg.fuehre(n, "einheit", k, "vorstoss", trotz=darf == "sieg")
                self.vor_ort = None
                if self.gefuehrt != k:
                    self.gefuehrt = k
                    self.befehle["schuss"] += 1
                    aus.append(
                        "VORSTOSS: %d Schuetzen %s Typ %d in %d Feldern"
                        % (
                            len(meine),
                            "ziehen zu" if fern is not None else "schiessen auf",
                            L[k]["typ"],
                            d,
                        )
                    )
                return aus
            if self._sende("schuss", k, befehl, meine, {"ziel": k}):
                aus.append(
                    "VORSTOSS: %d Schuetzen schiessen auf Typ %d in %d Feldern"
                    % (len(meine), L[k]["typ"], d)
                )
            return aus
        # B-182 (Logbuch, Partie 12.11. 20:53, Takt 2.566): der Vorstoss meldete "wartet, kein Ziel", die Wegfuehrung fuehrte seine
        # Schuetzen weiter zum alten Ziel U322 (path_target, 45 Zeilen). Waehlt er kein Ziel, nimmt er das alte zurueck
        if self.gefuehrt is not None:
            self._loslassen(meine)
        stand, ziel = self._stellung(L, G, mitte, len(meine))
        if stand is None or schach(mitte, stand) == 0:
            self._melde(
                meine,
                Action.WAIT_STAGING,
                point(mitte),
                "no_safe_firing_position" if stand is None else "at_firing_position_no_target",
            )
            self._sammeln(L, meine, mitte, aus)
            return aus
        stelle = self._weitester_sicherer(mitte, stand, L, G, len(meine))
        if not self._sicher(stelle, L, G, len(meine)):
            self._melde(
                meine, Action.WAIT_STAGING, point(mitte), "advance_unsafe", to=point(stelle)
            )
            self._sammeln(L, meine, mitte, aus)
            return aus
        if self.weg is not None:
            # B-182 (Daniel 11.11. 20:30 auf die Frage "Als Naechstes Waechter und Vorstoss-Vorruecken umziehen?": "ja gerne"): das Vorruecken
            # fuehrt die Wegfuehrung - jeder Schuetze auf sicherem Weg (Schusslinie) zur Stelle. Meldet sie fuer alle "gefahr" oder
            # "kein_weg", ist die Stelle nach ihrer Regel nicht sicher: SPERRE_RUNDEN Runden kein Vorruecken
            st = {self.weg.status(n) for n in meine if self.weg.fuehrt(n)}
            if self.vor_ort is not None and st and st <= {"gefahr", "kein_weg"}:
                # Daniel 16.11.2026 00:21 ("bogenschuetzen warten immer noch ewig ... die sollten gefaelligst sofort rauskommen"): Probe 5 -
                # nach "gefahr" warteten sie SPERRE_RUNDEN (10) Runden, Takt 1.450 bis 2.886. Jetzt kein Warten: das naechste Vorruecken geht
                # hoechstens halb so weit, bis die Wegfuehrung es annimmt
                weit = schach(mitte, self.vor_ort)
                self.vor_max = max(SCHRITT, weit // 2)
                self._loslassen(meine)
                aus.append(
                    "VORSTOSS: Vorruecken bis %s nicht sicher (%s) - sofort hoechstens %d Felder"
                    % (self.vor_ort, "/".join(sorted(st)), self.vor_max)
                )
                self.vor_ort = None
                stelle = self._weitester_sicherer(mitte, stand, L, G, len(meine))
            if self.vor_bis > self.runde:
                self._melde(
                    meine,
                    Action.WAIT_STAGING,
                    point(mitte),
                    "advance_paused",
                    rounds_left=self.vor_bis - self.runde,
                )
                self._sammeln(L, meine, mitte, aus)
                return aus
            self._frei(meine)
            self.gefuehrt = None
            if self.vor_ort is None or _grob(self.vor_ort) != _grob(stelle):
                self.vor_ort = stelle
                self.befehle["vor"] += 1
                aus.append("VORSTOSS: rueckt vor %s -> %s, Ziel %s" % (mitte, stelle, ziel))
            for n in sorted(meine):
                # #361 (Daniel 16.11.2026 00:21 "splitten sich dann auf und kommen somit erst viel spaeter an"): ob die Stelle sicher ist,
                # hat die Gruppenregel (_sicher an jedem Zwischenpunkt, mit Gefechtsrechnung) entschieden - die Wegfuehrung haelt keinen
                # Einzelnen mehr an, weil ihn dort ein Feind treffen koennte
                self.weg.fuehre(n, "ort", self.vor_ort, "vorstoss", trotz=True)
            self._melde(
                meine,
                Action.MOVE_TO_STAGING,
                point(self.vor_ort),
                "advance_toward_target",
                toward=point(ziel),
            )
            return aus
        self._melde(
            meine,
            Action.MOVE_TO_STAGING,
            point(stelle),
            "advance_toward_target",
            toward=point(ziel),
        )
        if self._sende("vor", stelle, befehl, meine, {"lauf": [stelle[0], stelle[1]]}):
            aus.append("VORSTOSS: rueckt vor %s -> %s, Ziel %s" % (mitte, stelle, ziel))
        return aus

    def plaetze_setzen(self, belegt):
        """Der Lenker sagt je Runde, wie viele Einzelbefehle je Feld der Brandtrupp braucht. Der geht vor: Seine Sklaven laufen wirklich
        durchs Feuer, die Schuetzen bleiben in Schussweite stehen."""
        self.plaetze = max(0, TRUPPS - belegt)

    def bericht(self):
        kern = "; " + self.kern.bericht() if self.kern is not None else ""
        return "Vorstoss: Befehle %s%s" % (dict(self.befehle), kern)
