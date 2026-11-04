# -*- coding: utf-8 -*-
"""B-142: Szene rufen_g. Offene Punkte der Checkliste, die eine Oberflaechen-Pruefung des Spiels sind: Die Funktion wird im angehaltenen Spiel direkt gerufen.

Jede Probe sagt vorher, was sie erwartet. Ein Fehler in einer Probe haelt die anderen nicht auf, jede Probe schreibt sofort in die Ergebnisdatei.
Nur Messlauf: Hier wird gesetzt und gerufen, nichts davon geht in SamurAI.
"""
import collections
import ctypes
import json
import os
import time

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk
from selfaware.tools.experiments.spielcode_rufen import Rufer

# Funktionen im Spiel
F_PUNKTE, F_PREIS = 0x0044a830, 0x004588f0
F_MAUERZAHL, F_ANWERBBAR, F_LEITER = 0x00457e80, 0x00464da0, 0x00465080
F_REPARATUR, F_MAPPER = 0x00410320, 0x004bb010
F_MAUERFELD, F_MAUERWEG, F_ERLAUBT, F_BAUPLATZ = 0x004f94a0, 0x005029d0, 0x004f9a60, 0x005037b0
F_MAUERKOSTEN, F_WAREN, F_BLOCKADE, F_ENTLASSEN = 0x0041c190, 0x00530d70, 0x0053a150, 0x004591f0
F_ABGABE, F_TUNNEL, F_TUNNELSUCHE, F_ESSEN_SPERRE = 0x0040c800, 0x00537700, 0x0049b5b0, 0x0043fbb0
GOLD_LEITER = 0x00df3358  # DAT_EnoughGoldForRequestedUnit: aus dem Maschinencode von F_LEITER gelesen

ARBEITER = (3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 31, 32, 33, 34, 36)  # die Arten aus dem switch von despawnPeasantOrWorker
ULS_REMOVE, US_DISAPPEAR = 3, 110
MAPPER_TUNNEL = 66
FARMEN = {"Weizen": 70, "Hopfen": 71, "Apfel": 72, "Vieh": 73}
WARE = {"Holz": 2, "Hopfen": 3, "Stein": 4, "Eisen": 6, "Pech": 7, "Teilpech": 8, "Brot": 10, "Kaese": 11, "Fleisch": 12, "Apfel": 13, "Bier": 14, "Gold": 15, "Mehl": 16, "Bogen": 17, "Armbrust": 18, "Speer": 19, "Pike": 20, "Keule": 21, "Schwert": 22, "Leder": 23, "Ruestung": 24}
ZIEL_DATEI = os.path.join("data", "research", "auge_plan", "lauf_s_20261103", "rufen_{}.json")


class Messung:
    def __init__(self, l, r, karte):
        self.l, self.s, self.k, self.r, self.K = l, l.s, l.k, r, karte
        self.G = karte.struktur("DAT_GameState")[0]
        self.B = karte.struktur("DAT_BuildingsState")[0]
        self.U = karte.struktur("DAT_UnitsState")[0]
        self.TM = karte.struktur("DAT_TileMapState")[0]
        self.PF = karte.struktur("DAT_PathFindingState")[0]
        self.MP = karte.struktur("DAT_MapPropertiesState")[0]
        self.AIC = karte.struktur("DAT_AICState")[0]  # thiscall: Die Funktion rechnet mit ECX, auch wenn der Export es nicht zeigt (Absturz bei 0x4CB2C2 ohne Zeiger)
        self.AIV = karte.struktur("DAT_AIVState")[0]
        self.aus = {}
        self.datei = ZIEL_DATEI.format(time.strftime("%Y%m%d_%H%M%S"))

    # Felder lesen und setzen. n = Spieler, Gebaeude oder Einheit
    def adr(self, g, f, n=0, i=0):
        a, gr, sch, _ = self.K.adresse(g, f)
        return a + n * sch + i, gr

    def p(self, f, n, i=0):
        a, gr = self.adr("DAT_GameState", f"playerDataArray[].{f}", n, i)
        return self.r.lies_i(a, gr)

    def p_setze(self, f, n, wert, i=0):
        a, gr = self.adr("DAT_GameState", f"playerDataArray[].{f}", n, i)
        self.r.setze_i(a, wert, gr)

    def ware(self, n, w):
        return self.p("currentResources[]", n, 4 * WARE[w])

    def ware_setze(self, n, w, wert):
        self.p_setze("currentResources[]", n, wert, 4 * WARE[w])

    def b(self, f, n):
        a, gr = self.adr("DAT_BuildingsState", f"buildings[].{f}", n)
        return self.r.lies_i(a, gr)

    def b_setze(self, f, n, wert):
        a, gr = self.adr("DAT_BuildingsState", f"buildings[].{f}", n)
        self.r.setze_i(a, wert, gr)

    def u(self, f, n):
        a, gr = self.adr("DAT_UnitsState", f"units[].{f}", n)
        return self.r.lies_i(a, gr)

    def u_setze(self, f, n, wert):
        a, gr = self.adr("DAT_UnitsState", f"units[].{f}", n)
        self.r.setze_i(a, wert, gr)

    def tm(self, f):
        a, gr = self.adr("DAT_TileMapState", f)
        return self.r.lies_i(a, gr)

    def tm_setze(self, f, wert):
        a, gr = self.adr("DAT_TileMapState", f)
        self.r.setze_i(a, wert, gr)

    def ebene(self, f, kachel):
        a, gr, sch, _ = self.K.adresse("DAT_TileMapState", f"{f}[]")
        return a + kachel * (sch or gr), (sch or gr)

    def takte(self, n, *befehle):
        if befehle:
            self.k.liste(list(befehle), lf.KANAL)
        lk.aufnahme_im_stand_ohne(self.l, lf.TEMPO_JEDER_TAKT)
        self.l.warte_takte(n)
        lk.anhalten(self.l)

    def probe(self, name, f, *a, **kw):
        anfang = time.perf_counter()
        try:
            e = f(*a, **kw)
        except Exception as x:  # eine kaputte Probe darf die anderen nicht aufhalten, der Fehler steht im Ergebnis
            e = {"fehler": repr(x)}
        self.aus[name] = {"ergebnis": e, "dauer_s": round(time.perf_counter() - anfang, 2), "takt": self.s.takt()}
        with open(self.datei, "w", encoding="utf-8") as d:
            json.dump(self.aus, d, ensure_ascii=False, indent=0, default=str)
        print(f"PROBE {name}: {json.dumps(e, ensure_ascii=False, default=str)[:600]}", flush=True)

    # Die Proben
    def p138_mauerzahl(self):
        """Erwartet: Stein 20 gibt 40 Felder, mit angebrochenem Stueck 39, Holz genauso, Decke 250."""
        alt = (self.ware(1, "Stein"), self.ware(1, "Holz"), self.p("partialStoneCounter", 1), self.p("partialWoodCounter", 1))
        z = []
        for st, teil in ((20, 0), (20, 1), (0, 0), (1, 0), (1, 1), (125, 0), (126, 0), (500, 0)):
            self.ware_setze(1, "Stein", st)
            self.p_setze("partialStoneCounter", 1, teil)
            z.append(("Stein", st, teil, self.r.rufe(F_MAUERZAHL, 1, 4, this=self.G)))
        self.ware_setze(1, "Holz", 20)
        self.p_setze("partialWoodCounter", 1, 0)
        z.append(("Holz", 20, 0, self.r.rufe(F_MAUERZAHL, 1, 2, this=self.G)))
        self.p_setze("partialWoodCounter", 1, 1)
        z.append(("Holz", 20, 1, self.r.rufe(F_MAUERZAHL, 1, 2, this=self.G)))
        z.append(("anderes Material", 20, 0, self.r.rufe(F_MAUERZAHL, 1, 9, this=self.G)))
        self.ware_setze(1, "Stein", alt[0])
        self.ware_setze(1, "Holz", alt[1])
        self.p_setze("partialStoneCounter", 1, alt[2])
        self.p_setze("partialWoodCounter", 1, alt[3])
        return z

    def p135_punkte(self):
        """Erwartet: Rueckgabe gleich der Formel, gerechnet aus Bestand, Preisen, Bevoelkerung und Truppenwert. Gegenprobe: 1000 Gold mehr gibt 100 Punkte mehr."""
        je = {}
        grund = [2, 3, 4, 6, 8, 14, 16]
        waffen = [17, 18, 19, 20, 21, 22, 23, 24]
        essen = [10, 11, 12, 13]
        for n in range(1, 9):
            w = [self.p("currentResources[]", n, 4 * i) for i in range(26)]
            pr = {i: self.r.rufe(F_PREIS, i, this=self.G) for i in grund + waffen + essen}
            f = (sum(pr[i] * w[i] for i in grund)) // 10 + self.p("currentPopulation", n) * 10 + (sum(pr[i] * w[i] for i in waffen)) // 10 + (sum(pr[i] * w[i] for i in essen)) // 10 + self.p("totalTroopValue", n) + w[15] // 10
            je[n] = (self.r.rufe(F_PUNKTE, n), f)
        g = self.ware(1, "Gold")
        vorher = self.r.rufe(F_PUNKTE, 1)
        self.ware_setze(1, "Gold", g + 1000)
        nachher = self.r.rufe(F_PUNKTE, 1)
        self.ware_setze(1, "Gold", g)
        return {"je_spieler (Rueckgabe, Formel)": je, "alle_gleich": all(a == b for a, b in je.values()), "1000 Gold mehr": nachher - vorher}

    def p100_reparatur(self, nr):
        """Erwartet: voll: Rueckgabe 0. Sonst (max-akt)*Baukosten/max, mindestens 1."""
        ma, ak = self.b("maxHealth", nr), self.b("currentHealth", nr)
        z = []
        for h in (ma, ma - 1, ma // 2, ma // 4, 1):
            self.b_setze("currentHealth", nr, h)
            self.r.setze_i(self.adr("DAT_BuildingsState", "INT_SelectedBuildingStoneRepairCost")[0], -7)
            self.r.setze_i(self.adr("DAT_BuildingsState", "INT_SelectedBuildingStoneWoodCost")[0], -7)
            rueck = self.r.rufe(F_REPARATUR, nr, this=self.B)
            z.append({"leben": h, "rueckgabe": rueck, "stein": self.r.lies_i(self.adr("DAT_BuildingsState", "INT_SelectedBuildingStoneRepairCost")[0]), "holz": self.r.lies_i(self.adr("DAT_BuildingsState", "INT_SelectedBuildingStoneWoodCost")[0])})
        self.b_setze("currentHealth", nr, ak)
        return {"max": ma, "typ": self.b("buildingType", nr), "faelle": z}

    def p154_anwerbbar(self):
        """Erwartet: 3 (MAX_ARMY), sobald Heer plus count_2 das Limit erreicht. Die Zahlen des Rueckgabewerts: 0 kann nicht, 1 kann, 2 nicht erlaubt, 3 Heer voll, 4 kein Bauer, 5 kein Gold, 6 keine Waffe."""
        limit = self.K.adresse("DAT_GameState", "mapAndTime.armySizeLimit")[0]
        heer, zwei, gold, speer = self.p("armySize", 1), self.p("count_2", 1), self.ware(1, "Gold"), self.ware(1, "Speer")
        grenze = self.r.lies_i(limit)
        z = {"limit": grenze, "armySize": heer, "count_2": zwei, "slot": self.r.lies_i(self.K.adresse("DAT_GameSynchronyState", "currentPlayerSlotID")[0])}
        self.ware_setze(1, "Gold", 500)
        self.ware_setze(1, "Speer", 5)
        z["normal"] = self.r.rufe(F_ANWERBBAR, 24)
        self.p_setze("armySize", 1, grenze - zwei - 1)
        z["ein Platz frei"] = self.r.rufe(F_ANWERBBAR, 24)
        self.p_setze("armySize", 1, grenze - zwei)
        z["am Limit"] = self.r.rufe(F_ANWERBBAR, 24)
        self.p_setze("armySize", 1, heer)
        self.ware_setze(1, "Gold", 0)
        z["ohne Gold"] = self.r.rufe(F_ANWERBBAR, 24)
        self.ware_setze(1, "Gold", 500)
        self.ware_setze(1, "Speer", 0)
        z["ohne Speer"] = self.r.rufe(F_ANWERBBAR, 24)
        self.ware_setze(1, "Gold", gold)
        self.ware_setze(1, "Speer", speer)
        return z

    def limit_haelt(self):
        """In sonder19_g blieb 1.160 in der Aufzeichnung. Haelt das Feld einen gesetzten Wert? Sofort lesen und nach 3 Takten."""
        a = self.K.adresse("DAT_GameState", "mapAndTime.armySizeLimit")[0]
        alt = self.r.lies_i(a)
        self.r.setze_i(a, 7)
        sofort = self.r.lies_i(a)
        self.takte(3)
        spaeter = self.r.lies_i(a)
        self.r.setze_i(a, alt)
        return {"alt": alt, "sofort": sofort, "nach 3 Takten": spaeter}

    def p155_anwerben(self, kaserne):
        """Erwartet: Bei Heer am Limit kein neuer Soldat, Gold bleibt. Gegenprobe davor: Es geht. Das Heer wird knapp davor gesetzt, wirkt es nicht, ist die Probe ohne Aussage."""
        def zahl():
            return sum(1 for e in self.s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] == 24)
        def versuch():
            return [{"player": 1, "ware": {"typ": WARE["Speer"], "menge": 5}}, {"player": 1, "ware": {"typ": WARE["Gold"], "menge": 500}}, {"player": 1, "werbe": {"typ": 24, "gebaeude": kaserne}}]
        grenze = self.r.lies_i(self.K.adresse("DAT_GameState", "mapAndTime.armySizeLimit")[0])
        a = zahl()
        self.takte(6, *versuch())
        aus = {"Gegenprobe: neue Soldaten": zahl() - a, "Gold nachher": self.ware(1, "Gold"), "armySize": self.p("armySize", 1), "count_2": self.p("count_2", 1), "limit": grenze}
        a = zahl()
        heer = self.p("armySize", 1)
        cmds = versuch()
        self.p_setze("armySize", 1, grenze)
        self.k.liste(cmds, lf.KANAL)
        lk.aufnahme_im_stand_ohne(self.l, lf.TEMPO_JEDER_TAKT)
        self.l.warte_takte(1)
        lk.anhalten(self.l)
        aus["armySize nach einem Takt"] = self.p("armySize", 1)
        self.takte(5)
        aus["am Limit: neue Soldaten"] = zahl() - a
        aus["am Limit: Gold nachher"] = self.ware(1, "Gold")
        aus["armySize am Ende"] = self.p("armySize", 1)
        aus["armySize davor"] = heer
        return aus

    def p156_leiter(self, gilde):
        """Erwartet laut Export: 0 bei 3 Gold, 1 bei 4. Die Liga verlangt 20: Der echte Befehl zeigt, was gilt."""
        g = self.ware(1, "Gold")
        z = {}
        for wert in (3, 4, 19, 20):
            self.ware_setze(1, "Gold", wert)
            self.r.rufe(F_LEITER)
            z[f"Pruefung bei {wert} Gold"] = self.r.lies_i(GOLD_LEITER)
        def leiter():
            return sum(1 for e in self.s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] == 29)
        for wert in (3, 4, 19, 20, 21):
            self.ware_setze(1, "Gold", wert)
            a = leiter()
            self.takte(5, {"player": 1, "werbe": {"typ": 29, "gebaeude": gilde}})
            z[f"Befehl bei {wert} Gold: neue Traeger, Gold danach"] = (leiter() - a, self.ware(1, "Gold"))
        self.ware_setze(1, "Gold", g)
        return z

    def p180_verfuegbar(self):
        """Erwartet: Jaeger nicht moeglich, wenn das Wild 0 ist. Hunde im Gefecht frei."""
        hirsche = self.K.adresse("DAT_GameState", "mapAndTime.rawDeerCount")[0]
        hunde = self.K.adresse("DAT_GameState", "mapAndTime.noDogs")[0]
        alt_h, alt_d = self.r.lies_i(hirsche), self.r.lies_i(hunde)
        z = {"Wild": alt_h, "Jaeger jetzt": self.r.rufe(F_MAPPER, 78, this=self.MP)}
        self.r.setze_i(hirsche, 0)
        z["Jaeger bei Wild 0"] = self.r.rufe(F_MAPPER, 78, this=self.MP)
        self.r.setze_i(hirsche, max(alt_h, 5))
        z["Jaeger bei Wild 5"] = self.r.rufe(F_MAPPER, 78, this=self.MP)
        self.r.setze_i(hirsche, alt_h)
        z["noDogs"] = alt_d
        z["Hundekaefig"] = self.r.rufe(F_MAPPER, 312, this=self.MP)
        self.r.setze_i(hunde, 1)
        z["Hundekaefig bei noDogs 1"] = self.r.rufe(F_MAPPER, 312, this=self.MP)
        self.r.setze_i(hunde, alt_d)
        return z

    def p192_p199_feind(self, ziel):
        """Erwartet: Mauerfeld 4 Felder vom Feindgebaeude: verboten. Weg bis dicht ans Feindgebaeude: verboten mit Grund 0x13, Radius vermutlich 7."""
        frei = self.s.raster()[0]
        tx, ty = ziel["x"], ziel["y"]
        z = {"ziel": ziel, "feld": {}, "weg": {}}
        for richtung, (dx, dy) in {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}.items():
            a, b = [], []
            for d in range(1, 16):
                x, y = tx + dx * d, ty + dy * d
                if not (0 <= x < 400 and 0 <= y < 400) or not frei[y, x]:
                    continue
                self.r.rufe(F_MAUERFELD, 1, x, y, 25, this=self.TM)
                a.append((d, self.tm("illegalBuild")))
                self.r.rufe(F_MAUERWEG, 1, x + dx * 22, y + dy * 22, x, y, 0x19, this=self.TM)
                b.append((d, self.tm("illegalBuild"), self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason")))
            z["feld"][richtung] = a
            z["weg"][richtung] = b
        return z

    def p193_hoehe(self, x, y):
        """Erwartet: Ueber der Hoehengrenze sagt die Warnung 1 Vieh, 2 Apfel, 3 Hopfen, 4 Weizen."""
        t = self.s.kachel(x, y)
        a, g = self.ebene("HeightLayer", t)
        alt_h, alt_g = self.r.lies_i(a, g), self.tm("buildingHeightLimit")
        z = {"hoehe": alt_h, "grenze": alt_g}
        self.tm_setze("buildingHeightLimit", alt_h - 1)
        for n, m in FARMEN.items():
            self.tm_setze("placementWarning", 0)
            z[n + " zu hoch"] = (self.r.rufe(F_ERLAUBT, t, 1, m, 0, this=self.TM), self.tm("placementWarning"))
        self.tm_setze("buildingHeightLimit", alt_h)
        for n, m in FARMEN.items():
            self.tm_setze("placementWarning", 0)
            z[n + " genau an der Grenze"] = (self.r.rufe(F_ERLAUBT, t, 1, m, 0, this=self.TM), self.tm("placementWarning"))
        self.tm_setze("buildingHeightLimit", alt_g)
        return z

    def p201_bauplatz(self, turm_mapper, turm_b):
        """Erwartet: Turm erlaubt bis Achsenabstand 50 zum Eingang, bei 51 Grund 0x12. 11. Kaefig: Grund 1000. Farm auf zu wenig fruchtbarem Boden: Grund 0x17 (Checkliste) oder 0x16 (Export)."""
        frei = self.s.raster()[0]
        keep = self.p("keep.id", 1)
        kx, ky = self.b("x", keep), self.b("y", keep)
        z = {"burg": (keep, kx, ky), "lager": (self.p("campground.id", 1),)}
        for richtung, (dx, dy) in {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}.items():
            rei = []
            for d in range(8, 75):
                x, y = kx + dx * d, ky + dy * d
                if not (0 <= x < 400 and 0 <= y < 400) or not frei[y, x]:
                    continue
                self.tm_setze("buildingPlacementFailReason", 0)
                self.r.rufe(F_BAUPLATZ, 1, x, y, turm_mapper, turm_b, this=self.TM)
                w = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
                if not rei or rei[-1][1:] != w:
                    rei.append((d,) + w)
            z["Turm " + richtung + " (Abstand, Fehler, Grund), nur Wechsel"] = rei
        # Kaefig: an einer Stelle, die fuer Kaefige geht
        ort = next(((kx + dx * d, ky + dy * d) for d in range(10, 40) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if frei[ky + dy * d, kx + dx * d]), None)
        alt = self.p("dogCageCount", 1)
        for wert in (0, 9, 10, 11):
            self.p_setze("dogCageCount", 1, wert)
            self.tm_setze("buildingPlacementFailReason", 0)
            self.r.rufe(F_BAUPLATZ, 1, ort[0], ort[1], 312, 3, this=self.TM)
            z[f"Kaefige {wert}"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        self.p_setze("dogCageCount", 1, alt)
        # Farm: Raster ueber die Karte, Haeufigkeit der Gruende, und je Grund ein Beispiel
        for n, m, b in (("Weizen", 70, 9), ("Apfel", 72, 10)):
            c, bei = collections.Counter(), {}
            for y in range(20, 380, 8):
                for x in range(20, 380, 8):
                    if not frei[y, x] or abs(x - y) > 195 or abs(x + y - 399) > 195:
                        continue
                    self.tm_setze("buildingPlacementFailReason", 0)
                    self.tm_setze("placementWarning", 0)
                    self.r.rufe(F_BAUPLATZ, 1, x, y, m, b, this=self.TM)
                    w = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"), self.tm("placementWarning"))
                    c[w] += 1
                    bei.setdefault(w, (x, y))
            z[f"Farm {n} (Fehler, Grund, Warnung): Anzahl, Beispiel"] = [(str(k), v, bei[k]) for k, v in c.most_common()]
        return z

    def p119_mauerkosten(self):
        """Erwartet laut Export: (nieder + 2 mal hoch + Rest) / 4. 8 niedere: 2 Stein. Lauf F sah je 13 Felder -1 und -3."""
        alt = self.p("partialStoneCounter", 1)
        st = self.ware(1, "Stein")
        z = {}
        self.ware_setze(1, "Stein", 500)
        for hoch, nieder in ((0, 8), (8, 0), (0, 13), (13, 0), (1, 0), (0, 1), (0, 3), (0, 4), (2, 0)):
            self.p_setze("partialStoneCounter", 1, 0)
            self.tm_setze("wallPlacementCost", -1)
            self.r.rufe(F_MAUERKOSTEN, 1, hoch, nieder, 1, this=self.B)
            z[f"hoch {hoch}, nieder {nieder}"] = self.tm("wallPlacementCost")
        self.p_setze("partialStoneCounter", 1, 3)
        self.r.rufe(F_MAUERKOSTEN, 1, 0, 1, 1, this=self.B)
        z["nieder 1 mit Rest 3"] = self.tm("wallPlacementCost")
        self.p_setze("partialStoneCounter", 1, alt)
        self.ware_setze(1, "Stein", st)
        return z

    def p213_waren(self, einheit):
        """Erwartet: Bei Produktivitaet 120 geben 10 Durchgaenge je 1 Ware 12 Stueck. Unter 100 bleibt es 10. boost: +50 im Gefecht."""
        alt = self.p("fearFactorProductivityUnk", 1)
        z = {}
        for ff in (60, 92, 100, 116, 120, 132, 148, 180):
            for boost in (0, 1):
                self.p_setze("fearFactorProductivityUnk", 1, ff)
                self.u_setze("productivityMod100", einheit, 0)
                self.u_setze("productivityDiv100", einheit, 0)
                z[f"ff {ff} boost {boost}"] = [self.r.rufe(F_WAREN, einheit, 1, boost) for _ in range(10)]
        self.p_setze("fearFactorProductivityUnk", 1, alt)
        self.u_setze("productivityMod100", einheit, 0)
        return {k: (sum(v), v[:4]) for k, v in z.items()}

    def p215_blockade(self, leute):
        """Erwartet: Schmied wartet: 0x38. Hier die ganze Tafel: je Arbeiterart die Zustaende, in denen die Funktion einen Grund meldet."""
        t = {}
        for e in leute:
            alt = self.u("state", e["nr"])
            z = {}
            for st in range(0, 130):
                self.u_setze("state", e["nr"], st)
                w = self.r.rufe(F_BLOCKADE, e["nr"], this=self.U)
                if w:
                    z[st] = w
            self.u_setze("state", e["nr"], alt)
            t[e["typ"]] = z
        return t

    def p147_entlassen(self, leute):
        """Erwartet: Heiler vor Priester vor Wirt. Jeder Aufruf waehlt einen, er wird danach aus der Wahl genommen, das Spiel bleibt stehen."""
        folge = []
        bauern = [e for e in self.s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] == 1]
        for e in bauern:
            self.u_setze("logicalState", e["nr"], ULS_REMOVE)
        vorher = {e["nr"]: self.u("state", e["nr"]) for e in leute}
        for _ in range(len(leute) + 2):
            self.r.rufe(F_ENTLASSEN, 1, this=self.G)
            neu = [e for e in leute if self.u("state", e["nr"]) == US_DISAPPEAR and vorher[e["nr"]] != US_DISAPPEAR]
            if not neu:
                folge.append("keiner")
                break
            for e in neu:
                folge.append(e["typ"])
                vorher[e["nr"]] = US_DISAPPEAR
                self.u_setze("logicalState", e["nr"], ULS_REMOVE)
        return {"bauern_vorher": len(bauern), "folge_der_arten": folge}

    def p092_abgabe(self):
        """Erwartet: Bogenschuetze 12. Die Tafel der Preise fuer jede Art, die die Funktion kennt. Geld gibt es laut Code nur in Siege That."""
        out = self.r.speicher + 0x900
        z = {}
        for t in range(1, 90):
            self.r.setze_i(out, -1)
            self.r.rufe(F_ABGABE, t, out, this=self.B)
            w = self.r.lies_i(out)
            if w != -1:
                z[t] = w
        return z

    def p214_ohne_ziel(self, nr):
        """Erwartet: Ohne Ziel zaehlt tunnelerCounter 0 bis 5, dann -1, Rueckgabe 0. Ein Bauplatz ohne Ziel schlaegt fehl. Laeuft, solange kein Feindturm steht."""
        x, y = self.b("x", nr), self.b("y", nr)
        z = {"gebaeude": (nr, self.b("buildingType", nr), x, y), "zaehler": []}
        for _ in range(8):
            w = self.r.rufe(F_TUNNEL, nr, 0, this=self.U)
            z["zaehler"].append((w, self.b("tunnelerCounter", nr), self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])))
        self.b_setze("tunnelerCounter", nr, 0)
        for d in (20, 40, 80, 150):
            self.r.rufe(F_TUNNELSUCHE, 1, 0, d, x, y - 1, this=self.PF)
            z[f"Suche {d} Felder"] = tuple(self.r.lies_i(self.K.adresse("DAT_PathFindingState", n)[0]) for n in ("ALG_TargetTile", "ALG_TargetX", "ALG_TargetY"))
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, x + 8, y, MAPPER_TUNNEL, 3, this=self.TM)
        z["Bauplatz 8 Felder daneben"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        return z

    def p177_mit_ziel(self, nr, turm):
        """Erwartet: Mit Feindturm in Reichweite findet die Suche ihn, der Zaehler springt auf -1, und der Bauplatz daneben geht."""
        x, y = self.b("x", nr), self.b("y", nr)
        tx, ty = self.b("x", turm), self.b("y", turm)
        z = {"tunnel": (x, y), "turm": (turm, self.b("buildingType", turm), self.b("owner", turm), tx, ty)}
        for d in (20, 40, 80, 150):
            self.r.rufe(F_TUNNELSUCHE, 1, 0, d, x, y - 1, this=self.PF)
            t = self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])
            z[f"Suche {d} Felder"] = (t, self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetX")[0]), self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetY")[0]), self.r.lies_i(self.ebene("LogicLayer", t)[0]) if t else None, self.r.lies_i(*self.ebene("BuildingLayer", t)) if t else None)
        self.b_setze("tunnelerCounter", nr, 0)
        z["Zaehler"] = []
        for _ in range(7):
            w = self.r.rufe(F_TUNNEL, nr, 0, this=self.U)
            z["Zaehler"].append((w, self.b("tunnelerCounter", nr)))
        frei = self.s.raster()[0]
        for d in (8, 12, 18, 30, 45, 60):
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                qx, qy = tx + dx * d, ty + dy * d
                if 0 <= qx < 400 and 0 <= qy < 400 and frei[qy, qx]:
                    self.tm_setze("buildingPlacementFailReason", 0)
                    self.r.rufe(F_BAUPLATZ, 1, qx, qy, MAPPER_TUNNEL, 3, this=self.TM)
                    z[f"Bauplatz {d} Felder vom Turm"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"), (qx, qy))
                    break
        return z

    def p109_essen(self):
        """Erwartet: Essensart sperren: totalFood und der Zaehler der Art sinken um den Bestand, die Kornkammer behaelt die Ware. 0 Brot, 1 Kaese, 2 Fleisch, 3 Aepfel."""
        lager = self.p("granaryIsAlmostFilledUp", 1) if False else None
        kammern = [g["nr"] for g in self.s.gebaeude(1) if g["typ"] == 19]
        def stand():
            return {"totalFood": self.p("totalFood", 1), "Brot": self.p("breadCount", 1), "Kaese": self.p("cheeseCount", 1), "Fleisch": self.p("meatCount", 1), "Apfel": self.p("appleCount", 1), "Kammer": [(self.b("resourceBread", k), self.b("resourceCheese", k), self.b("resourceMeat", k), self.b("resourceApple", k)) for k in kammern][:2], "bann": [self.p("isFoodTypeBanned[]", 1, 2 * i) for i in range(4)]}
        z = {"kammern": kammern, "vorher": stand()}
        for art in (0, 3):
            self.r.rufe(F_ESSEN_SPERRE, art)
            z[f"sofort nach Sperre {art}"] = stand()
            self.takte(4)
            z[f"nach Sperre {art}, 4 Takte"] = stand()
            self.r.rufe(F_ESSEN_SPERRE, art)
            self.takte(4)
            z[f"frei {art}, 4 Takte"] = stand()
        return z

    def p171_turmgeraet(self, turm_a, turm_b):
        """Erwartet: Mangonel und Balliste auf dem Turm per Befehl 42 setzen, per Befehl 75 (Art 2) entfernen. Zuwachs gleich den Baukosten?"""
        z = {}
        for name, art, turm in (("Mangonel", 41, turm_a), ("Balliste", 61, turm_b)):
            x, y = self.b("x", turm), self.b("y", turm)
            for w in ("Gold", "Holz", "Stein"):
                self.ware_setze(1, w, 300)
            vorher = {w: self.ware(1, w) for w in ("Gold", "Holz", "Stein")}
            bekannt = {e["nr"] for e in self.s.einheiten_alle()}
            self.takte(3, {"player": 1, "spielbefehl": {"nr": 42, "werte": [x * 8 + 4, y * 8 + 4, 0, art]}})
            neu = [e for e in self.s.einheiten_alle() if e["nr"] not in bekannt and e["typ"] == art]
            nach_bau = {w: self.ware(1, w) for w in vorher}
            z[name] = {"neu": [(e["nr"], e["x"], e["y"]) for e in neu], "Bau kostet": {w: vorher[w] - nach_bau[w] for w in vorher}, "Turm hat Geraet": self.b("containsSiegeMangonel1OrBallista2", turm)}
            if neu:
                self.takte(3, {"player": 1, "spielbefehl": {"nr": 75, "werte": [2, neu[0]["nr"]]}})
                nach = {w: self.ware(1, w) for w in vorher}
                z[name]["Entfernen gibt"] = {w: nach[w] - nach_bau[w] for w in vorher}
                z[name]["Turm hat Geraet danach"] = self.b("containsSiegeMangonel1OrBallista2", turm)
                z[name]["noch da"] = any(e["nr"] == neu[0]["nr"] for e in self.s.einheiten_alle())
        return z

    def p209_platzieren(self, x, y, opfer_nr):
        """Erwartet: Erste Huette mit weniger Holz als ihr Preis: Holz bleibt, Feld 0x288 der Huette = 1. Gebaeude auf Feld mit eigener Einheit: vermutlich verschwindet die Einheit."""
        from selfaware.game.ucp.bauen import NACH_TYP
        h = next(v for v in NACH_TYP.values() if "WOODCUT" in str(v.get("laufzeitName")).upper())
        z = {"mapper": h["mapper"], "groesse": h["b"], "huetten_vorher": [g["nr"] for g in self.s.gebaeude(1) if g["typ"] == 2 or "WOOD" in str(g.get("name", ""))]}
        self.ware_setze(1, "Holz", 0)
        vor = {g["nr"] for g in self.s.gebaeude(1)}
        self.takte(3, {"player": 1, "ware": {"typ": 2, "menge": 0}}, {"player": 1, "baue": {"mapper": h["mapper"], "x": x, "y": y, "groesse": h["b"], "richtung": 0}})
        neu = [g for g in self.s.gebaeude(1) if g["nr"] not in vor]
        z["neu"] = [(g["nr"], g["typ"], g["x"], g["y"]) for g in neu]
        z["Holz danach"] = self.ware(1, "Holz")
        if neu:
            z["Feld 0x288"] = self.b("field230_0x288", neu[0]["nr"])
        # zweite Lage: ein eigener Speertraeger steht auf dem Bauplatz
        opfer = next(e for e in self.s.einheiten_alle() if e["nr"] == opfer_nr)
        ux, uy = opfer["x"], opfer["y"]
        z["opfer"] = (opfer["nr"], ux, uy)
        self.ware_setze(1, "Holz", 50)
        vor = {g["nr"] for g in self.s.gebaeude(1)}
        self.takte(3, {"player": 1, "ware": {"typ": 2, "menge": 50}}, {"player": 1, "baue": {"mapper": h["mapper"], "x": ux - 1, "y": uy - 1, "groesse": h["b"], "richtung": 0}})
        neu = [g for g in self.s.gebaeude(1) if g["nr"] not in vor]
        z["auf der Einheit neu"] = [(g["nr"], g["typ"], g["x"], g["y"]) for g in neu]
        noch = next((e for e in self.s.einheiten_alle() if e["nr"] == opfer["nr"]), None)
        z["Einheit danach"] = noch and (noch["x"], noch["y"], self.u("logicalState", opfer["nr"]), self.u("state", opfer["nr"]))
        return z

    def p059_sumpf(self, x, y):
        """Erwartet: Sumpffeld am Rand: MacroLayer & 0x3f = 1. Mit 8 Sumpf-Nachbarn: 2, 4, 8 oder 0x10. Gesetzt per Spielbefehl 21 mit Bit 0x20000000. Der dritte Wert ist die Pinselgroesse: Nur der Graben setzt sie selbst (setTerrain), mit 0 geschieht sonst nichts (Lauf 20:27)."""
        befehle = [{"player": 1, "spielbefehl": {"nr": 21, "werte": [x + i, y + j, 1, 0x20000000, 0]}} for i in range(7) for j in range(7)]
        vorher = [[self.r.lies_i(*self.ebene("MacroLayer", self.s.kachel(x + i, y + j))) & 0x3f for i in range(-1, 8)] for j in range(-1, 8)]
        self.takte(10, *befehle)
        self.tm_setze("forceUpdateMacroLayerFlag", 1)
        self.takte(60)
        z = {}
        reihen = []
        for j in range(-1, 8):
            r = []
            for i in range(-1, 8):
                t = self.s.kachel(x + i, y + j)
                lo = self.r.lies_i(self.ebene("LogicLayer", t)[0])
                a, g = self.ebene("MacroLayer", t)
                r.append(("S" if lo & 0x20000000 else "-", self.r.lies_i(a, g) & 0x3f))
            reihen.append(r)
        z["vorher MacroLayer & 0x3f"] = vorher
        z["reihen (Sumpfbit, MacroLayer & 0x3f)"] = reihen
        return z

    def p197_graben(self, x, y):
        """Erwartet: someCountDown sinkt um 1 je Aufruf, nie unter 0. Das Feld bleibt sonst 0, darum wird es gesetzt."""
        self.takte(5, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x, y, 0, 0x40000000, 0]}})
        anzahl = self.tm("currentMoatCount")
        a, gr, sch, _ = self.K.adresse("DAT_TileMapState", "moats[].someCountDown")
        z = {"graeben": anzahl, "werte": []}
        self.r.setze_i(a, 5, gr)
        for _ in range(12):
            z["werte"].append((self.s.takt(), self.r.lies_i(a, gr)))
            self.takte(1)
        return z

    def p221_kinder(self, x, y):
        """Erwartet: Muetter plus Kinder nie ueber 75. 90 Kinder gesetzt."""
        self.k.liste([{"setzeEinheit": {"spieler": 1, "typ": 64, "x": x, "y": y, "anzahl": 90}}], lf.KANAL)
        zahl = []
        for _ in range(8):
            self.takte(6)
            zahl.append((self.s.takt(), sum(1 for e in self.s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] in (63, 64))))
        return {"zahl": zahl, "someCount02": self.p("someCount02", 1), "someCount03": self.p("someCount03", 1)}

    def p102_pech(self, nr):
        """Erwartet: countPitchRigs = Zahl der Gruben, je Takt neu gezaehlt."""
        z = []
        for _ in range(6):
            self.takte(1)
            z.append((self.s.takt(), self.p("countPitchRigs", 1)))
        return {"grube": (nr, self.b("buildingType", nr)), "werte": z}

    def p179_taste(self):
        """Erwartet: Taste + auf dem Ziffernblock: von 20 auf 25, bei 90 bleibt 90, Taste - bei 20 bleibt 20. Geschickt als Fensternachricht, ohne Maus und ohne das Fenster nach vorn zu holen."""
        u32 = ctypes.WinDLL("user32")
        from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz
        pid = pid_der_instanz(2)
        fenster = []
        Rueck = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def jeder(h, _):
            p = ctypes.c_ulong()
            u32.GetWindowThreadProcessId(ctypes.c_void_p(h), ctypes.byref(p))
            if p.value == pid and u32.IsWindowVisible(ctypes.c_void_p(h)):
                fenster.append(h)
            return True
        u32.EnumWindows(Rueck(jeder), None)
        if not fenster:
            return {"fehler": "kein Fenster"}
        a, gr = self.adr("DAT_GameCore", "gameSpeedLevel")
        alt = self.r.lies_i(a, gr)
        z = {"vorher": alt, "fenster": len(fenster)}
        u32.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t)

        def taste(start, code):
            self.r.setze_i(a, start, gr)
            u32.PostMessageW(ctypes.c_void_p(fenster[0]), 0x100, code, 1)
            u32.PostMessageW(ctypes.c_void_p(fenster[0]), 0x101, code, 0xC0000001)
            time.sleep(0.4)
            return self.r.lies_i(a, gr)
        z["+ bei 20"] = taste(20, 0x6B)
        z["+ bei 88"] = taste(88, 0x6B)
        z["+ bei 90"] = taste(90, 0x6B)
        z["- bei 25"] = taste(25, 0x6D)
        z["- bei 20"] = taste(20, 0x6D)
        z["- bei 11"] = taste(11, 0x6D)
        self.r.setze_i(a, alt, gr)
        return z


def szene(l):
    """Aufbau, dann die Proben. Das Spiel steht bei jedem Aufruf."""
    from selfaware.game.ucp.bauen import NACH_TYP
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    k, s = l.k, l.s
    lk.anhalten(l)
    ls.starttruppen_abwarten(l)
    ls.abraeumen(l)
    s.fern = 0  # die Ringe um die Burgen gehoeren hier dazu: Burgbauten gehen im Gefecht nur dort
    frei = s.raster()[0]
    innen = ls.burgbereich(l)(frei)
    feind = ls.burgbereich(l, sp=2)(frei)
    orte = ls.packen(innen, [(8, 8), (10, 8), (10, 8), (8, 8), (30, 6), (8, 8), (14, 12), (8, 8), (4, 4), (10, 10)], rand=4)
    orte_f = ls.packen(feind, [(12, 12)], rand=4)
    if None in orte or None in orte_f:
        raise ls.Abbruch(f"Kein Platz: {orte} {orte_f}")
    (p_turm, p_kaserne, p_gilde, p_grube, p_a, p_b, p_gel, p_opfer, p_graben, weit) = orte
    (p_feind,) = orte_f
    g = {
        "turm_a": ls._g(74, p_turm[0] + 2, p_turm[1] + 2, spieler=1),
        "turm_b": ls._g(74, p_b[0] + 2, p_b[1] + 2, spieler=1),
        "kaserne": ls._g(9, p_kaserne[0] + 2, p_kaserne[1] + 1, spieler=1),
        "gilde": ls._g(24, p_gilde[0] + 2, p_gilde[1] + 1, spieler=1),
        "grube": ls._g(6, p_grube[0] + 2, p_grube[1] + 2, spieler=1),
        "feindturm": ls._g(74, p_feind[0] + 5, p_feind[1] + 5, spieler=2),
    }
    for z in g.values():
        o = ls.erlaubte_stelle(l, z)
        if o:
            z["x"], z["y"] = o
    feindturm = g.pop("feindturm")  # kommt erst nach der Tunnelsuche ohne Ziel
    rest = ls.gebaeude_setzen(l, list(g.values()))
    tunnel = {"spieler": 1, "typ": 50, "mapper": MAPPER_TUNNEL, "groesse": 3, "name": "BT_TUNNEL", "x": weit[0] + 3, "y": weit[1] + 3}
    rest_t = ls.gebaeude_setzen(l, [tunnel])
    leute = [ls._e("arbeiter", t, p_a[0] + i, p_a[1] + 1) for i, t in enumerate(ARBEITER)]
    opfer = ls._e("opfer", 24, p_opfer[0] + 4, p_opfer[1] + 4)
    ls.setzen(l, leute + [opfer])
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
    l.warte_takte(2)
    lk.anhalten(l)
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung(l, r, karte)
        m.aus["aufbau"] = {"gebaeude": {n: {a: z.get(a) for a in ("nr", "x", "y", "typ")} for n, z in g.items()}, "nicht_gesetzt": [z["name"] for z in rest + rest_t], "tunnel": {a: tunnel.get(a) for a in ("nr", "x", "y")}, "arbeiter_gesetzt": sum(1 for e in leute if "nr" in e), "opfer": opfer.get("nr"), "orte": {"gel": p_gel, "graben": p_graben, "opfer": p_opfer}}
        # Reihenfolge: erst was nur liest und nichts aendert, dann was Takte braucht
        m.probe("P138 Mauerzahl", m.p138_mauerzahl)
        m.probe("P135 Punkte", m.p135_punkte)
        if "nr" in g["turm_a"]:
            m.probe("P100 Reparaturkosten", m.p100_reparatur, g["turm_a"]["nr"])
        m.probe("P154 Anwerben erlaubt", m.p154_anwerbbar)
        m.probe("P180 Jaeger und Kaefig", m.p180_verfuegbar)
        if "nr" in tunnel:
            m.probe("P214 ohne Ziel", m.p214_ohne_ziel, tunnel["nr"])
        m.aus["aufbau"]["feindturm nicht gesetzt"] = [z["name"] for z in ls.gebaeude_setzen(l, [feindturm])]
        if "nr" in feindturm:
            m.aus["aufbau"]["feindturm"] = {a: feindturm.get(a) for a in ("nr", "x", "y", "typ")}
            m.probe("P192 P199 Mauer am Feind", m.p192_p199_feind, {"x": feindturm["x"], "y": feindturm["y"]})
            if "nr" in tunnel:
                m.probe("P177 mit Ziel", m.p177_mit_ziel, tunnel["nr"], feindturm["nr"])
        m.probe("P193 Farm zu hoch", m.p193_hoehe, p_gel[0] + 3, p_gel[1] + 3)
        m.probe("P201 Bauplatz", m.p201_bauplatz, NACH_TYP[74]["mapper"], NACH_TYP[74]["b"])
        m.probe("P119 Mauerkosten", m.p119_mauerkosten)
        erster = next((e for e in leute if "nr" in e), None)
        if erster:
            m.probe("P213 Warenmenge", m.p213_waren, erster["nr"])
        m.probe("P215 Blockade", m.p215_blockade, [e for e in leute if "nr" in e])
        m.probe("P092 Preise beim Entlassen", m.p092_abgabe)
        m.probe("P179 Taste", m.p179_taste)
        # ab hier laeuft das Spiel einzelne Takte
        m.probe("Limit haelt", m.limit_haelt)
        if "nr" in g["kaserne"]:
            m.probe("P155 Anwerben am Limit", m.p155_anwerben, g["kaserne"]["nr"])
        if "nr" in g["gilde"]:
            m.probe("P156 Leitertraeger", m.p156_leiter, g["gilde"]["nr"])
        m.probe("P109 Essen sperren", m.p109_essen)
        if "nr" in g["turm_a"] and "nr" in g["turm_b"]:
            m.probe("P171 Turmgeraet", m.p171_turmgeraet, g["turm_a"]["nr"], g["turm_b"]["nr"])
        if "nr" in opfer:
            m.probe("P209 Bauen ohne Holz", m.p209_platzieren, p_gel[0] + 10, p_gel[1] + 1, opfer["nr"])
        m.probe("P059 Sumpf", m.p059_sumpf, p_gel[0], p_gel[1] + 3)
        m.probe("P197 Graben", m.p197_graben, p_graben[0] + 1, p_graben[1] + 1)
        if "nr" in g["grube"]:
            m.probe("P102 Pechgrube", m.p102_pech, g["grube"]["nr"])
        m.probe("P221 Kinder", m.p221_kinder, p_opfer[0], p_opfer[1])
        frisch = [ls._e("arbeiter", t, p_a[0] + i, p_a[1] + 3) for i, t in enumerate(ARBEITER)]
        ls.setzen(l, frisch)
        m.probe("P147 Wer zuerst geht", m.p147_entlassen, [e for e in frisch if "nr" in e])
        return {"szene": "rufen_g", "datei": m.datei, "proben": len(m.aus)}


class Messung2(Messung):
    """Zweite Runde: die Proben, deren Aufbau in der ersten nicht ging oder deren Frage genauer wurde."""

    def bau_ohne_pruefung(self, z):
        """placeBuilding prueft nur, wenn TM.field122_0x554930 0 ist. Fuer Lagen, die eine Karte brauchen, die hier fehlt (Pech, Eisen). Das Spiel setzt das Feld danach selbst zurueck."""
        from selfaware.tools.experiments import auge_lauf_s as ls
        self.tm_setze("field122_0x554930", 1)
        rest = ls.gebaeude_setzen(self.l, [z])
        return not rest, self.tm("field122_0x554930")

    def p201_reichweite(self, turm_mapper, turm_b):
        """Erwartet: 160 Karte 45, 200 Karte 50, 300 Karte 60, sonst 70. Fehler 0x12 ab einem Feld mehr, in allen 4 Richtungen, gemessen um einen Bezugspunkt."""
        frei = self.s.raster()[0]
        keep = self.p("keep.id", 1)
        kx, ky = self.b("x", keep), self.b("y", keep)
        alt = self.tm("mapSize")
        z = {"burg": (kx, ky), "karte": alt}
        for g in (160, 200, 300, 400):
            self.tm_setze("mapSize", g)
            je = {"Rueckgabe": self.r.rufe(0x004fbc30, this=self.TM)}
            for richtung, (dx, dy) in {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}.items():
                erster = None
                for d in range(10, 110):
                    x, y = kx + dx * d, ky + dy * d
                    if not (0 <= x < 400 and 0 <= y < 400):
                        break
                    self.tm_setze("buildingPlacementFailReason", 0)
                    self.r.rufe(F_BAUPLATZ, 1, x, y, turm_mapper, turm_b, this=self.TM)
                    if self.tm("buildingPlacementFailReason") == 0x12:
                        erster = (d, x, y)
                        break
                je[richtung] = erster
            z[f"Karte {g}"] = je
        self.tm_setze("mapSize", alt)
        return z

    def p192_p199_naehe(self, x0, y0):
        """Erwartet: Mauerfeld nahe Feind: verboten. Weg: Grund 0x13 oder 0x11. Hier je Abstand: Feld und Einzelfeld-Weg, der Grund wird vor jedem Aufruf geloescht."""
        frei = self.s.raster()[0]
        z = {}
        for richtung, (dx, dy) in {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}.items():
            r = []
            for d in range(1, 26):
                x, y = x0 + dx * d, y0 + dy * d
                if not (0 <= x < 400 and 0 <= y < 400) or not frei[y, x]:
                    continue
                self.r.rufe(F_MAUERFELD, 1, x, y, 25, this=self.TM)
                a = self.tm("illegalBuild")
                self.tm_setze("buildingPlacementFailReason", 0)
                self.r.rufe(F_MAUERWEG, 1, x, y, x, y, 0x19, this=self.TM)
                w = (a, self.tm("illegalBuild"), self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
                if not r or r[-1][1:] != w:
                    r.append((d,) + w)
            z[richtung + " (Abstand, Feld verboten, Weg verboten, Fehler, Grund), nur Wechsel"] = r
        return z

    def p214_ohne_ziel(self, nr):
        """Erwartet: Ohne Ziel zaehlt tunnelerCounter 0 bis 5, dann -1, Rueckgabe 0. Bauplatz ohne Ziel schlaegt fehl. Laeuft, solange kein Feindturm steht."""
        x, y = self.b("x", nr), self.b("y", nr)
        z = {"gebaeude": (nr, self.b("buildingType", nr), x, y), "zaehler": []}
        for _ in range(8):
            w = self.r.rufe(F_TUNNEL, nr, 0, this=self.U)
            z["zaehler"].append((w, self.b("tunnelerCounter", nr), self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])))
        self.b_setze("tunnelerCounter", nr, 0)
        for d in (20, 40, 80, 150):
            self.r.rufe(F_TUNNELSUCHE, 1, 0, d, x, y - 1, this=self.PF)
            z[f"Suche {d} Felder"] = self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, x + 6, y, MAPPER_TUNNEL, 3, this=self.TM)
        z["Bauplatz daneben (Fehler, Grund)"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        return z

    def p109_essen(self, nr):
        """Erwartet: Essensart sperren: totalFood und der Zaehler der Art sinken um den Bestand, die Kornkammer behaelt die Ware."""
        def stand():
            return {"totalFood": self.p("totalFood", 1), "Brot": self.p("breadCount", 1), "Kaese": self.p("cheeseCount", 1), "Fleisch": self.p("meatCount", 1), "Apfel": self.p("appleCount", 1), "Kammer": (self.b("resourceBread", nr), self.b("resourceCheese", nr), self.b("resourceMeat", nr), self.b("resourceApple", nr)), "bann": [self.p("isFoodTypeBanned[]", 1, 2 * i) for i in range(4)]}
        z = {"ohne Ware": stand()}
        self.b_setze("resourceBread", nr, 10)
        self.b_setze("resourceApple", nr, 5)
        self.takte(6)
        z["10 Brot, 5 Aepfel, 6 Takte"] = stand()
        self.r.rufe(F_ESSEN_SPERRE, 0)
        self.takte(6)
        z["Brot gesperrt, 6 Takte"] = stand()
        self.r.rufe(F_ESSEN_SPERRE, 0)
        self.takte(6)
        z["Brot frei, 6 Takte"] = stand()
        return z

    def p209_unter_gebaeude(self, opfer_nr, h):
        """Erwartet: Gebaeude auf Feld mit eigener Einheit: Einheit verschwindet (Code: deleteUnit). Zuerst die Pruefung, dann gesetzt ohne Pruefung."""
        o = next(e for e in self.s.einheiten_alle() if e["nr"] == opfer_nr)
        z = {"opfer": (o["x"], o["y"])}
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, o["x"], o["y"], h["mapper"], h["b"], this=self.TM)
        z["Pruefung (Fehler, Grund)"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        g = {"spieler": 1, "typ": 3, "mapper": h["mapper"], "groesse": h["b"], "name": h["laufzeitName"], "x": o["x"], "y": o["y"]}
        z["gesetzt, Rueckstellung"] = self.bau_ohne_pruefung(g)
        z["gebaeude"] = (g.get("nr"), g.get("x"), g.get("y"))
        z["Einheit sofort"] = (self.u("logicalState", opfer_nr), self.u("state", opfer_nr))
        self.takte(2)
        z["noch in der Liste"] = any(e["nr"] == opfer_nr for e in self.s.einheiten_alle())
        return z

    def p197_graben(self, x, y):
        """Erwartet: someCountDown sinkt um 1 je Aufruf, nie unter 0, nur bei Graeben mit Besitzer."""
        self.takte(4, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x, y, 0, 0x40000000, 0]}}, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x + 1, y, 0, 0x40000000, 0]}})
        n = self.tm("currentMoatCount")
        a, _, sch, _ = self.K.adresse("DAT_TileMapState", "moats[]")
        roh = [(i, self.r.lies_i(a + i * sch, 2), self.r.lies(a + i * sch + 12, 1)[0], self.r.lies(a + i * sch + 13, 1)[0], self.r.lies(a + i * sch + 14, 1)[0], self.r.lies(a + i * sch + 15, 1)[0]) for i in range(min(n, 14))]
        z = {"anzahl": n, "(Nr, Feld, Besitzer, Fuellung, Stufe, Zaehler)": roh, "werte": []}
        mit = [i for i, *r in roh if r[1]]
        for i in mit:
            self.r.setze_i(a + i * sch + 15, 5, 1)
        for _ in range(16):
            z["werte"].append((self.s.takt(), [self.r.lies(a + i * sch + 15, 1)[0] for i in mit[:3]]))
            self.takte(3)
        return z

    def p221_kinder(self, x, y):
        """Erwartet: Muetter plus Kinder nie ueber 75. In Runde 1 waren 90 Kinder nach rund 30 Takten alle weg: Haengt das an der Grenze? 60 Kinder, 90 Kinder, 90 Muetter."""
        def zahl(a):
            return sum(1 for e in self.s.einheiten_alle() if e["besitzer"] == 1 and e["typ"] == a)
        z = {}
        for name, art, n in (("60 Kinder", 64, 60), ("90 Kinder", 64, 90), ("90 Muetter", 63, 90)):
            self.k.liste([{"setzeEinheit": {"spieler": 1, "typ": art, "x": x, "y": y, "anzahl": n}}], lf.KANAL)
            r = []
            for _ in range(10):
                self.takte(6)
                r.append((self.s.takt(), zahl(63), zahl(64), self.p("someCount02", 1), self.p("someCount03", 1)))
            z[name + " (Takt, Muetter, Kinder, Zaehler 02, 03)"] = r
        return z

    def p147_entlassen(self, leute):
        """Erwartet: Heiler vor Priester vor Wirt. Laut Code die hoechste Stufe zuerst: Heiler 23, Priester 22, Wirt 21, Brauer 20. Die Probe zeigt die ganze Folge."""
        z = {"felder vor dem Takt": [(e["typ"], self.u("field67_0x90", e["nr"]), self.u("isSelectable_OR_matchTime", e["nr"]), self.u("logicalState", e["nr"])) for e in leute[:4]]}
        for e in self.s.einheiten_alle():
            if e["besitzer"] == 1 and e["typ"] == 1:
                self.u_setze("logicalState", e["nr"], ULS_REMOVE)
        folge, vorher = [], {e["nr"]: self.u("state", e["nr"]) for e in leute}
        for _ in range(len(leute) + 2):
            self.r.rufe(F_ENTLASSEN, 1, this=self.G)
            neu = [e for e in leute if self.u("state", e["nr"]) == US_DISAPPEAR and vorher[e["nr"]] != US_DISAPPEAR]
            if not neu:
                folge.append("keiner")
                break
            for e in neu:
                folge.append(e["typ"])
                vorher[e["nr"]] = US_DISAPPEAR
                self.u_setze("logicalState", e["nr"], ULS_REMOVE)
        z["folge_der_arten"] = folge
        return z

    def p179_taste(self):
        """Runde 1: + von 88 auf 93, von 90 auf 100, - von 20 auf 15, von 11 auf 6: Das Spiel im Speicher hat andere Grenzen als der Export. Wo liegen sie?"""
        u32 = ctypes.WinDLL("user32")
        from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz
        pid = pid_der_instanz(2)
        fenster = []
        Rueck = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def jeder(h, _):
            p = ctypes.c_ulong()
            u32.GetWindowThreadProcessId(ctypes.c_void_p(h), ctypes.byref(p))
            if p.value == pid and u32.IsWindowVisible(ctypes.c_void_p(h)):
                fenster.append(h)
            return True
        u32.EnumWindows(Rueck(jeder), None)
        a, gr = self.adr("DAT_GameCore", "gameSpeedLevel")
        alt = self.r.lies_i(a, gr)
        u32.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t)
        z = {"vorher": alt}

        def taste(start, code):
            self.r.setze_i(a, start, gr)
            u32.PostMessageW(ctypes.c_void_p(fenster[0]), 0x100, code, 1)
            u32.PostMessageW(ctypes.c_void_p(fenster[0]), 0x101, code, 0xC0000001)
            time.sleep(0.3)
            return self.r.lies_i(a, gr)
        for s_ in (85, 89, 90, 91, 100, 190, 200, 500, 990, 1000):
            z[f"+ bei {s_}"] = taste(s_, 0x6B)
        for s_ in (1000, 200, 100, 95, 90, 21, 20, 10, 6, 5, 2, 1):
            z[f"- bei {s_}"] = taste(s_, 0x6D)
        self.r.setze_i(a, alt, gr)
        return z

    def lange_stufe(self, grube, mine, takte, schritt):
        """P102, P226, P121. Pechgrube und Eisenmine ohne Vorkommen gesetzt. Erwartet: countPitchRigs bleibt 1, Pech kommt im Lager an, Eisen steigt je Guss um 1. Bei Menge >= 7 am Ende von Zustand 5 oder 6: Zustand 6."""
        z = {"rigs": [], "grube": [], "mine": []}
        gesetzt = False
        lk.aufnahme_im_stand_ohne(self.l, lf.TEMPO_LAUF)
        lk.anhalten(self.l)
        for _ in range(takte // schritt):
            lk.aufnahme_im_stand_ohne(self.l, lf.TEMPO_LAUF)
            self.l.warte_takte(schritt)
            lk.anhalten(self.l)
            t = self.s.takt()
            z["rigs"].append(self.p("countPitchRigs", 1))
            w = (self.b("state", grube), self.b("resourcePitch", grube), self.ware(1, "Pech"), self.b("workerID[]", grube) if False else None)
            if not z["grube"] or z["grube"][-1][1:] != w:
                z["grube"].append((t,) + w)
            m = (self.b("state", mine), self.b("resourceIron", mine))
            if not z["mine"] or z["mine"][-1][1:] != m:
                z["mine"].append((t,) + m)
            if not gesetzt and m[0] >= 4:
                self.b_setze("resourceIron", mine, 7)
                gesetzt = True
                z["mine"].append((t, "Eisen auf 7 gesetzt"))
        z["rigs"] = collections.Counter(z["rigs"]).most_common()
        return z


def szene2(l):
    from selfaware.game.ucp.bauen import NACH_TYP
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    k, s = l.k, l.s
    lk.anhalten(l)
    ls.starttruppen_abwarten(l)
    ls.abraeumen(l)
    s.fern = 0
    frei = s.raster()[0]
    innen = ls.burgbereich(l)(frei)
    feind = ls.burgbereich(l, sp=2)(frei)
    orte = ls.packen(innen, [(14, 6), (8, 8), (8, 8), (8, 8), (30, 6), (8, 8), (4, 4), (30, 3), (10, 10)], rand=4)
    orte_f = ls.packen(feind, [(12, 12)], rand=4)
    if None in orte or None in orte_f:
        raise ls.Abbruch(f"Kein Platz: {orte} {orte_f}")
    (p_einheit, p_grube, p_mine, p_kammer, p_a, p_opfer, p_graben, p_frei, weit) = orte
    (p_feind,) = orte_f
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    tunnel = {"spieler": 1, "typ": 50, "mapper": MAPPER_TUNNEL, "groesse": 3, "name": "BT_TUNNEL", "x": weit[0] + 3, "y": weit[1] + 3}
    grube = ls._g(6, p_grube[0] + 2, p_grube[1] + 2, spieler=1)
    from_mine = next(v for v in NACH_TYP.values() if v.get("laufzeitName") == "BT_IRONMINE")
    mine = {"spieler": 1, "typ": 5, "mapper": from_mine["mapper"], "groesse": from_mine["b"], "name": "BT_IRONMINE", "x": p_mine[0] + 2, "y": p_mine[1] + 2}
    kammer = ls._g(19, p_kammer[0] + 2, p_kammer[1] + 2, spieler=1)
    o = ls.erlaubte_stelle(l, kammer)
    if o:
        kammer["x"], kammer["y"] = o
    rest = ls.gebaeude_setzen(l, [kammer])
    opfer = ls._e("opfer", 24, p_opfer[0] + 4, p_opfer[1] + 4)
    ls.setzen(l, [opfer])
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
    l.warte_takte(2)
    lk.anhalten(l)
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung2(l, r, karte)
        m.aus["aufbau"] = {"kammer": {a: kammer.get(a) for a in ("nr", "x", "y")}, "nicht_gesetzt": [z["name"] for z in rest]}
        m.probe("P201 Reichweite je Kartengroesse", m.p201_reichweite, NACH_TYP[74]["mapper"], NACH_TYP[74]["b"])
        for name, z in (("tunnel", tunnel), ("grube", grube), ("mine", mine)):
            m.aus["aufbau"][name] = m.bau_ohne_pruefung(z) + (z.get("nr"), z.get("x"), z.get("y"))
        if "nr" in tunnel:
            m.probe("P214 ohne Ziel", m.p214_ohne_ziel, tunnel["nr"])
        ft = ls._g(74, p_feind[0] + 5, p_feind[1] + 5, spieler=2)
        o = ls.erlaubte_stelle(l, ft)
        if o:
            ft["x"], ft["y"] = o
        m.aus["aufbau"]["feindturm nicht gesetzt"] = [z["name"] for z in ls.gebaeude_setzen(l, [ft])]
        if "nr" in ft:
            m.probe("P192 P199 am Feindturm", m.p192_p199_naehe, ft["x"], ft["y"])
            if "nr" in tunnel:
                m.probe("P177 mit Ziel", m.p177_mit_ziel, tunnel["nr"], ft["nr"])
        fe = ls._e("feind", 24, p_frei[0] + 15, p_frei[1] + 1, 2)
        ls.setzen(l, [fe])
        if "nr" in fe:
            g = next(e for e in s.einheiten_alle() if e["nr"] == fe["nr"])
            m.probe("P192 P199 an Feind-Einheit", m.p192_p199_naehe, g["x"], g["y"])
            m.u_setze("logicalState", fe["nr"], ULS_REMOVE)
        m.probe("P179 Taste", m.p179_taste)
        if "nr" in opfer:
            m.probe("P209 Einheit unter Gebaeude", m.p209_unter_gebaeude, opfer["nr"], next(v for v in NACH_TYP.values() if "WOODCUT" in str(v.get("laufzeitName")).upper()))
        if "nr" in kammer:
            m.probe("P109 Essen sperren", m.p109_essen, kammer["nr"])
        m.probe("P197 Graben", m.p197_graben, p_graben[0] + 1, p_graben[1] + 1)
        m.probe("P221 Kinder", m.p221_kinder, p_einheit[0] + 2, p_einheit[1] + 2)
        if "nr" in grube and "nr" in mine:
            m.probe("P102 P226 P121 lange Stufe", m.lange_stufe, grube["nr"], mine["nr"], 4000, 20)
        frisch = [ls._e("arbeiter", t, p_a[0] + i, p_a[1] + 1) for i, t in enumerate(ARBEITER)]
        ls.setzen(l, frisch)
        lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
        l.warte_takte(2)
        lk.anhalten(l)
        m.probe("P147 Wer zuerst geht", m.p147_entlassen, [e for e in frisch if "nr" in e])
        return {"szene": "rufen2_g", "datei": m.datei, "proben": len(m.aus)}


class Messung3(Messung2):
    def p197_lang(self, x, y):
        """Runde 2: In 60 Takten sank der Zaehler nicht, nach 8.800 Takten stand er auf 0. Der Aufruf haengt am Balancer (Wert 40 von 0 bis 199). Erwartet: je Runde des Balancers 1 weniger."""
        self.takte(4, {"player": 1, "spielbefehl": {"nr": 21, "werte": [x, y, 0, 0x40000000, 0]}})
        a, _, sch, _ = self.K.adresse("DAT_TileMapState", "moats[]")
        z = {"werte": []}
        self.r.setze_i(a + sch + 15, 3, 1)
        ba = self.K.adresse("DAT_GameState", "gameTicksLoadBalancer")[0]
        alt = None
        for _ in range(60):
            w = self.r.lies(a + sch + 15, 1)[0]
            if w != alt:
                z["werte"].append((self.s.takt(), self.r.lies_i(ba), w))
                alt = w
            self.takte(10)
        z["ende"] = (self.s.takt(), self.r.lies_i(ba), self.r.lies(a + sch + 15, 1)[0])
        return z

    def p221_zustand(self, x, y):
        """Runde 2: Auch 60 Kinder waren nach 30 Takten weg. Ein Zustand 110 (verschwinden) dauert so lange. Vergleich: Wie viele stehen nach 2 Takten auf 110, einmal wie gesetzt, einmal mit Feld 0x3f4 auf 0."""
        z = {}
        for name, n, null in (("60 wie gesetzt", 60, False), ("60 mit Feld 0", 60, True), ("90 mit Feld 0", 90, True)):
            vorher = {e["nr"] for e in self.s.einheiten_alle()}
            self.k.liste([{"setzeEinheit": {"spieler": 1, "typ": 64, "x": x, "y": y, "anzahl": n}}], lf.KANAL)
            ende = time.time() + 8
            neu = []
            while time.time() < ende and len(neu) < n:
                neu = [e["nr"] for e in self.s.einheiten_alle() if e["nr"] not in vorher and e["typ"] == 64]
                time.sleep(0.2)
            feld = [self.u("field297_0x3f4", i) for i in neu]
            if null:
                for i in neu:
                    self.u_setze("field297_0x3f4", i, 0)
            self.takte(2)
            st = collections.Counter(self.u("state", i) for i in neu)
            z[name] = {"gesetzt": len(neu), "Feld vorher": collections.Counter(feld).most_common(3), "Zustaende nach 2 Takten": st.most_common(4), "Zaehler 02, 03": (self.p("someCount02", 1), self.p("someCount03", 1))}
            self.takte(36)
            z[name]["nach 38 Takten"] = sum(1 for e in self.s.einheiten_alle() if e["nr"] in set(neu))
            for i in neu:
                self.u_setze("logicalState", i, ULS_REMOVE)
            self.takte(2)
        return z

    def p209_mit_ohne(self, x, y):
        """Lehnt die Pruefung ab, weil eine eigene Einheit auf dem Feld steht? Dieselbe Stelle ohne und mit Einheit."""
        from selfaware.game.ucp.bauen import NACH_TYP
        from selfaware.tools.experiments import auge_lauf_s as ls
        h = next(v for v in NACH_TYP.values() if "WOODCUT" in str(v.get("laufzeitName")).upper())
        z = {}
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, x, y, h["mapper"], h["b"], this=self.TM)
        z["ohne Einheit"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        e = ls._e("opfer", 24, x, y)
        ls.setzen(self.l, [e])
        e2 = next(q for q in self.s.einheiten_alle() if q["nr"] == e["nr"])
        z["Einheit steht bei"] = (e2["x"], e2["y"])
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, e2["x"], e2["y"], h["mapper"], h["b"], this=self.TM)
        z["auf dem Feld der Einheit"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        self.tm_setze("buildingPlacementFailReason", 0)
        self.r.rufe(F_BAUPLATZ, 1, e2["x"] - 1, e2["y"] - 1, h["mapper"], h["b"], this=self.TM)
        z["ein Feld daneben, Einheit im Grundriss"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"))
        return z

    def p192_feind_einheit(self, nr):
        """Die Feindliste P[].enemies wird im Lauf gefuellt. Runde 2 las ohne Takt. Erwartet: Mauerfeld unter 5, Weg unter 15 Felder Abstand verboten, Luftlinie."""
        self.takte(30)
        z = {"enemies": self.p("enemies", 1)}
        g = next(e for e in self.s.einheiten_alle() if e["nr"] == nr)
        z["feind"] = (g["x"], g["y"])
        z.update(self.p192_p199_naehe(g["x"], g["y"]))
        return z


def szene3(l):
    from selfaware.game.ucp.bauen import NACH_TYP
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    k, s = l.k, l.s
    lk.anhalten(l)
    ls.starttruppen_abwarten(l)
    ls.abraeumen(l)
    s.fern = 0
    frei = s.raster()[0]
    innen = ls.burgbereich(l)(frei)
    feind = ls.burgbereich(l, sp=2)(frei)
    orte = ls.packen(innen, [(14, 6), (8, 8), (30, 3), (30, 8), (10, 10), (8, 8)], rand=5)
    orte_f = ls.packen(feind, [(12, 12)], rand=4)
    if None in orte or None in orte_f:
        raise ls.Abbruch(f"Kein Platz: {orte} {orte_f}")
    (p_kinder, p_graben, p_einheit, p_huette, weit, p_platz) = orte
    (p_feind,) = orte_f
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    tunnel = {"spieler": 1, "typ": 85, "mapper": MAPPER_TUNNEL, "groesse": 3, "name": "BT_UNKNOWN4", "x": weit[0] + 3, "y": weit[1] + 3}
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
    l.warte_takte(2)
    lk.anhalten(l)
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung3(l, r, karte)
        m.aus["aufbau"] = {"tunnel": m.bau_ohne_pruefung(tunnel) + (tunnel.get("nr"), tunnel.get("x"), tunnel.get("y"))}
        if "nr" in tunnel:
            m.probe("P214 ohne Ziel", m.p214_ohne_ziel, tunnel["nr"])
        huette = {"spieler": 2, "typ": 1, "mapper": NACH_TYP[1]["mapper"], "groesse": NACH_TYP[1]["b"], "name": "BT_HOVEL", "x": p_huette[0] + 14, "y": p_huette[1] + 2}
        m.aus["aufbau"]["feindhuette"] = m.bau_ohne_pruefung(huette) + (huette.get("nr"), huette.get("x"), huette.get("y"))
        if "nr" in huette:
            m.probe("P192 P199 an Feindhuette", m.p192_p199_naehe, huette["x"], huette["y"])
            m.b_setze("currentHealth", huette["nr"], 1)
            m.takte(1, {"player": 2, "spielbefehl": {"nr": 29, "werte": [huette["nr"], 100, huette["uid"]]}})
            m.takte(20)
            m.aus["aufbau"]["feindhuette weg"] = not any(g["nr"] == huette["nr"] for g in s.gebaeude(None))
        ft = ls._g(74, p_feind[0] + 5, p_feind[1] + 5, spieler=2)
        o = ls.erlaubte_stelle(l, ft)
        if o:
            ft["x"], ft["y"] = o
        m.aus["aufbau"]["feindturm nicht gesetzt"] = [z["name"] for z in ls.gebaeude_setzen(l, [ft])]
        if "nr" in ft and "nr" in tunnel:
            m.probe("P177 mit Ziel", m.p177_mit_ziel, tunnel["nr"], ft["nr"])
        fe = ls._e("feind", 24, p_einheit[0] + 15, p_einheit[1] + 1, 2)
        ls.setzen(l, [fe])
        if "nr" in fe:
            m.probe("P192 P199 an Feind-Einheit", m.p192_feind_einheit, fe["nr"])
            m.u_setze("logicalState", fe["nr"], ULS_REMOVE)
        m.probe("P209 mit und ohne Einheit", m.p209_mit_ohne, p_platz[0] + 4, p_platz[1] + 4)
        m.probe("P221 Kinder Zustand", m.p221_zustand, p_kinder[0] + 2, p_kinder[1] + 2)
        m.probe("P197 Graben lang", m.p197_lang, p_graben[0] + 1, p_graben[1] + 1)
        return {"szene": "rufen3_g", "datei": m.datei, "proben": len(m.aus)}


F_HOLZFAELLER, F_KAUFPLAN, F_NEUBAU, F_BITTE = 0x004cb290, 0x004cba50, 0x004f15c0, 0x004d1f00
F_ZAEHLE = 0x0040a9b0  # countBuildingsForPlayer(this=Gebaeude, Spieler, Art, Filter)


class Messung4(Messung3):
    def ki_stand(self, n):
        return {"aiType": self.p("aiType", n), "aivID": self.p("aivID", n), "Gold": self.ware(n, "Gold"), "Holz": self.ware(n, "Holz"), "Bevoelkerung": self.p("currentPopulation", n)}

    def eigentum_tafel(self):
        """Welche Gebaeudearten zaehlen als Feindgebaeude fuer den Radius 7 (DAT_BuildingTypeOwnable)? Die Hutte in Runde 3 zaehlte nicht."""
        a, g, sch, n = self.K.adresse("DAT_BuildingDefinedData", "DAT_BuildingTypeOwnable[]")
        s_ = sch or g
        return [i for i in range(min(n, 120)) if self.r.lies_i(a + i * s_, g)]

    def p214_ohne_ziel_gebaeude(self, nr):
        """Die Suche nimmt vom Gebaeude nur Ort und Besitzer. Hier ein eigener Turm, kein Ziel im Umkreis. Erwartet: 0 bis 5, dann -1, Rueckgabe 0."""
        x, y = self.b("x", nr), self.b("y", nr)
        z = {"gebaeude": (nr, self.b("buildingType", nr), x, y), "Zaehler (Rueckgabe, Stand, Zielfeld)": []}
        alt = self.b("tunnelerCounter", nr)
        for _ in range(8):
            w = self.r.rufe(F_TUNNEL, nr, 0, this=self.U)
            z["Zaehler (Rueckgabe, Stand, Zielfeld)"].append((w, self.b("tunnelerCounter", nr), self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])))
        self.b_setze("tunnelerCounter", nr, alt)
        for d in (20, 40, 80, 150):
            self.r.rufe(F_TUNNELSUCHE, 1, 0, d, x, y - 1, this=self.PF)
            z[f"Suche {d} Felder"] = self.r.lies_i(self.K.adresse("DAT_PathFindingState", "ALG_TargetTile")[0])
        frei = self.s.raster()[0]
        for dx, dy in ((8, 0), (-8, 0), (0, 8), (0, -8)):
            if frei[y + dy, x + dx]:
                self.tm_setze("buildingPlacementFailReason", 0)
                self.r.rufe(F_BAUPLATZ, 1, x + dx, y + dy, MAPPER_TUNNEL, 3, this=self.TM)
                z["Bauplatz ohne Ziel (Fehler, Grund)"] = (self.tm("buildingPlacementFail"), self.tm("buildingPlacementFailReason"), (x + dx, y + dy))
                break
        return z

    def p221_mit_heim(self, x, y, heim, uid):
        """Kinder ohne Zuhause verschwinden gleich. Mit Zuhause: 60 bleiben, von 90 sollen die ueber 75 gehen."""
        z = {}
        for n in (60, 90):
            vorher = {e["nr"] for e in self.s.einheiten_alle()}
            self.k.liste([{"setzeEinheit": {"spieler": 1, "typ": 64, "x": x, "y": y, "anzahl": n}}], lf.KANAL)
            ende = time.time() + 8
            neu = []
            while time.time() < ende and len(neu) < n:
                neu = [e["nr"] for e in self.s.einheiten_alle() if e["nr"] not in vorher and e["typ"] == 64]
                time.sleep(0.2)
            for i in neu:
                self.u_setze("workplaceBuildingID_1", i, heim)
                self.u_setze("workplaceBuildingUID", i, uid)
            self.takte(2)
            st = collections.Counter(self.u("state", i) for i in neu)
            eintrag = {"gesetzt": len(neu), "nach 2 Takten Zustaende": st.most_common(5), "Zaehler 03": self.p("someCount03", 1)}
            self.takte(36)
            eintrag["nach 38 Takten noch da"] = sum(1 for e in self.s.einheiten_alle() if e["nr"] in set(neu))
            z[f"{n} Kinder"] = eintrag
            for i in neu:
                self.u_setze("logicalState", i, ULS_REMOVE)
            self.takte(3)
        return z

    def p182_holzfaeller(self, n, huetten):
        """Erwartet: ab 3 Huetten kein Neubau, wenn der Wert unter 31 liegt, ab 6 unter 91, bei unter 1 nie."""
        a, g = self.adr("DAT_AIVState", "mapExtraInfo.totalWoodAvailable")
        alt = self.r.lies_i(a, g)
        pop = self.p("currentPopulation", n)
        self.p_setze("currentPopulation", n, 2000)
        z = {"Wert jetzt": alt, "huetten": huetten}
        for w in (0, 1, 30, 31, 90, 91, 500):
            self.r.setze_i(a, w, g)
            z[f"Wert {w}"] = self.r.rufe(F_HOLZFAELLER, n, this=self.AIC)
        self.r.setze_i(a, alt, g)
        self.p_setze("currentPopulation", n, pop)
        return z

    def p183_kaufplan(self, n):
        """Erwartet: Zaehler steigt je Aufruf um 1, bei 37 steht im Wunsch Holz 5, sofern er vorher 0 war."""
        a, gr, sch, _ = self.K.adresse("DAT_GameState", "playerDataArray[].resourcesToAcquireArray[]")
        el = 4 if gr == 4 else gr
        wunsch = a + n * sch + 2 * el
        alt = (self.ware(n, "Holz"), self.p("noWoodTracker", n), self.r.lies_i(wunsch, el), self.p("countFletchersPoleturners", n), self.p("canStartSpending", n))
        self.ware_setze(n, "Holz", 0)
        self.p_setze("noWoodTracker", n, 30)
        self.r.setze_i(wunsch, 0, el)
        self.p_setze("countFletchersPoleturners", n, 1)
        self.p_setze("canStartSpending", n, 1)
        z = []
        for _ in range(12):
            self.r.rufe(F_KAUFPLAN, n, this=self.AIC)
            z.append((self.p("noWoodTracker", n), self.r.lies_i(wunsch, el)))
        self.ware_setze(n, "Holz", 50)
        self.r.rufe(F_KAUFPLAN, n, this=self.AIC)
        z.append(("mit Holz", self.p("noWoodTracker", n), self.r.lies_i(wunsch, el)))
        self.ware_setze(n, "Holz", alt[0])
        self.p_setze("noWoodTracker", n, alt[1])
        self.r.setze_i(wunsch, alt[2], el)
        self.p_setze("countFletchersPoleturners", n, alt[3])
        self.p_setze("canStartSpending", n, alt[4])
        return {"vorher": alt, "(Zaehler, Wunsch Holz)": z}

    def p191_neubau(self, n):
        """Erwartet: Gold ueber 16.000: Ziel +2 je Aufruf, bis 16.000: +1, bis 5.000: +1, aber erst nach aivPoorLimit Aufrufen."""
        kid = self.p("aivID", n)
        if kid <= 0:
            return {"fehler": f"aivID {kid}"}

        def av(f):
            a, g = self.adr("DAT_AIVState", f"aivs[].{f}", kid)
            return a, g
        z = {"aivID": kid, "limit": self.r.lies_i(*av("aivPoorLimit_OR_AIC_buildInterval"))}
        gold = self.ware(n, "Gold")
        for wert in (20000, 10000, 3000):
            self.ware_setze(n, "Gold", wert)
            self.r.setze_i(*(av("aivPoorCounter")[:1]), 0, av("aivPoorCounter")[1])
            r = []
            for _ in range(8):
                self.p_setze("resourceRebuildDelay", n, 0)
                vor = self.r.lies_i(*av("currentStepGoal"))
                self.r.rufe(F_NEUBAU, n, this=self.AIV)
                r.append(self.r.lies_i(*av("currentStepGoal")) - vor)
            z[f"Gold {wert}: Zuwachs je Aufruf"] = r
        self.ware_setze(n, "Gold", gold)
        return z

    def p187_bitte(self, ki):
        """Erwartet: Eine verbuendete KI bittet um Ware: beim Verbuendeten stehen Warennummer und Menge. Gesetzt: Spieler 1 und die KI im selben Team, dann requestGoods direkt."""
        a, g, sch, _ = self.K.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
        el = sch or g
        teams = [self.r.lies_i(a + i * el, g) for i in range(9)]
        z = {"teams vorher": teams, "aiRequestDelay": self.p("aiRequestDelay", ki)}
        self.r.setze_i(a + ki * el, teams[1], g)
        self.p_setze("aiRequestDelay", ki, 0)
        self.r.rufe(F_BITTE, ki, 2, 7, this=self.AIC)
        z["Spieler 1: Ware, Menge"] = (self.p("requestedGoodsArray1Unk[]", 1, 2 * ki), self.p("requestedGoodsArray2Unk[]", 1, 2 * ki))
        z["Spieler 3 (kein Team): Ware"] = self.p("requestedGoodsArray1Unk[]", 3, 2 * ki)
        self.p_setze("requestedGoodsArray1Unk[]", 1, 0, 2 * ki)
        self.p_setze("requestedGoodsArray2Unk[]", 1, 0, 2 * ki)
        self.r.setze_i(a + ki * el, teams[ki], g)
        self.r.rufe(F_BITTE, ki, 2, 7, this=self.AIC)
        z["ohne Team: Spieler 1 bekommt"] = self.p("requestedGoodsArray1Unk[]", 1, 2 * ki)
        return z


def szene4(l):
    from selfaware.game.ucp.bauen import NACH_TYP
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    k, s = l.k, l.s
    lk.anhalten(l)
    ls.starttruppen_abwarten(l)
    ls.abraeumen(l)
    s.fern = 0
    frei = s.raster()[0]
    innen = ls.burgbereich(l)(frei)
    feind = ls.burgbereich(l, sp=2)(frei)
    orte = ls.packen(innen, [(8, 8), (10, 8), (30, 8), (8, 8)], rand=5)
    orte_f = ls.packen(feind, [(12, 12), (24, 6)], rand=4)
    if None in orte or None in orte_f:
        raise ls.Abbruch(f"Kein Platz: {orte} {orte_f}")
    (p_turm, p_heim, p_ziel, p_kinder) = orte
    (p_feind, p_huetten) = orte_f
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    turm = ls._g(74, p_turm[0] + 2, p_turm[1] + 2, spieler=1)
    o = ls.erlaubte_stelle(l, turm)
    if o:
        turm["x"], turm["y"] = o
    heim = ls._g(1, p_heim[0] + 2, p_heim[1] + 2, spieler=1)
    rest = ls.gebaeude_setzen(l, [turm, heim])
    lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
    l.warte_takte(2)
    lk.anhalten(l)
    h = next(v for v in NACH_TYP.values() if "WOODCUT" in str(v.get("laufzeitName")).upper())
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung4(l, r, karte)
        m.aus["aufbau"] = {"nicht_gesetzt": [z["name"] for z in rest], "turm": turm.get("nr"), "heim": heim.get("nr"), "KI 2": m.ki_stand(2), "Spieler 1": m.ki_stand(1)}
        if "nr" in turm:
            m.probe("P214 ohne Ziel", m.p214_ohne_ziel_gebaeude, turm["nr"])
        m.probe("Eigentum-Tafel", m.eigentum_tafel)
        tafel = m.aus["Eigentum-Tafel"]["ergebnis"]
        wahl = next((t for t in (10, 19, 26, 9, 24, 25, 8) if isinstance(tafel, list) and t in tafel and t in NACH_TYP), None)
        if wahl is not None:
            fg = {"spieler": 2, "typ": wahl, "mapper": NACH_TYP[wahl]["mapper"], "groesse": NACH_TYP[wahl]["b"], "name": NACH_TYP[wahl]["laufzeitName"], "x": p_ziel[0] + 14, "y": p_ziel[1] + 2}
            m.aus["aufbau"]["feindgebaeude"] = m.bau_ohne_pruefung(fg) + (wahl, fg.get("nr"), fg.get("x"), fg.get("y"))
            if "nr" in fg:
                m.probe("P199 an eigentumsfaehigem Feindgebaeude", m.p192_p199_naehe, fg["x"], fg["y"])
        ft = ls._g(74, p_feind[0] + 5, p_feind[1] + 5, spieler=2)
        o = ls.erlaubte_stelle(l, ft)
        if o:
            ft["x"], ft["y"] = o
        m.aus["aufbau"]["feindturm nicht gesetzt"] = [z["name"] for z in ls.gebaeude_setzen(l, [ft])]
        if "nr" in ft and "nr" in turm:
            m.probe("P177 mit Ziel", m.p177_mit_ziel, turm["nr"], ft["nr"])
        if "nr" in heim:
            m.probe("P221 Kinder mit Zuhause", m.p221_mit_heim, p_kinder[0] + 2, p_kinder[1] + 2, heim["nr"], heim["uid"])
        m.probe("P183 Kaufplan", m.p183_kaufplan, 2)
        m.probe("P182 Holzfaeller 0 Huetten", m.p182_holzfaeller, 2, 0)
        for i in range(1, 7):
            hu = {"spieler": 2, "typ": 3, "mapper": h["mapper"], "groesse": h["b"], "name": h["laufzeitName"], "x": p_huetten[0] + 3 * (i - 1), "y": p_huetten[1] + 1}
            m.aus["aufbau"][f"huette {i}"] = m.bau_ohne_pruefung(hu)
            if i in (3, 6):
                lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
                l.warte_takte(3)
                lk.anhalten(l)
                m.probe(f"P182 Holzfaeller {i} Huetten", m.p182_holzfaeller, 2, i)
        m.probe("P191 Neubau", m.p191_neubau, 2)
        m.probe("P187 Bitte um Ware", m.p187_bitte, 2)
        return {"szene": "rufen4_g", "datei": m.datei, "proben": len(m.aus)}


class OhneAufzeichnung:
    """Der KI-Lauf zeichnet nichts auf, die Wache fragt trotzdem nach Fehlern der Aufzeichnung (Lauf 20:30)."""

    def fehler(self):
        return None


class MessungKI(Messung4):
    def p182_tafel(self):
        """Wie zaehlt das Spiel die Huetten? countBuildingsForPlayer mit und ohne Filter, dazu die Grenzen je KI (Versatz 0x54 und 0x6c der KI-Daten)."""
        z = {}
        beste, ziel = -1, 1
        for n in range(1, 9):
            ai = self.p("aiType", n)
            ba = self.AIC + (ai - 1) * 0x2a4
            voll = self.r.rufe(F_ZAEHLE, n, 3, 0, this=self.B)
            gefiltert = self.r.rufe(F_ZAEHLE, n, 3, 1, this=self.B)
            bev, hoechst = self.r.lies_i(ba + 0x54), self.r.lies_i(ba + 0x6c)
            z[n] = {"KI": ai, "Huetten alle": voll, "gezaehlt": gefiltert, "Leute je Huette": bev, "hoechstens": hoechst}
            if hoechst > beste and bev > 0:
                beste, ziel = hoechst, n
        return {"je Spieler": z, "ziel": ziel}

    def p183_schwelle(self, n):
        """Bei welchem Zaehler entsteht der Holzwunsch? Erwartet laut Export: ueber 36, also bei 37. In der letzten Probe stand er schon bei 31."""
        a, gr, sch, _ = self.K.adresse("DAT_GameState", "playerDataArray[].resourcesToAcquireArray[]")
        el = 4 if gr == 4 else gr
        wunsch = a + n * sch + 2 * el
        alt = (self.ware(n, "Holz"), self.p("noWoodTracker", n), self.r.lies_i(wunsch, el), self.p("countFletchersPoleturners", n), self.p("canStartSpending", n))
        self.p_setze("countFletchersPoleturners", n, 1)
        self.p_setze("canStartSpending", n, 1)
        self.ware_setze(n, "Holz", 0)
        self.p_setze("noWoodTracker", n, 0)
        self.r.setze_i(wunsch, 0, el)
        z = []
        for _ in range(45):
            self.r.rufe(F_KAUFPLAN, n, this=self.AIC)
            w = (self.p("noWoodTracker", n), self.r.lies_i(wunsch, el))
            if not z or z[-1][1] != w[1]:
                z.append(w)
        erg = {"vorher": alt, "(Zaehler, Wunsch) bei jedem Wechsel des Wunsches": z}
        self.r.setze_i(wunsch, 3, el)
        self.p_setze("noWoodTracker", n, 44)
        self.r.rufe(F_KAUFPLAN, n, this=self.AIC)
        erg["Wunsch war 3, Zaehler 45"] = self.r.lies_i(wunsch, el)
        self.ware_setze(n, "Holz", alt[0])
        self.p_setze("noWoodTracker", n, alt[1])
        self.r.setze_i(wunsch, alt[2], el)
        self.p_setze("countFletchersPoleturners", n, alt[3])
        self.p_setze("canStartSpending", n, alt[4])
        return erg

    def p191_im_lauf(self, gold, takte, schritt):
        """Erwartet: Das Ziel steigt ueber 16.000 Gold um 2 je Aufruf, bis 16.000 um 1, bis 5.000 um 1 erst nach der Wartezeit. Das Gold wird alle paar Takte neu gesetzt, das Spiel laeuft dazwischen."""
        z = {}
        reihen = {n: [] for n in gold}
        kids = {n: self.p("aivID", n) for n in gold}
        def lies(n, f):
            a, g = self.adr("DAT_AIVState", f"aivs[].{f}", kids[n])
            return self.r.lies_i(a, g)
        z["limit"] = {n: lies(n, "aivPoorLimit_OR_AIC_buildInterval") for n in gold}
        for _ in range(takte // schritt):
            for n, g in gold.items():
                self.ware_setze(n, "Gold", g)
            self.takte(schritt)
            for n in gold:
                v = lies(n, "currentStepGoal")
                if not reihen[n] or reihen[n][-1][1] != v:
                    reihen[n].append((self.s.takt(), v))
        for n, g in gold.items():
            sp = collections.Counter(b[1] - a[1] for a, b in zip(reihen[n], reihen[n][1:]))
            ab = collections.Counter(b[0] - a[0] for a, b in zip(reihen[n], reihen[n][1:]))
            z[f"Spieler {n}, Gold {g}"] = {"Spruenge": sp.most_common(5), "Abstand Takte": ab.most_common(5), "Anfang": reihen[n][:10]}
        return z

    def p187_bitte_ki(self, ki, ziel):
        """Erwartet: Beim Verbuendeten stehen Warennummer und Menge. Das Ziel ist nicht der angezeigte Spieler, damit keine Bildbotschaft startet."""
        a, g, sch, _ = self.K.adresse("DAT_GameState", "mapAndTime.playerTeams[]")
        el = sch or g
        teams = [self.r.lies_i(a + i * el, g) for i in range(9)]
        z = {"teams vorher": teams, "aiType": self.p("aiType", ki), "aiRequestDelay": self.p("aiRequestDelay", ki), "Essen": self.p("totalFood", ki)}
        self.r.setze_i(a + ki * el, teams[ziel], g)
        self.p_setze("aiRequestDelay", ki, 0)
        self.p_setze("requestedGoodsArray1Unk[]", ziel, 0, 2 * ki)
        self.p_setze("requestedGoodsArray2Unk[]", ziel, 0, 2 * ki)
        self.r.rufe(F_BITTE, ki, 2, 7, this=self.AIC)
        z["Holz, Menge 7: beim Partner"] = (self.p("requestedGoodsArray1Unk[]", ziel, 2 * ki), self.p("requestedGoodsArray2Unk[]", ziel, 2 * ki))
        self.p_setze("requestedGoodsArray1Unk[]", ziel, 0, 2 * ki)
        self.p_setze("requestedGoodsArray2Unk[]", ziel, 0, 2 * ki)
        self.r.rufe(F_BITTE, ki, 3, 7, this=self.AIC)
        z["Hopfen ist ausgenommen: beim Partner"] = self.p("requestedGoodsArray1Unk[]", ziel, 2 * ki)
        self.r.setze_i(a + ki * el, teams[ki], g)
        self.r.rufe(F_BITTE, ki, 2, 7, this=self.AIC)
        z["ohne Team: beim Partner"] = self.p("requestedGoodsArray1Unk[]", ziel, 2 * ki)
        return z


def ki_main(n=2, karte_name="Green Haven", takte=2500):
    """Ein KI-Gefecht bis Takt 2500, dann die KI-Regeln direkt. Erwartungen stehen bei den Proben."""
    from selfaware.game.ucp.bauen import NACH_TYP
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import ProzessQuelle, pid_der_instanz

    lf.pruefe_laufinstanz(n)
    lf.sperre_holen("Rufen KI (B-142)")
    steht = False
    k = s = None
    try:
        k = lf.EchterKanal()
        lf.warte_auf_modul(k)
        for rest in lf.ALTE_SCHALTER:
            k.befehl(rest, lf.KANAL)
        karte = Feldkarte.laden(feldliste=FELDLISTE)
        quelle = ProzessQuelle(pid_der_instanz(n))
        s = ls.SpeicherS(quelle, karte)
        lk.gefecht_starten(k, karte_name, lk.FRIEDEN_NORMAL, startpause=1)
        steht, t = lf.anhalten_und_pruefen(k, s)
        if not steht:
            raise lf.Abbruch(f"Steht nicht am Start: {t}")
        l = ls.LaufS(k, s, OhneAufzeichnung(), print)
        l.gefecht = True
        s.fern = 0
        lk.aufnahme_im_stand_ohne(l, lf.TEMPO_LAUF)
        l.warte_takte(takte)
        lk.anhalten(l)
        h = next(v for v in NACH_TYP.values() if "WOODCUT" in str(v.get("laufzeitName")).upper())
        with Rufer(pid_der_instanz(n)) as r:
            m = MessungKI(l, r, karte)
            m.aus["aufbau"] = {"takt": s.takt(), "spieler": {i: m.ki_stand(i) for i in range(1, 9)}, "huetten": {i: sum(1 for g in s.gebaeude(i) if g["typ"] == 3) for i in range(1, 9)}}
            m.probe("P182 Tafel", m.p182_tafel)
            ziel = m.aus["P182 Tafel"]["ergebnis"]["ziel"]
            lord = next(e for e in s.einheiten_alle() if e["typ"] == 55 and e["besitzer"] == ziel)
            for _ in range(10):
                c = m.r.rufe(F_ZAEHLE, ziel, 3, 1, this=m.B)
                m.probe(f"P182 mit {c} Huetten", m.p182_holzfaeller, ziel, c)
                if c >= 7:
                    break
                o = ls.erlaubte_stelle(l, {"mapper": h["mapper"], "groesse": h["b"], "x": lord["x"] + 14, "y": lord["y"], "spieler": ziel}, rand=25)
                if not o:
                    break
                z = {"spieler": ziel, "typ": 3, "mapper": h["mapper"], "groesse": h["b"], "name": h["laufzeitName"], "x": o[0], "y": o[1]}
                if not m.bau_ohne_pruefung(z)[0]:
                    break
                lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
                l.warte_takte(1)
                lk.anhalten(l)
            m.probe("P183 Schwelle Spieler 2", m.p183_schwelle, 2)
            m.probe("P191 Neubau im Lauf", m.p191_im_lauf, {2: 20000, 5: 10000, 6: 3000}, 800, 5)
            m.probe("P187 Bitte um Ware", m.p187_bitte_ki, 3, 2)
            print("DATEI", m.datei)
        steht, t = lf.anhalten_und_pruefen(k, s)
    finally:
        if steht:
            lf.sperre_freigeben()


def szene_e(l):
    """P059 im Editor: Sumpf per Spielbefehl 21 wie der Graben (setTerrain, Flag 0x20000000). Erwartet: Sumpffeld am Rand MacroLayer & 0x3f = 1, mit 8 Sumpf-Nachbarn 2, 4, 8 oder 0x10."""
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    lk.anhalten(l)
    frei = l.s.raster()[0]
    ort = ls.packen(frei, [(14, 14)], rand=10)[0]
    if ort is None:
        raise ls.Abbruch("Kein Platz fuer den Sumpf")
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung4(l, r, karte)
        m.probe("P059 Sumpf im Editor", m.p059_sumpf, ort[0] + 3, ort[1] + 3)
        return {"szene": "rufen_e", "datei": m.datei, "proben": len(m.aus)}


def szene5(l):
    """Bitte von SAI (04.11. 21:10): Kommen mehrere Gruppenbefehle im selben Takt an? Jeder Befehl: Auswahl (16) und Laufen (17), direkt ohne die Warteschlange des Moduls.
    Faelle: 2, 5, 12 Gruppen mit verschiedenen Nummern, Gegenprobe mit derselben Nummer, Einzelbefehle je Einheit, zum Vergleich die Warteschlange. Beleg: Laufziel jeder Einheit und der Takt im Log."""
    import re
    from selfaware import workspace  # noqa: F401
    from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
    from selfaware.tools.experiments import auge_lauf_s as ls
    from selfaware.tools.experiments.auge_aufzeichnung import pid_der_instanz

    TICK = 0x01FE7DD8 if False else None
    k, s = l.k, l.s
    lk.anhalten(l)
    ls.starttruppen_abwarten(l)
    ls.abraeumen(l)
    frei = s.raster()[0]
    ort = ls.packen(frei, [(80, 46)], rand=2)[0]
    if ort is None:
        raise ls.Abbruch("Kein Platz fuer die Messung")
    x0, y0 = ort
    karte = Feldkarte.laden(feldliste=FELDLISTE)
    log = os.path.join(lf.ordner(2), "ucp3.log")
    with Rufer(pid_der_instanz(2)) as r:
        m = Messung4(l, r, karte)
        takt_adr = next(a for a in (0x0117CADC, ) if True)  # dasselbe Feld, das s.takt() liest, wird unten gegengeprueft
        ergebnis_ort = {"platz": (x0, y0), "takt_feld_ok": r.lies_i(takt_adr) == s.takt()}
        m.aus["aufbau"] = ergebnis_ort

        def fall(gruppen, je, gleich=False, schlange=False):
            ein = []
            for g in range(gruppen):
                for i in range(je):
                    ein.append(ls._e("m", 24, x0 + (g * je + i) % 25, y0 + (g * je + i) // 25))
            ls.setzen(l, ein)
            ziele, bef = [], []
            for g in range(gruppen):
                wer = ein[g * je:(g + 1) * je]
                z = (x0 + (g % 25) * 3, y0 + 30 + (g // 25) * 3)
                ziele.append(z)
                c = {"player": 1, "angriff": {"einheiten": [e["nr"] for e in wer], "lauf": list(z)}}
                if not schlange:
                    c["ausSchlange"] = True
                bef.append(c)
            start_log = os.path.getsize(log)
            if not schlange:  # Im angehaltenen Spiel abgesetzt entstand keine einzige Gruppe (Lauf 21:13). Darum laeuft das Spiel, 1 Takt je Sekunde: Das Log zeigt, ob alle im selben Takt lagen
                lk.aufnahme_im_stand_ohne(l, 1)
                time.sleep(1.2)
            t0 = s.takt()
            if gleich:  # die Reserve des Moduls gilt je Takt: Der Takt wird je Befehl kurz weitergestellt
                for i, c in enumerate(bef):
                    r.setze_i(takt_adr, t0 + i)
                    k.liste([c], lf.KANAL)
                r.setze_i(takt_adr, t0)
            else:
                for i in range(0, len(bef), ls.STUECK):
                    k.liste(bef[i:i + ls.STUECK], lf.KANAL)
            stand_ziel = lambda n: (m.u("plannedDestinationX", n), m.u("plannedDestinationY", n))
            if schlange:
                lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
            else:
                k.befehl({"tempo": lf.TEMPO_JEDER_TAKT}, lf.KANAL)
            l.warte_takte(3)
            lk.anhalten(l)
            nach3 = [(m.u("tribeID", e["nr"]), stand_ziel(e["nr"])) for e in ein]
            lk.aufnahme_im_stand_ohne(l, lf.TEMPO_JEDER_TAKT)
            l.warte_takte(60)
            lk.anhalten(l)
            nach60 = [(m.u("tribeID", e["nr"]), stand_ziel(e["nr"]), (m.u("x", e["nr"]), m.u("y", e["nr"]))) for e in ein]
            # Wer steuert auf sein eigenes Ziel zu? Geplantes Ziel naeher am eigenen als an jedem anderen, und hoechstens 4 Felder daneben
            richtig = 0
            falsch_auf = collections.Counter()
            ohne = 0
            for g in range(gruppen):
                for i in range(je):
                    _, pz, _ = nach60[g * je + i]
                    if pz == (0, 0):
                        ohne += 1
                        continue
                    best = min(range(gruppen), key=lambda h: max(abs(pz[0] - ziele[h][0]), abs(pz[1] - ziele[h][1])))
                    d = max(abs(pz[0] - ziele[g][0]), abs(pz[1] - ziele[g][1]))
                    if d <= 4 and (best == g or d == max(abs(pz[0] - ziele[best][0]), abs(pz[1] - ziele[best][1]))):
                        richtig += 1
                    else:
                        falsch_auf[best] += 1
            with open(log, encoding="utf-8", errors="replace") as d:
                d.seek(start_log)
                zeilen = re.findall(r"ANGRIFF Tick (\d+): (\d+) Einheiten, Gruppe (\d+), Art (\d+).*Auswahl=(\w+) Befehl=(\w+)", d.read())
            je_takt = collections.Counter(z[0] for z in zeilen)
            aus = {
                "Gruppen": gruppen, "je": je, "Einheiten": len(ein), "richtiges Ziel": richtig, "ohne Ziel": ohne, "falsche Ziele (Gruppe: Zahl)": falsch_auf.most_common(6),
                "Log: Befehle": len(zeilen), "Log: Takte (Takt: Befehle)": sorted(je_takt.items())[:8], "Log: Takte insgesamt": len(je_takt), "Log: verschiedene Nummern": len({z[2] for z in zeilen}),
                "Log: nicht abgesetzt": sum(1 for z in zeilen if z[4] != "true" or z[5] != "true"),
                "Gruppen im Spiel nach 3 Takten": len({a for a, _ in nach3 if a}), "nach 60 Takten": len({a for a, _, _ in nach60 if a}),
                "Beispiele (Ziel, geplant, Gruppe)": [(ziele[g], nach60[g * je][1], nach60[g * je][0]) for g in list(range(gruppen))[:4]],
            }
            ls.abraeumen(l)
            return aus
        for name, a in (("Gegenprobe 1 Gruppe je 3", (1, 3)), ("2 Gruppen je 3, verschiedene Nummern", (2, 3)), ("5 Gruppen je 3, verschiedene Nummern", (5, 3)), ("12 Gruppen je 3, verschiedene Nummern", (12, 3))):
            m.probe(name, fall, *a)
        m.probe("Gegenprobe 5 Gruppen je 3, dieselbe Nummer", fall, 5, 3, gleich=True)
        m.probe("Gegenprobe 12 Gruppen je 3, dieselbe Nummer", fall, 12, 3, gleich=True)
        for n in (8, 20, 50, 100, 120):
            m.probe(f"Einzelbefehle {n} Einheiten", fall, n, 1)
        return {"szene": "rufen5_g", "datei": m.datei, "proben": len(m.aus)}


if __name__ == "__main__":
    ki_main()
