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
Startwerte, nicht gemessen: FERN_ANGRIFF, FERN_STAND, NEU_PLANEN, ZIEL_WANDERT (Plan_Wegfuehrung.md, Sandkasten misst sie).
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
BUDGET = 8  # Einzelbefehle je Runde (S82: 8 kamen alle rechtzeitig)
NEU_ALLE = 6  # gleicher Befehl hoechstens alle NEU_ALLE Runden noch einmal
NEU_PLANEN = 10  # Startwert: spaetestens nach so vielen Runden neu planen
ZIEL_WANDERT = 8  # Startwert: Felder, ab denen ein gewandertes Ziel neu geplant wird
RICHTUNGEN = 16  # Standplaetze auf dem Kreis um das Ziel
ASSASSINE = 73  # getarnt: Schuetzen nehmen sie nur, wenn sie sichtbar ist (L75)
STECKT_RUNDEN = 3  # Startwert: so viele Runden auf demselben Feld trotz Laufbefehl - der Wegpunkt gilt als nicht erreichbar


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

    def fuehre(self, nr, art, ziel, zweck=""):
        """art: "einheit" (ziel = Nummer), "gebaeude" (ziel = Nummer) oder "ort" (ziel = (x, y))."""
        alt = self.auftraege.get(nr)
        # "ziel_weg": die Nummer traegt inzwischen eine andere Einheit - fuehrt das Modul sie trotzdem, gilt die neue
        if alt is None or (alt.art, alt.ziel) != (art, ziel) or alt.status == "ziel_weg":
            self.auftraege[nr] = Auftrag(art, ziel, zweck)

    def loslassen(self, nr):
        self.auftraege.pop(nr, None)
        self.befohlen.pop(nr, None)

    def fuehrt(self, nr):
        return nr in self.auftraege

    def status(self, nr):
        a = self.auftraege.get(nr)
        return a.status if a else None

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
        """Standplatz und seine Gefahr: Fernkaempfer auf dem Kreis um das Ziel (zuerst die Seite der Einheit), sonst das Ziel."""
        if r is None:
            return zielort, gefahr_an(zielort)
        d = max(1.0, _luft(ort, zielort))
        rad = max(1.0, r - FERN_STAND)
        w0 = math.atan2(ort[1] - zielort[1], ort[0] - zielort[0]) if d > 0 else 0.0
        best = None
        for i in range(RICHTUNGEN):
            w = w0 + (i // 2 + 1) * (2 * math.pi / RICHTUNGEN) * (1 if i % 2 else -1) if i else w0
            p = (
                int(round(zielort[0] + rad * math.cos(w))),
                int(round(zielort[1] + rad * math.sin(w))),
            )
            k = (gefahr_an(p), _luft(ort, p), p)
            if best is None or k < best:
                best = k
        return best[2], best[0]

    def schritt(self, L, G, befehl):
        """Eine Runde fuer alle gefuehrten Einheiten; gibt {Einheit: Status} (unterwegs, greift_an, am_ziel, gefahr, ziel_weg,
        kein_weg, wartet, weg)."""
        self.runde += 1
        bild = Gefahr(L, G, self.sp)
        gitter = {}  # je Runde ein Gitter fuer Getarnte (Assassinen) und eines fuer alle anderen
        befehle = []
        for nr, a in list(self.auftraege.items()):
            e = L.get(nr)
            if e is None or e.get("besitzer") != self.sp or e.get("leben", 1) <= 0:
                a.status = "weg"
                self.loslassen(nr)
                continue
            ort = (e["x"], e["y"])
            zielort = self._zielort(a, L, G)
            if zielort is None:
                a.status = "ziel_weg"
                continue
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
            if gefahr_stand and a.zweck not in self.trotz_gefahr:
                a.status = "gefahr"
                continue
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
                    a.status = "kein_weg"
                    continue
                a.zellen = zellen
                a.plan_gefahr = [g.schaden_je_tick(c) for c in zellen]
                a.weg = SF.wegpunkte(g, zellen, stand)
                a.geplant = (stand, self.runde)
            while len(a.weg) > 1 and SF.schach(ort, a.weg[0]) <= AM_WEGPUNKT:
                a.weg.pop(0)
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
                cx, cy = g.zelle_von(ziel_p)
                g.frei[cy][cx] = False
                a.geplant, a.steht, a.letzter = (None, -(10**6)), 0, None
                a.status = "steckt"
                continue
            a.status = "unterwegs"
            befehle.append(
                (
                    bild.an(ort, typ),
                    nr,
                    {"angriff": {"einheiten": [nr], "lauf": [int(ziel_p[0]), int(ziel_p[1])]}},
                )
            )
        # Budget: dringende zuerst (Einheit selbst in Gefahr), dann nach Nummer; nur Aenderungen oder nach NEU_ALLE Runden. Gleiche
        # Befehle (selbes Ziel, selber Wegpunkt) gehen als EIN Befehl fuer alle diese Einheiten hinaus
        gruppen = {}
        for _g, nr, b in sorted(befehle, key=lambda x: (-x[0], x[1])):
            alt = self.befohlen.get(nr)
            if alt is not None and alt[0] == b and self.runde - alt[1] < NEU_ALLE:
                continue
            inhalt = tuple(
                sorted(
                    (k, tuple(v) if isinstance(v, list) else v)
                    for k, v in b["angriff"].items()
                    if k != "einheiten"
                )
            )
            gruppen.setdefault(inhalt, []).append((nr, b))
        gesendet = 0
        for liste in gruppen.values():
            if gesendet >= BUDGET:
                for nr, _b in liste:
                    self.auftraege[nr].status = "wartet"
                continue
            befehl(
                {"angriff": dict(liste[0][1]["angriff"], einheiten=sorted(nr for nr, _b in liste))},
                1.0,
                bis="ANGRIFF",
            )
            for nr, b in liste:
                self.befohlen[nr] = (b, self.runde)
            gesendet += 1
        return {nr: a.status for nr, a in self.auftraege.items()}
