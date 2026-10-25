# -*- coding: utf-8 -*-
"""B-241 Schritt 3 - der Einkaeufer: EINE Stelle kauft Truppen, mit EINER Muenze (Daniel 25.10.2026 10:23 "ja zum Anschluss-Vorschlag").

Vorher kauften sechs Stellen fest ein (erstes_spiel: Heer-Werbung arab. Schwert/Bogen im Takt 3:1, Streitkolben ueber die
Kaserne bis zur Sollzahl, Assassinen bis zur Sollzahl, raids.werbung Sklaven/Schleuderer/Reiter bis Sollzahlen). Jetzt:
  Muenze = GOLD-GEGENWERT. Eine Einheit ist ihren Preis wert (kaufrechnung.preise: Anwerbegold + Waffen zum Marktpreis), ein
  Gebaeude seine Baukosten zu Marktpreisen (gebaeude_wert), ein Partiesieg die ganze Wirtschaft des Gegners (siegwert).
  Drei Aufgaben melden je Einheitenart, was EINE weitere Einheit bringt:
    Raid      - bestes Ziel fuer einen Sklaven (A_SLAVE 71) / Meuchelmoerder (A_ASSASSIN 73) vom Soeldnerposten aus:
                Gebaeudewert x (1 - P(Tod)) - Preis x P(Tod), P(Tod) aus gefahrenschutz.Lage.plan (gelernte Baender je Art);
                Berittene Bogenschuetzen (A_HARCHER 74) nur, wenn die Reiterjagd mehr Ziele sah als Reiter da sind (B-220),
                Wert je Ziel ARBEITER_WERT (Startwert, UNGEMESSEN)
    Feldzug   - Fortschritt zum Lord: gefecht.simuliere (Wettlauf auf den Lord) mit dem Heer + n neue Einheiten; Wert =
                siegwert x (Fortschritt nachher - vorher), Fortschritt = Anteil des Lord-Lebens, den das Heer schafft
    Heimwache - feindliche Raider (Truppen bis HEIM_R um eigene Gebaeude): Wert der bedrohten Gebaeude, wenn die Heimwache
                + n neue Einheiten das Gefecht gewinnt (B-239)
  Zweite Waehrung: Bauern am Feuer (jede Werbung nimmt einen; raids.FEUER_MIN bleiben). Ist das Feuer knapper als das Gold,
  zaehlt Wert je Bauer, sonst Wert je Gold. Gold frei = Gold - Ruecklage der Wirtschaft (ohne Heereskasse, B-141) - HEER_GOLD_RAND.
  Fehlt fuer die beste Art ein Gebaeude (Kaserne 9, Waffenlager 11, Stall 35) oder die Waffe, meldet der Einkaeufer den Wunsch
  (self.wunsch) - gebaut wird in erstes_spiel (ruestung_kaufen), Waffen kauft er selbst am Markt (Spielbefehl 38, 5er-Los).
Nichts hier ist eine Sollzahl. Die Bremsen aus 1019k (Assassinen ohne Ziel) bleiben als Wert 0: ohne lohnendes Ziel kauft
der Raid keine Assassinen. Alte Wege: erstes_spiel einkauf=alt, nur fuer den Vergleichslauf (danach weg, Grundregel 8).
"""
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
D = os.path.join(HIER, "..", "daten")

import kaufrechnung as KR

KASERNE, SOELDNER, STALL, WAFFENLAGER = 9, 8, 35, 11
RT_NAME = {17: "bogen", 18: "armbrust", 19: "speer", 20: "pike", 21: "keule", 22: "schwert", 23: "leder", 24: "ruestung"}
RAID_ARTEN = (71, 73)             # zuenden / abreissen
REITER = 74
FELDZUG_ARTEN = (22, 23, 24, 25, 26, 27, 28, 70, 72, 73, 75, 76)
HEIM_ARTEN = (22, 23, 24, 25, 26, 27, 28, 70, 72, 75, 76)
TRUPPE = {22, 23, 24, 25, 26, 27, 28, 37, 55, 70, 71, 72, 73, 74, 75, 76}
HEIM_R = 20                       # Raider so nah an eigenen Gebaeuden bedrohen sie (Startwert, UNGEMESSEN)
LORD_UMKREIS = 25                 # wie feldzug.LORD_UMKREIS: Wachen so nah am Lord kaempfen mit
ARBEITER_WERT = 10.0              # Gold-Gegenwert eines gejagten Arbeiters (wie raids.SCHUETZE_WERT, Startwert, UNGEMESSEN)
FELDZUG_ALLE = 10                 # Runden zwischen zwei Feldzug-Rechnungen (14 Arten x Stufen x Gefechtsrechnung)
STUFEN = (1, 2, 4, 8, 16)         # so viele auf einmal probiert der Feldzug je Art
RAND = 150                        # erstes_spiel.HEER_GOLD_RAND: Rest, der nie angefasst wird (Startwert)
FEUER_MIN = 2                     # raids.FEUER_MIN


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def spielwerte_live(spielordner=None):
    """Spielwerte aus dem laufenden Spiel lesen (spielwerte.py) und als daten/spielwerte_<stempel>.json sichern; geht das
    nicht, die juengste live-Datei. Gibt das Dict wie kaufrechnung.spielwerte_laden."""
    try:
        import spielwerte as SW
        q, lies = SW.quelle_live()
        w = SW.lesen(lies)
        sch = SW.schuss(lies)
        w.update(SW.abgeleitet(w, sch, SW.hacken(lies)))
        aus = {"erstellt": time.strftime("%Y-%m-%d %H:%M:%S"), "quelle": q, "marke": "abgelesen (Speicher, Aufbau aus Ghidra OpenSHC)",
               "aufzaehlungen": {"UT": SW.UT, "BT": SW.BT, "RT": SW.RT, "ET": SW.ET},
               "namen": SW.namen(spielordner or SW.SPIELORDNER), "tabellen": w, "schuss": sch,
               "code_konstanten": SW.CODE_KONSTANTEN, "gegenproben": SW.gegenproben(w)}
        import json
        pfad = os.path.join(D, time.strftime("spielwerte_%Y%m%d_%H%M%S.json"))
        json.dump(aus, open(pfad, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        aus["_pfad"] = pfad
        return aus
    except Exception:
        return KR.spielwerte_laden()


def gebaeude_wert(sw, typ):
    """Baukosten zu Marktpreisen: Holz, Stein (Kaufpreis je Stueck) + Gold (gebaeude.kosten: Holz, Stein, ?, ?, Gold)."""
    k = KR._w(sw, "gebaeude.kosten")
    if typ >= len(k):
        return 0.0
    kauf = KR._w(sw, "markt.kaufpreis_je5")
    z = k[typ]
    return z[0] * kauf[2] / 5.0 + z[1] * kauf[4] / 5.0 + (z[4] if len(z) > 4 else 0)


class Einkaeufer:
    def __init__(self, sp, sw, freunde=None):
        self.sp, self.sw = sp, sw
        self.freunde = freunde or (lambda sp_: {0, sp_})
        self.preise = KR.preise(sw)
        self.schaden, self.fern, self.leben, self.kalib = KR.schadenstabelle(sw)
        self.wunsch = {}                     # {"kaserne": True, "stall": True, "waffenlager": True} - fuer erstes_spiel
        self.runde = 0
        self._feldzug = (-99, [])            # (Runde, Bedarfe) - Feldzug-Rechnung alle FELDZUG_ALLE Runden
        self.letzte = []                     # Bedarfe der letzten Runde (fuer die Mitschrift / Pruefungen)

    # ---- Hilfen --------------------------------------------------------------------------------------------------------
    def _einheit(self, typ, x=0, y=0, leben=None):
        return dict(typ=typ, leben=leben if leben is not None else self.leben.get(typ, 1), x=x, y=y)

    def _simuliere(self, wir, sie, fokus=None, bis=None):
        import gefecht
        return gefecht.simuliere(wir, sie, self.schaden, bis=bis or gefecht.BIS, fokus=fokus, fern=self.fern)

    def gebaeude_da(self, G, typ):
        return next((n for n, g in G.items() if g.get("besitzer") == self.sp and g.get("typ") == typ), None)

    def siegwert(self, G, L, besitzer):
        """Was ein Sieg ueber besitzer wert ist: alle seine Gebaeude zu Baukosten + alle seine Truppen zu Preisen."""
        w = sum(gebaeude_wert(self.sw, g["typ"]) for g in G.values() if g.get("besitzer") == besitzer)
        w += sum(self.preise.get(e["typ"], {}).get("gold", 0) for e in L.values() if e.get("besitzer") == besitzer and e["typ"] in TRUPPE)
        return w

    # ---- Bedarfe -------------------------------------------------------------------------------------------------------
    def bedarf_raid(self, L, G, lage, posten_ort, reiter_ziele=None, reiter_da=0):
        """[(typ, wert_je_einheit, n_max, text)] - je Art das beste Ziel vom Posten aus; ein Ziel traegt eine Einheit."""
        import raids
        fr = self.freunde(self.sp)
        ziele = [(n, g) for n, g in G.items() if g.get("besitzer") not in fr and g["typ"] in raids.WERT and g.get("feuer", 0) == 0
                 and g.get("abkling", 0) == 0]
        aus = []
        for typ in RAID_ARTEN:
            if typ not in self.preise:
                continue
            preis = self.preise[typ]["gold"]
            saldi = []
            for n, g in ziele:
                p = lage.plan(posten_ort, (g["x"], g["y"]), typ, self.leben.get(typ, 1)) if lage is not None else None
                if p is None:
                    continue
                wert = gebaeude_wert(self.sw, g["typ"]) * (1.0 - p["p_tod"]) - preis * p["p_tod"]
                if wert > 0:
                    saldi.append(wert)
            if saldi:
                saldi.sort(reverse=True)
                aus.append((typ, saldi[0], len(saldi), "Raid: %d lohnende Ziele, bestes %.0f Gold" % (len(saldi), saldi[0])))
        if REITER in self.preise and reiter_ziele is not None and reiter_ziele > reiter_da:
            aus.append((REITER, ARBEITER_WERT * min(3, reiter_ziele - reiter_da), reiter_ziele - reiter_da,
                        "Reiterjagd: %d Ziele fuer %d Reiter (ARBEITER_WERT UNGEMESSEN)" % (reiter_ziele, reiter_da)))
        return aus

    def bedarf_feldzug(self, L, G, heer, gold_frei, feuer_frei):
        """[(typ, wert_je_einheit, n, text)] - je Art die Stufe n mit dem besten Siegfortschritt je Gold."""
        import gefecht
        fr = self.freunde(self.sp)
        lords = [(n, e) for n, e in L.items() if e["typ"] == gefecht.LORD and e.get("besitzer") not in fr and e.get("leben", 0) > 0]
        if not lords:
            return []
        ln, lord = min(lords, key=lambda x: x[0])
        lp = (lord["x"], lord["y"])
        sie = [dict(typ=gefecht.LORD, leben=lord["leben"], x=lp[0], y=lp[1], steht=True)]
        sie += [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=False) for e in L.values()
                if e.get("besitzer") == lord.get("besitzer") and e["typ"] in TRUPPE and e["typ"] != gefecht.LORD and e.get("leben", 0) > 0
                and (schach((e["x"], e["y"]), lp) <= LORD_UMKREIS or (e["typ"] in gefecht.FERN_REICH and schach((e["x"], e["y"]), lp) <= gefecht.FERN_REICH[e["typ"]]))]
        wir0 = [dict(typ=L[n]["typ"], leben=L[n]["leben"], x=lp[0] - 12, y=lp[1]) for n in heer if n in L]
        siegwert = self.siegwert(G, L, lord.get("besitzer"))

        def fortschritt(wir):
            if not wir:
                return 0.0
            _, rest_lord, _, gefallen = self._simuliere(wir, sie, fokus=0)
            return 1.0 if gefallen else 1.0 - rest_lord / float(max(1, lord["leben"]))
        f0 = fortschritt(wir0)
        aus = []
        for typ in FELDZUG_ARTEN:
            if typ not in self.preise or typ not in self.leben:
                continue
            preis = self.preise[typ]["gold"]
            best = None
            for n in STUFEN:
                if n * preis > gold_frei or n > feuer_frei:
                    break
                f = fortschritt(wir0 + [self._einheit(typ, lp[0] - 12, lp[1]) for _ in range(n)])
                wert = siegwert * (f - f0)
                if wert <= 0:
                    continue
                if best is None or wert / (n * preis) > best[1] / (best[0] * preis):
                    best = (n, wert, f)
            if best:
                n, wert, f = best
                aus.append((typ, wert / n, n, "Feldzug: %d x -> Fortschritt %.2f -> %.2f (Sieg %.0f Gold)" % (n, f0, f, siegwert)))
        return aus

    def bedarf_heim(self, L, G, heim_ort):
        """[(typ, wert_je_einheit, n, text)] - feindliche Raider an eigenen Gebaeuden; Wert = bedrohte Gebaeude, wenn die
        Heimwache + n Neue das Gefecht gewinnt."""
        fr = self.freunde(self.sp)
        eigene = [(g["x"], g["y"], gebaeude_wert(self.sw, g["typ"])) for g in G.values() if g.get("besitzer") == self.sp]
        raider = [e for e in L.items() if False]
        raider = [e for n, e in L.items() if e.get("besitzer") not in fr and e["typ"] in TRUPPE and e["typ"] != 55 and e.get("leben", 0) > 0
                  and any(schach((e["x"], e["y"]), (x, y)) <= HEIM_R for x, y, _ in eigene)]
        if not raider:
            return []
        bedroht = sum(w for x, y, w in eigene if any(schach((e["x"], e["y"]), (x, y)) <= HEIM_R for e in raider))
        sie = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"], steht=False) for e in raider]
        mitte = (sum(e["x"] for e in raider) // len(raider), sum(e["y"] for e in raider) // len(raider))
        wache = [dict(typ=e["typ"], leben=e["leben"], x=e["x"], y=e["y"]) for e in L.values()
                 if e.get("besitzer") == self.sp and e["typ"] in TRUPPE and e["typ"] != 55 and schach((e["x"], e["y"]), heim_ort) <= 40]
        if wache and self._simuliere(wache, sie)[3]:
            return []                                        # die Heimwache schafft es schon
        aus = []
        for typ in HEIM_ARTEN:
            if typ not in self.preise or typ not in self.leben:
                continue
            preis = self.preise[typ]["gold"]
            for n in STUFEN:
                if self._simuliere(wache + [self._einheit(typ, mitte[0] - 6, mitte[1]) for _ in range(n)], sie)[3]:
                    aus.append((typ, (bedroht - n * preis * 0.0) / n, n, "Heimwache: %d Raider bedrohen %.0f Gold, %d x reichen" % (len(raider), bedroht, n)))
                    break
        return aus

    # ---- Einkauf ---------------------------------------------------------------------------------------------------------
    def einkaufen(self, st, L, G, vorrat, ruecklage_gold, lage=None, heer=(), reiter_ziele=None, reiter_da=0, heim_ort=None,
                  gesperrt=()):
        """Gibt (werbungen [(typ, n, gebaeude_nr)], marktkaeufe [RT], ereignisse). gesperrt: Arten, die diese Runde nicht
        gekauft werden (Loewen am Posten, Hunger: erstes_spiel)."""
        self.runde += 1
        ereignis = []
        gold_frei = int(st.get("gold", 0)) - int(ruecklage_gold) - RAND
        feuer_frei = int(st.get("feuer", 0)) - FEUER_MIN
        if gold_frei <= 0 or feuer_frei <= 0:
            return [], [], ereignis
        posten = self.gebaeude_da(G, SOELDNER)
        kaserne = self.gebaeude_da(G, KASERNE)
        stall = self.gebaeude_da(G, STALL)
        waffenlager = self.gebaeude_da(G, WAFFENLAGER)
        bedarfe = []
        if posten is not None:
            posten_ort = (G[posten]["x"], G[posten]["y"])
            bedarfe += [b + ("raid",) for b in self.bedarf_raid(L, G, lage, posten_ort, reiter_ziele, reiter_da)]
        if self.runde - self._feldzug[0] >= FELDZUG_ALLE:
            self._feldzug = (self.runde, self.bedarf_feldzug(L, G, heer, gold_frei, feuer_frei))
        bedarfe += [b + ("feldzug",) for b in self._feldzug[1]]
        if heim_ort is not None:
            bedarfe += [b + ("heim",) for b in self.bedarf_heim(L, G, heim_ort)]
        self.letzte = bedarfe
        if not bedarfe:
            return [], [], ereignis
        # Reihenfolge: ist das Feuer knapper als das Gold, zaehlt Wert je Bauer, sonst Wert je Gold
        billigst = min(self.preise[t]["gold"] for t, *_ in bedarfe if t in self.preise)
        feuer_knapp = feuer_frei < gold_frei // max(1.0, billigst)
        bedarfe.sort(key=lambda b: -(b[1] if feuer_knapp else b[1] / max(1.0, self.preise[b[0]]["gold"])))
        werbungen, markt = [], []
        self.wunsch = {}
        for typ, wert, n_max, text, aufgabe in bedarfe:
            if typ in gesperrt or typ not in self.preise:
                continue
            p = self.preise[typ]
            if wert <= 0:
                continue
            geb = posten if p["gebaeude"] == SOELDNER else kaserne
            if geb is None or (p["stall"] and stall is None) or (p["waren"] and waffenlager is None):
                if p["gebaeude"] == KASERNE and kaserne is None:
                    self.wunsch["kaserne"] = True
                if p["stall"] and stall is None:
                    self.wunsch["stall"] = True
                if p["waren"] and waffenlager is None:
                    self.wunsch["waffenlager"] = True
                ereignis.append("EINKAUF wartet auf %s fuer %s (%s, %.0f Gold je Einheit)" % (
                    ", ".join(k for k in ("kaserne", "stall", "waffenlager") if self.wunsch.get(k)), KR.name(self.sw, typ), text, wert))
                continue
            n = min(int(n_max), gold_frei // max(1, int(p["gold"])), feuer_frei)
            if n <= 0:
                continue
            # Waffen: je Einheit ein Stueck je RT im Lager - fehlt es, ein 5er-Los am Markt (naechste Runde werben)
            fehlt = [rt for rt, _ in p["waren"] if int(vorrat.get(RT_NAME.get(rt, ""), 0)) < n]
            if fehlt:
                kauf5 = KR._w(self.sw, "markt.kaufpreis_je5")
                for rt in fehlt:
                    if rt not in markt and gold_frei >= kauf5[rt]:
                        markt.append(rt)
                        gold_frei -= kauf5[rt]
                        ereignis.append("EINKAUF Markt: 5 %s (%d Gold) fuer %s - %s" % (RT_NAME.get(rt, rt), kauf5[rt], KR.name(self.sw, typ), text))
                continue
            werbungen.append((typ, n, geb))
            gold_frei -= n * int(p["gold"])
            feuer_frei -= n
            ereignis.append("EINKAUF %s: %d x %s (je %.0f Gold, Wert %.0f je Einheit) - %s" % (
                aufgabe, n, KR.name(self.sw, typ), p["gold"], wert, text))
            if gold_frei <= 0 or feuer_frei <= 0:
                break
        return werbungen, markt, ereignis
