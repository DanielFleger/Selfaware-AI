# -*- coding: utf-8 -*-
"""Nahkaempfer (B-181). Daniel 10.11.2026: "ein Modul fuer Nahkaempfer und die hat eben das Submodul Raid ganz einfach fuer jede Einheit.
Alles was wir wissen wird da reingefeeded und default agieren sie einfach wie es am Anfang Assassinen gemacht haben - nach Wirkung.
schlaues pathing. maximaler effekt".

NahkampfRaid fuehrt jede Einheit einzeln: Ziel nach Wirkung (baukasten/wirkung.py: Wert mal Erfolg je Takt, ein Ziel je Einheit), Weg mit
der wenigsten Gefahr (services/schussfeld.sicherer_weg, wie die Assassinen), am Ende der Angriff. Faellt das Ziel weg oder wird es zu
gefaehrlich, kommt das naechste. Es gehoeren nur Einheiten dazu, die fuer den Raid bestellt wurden; Starttruppen bleiben bei den Waechtern.
"""

import collections

import selfaware.services.schussfeld as schussfeld
from selfaware.baukasten import wirkung as WK
from selfaware.micro.tasks import raids as RA

# Nahkampf-Arten ohne eigenes Raid-Modul: Sklaven fuehrt der Brandtrupp, Assassinen ihr eigenes Modul, der Lord verteidigt nur
KANN = frozenset({24, 25, 26, 27, 28, 75})
AM_ZIEL = 4  # Felder: so nah gilt die Einheit als am Ziel (wie der Brandtrupp)
AM_WEGPUNKT = 3  # Felder: dann kommt der naechste Wegpunkt


class NahkampfRaid:
    def __init__(self, sp, gelaende=None, wissen=None):
        self.sp, self.gelaende = sp, gelaende
        self.wissen = wissen if wissen is not None else WK.Wissen()
        self.erwartet = collections.Counter()  # bestellte, noch nicht angekommene Einheiten je Art
        self.bekannt = None  # eigene Einheit -> Art, wie zuletzt gesehen; None bis zur ersten Runde
        self.mitglieder = set()
        self.ziel = {}  # Einheit -> Schluessel des Ziels
        self.weg = {}  # Einheit -> offene Wegpunkte
        self.befohlen = {}  # Einheit -> (Befehl, Runde)
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
                if z.schluessel not in belegt
            ),
            default=(0.0, None),
            key=lambda x: x[0],
        )
        if best[1] is None or best[0] <= 0:
            return None
        z = best[1]
        weg = []
        if self.gelaende:
            weg = list(schussfeld.sicherer_weg(self.gelaende, L, self.sp, ort, z.ort)[0])
        self.ziel[n], self.weg[n] = (
            z.schluessel,
            weg[:-1],
        )  # der letzte Wegpunkt ist das Ziel selbst, dort kommt der Angriff
        return z

    def schritt(self, L, G, befehl):
        self.runde += 1
        self._aufnehmen(L)
        if not self.mitglieder:
            return []
        self.wissen.lernen(L, self.sp)
        ziele = {z.schluessel: z for z in WK.ziele(L, G, self.sp)}
        aus = []
        for n in sorted(self.mitglieder):
            e = L[n]
            ort = (e["x"], e["y"])
            alt = self.ziel.get(n)
            if alt is not None and (
                alt not in ziele or not self.wissen.am_ziel(e["typ"], ziele[alt])[1]
            ):
                if (
                    alt not in ziele
                    and n in self.befohlen
                    and self.befohlen[n][0].get("angriff", {}).keys() & {"gebaeude", "ziel"}
                ):
                    if alt[0] == "g":
                        self.zerstoert += 1
                    else:
                        self.getoetet += 1
                    # B-182: jeder Erfolg in die Mitschrift, die Eichung misst daran die Takte vom Ziel bis zum Erfolg
                    aus.append(
                        "NAHKAMPF-RAID: %d (Typ %d) hat %s %d erledigt"
                        % (n, e["typ"], "Gebaeude" if alt[0] == "g" else "Arbeiter", alt[1])
                    )
                self.ziel.pop(n, None)
                self.weg.pop(n, None)
                alt = None
            if alt is None:
                belegt = set(self.ziel.values())
                z = self._waehlen(n, e, ziele, belegt, L)
                if z is None:
                    continue
                aus.append(
                    "NAHKAMPF-RAID: %d (Typ %d) -> %s %d (Typ %d) bei %s, %d Wegpunkte, %d Felder"
                    % (
                        n,
                        e["typ"],
                        "Gebaeude" if z.schluessel[0] == "g" else "Arbeiter",
                        z.schluessel[1],
                        z.typ,
                        z.ort,
                        len(self.weg[n]),
                        WK.schach(ort, z.ort),
                    )
                )
            weg = self.weg.get(n, [])
            while weg and WK.schach(ort, weg[0]) <= AM_WEGPUNKT:
                weg.pop(0)
            art, nr = self.ziel[n]
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
