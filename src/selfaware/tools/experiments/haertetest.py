# -*- coding: utf-8 -*-
"""Haertetest 1 (Daniel 06.10. 20:54): Zeit von Tick 0 bis zu den ersten 10 ausgebildeten Streitkolbenkaempfern,
realistische Startbedingungen (Liga: 0 Gold, Startholz kommt bis Tick ~650 auf 150, Startessen 15 je Sorte).
Nichts gesetzt, nichts gratis - Daniel schaut zu.

Bauordnung v1 (Plan_Streitkolben.md, Grundlinie: Lager bleibt am Bergfried; Test 2 versetzt es):
  Kornspeicher + Markt am Bergfried -> Kaese und Brot verkaufen (+150 Gold), Aepfel/Fleisch behalten (Vielfalt)
  2 Milchviehhoefe zuerst (Kuehe brauchen Zeit) -> Steinbruch + Ochsenjoch (einziger Steinplatz, Westen)
  -> Gerberei / Eisenmine (Sueden) / Schmiede / Waffenlager (Aufbauplaner, 1 Feld vom Lager) -> Kaserne weit weg.
Jeder Auftrag wird gebaut, sobald Holz/Stein/Gold reichen (Kosten aus der Spieltabelle). Anwerben, sobald Keule +
Leder + 20 Gold + ein Bauer am Feuer da sind.
Zeitmarken: erster Stein, erstes Eisen, erste Kuh, erste Keule, erstes Leder, Kaempfer 1..10, Gold/Beliebtheit/Leute.
Ergebnis: data/research/haertetest_<zeit>.json
Aufruf: uv run python -m selfaware.tools.experiments.haertetest [tempo=200] [max=40000] [version=v1]
"""

from selfaware import workspace as _workspace
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))

import selfaware.game.ucp.befehl as kanal
import selfaware.runtime.live.erstes_spiel as E
import selfaware.services.wegkarte as W
import selfaware.macro.aufbau_planer as P
from selfaware.game.ucp.laden import befehl, peek, TICK
from selfaware.game.ucp.bauen import kosten, vorrat
from selfaware.tools.experiments.streitkolben_messen import warte_ticks

D = os.path.join(_workspace.DATA)
SP = 1
KEULE, LEDER = 21, 23
MAPPER = {P.WAFFENLAGER: 81, P.SCHMIEDE: 83, P.GERBEREI: 85}
NAME = {19: "Kornspeicher", 26: "Markt", 33: "Milchviehhof", 20: "Steinbruch", 4: "Ochsenjoch", 16: "Gerberei",
        5: "Eisenmine", 13: "Schmiede", 11: "Waffenlager", 9: "Kaserne", 1: "Huette"}


class Lenker:
    def __init__(self, version):
        self.version = version
        self.t0 = None
        self.marken = {}
        self.verlauf = []
        self.erledigt = []
        self.kaserne = None
        self.verkauft = False
        self.geplant = False
        G = E.runde_lesen()[2]
        berg = next(g for g in G.values() if g["besitzer"] == SP and g["typ"] == 41)
        self.bx, self.by = berg["x"] + 3, berg["y"] + 3
        teile = [g for g in G.values() if g["besitzer"] == SP and g["typ"] == 10]
        self.lx, self.ly = teile[0]["x"], teile[0]["y"]
        self.kosten = {t: kosten(t) for t in NAME}
        # (Name, Typ, Ort, Umkreis) - Ort = Mitte fuer die Platzsuche des Spiels; "plan" = Aufbauplaner
        bx, by = self.bx, self.by
        self.auftraege = [
            ["Kornspeicher", 19, (bx - 12, by - 8), 12], ["Markt", 26, (bx - 12, by + 4), 14],
            ["Milchviehhof", 33, (172, 297), 20], ["Milchviehhof", 33, (172, 297), 25],
            ["Steinbruch", 20, (81, 267), 10], ["Ochsenjoch", 4, (90, 267), 10],
            ["Huette", 1, (bx - 16, by - 2), 18], ["Huette", 1, (bx - 16, by - 2), 18],
            ["Gerberei", "plan", None, None], ["Eisenmine", 5, (141, 317), 14], ["Waffenlager", "plan", None, None],
            ["Schmiede", "plan", None, None], ["Kaserne", 9, (bx - 14, by + 16), 25]]

    def tick(self):
        return peek(TICK)[0]

    def marke(self, name, t):
        if name not in self.marken:
            self.marken[name] = t
            print("MARKE %-18s Tick %6d" % (name, t), flush=True)

    def bezahlbar(self, typ, st, reserve=None):
        c = self.kosten[typ]
        r = reserve or {}
        return st.get("holz", 0) >= c["holz"] + r.get("holz", 0) and st.get("stein", 0) >= c["stein"] + r.get("stein", 0) \
            and st.get("gold", 0) >= c["gold"] + r.get("gold", 0)

    def planen(self, G):
        """Gerberei, Waffenlager, Schmiede um das Lager - sobald die Hoefe stehen (Hoftore im Plan)."""
        hoefe = [(g["x"], g["y"]) for g in G.values() if g["besitzer"] == SP and g["typ"] == 33]
        k = W.holen(max(self.lx - 30, 0), max(self.ly - 30, 0), min(self.lx + 40, 399), min(self.ly + 45, 399))
        plan, bericht = P.plane(k, 1, 1, None, hoefe)
        self.plan = {P.GERBEREI: None, P.WAFFENLAGER: None, P.SCHMIEDE: None}
        for art, x, y, r, e in plan.bauten:
            self.plan[art] = (x, y, r)
        self.bericht_plan = bericht
        self.geplant = True
        print("PLAN", {NAME[a]: v for a, v in self.plan.items()}, flush=True)

    def runde(self):
        st, L, G = E.runde_lesen()
        t = st.get("t", 0)
        eigen = {n: g for n, g in G.items() if g["besitzer"] == SP}
        # Zeitmarken
        for name, ok in (("erstes Holz>150", st.get("holz", 0) >= 150), ("erster Stein", st.get("stein", 0) > 0),
                         ("erstes Eisen", st.get("eisen", 0) > 0), ("erste Kuh", st.get("T51", 0) > 0)):
            if ok:
                self.marke(name, t)
        v = vorrat(SP)
        if v.get("keule", 0) > 0:
            self.marke("erste Keule", t)
        if v.get("leder", 0) > 0:
            self.marke("erstes Leder", t)
        kaempfer = st.get("T26", 0)
        for n in range(1, 11):
            if kaempfer >= n:
                self.marke("Kaempfer %d" % n, t)
        self.verlauf.append({"t": t, "holz": st.get("holz"), "stein": st.get("stein"), "eisen": st.get("eisen"),
                             "gold": st.get("gold"), "beliebt": st.get("beliebt"), "leute": st.get("leute"),
                             "feuer": st.get("feuer"), "kuehe": st.get("T51", 0), "keule": v.get("keule"),
                             "leder": v.get("leder"), "kaempfer": kaempfer})
        # Essen verkaufen, sobald der Kornspeicher es zeigt (Kaese 6, Brot 4 Gold je Stueck)
        if not self.verkauft and any(g["typ"] == 19 for g in eigen.values()) and any(g["typ"] == 26 for g in eigen.values()):
            if st.get("kaese", 0) >= 5 or st.get("brot", 0) >= 5:
                for ware, name in ((11, "kaese"), (10, "brot")):
                    for _ in range(st.get(name, 0) // 5):
                        befehl({"spielbefehl": {"nr": 38, "werte": [1, ware]}}, 1.0, bis="SPIELBEFEHL")
                self.verkauft = True
                self.marke("Essen verkauft", t)
        # Planen, sobald beide Hoefe stehen
        if not self.geplant and sum(1 for g in eigen.values() if g["typ"] == 33) >= 2:
            self.planen(G)
        # Auftraege der Reihe nach - der erste, der nicht bezahlbar ist, haelt die spaeteren NICHT auf (Gold/Stein
        # kommen zu verschiedenen Zeiten), aber Holz wird fuer die vorderen zurueckgehalten
        reserve = {"holz": 0, "stein": 0, "gold": 0}
        for a in self.auftraege:
            name, typ, ort, r = a
            art = {"Gerberei": P.GERBEREI, "Waffenlager": P.WAFFENLAGER, "Schmiede": P.SCHMIEDE}.get(name, typ)
            if typ == "plan" and not self.geplant:
                c = self.kosten[art]
                for k2 in reserve:
                    reserve[k2] += c[k2]
                continue
            if self.bezahlbar(art, st, reserve):
                if typ == "plan":
                    x, y, rr = self.plan[art]
                    befehl({"baue": {"mapper": MAPPER[art], "x": x, "y": y, "groesse": 4, "richtung": rr}}, 0.8, bis="BAUE")
                    o = (x, y)
                else:
                    o = E.baue_schnell(art, ort[0], ort[1], r)
                if o:
                    self.auftraege.remove(a)
                    self.erledigt.append([name, list(o), t])
                    print("BAU %-12s bei %s Tick %d" % (name, o, t), flush=True)
                    return st                              # eine Bauaktion je Runde: Bestand neu lesen
            c = self.kosten[art]
            for k2 in reserve:
                reserve[k2] += c[k2]
        # Schmiede auf Keulen, Kaserne merken, anwerben
        for n, g in eigen.items():
            if g["typ"] == P.SCHMIEDE and n not in getattr(self, "umgestellt", set()):
                befehl({"spielbefehl": {"nr": 33, "werte": [n, KEULE, g.get("uid", 0)]}}, 1.0, bis="SPIELBEFEHL")
                self.umgestellt = getattr(self, "umgestellt", set()) | {n}
            if g["typ"] == 9:
                self.kaserne = n
        if self.kaserne and v.get("keule", 0) and v.get("leder", 0) and st.get("gold", 0) >= 20 and st.get("feuer", 0) > 0:
            befehl({"werbe": {"typ": 26, "gebaeude": self.kaserne}}, 1.0, bis="WERBE")
        return st


def main():
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    tempo, maxt, version = int(arg.get("tempo", 200)), int(arg.get("max", 40000)), arg.get("version", "v1")
    E.LEERE_KI = True
    E.gefecht_starten(tempo)
    lk = Lenker(version)
    stempel = time.strftime("%Y%m%d_%H%M%S")
    try:
        while True:
            st = lk.runde()
            if "Kaempfer 10" in lk.marken or st.get("t", 0) > maxt:
                break
            warte_ticks(40)
    finally:
        befehl({"pause": True}, 0.5)
        erg = {"version": version, "marken": lk.marken, "gebaut": lk.erledigt, "offen": [a[0] for a in lk.auftraege],
               "plan": getattr(lk, "bericht_plan", None), "verlauf": lk.verlauf}
        pfad = os.path.join(D, "haertetest_%s_%s.json" % (version, stempel))
        json.dump(erg, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
        print("ERGEBNIS: 10 Kaempfer bei Tick %s" % lk.marken.get("Kaempfer 10"), flush=True)
        print("Daten:", pfad, flush=True)


if __name__ == "__main__":
    kanal.belege()
    try:
        main()
    finally:
        kanal.freigeben()
