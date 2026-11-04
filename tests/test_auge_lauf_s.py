"""B-142: Lauf S ohne Spiel: Ablauf einer Szene, jeder Abbruchgrund, Regel-Pruefer, Wechselprobe."""
from __future__ import annotations

import json

import numpy as np
import pytest

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.analysis.auge_feldkarte import FELDLISTE, Feldkarte
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_s as ls


KARTE = Feldkarte.laden(feldliste=FELDLISTE)


class Spiel:
    """Takte laufen mit der Uhr, solange keine Pause ist. Gesetzte Einheiten stehen 1 Feld weiter als angegeben, wie im Spiel."""

    def __init__(self, tmp, **f):
        self.f, self.tmp = f, tmp
        self.jetzt, self.t, self.tempo, self.pausiert, self.rest = 0.0, 100, 1000, 0, 0.0
        self.log, self.protokoll, self.gestartet = [], [], []
        self.einheiten = []
        self.pfad = None
        self.nr = 0
        self.stand = {"fehlend": f.get("fehlend", 0), "gemischt": 0}
        self.tod_ab = None
        self.tod_typen = None
        self.gebaeude_liste = []
        self.speicher = {}
        self.haltungen = {}
        self.fern = 0
        self.hoehe = np.zeros((400, 400), dtype=np.int32)
        self.linien_abgelehnt = f.get("linien_abgelehnt", 0)
        self.gebaeude_abgelehnt = f.get("gebaeude_abgelehnt", 0)

    def uhr(self):
        return self.jetzt

    def ruhe(self, d):
        self.jetzt += d
        if self.pausiert or self.f.get("stillstand"):
            return
        self.rest += d * min(self.tempo, 825)
        while self.rest >= 1:
            self.rest -= 1
            self.t += 1
            if self.tod_ab is not None and self.t >= self.tod_ab and not self.f.get("steintod_bleibt"):
                self.einheiten = [e for e in self.einheiten if not (e["besitzer"] in self.tod and (self.tod_typen is None or e["typ"] in self.tod_typen))]
                self.tod, self.tod_ab, self.tod_typen = set(), None, None

    def takt(self):
        return self.t

    def haltung(self, trupp):
        return self.haltungen.get(trupp, 1)

    def besatzung(self, nr):
        return 0 if self.f.get("steigt_nicht_ein") else 9

    def kachel(self, x, y):
        return 1000 * y + x

    def platzkarte(self, mapper, groesse, x0, y0, x1, y1, sp=1):
        return ["+" * (x1 - x0 + 1)] * (y1 - y0 + 1)

    def feld(self, gruppe, name):
        KARTE.adresse(gruppe, name)  # sonder19_g: Ein falscher Feldname fiel erst im Lauf auf
        return 7000, 100

    def pech_liste(self, sp):
        return [{"nr": 5 + i, "uid": 50 + i, "x": c["baue"]["x"], "y": c["baue"]["y"]} for i, c in enumerate(c for c in self.log if isinstance(c, dict) and "baue" in c)]

    def gebaeude(self, sp=1):
        return [dict(g) for g in self.gebaeude_liste if sp is None or g["besitzer"] == sp]

    def peek(self, adr, n=1):
        return [self.speicher.get(adr, 0)]

    def befehl(self, c, warte=0.8, bis=None):
        self.log.append(c)
        if "pause" in c:
            self.pausiert = 1 if c["pause"] else 0
        if "tempo" in c:
            self.tempo = c["tempo"]
        self.ruhe(0.01)
        return []

    def liste(self, cmds, warte=1.0):
        self.tod = getattr(self, "tod", set())
        for c in cmds:
            self.log.append(c)
            if "setzeEinheit" in c:
                e = c["setzeEinheit"]
                if self.f.get("fehlt_einer") and self.nr == 3:
                    self.nr += 1
                    continue
                self.nr += 1
                assert self.pausiert, "gesetzt wird im angehaltenen Spiel"
                self.einheiten.append({"nr": self.nr, "uid": 1000 + self.nr, "typ": e["typ"], "besitzer": e["spieler"], "x": e["x"] + 1, "y": e["y"] + 1, "leben": 100, "trupp": 0})
                for _ in range(e.get("anzahl", 1) - 1):
                    self.nr += 1
                    self.einheiten.append({"nr": self.nr, "uid": 1000 + self.nr, "typ": e["typ"], "besitzer": e["spieler"], "x": e["x"] + 1, "y": e["y"] + 1, "leben": 100, "trupp": 0})
            if "angriff" in c:
                for e in self.einheiten:
                    if e["nr"] in c["angriff"]["einheiten"]:
                        e["trupp"] = 1000 + e["nr"]
            if "spielbefehl" in c and c["spielbefehl"]["nr"] == 25:
                if self.linien_abgelehnt > 0:
                    self.linien_abgelehnt -= 1
                else:
                    for x, y in ls.linie_felder(c["spielbefehl"]["werte"]):
                        self.hoehe[y, x] = 90
            if "spielbefehl" in c and c["spielbefehl"]["nr"] == 70 and not self.f.get("haltung_wirkt_nicht"):
                t, w = c["spielbefehl"]["werte"]
                self.haltungen[t] = w
            if "setzeGebaeude" in c:
                z = c["setzeGebaeude"]
                assert self.pausiert, "gesetzt wird im angehaltenen Spiel"
                if self.gebaeude_abgelehnt > 0:
                    self.gebaeude_abgelehnt -= 1
                elif not self.f.get("kein_gebaeude") or z["mapper"] != self.f["kein_gebaeude"]:
                    from selfaware.game.ucp.bauen import NACH_TYP
                    typ = next((t for t, v in NACH_TYP.items() if v["mapper"] == z["mapper"]), z["mapper"])
                    self.gebaeude_liste.append({"nr": 1000 + len(self.gebaeude_liste), "uid": 5000 + len(self.gebaeude_liste), "typ": typ, "x": z["x"], "y": z["y"], "besitzer": z["spieler"]})
            if "baue" in c and c["baue"]["mapper"] == ls.MAPPER_TUNNEL and not self.f.get("kein_eingang"):
                self.gebaeude_liste.append({"nr": 2000 + len(self.gebaeude_liste), "uid": 6000 + len(self.gebaeude_liste), "typ": 85, "x": c["baue"]["x"], "y": c["baue"]["y"], "besitzer": c["player"]})
            if "toeteAlle" in c:
                self.geraeumt = getattr(self, "geraeumt", []) + [self.t]
                t = c["toeteAlle"]
                if isinstance(t, dict):
                    assert t.get("ohneLord") or t["typen"] == [55]  # den Lord nimmt nur der ausdrueckliche Befehl
                    self.tod_typen = set(t["typen"])
                    t = t["spieler"]
                self.tod.add(t)
                self.tod_ab = self.t + 30
        self.ruhe(0.01)

    def einheiten_alle(self):
        return [dict(e) for e in self.einheiten]

    def raster(self):
        frei = np.zeros((400, 400), dtype=bool)
        frei[50:350, 50:350] = True
        return frei, self.hoehe.copy(), np.zeros((400, 400), dtype=np.int32)

    # Rekorder
    def fehler(self):
        return None

    def starten(self, name, tempo, streng=False, messen=True, felder=False, warte_ms=0):
        self.gestartet.append({"name": name, "tempo": tempo, "streng": streng, "warte_ms": warte_ms, "pausiert": self.pausiert, "tempo_schon": self.tempo == tempo})
        self.pfad = str(self.tmp / f"{name}.auge")

    def laeuft(self):
        return True

    def beenden(self):
        self.log.append("aufzeichnung_beendet")
        if not self.f.get("kein_treffer"):
            for e in [x for x in self.einheiten if x["nr"] < 900][:2]:  # ab 900: Lords und Bauern des Gefechts
                e["leben"] = 90
        return dict(self.stand)


def lauf_von(g):
    return ls.LaufS(g, g, g, g.protokoll.append, uhr=g.uhr, ruhe=g.ruhe)


def test_nahkampf_setzt_alle_paare_im_stand_und_raeumt_ab(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_fahren(lauf_von(g), ls.SZENEN["nahkampf"])
    assert e["einheiten"] == 190 * 2 + 1
    s = g.gestartet[0]
    assert s["streng"] and s["warte_ms"] == 5 and s["pausiert"] and s["tempo_schon"] and s["tempo"] == 40
    assert e["bis"] - e["von"] >= ls.GRENZE_NAH
    assert not g.einheiten and e["abraeumen_takte"] >= 30  # abgeraeumt, die Dauer ist gemessen
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    assert {x["rolle"] for x in plan["einheiten"]} == {"a", "b", "kontrolle"} and all("nr" in x and "uid" in x for x in plan["einheiten"])


def test_paare_stehen_beieinander_und_fremde_weiter_weg():
    class L:
        class s:
            @staticmethod
            def raster():
                frei = np.ones((400, 400), dtype=bool)
                return frei, np.zeros((400, 400)), np.zeros((400, 400))
    p = ls.aufbau_nahkampf(L)["einheiten"]
    a = {x["paar"]: x for x in p if x["rolle"] == "a"}
    b = {x["paar"]: x for x in p if x["rolle"] == "b"}
    assert len(a) == 190
    for i in a:
        assert max(abs(a[i]["x"] - b[i]["x"]), abs(a[i]["y"] - b[i]["y"])) == 1
    for i in list(a)[:40]:
        assert min(max(abs(a[i]["x"] - b[j]["x"]), abs(a[i]["y"] - b[j]["y"])) for j in b if j != i) >= 4
    k = next(x for x in p if x["rolle"] == "kontrolle")
    assert all(max(abs(k["x"] - x["x"]), abs(k["y"] - x["y"])) >= 60 for x in p if x is not k)


def test_schuetze_hat_sein_ziel_am_naechsten():
    class L:
        class s:
            @staticmethod
            def raster():
                return np.ones((400, 400), dtype=bool), np.zeros((400, 400)), np.zeros((400, 400))
    p = ls.aufbau_beschuss(L)["einheiten"]
    a = [x for x in p if x["rolle"] == "a"]
    b = [x for x in p if x["rolle"] == "b"]
    assert len(a) == 6 * 19
    for s in a[:30]:
        d = sorted((max(abs(s["x"] - z["x"]), abs(s["y"] - z["y"])), z["paar"]) for z in b)
        assert d[0] == (8, s["paar"]) and d[1][0] > 8


def test_fehlender_takt_bricht_ab(tmp_path):
    with pytest.raises(lf.Abbruch, match="Takt fehlt"):
        ls.szene_fahren(lauf_von(Spiel(tmp_path, fehlend=1)), ls.SZENEN["nahkampf"])


def test_gefecht_raeumt_ohne_lord_und_bauern(tmp_path):
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900 + i, "uid": 900 + i, "typ": t, "besitzer": p, "x": 20, "y": 20, "leben": 100} for i, (t, p) in enumerate(((55, 1), (55, 2), (56, 1)))]
    l = lauf_von(g)
    l.gefecht = True
    e = ls.szene_fahren(l, ls.SZENEN["nahkampf_g"])
    assert e["einheiten"] == 171 * 2 + 1 and sorted(x["typ"] for x in g.einheiten) == [55, 55, 56]
    assert 55 not in {c["setzeEinheit"]["typ"] for c in g.log if isinstance(c, dict) and "setzeEinheit" in c}
    assert e["bis"] - e["von"] >= ls.GRENZE_NAH_G


def test_im_editor_raeumt_das_abraeumen_alles(tmp_path):
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900, "uid": 900, "typ": 55, "besitzer": 1, "x": 20, "y": 20, "leben": 100}, {"nr": 901, "uid": 901, "typ": 56, "besitzer": 2, "x": 20, "y": 20, "leben": 100}]
    ls.abraeumen(lauf_von(g))
    assert g.einheiten == [] and {"toeteAlle": 1} in g.log and {"toeteAlle": 2} in g.log


def test_fern_maske_sperrt_nur_um_spieler():
    frei = np.ones((400, 400), dtype=bool)
    m = ls.fern_maske(frei, [{"besitzer": 1, "x": 100, "y": 200}, {"besitzer": 0, "x": 300, "y": 300}], 60)
    assert not m[200, 100] and not m[200, 160] and m[200, 161] and not m[140, 100] and m[139, 100] and m[300, 300]
    assert frei.all()


def test_lord_szene_merkt_das_ende(tmp_path):
    g = Spiel(tmp_path)
    lord = {"nr": 900, "uid": 900, "typ": 55, "besitzer": 2, "x": 100, "y": 100, "leben": 100}
    g.einheiten = [lord]
    l = lauf_von(g)
    l.gefecht = True
    ruhe_alt = g.ruhe

    def ruhe(d):
        ruhe_alt(d)
        befohlen = any(isinstance(c, dict) and c.get("player") == 2 and "angriff" in c for c in g.log)
        if befohlen and not g.pausiert:
            lord["x"], lord["y"] = next(c["angriff"]["lauf"] for c in g.log if isinstance(c, dict) and "angriff" in c)
            lord["leben"] = 0 if g.t > g_start["t"] + 50 else lord["leben"]
            if lord["leben"] == 0:
                g.speicher[lf.GAMEOVER] = 1
        else:
            g_start["t"] = g.t
    g_start = {"t": 0}
    g.ruhe = ruhe
    l.ruhe = ruhe
    e = ls.szene_lord(l)
    assert e["gefallen"] and e["ende_gemerkt"] and e["gameover"] == 1 and not e["per_befehl"]
    assert any(isinstance(c, dict) and c.get("menue") == ls.HAUPTMENUE for c in g.log)
    a = next(c for c in g.log if isinstance(c, dict) and "angriff" in c)
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    mx, my = plan["mitte"]
    assert a["player"] == 2 and a["angriff"] == {"einheiten": [900], "lauf": [mx, my]} and max(abs(mx - 100), abs(my - 100)) >= 6
    ritter = plan["einheiten"]
    assert len(ritter) == 8 and all(x["typ"] == 28 and x["spieler"] == 1 and max(abs(x["x"] - mx), abs(x["y"] - my)) == 2 for x in ritter)
    assert len({(x["x"], x["y"]) for x in ritter}) == 8


def test_freie_mitte_hat_einen_freien_rand_und_abstand():
    frei = np.zeros((400, 400), dtype=bool)
    frei[100:103, 105:125] = True  # zu schmal
    frei[200:205, 100:105] = True  # genau 5 x 5
    assert ls.freie_mitte(frei, 102, 102) == (102, 202)
    assert ls.freie_mitte(np.zeros((400, 400), dtype=bool), 10, 10) is None
    frei = np.ones((400, 400), dtype=bool)
    x, y = ls.freie_mitte(frei, 100, 100)
    assert max(abs(x - 100), abs(y - 100)) == 6


def test_lord_steht_nicht_gemerkt_ist_kein_ende(tmp_path):
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900, "uid": 900, "typ": 55, "besitzer": 2, "x": 100, "y": 100, "leben": 100}]
    l = lauf_von(g)
    e = ls.szene_lord(l)
    assert e["per_befehl"] and e["gefallen"] and not e["ende_gemerkt"]  # er blieb oben: Er faellt per Befehl, und das steht dabei
    assert {"toeteAlle": {"spieler": 2, "typen": [55]}} in g.log
    assert e["bis"] - e["von"] >= ls.LORD_WEG


def test_lord_faellt_nicht_ist_ein_fund(tmp_path):
    g = Spiel(tmp_path, steintod_bleibt=True)
    g.einheiten = [{"nr": 900, "uid": 900, "typ": 55, "besitzer": 2, "x": 100, "y": 100, "leben": 100}]
    e = ls.szene_lord(lauf_von(g))
    assert e["per_befehl"] and not e["gefallen"] and not e["ende_gemerkt"] and e["bis"] - e["von"] >= ls.LORD_WEG + ls.LORD_GRENZE


def test_szenen_mischen_geht_nicht():
    assert ls.bank_von(["nahkampf_g", "lord_g"]) and not ls.bank_von(["nahkampf", "last"])
    with pytest.raises(lf.Fehler):
        ls.bank_von(["nahkampf", "nahkampf_g"])


def test_aus_einem_test_startet_kein_echter_lauf(monkeypatch):
    def nie(n):
        raise AssertionError("Der Lauf ist bis zum Spiel gekommen")
    monkeypatch.setattr(lf, "pruefe_laufinstanz", nie)  # faellt die Sperre weg, wird dieser Test rot, ohne das Spiel anzufassen
    with pytest.raises(lf.Fehler):
        ls.los(2, ["nahkampf"])


def test_gefecht_gibt_beiden_spielern_einen_startplatz():
    assert ls.STARTPLAETZE[:2] == (0, 1) and set(ls.STARTPLAETZE[2:]) == {246}
    g = []

    class K:
        def peek(self, adr):
            return [ls.HAUPTMENUE] if not g else [lf.IN_PARTIE]

        def befehl(self, c, warte=0):
            g.append(c)
    ls.gefecht_oeffnen(K(), ruhe=lambda d: None)
    start = next(c for c in g if "eigenesGefecht" in c)
    assert start["startliste"] == list(ls.STARTPLAETZE) and start["menschen"] == 2 and start["gegner"] == 0


def test_richtige_lords_prueft_besitzer_und_ort():
    class S:
        def __init__(self, e):
            self.e = e

        def einheiten_alle(self):
            return self.e
    hier = {"typ": 55, "besitzer": 1, "x": 165, "y": 107}
    dort = {"typ": 55, "besitzer": 2, "x": 251, "y": 127}
    assert ls.richtige_lords(S([hier, dort]))
    assert not ls.richtige_lords(S([hier]))
    assert not ls.richtige_lords(S([hier, dict(dort, besitzer=3)]))
    assert not ls.richtige_lords(S([hier, dict(dort, x=20, y=20)]))


def test_modul_bekommt_toete_ohne_lord_und_jede_anweisung():
    roh = lf.TOETE_ANKER + "\n    local sp = tonumber(cmd.toeteAlle)\n" + lf.ART_ANKER + "\n"
    neu = lf._mit_art(lf._mit_toete(roh))
    assert neu.index(lf.TOETE_NEU[1]) < neu.index("local sp = tonumber") and neu.index(lf.ART_NEU) < neu.index(lf.ART_ANKER)
    assert lf._mit_art(lf._mit_toete(neu)) == neu  # zweimal einspielen aendert nichts
    assert lf._mit_toete("ohne") == "ohne" and lf._mit_art("ohne") == "ohne"


def test_reichweite_jede_bahn_hat_ihr_ziel_und_den_befehl(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_fahren(lauf_von(g), ls.SZENEN["reichweite"])
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    laeufer = [x for x in plan["einheiten"] if x["rolle"] == "laeufer"]
    ziele = {x["paar"]: x for x in plan["einheiten"] if x["rolle"] == "ziel"}
    assert len(laeufer) == 19 and plan["eben"] is True and all(ziele[x["paar"]]["typ"] == 59 and ziele[x["paar"]]["x"] - x["x"] == ls.FELDER_BAHN and ziele[x["paar"]]["spieler"] == 2 for x in laeufer)
    bef = [c for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert len(bef) == 19 and all(c["player"] == 1 and c["angriff"]["ziel"] == ziele[x["paar"]]["nr"] and c["angriff"]["einheiten"] == [x["nr"]] for c, x in zip(bef, laeufer))
    assert e["bis"] - e["von"] >= ls.GRENZE_BAHN


def test_reichweite_nimmt_unebene_bahnen_nur_wenn_es_sein_muss():
    class L:
        class s:
            @staticmethod
            def raster():
                return np.ones((400, 400), dtype=bool), np.indices((400, 400))[1] // 2, np.zeros((400, 400))
    p = ls.aufbau_reichweite(L)
    assert p["eben"] is False and len([x for x in p["einheiten"] if x["rolle"] == "laeufer"]) == 19


def test_schussweite_leiter_rund_um_den_tabellenwert(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_fahren(lauf_von(g), ls.SZENEN["schussweite"])
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    laeufer = [x for x in plan["einheiten"] if x["rolle"] == "laeufer"]
    ziele = {x["paar"]: x for x in plan["einheiten"] if x["rolle"] == "ziel"}
    assert len(laeufer) == 36 and all(ziele[x["paar"]]["x"] - x["x"] == x["abstand"] for x in laeufer)
    assert {x["abstand"] for x in laeufer if x["typ"] == 72} == {9, 16, 17, 18, 19, 20} and {x["abstand"] for x in laeufer if x["typ"] == 22} == {27, 52, 53, 54, 55, 56}
    assert sum(1 for c in g.log if isinstance(c, dict) and "angriff" in c) == 36


def test_schussweite_zaehlt_nur_das_befohlene_ziel():
    e = [{"rolle": "laeufer", "paar": 0, "typ": 22, "nr": 1, "abstand": 54}, {"rolle": "ziel", "paar": 0, "typ": 59, "nr": 2}, {"rolle": "laeufer", "paar": 1, "typ": 22, "nr": 3, "abstand": 55}, {"rolle": "ziel", "paar": 1, "typ": 59, "nr": 4}]
    g = [{"schuetze": 1, "ziel": 2, "start": (0, 0), "punkt": (432, 0)}, {"schuetze": 3, "ziel": 2, "start": (0, 8), "punkt": (440, 0)}]
    z = ar.schussweite_werten(g, e)
    assert z[0]["auf_ziel"] == 1 and z[0]["abstand_mikro"] == 432 and z[0]["urteil"] == "schiesst"
    assert z[1]["auf_ziel"] == 0 and z[1]["andere"] == 1 and z[1]["urteil"] == "kein Treffer"
    assert ar.schussweite_grenzen(z) == {22: {"weitester_schuss": 54, "naechster_ohne": 55, "eindeutig": True}}
    z2 = [{"typ": 22, "abstand": 54, "auf_ziel": 0}, {"typ": 22, "abstand": 55, "auf_ziel": 1}]
    assert not ar.schussweite_grenzen(z2)[22]["eindeutig"]


def test_schussweite_pfeil_liegt_zwischen_den_gemessenen_grenzen(tmp_path):
    e = ls.szene_fahren(lauf_von(Spiel(tmp_path)), ls.SZENEN["schussweite_pfeil"])
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    laeufer = [x for x in plan["einheiten"] if x["rolle"] == "laeufer"]
    assert len(laeufer) == 36 and {x["typ"] for x in laeufer} == {22, 70, 74} and min(x["abstand"] for x in laeufer) == 28 and max(x["abstand"] for x in laeufer) == 50


def test_geschoss_zwischen_zwei_rahmen_gelandet_zaehlt_als_gelandet():
    class Karte:
        @staticmethod
        def adresse(b, f):
            o = {"logicalState": 0, "entityType": 2, "unitID": 4, "unitID_OR_seaGullID": 6, "owner": 8, "uid": 10, "targetX": 14, "targetY": 16, "microX": 18, "microY": 20}[f.split(".")[-1]]
            return (1000 + o, 4 if f.endswith("uid") else 2, 32, 3)

    class R:
        def __init__(self, t):
            self.takt, self.bereich, self.rein = t, 0, True

    def eintrag(da):
        return np.array([0] * 16, dtype="<i2").tobytes() + np.array([da, 1, 2, 1, 1, 7, 0, 80, 0, 0, 0, 0, 0, 0, 0, 0], dtype="<i2").tobytes() + bytes(32)

    class Auf:
        namen = ["DAT_EntityState"]
        bereiche = [(0, 1000)]

        def __init__(self, pfad):
            pass

        @staticmethod
        def staende():
            return [(R(10), eintrag(2), None), (R(14), eintrag(2), None), (R(20), bytes(96), None)]
    import selfaware.tools.analysis.auge_auswertung as aa
    alt = aa.Aufzeichnung
    aa.Aufzeichnung = Auf
    try:
        g = ar.geschosse_lesen("x", Karte)
    finally:
        aa.Aufzeichnung = alt
    assert len(g) == 1 and g[0]["von"] == 10 and g[0]["bis"] == 14 and g[0]["schuetze"] == 1 and g[0]["ziel"] == 2 and g[0]["art"] == "pfeil"


def test_vorhalt_nennt_den_abstand_bei_abschuss_und_einschlag():
    r = []
    for i in range(5):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s["mx"][2], s["my"][2] = 80, 8 * i
        r.append((100 + i, s))
    g = [{"von": 100, "bis": 104, "punkt": (80, 32)}]
    assert ar._vorhalt(g, r, 2) == {"punkt_zum_laeufer_abschuss": 32, "punkt_zum_laeufer_einschlag": 0}


def test_laufen_trupp_laeuft_ueber_den_gruppenbefehl(tmp_path):
    g = Spiel(tmp_path)
    ls.szene_fahren(lauf_von(g), ls.SZENEN["laufen_trupp"])
    bef = [c for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert len(bef) == 38 and all(c["player"] == 1 and len(c["angriff"]["einheiten"]) == 1 and "lauf" in c["angriff"] for c in bef)
    assert not any(isinstance(c, dict) and "einheit_ziel" in c for c in g.log)


def test_laufziel_wendet_am_wendepunkt(tmp_path):
    g = Spiel(tmp_path)
    p = {"einheiten": [{"rolle": "pendel", "nr": 7, "wende": [[10, 30], [10, 10]], "weiter": 0}, {"rolle": "schuetze", "nr": 8}]}
    g.einheiten = [{"nr": 7, "x": 10, "y": 20, "besitzer": 2, "typ": 26}]
    l = lauf_von(g)
    assert ls.pendeln(l, p) is False and not any(isinstance(c, dict) and "einheit_ziel" in c for c in g.log)
    g.einheiten[0]["y"] = 30
    assert ls.pendeln(l, p) is False and p["einheiten"][0]["weiter"] == 0  # noch keine 8 Takte seit dem letzten Nachsehen
    g.t += 8
    assert ls.pendeln(l, p) is False and p["einheiten"][0]["weiter"] == 1
    assert [c for c in g.log if isinstance(c, dict) and "einheit_ziel" in c] == [{"einheit_ziel": {"nr": 7, "x": 10, "y": 10}}]


def test_laufziel_schuetzen_haben_ihr_ziel_und_alle_einen_laeufer(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_fahren(lauf_von(g), ls.SZENEN["laufziel"])
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    s = {x["paar"]: x for x in plan["einheiten"] if x["rolle"] == "schuetze"}
    z = {x["paar"]: x for x in plan["einheiten"] if x["rolle"] == "pendel"}
    assert len(s) == 6 and all(z[i]["x"] - s[i]["x"] == ls.ABSTAND_PENDEL and z[i]["typ"] == ls.PENDLER for i in s)
    assert sum(1 for c in g.log if isinstance(c, dict) and "einheit_ziel" in c) >= 6


def test_haltung_erst_gruppe_dann_haltung_dann_feind(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_haltung(lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    wachen = [x for x in plan["einheiten"] if x["rolle"] == "wache"]
    feinde = {x["fall"]: x for x in plan["einheiten"] if x["rolle"] == "feind"}
    assert len(wachen) == 15 and {(x["typ"], x["haltung"], x["abstand"]) for x in wachen} == {(t, h[0], h[2]) for t in ls.HALTUNG_ARTEN for h in ls.HALTUNGEN}
    assert all(feinde[x["fall"]]["x"] - x["x"] == x["abstand"] and feinde[x["fall"]]["y"] == x["y"] and feinde[x["fall"]]["spieler"] == 2 for x in wachen)
    arten = [("trupp" if "angriff" in c else "haltung" if "spielbefehl" in c else "feind") for c in g.log if isinstance(c, dict) and ("angriff" in c or "spielbefehl" in c or ("setzeEinheit" in c and c["setzeEinheit"]["spieler"] == 2))]
    assert arten == ["trupp"] * 15 + ["haltung"] * 15 + ["feind"] * 15
    assert all(c["spielbefehl"]["werte"][1] in (0, 1, 2) for c in g.log if isinstance(c, dict) and "spielbefehl" in c)


def test_haltung_zwei_szenen_decken_alle_faelle(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    a = ls.SZENEN["haltung"](l)
    b = ls.SZENEN["haltung2"](l)
    pa = json.load(open(a["pfad"] + ".plan.json", encoding="utf-8"))
    pb = json.load(open(b["pfad"] + ".plan.json", encoding="utf-8"))
    alle = [(x["typ"], x["haltung"], x["abstand"]) for p in (pa, pb) for x in p["einheiten"] if x["rolle"] == "wache"]
    assert pa["szene"] == "haltung" and pb["szene"] == "haltung2" and len(alle) == 15 and len(set(alle)) == 15
    assert sum(1 for x in pa["einheiten"] if x["rolle"] == "wache") <= 11 and sum(1 for x in pb["einheiten"] if x["rolle"] == "wache") <= 11  # mehr passt nicht auf die Karte


def test_haltung_ohne_wirkung_bricht_ab(tmp_path):
    with pytest.raises(lf.Abbruch, match="Befehl 70"):
        ls.szene_haltung(lauf_von(Spiel(tmp_path, haltung_wirkt_nicht=True)))


def schuss_reihe(leben):
    aus = []
    for i, w in enumerate(leben):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s["da"][[1, 2]], s["typ"][[1, 2]] = 1, 22
        s["leben"][1], s["leben"][2] = 1000, w
        aus.append((100 + i, s))
    return aus


def test_geschoss_trifft_nur_wenn_das_ziel_leben_verliert():
    r = schuss_reihe([500] * 3 + [400] * 7)
    g = [{"art": "pfeil", "schuetze": 1, "ziel": 2, "von": 95, "bis": 103, "start": (0, 0), "punkt": (40, 0)}, {"art": "pfeil", "schuetze": 1, "ziel": 2, "von": 100, "bis": 109, "start": (0, 0), "punkt": (45, 0)}, {"art": "pfeil", "schuetze": 1, "ziel": 2, "von": 100, "bis": None, "start": (0, 0), "punkt": (45, 0)}]
    w = ar.geschosse_werten(g, r)["pfeil"]
    assert w["flogen"] == 3 and w["gelandet"] == 2 and w["traf"] == 1 and w["verfehlt"] == 1 and w["mikro_je_takt"] == 5.0 and w["abstand_hoechstens"] == 45


def test_abstand_wie_im_spiel():
    assert ar._abstand(0, 0, 80, 0) == 80 and ar._abstand(0, 0, 0, 0) == 0 and ar._abstand(0, 0, 80, 40) == 80 + (2 * 40 // 5) * 40 // 80


def reichweite_reihe(orte, leben):
    aus = []
    for i, (x, w) in enumerate(zip(orte, leben)):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s["da"][[1, 2]], s["typ"][1], s["typ"][2] = 1, 22, 59
        s["mx"][1], s["my"][1], s["mx"][2], s["my"][2] = x, 40, 480, 40
        s["leben"][2] = w
        aus.append((100 + i, s))
    return aus


def test_reichweite_liest_lauf_halt_und_schusstakt():
    r = reichweite_reihe([0] * 2 + list(range(0, 320, 2)) + [318] * 40 + [330] * 20, [1000] * 170 + [900] * 20 + [800] * 32)
    e = [{"rolle": "laeufer", "paar": 0, "typ": 22, "nr": 1}, {"rolle": "ziel", "paar": 0, "typ": 59, "nr": 2}]
    tab = {"tempo": np.full(80, 1)}
    z = ar.reichweite_werten(r, e, tab)[0]
    assert z["abstand_mikro"] == 162 and z["abstand_felder"] == 20.2 and z["felder_gelaufen"] == 39.8 and z["treffer"] == 2 and z["abstaende"] == {20: 1} and z["werte"] == {100: 2} and z["urteil"] == "trifft" and z["tempo_soll"] == 16


def test_reichweite_ohne_treffer_ist_ein_fund():
    r = reichweite_reihe([0] * 10, [1000] * 10)
    z = ar.reichweite_werten(r, [{"rolle": "laeufer", "paar": 0, "typ": 22, "nr": 1}, {"rolle": "ziel", "paar": 0, "typ": 59, "nr": 2}], {"tempo": np.full(80, 1)})[0]
    assert z["urteil"] == "kein Treffer" and z["erster_schritt"] is None and z["takte_je_feld"] is None


def test_haltung_prueft_beide_seiten_des_radius():
    def reihe(zieht):
        s0 = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s0["mx"][1], s0["my"][1] = 84, 84
        s1 = {k: v.copy() for k, v in s0.items()}
        if zieht:
            s1["mx"][1] = 92
        return [(100, s0), (130, s1)]
    w = {"rolle": "wache", "nr": 1, "x": 10, "y": 10, "typ": 28}
    assert ar.haltung_werten(reihe(True), [dict(w, wert=2, abstand=24, haltung="aggressiv")])[0]["urteil"] == "bestaetigt"
    assert ar.haltung_werten(reihe(False), [dict(w, wert=2, abstand=24, haltung="aggressiv")])[0]["urteil"] == "weicht ab"
    assert ar.haltung_werten(reihe(False), [dict(w, wert=2, abstand=26, haltung="aggressiv")])[0]["urteil"] == "bestaetigt"
    assert ar.haltung_werten(reihe(True), [dict(w, wert=2, abstand=26, haltung="aggressiv")])[0]["urteil"] == "weicht ab"
    assert ar.haltung_werten(reihe(True), [dict(w, wert=0, abstand=4, haltung="stehen")])[0]["urteil"] == "weicht ab"
    assert ar.haltung_werten(reihe(True), [dict(w, wert=1, abstand=6, haltung="defensiv")])[0]["urteil"] == "weicht ab"
    assert ar.haltung_werten(reihe(True), [dict(w, wert=1, abstand=4, haltung="defensiv")])[0]["urteil"] == "bestaetigt"
    assert ar.haltung_werten(reihe(True), [dict(w, wert=1, abstand=4, haltung="defensiv")])[0]["nach_takten"] == 30


def test_gefecht_erster_rahmen_alt_wird_gezaehlt_nicht_versteckt():
    w = int(TAB["nah"][24, 27])
    r = reihen_von([1000, 1000, 1000 - 2 * w, 1000 - 3 * w], [1000] * 4)
    z = next(x for x in ar.nahkampf_werten(r, PAAR, TAB, erster_rahmen_alt=True) if x["schlaeger"] == 27 or x["opfer"] == 24)
    r2 = next(x for x in ar.nahkampf_werten(r, PAAR, TAB) if x["opfer"] == 24)
    assert r2["urteil"] == "weicht ab"
    z = next(x for x in ar.nahkampf_werten(r, PAAR, TAB, erster_rahmen_alt=True) if x["opfer"] == 24)
    assert z["urteil"] == "bestaetigt" and z["erster_doppelt"] is True
    r3 = reihen_von([1000, 1000 - w, 1000 - 3 * w, 1000 - 4 * w], [1000] * 4)  # doppelt nicht am Anfang bleibt ein Fund
    assert next(x for x in ar.nahkampf_werten(r3, PAAR, TAB, erster_rahmen_alt=True) if x["opfer"] == 24)["urteil"] == "weicht ab"
    assert not next(x for x in ar.nahkampf_werten(r3, PAAR, TAB, erster_rahmen_alt=True) if x["opfer"] == 24)["erster_doppelt"]


def test_kanal_behaelt_den_spieler_des_befehls():
    k = lf.EchterKanal.__new__(lf.EchterKanal)
    k._sende = lambda d, w: d["befehle"]
    k._neue_id = lambda: 7
    assert k.liste([{"player": 2, "x": 1}, {"x": 2}]) == [{"player": 2, "x": 1, "id": 7}, {"player": 1, "x": 2, "id": 7}]


def test_gefecht_sonderfaelle_bekommen_waren_und_alle_posten(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    l.gefecht = True
    e = ls.SZENEN["sonder_g"](l)
    assert e["kein_platz"] == []
    waren = [c for c in g.log if isinstance(c, dict) and "ware" in c]
    assert len(waren) == 4 and {c["player"] for c in waren} == {1, 2}
    i = g.log.index(waren[0])
    assert all(g.log.index(c) > i for c in g.log if isinstance(c, dict) and "spielbefehl" in c)  # erst die Waren, dann die Mauern
    assert {"graben", "leiter", "turmgeraet", "schild", "hoehe", "tor", "oel"} == {k["posten"] for k in json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))["karte"]}
    arten = [c["angriff"].get("art") for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert arten.index(15) < arten.index(20)  # das Oel holen, dann erst werfen


def test_zweiter_durchgang_sonderfaelle_wie_der_code_es_verlangt(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    l.gefecht = True
    e = ls.SZENEN["sonder2_g"](l)
    assert e["kein_platz"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    ort = {k["posten"]: k for k in plan["karte"]}
    assert set(ort) == {"graben", "leiter", "kuh", "hunde", "pech", "oel", "tunnel"}
    bef = [c for c in g.log if isinstance(c, dict)]
    # Graben: geplant mit Flag 2 = 0, nicht der Editorweg
    planung = next(c["spielbefehl"]["werte"] for c in bef if c.get("spielbefehl", {}).get("nr") == 21)
    assert planung[3:] == [0x40000000, 0] and len(ort["graben"]["felder"]) == 9
    an = {c["angriff"].get("art"): c for c in bef if "angriff" in c and "art" in c["angriff"]}
    assert an[6]["player"] == 1 and an[7]["player"] == 2
    # Leiter und Mauerangriff nehmen die Feldnummer
    x, y = ort["leiter"]["x"], ort["leiter"]["y"]
    assert an[24]["angriff"]["a"] == 1000 * (y + 7) + x + 20
    x, y = ort["tunnel"]["x"], ort["tunnel"]["y"]
    assert an[23]["angriff"]["a"] == 1000 * (y + 11) + x + 24
    # Kuh: erst der Zaehler, dann der Wurf
    i = next(j for j, c in enumerate(bef) if c.get("poke") == 7100)
    assert bef[i]["wert"] == 5 and bef.index(an[22]) == i + 1
    # Oel: Pech in die Schmelze, holen, spaeter werfen
    assert any(c.get("poke", 0) > 7100 for c in bef) and bef.index(an[15]) < bef.index(an[20])
    # Pech: gebaut von Spieler 2, angezuendet ueber Nummer und uid
    assert sum(1 for c in bef if "baue" in c and c["player"] == 2) == 5
    assert an[34]["player"] == 2 and an[34]["angriff"]["a"] == 7 and an[34]["angriff"]["b"] == 52


def lauf_im_gefecht(tmp_path):
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900, "uid": 900, "typ": 55, "besitzer": 1, "x": 150, "y": 150, "leben": 100, "trupp": 0}]
    l = lauf_von(g)
    l.gefecht = True
    return g, l


def test_burgbereich_nur_nahe_der_eigenen_burg():
    class L:
        class s:
            @staticmethod
            def einheiten_alle():
                return [{"typ": 55, "besitzer": 1, "x": 100, "y": 100}, {"typ": 55, "besitzer": 2, "x": 300, "y": 300}]
    m = ls.burgbereich(L)(np.ones((400, 400), dtype=bool))
    assert not m[100, 100] and not m[100, 113] and m[100, 114] and m[100, 140] and not m[100, 141] and not m[300, 300]


def test_graben_und_hunde_im_burgbereich_von_spieler_1(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder3_g"](l)
    assert e["kein_platz"] == [] and any(x["typ"] == 55 for x in g.einheiten)  # der Lord bleibt
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    for k in plan["karte"]:
        assert 14 <= max(abs(k["x"] - 150), abs(k["y"] - 150)) <= 40
    p = next(c["spielbefehl"]["werte"] for c in g.log if isinstance(c, dict) and c.get("spielbefehl", {}).get("nr") == 21)
    assert p[3:] == [0x40000000, 0]
    an = {c["angriff"].get("art"): c for c in g.log if isinstance(c, dict) and "art" in c.get("angriff", {})}
    assert an[6]["player"] == 1 and an[7]["player"] == 2  # nur ein anderes Team schuettet zu
    assert g.log.index(an[6]) < g.log.index(an[7])
    assert g.geraeumt[0] >= ls.STARTTRUPPEN_TAKT  # sonst schiessen die Starttruppen auf die Opfer der Hunde (17 Pfeile, Lauf 21:41)
    assert not any(c.get("spielbefehl", {}).get("nr") == 74 for c in g.log if isinstance(c, dict))  # der setzt nur feststeckende Hunde dazu
    assert sum(1 for x in plan["einheiten"] if x.get("posten") == "hunde" and x["rolle"] == "opfer") > 5  # sonst kommen die Hunde nicht heraus
    lauf = next(c for c in g.log if isinstance(c, dict) and "lauf" in c.get("angriff", {}))
    assert lauf["player"] == 1 and g.log.index(an[6]) < g.log.index(lauf) < g.log.index(an[7])  # die Graeber gehen weg, bevor zugeschuettet wird


def test_pech_von_spieler_1_und_der_gegner_steht_darauf(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder4_g"](l)
    assert e["kein_platz"] == []
    b = [c for c in g.log if isinstance(c, dict)]
    assert sum(1 for c in b if "baue" in c and c["player"] == 1) == 5
    an = next(c for c in b if c.get("angriff", {}).get("art") == 34)
    assert an["player"] == 1
    lauf = next(c for c in b if "lauf" in c.get("angriff", {}))
    assert lauf["player"] == 2


def test_hoehe_mit_treppe_mauer_und_leiter_der_abstaende(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder3"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    wer = {x["paar"]: x for x in plan["einheiten"] if x.get("posten") == "hoehe" and x["rolle"] == "laeufer"}
    ziel = {x["paar"]: x for x in plan["einheiten"] if x.get("posten") == "hoehe" and x["rolle"] == "ziel"}
    assert [wer[i]["abstand"] for i in range(4)] == [38, 42, 46, 50] and all(ziel[i]["x"] == plan["karte"][3]["x"] + 6 + wer[i]["abstand"] for i in range(4))
    mapper = [c["spielbefehl"]["werte"][4] for c in g.log if isinstance(c, dict) and c.get("spielbefehl", {}).get("nr") == 25]
    assert 27 in mapper and 25 in mapper


def test_hoehe_ueber_die_leiter_und_dann_erst_der_schuss(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder5"](lauf_von(g))
    assert e["kein_platz"] == []
    bef = [c for c in g.log if isinstance(c, dict) and "angriff" in c]
    arten = [("leiter" if c["angriff"].get("art") == 24 else "lauf" if "lauf" in c["angriff"] else "ziel") for c in bef]
    assert arten == ["leiter", "lauf"] + ["ziel"] * 4
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    assert bef[0]["angriff"]["a"] == 1000 * (plan["karte"][0]["y"] + 7) + plan["karte"][0]["x"] + 20  # die Feldnummer


def test_tunnel_zweiter_lauf_raeumt_erst_nach_den_starttruppen(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    g.einheiten.append({"nr": 901, "uid": 901, "typ": 55, "besitzer": 2, "x": 250, "y": 250, "leben": 100, "trupp": 0})
    e = ls.SZENEN["sonder7_g"](l)
    assert e["kein_platz"] == [] and g.geraeumt[0] >= ls.STARTTRUPPEN_TAKT
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    assert {k["posten"] for k in plan["karte"]} == {"mauer", "abbruch"}
    k = next(k for k in plan["karte"] if k["posten"] == "abbruch")
    st = next(x for x in plan["einheiten"] if x["rolle"] == "stoerer")
    assert abs(st["x"] - (k["x"] + 11)) >= 6  # weiter als 5 Felder vom Graeber, sonst greift er von selbst an


def test_pruefer_zeigt_fremde_treffer_je_posten():
    s = {k: np.zeros(ar.PLAETZE, dtype=ar.FELDER[k][1]) for k in ar.FELDER}
    s["zustand"] = np.zeros(ar.PLAETZE, dtype=np.int16)
    for nr, typ, besitzer, x in ((5, 24, 2, 11), (6, 24, 2, 60), (7, 22, 1, 12), (8, 76, 1, 13)):
        s["da"][nr], s["typ"][nr], s["besitzer"][nr], s["mx"][nr], s["my"][nr], s["leben"][nr] = 2, typ, besitzer, x * 8, 80, 100
    s["schlaegt"][7] = 5  # fremd auf den Posten a
    s["da"][0], s["typ"][0], s["besitzer"][0], s["schlaegt"][0] = 2, 67, 0, 5  # Platz 0 ist nur eine Kopie
    s["schlaegt"][8] = 5  # im Plan: kein Fremder
    plan = {"karte": [{"posten": "a", "x": 10, "y": 8, "breite": 5, "hoehe": 5}, {"posten": "b", "x": 58, "y": 8, "breite": 5, "hoehe": 5}], "gebaeude": [],
            "einheiten": [{"nr": 5, "posten": "a", "typ": 24, "rolle": "opfer"}, {"nr": 8, "posten": "a", "typ": 76, "rolle": "taeter"}, {"nr": 6, "posten": "b", "typ": 24, "rolle": "opfer"}]}
    geschosse = [{"art": "pfeil", "schuetze": 7, "ziel": 6, "start": (480, 80)}, {"art": "pfeil", "schuetze": 7, "ziel": 6, "start": (480, 80)}, {"art": "feuer", "schuetze": 8, "ziel": 5, "start": (100, 80)}]
    a, b = ar.sonder_werten([(100, s), (101, s)], [], geschosse, plan)
    assert a["fremd"] == {"schlaeger": {"22/1": 2}, "geschosse": {}}
    assert b["fremd"] == {"schlaeger": {}, "geschosse": {"pfeil": 2}}


def test_nachlauf_editor_mauer_je_art_mit_feldnummer(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder8"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    ort = {k["posten"]: k for k in plan["karte"]}
    b = [c for c in g.log if isinstance(c, dict)]
    # Mauer je Art: von Spieler 2, Angriff mit der Feldnummer des Mittelstuecks
    wer = [x for x in plan["einheiten"] if x.get("posten") == "mauer_art"]
    assert [x["typ"] for x in wer if x["rolle"] == "taeter"] == list(ls.MAUER_ARTEN) and sum(1 for x in wer if x["rolle"] == "kreuz") == 1
    x0, y0 = ort["mauer_art"]["x"], ort["mauer_art"]["y"]
    an = {c["angriff"]["einheiten"][0]: c for c in b if c.get("angriff", {}).get("art") == 23}
    erster = next(x for x in wer if x["typ"] == 24)
    assert an[erster["nr"]]["angriff"]["a"] == 1000 * (y0 + 2) + x0 + 6
    wand = [c for c in b if c.get("spielbefehl", {}).get("nr") == 25]
    assert all(c["player"] == 2 for c in wand) and len(wand) >= 10
    assert len(ort["mauer_art"]["felder"]) == 9
    # Das Kreuz: Das Zielfeld hat drei Nachbarn
    kr = next(x for x in wer if x["rolle"] == "kreuz")
    assert an[kr["nr"]]["angriff"]["a"] == 1000 * (y0 + 19) + x0 + 6
    # Belagerungsturm mit Anweisung 23, nicht laufen
    t = next(x for x in plan["einheiten"] if x.get("posten") == "turmgeraet" and x["typ"] == 58)
    assert an[t["nr"]]["player"] == 1
    # Rammen mit 1, 2, 3, 4 Mann, alle bekommen den Gebaeudeangriff
    r = [x for x in plan["einheiten"] if x.get("posten") == "ramme" and x["typ"] == 59]
    assert [x["mann"] for x in r] == [1, 2, 3, 4]
    assert sum(1 for c in b if "gebaeude" in c.get("angriff", {}) and c["angriff"]["einheiten"][0] in {x["nr"] for x in r}) == 4
    # Abstand 24 und 26 vor dem Tor
    for n, d in (("tor_24", 24), ("tor_26", 26)):
        f = next(x for x in plan["einheiten"] if x.get("posten") == n)
        tor = next(x for x in plan["gebaeude"] if x.get("posten") == n)
        assert tor["x"] - f["x"] == d and tor["spieler"] == 2 and f["spieler"] == 1
    # Haltung stehen fuer genau einen Armbrustschuetzen
    assert any(c.get("spielbefehl", {}).get("nr") == 70 and c["spielbefehl"]["werte"][1] == 0 for c in b)
    # Trupp: 6 Schwertkaempfer in einem Befehl
    assert sum(1 for c in b if len(c.get("angriff", {}).get("einheiten", [])) == 6) == 2
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_kampf" and x["rolle"] == "feind")
    nah = [x for x in plan["einheiten"] if x.get("posten") == "trupp_kampf" and x["rolle"] == "trupp" and max(abs(x["x"] - k["x"]), abs(x["y"] - k["y"])) <= 2]
    assert len(nah) == 1  # nur einer steht in Reichweite


def test_steigung_nur_ansteigend_und_frei():
    frei = np.ones((30, 40), dtype=bool)
    h = np.full((30, 40), 8)
    assert ls.steigung(frei, h) is None
    h[5, 10:24] = np.arange(8, 22)
    assert ls.steigung(frei, h) == (5, 5)  # das erste Fenster: erst eben, dann 8 hoeher
    h2 = h.copy()
    h2[5, 15] = 5  # eine Delle: nicht nur ansteigend
    assert ls.steigung(frei, h2) is None
    f2 = frei.copy()
    f2[5, 12] = False
    assert ls.steigung(f2, h) is None


def test_nachlauf_gefecht_stein_oel_und_grenze(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    g.speicher[7100] = 150  # Lagerplatz von Spieler 1: feld() liefert im Prueffall Adresse 7000, Schritt 100
    e = ls.SZENEN["sonder8_g"](l)
    assert e["kein_platz"] == [] and g.geraeumt[0] >= ls.STARTTRUPPEN_TAKT
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    ware = [c for c in b if c.get("ware", {}).get("menge") == ls.STEIN_MENGE]
    assert len(ware) == 1 + len(ls.STEIN_TAKTE) and all(c["ware"]["typ"] == 4 and c["player"] == 1 for c in ware)  # Stein, kurz vor dem Bedarf
    befehl = next(c for c in b if c.get("spielbefehl", {}).get("nr") == 86)
    assert befehl["spielbefehl"]["werte"][0] and b.index(ware[0]) < b.index(befehl)
    assert sum(1 for x in plan["einheiten"] if x.get("posten") == "oel_stehen" and x["rolle"] == "oel") == 2  # einer bedient, einer traegt
    assert sum(1 for c in b if c.get("wert") == 20 and "poke" in c) == 3  # Pech in jede Schmelze
    haltung = [c["spielbefehl"]["werte"][1] for c in b if c.get("spielbefehl", {}).get("nr") == 70]
    assert sorted(haltung) == [0, 1, 2]
    gr = {x["rolle"]: x for x in plan["einheiten"] if x.get("posten") == "grenze"}
    assert max(abs(gr["nah"]["x"] - 150), abs(gr["nah"]["y"] - 150)) == 39 and max(abs(gr["weit"]["x"] - 150), abs(gr["weit"]["y"] - 150)) == 41
    assert gr["nah"]["typ"] == 24 and gr["weit"]["typ"] == 22


def test_nachlauf_pech_gegner_laufen_quer_durch(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder9_g"](l)
    assert e["kein_platz"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    k = plan["karte"][0]
    geher = [x for x in plan["einheiten"] if x["rolle"] == "geher"]
    assert len(geher) == 5 and all(x["spieler"] == 2 and x["y"] > k["y"] + 4 for x in geher)
    lauf = [c for c in g.log if isinstance(c, dict) and "lauf" in c.get("angriff", {}) and c["angriff"]["einheiten"][0] in {x["nr"] for x in geher}]
    assert len(lauf) == 5 and all(c["player"] == 2 and c["angriff"]["lauf"][1] < k["y"] + 4 for c in lauf)  # auf die andere Seite des Grabens


def test_lord_selbst_ohne_testbefehl(tmp_path):
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900 + i, "uid": 900 + i, "typ": 55, "besitzer": i + 1, "x": 150 + 100 * i, "y": 150 + 100 * i, "leben": 100, "trupp": 0} for i in range(2)]
    e = ls.szene_lord(lauf_von(g), "lord2_g", True)
    assert e["szene"] == "lord2_g" and not e["per_befehl"]
    assert not any(isinstance(c, dict) and isinstance(c.get("toeteAlle"), dict) and c["toeteAlle"].get("typen") == [55] for c in g.log)


def test_zweiter_nachlauf_editor(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder10"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    sp = [c for c in b if c.get("spielbefehl", {}).get("nr") == 25]
    assert sum(1 for c in sp if c["spielbefehl"]["werte"][4] == ls.TREPPE and c["player"] == 1) == 2  # je Turm eine Treppe von Spieler 1
    assert sum(1 for c in sp if c["player"] == 2) == 4  # Mauer links und rechts der beiden Tore
    ort = {k["posten"]: k for k in plan["karte"]}
    t = next(x for x in plan["gebaeude"] if x.get("posten") == "turm_oben")
    assert t["spieler"] == 1
    assert sum(1 for x in plan["einheiten"] if x.get("posten") == "tor_zu" and x["rolle"] == "feind") == 1 and not any(x.get("posten") == "tor_offen" and x["rolle"] == "feind" for x in plan["einheiten"])
    geher = [c for c in b if "lauf" in c.get("angriff", {}) and c["player"] == 2]
    assert len(geher) == 2 and all(c["angriff"]["lauf"][1] == ort[n]["y"] + 11 for c, n in zip(geher, ("tor_offen", "tor_zu")))
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_nah" and x["rolle"] == "feind")
    nah = [x for x in plan["einheiten"] if x.get("posten") == "trupp_nah" and x["rolle"] == "trupp" and max(abs(x["x"] - k["x"]), abs(x["y"] - k["y"])) <= 1]
    assert len(nah) == 1


def test_zweiter_nachlauf_gefecht(tmp_path):
    class S(Spiel):
        n = 0

        def peek(self, adr, n=1):
            if adr == ls.VERLUSTE:
                S.n += 1
                return [S.n] * n
            return super().peek(adr, n)
    g = S(tmp_path)
    g.einheiten = [{"nr": 900 + i, "uid": 900 + i, "typ": 55, "besitzer": i + 1, "x": 150 + 100 * i, "y": 150 + 100 * i, "leben": 100, "trupp": 0} for i in range(2)]
    l = lauf_von(g)
    l.gefecht = True
    e = ls.SZENEN["sonder10_g"](l)
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    gb = plan["gebaeude"]
    assert {x["typ"] for x in gb} == {1, 27, 66, 93}
    assert all(x["spieler"] == 1 for x in gb if x["typ"] in (1, 27, 66)) and all(x["spieler"] == 2 for x in gb if x["typ"] == 93)
    assert sum(x["typ"] == 66 for x in gb) == ls.ANGST_BAUTEN == sum(x["typ"] == 93 for x in gb)
    assert all(14 <= max(abs(x["x"] - 250), abs(x["y"] - 250)) <= 40 for x in gb if x["typ"] == 93)  # im Burgbereich von Spieler 2
    h = next(x for x in gb if x["typ"] == 1)
    an = next(c for c in b if "gebaeude" in c.get("angriff", {}))
    assert an["player"] == 2 and an["angriff"]["gebaeude"] == h["nr"]
    assert not any("poke" in c for c in b)
    k = [x for x in plan["einheiten"] if x["typ"] == 39]
    bef = [c for c in b if c.get("spielbefehl", {}).get("nr") == 86]
    assert len(bef) == 2 and bef[0]["spielbefehl"]["werte"][1] == 1 and bef[1]["spielbefehl"]["werte"] == [k[0]["nr"], 0]
    assert bef[0]["spielbefehl"]["werte"][0] == 1000 + k[1]["nr"]  # der Trupp des zweiten Katapults
    i0, i1 = b.index(bef[0]), b.index(bef[1])
    assert b[i0 - 1].get("ware", {}).get("typ") == 4 and b[i1 - 1].get("ware", {}).get("typ") == 4  # Stein kurz davor
    assert plan["verluste"]["vorher"]["verlust"] != plan["verluste"]["nachher"]["verlust"]
    v = [x for x in plan["einheiten"] if x.get("posten") == "verlust"]
    assert {(x["rolle"], x["spieler"], x["typ"]) for x in v} == {("opfer", 1, 24), ("taeter", 2, 28)}


def test_dritter_nachlauf_editor(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder12"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    ort = {k["posten"]: k for k in plan["karte"]}
    gb = {x["posten"]: x for x in plan["gebaeude"]}
    sp = [c["spielbefehl"]["werte"] for c in b if c.get("spielbefehl", {}).get("nr") == 25]
    for n in ("turm_eck", "turm_mitte", "turm4_weg"):
        t = gb[n]
        linie = [w for w in sp if w[4] == 25 and w[1] == w[3] and ort[n]["y"] <= w[1] < ort[n]["y"] + ort[n]["hoehe"] and ort[n]["x"] <= w[0] <= ort[n]["x"] + 3]
        assert len(linie) == 1 and linie[0][2] == t["x"] - 1  # bis vor den Turm, nicht darauf
    laeufe = {tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {})}
    for n in ("turm_eck", "turm_mitte", "turm_treppe", "turm4_weg"):
        assert (gb[n]["x"], gb[n]["y"]) in laeufe  # das Eckfeld
    d = next(x for x in plan["einheiten"] if x.get("posten") == "turm_direkt")
    assert (d["x"], d["y"]) == (gb["turm_direkt"]["x"], gb["turm_direkt"]["y"])
    for n, a in (("tor_17", 17), ("tor_18", 18)):
        f = next(x for x in plan["einheiten"] if x.get("posten") == n)
        assert gb[n]["x"] - f["x"] == a
    for n in ("tor_offen_w", "tor_zu_w"):
        assert [gb[n]["x"] - 10, gb[n]["y"] + 2, gb[n]["x"] - 1, gb[n]["y"] + 2, 25, 13] in sp  # linke Wand bis vor das Tor
    assert any(x.get("posten") == "tor_zu_w" and x["rolle"] == "feind" for x in plan["einheiten"]) and not any(x.get("posten") == "tor_offen_w" and x["rolle"] == "feind" for x in plan["einheiten"])
    o = ort["trupp_ring"]
    assert (o["x"] + 34, o["y"] + 4) in laeufe  # im Ring
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_ring" and x["rolle"] == "feind")
    assert sum(max(abs(x["x"] - k["x"]), abs(x["y"] - k["y"])) <= 1 for x in plan["einheiten"] if x.get("posten") == "trupp_ring" and x["rolle"] == "trupp") == 1


def test_vierter_nachlauf_treppe_mit_stufen(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder13"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    assert plan["mauer_fehlt"] == [] and plan["mauer_wiederholt"] == 0
    b = [c for c in g.log if isinstance(c, dict)]
    gb = {x["posten"]: x for x in plan["gebaeude"]}
    sp = [c["spielbefehl"]["werte"] for c in b if c.get("spielbefehl", {}).get("nr") == 25]
    laeufe = {tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {})}
    for n, zeile in (("turm_eck", 0), ("turm_mitte", 1), ("turm4_weg", 0)):
        t = gb[n]
        mauer = next(w for w in sp if w[4] == 25 and w[2] == t["x"] - 1 and w[1] == t["y"] + zeile)
        assert (t["x"], t["y"]) in laeufe  # das Eckfeld
        treppe = next(w for w in sp if w[4] == ls.TREPPE and w[1] == t["y"] + zeile and w[0] == mauer[0] - 1)  # beginnt neben dem Mauerende
        assert treppe[0] - treppe[2] == 4  # 5 Stufen, weg von der Mauer
    wer = [x for x in plan["einheiten"] if x.get("posten") == "turm_eck"]
    assert len(wer) == 8
    assert not any(x["y"] == gb["turm_eck"]["y"] for x in wer)  # keiner steht auf der Linie, sonst baut das Spiel sie nicht
    o = next(k for k in plan["karte"] if k["posten"] == "tor_17")
    f = next(x for x in plan["einheiten"] if x.get("posten") == "tor_17")
    assert gb["tor_17"]["x"] - f["x"] == 17 and gb["tor_17"]["x"] == o["x"] + 30
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_ring" and x["rolle"] == "feind")
    assert sum(max(abs(x["x"] - k["x"]), abs(x["y"] - k["y"])) <= 1 for x in plan["einheiten"] if x.get("posten") == "trupp_ring" and x["rolle"] == "trupp") == 1
    r = next(k for k in plan["karte"] if k["posten"] == "trupp_ring")
    assert (r["x"] + 34, r["y"] + 4) in laeufe  # im Ring


def test_fuenfter_nachlauf_befehl_erst_nach_dem_bau(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder14"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    gb = {x["posten"]: x for x in plan["gebaeude"]}
    ort = {k["posten"]: k for k in plan["karte"]}
    laeufe = [tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {})]
    assert (ort["nur_mauer"]["x"] + 9, ort["nur_mauer"]["y"] + 2) in laeufe  # auf der Mauer
    assert (gb["turm_eck"]["x"], gb["turm_eck"]["y"]) in laeufe  # Eckfeld
    assert (gb["turm_mitte"]["x"] + 1, gb["turm_mitte"]["y"] + 1) in laeufe  # Mitte
    # der Befehl kommt erst nach dem Bau: beim Start kein Laufbefehl, die Stufe liegt hinter der Flaechenkarte
    for n, f, _, _ in ls.sonder14(lauf_von(Spiel(tmp_path))):
        if n in ("nur_mauer", "turm_eck", "turm_mitte", "turm4_weg"):
            *_, jetzt, stufen = f(100, 100)
            assert jetzt() == [] and stufen[0][0] == ls.LAUF_NACH_BAU >= 100
    t = [x for x in plan["einheiten"] if x.get("posten") == "trupp_ohne_flaeche" and x["rolle"] == "trupp"]
    turm = gb["trupp_ohne_flaeche"]
    assert (t[0]["x"], t[0]["y"]) == (turm["x"] + 1, turm["y"] + 1)  # die erste Einheit in der Turmmitte
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_ohne_flaeche" and x["rolle"] == "feind")
    assert max(abs(t[1]["x"] - k["x"]), abs(t[1]["y"] - k["y"])) <= 1  # der zweite kaempft
    an = next(c for c in b if c.get("angriff", {}).get("lauf") and t[1]["nr"] in c["angriff"]["einheiten"])
    assert an["angriff"]["einheiten"][0] == t[0]["nr"] and len(an["angriff"]["einheiten"]) == 6


def test_sechster_nachlauf_turm_mitte_und_trupp_auf_der_ecke(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder17"](lauf_von(g))
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    gb = {x["posten"]: x for x in plan["gebaeude"]}
    laeufe = [tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {})]
    t = gb["turm_voll"]
    assert laeufe.count((t["x"] + 1, t["y"] + 1)) == 8  # 8 Mann in die Mitte
    g4 = gb["turm4_gang"]
    assert (g4["x"] + 2, g4["y"] + 2) in laeufe  # nicht auf eine Ecke
    sp = [c["spielbefehl"]["werte"] for c in b if c.get("spielbefehl", {}).get("nr") == 25]
    for t_, zeile in ((t, t["y"] + 1), (g4, g4["y"] + 2)):
        assert next(w for w in sp if w[4] == 25 and w[2] == t_["x"] - 1)[1] == zeile  # Mauer trifft eine Zeile ohne Ecke
    tr = [x for x in plan["einheiten"] if x.get("posten") == "trupp_eck" and x["rolle"] == "trupp"]
    ecke = gb["trupp_eck"]
    assert (tr[0]["x"], tr[0]["y"]) == (ecke["x"], ecke["y"])  # erste Einheit auf der Ecke
    k = next(x for x in plan["einheiten"] if x.get("posten") == "trupp_eck" and x["rolle"] == "feind")
    assert max(abs(tr[1]["x"] - k["x"]), abs(tr[1]["y"] - k["y"])) <= 1
    an = next(c for c in b if c.get("angriff", {}).get("lauf") and tr[1]["nr"] in c["angriff"]["einheiten"])
    assert an["angriff"]["einheiten"][0] == tr[0]["nr"]


def test_gesetzte_schalter_assassinen_und_feuerkorb(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    g.speicher[7000 + 100 * 3] = 0x00070001  # Nachbarfeld oben 7, darf nicht verloren gehen
    e = ls.SZENEN["sonder15_g"](l)
    assert e["kein_platz"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    wer = [x for x in plan["einheiten"] if x.get("posten") == "assassinen"]
    assert len(wer) == 2 and all(x["typ"] == 73 for x in wer)
    pokes = [c for c in b if "poke" in c]
    gesetzt = {c["poke"]: c["wert"] for c in pokes}
    assert all(gesetzt[7000 + 100 * x["nr"]] & 0xFFFF == 12 for x in wer)  # updateUnits: case 0xc
    t = next(c for c in b if isinstance(c.get("toeteAlle"), dict) and c["toeteAlle"].get("typen") == [73])
    assert t["toeteAlle"]["spieler"] == 1 and t["toeteAlle"]["ohneLord"]
    korb = [c for c in b if c.get("spielbefehl", {}).get("nr") == 69]
    assert len(korb) == 2 and all(c["spielbefehl"]["werte"][4] == ls.ET_BRAZIER and c["spielbefehl"]["werte"][0] == 1 for c in korb)
    ik = [b.index(c) for c in korb]
    modi = [i for i, c in enumerate(b) if c.get("poke") == 7000 and c.get("wert") in (ls.GM_SIEGE_THAT, ls.GM_GEFECHT_2)]
    assert len(modi) == 2 and b[modi[0]]["wert"] == ls.GM_SIEGE_THAT and b[modi[1]]["wert"] == ls.GM_GEFECHT_2  # gesetzt und zurueck
    assert ik[0] < modi[0] < ik[1] < modi[1]  # erst ohne, dann mit, dann zurueck
    assert all(b[i - 1].get("ware", {}).get("typ") == 15 for i in ik)  # Gold kurz davor


def test_knapper_stein_vor_dem_auffuellen(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder18_g"](l)
    assert e["kein_platz"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    k = next(x for x in plan["einheiten"] if x["typ"] == 39)
    bef = next(c for c in b if c.get("spielbefehl", {}).get("nr") == 86)
    assert bef["spielbefehl"]["werte"] == [1000 + k["nr"], 1]
    w = b[b.index(bef) - 1]
    assert w["ware"] == {"typ": 4, "menge": 2}


def test_mauerluecke_und_befehle(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder19"](lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    o = plan["karte"][0]
    laeufe = [tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {})]
    assert laeufe.count((o["x"] + 14, o["y"] + 4)) == 2  # vor und nach dem Durchbruch
    assert any(c.get("angriff", {}).get("art") == 23 for c in b)
    g = Spiel(tmp_path)
    g.einheiten = [{"nr": 900 + i, "uid": 900 + i, "typ": 55, "besitzer": i + 1, "x": 150 + 100 * i, "y": 150 + 100 * i, "leben": 100, "trupp": 0} for i in range(2)]
    g.gebaeude_liste.append({"nr": 77, "uid": 78, "typ": 10, "x": 250, "y": 240, "besitzer": 2})
    l = lauf_von(g)
    l.gefecht = True
    e = ls.SZENEN["sonder19_g"](l)
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    sp = {c["spielbefehl"]["nr"]: c["spielbefehl"]["werte"] for c in b if "spielbefehl" in c}
    assert sp[34] == [ls.STEUER_STUFE] and sp[102][0] == 0 and sp[68][1:3] == [5, 5] and sp[41][1] == 100 and sp[29][1] == 100
    gb = {x["typ"]: x for x in plan["gebaeude"]}
    assert sp[68][0] == gb[74]["nr"] and sp[68][3] == gb[74]["uid"] and sp[29][0] == gb[1]["nr"] and sp[29][2] == gb[1]["uid"]
    assert sum(1 for c in b if c.get("werbe")) == 2 and sum(1 for c in b if c.get("poke") == 7000 and c.get("wert") == 1) == 1
    assert sum(x.get("posten") == "hunde4" and x["rolle"] == "opfer" for x in plan["einheiten"]) == 4
    an = next(c for c in b if c.get("angriff", {}).get("gebaeude") == 77)
    assert an["player"] == 1 and len(an["angriff"]["einheiten"]) == 3


def test_letzte_reste_hunde_und_lager(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    g.gebaeude_liste.append({"nr": 77, "uid": 78, "typ": 10, "x": 250, "y": 240, "besitzer": 2})
    e = ls.SZENEN["sonder20_g"](l)
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    assert sum(x.get("posten") == "hunde_5" and x["rolle"] == "opfer" for x in plan["einheiten"]) == 5
    assert sum(x.get("posten") == "hunde_6" and x["rolle"] == "opfer" for x in plan["einheiten"]) == 6
    w = [x for x in plan["einheiten"] if x.get("posten") == "lager"]
    assert len(w) == 3 and all(abs(x["x"] - 250) <= 1 and abs(x["y"] - 240) <= 2 for x in w)
    an = next(c for c in b if c.get("angriff", {}).get("gebaeude") == 77)
    assert an["player"] == 1


def test_gegenprobe_befehl_sofort(tmp_path):
    for n, f, _, _ in ls.sonder21(lauf_von(Spiel(tmp_path))):
        g, wer, d, jetzt, stufen = f(100, 100)
        assert stufen is None and len(d) == 2
        for w in wer:
            w["nr"], w["uid"] = 1, 1
        assert jetzt()[0]["angriff"]["lauf"] == {"sofort_mitte": [114, 103], "sofort_mauer": [109, 102]}[n]  # Mitte des Turms, ein Feld der Mauer


def test_holztor_als_ziel(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder22"](lauf_von(g))
    assert e["kein_platz"] == []
    b = [c for c in g.log if isinstance(c, dict)]
    s = next(c for c in b if "setzeGebaeude" in c)
    assert s["setzeGebaeude"]["mapper"] == 103 and s["setzeGebaeude"]["spieler"] == 2


def test_sonder24_baut_zelt_mit_trupp_und_wirft_oel(tmp_path):
    g = Spiel(tmp_path)
    p = dict((n, f) for n, f, _, _ in ls.sonder24_g(lauf_von(g)))
    assert set(p) == {"zelt4", "zelt2", "oel_wurf", "oel_lager", "mauer_real", "punkt_halten", "holztor"}
    _, wer, _, _, stufen = p["zelt4"](100, 100)
    assert len(wer) == 4 and {e["typ"] for e in wer} == {30}
    assert stufen[0][0] == ls.TUNNEL_TRUPP
    assert len(p["zelt2"](100, 100)[1]) == 2
    assert ls.MAPPER_ZELT_TURM == 192  # 94 baut Art 69, kein Zelt
    _, _, _, _, stufen = p["punkt_halten"](100, 100)
    assert [t for t, _ in stufen] == list(range(50, 1001, 50))
    _, _, _, _, stufen = p["mauer_real"](100, 100)
    c = [f() for _, f in stufen]
    assert [x[1]["spielbefehl"]["werte"][4] for x in c] == [25, 46, 46, 25]
    assert [x[1]["spielbefehl"]["werte"][2] - x[1]["spielbefehl"]["werte"][0] + 1 for x in c] == [13, 13, 8, 8]


def test_einheiten_auf_einen_punkt(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["sonder23"](lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict) and "lauf" in c.get("angriff", {})]
    ort = {k["posten"]: k for k in plan["karte"]}
    assert len(b) == 9  # 8 einzeln, 1 Trupp
    einzeln = [c for c in b if len(c["angriff"]["einheiten"]) == 1]
    trupp = [c for c in b if len(c["angriff"]["einheiten"]) == 8]
    o = ort["punkt_einzeln"]
    assert len(einzeln) == 8 and {tuple(c["angriff"]["lauf"]) for c in einzeln} == {(o["x"] + 4, o["y"] + 8)}
    o = ort["punkt_trupp"]
    assert len(trupp) == 1 and tuple(trupp[0]["angriff"]["lauf"]) == (o["x"] + 4, o["y"] + 8)


def test_poke_zwei_byte_laesst_den_nachbarn():
    class L:
        class k:
            @staticmethod
            def peek(adr):
                return [0xABCD0001]
    assert ls.poke2(L, 500, 12) == {"poke": 500, "wert": 0xABCD000C}


def test_rush_schutz_setzen_und_zurueck(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder16_g"](l)
    assert e["kein_platz"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    b = [c for c in g.log if isinstance(c, dict)]
    a, o = [next(x for x in plan["einheiten"] if x.get("rolle") == r and x.get("posten") == "rush") for r in ("taeter", "opfer")]
    assert (a["spieler"], o["spieler"]) == (1, 2) and a["typ"] == o["typ"]
    lauf = next(c for c in b if "lauf" in c.get("angriff", {}))
    assert tuple(lauf["angriff"]["lauf"]) == (o["x"] - 1, o["y"])  # neben den Gegner
    i = b.index(lauf)
    werte = [c["wert"] for c in b[i:] if "poke" in c]
    assert werte == [ls.RUSH_TAKTE, ls.GM_MEHRSPIELER, ls.GM_EINZEL]  # Schutz, Spielart, und zurueck
    assert ls.RUSH_SETZEN < ls.RUSH_LAUF + 12 * 12  # der Schutz gilt, bevor er ankommt


def test_abgelehnte_mauer_wird_wiederholt_und_bleibt_sichtbar(tmp_path):
    g = Spiel(tmp_path, linien_abgelehnt=3)
    plan = json.load(open(ls.SZENEN["sonder13"](lauf_von(g))["pfad"] + ".plan.json", encoding="utf-8"))
    assert plan["mauer_fehlt"] == [] and plan["mauer_wiederholt"] >= 1
    g = Spiel(tmp_path, linien_abgelehnt=10000)
    plan = json.load(open(ls.SZENEN["sonder13"](lauf_von(g))["pfad"] + ".plan.json", encoding="utf-8"))
    assert len(plan["mauer_fehlt"]) == 10  # 3 mal Mauer und Treppe, 4 Seiten des Rings: Am Ende steht offen da, was fehlt
    assert sum(c.get("spielbefehl", {}).get("nr") == 25 for c in g.log if isinstance(c, dict)) == 10 * ls.MAUER_VERSUCHE


def test_abgelehntes_gebaeude_wird_wiederholt(tmp_path):
    g = Spiel(tmp_path, gebaeude_abgelehnt=1)
    e = ls.SZENEN["sonder13"](lauf_von(g))
    assert e["nicht_gesetzt"] == []


def test_linie_felder_endet_bei_der_erlaubten_laenge():
    assert ls.linie_felder([5, 7, 1, 7, 27, 13]) == [(5, 7), (4, 7), (3, 7), (2, 7), (1, 7)]
    assert ls.linie_felder([3, 0, 3, 20, 25, 13]) == [(3, i) for i in range(13)]


def test_zweiter_nachlauf_geher_auf_das_pech(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder11_g"](l)
    assert e["kein_platz"] == []
    b = [c for c in g.log if isinstance(c, dict)]
    pech = {(c["baue"]["x"], c["baue"]["y"]) for c in b if "baue" in c}
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    geher = {x["nr"] for x in plan["einheiten"] if x["rolle"] == "geher"}
    ziele = [tuple(c["angriff"]["lauf"]) for c in b if "lauf" in c.get("angriff", {}) and c["angriff"]["einheiten"][0] in geher]
    assert len(ziele) == 5 and all(z in pech for z in ziele)


def test_tunnel_ohne_eingang_bricht_gleich_ab(tmp_path):
    g = Spiel(tmp_path, kein_eingang=True)
    g.einheiten = [{"nr": 900 + i, "uid": 900 + i, "typ": 55, "besitzer": i + 1, "x": 150 + 100 * i, "y": 150 + 100 * i, "leben": 100, "trupp": 0} for i in range(2)]
    l = lauf_von(g)
    l.gefecht = True
    with pytest.raises(ls.Abbruch, match="Kein Eingang"):
        ls.SZENEN["sonder6_g"](l)


def test_tunnel_erst_mauer_und_turm_dann_eingang_mit_trupp(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    g.einheiten.append({"nr": 901, "uid": 901, "typ": 55, "besitzer": 2, "x": 250, "y": 250, "leben": 100, "trupp": 0})
    e = ls.SZENEN["sonder6_g"](l)
    assert e["kein_platz"] == [] and e["nicht_gesetzt"] == []
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    for k in plan["karte"]:
        assert 14 <= max(abs(k["x"] - 250), abs(k["y"] - 250)) <= 40  # im Burgbereich von Spieler 2
    ko = next(x for x in plan["einheiten"] if x["rolle"] == "kontrolle")
    assert max(abs(ko["x"] - 250), abs(ko["y"] - 250)) > 40  # die Posten belegen den Ring, die Kontrolle steht ausserhalb
    b = [c for c in g.log if isinstance(c, dict)]
    baue = [c for c in b if "baue" in c]
    assert len(baue) == 4 and all(c["player"] == 1 and c["baue"]["mapper"] == 66 and c["baue"]["groesse"] == 3 and c["baue"]["trupp"] for c in baue)  # ohne Trupp geht niemand hin
    mauer = next(c for c in b if c.get("spielbefehl", {}).get("nr") == 25)
    assert mauer["player"] == 2 and b.index(mauer) < b.index(baue[0])  # ohne Ziel erlaubt das Spiel den Eingang nicht
    assert all(z["spieler"] == 2 and z["typ"] == 74 for z in plan["gebaeude"])
    los = [c for c in b if "lauf" in c.get("angriff", {})]
    assert b.index(los[0]) < b.index(baue[0])  # der Trupp entsteht erst mit dem ersten Befehl
    wer = {x["rolle"]: x for x in plan["einheiten"] if x.get("posten") == "mauer"}
    assert set(wer) == {"taeter", "reserve"} and wer["taeter"]["typ"] == 5
    st = next(c for c in b if "gebaeude" in c.get("angriff", {}))
    assert st["player"] == 2 and st["angriff"]["gebaeude"] >= 2000  # der Gegner schlaegt den Eingang, nicht den Turm


def test_pech_mit_feuerwerfer(tmp_path):
    g, l = lauf_im_gefecht(tmp_path)
    e = ls.SZENEN["sonder5_g"](l)
    assert e["kein_platz"] == []
    b = [c for c in g.log if isinstance(c, dict)]
    assert sum(1 for c in b if "baue" in c) == 5 and any("ziel" in c.get("angriff", {}) and c["player"] == 1 for c in b)


def test_spielbefehle_verschiedener_spieler_laufen_in_verschiedenen_takten(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    l.gefecht = True
    ls.SZENEN["sonder2_g"](l)
    b = [c for c in g.log if isinstance(c, dict)]
    p1 = max(i for i, c in enumerate(b) if c.get("player") == 1 and ("ware" in c or c.get("spielbefehl", {}).get("nr") == 21))
    p2 = min(i for i, c in enumerate(b) if c.get("player") == 2 and ("ware" in c or "baue" in c))
    assert p1 < p2 and any(c.get("pause") is False for c in b[p1:p2])


def test_erlaubte_stelle_fragt_das_spiel_und_nimmt_die_naechste(tmp_path):
    g = Spiel(tmp_path)
    karte = ["-" * 13 for _ in range(13)]
    karte[9] = "-" * 12 + "+"
    karte[6] = "-" * 8 + "+" + "-" * 4
    g.platzkarte = lambda *a, **k: karte
    z = {"mapper": 1, "groesse": 3, "x": 100, "y": 200, "spieler": 2}
    assert ls.erlaubte_stelle(lauf_von(g), z) == (102, 200)
    g.platzkarte = lambda *a, **k: ["-" * 13] * 13
    assert ls.erlaubte_stelle(lauf_von(g), z) is None


def test_oel_einzeln_werfen_und_hingehen(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    l.gefecht = True
    ls.SZENEN["sonder2_g"](l)
    w = [c["angriff"] for c in g.log if isinstance(c, dict) and c.get("angriff", {}).get("art") == 20]
    assert len(w) == 4 and all(len(c["einheiten"]) == 1 for c in w)


def test_stufen_laufen_in_der_reihenfolge_ihrer_takte(tmp_path):
    g = Spiel(tmp_path)
    g.pausiert = 1
    zeit = []
    def posten(x, y):
        return [], [ls._e("a", 24, x, y)], [], lambda: [], [(500, lambda: zeit.append(("spaet", g.t)) or []), (100, lambda: zeit.append(("frueh", g.t)) or [])]
    ls.szene_sonder(lauf_von(g), "sonder1", (("p", posten, 10, 4),))
    assert [z[0] for z in zeit] == ["frueh", "spaet"] and zeit[1][1] - zeit[0][1] >= 400


def test_packen_legt_dicht_und_sperrt_den_rand():
    frei = np.zeros((400, 400), dtype=bool)
    frei[10:30, 10:50] = True
    o = ls.packen(frei, [(10, 5), (10, 5), (40, 20)], rand=2)
    assert o[0] == (10, 10) and o[1] == (22, 10) and o[2] is None
    assert frei[10:30, 10:50].all()  # die Eingabe bleibt unberuehrt


def test_geraete_weite_leiter(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["geraete_weite"](lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    gr = [x for x in plan["einheiten"] if x["rolle"] == "geraet"]
    ziele = {x["paar"]: x for x in plan["einheiten"] if x["rolle"] == "ziel"}
    assert len(gr) == 25 and all(ziele[x["paar"]]["x"] - x["x"] == x["abstand"] for x in gr)
    assert {x["abstand"] for x in gr if x["typ"] == 40} == {34, 47, 57, 68, 70}
    bef = [c["angriff"] for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert sum(1 for c in bef if c.get("art") == 16) == 25 and sum(1 for c in bef if "ziel" in c) == 25


def test_punkt_alle_acht_bloecke_und_die_mauer_mit_luecke(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_punkt(lauf_von(g))
    assert e["bloecke"] == [10, 100, 500, 100, 500, 100, 100, 500]
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    mauern = [c for c in plan["mauern"]]
    assert len(mauern) == 4 and all(c["player"] == 2 and c["spielbefehl"]["nr"] == 25 and c in g.log for c in mauern)
    l1 = next(p for p in plan["posten"] if p["art"] == "luecke")
    wx, y0, y1, m = l1["mauer"]
    w = [c["spielbefehl"]["werte"] for c in mauern[:2]]
    assert w[0][:4] == [wx, y0, wx, m - 2] and w[1][:4] == [wx, m + 2, wx, y1]
    bef = [c["angriff"] for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert sum("gebaeude" in c for c in bef) == 3 and sum("lauf" in c for c in bef) == 5
    assert sum(len(c["einheiten"]) for c in bef) == 1910


def test_sonderfaelle_jeder_posten_steht_und_hat_befehle(tmp_path):
    g = Spiel(tmp_path)
    l = lauf_von(g)
    a = ls.SZENEN["sonder1"](l)
    assert a["kein_platz"] == [] and a["nicht_gesetzt"] == []
    b = ls.SZENEN["sonder2"](l)
    assert b["kein_platz"] == [] and b["nicht_gesetzt"] == []
    bef = [c for c in g.log if isinstance(c, dict)]
    arten = {c["angriff"].get("art") for c in bef if "angriff" in c}
    assert {6, 16, 20, 22, 24} <= arten
    nummern = {c["spielbefehl"]["nr"] for c in bef if "spielbefehl" in c}
    assert {21, 25, 45, 74} <= nummern
    pa = json.load(open(a["pfad"] + ".plan.json", encoding="utf-8"))
    pb = json.load(open(b["pfad"] + ".plan.json", encoding="utf-8"))
    assert {k["posten"] for k in pa["karte"]} == {"feuer", "pech", "mordloch", "hunde", "kuh", "graben"}
    assert {k["posten"] for k in pb["karte"]} == {"leiter", "turmgeraet", "tunnel", "schild", "hoehe", "tor", "oel"}


def test_sonderfall_ohne_platz_haelt_die_anderen_nicht_auf(tmp_path):
    g = Spiel(tmp_path)
    r = ls.szene_sonder(lauf_von(g), "sonder1", (("riesig", ls.p_feuer, 399, 399), ("feuer", ls.p_feuer, 24, 12)))
    assert r["kein_platz"] == ["riesig"] and r["einheiten"] == 3


def punkt_rahmen(orte):
    aus = []
    for i, o in enumerate(orte):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        for j, (x, y) in enumerate(o):
            s["da"][j + 1], s["typ"][j + 1], s["mx"][j + 1], s["my"][j + 1] = 1, 24, x * 8, y * 8
        aus.append((100 + i * 10, s))
    return aus


def test_punkt_ankunft_dichte_und_luecke():
    p = {"art": "luecke", "anzahl": 2, "nummern": [1, 2], "ziel": [20, 10], "mauer": [15, 0, 20, 10]}
    r = punkt_rahmen([[(0, 10), (0, 3)], [(15, 10), (15, 3)], [(20, 10), (15, 3)], [(20, 10), (20, 10)]])
    z = ar.punkt_werten(r, [p])[0]
    assert z["angekommen"] == 2 and z["takte_10_50_90"][1] == 25 and z["letzter"] == 30 and z["dichtestes_feld"] == 2 and z["durch_luecke"] == 1 and z["anderswo_an_mauerlinie"] == 1


def test_schussweite_katapult_zielt_aufs_feld():
    e = [{"rolle": "geraet", "paar": 0, "typ": 39, "nr": 1, "abstand": 30}, {"rolle": "ziel", "paar": 0, "typ": 59, "nr": 2, "x": 40, "y": 10}]
    g = [{"schuetze": 1, "ziel": 0, "start": (80, 84), "punkt": (324, 84)}, {"schuetze": 1, "ziel": 0, "start": (80, 84), "punkt": (500, 84)}]
    z = ar.schussweite_werten(g, e)[0]
    assert z["auf_ziel"] == 1 and z["andere"] == 1


def test_besatzung_voll_und_ein_mann_zu_wenig(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["besatzung"](lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    geraete = [x for x in plan["einheiten"] if x["rolle"] == "geraet"]
    assert len(geraete) == 20 and {(x["art"], x["typ"], x["mann"]) for x in geraete} == {(a, t, n) for a, ts in (("schiessen", ls.SCHIESSEN), ("fahren", ls.FAHREN)) for t in ts for n in (ls.BESATZUNG[t], ls.BESATZUNG[t] - 1)}
    for x in geraete:
        assert sum(1 for i in plan["einheiten"] if i["rolle"] == "ingenieur" and i["fall"] == x["fall"]) == x["mann"]
    assert plan["bemannt"] is True
    bef = [c["angriff"] for c in g.log if isinstance(c, dict) and "angriff" in c]
    einstieg = [c for c in bef if c.get("art") == 16]
    assert len(einstieg) == 19  # der Schild mit einem Mann zu wenig hat keinen
    assert all(c["b"] == next(x["uid"] for x in geraete if x["nr"] == c["a"]) for c in einstieg)
    danach = bef[19:]
    assert len(danach) == 20 and sum("ziel" in c for c in danach) == 10 and sum("lauf" in c for c in danach) == 10


def test_besatzung_steigt_nicht_ein_ist_ein_fund_kein_abbruch(tmp_path):
    e = ls.SZENEN["besatzung"](lauf_von(Spiel(tmp_path, steigt_nicht_ein=True)))
    assert e["bemannt"] is False and e["bemannt_nach"] >= ls.GRENZE_BEMANNEN


def test_gebaeude_setzen_liest_nach_was_wirklich_steht(tmp_path):
    g = Spiel(tmp_path, kein_gebaeude=2)
    g.pausiert = 1
    z = [{"spieler": 2, "typ": 1001, "x": 100, "y": 100, "mapper": 1001, "groesse": 4}, {"spieler": 2, "typ": 2, "x": 200, "y": 100, "mapper": 2, "groesse": 4}, {"spieler": 2, "typ": 1003, "x": 100, "y": 200, "mapper": 1003, "groesse": 4}]
    fehlt = ls.gebaeude_setzen(lauf_von(g), z)
    assert [x["mapper"] for x in fehlt] == [2] and z[0]["nr"] == 1000 and z[2]["nr"] == 1001 and "nr" not in z[1]


def test_gebaeude_setzen_nimmt_nicht_das_gebaeude_des_nachbarn(tmp_path):
    g = Spiel(tmp_path, kein_gebaeude=2)
    g.pausiert = 1
    z = [{"spieler": 2, "typ": 2, "x": 100, "y": 100, "mapper": 2, "groesse": 4}, {"spieler": 2, "typ": 1003, "x": 103, "y": 100, "mapper": 1003, "groesse": 4}]
    fehlt = ls.gebaeude_setzen(lauf_von(g), z)
    assert [x["typ"] for x in fehlt] == [2] and z[1]["nr"] == 1000


def test_belagerung_klassen_zuerst_und_jedes_ziel_ein_geraet(tmp_path):
    g = Spiel(tmp_path)
    e = ls.SZENEN["belagerung"](lauf_von(g))
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    geraete = {x["fall"]: x for x in plan["einheiten"] if x["rolle"] == "geraet"}
    z = plan["gebaeude"]
    assert all(geraete[x["fall"]]["x"] + ls.ABSTAND_BELAGERUNG == x["x"] for x in z)
    assert [(geraete[x["fall"]]["typ"], x["typ"]) for x in z[:24]] == [(t, k) for t in ls.ANDERE_GERAETE + (39,) for k in ls.KLASSEN]
    assert all(geraete[x["fall"]]["typ"] == 39 for x in z[24:]) and len(z) + len(plan["nicht_gefahren"]) == 24 + 59
    breit = [x["groesse"] for x in z[24:]]
    assert breit == sorted(breit, reverse=True)  # die grossen zuerst


def test_gebaeude_nah_alle_paare(tmp_path):
    g = Spiel(tmp_path)
    e = ls.szene_fahren(lauf_von(g), ls.SZENEN["gebaeude_nah"])
    plan = json.load(open(e["pfad"] + ".plan.json", encoding="utf-8"))
    wer = {x["fall"]: x for x in plan["einheiten"] if x["rolle"] == "angreifer"}
    assert len(wer) == 50 and {(wer[z["fall"]]["typ"], z["typ"]) for z in plan["gebaeude"]} == {(a, b) for a in ls.NAH_GEGEN_GEBAEUDE for b in ls.NAH_ZIELE}
    bef = [c["angriff"] for c in g.log if isinstance(c, dict) and "angriff" in c]
    assert len(bef) == 50 and all(c["gebaeude"] >= 1000 and len(c["einheiten"]) == 1 for c in bef)


def gebaeude_reihe(leben, hoechst=None, da=None):
    aus = []
    for i, w in enumerate(leben):
        s = {k: np.zeros(2000, dtype=np.int64) for k in ("leben", "hoechst", "da")}
        s["leben"][5], s["hoechst"][5], s["da"][5] = w, hoechst or leben[0], 1 if da is None else da[i]
        aus.append((100 + i, s))
    return aus


def test_belagerung_vielfache_des_steins_sind_die_regel():
    e = [{"rolle": "geraet", "fall": 0, "typ": 39, "nr": 1}]
    z = [{"fall": 0, "nr": 5, "name": "BT_HOVEL", "laufzeit": 1, "typ": 1}]
    g = [{"schuetze": 1}, {"schuetze": 1}, {"schuetze": 2}]
    r = ar.belagerung_werten(gebaeude_reihe([500, 500, 370, 270]), g, e, z)[0]
    assert r["urteil"] == "bestaetigt" and r["steine"] == 2 and r["verluste"] == {130: 1, 100: 1} and r["erster_verlust"] == 102
    assert ar.belagerung_werten(gebaeude_reihe([200, 199]), g, e, z)[0]["urteil"] == "weicht ab"
    assert ar.belagerung_werten(gebaeude_reihe([200, 200]), g, e, z)[0]["urteil"] == "gemessen"
    e2 = [dict(e[0], typ=59)]
    assert ar.belagerung_werten(gebaeude_reihe([200, 185]), g, e2, z)[0]["urteil"] == "gemessen"
    assert ar.belagerung_werten(gebaeude_reihe([200, 70]), g, e, [dict(z[0], laufzeit=74)])[0]["urteil"] == "falsches Gebaeude"


def test_stein_voller_treffer_und_rand():
    assert ar._stein_passt(130, 40, 15) and ar._stein_passt(100, 40, 15) and ar._stein_passt(75, 40, 15) and ar._stein_passt(300, 120, 30) and ar._stein_passt(10, 5, 0)
    assert not ar._stein_passt(20, 40, 15) and not ar._stein_passt(7, 5, 0)


def test_gebaeude_verlauf_merkt_das_ende():
    v = ar._gebaeude_verlauf(gebaeude_reihe([100, 50, 0, 0], da=[1, 1, 0, 0]), 5)
    assert v["weg"] == 102 and v["erster_verlust"] == 101 and v["verluste"] == [50, 50] and v["leben"] == 100


def geraet_reihe(orte, mann=2):
    aus = []
    for i, x in enumerate(orte):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s["da"][1], s["typ"][1], s["mann"][1] = 1, 59, mann
        s["mx"][1], s["my"][1] = x, 40
        aus.append((100 + i * 10, s))
    return aus


def test_besatzung_prueft_beide_richtungen():
    fahren = {"rolle": "geraet", "fall": 0, "art": "fahren", "soll": 4, "mann": 4, "typ": 59, "nr": 1}
    r = ar.besatzung_werten(geraet_reihe([0, 0, 32, 64]), [], [fahren])[0]
    assert r["urteil"] == "bestaetigt" and r["felder"] == 8.0 and r["takte_je_feld"] == 1.25 and r["besetzt"] == 2
    assert ar.besatzung_werten(geraet_reihe([0, 0, 0]), [], [fahren])[0]["urteil"] == "weicht ab"
    assert ar.besatzung_werten(geraet_reihe([0, 0, 32]), [], [dict(fahren, mann=3)])[0]["urteil"] == "weicht ab"
    assert ar.besatzung_werten(geraet_reihe([0, 0, 0]), [], [dict(fahren, mann=3)])[0]["urteil"] == "bestaetigt"
    sch = dict(fahren, art="schiessen", soll=2, mann=2)
    g = [{"schuetze": 1, "von": 100}, {"schuetze": 1, "von": 223}, {"schuetze": 1, "von": 346}]
    r = ar.besatzung_werten(geraet_reihe([0, 0]), g, [sch])[0]
    assert r["urteil"] == "bestaetigt" and r["schuesse"] == 3 and r["schusstakt"] == 123
    assert ar.besatzung_werten(geraet_reihe([0, 0]), g, [dict(sch, mann=1)])[0]["urteil"] == "weicht ab"


def test_kein_einziger_treffer_bricht_ab(tmp_path):
    with pytest.raises(lf.Abbruch, match="Kein einziger Treffer"):
        ls.szene_fahren(lauf_von(Spiel(tmp_path, kein_treffer=True)), ls.SZENEN["nahkampf"])


def test_fehlende_einheit_bricht_ab(tmp_path):
    with pytest.raises(lf.Abbruch, match="stehen nicht"):
        ls.szene_fahren(lauf_von(Spiel(tmp_path, fehlt_einer=True)), ls.SZENEN["nahkampf"])


def test_abraeumen_hat_eine_grenze(tmp_path):
    with pytest.raises(lf.Abbruch, match="Abraeumen"):
        ls.szene_fahren(lauf_von(Spiel(tmp_path, steintod_bleibt=True)), ls.SZENEN["nahkampf"])


def test_stillstand_bricht_ab(tmp_path):
    g = Spiel(tmp_path, stillstand=True)
    with pytest.raises(lf.Abbruch, match="kein neuer Takt"):
        ls.szene_fahren(lauf_von(g), ls.SZENEN["nahkampf"])


def test_gitter_nimmt_nur_freie_und_ebene_stellen():
    frei = np.zeros((40, 40), dtype=bool)
    frei[10:20, 10:20] = True
    h = np.zeros((40, 40), dtype=np.int32)
    assert ls.gitter(frei, h, 2, 1, 5, 5, 99) == [(10, 10), (15, 10), (10, 15), (15, 15)]
    h[10:20, 10:20] = np.arange(10)
    assert (10, 10) not in ls.gitter(frei, h, 8, 8, 1, 1, 99, flach=True)
    assert ls.gitter(frei, h, 2, 1, 5, 5, 2) == [(10, 10), (15, 10)]


# --- Regel-Pruefer ---
TAB = {"nah": np.full((80, 80), 25), "pfeil": np.full(80, 1000), "bolzen": np.full(80, 3000), "stein": np.full(80, 900), "schlaegt": np.ones(80, dtype=int), "tempo": np.ones(80, dtype=int), "leben": np.full(80, 1000)}
PAAR = [{"rolle": "a", "paar": 0, "spieler": 1, "typ": 24, "x": 5, "y": 5, "nr": 1, "uid": 1}, {"rolle": "b", "paar": 0, "spieler": 2, "typ": 27, "x": 6, "y": 5, "nr": 2, "uid": 2}]


def reihen_von(leben_a, leben_b, schlaegt=True, typ_b=27):
    aus = []
    for i, (la, lb) in enumerate(zip(leben_a, leben_b)):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        s["da"][[1, 2]] = 1
        s["typ"][1], s["typ"][2] = 24, typ_b
        s["leben"][1], s["leben"][2] = la, lb
        if schlaegt:
            s["schlaegt"][1], s["schlaegt"][2] = 2, 1
        aus.append((100 + i, s))
    return aus


def test_nahkampf_tabellenwert_ist_bestaetigt():
    z = ar.nahkampf_werten(reihen_von([1000] * 5, [1000, 975, 950, 925, 900]), PAAR, TAB)
    r = next(x for x in z if x["schlaeger"] == 24)
    assert r["urteil"] == "bestaetigt" and r["treffer"] == 4 and r["abstaende"] == {1: 3} and r["erster"] == 1


def test_nahkampf_der_letzte_schlag_nimmt_nur_den_rest():
    z = ar.nahkampf_werten(reihen_von([1000] * 4, [60, 35, 10, 0]), PAAR, TAB)
    r = next(x for x in z if x["schlaeger"] == 24)
    assert r["urteil"] == "bestaetigt" and r["treffer"] == 3 and r["werte"] == {"25": 2} or r["werte"] == {25: 2}


def test_nahkampf_mehr_als_der_schaden_ist_auch_beim_letzten_schlag_falsch():
    z = ar.nahkampf_werten(reihen_von([1000] * 3, [60, 35, 0]), PAAR, TAB)
    assert next(x for x in z if x["schlaeger"] == 24)["urteil"] == "weicht ab"


def test_nahkampf_fremdes_geschoss_im_selben_takt_ist_kein_fehler_des_schlaegers():
    z = ar.nahkampf_werten(reihen_von([1000] * 4, [5000, 4975, 3950, 3925]), PAAR, TAB)  # 1025 = 25 + Pfeil 1000
    r = next(x for x in z if x["schlaeger"] == 24)
    assert r["urteil"] == "bestaetigt" and r["fremde_geschosse"] == 1


def test_nahkampf_falscher_wert_weicht_ab():
    z = ar.nahkampf_werten(reihen_von([1000] * 4, [1000, 975, 940, 915]), PAAR, TAB)
    assert next(x for x in z if x["schlaeger"] == 24)["urteil"] == "weicht ab"


def test_nahkampf_treffer_ohne_ziel_ist_kein_schlag():
    z = ar.nahkampf_werten(reihen_von([1000] * 3, [1000, 0 + 500, 100], schlaegt=False), PAAR, TAB)
    assert next(x for x in z if x["schlaeger"] == 24)["urteil"] == "Treffer ohne Nahkampf"


def test_nahkampf_wer_nicht_schlagen_kann_ist_kein_fund_und_wer_es_kann_schon():
    tab = dict(TAB, schlaegt=np.where(np.arange(80) == 24, 0, 1))
    z = ar.nahkampf_werten(reihen_von([1000] * 3, [1000] * 3), PAAR, tab)
    assert next(x for x in z if x["schlaeger"] == 24)["urteil"].startswith("schlaegt nicht")
    assert next(x for x in z if x["schlaeger"] == 27)["urteil"] == "kein Treffer"


def test_nahkampf_gleiche_art_gibt_eine_zeile():
    p = [dict(PAAR[0]), dict(PAAR[1], typ=24)]
    assert len(ar.nahkampf_werten(reihen_von([1000] * 3, [1000] * 3, typ_b=24), p, TAB)) == 1


def test_treffer_enden_mit_dem_tod_und_neuer_belegung():
    r = reihen_von([1000] * 5, [1000, 975, 0, 1000, 975])
    assert [x["betrag"] for x in ar.treffer_lesen(r, PAAR[0], PAAR[1])] == [25, 975]
    r2 = reihen_von([1000] * 5, [1000, 975, 950, 925, 900])
    r2[2][1]["typ"][2] = 30  # Platz neu belegt
    assert len(ar.treffer_lesen(r2, PAAR[0], PAAR[1])) == 1


def test_beschuss_wertet_nach_dem_opfer_und_nennt_was_fehlt():
    r = reihen_von([1000] * 4, [9000, 8000, 5000, 4100])  # Pfeil, Bolzen, Stein
    z = {x["ziel"]: x for x in ar.beschuss_werten(r, PAAR, TAB)}[27]
    assert z["gesehen"] == {"pfeil": 1, "bolzen": 1, "stein": 1} and z["urteil"] == "bestaetigt" and not z["nicht_gesehen"]
    r = reihen_von([1000] * 2, [9000, 8000])
    assert {x["ziel"]: x for x in ar.beschuss_werten(r, PAAR, TAB)}[27]["nicht_gesehen"] == ["bolzen", "stein"]


def test_beschuss_unerklaerter_betrag_weicht_ab():
    r = reihen_von([1000] * 2, [9000, 8123])
    z = {x["ziel"]: x for x in ar.beschuss_werten(r, PAAR, TAB)}[27]
    assert z["urteil"] == "weicht ab" and z["ungeklaert"] == {877: 1}


def test_beschuss_zwei_geschosse_im_selben_takt_und_feuer_sind_erklaert():
    r = reihen_von([1000] * 3, [9000, 7000, 6963])  # zwei Pfeile, dann Feuer 37
    z = {x["ziel"]: x for x in ar.beschuss_werten(r, PAAR, TAB)}[27]
    assert z["urteil"] == "bestaetigt" and z["feuer"] == 1 and z["gesehen"] == {"mehrere": 1}


def test_beschuss_letzter_treffer_nimmt_den_rest():
    r = reihen_von([1000] * 2, [300, 0])
    assert {x["ziel"]: x for x in ar.beschuss_werten(r, PAAR, TAB)}[27]["urteil"] == "bestaetigt"


def test_laufen_zaehlt_takte_je_feld_ab_dem_ersten_schritt():
    r = []
    for i in range(40):
        s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
        x = 5 + max(0, i - 3) // 12  # 3 Takte Stand, dann 1 Feld je 12 Takte
        s["mx"][1], s["my"][1] = x * 8 + 2, 40
        r.append((i, s))
    z = ar.laufen_werten(r, [{"rolle": "gerade", "typ": 22, "x": 5, "y": 5, "ziel": (7, 5), "nr": 1}], 2)
    assert z[0]["takte_je_feld"] == 12.0 and z[0]["erster_schritt"] == 15


def masse_rahmen(t, leben, schlaegt=(3, 3), da=(1, 1, 1)):
    s = {k: np.zeros(ar.PLAETZE, dtype=np.int64) for k in ar.FELDER}
    s["da"][0], s["besitzer"][0] = 1, 1  # der Merkplatz
    s["da"][[1, 2, 3]] = da
    s["besitzer"][[1, 2, 3]] = 1, 1, 2
    s["typ"][[1, 2, 3]] = 24
    s["leben"][[1, 2, 3]] = 1000, 1000, leben
    s["schlaegt"][[1, 2]] = schlaegt
    return t, s


def test_masse_zaehlt_ohne_merkplatz_und_nennt_den_ersten_tod():
    w = int(TAB["nah"][24, 24])
    m = ar.masse_werten([masse_rahmen(100, 1000), masse_rahmen(101, 1000 - 2 * w), masse_rahmen(105, 1000 - 2 * w, da=(1, 0, 1))], TAB)
    assert m["start"] == (2, 1, 3) and m["ende"] == (1, 1, 2) and m["erster_tod_nach"] == 5 and m["takte"] == 5 and m["plaetze_hoechstens"] == 3


def test_masse_summe_der_angreifer():
    w = int(TAB["nah"][24, 24])
    assert ar.masse_werten([masse_rahmen(100, 1000), masse_rahmen(103, 1000 - 3 * 2 * w)], TAB)["summe"] == {"gleich": 1, "weniger": 0, "mehr": 0}
    assert ar.masse_werten([masse_rahmen(100, 1000), masse_rahmen(103, 1000 - 3 * 2 * w - 1)], TAB)["summe"]["mehr"] == 1
    assert ar.masse_werten([masse_rahmen(100, 1000), masse_rahmen(103, 1000 - 2 * w)], TAB)["summe"]["weniger"] == 1
    # wechselt ein Angreifer das Ziel, ist die Summe nicht bekannt: kein Fall
    assert ar.masse_werten([masse_rahmen(100, 1000), masse_rahmen(103, 900, schlaegt=(3, 0))], TAB)["summe"] == {"gleich": 0, "weniger": 0, "mehr": 0}


def test_vergleich_editor_gegen_gefecht():
    a = {"zeilen": [{"schlaeger": 1, "opfer": 2, "soll": 5, "werte": {"5": 3}, "urteil": "bestaetigt"}, {"typ": 22, "lage": "gerade", "takte_je_feld": 16.0}, {"typ": 23, "lage": "gerade", "takte_je_feld": 16.0}, {"schlaeger": 9, "opfer": 9, "soll": 5, "werte": {"5": 1}, "urteil": "bestaetigt"}]}
    b = {"zeilen": [{"schlaeger": 1, "opfer": 2, "soll": 5, "werte": {"5": 9}, "urteil": "bestaetigt"}, {"typ": 22, "lage": "gerade", "takte_je_feld": 16.9}, {"typ": 23, "lage": "gerade", "takte_je_feld": 11.0}, {"schlaeger": 7, "opfer": 7, "soll": 5, "werte": {"5": 1}, "urteil": "bestaetigt"}]}
    v = ar.vergleichen(a, b)
    assert v["gleich"] == 2 and len(v["anders"]) == 1 and v["anders"][0]["zweite"]["typ"] == 23 and v["nur_erste"] == 1 and v["nur_zweite"] == 1


def test_kontrolle_schlaegt_an():
    e = [{"rolle": "kontrolle", "typ": 24, "nr": 1}]
    r = reihen_von([1000, 1000], [1000, 1000])
    assert ar.kontrolle_werten(r, e)[0]["ungestoert"]
    r = reihen_von([1000, 990], [1000, 1000])
    assert not ar.kontrolle_werten(r, e)[0]["ungestoert"]
    r = reihen_von([1000, 1000], [1000, 1000])
    r[1][1]["mx"][1] = 80
    assert not ar.kontrolle_werten(r, e)[0]["ungestoert"]


# --- Wechselprobe: Daniels Vorgabe unter Last ---
def wechsel(abzug, fall=0.10, start=825.0, zittern=0.3):
    """Tempo faellt ueber alle Phasen gleichmaessig um fall, wie in einer schrumpfenden oder wachsenden Schlacht."""
    ohne, mit = [], []
    rand = np.random.default_rng(7)
    for i in range(11):
        w = start * (1 - fall * i / 10) + rand.uniform(-zittern, zittern)
        if i % 2:
            mit.append(w * (1 - abzug))
        else:
            ohne.append(w)
    return {"ohne": ohne, "mit": mit, "sekunden": 1.2}


def test_wechselprobe_findet_ein_prozent_abzug_bei_fallender_last():
    e = aw.a4_wechselprobe({1000: wechsel(0.01)})
    assert e.status == aw.WIDERLEGT
    assert e.daten["stufen"][1000]["abzug"] == pytest.approx(8, abs=2)


def test_alter_vergleich_haette_den_abzug_nicht_gesehen():
    w = wechsel(0.01)
    z = {"tempo": 1000, "soll": 1000, "gezaehlt": 1000, "sekunden": 1.2, "ohne_1": w["ohne"][2], "mit": w["mit"][2], "ohne_2": w["ohne"][3], "gelesen": 1000, "gesamt": 1000}
    assert aw.a4_tempotreppe([z]).status == aw.BESTAETIGT


def test_wechselprobe_ohne_abzug_bestaetigt_und_nennt_ihre_grenze():
    e = aw.a4_wechselprobe({1000: wechsel(0.0)})
    assert e.status == aw.BESTAETIGT
    g = e.daten["stufen"][1000]["grenze"]
    assert 0 < g < 8.25  # sie haette 1 Prozent gesehen, und das steht im Text
    assert "ab " in e.text


def test_wechselprobe_mit_zu_wenig_phasen_ist_nicht_gemessen():
    e = aw.a4_wechselprobe({1000: {"ohne": [825.0], "mit": [], "sekunden": 1.2}})
    assert e.status == aw.NICHT_GESEHEN

def test_streuung_szenen_stehen_bereit():
    import inspect
    for n in ("streuung", "streuung2", "streuung3", "streuung4", "streuung4_g"):
        assert n in ls.SZENEN, n
    p = inspect.signature(ls.szene_sonder).parameters
    assert p["tempo"].default == 100 and p["grenze"].default == ls.GRENZE_SONDER  # die alten Sonderszenen bleiben, wie sie waren
    assert ls.GRENZE_STREUUNG < ls.GRENZE_SONDER and ls.GRENZE_PECH < ls.GRENZE_STREUUNG
