# -*- coding: utf-8 -*-
"""B-250 Gehirn, Baustein 1: Trefferprognose (Daniel 25.10.2026 20:01 "ja"; Auge von Daniel um 20:00 abgenommen).

Aus EINEM Takt-Schnappschuss des Auges (auge.Schnappschuss / auge.Protokoll) und den Spielwerten (spielwerte_*.json, live)
vorhersagen, welche Einheit in den naechsten H Takten wie viel Leben verliert und durch wen. Nichts davon ist geschaetzt:
  Geschosse in der Luft  - sre_bahn/sre_rest_takte (Flugformel aus dem Code, Auge AU4): Landetakt; Opfer = die anvisierte
                           Einheit (unitID), wenn sie am Zielfeld (+-1) steht, sonst jede Feindeinheit auf dem Zielfeld;
                           Schaden = Geschosstabelle je Geschossart (Pfeil arrow_damage, Bolzen bolt_damage, Stein
                           stone_damage, SRE 25.10. 09:59) an der Zielart
  Schuetzen              - sre_naechster_schuss_takte (Phasen-Restdauer, Auge AU6) + Flugzeit (Abstand / Geschosstempo) bis
                           zum Ziel shootTargetedUnit; danach je takt.schuss_zyklus ein weiterer Schuss im Fenster
  Nahkampf               - Zustand 106 (US_MELEE_ATTACK) mit attackedUnitID: melee_damage[Angreifer][Opfer] je Takt (Schaden
                           je TAKT, SRE P23) fuer alle Takte des Fensters
Je Opfer wird die Summe auf sein Leben gedeckelt. Ausgabe: [dict(opfer, art, besitzer, verlust, quellen[...])].
Nicht enthalten (Baustein 2): Kaempfe, die im Fenster erst beginnen (Anmarsch), Zielwechsel (+44-46 Takte, AU6), Feuer.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

GESCHOSS_TABELLE_ET = {1: "einheit.arrow_damage", 7: "einheit.bolt_damage", 33: "einheit.stone_damage"}
GESCHOSS_TABELLE_UT = {22: "einheit.arrow_damage", 70: "einheit.arrow_damage", 74: "einheit.arrow_damage",
                       23: "einheit.bolt_damage", 72: "einheit.stone_damage"}
NAHKAMPF = 106
FELDER_JE_TAKT = 0.7          # Pfeil 0,7 Felder je Takt (Auge AU4, gemessen); Bolzen/Stein aus sre_mikroschritte_je_takt


def _w(sw, name):
    return sw["tabellen"][name]["werte"]


def schach(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class Gehirn:
    def __init__(self, sw):
        self.sw = sw
        self.melee = _w(sw, "einheit.melee_damage")
        self.tab = {k: _w(sw, k) for k in set(GESCHOSS_TABELLE_ET.values())}
        zt = sw["tabellen"].get("takt.schuss_zyklus")
        self.zyklus = zt["werte"] if zt else []
        bt = sw["tabellen"].get("bewegung.takte_je_feld")
        self.tempo = bt["werte"] if bt else []           # Baustein 2: Takte je Feld je Art (8 x (Stufe + 1), SRE P13)

    NAH_R = 2                 # Nahkampf wirkt bis 2 Felder (Auge AU14: Mikro-Abstand hoechstens 23)

    def _nah(self, a, o):
        return float(self.melee[a["unitType"]][o["unitType"]]) if a["unitType"] < len(self.melee) else 0.0

    def _geschoss_schaden(self, tabelle, opfer_typ):
        t = self.tab.get(tabelle)
        return float(t[opfer_typ]) if t and opfer_typ < len(t) else 0.0

    def prognose(self, s, horizont=30, einheiten=None, begegnung=True):
        """s: auge-Schnappschuss. Gibt {opfer_id: dict(verlust, quellen, art, besitzer, leben)} fuer (t, t+horizont]."""
        E = {e["id"]: e for e in (einheiten if einheiten is not None else s.einheiten_liste())}
        aus = {}

        def treffer(opfer, menge, quelle):
            o = E.get(opfer)
            if o is None or menge <= 0 or o.get("dying"):
                return
            z = aus.setdefault(opfer, {"verlust": 0.0, "quellen": [], "art": o["unitType"], "besitzer": o["owner"],
                                       "leben": o["health"]})
            z["verlust"] += menge
            z["quellen"].append(quelle)

        # 1 Geschosse in der Luft
        for g in s.geschosse():
            tab = GESCHOSS_TABELLE_ET.get(g.get("entityType"))
            if tab is None or g.get("sre_zustand") not in (None, "fliegt"):
                continue
            rest = g.get("sre_rest_takte")
            if rest is None or rest > horizont:
                continue
            ziel = tuple(g.get("ziel_feld") or ())
            opfer = g.get("unitID")
            if not (opfer in E and ziel and schach(tuple(E[opfer]["feld"]), ziel) <= 1):
                kand = [e for e in E.values() if ziel and tuple(e["feld"]) == ziel and e["owner"] != g.get("owner")]
                opfer = kand[0]["id"] if kand else None
            if opfer is not None:
                treffer(opfer, self._geschoss_schaden(tab, E[opfer]["unitType"]),
                        {"art": "geschoss", "uid": g.get("uid"), "schuetze": g.get("unitID_OR_seaGullID"), "takt": rest})
        # 2 Schuetzen: naechster Schuss + Flugzeit, dann je Zyklus
        for e in E.values():
            tab = GESCHOSS_TABELLE_UT.get(e["unitType"])
            ziel = e.get("shootTargetedUnit") or 0
            n = e.get("sre_naechster_schuss_takte")
            if tab is None or not ziel or ziel not in E or n is None or e.get("dying"):
                continue
            if E[ziel]["owner"] == e["owner"]:
                continue
            flug = int(round(schach(tuple(e["feld"]), tuple(E[ziel]["feld"])) / FELDER_JE_TAKT))
            zyk = self.zyklus[e["unitType"]] if e["unitType"] < len(self.zyklus) and self.zyklus[e["unitType"]] else None
            t = n + flug
            while t <= horizont:
                treffer(ziel, self._geschoss_schaden(tab, E[ziel]["unitType"]),
                        {"art": "schuss", "schuetze": e["id"], "takt": t})
                if not zyk:
                    break
                t += zyk
        # 3 Nahkampf: Schaden je Takt; stirbt das Opfer im Fenster (Summe aller Angreifer), schlaegt jeder Angreifer die
        #   restlichen Takte auf den naechsten Feind bis NAH_R Felder (Pruefstein 191847: 58.215 Leben Nahkampf ohne Vorhersage,
        #   die Angreifer hatten ein anderes Ziel - das alte war tot)
        paare = []
        for e in E.values():
            if e.get("state") != NAHKAMPF or e.get("dying"):
                continue
            o = e.get("attackedUnitID") or 0
            if o not in E or E[o]["owner"] == e["owner"]:
                continue
            paare.append((e, o))
        dps = {}
        for e, o in paare:
            dps[o] = dps.get(o, 0.0) + self._nah(e, E[o])
        for e, o in paare:
            je = self._nah(e, E[o])
            tot_nach = E[o]["health"] / dps[o] if dps[o] > 0 else horizont + 1
            if tot_nach >= horizont:
                treffer(o, je * horizont, {"art": "nahkampf", "angreifer": e["id"], "je_takt": je})
                continue
            treffer(o, je * tot_nach, {"art": "nahkampf", "angreifer": e["id"], "je_takt": je})
            p = tuple(e["feld"])
            naechste = sorted((schach(p, tuple(x["feld"])), x["id"]) for x in E.values()
                              if x["id"] != o and x["owner"] != e["owner"] and x["owner"] not in (0,) and not x.get("dying")
                              and schach(p, tuple(x["feld"])) <= self.NAH_R)
            if naechste:
                n2 = naechste[0][1]
                je2 = self._nah(e, E[n2])
                treffer(n2, je2 * (horizont - tot_nach), {"art": "nahkampf_folge", "angreifer": e["id"], "je_takt": je2})
        if begegnung:
            self._begegnungen(E, aus, treffer, horizont, {e["id"] for e, _ in paare})
        for z in aus.values():
            z["verlust"] = min(z["verlust"], float(z["leben"]))
        return aus

    SUCH_R_FEIN = 200         # Register L77: Nahkaempfer in Angriffshaltung suchen bis 200 Feinmass um sich (~25 Felder)
    FERN_ARTEN = (22, 23, 70, 72, 74, 76)       # Schuetzen kaempfen nur, wenn ein Feind direkt anliegt

    @staticmethod
    def fein(a, b):
        """Abstand in Feinmass wie das Spiel (8 je Feld, Naeherung max + 0,4*min^2/max - Register L75/P15)."""
        dx, dy = abs(a[0] - b[0]) * 8, abs(a[1] - b[1]) * 8
        mx, mn = max(dx, dy), min(dx, dy)
        return mx + (0.4 * mn * mn / mx if mx else 0.0)

    def _begegnungen(self, E, aus, treffer, horizont, kaempfen):
        """Baustein 2 (B-250): Kaempfe, die im Fenster erst beginnen - nach der Feindsuche des Spiels (Register L77, P15,
        findNearestEnemyAndHeadTowardsIt 0x0054A7B0): eine freie Einheit sucht in ihrem eigenen Suchtakt (sicht.feind_takt:
        64 bzw. 128) den naechsten Feind bis SUCH_R_FEIN und laeuft hin; direkt Benachbarte (bis NAH_R) greift sie sofort an.
        Beginn = halber Suchtakt (Phase unbekannt) + (Abstand - NAH_R) x Takte je Feld; danach melee_damage je Takt."""
        ft = self.sw["tabellen"].get("sicht.feind_takt")
        such = ft["werte"] if ft else []
        for e in E.values():
            if e["id"] in kaempfen or e.get("dying") or e["unitType"] >= len(self.melee):
                continue
            if not any(self.melee[e["unitType"]]):
                continue
            p = tuple(e["feld"])
            feinde = [x for x in E.values() if x["owner"] != e["owner"] and x["owner"] != 0 and not x.get("dying")
                      and x["unitType"] < len(self.melee)]
            if not feinde:
                continue
            ziel = min(feinde, key=lambda x: (self.fein(p, tuple(x["feld"])), x["id"]))
            d = schach(p, tuple(ziel["feld"]))
            if d <= self.NAH_R:
                an = 0
            else:
                st = such[e["unitType"]] if e["unitType"] < len(such) else 0
                if e["unitType"] in self.FERN_ARTEN or not st or self.fein(p, tuple(ziel["feld"])) > self.SUCH_R_FEIN:
                    continue
                tpf = self.tempo[e["unitType"]] if e["unitType"] < len(self.tempo) and self.tempo[e["unitType"]] else 16
                an = st // 2 + (d - self.NAH_R) * tpf
            if an >= horizont:
                continue
            je = self._nah(e, ziel)
            treffer(ziel["id"], je * (horizont - an), {"art": "begegnung", "angreifer": e["id"], "je_takt": je, "takt": an})
            # SRE AU18 Punkt 6 (processMeleeInitiation): das Opfer bekommt den Waehlenden als Ziel, wenn es noch keins hat,
            # und schlaegt ab Kontakt zurueck
            if ziel["id"] not in kaempfen and not (ziel.get("attackedUnitID") or 0) and ziel["unitType"] < len(self.melee):
                je_r = self._nah(ziel, e)
                treffer(e["id"], je_r * (horizont - an), {"art": "begegnung_gegen", "angreifer": ziel["id"], "je_takt": je_r, "takt": an})
