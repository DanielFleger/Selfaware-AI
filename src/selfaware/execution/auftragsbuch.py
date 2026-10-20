# -*- coding: utf-8 -*-
"""Auftragsbuch (Daniel 06.10. 22:08: "wie kann es sein, dass irgendein Gebaeude ohne Pruefung gebaut wird? ... jedes
Gebaeude, jede Person etc. muss zu jedem Tick klar sein").

Vorher schickte baue_schnell den Bauauftrag und gab den Platz zurueck, als stuende das Gebaeude schon. Folge (Serie
06.10. 21:58, Versuche 1-4): "Ersatzplatz Steinbruch bei (80,271): (80,271)" bei 8 Holz - gebaut wurde nichts, bei
Tick 1.500 stand kein Steinbruch.

Jetzt, fuer jeden Bau ueber baue_schnell:
  1. VOR dem Senden: reichen Holz/Stein/Gold (Kostentabelle des Spiels gegen den Bestand)? Sonst nicht senden (ABGELEHNT
     mit Grund, je Art und Grund hoechstens alle 200 Ticks gemeldet).
  2. NACH dem Senden: offener Auftrag (Art, Platz, Tick, Zweck).
  3. JEDE Runde Abgleich mit der Gebaeudeliste des Spiels: neues eigenes Gebaeude dieser Art hoechstens 2 Felder vom
     Platz -> BESTAETIGT (mit Ticks bis dahin); nach WARTEN Ticks nicht da -> GESCHEITERT (mit Bestand jetzt).
  4. Belegung: je Betrieb Arbeiter Soll/Ist aus dem Lagebild (Arbeitsplatz jeder Einheit); unterbesetzt seit wann,
     ab 200 Ticks einmal gemeldet, die Besetzung danach auch.
Gebaeude, die ohne Auftrag auftauchen (Eroeffnung baue_viele, Steinhaufen des Spiels), werden still aufgenommen.
"""


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Auftragsbuch:
    WARTEN = 60          # Ticks: so lange darf ein gesendeter Bau brauchen, bis er in der Gebaeudeliste steht
    MELDEN_LEER = 200    # Ticks unterbesetzt, ab denen ein Betrieb gemeldet wird
    UEBERHOLT = 2        # so viele spaeter gebaute Holzfaellerhuetten besetzt, waehrend eine leer bleibt -> unerreichbar

    def __init__(self, sp, arbeiter_je, namen):
        self.sp, self.arbeiter_je, self.namen = sp, arbeiter_je, namen
        self.offen = []
        self.bekannt = {}            # Gebaeudenummer -> (typ, x, y); Nummern werden nach Abriss neu vergeben (v3)
        self.zahl = {"bestellt": 0, "bestaetigt": 0, "gescheitert": 0, "abgelehnt": 0}
        self.leer_seit, self.gemeldet = {}, set()
        self.abgelehnt_zuletzt = {}
        self.ereignisse = []
        self.tick = 0
        self.gescheitert = []        # (tick, typ, ort, zweck) - fuer die Fruehpruefung
        self.unerreichbar = []       # (nr, typ, ort) - bestaetigt, aber laut Spiel nicht erreichbar; der Lenker reisst ab
        self.erreichbar_pruefen = {} # nr -> (tick, typ, ort): frisch gebaut mit erreichbar=0, Nachpruefung nach 250 Ticks
        self.hat = {}
        self.bestaetigt_tick = {}    # nr -> Tick, ab dem der Betrieb in der Liste steht (Reihenfolge fuer "ueberholt")

    def name(self, typ):
        return self.namen.get(typ, {}).get("name", str(typ)) if isinstance(self.namen.get(typ), dict) else str(typ)

    # ---- vor / nach dem Senden ------------------------------------------------------------------------------------
    def ablehnen(self, typ, ort, grund):
        self.zahl["abgelehnt"] += 1
        schl = (typ, grund.split(" ")[0])
        if self.tick - self.abgelehnt_zuletzt.get(schl, -999) >= 200:
            self.abgelehnt_zuletzt[schl] = self.tick
            self.ereignisse.append("BAU ABGELEHNT %s bei %s: %s" % (self.name(typ), tuple(ort), grund))

    def vormerken(self, typ, ort, zweck=""):
        self.offen.append({"typ": typ, "ort": tuple(ort), "tick": self.tick, "zweck": zweck})
        self.zahl["bestellt"] += 1

    def offen_bei(self, typ, ort, r=2):
        return any(a["typ"] == typ and schach(a["ort"], ort) <= r for a in self.offen)

    # ---- jede Runde -----------------------------------------------------------------------------------------------
    def abgleich(self, G, L, st):
        t = st.get("t", self.tick)
        self.tick = t
        ev, self.ereignisse = self.ereignisse, []
        eig = {n: g for n, g in G.items() if g["besitzer"] == self.sp}
        neu = {n: g for n, g in eig.items() if self.bekannt.get(n) != (g["typ"], g["x"], g["y"])}
        for a in list(self.offen):
            treffer = [n for n, g in neu.items() if g["typ"] == a["typ"] and schach((g["x"], g["y"]), a["ort"]) <= 2]
            if treffer:
                n = min(treffer, key=lambda m: schach((neu[m]["x"], neu[m]["y"]), a["ort"]))
                g = neu.pop(n)
                self.bekannt[n] = (g["typ"], g["x"], g["y"])
                self.offen.remove(a)
                self.zahl["bestaetigt"] += 1
                ev.append("BAU BESTAETIGT %s Nr %d bei (%d,%d) nach %d Ticks%s" % (
                    self.name(a["typ"]), n, g["x"], g["y"], t - a["tick"], " [%s]" % a["zweck"] if a["zweck"] else ""))
                self.bestaetigt_tick[n] = t
                # Nachpruefung (Daniel 23:10 "Holzfaeller sollten alle zugaenglich sein"): mit Flag 0 jeder Betrieb; ohne Flag
                # die Holzfaellerhuetten (08.10. 00:08, Daniel, Bild: Huetten jenseits des Flusses; Lauf s25/5: 21 Huetten mit
                # "erreichbar" 1, nie besetzt - das Feld beweist in keine Richtung etwas)
                if g.get("erreichbar") == 0 or a["typ"] == 3:
                    self.erreichbar_pruefen[n] = (t, g["typ"], (g["x"], g["y"]))
            elif t - a["tick"] > self.WARTEN:
                self.offen.remove(a)
                self.zahl["gescheitert"] += 1
                self.gescheitert.append((t, a["typ"], a["ort"], a["zweck"]))
                ev.append("BAU GESCHEITERT %s bei %s (gesendet Tick %d%s, nach %d Ticks nicht in der Gebaeudeliste; "
                          "jetzt Holz %d Stein %d Gold %d)" % (
                              self.name(a["typ"]), a["ort"], a["tick"], ", %s" % a["zweck"] if a["zweck"] else "",
                              t - a["tick"], st.get("holz", 0), st.get("stein", 0), st.get("gold", 0)))
        ev_beleg = self._belegung(eig, L)          # Arbeiter je Betrieb JETZT (fuer den Beweis unten)
        for n, (t0, typ0, ort0) in list(self.erreichbar_pruefen.items()):
            if n not in eig or self.hat.get(n, 0) > 0 or not self.arbeiter_je.get(typ0):
                del self.erreichbar_pruefen[n]                # hat einen Arbeiter -> erreichbar
                continue
            if typ0 == 3:
                # Holzfaeller: Beweis = UEBERHOLT. Neue Bauern besetzen die Huetten der Reihe nach (Lauf s25/6: 22-26, dann
                # 36-43, dann 47; die 1-4 am Feuer sind die Vierergruppe, die sich sammelt, L7) - "600 Ticks leer bei freien
                # Bauern" riss so Huette 47 ab, die einfach die letzte in der Schlange war. Unerreichbar ist eine Huette erst,
                # wenn mindestens 2 SPAETER gebaute Huetten Arbeiter bekommen haben, waehrend sie leer blieb.
                ueberholt = [m for m, tm in self.bestaetigt_tick.items() if tm > t0 and m in eig and eig[m]["typ"] == 3
                             and self.hat.get(m, 0) > 0]
                if len(ueberholt) >= self.UEBERHOLT:
                    del self.erreichbar_pruefen[n]
                    self.unerreichbar.append((n, typ0, ort0))
                    ev.append("BAU UNERREICHBAR %s Nr %d bei %s: leer seit Tick %d, spaeter gebaute Huetten %s schon besetzt "
                              "- wird abgerissen" % (self.name(typ0), n, ort0, t0, sorted(ueberholt)[:5]))
            elif t - t0 >= 600 and st.get("feuer", 0) > 0:
                # andere Betriebe mit Flag 0 (23:41, Daniel: "laesst immer noch Apfelplantagen abreissen"): Flag allein ist
                # kein Beweis - unerreichbar erst nach 600 Ticks ohne Arbeiter bei freien Bauern
                del self.erreichbar_pruefen[n]
                self.unerreichbar.append((n, typ0, ort0))
                ev.append("BAU UNERREICHBAR %s Nr %d bei %s: %d Ticks ohne Arbeiter bei %d freien Bauern - wird abgerissen" % (
                    self.name(typ0), n, ort0, t - t0, st.get("feuer", 0)))
        for n, g in neu.items():                       # ohne Auftrag aufgetaucht: still aufnehmen
            self.bekannt[n] = (g["typ"], g["x"], g["y"])
            self.bestaetigt_tick[n] = t
        for n in [n for n in self.bekannt if n not in eig]:
            del self.bekannt[n]
            self.bestaetigt_tick.pop(n, None)
        ev += ev_beleg
        return ev

    def _belegung(self, eig, L):
        ev = []
        self.hat = {}
        for e in L.values():
            ap = e.get("arbeitsplatz")
            if e["besitzer"] == self.sp and ap:
                self.hat[ap] = self.hat.get(ap, 0) + 1
        for n, g in eig.items():
            soll = self.arbeiter_je.get(g["typ"])
            if not soll:
                continue
            if self.hat.get(n, 0) < soll:
                seit = self.leer_seit.setdefault(n, self.tick)
                if self.tick - seit >= self.MELDEN_LEER and n not in self.gemeldet:
                    self.gemeldet.add(n)
                    ev.append("UNTERBESETZT %s Nr %d bei (%d,%d): %d von %d Arbeitern seit Tick %d" % (
                        self.name(g["typ"]), n, g["x"], g["y"], self.hat.get(n, 0), soll, seit))
            elif n in self.leer_seit:
                seit = self.leer_seit.pop(n)
                if n in self.gemeldet:
                    self.gemeldet.discard(n)
                    ev.append("BESETZT %s Nr %d nach %d Ticks" % (self.name(g["typ"]), n, self.tick - seit))
        for n in [n for n in self.leer_seit if n not in eig]:
            self.leer_seit.pop(n)
            self.gemeldet.discard(n)
        return ev

    def stand(self, G, st):
        """Eine Zeile: jede Gebaeudeart (Anzahl, davon unterbesetzt), Feuer, offene Auftraege, Zaehler."""
        eig = {n: g for n, g in G.items() if g["besitzer"] == self.sp}
        art = {}
        for n, g in eig.items():
            a = art.setdefault(g["typ"], [0, 0, 0, 0])
            a[0] += 1
            soll = self.arbeiter_je.get(g["typ"], 0)
            a[1] += soll
            a[2] += min(self.hat.get(n, 0), soll) if soll else 0
            a[3] += 1 if soll and self.hat.get(n, 0) < soll else 0
        teile = []
        for typ, (k, soll, ist, leer) in sorted(art.items()):
            teile.append("%s %d%s" % (self.name(typ), k, " (Arbeiter %d/%d)" % (ist, soll) if soll else ""))
        return "STAND Tick %d | Feuer %d, Leute %d/%d | %s | offen %s | %s" % (
            self.tick, st.get("feuer", 0), st.get("leute", 0), st.get("platz", 0), ", ".join(teile),
            [(self.name(a["typ"]), a["ort"]) for a in self.offen] or "-",
            ", ".join("%s %d" % kv for kv in self.zahl.items()))
