"""B-142: Lauf K ohne Spiel: Ablauf, jeder Abbruchgrund, Ende ohne letzten Lord."""
from __future__ import annotations

import pytest

from selfaware.tools.experiments import auge_lauf_f as lf
from selfaware.tools.experiments import auge_lauf_k as lk


class Spiel:
    """Takte laufen mit der Uhr, solange keine Pause ist. Speichern und Laden wie im Spiel: Laden setzt den Takt zurueck."""

    def __init__(self, **f):
        self.f = f
        self.jetzt, self.t, self.tempo, self.pausiert, self.rest = 0.0, 100, 1000, 0, 0.0
        self.anzahl_lords = f.get("lords", 8)
        self.ansicht_jetzt = lf.IN_PARTIE
        self.frieden_rest = f.get("frieden", 12000)
        self.log, self.protokoll, self.gestartet, self.stand = [], [], [], {"fehlend": 0, "gemischt": 0}
        self.pfad = None
        self.gespeichert = None

    def uhr(self):
        return self.jetzt

    def ruhe(self, d):
        self.jetzt += d
        if self.pausiert or self.f.get("stillstand_bei", 10 ** 9) <= self.t:
            return
        self.rest += d * min(self.tempo, 825)
        while self.rest >= 1:
            self.rest -= 1
            self.t += 1
            if self.frieden_rest > 0 and not self.f.get("frieden_steht"):
                self.frieden_rest -= 1
            if self.f.get("lords_sterben_bei", 10 ** 9) <= self.t:
                self.anzahl_lords = 1
            if self.f.get("ende_bei", 10 ** 9) <= self.t:
                self.ansicht_jetzt = 30

    def befehl(self, c, warte=0.8, bis=None):
        self.log.append(c)
        if "pause" in c:
            self.pausiert = 1 if c["pause"] else 0
        if "tempo" in c:
            self.tempo = c["tempo"]
        self.ruhe(0.01)
        return []

    def takt(self):
        if self.f.get("spiel_weg_bei", 10 ** 9) <= self.t:
            raise OSError("weg")
        return self.t

    def lords(self):
        return self.anzahl_lords

    def ansicht(self):
        return self.ansicht_jetzt

    def frieden(self):
        return self.frieden_rest

    # Rekorder
    def fehler(self):
        return "beendet mit 3" if self.f.get("streng_bei", 10 ** 9) <= self.t else None

    def starten(self, name, tempo, streng=False, messen=True, felder=False):
        self.gestartet.append((name, tempo, streng, messen))
        self.pfad = f"{name}.auge"

    def laeuft(self):
        return True

    def beenden(self):
        self.log.append("aufzeichnung_beendet")
        return dict(self.stand)

    def aussetzen(self, an):
        pass

    def felder(self):
        return None

    # Speichern und Laden
    def speichern(self, name):
        if self.f.get("speichern_scheitert"):
            raise Abbruch_("Speichern")
        self.gespeichert = (name, self.t)
        self.log.append("gespeichert")

    def laden(self, name):
        self.log.append("geladen")
        self.t = self.gespeichert[1]
        self.pausiert = 1
        return self.t


Abbruch_ = lf.Abbruch


def lauf_von(g, **kw):
    a5 = (lambda f1, f2: g.f.get("a5", [])) if not kw.pop("ohne_a5", False) else None
    return lk.LaufK(g, g, {}, g, g.protokoll.append, frist=kw.pop("frist", lk.FRIST), uhr=g.uhr, ruhe=g.ruhe, stop=kw.pop("stop", lambda: False), speichern=g.speichern, laden=g.laden, a5=a5, frist_ende=kw.pop("frist_ende", lk.FRIST_ENDE), **kw)


def test_ganzer_lauf_endet_am_letzten_lord_und_ist_gueltig():
    g = Spiel(lords_sterben_bei=60000)
    aus = lf.programm(lauf_von(g), lk.ABSCHNITTE)
    e = lk.schluss(aus)
    assert e["gueltig"] and e["ende"] == "letzter Lord" and e["lords_start"] == 8 and e["lords_ende"] == 1
    assert [x[:3] for x in g.gestartet if x[0] in ("t1", "t2")] == [("t1", 40, True), ("t2", 40, True)]
    assert all(not x[3] for x in g.gestartet if x[0] in ("t1", "t2")), "im angehaltenen Spiel wird das Tempo nicht gemessen"
    ablauf = [x for x in g.log if x in ("gespeichert", "geladen")]
    assert ablauf == ["gespeichert", "geladen"]
    assert e["t"] == e["t2"], "Das Laden fuehrt auf denselben Takt"


def test_ohne_letzten_lord_endet_der_lauf_normal_wenn_die_zeit_um_ist():
    g = Spiel()
    aus = lf.programm(lauf_von(g, frist_ende=400), lk.ABSCHNITTE)
    e = lk.schluss(aus)
    assert e["gueltig"] and "nicht erreicht" in e["ende"]


def test_endbildschirm_beendet_den_lauf_ohne_stillstand():
    g = Spiel(ende_bei=30000)
    aus = lf.programm(lauf_von(g), lk.ABSCHNITTE)
    assert lk.schluss(aus)["ende"] == "Ansicht 30"


@pytest.mark.parametrize("fehler, text", [
    ({"lords": 5}, "Nur 5 von 8 Lords"),
    ({"frieden_steht": True}, "Friedenszeit endet nicht"),
    ({"stillstand_bei": 3000}, "kein neuer Takt"),
    ({"spiel_weg_bei": 3000}, "Spiel laeuft nicht mehr"),
    ({"streng_bei": 3000}, "Aufzeichnung"),
    ({"speichern_scheitert": True}, "Speichern"),
    ({"a5": ["units[].x", "gfxNumber"]}, "Kernfelder"),
])
def test_jeder_abbruchgrund_beendet_den_lauf_mit_seinem_namen(fehler, text):
    g = Spiel(**fehler)
    with pytest.raises(lf.Abbruch, match=text):
        lf.programm(lauf_von(g), lk.ABSCHNITTE)


def test_a5_ohne_kernfeld_ist_ein_fund_und_kein_abbruch():
    g = Spiel(a5=["units[].gfxNumber"], lords_sterben_bei=60000)
    aus = lf.programm(lauf_von(g), lk.ABSCHNITTE)
    assert lk.schluss(aus)["gueltig"]


def test_fehlender_takt_im_fenster_bricht_ab():
    g = Spiel()
    g.stand = {"fehlend": 1, "gemischt": 0}
    with pytest.raises(lf.Abbruch, match="Fenster t1"):
        lf.programm(lauf_von(g), lk.ABSCHNITTE)


def test_abzug_in_der_bremsprobe_ist_ein_fund(monkeypatch):
    def bremst(l, wann):
        raise lf.Abbruch(f"Das Lesen bremst {wann}: 700 statt 825")
    monkeypatch.setattr(lf, "bremsprobe", bremst)
    g = Spiel(lords_sterben_bei=60000)
    l = lauf_von(g)
    lf.programm(l, lk.ABSCHNITTE)
    assert any("Bremsprobe" in f["was"] for f in l.funde)


def test_friedenszeit_und_ki_stehen_im_startbefehl():
    class K:
        def __init__(self):
            self.ansicht, self.log = lf.IN_PARTIE, []

        def peek(self, adr, n=1):
            return [self.ansicht]

        def befehl(self, c, warte=0.8, bis=None):
            self.log.append(c)
            if c.get("menue") == lf.HAUPTMENUE:
                self.ansicht = lf.HAUPTMENUE
            if c.get("eigenesGefecht"):
                self.ansicht = lf.IN_PARTIE
            return []
    k = K()
    lk.gefecht_starten(k, "Karte", lk.FRIEDEN_NORMAL, ruhe=lambda _: None)
    start = next(c for c in k.log if c.get("eigenesGefecht"))
    assert start["kis"] == list(lk.KIS) and len(set(lk.KIS)) == 8 and start["friedenszeit"] == 1
    assert k.log.index({"pause": False}) < k.log.index(start), "sonst startet das Gefecht eingefroren"


def test_logik_kennt_den_gefechtsblock(tmp_path):
    d = tmp_path / "logik.lua"
    d.write_text(lf.GEFECHT_ANKER + "\n" + lf.ANKER + "\n" + lf.BAU_ALT + "\n" + lf.BAU_LOG_ALT + "\n", encoding="latin-1")
    t = lf.logik_text(str(d))
    assert "cmd.kis" in t and t.index("cmd.kis") < t.index(lf.GEFECHT_ANKER) and lf.logik_text(str(d)).count("cmd.kis") == t.count("cmd.kis")
    d.write_bytes(t.encode("latin-1"))
    assert lf.logik_text(str(d)) == t, "Zweimal eingespielt bleibt es einmal drin"
