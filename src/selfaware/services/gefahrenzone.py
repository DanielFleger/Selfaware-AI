# -*- coding: utf-8 -*-
"""Neubau nur an sicheren Stellen (19.10., Punkt 4 der Liste; Daniel 16:53 "jetzt sieht man halt, dass viel zu viel Hopfen
gemacht wird", Vorschlag 16:54 "neue Betriebe nur dort, wo sie ihre Anlaufzeit voraussichtlich ueberleben", 16:57 "ja bau
in der Reihenfolge").

Anlass 1018k: Spieler 2 baute zwischen Tick 19.000 und 25.000 50 Holzfaellerhuetten neu und verlor 47, in denen nie Holz
lag - Nachbau genau dort, wo die Huetten gerade fielen.

GEMESSEN 19.10. 17:33 (Lageprotokolle 1018i/j/k/l, beide Spieler, Holzfaellerhuetten - nur bei ihnen ist "hat geliefert"
messbar, partie_vergleich.MIT_VORRAT): eigene Gebaeude verloren im Umkreis R in den TICKS davor ->
    Umkreis 20:  keine 86 gebaut, 72 % lieferten | 1-2: 205, 33 % | >= 3: 602, 15 %
    Umkreis 10:  keine 162, 57 %                | 1-2: 332, 19 % | >= 3: 399, 17 %
Darum: ein Betrieb (ARTEN) wird nicht gebaut, solange im Umkreis R ein eigenes Gebaeude in den letzten TICKS verloren ging.
Verlust = ein eigenes Gebaeude (ausser Fallgruben und Lagerplaetzen, NICHT_VERLUST) verschwindet aus der Gebaeudeliste.
Pruefung ohne Spiel: src/selfaware/tools/checks/gefahrenzone_pruefen.py."""
from collections import Counter

R, TICKS = 20, 3000
# KORREKTUR 19.10. 17:47 (1018n: Spieler 1 - 121 Apfelplantagen von der Gefahrenzone verhindert, ab ~47.000 keine Nahrung,
# Regelbruch bei 55.409; gemessen war die Zone nur an Holzfaellerhuetten): Nahrung (Apfel 32, Milch 33, Jaeger 7) wird IMMER
# nachgebaut - Regel 50 geht vor
ARTEN = {3, 5, 20, 31}                   # Holzfaeller, Eisenmine, Steinbruch, Hopfen
GRUBE = 67
# eigene, gewollte Abrisse sind keine Verluste: Fallgruben (Kornring-Umbau reisst sie ab, L131) und Lagerplaetze (Lager-
# Umzug in der Eroeffnung reisst das Startlager ab - sonst laege gleich zu Beginn eine Zone am Bergfried)
NICHT_VERLUST = {GRUBE, 10}


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Gefahrenzonen:
    def __init__(self, sp):
        self.sp = sp
        self.vorher = {}            # uid -> (x, y, typ)
        self.verluste = []          # (Tick, (x, y), typ)
        self.verhindert = Counter()
        self.t = 0

    def runde(self, t, G):
        if t is None:
            return
        jetzt = {g["uid"]: (g["x"], g["y"], g["typ"]) for g in G.values()
                 if g.get("besitzer") == self.sp and g["typ"] not in NICHT_VERLUST and g.get("uid")}
        for uid, (x, y, typ) in self.vorher.items():
            if uid not in jetzt:
                self.verluste.append((t, (x, y), typ))
        self.vorher = jetzt
        self.t = t
        self.verluste = [v for v in self.verluste if t - v[0] <= TICKS]

    def gefaehrdet(self, x, y, t=None):
        t = self.t if t is None else t
        return any(t - tv <= TICKS and schach((x, y), p) <= R for tv, p, _ in self.verluste)

    def erlaubt(self, typ, x, y, t=None):
        if typ in ARTEN and self.gefaehrdet(x, y, t):
            self.verhindert[typ] += 1
            return False
        return True

    def rechtecke(self, t=None):
        """Sperrflaechen fuer den Planer (ertragsplaner._orte): je frischer Verlust ein Quadrat mit Rand R."""
        t = self.t if t is None else t
        return [(p[0] - R, p[1] - R, p[0] + R, p[1] + R) for tv, p, _ in self.verluste if t - tv <= TICKS]

    def bericht(self):
        return "Gefahrenzonen: %d Neubauten verhindert %s" % (sum(self.verhindert.values()), dict(self.verhindert))
