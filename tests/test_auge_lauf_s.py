"""B-142: Lauf S ohne Spiel: Ablauf einer Szene, jeder Abbruchgrund, Regel-Pruefer, Wechselprobe."""
from __future__ import annotations

import json

import numpy as np
import pytest

from selfaware.tools.analysis import auge_auswertung as aw
from selfaware.tools.analysis import auge_regeln as ar
from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_s as ls


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
                self.einheiten = [e for e in self.einheiten if e["besitzer"] not in self.tod]

    def takt(self):
        return self.t

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
                self.einheiten.append({"nr": self.nr, "uid": 1000 + self.nr, "typ": e["typ"], "besitzer": e["spieler"], "x": e["x"] + 1, "y": e["y"] + 1, "leben": 100})
            if "toeteAlle" in c:
                self.tod.add(c["toeteAlle"])
                self.tod_ab = self.t + 30
        self.ruhe(0.01)

    def einheiten_alle(self):
        return [dict(e) for e in self.einheiten]

    def raster(self):
        frei = np.zeros((400, 400), dtype=bool)
        frei[50:350, 50:350] = True
        return frei, np.zeros((400, 400), dtype=np.int32), np.zeros((400, 400), dtype=np.int32)

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
            for e in self.einheiten[:2]:
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
