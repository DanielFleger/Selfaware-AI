# -*- coding: utf-8 -*-
"""B-182 Wegfuehrung fuer alle Einheiten (Plan: docs/plans/Plan_Wegfuehrung.md).

Daniel 11.11.2026: "Ja, so bauen"; "er sollte immer adjustieren sollte im lauf eine gefahr in den weg kommen ... es sollte nicht
einfach nur mit einem befehl im stich gelassen werden"; Gefahr ist alles Sichtbare - Einheiten, Arbeiter, Tuerme, Gelaende -, nicht
die verborgenen Holzfallen und das Pech (FAIRNESS F12).

Die Module sagen, WAS sie wollen (fuehre: eine Einheit, ein Gebaeude oder einen Ort), die Wegfuehrung, WIE die Einheit hinkommt.
Jede Runde, gegen die aktuelle Lage:
  - Gefahrenkarte (services/schussfeld.Gitter) aus allen sichtbaren gegnerischen Fernkaempfern (Reichweite wie schussfeld), Nahkaempfern
    (raids.GEFAHR_NAH) und Tuermen (wie ein Bogenschuetze; der Hoehenvorteil ist ungemessen).
  - Standplatz: Fernkaempfer in Reichweite minus FERN_STAND vor dem Ziel, Nahkaempfer und Gebaeudeangriffe am Ziel. Liegt er in Gefahr,
    sucht die Wegfuehrung auf dem Kreis um das Ziel den sichersten; bleibt Gefahr, meldet sie "gefahr" und gibt keinen Befehl - das Modul
    waehlt ein anderes Ziel.
  - Weg: sicherer Weg (Dijkstra, Gefahr teuer). Neu geplant wird, sobald auf dem restlichen Weg mehr Gefahr liegt als beim Planen, das
    Ziel weitergezogen ist oder NEU_PLANEN Runden vergangen sind.
  - Befehl: in Reichweite der Angriff, sonst ein Laufbefehl zum naechsten Wegpunkt; hoechstens BUDGET Einzelbefehle je Runde (S82), ein
    Befehl geht nur bei Aenderung oder nach NEU_ALLE Runden noch einmal hinaus.
Startwerte, nicht gemessen: FERN_ANGRIFF, FERN_STAND, NEU_PLANEN, ZIEL_WANDERT (Plan_Wegfuehrung.md, Sandkasten misst sie).
"""
import math

import selfaware.services.schussfeld as SF
import selfaware.services.spielwerte as SW

NAH_AM_ZIEL = 4        # Felder (Schach): Nahkampf und Gebaeude gelten als am Ziel (wie Brandtrupp und Nahkampf-Raid)
FERN_ANGRIFF = 2       # Startwert: Fernkaempfer greifen an, wenn die Luftlinie hoechstens Reichweite minus FERN_ANGRIFF ist
FERN_STAND = 4         # Startwert: Standplatz in Reichweite minus FERN_STAND vor dem Ziel
AM_WEGPUNKT = 3        # Felder: dann gilt der naechste Wegpunkt (wie Nahkampf-Raid)
BUDGET = 8             # Einzelbefehle je Runde (S82: 8 kamen alle rechtzeitig)
NEU_ALLE = 6           # gleicher Befehl hoechstens alle NEU_ALLE Runden noch einmal
NEU_PLANEN = 10        # Startwert: spaetestens nach so vielen Runden neu planen
ZIEL_WANDERT = 8       # Startwert: Felder, ab denen ein gewandertes Ziel neu geplant wird
RICHTUNGEN = 16        # Standplaetze auf dem Kreis um das Ziel


def _luft(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def gefahren(L, G, sp):
    """[(Ort, Radius)] alles Sichtbare, das eine eigene Einheit treffen kann. Keine Fallgruben, kein Pech (F12)."""
    # hier importiert, damit raids die Wegfuehrung spaeter selbst nutzen kann
    from selfaware.micro.tasks import raids as RA
    aus = list(SF.schuetzen(L, sp))
    aus += [((e["x"], e["y"]), RA.GEFAHR_NAH) for e in L.values()
            if e.get("besitzer") not in (0, sp) and e.get("typ") in RA.NAH and e.get("leben", 1) > 0]
    turm_r = max(SF.REICHWEITE.values())
    aus += [((g["x"], g["y"]), turm_r) for g in G.values() if g.get("besitzer") not in (0, sp) and g.get("typ") in RA.TUERME]
    return aus


class Auftrag:
    def __init__(self, art, ziel, zweck):
        self.art, self.ziel, self.zweck = art, ziel, zweck
        self.kennung = None      # (Art, Besitzer) des Ziels beim ersten Sehen - das Spiel vergibt Nummern Toter neu
        self.weg = []            # offene Wegpunkte
        self.zellen = []         # geplante Zellen (fuer die Gefahrenpruefung je Runde)
        self.plan_gefahr = []    # Gefahr je Zelle beim Planen
        self.geplant = (None, -10 ** 6)   # (Standplatz, Runde)
        self.status = "neu"


class Wegfuehrung:
    def __init__(self, sp, gelaende=None, trotz_gefahr=()):
        """trotz_gefahr: Zwecke, die auch in Gefahr angreifen duerfen - nur auf Daniels Freigabe (bis jetzt keiner)."""
        self.sp, self.gelaende, self.trotz_gefahr = sp, gelaende, frozenset(trotz_gefahr)
        self.auftraege = {}
        self.befohlen = {}       # Einheit -> (Befehl, Runde)
        self.runde = 0
        self._frei = None        # Begehbarkeit des Gelaendes, einmal berechnet

    def fuehre(self, nr, art, ziel, zweck=""):
        """art: "einheit" (ziel = Nummer), "gebaeude" (ziel = Nummer) oder "ort" (ziel = (x, y))."""
        alt = self.auftraege.get(nr)
        if alt is None or (alt.art, alt.ziel) != (art, ziel):
            self.auftraege[nr] = Auftrag(art, ziel, zweck)

    def loslassen(self, nr):
        self.auftraege.pop(nr, None)
        self.befohlen.pop(nr, None)

    def fuehrt(self, nr):
        return nr in self.auftraege

    def status(self, nr):
        a = self.auftraege.get(nr)
        return a.status if a else None

    def _gitter(self, gefahr):
        g = SF.Gitter(self.gelaende, gefahr, frei=self._frei)
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
            return None          # die Nummer traegt eine andere Einheit: das alte Ziel ist tot
        return (z["x"], z["y"])

    def _standplatz(self, ort, zielort, r, gefahr):
        """Standplatz und seine Gefahr: Fernkaempfer auf dem Kreis um das Ziel (zuerst die Seite der Einheit), sonst das Ziel."""
        if r is None:
            return zielort, SF.gefahr_am(zielort, gefahr)
        d = max(1.0, _luft(ort, zielort))
        rad = max(1.0, r - FERN_STAND)
        w0 = math.atan2(ort[1] - zielort[1], ort[0] - zielort[0]) if d > 0 else 0.0
        best = None
        for i in range(RICHTUNGEN):
            w = w0 + (i // 2 + 1) * (2 * math.pi / RICHTUNGEN) * (1 if i % 2 else -1) if i else w0
            p = (int(round(zielort[0] + rad * math.cos(w))), int(round(zielort[1] + rad * math.sin(w))))
            k = (SF.gefahr_am(p, gefahr), _luft(ort, p), p)
            if best is None or k < best:
                best = k
        return best[2], best[0]

    def schritt(self, L, G, befehl):
        """Eine Runde fuer alle gefuehrten Einheiten; gibt {Einheit: Status} (unterwegs, greift_an, am_ziel, gefahr, ziel_weg,
        kein_weg, wartet, weg)."""
        self.runde += 1
        gefahr = gefahren(L, G, self.sp)
        gitter = None
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
            r = SW.erfassen(e["typ"]) if a.art == "einheit" else None
            # in Reichweite: angreifen
            if a.art != "ort" and ((r is not None and _luft(ort, zielort) <= r - FERN_ANGRIFF)
                                   or (r is None and SF.schach(ort, zielort) <= NAH_AM_ZIEL)):
                a.status = "greift_an"
                schluessel = "ziel" if a.art == "einheit" else "gebaeude"
                befehle.append((SF.gefahr_am(ort, gefahr), nr, {"angriff": {"einheiten": [nr], schluessel: a.ziel}}))
                continue
            if a.art == "ort" and SF.schach(ort, zielort) <= AM_WEGPUNKT:
                a.status = "am_ziel"
                continue
            # Nahkaempfer muessen an ihr Ziel heran - seine eigene Gefahr zaehlt fuer sie nicht. Fernkaempfer dagegen halten Abstand:
            # gegen einen Schleuderer (22) geht der Standplatz in 36 Feldern, gegen einen Bogenschuetzen (44) nicht
            ohne_ziel = [x for x in gefahr if tuple(x[0]) != zielort] if (a.art == "einheit" and r is None) else gefahr
            stand, gefahr_stand = (self._standplatz(ort, zielort, r, ohne_ziel) if a.art != "ort"
                                   else (zielort, SF.gefahr_am(zielort, gefahr)))
            if gefahr_stand and a.zweck not in self.trotz_gefahr:
                a.status = "gefahr"
                continue
            if gitter is None:
                gitter = self._gitter(gefahr)
            # neu planen: neuer Standplatz, gewandertes Ziel, mehr Gefahr auf dem restlichen Weg als beim Planen, oder zu alt
            alt_stand, alt_runde = a.geplant
            neue_gefahr = False
            if a.zellen:
                hier = gitter.zelle_von(ort)
                i = min(range(len(a.zellen)), key=lambda k: SF.schach(a.zellen[k], hier))
                neue_gefahr = sum(gitter.schaden_je_tick(c) for c in a.zellen[i:]) > sum(a.plan_gefahr[i:])
            if (alt_stand is None or SF.schach(alt_stand, stand) > ZIEL_WANDERT or neue_gefahr
                    or self.runde - alt_runde >= NEU_PLANEN or not a.weg):
                zellen = gitter.weg(ort, stand)
                if zellen is None:
                    a.status = "kein_weg"
                    continue
                a.zellen = zellen
                a.plan_gefahr = [gitter.schaden_je_tick(c) for c in zellen]
                a.weg = SF.wegpunkte(gitter, zellen, stand)
                a.geplant = (stand, self.runde)
            while len(a.weg) > 1 and SF.schach(ort, a.weg[0]) <= AM_WEGPUNKT:
                a.weg.pop(0)
            ziel_p = a.weg[0] if a.weg else stand
            a.status = "unterwegs"
            befehle.append((SF.gefahr_am(ort, gefahr), nr, {"angriff": {"einheiten": [nr], "lauf": [int(ziel_p[0]), int(ziel_p[1])]}}))
        # Budget: dringende zuerst (Einheit selbst in Gefahr), dann nach Nummer; nur Aenderungen oder nach NEU_ALLE Runden
        gesendet = 0
        for _g, nr, b in sorted(befehle, key=lambda x: (-x[0], x[1])):
            alt = self.befohlen.get(nr)
            if alt is not None and alt[0] == b and self.runde - alt[1] < NEU_ALLE:
                continue
            if gesendet >= BUDGET:
                self.auftraege[nr].status = "wartet"
                continue
            befehl(b, 1.0, bis="ANGRIFF")
            self.befohlen[nr] = (b, self.runde)
            gesendet += 1
        return {nr: a.status for nr, a in self.auftraege.items()}
