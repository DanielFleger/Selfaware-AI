"""B-182 (Daniel 10.11. 23:16): Obergrenze fuer eigene Kaempfer und Fehlerwache, ohne Spiel (der Kern ist ein Ersatz)."""

from types import SimpleNamespace

import pytest

from selfaware.baukasten.obergrenze import UNTERWEGS_TAKTE, Obergrenze, kaempfer
from selfaware.tools.checks.fehlerwache import Wache, anspruechen_aus


def einheit(nr, besitzer, typ, x, y, **f):
    d = {
        "nr": nr,
        "besitzer": besitzer,
        "typ": typ,
        "x": x,
        "y": y,
        "leben": 10000,
        "zielart": 0,
        "zieleinheit": 0,
        "schusseinheit": 0,
        "nahziel": 0,
        "mauerx": 0,
        "mauery": 0,
        "laufx": 0,
        "laufy": 0,
    }
    d.update(f)
    return d


def welt(tick, *es):
    return SimpleNamespace(tick=tick, ich=1, einheiten={e["nr"]: e for e in es})


class Kern:
    def __init__(self, w):
        self.w = w

    def lesen(self):
        return self.w


LORD = einheit(1, 1, 55, 100, 100, leben=150000)


# ---- Obergrenze ---------------------------------------------------------------------------------------------------
def test_zaehlt_nur_eigene_kaempfer_ohne_lord():
    w = welt(
        10,
        LORD,
        einheit(2, 1, 22, 101, 100),
        einheit(3, 1, 3, 102, 100),
        einheit(4, 2, 22, 200, 200),
    )
    assert kaempfer(w, 1) == [
        2
    ]  # Lord, Arbeiter (Typ 3) und der fremde Bogenschuetze zaehlen nicht


def test_grenze_haelt_auch_bei_zwei_werbungen_im_selben_takt():
    k = Kern(welt(10, LORD, einheit(2, 1, 22, 101, 100)))
    og = Obergrenze(2, k)
    assert og.erlaubt(74) is True  # 1 Kaempfer -> der zweite darf
    assert (
        og.erlaubt(74) is False
    )  # der Kern zeigt ihn noch nicht, er zaehlt trotzdem als unterwegs
    k.w = welt(12, LORD, einheit(2, 1, 22, 101, 100), einheit(5, 1, 74, 102, 100))
    assert og.erlaubt(71) is False  # jetzt steht er im Kern: 2 von 2
    k.w = welt(14, LORD, einheit(5, 1, 74, 102, 100))  # einer ist gestorben
    assert og.erlaubt(71) is True
    assert og.erlaubt(1) is True  # ein Bauer ist kein Kaempfer
    assert dict(og.abgelehnt) == {74: 1, 71: 1}


def test_werbung_die_nie_erscheint_verfaellt():
    k = Kern(welt(10, LORD))
    og = Obergrenze(1, k)
    assert og.erlaubt(73) is True
    assert og.erlaubt(73) is False
    k.w = welt(10 + UNTERWEGS_TAKTE, LORD)  # kein Gold, kein Bauer: der Assassine kam nie
    assert og.erlaubt(73) is True


def test_laden_befehl_schickt_ueber_der_grenze_nichts_ans_spiel(monkeypatch):
    try:
        from selfaware.game.ucp import laden
    except RuntimeError:
        pytest.skip("laden braucht eine Spielinstanz")
    gesendet = []
    monkeypatch.setattr(laden, "sende", lambda b, w, bis=None: gesendet.append(b) or ["WERBE ok"])
    monkeypatch.setattr(laden, "OBERGRENZE", Obergrenze(0, Kern(welt(1, LORD))))
    antwort = laden.befehl({"werbe": {"typ": 74, "gebaeude": 9}}, 0.1, bis="WERBE")
    assert gesendet == [] and "OBERGRENZE" in antwort[0]
    laden.befehl({"pause": True}, 0.1)  # andere Befehle laufen durch
    assert len(gesendet) == 1


# ---- Fehlerwache --------------------------------------------------------------------------------------------------
def test_f1_mehr_kaempfer_als_erlaubt():
    w = welt(100, LORD, *[einheit(10 + i, 1, 24, 100, 101) for i in range(3)])
    assert [f["art"] for f in Wache(grenze=2).schritt(w)] == ["F1 Obergrenze"]
    assert Wache(grenze=3).schritt(w) == []


def test_f2_reiter_mit_fernem_ziel_steht_nahes_ziel_nicht():
    fern = einheit(50, 2, 3, 255, 100)  # 155 Felder
    wa = Wache(still=600)
    for t in (100, 400, 699):
        assert (
            wa.schritt(
                welt(
                    t,
                    LORD,
                    fern,
                    einheit(20, 1, 74, 100, 102, zielart=4, zieleinheit=50, schusseinheit=50),
                )
            )
            == []
        )
    f = wa.schritt(
        welt(
            700,
            LORD,
            fern,
            einheit(20, 1, 74, 100, 102, zielart=4, zieleinheit=50, schusseinheit=50),
        )
    )
    assert [x["art"] for x in f] == ["F2 steht"] and f[0]["einheit"] == 20
    nah = einheit(51, 2, 3, 130, 102)  # 30 Felder: er schiesst
    wb = Wache(still=600)
    for t in (100, 700, 1300):
        assert (
            wb.schritt(
                welt(
                    t,
                    LORD,
                    nah,
                    einheit(20, 1, 74, 100, 102, zielart=4, zieleinheit=51, schusseinheit=51),
                )
            )
            == []
        )


def test_f3_soeldner_untaetig_zu_hause_nicht_wenn_er_laeuft():
    wa = Wache(untaetig=2000)
    assert wa.schritt(welt(100, LORD, einheit(30, 1, 71, 105, 100))) == []
    f = wa.schritt(welt(2100, LORD, einheit(30, 1, 71, 105, 100)))
    assert [x["art"] for x in f] == ["F3 untaetig"]
    wb = Wache(untaetig=2000)
    assert wb.schritt(welt(100, LORD, einheit(30, 1, 71, 105, 100, laufx=200, laufy=200))) == []
    assert wb.schritt(welt(2100, LORD, einheit(30, 1, 71, 106, 101, laufx=200, laufy=200))) == []
    # die Starttruppe (Speertraeger, kein Soeldner) steht zu Hause, das ist kein F3
    wc = Wache(untaetig=2000)
    wc.schritt(welt(100, LORD, einheit(31, 1, 24, 105, 100)))
    assert wc.schritt(welt(2100, LORD, einheit(31, 1, 24, 105, 100))) == []


def test_f4_erfolg_nur_mit_beleg():
    text = "  2600 | x | REITERJAGD: Reiter 20 hat Arbeiter 50 erledigt; NAHKAMPF-RAID: 21 (Typ 75) hat Arbeiter 52 erledigt"
    assert anspruechen_aus(text) == [("Reiterjagd", 20, 50), ("Nahkampf-Raid", 21, 52)]
    wa = Wache(beleg=600)
    opfer = einheit(50, 2, 3, 120, 100)
    wa.schritt(
        welt(
            2500,
            LORD,
            opfer,
            einheit(20, 1, 74, 100, 100, schusseinheit=50),
            einheit(21, 1, 75, 100, 101),
        )
    )
    f = wa.schritt(
        welt(2600, LORD, einheit(20, 1, 74, 100, 100), einheit(21, 1, 75, 100, 101)),
        anspruechen_aus(text),
    )
    assert [(x["art"], x["einheit"]) for x in f] == [
        ("F4 ohne Taeter", 21)
    ]  # Reiter 20 hatte 50 als Schussziel, 21 nie


def test_beobachtet_die_ersten_zwanzig():
    w = welt(100, LORD, *[einheit(10 + i, 1, 24, 100, 101) for i in range(25)])
    wa = Wache(grenze=30, beobachten=20)
    wa.schritt(w)
    assert wa.gruppe == list(range(10, 30))


def test_nachspielen_findet_den_fehler_im_lageprotokoll(tmp_path):
    """Nachspiel-Modus (10.11. 23:40): dieselbe Wache ueber gespeicherte Staende; eigene Kernfelder aus der Tabelle eigen."""
    import gzip
    import json

    from selfaware.tools.checks.fehlerwache import nachspielen

    kopf = "nr besitzer typ x y leben zielart zieleinheit laufx laufy nahziel"
    eigen_kopf = "nr typ x y zielart zieleinheit zieluid schusseinheit schussziel_uid mauerx mauery planx plany nahziel"
    zeilen = []
    for t in (100, 800):
        e = [
            "1 1 55 100 100 150000 0 0 100 100 0",
            "50 2 3 255 100 2500 0 0 255 100 0",
            "20 1 74 100 102 15000 4 50 100 102 0",
        ]
        k = ["20 74 100 102 4 50 0 50 0 0 0 0 0 0"]
        zeilen.append(
            {
                "t": t,
                "st": {},
                "einheiten": "tick %d\n%s\n%s\n" % (t, kopf, "\n".join(e)),
                "gebaeude": "nr\n",
                "eigen": "kern_tick %d ich 1\n%s\n%s\n" % (t, eigen_kopf, "\n".join(k)),
            }
        )
    p = tmp_path / "lage.jsonl.gz"
    with gzip.open(p, "wt", encoding="utf-8") as f:
        for z in zeilen:
            f.write(json.dumps(z) + "\n")
    fehler, wache = nachspielen(str(p), still=600)
    assert [x["art"] for x in fehler] == ["F2 steht"] and wache.gruppe == [20]


def test_melden_schreibt_bericht_vor_dem_anhalten_und_wartet_auf_den_kanal(tmp_path):
    """Lauf 1 und 2 (10.11. 23:28, 23:35): Die Wache stuerzte beim Melden ab - erst am belegten Kanal, dann am falschen Ordner."""
    import json

    from selfaware.tools.checks.fehlerwache import melden

    versuche = []

    def befehl(cmd, warte):
        versuche.append(cmd)
        if len(versuche) < 3:
            raise RuntimeError("KANAL BELEGT: ein Lauf (Prozess 1) benutzt den Befehlskanal")
        return ["PAUSE"]

    stop = tmp_path / "STOP"
    fehler = [{"art": "F2 steht", "takt": 4517, "text": "Ziel 307 in 41 Feldern"}]
    pfad, angehalten = melden(
        fehler, Wache(), 4517, None, str(tmp_path), 2, befehl, str(stop), versuche=5, warte=0
    )
    assert angehalten and len(versuche) == 3 and stop.exists()
    assert json.load(open(pfad, encoding="utf-8"))["fehler"][0]["art"] == "F2 steht"


def test_datenordner_der_wache_ist_data_research():
    """Lauf 2: workspace.DATA ist schon data/research - die Wache darf kein zweites research anhaengen."""
    import os

    from selfaware import workspace

    assert os.path.basename(workspace.DATA) == "research" and os.path.isdir(workspace.DATA)


def test_wiedervergebene_nummer_ist_kein_ziel_mehr():
    """Lauf 2 nachgespielt (10.11. 23:40): Arbeiter 322 starb, das Spiel gab die Nummer einem Bauern 78 Felder weiter; das
    Zielfeld der Bogenschuetzen trug noch 322 - die Wache darf das nicht als Ziel ausser Reichweite werten."""
    wa = Wache(still=600)
    nah = einheit(322, 2, 3, 130, 100)  # 30 Felder, wird beschossen
    for t in (100, 200):
        wa.schritt(
            welt(
                t,
                LORD,
                nah,
                einheit(20, 1, 22, 100, 100, zielart=4, zieleinheit=322, schusseinheit=322),
            )
        )
    wa.schritt(
        welt(300, LORD, einheit(20, 1, 22, 100, 100, zielart=4, zieleinheit=322, schusseinheit=322))
    )  # tot
    neu = einheit(322, 2, 1, 178, 100)  # dieselbe Nummer, eine andere Einheit
    for t in (400, 1000, 1400):
        assert (
            wa.schritt(
                welt(
                    t,
                    LORD,
                    neu,
                    einheit(20, 1, 22, 100, 100, zielart=4, zieleinheit=322, schusseinheit=322),
                )
            )
            == []
        )


def test_uhr_beginnt_neu_wenn_das_ziel_wechselt():
    """Lauf 2 nachgespielt (10.11. 23:45): 700 Takte ohne Ziel, dann ein neues Ziel - kein F2, bevor es 600 Takte steht."""
    wa = Wache(still=600)
    for t in (100, 500, 800):
        assert wa.schritt(welt(t, LORD, einheit(20, 1, 22, 100, 100))) == []
    fern = einheit(60, 2, 11, 141, 100)  # 41 Felder: knapp ausser Reichweite
    for t in (810, 1000, 1400):
        assert (
            wa.schritt(
                welt(
                    t,
                    LORD,
                    fern,
                    einheit(20, 1, 22, 100, 100, zielart=4, zieleinheit=60, schusseinheit=60),
                )
            )
            == []
        )
    f = wa.schritt(
        welt(
            1410,
            LORD,
            fern,
            einheit(20, 1, 22, 100, 100, zielart=4, zieleinheit=60, schusseinheit=60),
        )
    )
    assert [x["art"] for x in f] == ["F2 steht"]


def test_lies_wartet_auf_einen_ruhigen_kernstand():
    """Lauf 3 (10.11. 23:43): Beim Partieende gab Leitung.lesen() None, die Wache stuerzte ab."""
    from selfaware.tools.checks.fehlerwache import lies

    staende = iter([None, None, welt(5)])

    class Le:
        def lesen(self):
            return next(staende)

    assert lies(Le(), warte=0).tick == 5


def test_wache_wartet_auf_einen_leeren_kern_statt_abzustuerzen():
    """11.11. 22:02: frisch gestartete Instanz - der Kern hatte noch nichts geschrieben (Kennung 0x0 / Aufbau 0), die Wache
    brach ab. Jetzt wartet sie, und der erste Stand gilt schon als die neue Partie."""
    from selfaware.game.kern_leitung import FalscherAufbau
    from selfaware.tools.checks import fehlerwache as FW

    class Leitung:
        def __init__(self):
            self.n = 0

        def lesen(self):
            self.n += 1
            if self.n <= 2:
                raise FalscherAufbau("Kennung 0x0 / Aufbau 0")
            return type("Welt", (), {"tick": 120})()

    le = Leitung()
    assert FW._kern_leer(le) is True
    assert FW.lies(le, warte=0).tick == 120 and le.n == 3
