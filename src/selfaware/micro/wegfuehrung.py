# -*- coding: utf-8 -*-
"""B-182 Wegfuehrung fuer alle Einheiten (Plan: docs/plans/Plan_Wegfuehrung.md).

Daniel 11.11.2026 auf den Vorschlag einer gemeinsamen Wegfuehrung fuer jede Einheit, die wir bewegen: "Ja, so bauen"; dazu "er sollte
immer adjustieren sollte im lauf eine gefahr in den weg kommen ... es sollte nicht einfach nur mit einem befehl im stich gelassen
werden"; Gefahr ist alles Sichtbare - Einheiten, Arbeiter, Tuerme, Gelaende -, nicht die verborgenen Holzfallen und das Pech
(FAIRNESS F12).

Die Module sagen, WAS sie wollen (fuehre: eine Einheit, ein Gebaeude oder einen Ort), die Wegfuehrung, WIE die Einheit hinkommt.
Jede Runde, gegen die aktuelle Lage:
  - Gefahr (Klasse Gefahr; Plan Nachtrag 11.11. 20:45, Daniel 20:30: "toter winkel hat JEDE einheit"): gegnerische Schuetzen in
    Reichweite (schussfeld.REICHWEITE) mit freier Linie - ein nicht flaches Gebaeude dazwischen sperrt (L79), wer auf Turm, Torhaus
    oder Bergfried steht, schiesst frei; eine Assassine nur, wenn sie sichtbar waere (L75, sicht.py); Nahkaempfer bis
    raids.GEFAHR_NAH. Tuerme selbst zaehlen nicht, die Schuetzen darauf schon. Dieselbe Regel gilt fuer Standplatz und Wegegitter.
    Nicht drin: Mauern (die Karte ist vom Partiebeginn), Gelaendehoehe, Belagerungsgeraete (in keiner Reichweitentabelle).
  - Standplatz: Fernkaempfer in Reichweite minus FERN_STAND vor dem Ziel, Nahkaempfer und Gebaeudeangriffe am Ziel. Liegt er in Gefahr,
    sucht die Wegfuehrung auf dem Kreis um das Ziel den sichersten; bleibt Gefahr, meldet sie "gefahr" und gibt keinen Befehl - das Modul
    waehlt ein anderes Ziel.
  - Weg: sicherer Weg (Dijkstra, Gefahr teuer). Neu geplant wird, sobald auf dem restlichen Weg mehr Gefahr liegt als beim Planen, das
    Ziel weitergezogen ist oder NEU_PLANEN Runden vergangen sind.
  - Befehl: in Reichweite der Angriff, sonst ein Laufbefehl zum naechsten Wegpunkt; hoechstens BUDGET Befehle je Runde (S82), ein
    Befehl geht nur bei Aenderung oder nach NEU_ALLE Runden noch einmal hinaus. Gleiche Befehle mehrerer Einheiten (selbes Ziel, selber
    Wegpunkt) gehen als EIN Befehl hinaus, wie der Vorstoss sie immer schickte - ob er so schnell ankommt wie ein Einzelbefehl, ist
    ungemessen.
  - Begehbar ist, was die Weg-Ebene des Spiels erlaubt (services/wegkarte.als_gelaende, der Lenker liest sie neu alle
    KARTE_RUNDEN Runden; Partie 11.11. 22:37, Daniel 22:41: "warum wird denn der soeldnerposten als unbegehbar gegolten? macht doch keinen sinn offensichtlich sammeln die sich dort ja") - die
    Startkarte zaehlte jedes Gebaeudefeld als Wand, auch den Hof des Soeldnerpostens. Findet unser Gitter trotzdem keinen Weg oder
    steckt die Einheit, fuehrt die Wegsuche des Spiels sie, bis sie DIREKT_BIS Felder weiter ist (sie kennt keine Gefahr);
    "kein_weg" heisst: auch so bewegt sie sich STECKT_RUNDEN Runden nicht.
Startwerte, nicht gemessen: FERN_ANGRIFF, FERN_STAND, NEU_PLANEN, ZIEL_WANDERT, STECKT_RUNDEN, DIREKT_BIS (Plan_Wegfuehrung.md,
Sandkasten misst sie).
"""

import functools
import math

import selfaware.services.schussfeld as SF
import selfaware.services.sicht as SI
import selfaware.services.spielwerte as SW

NAH_AM_ZIEL = 4  # Felder (Schach): Nahkampf und Gebaeude gelten als am Ziel (wie Brandtrupp und Nahkampf-Raid)
FERN_ANGRIFF = 2  # Startwert: Fernkaempfer greifen an, wenn die Luftlinie hoechstens Reichweite minus FERN_ANGRIFF ist
FERN_STAND = 4  # Startwert: Standplatz in Reichweite minus FERN_STAND vor dem Ziel
AM_WEGPUNKT = 3  # Felder: dann gilt der naechste Wegpunkt (wie Nahkampf-Raid)
# B-182 (Daniel 11.11. 23:28: "warum so viele befehle zur wegfindung kommen die eine einheit unnötig
# aufhalten und deine gleichzeitigkeit unnötig einschränken"): gemessen in der Partie 23:25 gingen in keinem 45-Takt-Fenster 8 oder
# mehr Befehle hinaus (hoechstens 5) - die 8 aus S82 galten dem Zickzack (8 in 12 Takten). Die Schlange des Spiels setzt einen
# Angriffsbefehl je Takt ab (logik.lua angriffSchlange, abgelesen); eine Runde sind etwa 45 Takte. Startwert, nicht gemessen:
BUDGET = 20  # Einzelbefehle je Runde
NEU_ALLE = 6  # gleicher Befehl hoechstens alle NEU_ALLE Runden noch einmal
NEU_PLANEN = 10  # Startwert: spaetestens nach so vielen Runden neu planen
ZIEL_WANDERT = 8  # Startwert: Felder, ab denen ein gewandertes Ziel neu geplant wird
# Standplaetze auf dem Kreis um das Ziel, in festen Richtungen (B-182, Partie 11.11. 23:53: gedreht nach der Seite der Einheit sah die
# Frage aus der Gruppenmitte einen sicheren Punkt, den kein einzelner Schuetze je pruefte - der Vorstoss waehlte das Ziel, die
# Wegfuehrung meldete fuer alle "gefahr"). Startwert, nicht gemessen:
RICHTUNGEN = 32
ASSASSINE = 73  # getarnt: Schuetzen nehmen sie nur, wenn sie sichtbar ist (L75)
# S155 (Daniel 15.11.2026 00:04 "eine einheit geht nicht einfach weiter, sie braucht noch weitere laufbefehle um durchzuspammen", 00:20
# "Ja, Kern bauen"): die Befehle dieser Zwecke gehen ueber den Kern, wenn er bereit ist (Wegfuehrung.kern) - einen Laufbefehl wiederholt er
# jeden Takt, solange die Einheit gegen einen anderen als ihr Ziel kaempft
KERN_ZWECKE = frozenset({"nahkampfraid"})
STECKT_RUNDEN = 3  # Startwert: so viele Runden auf demselben Feld trotz Laufbefehl - der Wegpunkt gilt als nicht erreichbar
DIREKT_BIS = 12  # Startwert: Felder (Schach) vom Ort der Uebergabe, ab denen die Wegfuehrung wieder selbst fuehrt
FREI_SUCHE = (
    8  # Startwert: Felder, in denen ein Laufpunkt auf das naechste begehbare Feld der Karte rueckt
)
# B-182 (Partie 11.11. 23:25: Sklaven standen 12 % ihrer Zeit an einem erreichten Wegpunkt und warteten auf den naechsten Befehl):
# der naechste Wegpunkt geht hinaus, solange die Einheit noch VORLAUF_RUNDEN Runden ihres eigenen Laufs (gemessen an der Vorrunde)
# vor dem alten ist. Startwerte, nicht gemessen:
VORLAUF_RUNDEN = 2
VORLAUF_MAX = 16  # Felder


def _luft(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class _Sicht(SI.Lage):
    """sicht.Lage ohne den Nachbau der Zielwahl - die Wegfuehrung braucht nur Gebaeude, Schuetzen und Sichtbarkeit."""

    def zuteilen(self):
        self.feuer, self.bestwert = {}, []


class Gefahr:
    """Eine Runde: was eine eigene Einheit an einem Ort treffen kann (alles Sichtbare; keine Fallgruben, kein Pech - F12)."""

    def __init__(self, L, G, sp):
        # hier importiert, damit raids die Wegfuehrung selbst nutzen kann
        from selfaware.micro.tasks import raids as RA

        self.lage = _Sicht(L, G or {}, sp)
        self.schuetzen = []  # (Ort, Reichweite, erhoeht, Nr des Gebaeudes unter ihm)
        for i, (ort, _r, erhoeht, steht, _art) in enumerate(self.lage.schuetzen):
            r = SF.REICHWEITE.get((L.get(self.lage.schuetzen_nr[i]) or {}).get("typ"))
            if r:
                self.schuetzen.append((ort, r, erhoeht, steht))
        self.nah = [
            (e["x"], e["y"])
            for e in L.values()
            if e.get("besitzer") not in (0, sp) and e.get("typ") in RA.NAH and e.get("leben", 1) > 0
        ]
        self.nah_r = RA.GEFAHR_NAH
        self._linie, self._sicht = {}, {}

    def _frei(self, s, steht, ziel, ausser):
        """Linie frei: kein nicht flaches Gebaeude zwischen s und ziel, ausser dem unter dem Schuetzen und dem Ziel selbst (L79)."""
        schl = (s, steht, ziel, ausser)
        frei = self._linie.get(schl)
        if frei is None:
            frei = True
            geb = self.lage.gebaeude
            for f in SI.linie(s, ziel):
                b = geb.get(f)
                if b and b[1] not in SI.FLACH and b[0] != steht and b[0] != ausser:
                    frei = False
                    break
            self._linie[schl] = frei
        return frei

    def _sichtbar(self, p):
        s = self._sicht.get(p)
        if s is None:
            s = self._sicht[p] = self.lage.sichtbar(p, self.lage.RAND)
        return s

    def an(self, ort, typ=None, ausser_ort=None, ausser_gebaeude=None):
        """Zahl der Gefahren, die ort erreichen. ausser_ort: was dort steht, zaehlt nicht (das Ziel eines Nahkaempfers);
        ausser_gebaeude: dieses Gebaeude sperrt keine Linie (das Ziel selbst, an dem die Einheit steht)."""
        p = (int(round(ort[0])), int(round(ort[1])))
        rn2 = self.nah_r * self.nah_r
        n = sum(1 for q in self.nah if q != ausser_ort and SF.luftlinie2(q, p) <= rn2)
        if typ == ASSASSINE and not self._sichtbar(p):
            return n
        for s, r, erhoeht, steht in self.schuetzen:
            if s == ausser_ort or SF.luftlinie2(s, p) > r * r:
                continue
            if erhoeht or self._frei(s, steht, p, ausser_gebaeude):
                n += 1
        return n

    def gitter(self, gelaende, frei=None, typ=None):
        """Wegegitter mit Gefahr je Zelle (Zellmitte) nach derselben Regel - gerechnet nur fuer Zellen in Reichweite einer Gefahr."""
        g = SF.Gitter(gelaende, [], frei=frei)
        zellen = set()
        for (px, py), r in [(s, r) for s, r, _e, _st in self.schuetzen] + [
            (q, self.nah_r) for q in self.nah
        ]:
            ri = int(math.ceil(r))
            for cy in range(max(0, (py - ri) // g.z), min(g.n - 1, (py + ri) // g.z) + 1):
                for cx in range(max(0, (px - ri) // g.z), min(g.n - 1, (px + ri) // g.z) + 1):
                    zellen.add((cx, cy))
        for cx, cy in zellen:
            g.gefahr[cy][cx] = self.an(g.mitte((cx, cy)), typ)
        return g


class Auftrag:
    def __init__(self, art, ziel, zweck):
        self.art, self.ziel, self.zweck = art, ziel, zweck
        self.kennung = None  # (Art, Besitzer) des Ziels beim ersten Sehen - das Spiel vergibt Nummern Toter neu
        self.weg = []  # offene Wegpunkte
        self.zellen = []  # geplante Zellen (fuer die Gefahrenpruefung je Runde)
        self.plan_gefahr = []  # Gefahr je Zelle beim Planen
        self.geplant = (None, -(10**6))  # (Standplatz, Runde)
        self.letzter = None  # (Ort, Wegpunkt) der Vorrunde - fuer die Erkennung "steckt fest"
        self.steht = 0  # Runden auf demselben Feld mit demselben Wegpunkt
        self.direkt = False  # die Wegsuche des Spiels uebernimmt (unser Gitter fand keinen Weg oder die Einheit steckte)
        self.direkt_ab = (
            None  # Ort der Uebergabe - DIREKT_BIS Felder weiter fuehrt wieder die Wegfuehrung
        )
        self.vorher = (
            None  # Ort der Einheit in der Vorrunde (ihr eigenes Lauftempo, und ob sie steht)
        )
        self.art_eigen = None  # Art der gefuehrten Einheit beim ersten Schritt - das Spiel vergibt Nummern Toter neu
        self.status = "neu"


class Wegfuehrung:
    def __init__(self, sp, gelaende=None, trotz_gefahr=()):
        """trotz_gefahr: Zwecke, die auch in Gefahr angreifen duerfen - nur auf Daniels Freigabe (seit 11.11. 19:40 der
        Nahkampf-Raid, baukasten/raid.TROTZ_GEFAHR)."""
        self.sp, self.gelaende, self.trotz_gefahr = sp, gelaende, frozenset(trotz_gefahr)
        self.auftraege = {}
        self.befohlen = {}  # Einheit -> (Befehl, Runde)
        self.runde = 0
        self._frei = None  # Begehbarkeit des Gelaendes, einmal berechnet
        self._frage = None  # (Runde, Lage) -> Gefahr fuer Fragen von aussen (schuss_moeglich)
        self._ketten = {}  # S159: Einheit -> (weitere Wegpunkte, Angriff am Ende) dieser Runde, fuer den Kern
        self.kern = None  # S155: Kernweg (execution/kernweg.py) fuer die Befehle der KERN_ZWECKE; None = alles ueber das Modul

    def raster(self, L, G, typ):
        """B-182 S150: das Gitter mit der Gefahr dieser Lage, wie schritt es fuer diese Art baut (gemessen 14.11.2026 23:39 auf der
        Lage von Partie 21: 0,026 s) - fuer Fragen von aussen; der Raid baut es einmal je Runde fuer alle seine Einheiten."""
        return self._gitter(Gefahr(L, G, self.sp), ASSASSINE if typ == ASSASSINE else None)

    @staticmethod
    def weglaenge(g, ort):
        """B-182 S150 (Daniel 14.11.2026 23:29 "Niemals nach luftlinie"): -> Funktion Zielort -> Felder auf dem sicheren Weg von ort
        im Gitter g (derselbe guenstigste Weg wie in schritt: Zellenschritte x Zellengroesse, in Start- und Nachbarzelle die
        Schachdistanz), None ohne Weg."""
        schritte = g.laengen(ort)

        def laenge(ziel):
            k = schritte.get(g.zelle_von(ziel))
            if k is None:
                return None
            return SF.schach(ort, ziel) if k <= 1 else k * g.z

        return laenge

    def fuehre(self, nr, art, ziel, zweck=""):
        """art: "einheit" (ziel = Nummer), "gebaeude" (ziel = Nummer) oder "ort" (ziel = (x, y))."""
        alt = self.auftraege.get(nr)
        # "ziel_weg": die Nummer traegt inzwischen eine andere Einheit - fuehrt das Modul sie trotzdem, gilt die neue
        if alt is None or (alt.art, alt.ziel) != (art, ziel) or alt.status == "ziel_weg":
            self.auftraege[nr] = Auftrag(art, ziel, zweck)

    def schuss_moeglich(self, typ, von, ziel_ort, L, G, zweck=""):
        """B-182 (Partie 11.11. 23:53): Faende die Wegfuehrung fuer einen Fernkaempfer dieser Art einen Standplatz in Reichweite von
        ziel_ort, an dem ihn niemand trifft - oder darf der Zweck trotz Gefahr? Fuer den Kauf nach Wirkung (raid.RaidEinsatz.greift_an):
        er kaufte 4 Arabische Bogenschuetzen (240 Gold), waehrend der Vorstoss mit 9 Schuetzen stillstand, weil an jeder Stellung 1-2
        feindliche Armbrustschuetzen hinreichten."""
        r = SW.erfassen(typ)
        if r is None:
            return True
        schl = (self.runde, id(L), id(G))
        if self._frage is None or self._frage[0] != schl:
            self._frage = (schl, Gefahr(L, G, self.sp))
        _stand, gefahr = self._standplatz(
            von, ziel_ort, r, functools.partial(self._frage[1].an, typ=typ)
        )
        return not gefahr or zweck in self.trotz_gefahr

    def karte(self, gelaende):
        """Neue Begehbarkeit (Weg-Ebene des Spiels, services/wegkarte.als_gelaende): das Gitter wird neu gerechnet, und wen gerade
        die Wegsuche des Spiels fuehrt, den plant die Wegfuehrung mit der neuen Karte wieder selbst."""
        self.gelaende, self._frei = gelaende, None
        for a in self.auftraege.values():
            if a.direkt:
                a.direkt, a.weg, a.steht, a.letzter = False, [], 0, None

    def _begehbar_nah(self, p):
        """Das naechste Feld, das die Karte begehbar nennt (Ring um Ring bis FREI_SUCHE); ohne Karte oder ohne freies Feld p selbst.
        B-182 (Partie 11.11. 23:12, Fehlerwache F2): die Vorrueck-Stelle (168, 234) lag auf einem eigenen Apfelhof - das Spiel nahm
        den Laufbefehl an, und keiner der drei Schuetzen ging los. Auf ein Gebaeudefeld kann niemand laufen."""
        x, y = int(p[0]), int(p[1])
        gel = self.gelaende
        if not gel:
            return (x, y)

        def frei(q):
            return (
                0 <= q[1] < len(gel)
                and 0 <= q[0] < len(gel[q[1]])
                and gel[q[1]][q[0]] in SF.BEGEHBAR
            )

        if frei((x, y)):
            return (x, y)
        for d in range(1, FREI_SUCHE + 1):
            ring = [(x + dx, y + dy) for dx in range(-d, d + 1) for dy in (-d, d)]
            ring += [(x + dx, y + dy) for dx in (-d, d) for dy in range(-d + 1, d)]
            gut = [q for q in ring if frei(q)]
            if gut:
                return min(gut, key=lambda q: (_luft(q, (x, y)), q))
        return (x, y)

    @staticmethod
    def _linie(g, von, nach, frei):
        """Die gerade Linie (Zellen ohne Start und Ende) hat keine Gefahr - und mit frei=True auch nur begehbare Zellen und keinen
        schraegen Schritt zwischen zwei gesperrten (dieselbe Regel wie Gitter.weg)."""
        zellen = g.gerade(von, nach)
        for k in range(1, len(zellen) - 1):
            c, p = zellen[k], zellen[k - 1]
            if g.schaden_je_tick(c) > 0:
                return False
            if frei and (
                not g.frei[c[1]][c[0]]
                or (
                    c[0] != p[0] and c[1] != p[1] and not (g.frei[p[1]][c[0]] or g.frei[c[1]][p[0]])
                )
            ):
                return False
        return True

    def _kette_punkte(self, g, weg):
        """S159: die Wegpunkte nach dem ersten, die der Lenker selbst befehlen wuerde - wie _naechster springt die Kette zum weitesten
        Punkt, zu dem die gerade Linie frei und ohne Gefahr ist (jeder Laufbefehl kostet eine laufende Einheit Zeit: 15,9 statt 9,5 Takte
        je Feld, S151). Der letzte Punkt ist der Standplatz am Ziel."""
        aus, jetzt, rest = [], weg[0], list(weg[1:])
        while rest:
            i = 0
            while i + 1 < len(rest) and self._linie(g, jetzt, rest[i + 1], True):
                i += 1
            jetzt = rest[i]
            aus.append(self._begehbar_nah(jetzt))
            rest = rest[i + 1 :]
        return aus

    def _naechster(self, a, g, ort, weit):
        """B-182 (Daniel 11.11. 23:28: "warum so viele befehle zur wegfindung kommen die eine einheit unnötig aufhalten"): ein Wegpunkt
        faellt weg, wenn er erreicht ist, wenn die gerade Linie zum naechsten frei und ohne Gefahr ist (dann braucht es ihn nicht), oder
        wenn die Einheit ihn in VORLAUF_RUNDEN Runden ihres Laufs (weit = Felder seit der Vorrunde) erreicht und die Linie zum
        naechsten ohne Gefahr ist - um ein Hindernis findet das Spiel selbst, so steht sie nie an einem Wegpunkt."""
        vorlauf = min(VORLAUF_MAX, max(AM_WEGPUNKT, VORLAUF_RUNDEN * weit))
        while len(a.weg) > 1 and (
            SF.schach(ort, a.weg[0]) <= AM_WEGPUNKT
            or self._linie(g, ort, a.weg[1], True)
            or (SF.schach(ort, a.weg[0]) <= vorlauf and self._linie(g, ort, a.weg[1], False))
        ):
            a.weg.pop(0)

    def _lauf(self, nr, p):
        q = self._begehbar_nah(p)
        return {"angriff": {"einheiten": [nr], "lauf": [q[0], q[1]]}}

    def loslassen(self, nr):
        self.auftraege.pop(nr, None)
        self.befohlen.pop(nr, None)
        if self.kern is not None and nr in self.kern.uebergeben:
            self.kern.freigeben(
                [nr]
            )  # S155: fuehrt sie jetzt jemand anderes, wiederholt der Kern fuer sie nichts mehr

    def _kette_aktiv(self, nr):
        """S159: fuehrt der Kern die Wegpunktkette dieser Einheit?"""
        return self.kern_fuehrt(nr) and getattr(self.kern, "kann_ketten", False)

    def kern_fuehrt(self, nr):
        """S155: Gehen die Befehle dieser Einheit ueber den Kern, der einen Laufbefehl im Kampf selbst wiederholt?"""
        a = self.auftraege.get(nr)
        return self.kern is not None and a is not None and a.zweck in KERN_ZWECKE

    def _ueber_kern(self, c, liste, befehl):
        """S155: Der Befehl c ({"angriff": ...}-Inhalt) geht ueber den Kern - ein Laufbefehl als durchzusetzender, das Ziel der Einheit als
        erlaubter Gegner. Was der Kern nicht nimmt (Ring voll), geht ans Modul."""
        for nr, _b in liste:
            a = self.auftraege[nr]
            self.kern.erlauben(nr, a.ziel if a.art == "einheit" else 0)
        if "lauf" in c:
            c = dict(c, durchsetzen=True)
        rest = self.kern.senden([{"angriff": c}])
        for r in rest:
            befehl(
                {"angriff": {k: v for k, v in r["angriff"].items() if k != "durchsetzen"}},
                1.0,
                bis="ANGRIFF",
            )
        if "lauf" in c and not rest:
            for (
                nr,
                _b,
            ) in (
                liste
            ):  # S159: der Rest des Wegs und der Angriff am Ende - der Kern gibt sie im Takt
                if nr in self._ketten:
                    self.kern.kette(nr, *self._ketten[nr])

    def fuehrt(self, nr):
        return nr in self.auftraege

    def status(self, nr):
        a = self.auftraege.get(nr)
        return a.status if a else None

    def absichten(self):
        """B-182 Logbuch je Einheit (docs/plans/Plan_Unit_Status_Log.md): {Einheit: (Zweck, Status, Ziel als Text, naechster Wegpunkt
        oder None)} fuer jede gefuehrte Einheit - nach schritt aufrufen, dann ist der Status der dieser Runde."""
        from selfaware.micro import unit_log as UL

        aus = {}
        for nr, a in self.auftraege.items():
            ziel = (
                UL.unit(a.ziel)
                if a.art == "einheit"
                else UL.building(a.ziel)
                if a.art == "gebaeude"
                else UL.point(a.ziel)
            )
            aus[nr] = (a.zweck or "wegfuehrung", a.status, ziel, tuple(a.weg[0]) if a.weg else None)
        return aus

    def _gitter(self, bild, typ):
        g = bild.gitter(self.gelaende, self._frei, typ)
        if self._frei is None:
            self._frei = g.frei
        return g

    def _zielort(self, a, L, G):
        if a.art == "ort":
            return tuple(a.ziel)
        tabelle = L if a.art == "einheit" else G
        z = tabelle.get(a.ziel)
        if z is None or z.get("besitzer") in (0, self.sp) or z.get("leben", 1) <= 0:
            return None
        kennung = (z.get("typ"), z.get("besitzer"))
        if a.kennung is None:
            a.kennung = kennung
        elif a.kennung != kennung:
            return None  # die Nummer traegt eine andere Einheit: das alte Ziel ist tot
        return (z["x"], z["y"])

    def _standplatz(self, ort, zielort, r, gefahr_an):
        """Standplatz und seine Gefahr: Fernkaempfer auf dem Kreis um das Ziel - fuer jede Einheit dieselben RICHTUNGEN Punkte, jeder
        aufs naechste begehbare Feld gerueckt und nur, solange er in Schussweite bleibt; der sicherste, bei Gleichstand der naechste zur
        Einheit. Nahkampf und Gebaeude: das Ziel selbst."""
        if r is None:
            return zielort, gefahr_an(zielort)
        rad = max(1.0, r - FERN_STAND)
        best = None
        for i in range(RICHTUNGEN):
            w = 2 * math.pi * i / RICHTUNGEN
            p = self._begehbar_nah(
                (
                    int(round(zielort[0] + rad * math.cos(w))),
                    int(round(zielort[1] + rad * math.sin(w))),
                )
            )
            if _luft(p, zielort) > r - FERN_ANGRIFF:
                continue
            k = (gefahr_an(p), _luft(ort, p), p)
            if best is None or k < best:
                best = k
        if (
            best is None
        ):  # kein begehbarer Punkt in Schussweite: der Punkt zur Einheit hin, wie er ist
            d = max(1.0, _luft(ort, zielort))
            p = (
                int(round(zielort[0] + (ort[0] - zielort[0]) * rad / d)),
                int(round(zielort[1] + (ort[1] - zielort[1]) * rad / d)),
            )
            return p, gefahr_an(p)
        return best[2], best[0]

    def schritt(self, L, G, befehl):
        """Eine Runde fuer alle gefuehrten Einheiten; gibt {Einheit: Status} (unterwegs, greift_an, am_ziel, gefahr, ziel_weg,
        steckt, direkt, kein_weg, wartet, weg)."""
        self.runde += 1
        self._ketten = {}
        bild = Gefahr(L, G, self.sp)
        gitter = {}  # je Runde ein Gitter fuer Getarnte (Assassinen) und eines fuer alle anderen
        befehle = []
        bewegt = {}  # Einheit -> hat sich seit der Vorrunde bewegt
        for nr, a in list(self.auftraege.items()):
            e = L.get(nr)
            if e is None or e.get("besitzer") != self.sp or e.get("leben", 1) <= 0:
                a.status = "weg"
                self.loslassen(nr)
                continue
            # B-182 (Logbuch, Partie 12.11. 20:53, Takt 24.021): Schuetze 582 (A_ARCHER 70) starb, das Spiel gab seine Nummer einer
            # eigenen Einheit vom Typ 52, und die Wegfuehrung fuehrte sie weiter als Vorstoss-Schuetzen. Ein Auftrag gilt der Einheit,
            # fuer die er gegeben wurde: traegt die Nummer eine andere Art, endet er (beim Anwerben wechselt die Art bei gleicher Nummer)
            if a.art_eigen is None:
                a.art_eigen = e.get("typ")
            elif e.get("typ") != a.art_eigen:
                a.status = "weg"
                self.loslassen(nr)
                continue
            ort = (e["x"], e["y"])
            weit = (
                SF.schach(ort, a.vorher) if a.vorher is not None else 0
            )  # Felder seit der Vorrunde
            bewegt[nr] = weit > 0
            a.vorher = ort
            zielort = self._zielort(a, L, G)
            if zielort is None:
                a.status = "ziel_weg"
                continue
            if a.art == "ort":
                zielort = self._begehbar_nah(
                    zielort
                )  # B-182: ein Ort, den es zu Fuss nicht gibt, rueckt aufs naechste freie Feld
            typ = e["typ"]
            r = SW.erfassen(typ) if a.art == "einheit" else None
            # in Reichweite: angreifen
            if a.art != "ort" and (
                (r is not None and _luft(ort, zielort) <= r - FERN_ANGRIFF)
                or (r is None and SF.schach(ort, zielort) <= NAH_AM_ZIEL)
            ):
                a.status = "greift_an"
                schluessel = "ziel" if a.art == "einheit" else "gebaeude"
                befehle.append(
                    (bild.an(ort, typ), nr, {"angriff": {"einheiten": [nr], schluessel: a.ziel}})
                )
                continue
            if a.art == "ort" and SF.schach(ort, zielort) <= AM_WEGPUNKT:
                a.status = "am_ziel"
                continue
            # Nahkaempfer muessen an ihr Ziel heran - seine eigene Gefahr zaehlt fuer sie nicht, ein Gebaeude als Ziel sperrt keine
            # Linie zu sich selbst. Fernkaempfer halten Abstand: gegen einen Schleuderer (22) geht der Standplatz in 36 Feldern, gegen
            # einen Bogenschuetzen (44) nur, wo ein Gebaeude seine Linie sperrt
            gefahr_an = functools.partial(
                bild.an,
                typ=typ,
                ausser_ort=zielort if (a.art == "einheit" and r is None) else None,
                ausser_gebaeude=a.ziel if a.art == "gebaeude" else None,
            )
            stand, gefahr_stand = (
                self._standplatz(ort, zielort, r, gefahr_an)
                if a.art != "ort"
                else (zielort, gefahr_an(zielort))
            )
            if r is not None:
                stand = self._begehbar_nah(
                    stand
                )  # B-182: der Standplatz eines Fernkaempfers muss begehbar sein
                gefahr_stand = gefahr_an(stand)
            if gefahr_stand and a.zweck not in self.trotz_gefahr:
                a.status = "gefahr"
                continue
            # B-182 (Partie 11.11. 22:37): die Wegsuche des Spiels kennt keine Gefahr - Sklave 404 lief mit ihr geradeaus bis zu einem
            # Typ 23 und einem Schleuderer (A_SLINGER 72) und starb. Sie fuehrt deshalb nur aus der Stelle heraus, an der unsere
            # Karte irrte: DIREKT_BIS Felder weiter plant die Wegfuehrung wieder selbst.
            if a.direkt and SF.schach(ort, a.direkt_ab) > DIREKT_BIS:
                a.direkt, a.weg, a.steht, a.letzter = False, [], 0, None
            if not a.direkt:
                klasse = ASSASSINE if typ == ASSASSINE else None
                if klasse not in gitter:
                    gitter[klasse] = self._gitter(bild, klasse)
                g = gitter[klasse]
                # neu planen: neuer Standplatz, gewandertes Ziel, mehr Gefahr auf dem restlichen Weg als beim Planen, oder zu alt
                alt_stand, alt_runde = a.geplant
                neue_gefahr = False
                if a.zellen:
                    hier = g.zelle_von(ort)
                    i = min(range(len(a.zellen)), key=lambda k: SF.schach(a.zellen[k], hier))
                    neue_gefahr = sum(g.schaden_je_tick(c) for c in a.zellen[i:]) > sum(
                        a.plan_gefahr[i:]
                    )
                if (
                    alt_stand is None
                    or SF.schach(alt_stand, stand) > ZIEL_WANDERT
                    or neue_gefahr
                    or self.runde - alt_runde >= NEU_PLANEN
                    or not a.weg
                ):
                    zellen = g.weg(ort, stand)
                    if zellen is None:
                        # unser Gitter kennt keinen Weg: das Spiel sucht ihn, schon in DIESER Runde und als "direkt" - auf "kein_weg"
                        # gab der Brandtrupp das Ziel auf und waehlte es wieder (Partie 11.11. 22:37: Sklave 407 fuenfmal)
                        a.direkt, a.direkt_ab, a.steht, a.letzter = True, ort, 0, None
                    else:
                        a.zellen = zellen
                        a.plan_gefahr = [g.schaden_je_tick(c) for c in zellen]
                        a.weg = SF.wegpunkte(g, zellen, stand)
                        a.geplant = (stand, self.runde)
            if a.direkt:
                # steht die Einheit auch mit dem Befehl an das Spiel STECKT_RUNDEN Runden still, kennt auch das Spiel keinen Weg
                a.steht = a.steht + 1 if a.letzter == (ort, "direkt") else 0
                a.letzter = (ort, "direkt")
                if a.steht >= STECKT_RUNDEN:
                    a.status = "kein_weg"  # das Modul waehlt ein anderes Ziel
                    continue
                a.status = "direkt"
                if a.art == "gebaeude" or (a.art == "einheit" and r is None):
                    b = {
                        "angriff": {
                            "einheiten": [nr],
                            ("gebaeude" if a.art == "gebaeude" else "ziel"): a.ziel,
                        }
                    }
                else:
                    b = self._lauf(nr, stand)
                befehle.append((bild.an(ort, typ), nr, b))
                continue
            if self._kette_aktiv(nr):
                # S159: der Kern hat die Einheit vielleicht schon weitergeschickt - ihr Laufziel im Spiel zeigt, an welchem Wegpunkt
                # der Kette sie ist; der Lenker schickt sie nicht zurueck und nicht noch einmal dorthin
                lauf = (e.get("laufx", 0), e.get("laufy", 0))
                for i in range(len(a.weg)):
                    if SF.schach(lauf, self._begehbar_nah(a.weg[i])) <= AM_WEGPUNKT:
                        a.weg = a.weg[i:]
                        self.befohlen[nr] = (self._lauf(nr, a.weg[0]), self.runde)
                        break
            self._naechster(a, g, ort, weit)
            ziel_p = a.weg[0] if a.weg else stand
            # B-182 (Partie 11.11. 22:10, Fehlerwache F3): Sklave 392 bekam 2.000 Takte lang denselben Wegpunkt (142, 234), das Spiel
            # nahm den Befehl an, der Sklave ruehrte sich nicht - der Punkt war fuer ihn nicht erreichbar (die Karte ist vom
            # Partiebeginn). Steht die Einheit STECKT_RUNDEN Runden mit demselben Wegpunkt auf demselben Feld, gilt dessen Zelle
            # fuer die Partie als nicht begehbar, und der Weg wird neu geplant.
            a.steht = (
                a.steht + 1
                if a.letzter == (ort, tuple(ziel_p)) and SF.schach(ort, ziel_p) > AM_WEGPUNKT
                else 0
            )
            a.letzter = (ort, tuple(ziel_p))
            if a.steht >= STECKT_RUNDEN:
                # 22:34: keine Zellen mehr sperren - das mauerte Wege zu; das Spiel uebernimmt ab der naechsten Runde
                a.direkt, a.direkt_ab, a.steht, a.letzter = True, ort, 0, None
                a.status = "steckt"
                continue
            a.status = "unterwegs"
            if self._kette_aktiv(nr):
                self._ketten[nr] = (
                    self._kette_punkte(g, a.weg) if a.weg else [],
                    (a.art, a.ziel) if a.art in ("einheit", "gebaeude") else None,
                )
            befehle.append((bild.an(ort, typ), nr, self._lauf(nr, ziel_p)))
        # Budget: dringende zuerst (Einheit selbst in Gefahr), dann nach Nummer; nur Aenderungen - derselbe Befehl noch einmal erst nach
        # NEU_ALLE Runden und nur an eine Einheit, die steht (B-182, 23:28: jeder Befehl laesst eine laufende Einheit kurz anhalten).
        # Gleiche Befehle (selbes Ziel, selber Wegpunkt) gehen als EIN Befehl fuer alle diese Einheiten hinaus
        gruppen = {}
        for _g, nr, b in sorted(befehle, key=lambda x: (-x[0], x[1])):
            alt = self.befohlen.get(nr)
            if (
                alt is not None
                and alt[0] == b
                and (self.runde - alt[1] < NEU_ALLE or bewegt.get(nr))
            ):
                continue
            inhalt = tuple(
                sorted(
                    (k, tuple(v) if isinstance(v, list) else v)
                    for k, v in b["angriff"].items()
                    if k != "einheiten"
                )
            )
            gruppen.setdefault((self.kern_fuehrt(nr), inhalt), []).append((nr, b))
        gesendet = 0
        for (ueber_kern, _inhalt), liste in gruppen.items():
            if gesendet >= BUDGET:
                for nr, _b in liste:
                    self.auftraege[nr].status = "wartet"
                continue
            c = dict(liste[0][1]["angriff"], einheiten=sorted(nr for nr, _b in liste))
            if ueber_kern:
                self._ueber_kern(c, liste, befehl)
            else:
                if (
                    self.kern is not None
                ):  # S155: fuehrt das Modul eine Einheit, die der Kern hatte, gibt er sie vorher frei
                    self.kern.freigeben([n for n in c["einheiten"] if n in self.kern.uebergeben])
                befehl({"angriff": c}, 1.0, bis="ANGRIFF")
            for nr, b in liste:
                self.befohlen[nr] = (b, self.runde)
            gesendet += 1
        return {nr: a.status for nr, a in self.auftraege.items()}
