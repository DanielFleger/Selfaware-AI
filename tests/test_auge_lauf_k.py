"""B-142: Lauf K ohne Spiel: Ablauf, jeder Abbruchgrund, Ende ohne letzten Lord."""

from __future__ import annotations

import re
import struct

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
        self.log, self.protokoll, self.gestartet, self.stand = (
            [],
            [],
            [],
            {"fehlend": 0, "gemischt": 0},
        )
        self.tempo_beim_weiter = []
        self.gewartet = {}
        self.pfad = None
        self.gespeichert = None

    def uhr(self):
        return self.jetzt

    def ruhe(self, d):
        self.jetzt += d
        if (self.pausiert and not self.f.get("pause_wirkt_nicht")) or self.f.get(
            "stillstand_bei", 10**9
        ) <= self.t:
            return
        self.rest += d * min(self.tempo, 825)
        while self.rest >= 1:
            self.rest -= 1
            self.t += 1
            if self.frieden_rest > 0 and not self.f.get("frieden_steht"):
                self.frieden_rest -= 1
            if self.f.get("lords_sterben_bei", 10**9) <= self.t:
                self.anzahl_lords = 1
            if self.f.get("ende_bei", 10**9) <= self.t:
                self.ansicht_jetzt = 30

    def peek(self, adr, n=1):
        return [self.ansicht_jetzt]

    def befehl(self, c, warte=0.8, bis=None):
        self.log.append(c)
        if c.get("menue") == lf.HAUPTMENUE:
            self.ansicht_jetzt = lf.HAUPTMENUE
        if c.get("eigenesGefecht"):
            self.ansicht_jetzt = lf.IN_PARTIE
            self.t = 0
        if "pause" in c:
            if self.pausiert and not c["pause"]:
                self.tempo_beim_weiter.append(self.tempo)
            self.pausiert = 1 if c["pause"] else 0
        if "tempo" in c:
            self.tempo = c["tempo"]
        self.ruhe(0.01)
        return []

    def takt(self):
        if self.f.get("spiel_weg_bei", 10**9) <= self.t:
            raise OSError("weg")
        return self.t

    def lords(self):
        return self.anzahl_lords

    def lord_besitzer(self):
        return self.f.get("besitzer") or list(range(1, self.anzahl_lords + 1))

    def ansicht(self):
        return self.ansicht_jetzt

    def frieden(self):
        return self.frieden_rest

    # Rekorder
    def fehler(self):
        return "beendet mit 3" if self.f.get("streng_bei", 10**9) <= self.t else None

    def starten(self, name, tempo, streng=False, messen=True, felder=False, warte_ms=0):
        self.gestartet.append((name, tempo, streng, messen))
        self.gewartet[name] = warte_ms
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
        self.ansicht_jetzt = lf.IN_PARTIE
        return self.t + self.f.get("geladen_daneben", 0)


Abbruch_ = lf.Abbruch


def lauf_von(g, **kw):
    return lk.LaufK(
        g,
        g,
        {},
        g,
        g.protokoll.append,
        frist=kw.pop("frist", lk.FRIST),
        uhr=g.uhr,
        ruhe=g.ruhe,
        stop=kw.pop("stop", lambda: False),
        speichern=g.speichern,
        laden=g.laden,
        frist_ende=kw.pop("frist_ende", lk.FRIST_ENDE),
        **kw,
    )


def test_ganzer_lauf_endet_am_letzten_lord_und_ist_gueltig():
    g = Spiel(lords_sterben_bei=60000)
    aus = lf.programm(lauf_von(g), lk.ABSCHNITTE)
    e = lk.schluss(aus)
    assert (
        e["gueltig"]
        and e["ende"] == "letzter Lord"
        and e["lords_start"] == 8
        and e["lords_ende"] == 1
    )
    assert [x[:3] for x in g.gestartet] == [
        ("t1", 40, True),
        ("danach", 1000, False),
        ("t2", 40, True),
        ("t3", 40, True),
    ], "Geladen wird erst nach dem Kampf, zweimal"
    assert all(not x[3] for x in g.gestartet), "im angehaltenen Spiel wird das Tempo nicht gemessen"
    assert g.tempo_beim_weiter == [40, 1000, 1000, 40, 40, 40], (
        "Das Tempo steht, bevor das Spiel weiterlaeuft: Die Probe brach sonst am ersten strengen Takt ab. Dazwischen je ein Weiter fuer die frische Partie vor dem Laden"
    )
    assert [x for x in g.log if x in ("gespeichert", "geladen")] == [
        "gespeichert",
        "geladen",
        "geladen",
    ]
    assert sum(1 for c in g.log if isinstance(c, dict) and c.get("eigenesGefecht")) == 2, (
        "Beide Male derselbe Weg zum Laden: aus einer frisch gestarteten Partie"
    )
    assert {n: g.gewartet[n] for n in ("t1", "t2", "t3")} == {
        "t1": lk.WARTE_MS,
        "t2": lk.WARTE_MS,
        "t3": lk.WARTE_MS,
    }, "In den strengen Fenstern fertige Takte lesen"


def test_ohne_letzten_lord_endet_der_lauf_normal_wenn_die_zeit_um_ist():
    g = Spiel()
    aus = lf.programm(lauf_von(g, frist_ende=400), lk.ABSCHNITTE)
    e = lk.schluss(aus)
    assert e["gueltig"] and "nicht erreicht" in e["ende"]


def test_endbildschirm_beendet_den_lauf_ohne_stillstand():
    g = Spiel(ende_bei=30000)
    aus = lf.programm(lauf_von(g), lk.ABSCHNITTE)
    assert lk.schluss(aus)["ende"] == "Ansicht 30"


@pytest.mark.parametrize(
    "fehler, text",
    [
        ({"lords": 5}, "Nur 5 von 8 Lords"),
        ({"besitzer": [2, 2, 3, 4, 5, 6, 7, 8]}, "Nur 7 von 8 Lords"),
        ({"frieden": 0}, "Friedenszeit greift nicht"),
        ({"frieden_steht": True}, "Friedenszeit endet nicht"),
        ({"geladen_daneben": 5}, "Geladen auf Takt"),
        ({"pause_wirkt_nicht": True}, "Takt steht nach dem Anhalten nicht"),
        ({"stillstand_bei": 3000}, "kein neuer Takt"),
        ({"spiel_weg_bei": 3000}, "Spiel laeuft nicht mehr"),
        ({"streng_bei": 3000}, "Aufzeichnung"),
        ({"speichern_scheitert": True}, "Speichern"),
    ],
)
def test_jeder_abbruchgrund_beendet_den_lauf_mit_seinem_namen(fehler, text):
    g = Spiel(**fehler)
    with pytest.raises(lf.Abbruch, match=text):
        lf.programm(lauf_von(g), lk.ABSCHNITTE)


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
    assert k.log.index({"pause": False}) < k.log.index(start), (
        "sonst startet das Gefecht eingefroren"
    )


def test_startpause_steht_nur_im_befehl_wenn_sie_gewuenscht_ist():
    class K:
        def __init__(self):
            self.log = []

        def peek(self, adr, n=1):
            return [lf.HAUPTMENUE if not self.log else lf.IN_PARTIE]

        def befehl(self, c, warte=0.8, bis=None):
            self.log.append(c)
            return []

    k = K()
    lk.gefecht_starten(k, "Karte", lk.FRIEDEN_NORMAL, ruhe=lambda _: None, startpause=1)
    assert next(c for c in k.log if c.get("eigenesGefecht"))["startpause"] == 1
    assert "teams" not in next(
        c for c in k.log if c.get("eigenesGefecht")
    )  # ohne Angabe jeder gegen jeden
    k = K()
    lk.gefecht_starten(k, "Karte", lk.FRIEDEN_NORMAL, ruhe=lambda _: None, teams=[1, 1, 2, 2])
    assert next(c for c in k.log if c.get("eigenesGefecht"))["teams"] == [1, 1, 2, 2]
    k = K()
    lk.gefecht_starten(k, "Karte", lk.FRIEDEN_NORMAL, ruhe=lambda _: None)
    assert "startpause" not in next(c for c in k.log if c.get("eigenesGefecht"))


def test_lord_zaehler_haengt_nicht_an_max_unit_count():
    """updateUnits setzt maxUnitCount mitten im Takt auf 0. Der erste echte Lauf endete so bei 3 Lebenden mit "letzter Lord"."""
    roh = bytearray(lk.ALLE_PLAETZE * lf.E_SCHRITT)
    for platz, besitzer in ((9, 1), (2000, 2), (2400, 3)):
        struct.pack_into("<h", roh, platz * lf.E_SCHRITT + lf.E_DA, 1)
        struct.pack_into("<h", roh, platz * lf.E_SCHRITT + lf.E_TYP, lk.LORD)
        struct.pack_into("<h", roh, platz * lf.E_SCHRITT + lf.E_BESITZER, besitzer)

    class Quelle:
        def lies(self, adr, n):
            return (
                bytes(roh[:n])
                if adr == lf.EINHEITEN
                else struct.pack("<i", 0) + bytes(max(0, n - 4))
            )

    assert lk.SpeicherK(Quelle()).lord_besitzer() == [1, 2, 3]


def test_jeder_spieler_bekommt_einen_platz():
    """Wie GetPlayerPosition 0x0042AC60: Eingetragen ist Spieler minus 1. Die alte Liste liess Spieler 1 aus, jede Karte zeigte hoechstens 7 Lords."""
    zeile = next(z for z in lf.GEFECHT_NEU if "posArr + i" in z)
    ausdruck = re.search(r"posArr \+ i, (.+?)\) end", zeile).group(1)
    eingetragen = [eval(ausdruck, {"i": i}) for i in range(8)]
    assert sorted(wert + 1 for wert in eingetragen) == lk.SOLL_LORDS


def kopf_bytes(typ=1, spieler=8, plaetze=8, abschnitt4=True):
    z = lambda *w: struct.pack(f"<{len(w)}i", *w)
    stellen = [v for i in range(8) for v in ((10 * i, 20 * i) if i < plaetze else (-1, -1))]
    daten = (
        z(-1)
        + z(3)
        + b"abc"
        + z(12)
        + b"x" * 12
        + z(8)
        + z(0, 0)
        + z(28)
        + z(typ)
        + b"\0" * 0x14
        + z(spieler)
        + z(4)
        + z(3)
    )
    return daten + (z(16 + 0x40) + z(0, 0, 0, 0) + z(*stellen) if abschnitt4 else z(0))


@pytest.mark.parametrize(
    "kw, soll, passt",
    [
        ({}, {"typ": 1, "spieler": 8, "startplaetze": 8}, True),
        ({"spieler": 7, "plaetze": 7}, {"typ": 1, "spieler": 7, "startplaetze": 7}, False),
        ({"plaetze": 1}, {"typ": 1, "spieler": 8, "startplaetze": 1}, False),
        ({"typ": 0}, {"typ": 0, "spieler": 8, "startplaetze": 8}, False),
        ({"abschnitt4": False}, {"typ": 1, "spieler": 8}, False),
    ],
)
def test_kartenkopf_nennt_spieler_und_startplaetze(tmp_path, kw, soll, passt):
    p = tmp_path / "karte.map"
    p.write_bytes(kopf_bytes(**kw))
    assert lk.karten_kopf(str(p)) == soll
    assert lk.passt_fuer_acht(soll) is passt


def test_lauf_startet_nicht_auf_karte_mit_zu_wenig_spielern(tmp_path, monkeypatch):
    (tmp_path / "Sieben.map").write_bytes(kopf_bytes(spieler=7, plaetze=7))
    (tmp_path / "Acht.map").write_bytes(kopf_bytes())
    monkeypatch.setattr(lk, "karten_ordner", lambda n: [str(tmp_path)])
    assert lk.karte_pruefen(2, "Acht")["spieler"] == 8
    assert list(lk.karten_fuer_acht(2)) == ["Acht"]
    with pytest.raises(lf.Fehler, match="passt nicht"):
        lk.karte_pruefen(2, "Sieben")
    with pytest.raises(lf.Fehler, match="keinem Kartenordner"):
        lk.karte_pruefen(2, "Gibt es nicht")


def test_logik_kennt_den_gefechtsblock(tmp_path):
    d = tmp_path / "logik.lua"
    d.write_text(
        lf.GEFECHT_ANKER + "\n" + lf.ANKER + "\n" + lf.BAU_ALT + "\n" + lf.BAU_LOG_ALT + "\n",
        encoding="latin-1",
    )
    t = lf.logik_text(str(d))
    assert (
        "cmd.kis" in t
        and t.index("cmd.kis") < t.index(lf.GEFECHT_ANKER)
        and lf.logik_text(str(d)).count("cmd.kis") == t.count("cmd.kis")
    )
    d.write_bytes(t.encode("latin-1"))
    assert lf.logik_text(str(d)) == t, "Zweimal eingespielt bleibt es einmal drin"
