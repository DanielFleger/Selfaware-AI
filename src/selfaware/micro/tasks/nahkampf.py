# -*- coding: utf-8 -*-
"""Nahkaempfer (B-181). Daniel 10.11.2026: "ein Modul fuer Nahkaempfer und die hat eben das Submodul Raid ganz einfach fuer jede Einheit.
Alles was wir wissen wird da reingefeeded und default agieren sie einfach wie es am Anfang Assassinen gemacht haben - nach Wirkung.
schlaues pathing. maximaler effekt".

NahkampfRaid fuehrt jede Einheit einzeln: Ziel nach Wirkung (baukasten/wirkung.py: Wert mal Erfolg je Takt, ein Ziel je Einheit), Weg mit
der wenigsten Gefahr (services/schussfeld.sicherer_weg, wie die Assassinen), am Ende der Angriff. Faellt das Ziel weg oder wird es zu
gefaehrlich, kommt das naechste. Es gehoeren nur Einheiten dazu, die fuer den Raid bestellt wurden; Starttruppen bleiben bei den Waechtern.

B-182 (Plan_Wegfuehrung.md; Daniel 11.11. 00:48 auf die Frage, ob als Naechstes der Nahkampf-Raid umzieht: "Ja, Nahkampf-Raid"):
Mit der gemeinsamen Wegfuehrung (self.weg, setzt der Raid-Einsatz) waehlt das Modul nur noch das Ziel; Weg und Befehle kommen jede
Runde neu von der Wegfuehrung. Meldet sie "gefahr" oder "kein_weg", nimmt diese Einheit fuer raids.SPERRE_RUNDEN ein anderes Ziel;
ein Erfolg zaehlt nur, wenn sie das Ziel am Ziel angriff ("greift_an"). Am Ziel greift sie auch unter Beschuss an: Daniel 11.11.
19:40 auf die Frage "Darf der Nahkampf-Raid Ziele unter Beschuss angreifen?": "Gerne freigeben" (baukasten/raid.TROTZ_GEFAHR).
"""

import collections

import selfaware.services.schussfeld as schussfeld
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import raids as RA

# Nahkampf-Arten ohne eigenes Raid-Modul: Sklaven fuehrt der Brandtrupp, Assassinen ihr eigenes Modul, der Lord verteidigt nur
KANN = frozenset({24, 25, 26, 27, 28, 75})
AM_ZIEL = 4  # Felder: so nah gilt die Einheit als am Ziel (wie der Brandtrupp)
AM_WEGPUNKT = 3  # Felder: dann kommt der naechste Wegpunkt


def _name(schluessel):
    return "Gebaeude" if schluessel[0] == "g" else "Arbeiter"


class NahkampfRaid:
    def __init__(self, sp, gelaende=None, wissen=None):
        self.sp, self.gelaende = sp, gelaende
        self.wissen = wissen if wissen is not None else WK.Wissen()
        self.erwartet = collections.Counter()  # bestellte, noch nicht angekommene Einheiten je Art
        self.bekannt = None  # eigene Einheit -> Art, wie zuletzt gesehen; None bis zur ersten Runde
        self.mitglieder = set()
        self.ziel = {}  # Einheit -> Schluessel des Ziels
        self.wegpunkte = {}  # Einheit -> offene Wegpunkte (nur ohne Wegfuehrung)
        self.befohlen = {}  # Einheit -> (Befehl, Runde) (nur ohne Wegfuehrung)
        self.weg = None  # B-182: gemeinsame Wegfuehrung (micro/wegfuehrung.py), setzt der Raid-Einsatz
        self.gesperrt = {}  # (Einheit, Ziel) -> Runde: nach "gefahr"/"kein_weg" waehlt diese Einheit das Ziel so lange nicht
        self.greift = {}  # Einheit -> Ziel, das sie zuletzt am Ziel angriff (Status "greift_an" der Wegfuehrung)
        self.runde = 0
        self.zerstoert = self.getoetet = 0

    def bestellt(self, typ, anzahl):
        """Der Lenker meldet, was er fuer den Raid bestellt hat: Diese Arten nimmt das Modul auf, sobald sie da sind."""
        if typ in KANN:
            self.erwartet[typ] += anzahl

    def _aufnehmen(self, L):
        eigene = {
            n: e for n, e in L.items() if e.get("besitzer") == self.sp and e.get("leben", 1) > 0
        }
        if self.bekannt is None:
            self.bekannt = {n: e["typ"] for n, e in eigene.items()}
            return
        # Reihe 2b (10.11.): Angeworben wird aus einem Bauern, die Nummer bleibt, nur die Art wechselt (Bauer 565 wurde Typ 75)
        for n in sorted(eigene):
            typ = eigene[n]["typ"]
            if typ in KANN and self.bekannt.get(n) != typ and self.erwartet[typ] > 0:
                self.erwartet[typ] -= 1
                self.mitglieder.add(n)
        self.bekannt = {n: e["typ"] for n, e in eigene.items()}
        self.mitglieder &= {n for n, e in eigene.items() if e["typ"] in KANN}

    def _senden(self, n, b, befehl):
        alt = self.befohlen.get(n)
        if alt is None or alt[0] != b or self.runde - alt[1] >= RA.NEU_ALLE:
            befehl(b, 1.0, bis="ANGRIFF")
            self.befohlen[n] = (b, self.runde)

    def _waehlen(self, n, e, ziele, belegt, L):
        ort = (e["x"], e["y"])
        best = max(
            (
                (self.wissen.wert_je_takt(e["typ"], ort, z)[0], z)
                for z in ziele.values()
                if z.schluessel not in belegt and self.gesperrt.get((n, z.schluessel), -1) <= self.runde
            ),
            default=(0.0, None),
            key=lambda x: x[0],
        )
        if best[1] is None or best[0] <= 0:
            return None
        z = best[1]
        weg = []
        if self.gelaende and self.weg is None:  # mit Wegfuehrung plant sie den Weg, jede Runde neu
            weg = list(schussfeld.sicherer_weg(self.gelaende, L, self.sp, ort, z.ort)[0])
        self.ziel[n], self.wegpunkte[n] = (
            z.schluessel,
            weg[:-1],
        )  # der letzte Wegpunkt ist das Ziel selbst, dort kommt der Angriff
        return z

    def _am_ziel_gewesen(self, n, alt):
        """Griff diese Einheit ihr Ziel zuletzt am Ziel an? Mit Wegfuehrung deren Status, sonst der letzte eigene Befehl."""
        if self.weg is not None:
            return self.greift.get(n) == alt
        return n in self.befohlen and bool(self.befohlen[n][0].get("angriff", {}).keys() & {"gebaeude", "ziel"})

    def _freigeben(self, n):
        self.ziel.pop(n, None)
        self.wegpunkte.pop(n, None)
        self.greift.pop(n, None)
        if self.weg is not None:
            self.weg.loslassen(n)

    def schritt(self, L, G, befehl):
        self.runde += 1
        self._aufnehmen(L)
        # B-182: Ziele toter Teilnehmer gelten nicht mehr als belegt (sie sperrten das Ziel fuer die anderen und fuer den Kauf)
        for n in [n for n in self.ziel if n not in self.mitglieder]:
            self._freigeben(n)
        if not self.mitglieder:
            return []
        self.wissen.lernen(L, self.sp)
        ziele = {z.schluessel: z for z in WK.ziele(L, G, self.sp)}
        aus = []
        for n in sorted(self.mitglieder):
            e = L[n]
            ort = (e["x"], e["y"])
            alt = self.ziel.get(n)
            st = self.weg.status(n) if self.weg is not None and alt is not None else None
            if st == "greift_an":
                self.greift[n] = alt
            elif st in ("gefahr", "kein_weg"):
                # B-182 (Plan_Wegfuehrung.md): kein sicherer Standplatz oder kein Weg - diese Einheit nimmt ein anderes Ziel
                self.gesperrt[(n, alt)] = self.runde + RA.SPERRE_RUNDEN
                aus.append("NAHKAMPF-RAID: %d (Typ %d) gibt %s %d auf (%s)" % (n, e["typ"], _name(alt), alt[1], st))
                self._freigeben(n)
                alt = None
            # "ziel_weg": die Wegfuehrung sieht unter der Nummer etwas anderes (Art, Besitzer) - das alte Ziel ist weg
            weg_ist = alt is not None and (alt not in ziele or st == "ziel_weg")
            if alt is not None and (weg_ist or not self.wissen.am_ziel(e["typ"], ziele[alt])[1]):
                if weg_ist and self._am_ziel_gewesen(n, alt):
                    if alt[0] == "g":
                        self.zerstoert += 1
                    else:
                        self.getoetet += 1
                    # B-182: jeder Erfolg in die Mitschrift, die Eichung misst daran die Takte vom Ziel bis zum Erfolg
                    aus.append("NAHKAMPF-RAID: %d (Typ %d) hat %s %d erledigt" % (n, e["typ"], _name(alt), alt[1]))
                elif weg_ist and self.weg is not None:
                    aus.append("NAHKAMPF-RAID: %s %d ist weg, %d war nicht am Ziel - kein eigener Erfolg" % (_name(alt), alt[1], n))
                self._freigeben(n)
                alt = None
            if alt is None:
                belegt = set(self.ziel.values())
                z = self._waehlen(n, e, ziele, belegt, L)
                if z is None:
                    continue
                aus.append(
                    "NAHKAMPF-RAID: %d (Typ %d) -> %s %d (Typ %d) bei %s, %d Wegpunkte, %d Felder%s"
                    % (
                        n,
                        e["typ"],
                        _name(z.schluessel),
                        z.schluessel[1],
                        z.typ,
                        z.ort,
                        len(self.wegpunkte[n]),
                        WK.schach(ort, z.ort),
                        ", Weg ueber die Wegfuehrung" if self.weg is not None else "",
                    )
                )
            art, nr = self.ziel[n]
            if self.weg is not None:
                # B-182: Weg und Befehle jede Runde neu von der Wegfuehrung - unterwegs um neue Gefahr herum, am Ziel der Angriff
                self.weg.fuehre(n, "gebaeude" if art == "g" else "einheit", nr, "nahkampfraid")
                continue
            weg = self.wegpunkte.get(n, [])
            while weg and WK.schach(ort, weg[0]) <= AM_WEGPUNKT:
                weg.pop(0)
            if weg:
                b = {"angriff": {"einheiten": [n], "lauf": [weg[0][0], weg[0][1]]}}
            elif art == "g":
                b = {"angriff": {"einheiten": [n], "gebaeude": nr}}
            else:
                b = {"angriff": {"einheiten": [n], "ziel": nr}}
            self._senden(n, b, befehl)
        return aus

    def bericht(self):
        return "Nahkampf-Raid: %d Einheiten, %d Gebaeude zerstoert, %d Arbeiter getoetet" % (
            len(self.mitglieder),
            self.zerstoert,
            self.getoetet,
        )
