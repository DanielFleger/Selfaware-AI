"""Wertungsmesser je Einheit (Daniel 16.11.2026 17:39/17:54: Punkte je Einheit und Partie, "wo man am ende pro einheit genau sieht welche
punkte sie wofuer bekommen hat"). Jede Messgroesse an einer kleinen Partie im echten Format des Lageprotokolls."""

import gzip
import json

import pytest

from selfaware.telemetry import wertung as W

E_KOPF = (
    "nr besitzer typ x y leben zustand zielart zieleinheit zieluid zielgebaeude ziel zielx ziely laufx laufy auswahlvon auswahlmarke "
    "gruppe gruppenuid ladung arbeitsplatz erreichbar nahziel nahangreifer"
)
G_KOPF = "nr besitzer typ x y leben uid erreichbar vorrat grenze verbund ware feuer"
SP = 2


def _e(nr, besitzer, typ, x, y, leben, zustand=2, zieleinheit=0, nahziel=0, zielgebaeude=0):
    w = dict.fromkeys(E_KOPF.split(), 0)
    w.update(
        nr=nr,
        besitzer=besitzer,
        typ=typ,
        x=x,
        y=y,
        leben=leben,
        zustand=zustand,
        zieleinheit=zieleinheit,
        nahziel=nahziel,
        zielgebaeude=zielgebaeude,
        laufx=x,
        laufy=y,
    )
    return " ".join(str(w[k]) for k in E_KOPF.split())


def _g(nr, besitzer, typ, x, y, leben, uid, feuer=0):
    w = dict.fromkeys(G_KOPF.split(), 0)
    w.update(
        nr=nr, besitzer=besitzer, typ=typ, x=x, y=y, leben=leben, uid=uid, erreichbar=1, feuer=feuer
    )
    return " ".join(str(w[k]) for k in G_KOPF.split())


def _partie(tmp_path, runden):
    """runden: [(Takt, [Einheiten-Zeilen], [Gebaeude-Zeilen], {nr: (Aktion, Ziel, Grund)})] - die Absichten einer Runde gelten wie im
    echten Protokoll fuer die Zeit bis zur naechsten Zeile, stehen also in der naechsten Zeile."""
    p = tmp_path / "lage_20261116_120000_i2_sp2.jsonl.gz"
    with gzip.open(p, "wt", encoding="utf-8") as f:
        vorige = None
        for t, E, G, absicht in runden:
            ints = ""
            if vorige is not None:
                rows = ["tick %d" % vorige[0], "unit type owner action target reason path params"]
                for nr, (a, z, g) in sorted(vorige[1].items()):
                    rows.append("%d 24 test %s %s %s walking -" % (nr, a, z, g))
                ints = "\n".join(rows) + "\n"
            f.write(
                json.dumps(
                    {
                        "t": t,
                        "st": {},
                        "einheiten": "tick %d\n%s\n%s" % (t, E_KOPF, "\n".join(E)),
                        "gebaeude": "%s\n%s" % (G_KOPF, "\n".join(G)),
                        "intents": ints,
                    }
                )
                + "\n"
            )
            vorige = (t, absicht)
    return str(p)


def _einheit(erg, nr):
    return next(e for e in erg["einheiten"] if e["nr"] == nr)


LORD_FEIND = _e(900, 1, 55, 50, 50, 100000)  # ohne feindlichen Lord gaebe es keinen Kill-Takt


def test_gebaeude_angreifen_und_zerstoeren(tmp_path):
    # Huette (Typ 1, Grundflaeche 4x4 ab 200,100, Wert 12 = 1 Huette); Speertraeger 10 steht daneben und schlaegt (Zustand 107)
    angriff = {10: ("ATTACK_BUILDING", "B7", "best_value_per_tick")}
    p = _partie(
        tmp_path,
        [
            (
                1000,
                [_e(10, SP, 24, 199, 101, 12500, 107), LORD_FEIND],
                [_g(7, 1, 1, 200, 100, 100, 77)],
                angriff,
            ),
            (
                1100,
                [_e(10, SP, 24, 199, 101, 12500, 107), LORD_FEIND],
                [_g(7, 1, 1, 200, 100, 50, 77)],
                angriff,
            ),
            (1200, [_e(10, SP, 24, 199, 101, 12500, 2), LORD_FEIND], [], {}),
        ],
    )
    e = _einheit(W.messen(p), 10)
    assert e["menge"]["gebaeude_schaden"] == pytest.approx(1.0)
    assert e["menge"]["gebaeude_zerstoert"] == pytest.approx(1.0)
    assert any("zerstoert" in x[3] for x in e["ereignisse"])
    assert "steht_ohne_wirkung" not in e["menge"]  # wer Schaden macht, steht nicht ohne Wirkung


def test_stehen_ohne_wirkung_und_leben_dabei(tmp_path):
    # Probe 6, Speer 218: Angriffsabsicht, steht still (Zustand 2), kein Schaden am Ziel, verliert Leben
    angriff = {10: ("ATTACK_BUILDING", "B7", "keeps_target")}
    p = _partie(
        tmp_path,
        [
            (
                1000,
                [_e(10, SP, 24, 190, 101, 12500), LORD_FEIND],
                [_g(7, 1, 1, 200, 100, 100, 77)],
                angriff,
            ),
            (
                1500,
                [_e(10, SP, 24, 190, 101, 10000), LORD_FEIND],
                [_g(7, 1, 1, 200, 100, 100, 77)],
                angriff,
            ),
            (
                2000,
                [_e(10, SP, 24, 190, 101, 7500), LORD_FEIND],
                [_g(7, 1, 1, 200, 100, 100, 77)],
                angriff,
            ),
        ],
    )
    e = _einheit(W.messen(p), 10)
    assert e["menge"]["steht_ohne_wirkung"] == pytest.approx(1.0)  # 2 x 500 Takte
    assert e["menge"]["leben_beim_stehen"] == pytest.approx(5000 / 12500)
    assert "wartet_mit_grund" not in e["menge"]


def test_geplantes_warten_ist_eigene_groesse(tmp_path):
    warten = {10: ("WAIT_STAGING", "(190,101)", "no_free_target")}
    p = _partie(
        tmp_path,
        [
            (1000, [_e(10, SP, 24, 190, 101, 12500), LORD_FEIND], [], warten),
            (2000, [_e(10, SP, 24, 190, 101, 12500), LORD_FEIND], [], warten),
        ],
    )
    e = _einheit(W.messen(p), 10)
    assert (
        e["menge"]["wartet_mit_grund"] == pytest.approx(1.0)
        and "steht_ohne_wirkung" not in e["menge"]
    )


def test_kehrtwende(tmp_path):
    # Daniel 16.11. 00:09: "lief ewig in eine richtung nur um dann zurueckzugehen"
    los = {10: ("ATTACK_BUILDING", "B7", "x")}
    p = _partie(
        tmp_path,
        [
            (
                1000,
                [_e(10, SP, 24, 100, 100, 12500), LORD_FEIND],
                [_g(7, 1, 1, 300, 100, 100, 77)],
                los,
            ),
            (
                1100,
                [_e(10, SP, 24, 110, 100, 12500), LORD_FEIND],
                [_g(7, 1, 1, 300, 100, 100, 77)],
                los,
            ),
            (
                1200,
                [_e(10, SP, 24, 100, 100, 12500), LORD_FEIND],
                [_g(7, 1, 1, 300, 100, 100, 77)],
                los,
            ),
            (
                1300,
                [_e(10, SP, 24, 100, 100, 12500), LORD_FEIND],
                [_g(7, 1, 1, 300, 100, 100, 77)],
                los,
            ),
        ],
    )
    e = _einheit(W.messen(p), 10)
    assert e["menge"]["kehrtwende"] == pytest.approx(1.0)


def test_artwechsel_ist_kein_tod_aber_ein_kill_zaehlt(tmp_path):
    # Probe 7: 197 Mal wechselte ein Bauer die Art; dort wurde vorher ein "Kill" gezaehlt
    schuss = {20: ("ATTACK_UNIT", "U30", "worker_in_range")}
    p = _partie(
        tmp_path,
        [
            (
                1000,
                [
                    _e(20, SP, 22, 100, 100, 10000, 5, zieleinheit=30),
                    _e(30, 1, 3, 120, 100, 1000),
                    _e(31, 1, 1, 125, 100, 1000),
                    LORD_FEIND,
                ],
                [],
                schuss,
            ),
            (
                1100,
                [
                    _e(20, SP, 22, 100, 100, 10000, 5, zieleinheit=30),
                    _e(31, 1, 6, 125, 100, 1000),
                    LORD_FEIND,
                ],
                [],
                {},
            ),
        ],
    )
    erg = W.messen(p)
    e = _einheit(erg, 20)
    assert e["menge"]["bevoelkerung_kill"] == pytest.approx(
        1.0
    )  # Arbeiter 30 starb, Ziel des Schuetzen
    assert (
        erg["ohne_taeter"]["einheit_schaden"] == 0
    )  # Bauer 31 wurde Arbeiter (Typ 1 -> 6): kein Schaden, kein Tod


def test_eigene_arbeiter_werden_nicht_gewertet(tmp_path):
    p = _partie(
        tmp_path,
        [
            (1000, [_e(40, SP, 6, 50, 50, 1000), LORD_FEIND], [], {}),
            (2000, [_e(40, SP, 6, 50, 50, 1000), LORD_FEIND], [], {}),
        ],
    )
    assert W.messen(p)["einheiten"] == []


def test_punkte_nach_reglern():
    e = {"typ": 24, "menge": {"gebaeude_schaden": 2.0, "kehrtwende": 3.0}}
    reg = [
        {
            "id": "a",
            "messgroesse": "gebaeude_schaden",
            "arten": "alle",
            "gewicht": 1.5,
            "archiviert": False,
        },
        {"id": "b", "messgroesse": "kehrtwende", "arten": [24], "gewicht": -2, "archiviert": False},
        {
            "id": "c",
            "messgroesse": "kehrtwende",
            "arten": [71],
            "gewicht": -9,
            "archiviert": False,
        },  # andere Art
        {
            "id": "d",
            "messgroesse": "gebaeude_schaden",
            "arten": "alle",
            "gewicht": 100,
            "archiviert": True,
        },  # archiviert
    ]
    assert W.punkte(e, reg) == {"a": 3.0, "b": -6.0}


def test_regler_verlauf_und_zuruecknehmen(tmp_path, monkeypatch):
    monkeypatch.setattr(W, "REGLER_DATEI", str(tmp_path / "regler.json"))
    monkeypatch.setattr(W, "VERLAUF_DATEI", str(tmp_path / "verlauf.jsonl"))
    r = W.regler_lesen()
    assert {x["messgroesse"] for x in r} == set(W.MESSGROESSEN)
    r[0]["gewicht"] = 5.0
    W.regler_schreiben(r, "Test", "geaendert")
    assert W.regler_lesen()[0]["gewicht"] == 5.0
    assert W.regler_zuruecknehmen("Test")
    assert W.regler_lesen()[0]["gewicht"] == W.regler_standard()[0]["gewicht"]
    assert len(W.verlauf_lesen()) == 2  # der Verlauf behaelt beides


def test_seite_loescht_nie_sondern_archiviert(tmp_path, monkeypatch):
    from selfaware.tools.analysis import wertung_seite as WS

    monkeypatch.setattr(W, "REGLER_DATEI", str(tmp_path / "regler.json"))
    monkeypatch.setattr(W, "VERLAUF_DATEI", str(tmp_path / "verlauf.jsonl"))
    nur_einer = [dict(W.regler_standard()[0])]
    neu = WS.regler_pruefen(nur_einer)
    assert (
        len(neu) == len(W.MESSGROESSEN)
        and sum(1 for x in neu if x["archiviert"]) == len(W.MESSGROESSEN) - 1
    )
    with pytest.raises(ValueError):
        WS.regler_pruefen([{"id": "x", "messgroesse": "gibt_es_nicht", "gewicht": 1}])
    assert not WS.NAME_OK.match("../../geheim.jsonl.gz")


def test_ergebnis_und_kurzfassung(tmp_path):
    # Daniel 16.11.2026 18:16: wer gegen wen, wer gestorben, wer gewonnen
    p = _partie(
        tmp_path,
        [
            (
                1000,
                [_e(10, SP, 24, 199, 101, 12500), _e(901, SP, 55, 10, 10, 100000), LORD_FEIND],
                [],
                {},
            ),
            (1100, [_e(10, SP, 24, 199, 101, 12500), _e(901, SP, 55, 10, 10, 100000)], [], {}),
        ],
    )
    erg = W.messen(p)
    assert erg["ergebnis"] == "gewonnen" and erg["kill_takt"] == 1100
    assert [(s["nr"], s["lord_tod"], s["wir"]) for s in erg["spieler_liste"]] == [
        (1, 1100, False),
        (2, None, True),
    ]
    k = W.kurzfassung(erg)
    assert k["arten"]["24"]["n"] == 1 and k["ergebnis"] == "gewonnen" and not k["logbuch"]
    assert (
        "ohne_absicht" not in erg["einheiten"][0]["menge"]
    )  # ohne Logbuch kein Abzug fuers Nichtdenken
