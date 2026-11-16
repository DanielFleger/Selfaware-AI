"""B-182 S146 (Daniel 14.11.2026 23:03 "ja probieren wir es so, sollte es zu sehr laggen müssen wir das vlt schlauer gestalten"): die
Weg-Ebene wird auch neu gelesen, sobald ein Gebaeude dazukommt - Partie 18 legte einen Wegpunkt in einen gegnerischen Hof (Gebaeude
63, Typ 31), den die Karte der Wegfuehrung nicht kannte, und das Spiel verwarf den Laufbefehl. Ohne Spiel."""

import pathlib

from selfaware.services import wegkarte as W

LENKER = (
    pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
).read_text(encoding="utf-8")


def test_erste_karte_neues_gebaeude_und_alle_n_runden():
    G = {10: {"typ": 32}, 63: {"typ": 31}}
    assert W.neu_lesen(1, None, G, None, 20) == "erste Karte"
    bekannt = {10: 32}
    assert W.neu_lesen(2, 1, G, bekannt, 20) == "neue Gebaeude 1 (63)"  # der Hof aus Partie 18
    bekannt = {10: 32, 63: 31}
    assert W.neu_lesen(3, 2, G, bekannt, 20) is None  # nichts dazugekommen
    assert (
        W.neu_lesen(3, 2, {63: {"typ": 31}}, bekannt, 20) is None
    )  # nur abgerissen: kein Grund (Daniel: "dazukommt")
    assert (
        W.neu_lesen(3, 2, {10: {"typ": 32}, 63: {"typ": 30}}, bekannt, 20) == "neue Gebaeude 1 (63)"
    )  # neue Art unter der Nummer
    assert W.neu_lesen(22, 2, G, bekannt, 20) == "alle 20 Runden"


def test_viele_neue_gebaeude_kurz_genannt():
    G = {n: {"typ": 1} for n in range(100, 108)}
    assert W.neu_lesen(5, 4, G, {}, 20) == "neue Gebaeude 8 (100, 101, 102, 103, 104 ...)"


def test_der_lenker_fragt_neu_lesen_und_schreibt_jedes_lesen_mit():
    assert (
        "W_karte.neu_lesen(runde, wegf_karte_runde, G, wegf_karte_geb, WEGKARTE_RUNDEN)" in LENKER
    )
    assert '"WEGKARTE gelesen Runde %d Takt %s (%s, %s), %.2f s"' in LENKER
    # S147: bei neuen Gebaeuden nur die Ausschnitte um sie
    assert (
        "W_karte.rechtecke_fuer(G, wegf_karte_geb)" in LENKER
        and "W_karte.flicken(neue_karte, k_wk)" in LENKER
    )
    assert 'tz = uhr("wegkarte", tz)' in LENKER


def test_je_neues_gebaeude_ein_ausschnitt_und_flicken_aendert_nur_ihn(monkeypatch):
    import selfaware.services.sicht as sicht

    monkeypatch.setitem(sicht.GROESSE, 31, 9)
    G = {
        10: {"typ": 32, "x": 5, "y": 5},
        63: {"typ": 31, "x": 242, "y": 168},
        64: {"typ": 31, "x": 398, "y": 0},
    }
    assert W.rechtecke_fuer(G, {10: 32, 64: 31}) == [
        (240, 166, 252, 178)
    ]  # der Hof aus Partie 18: Flaeche 9 plus RAND 2
    assert W.rechtecke_fuer(G, {10: 32}) == [
        (240, 166, 252, 178),
        (396, 0, 399, 10),
    ]  # am Kartenrand abgeschnitten
    assert W.rechtecke_fuer(G, dict((n, g["typ"]) for n, g in G.items())) is None  # nichts Neues
    viele = {n: {"typ": 31, "x": 10 * n, "y": 10} for n in range(W.AUSSCHNITT_BIS + 1)}
    assert W.rechtecke_fuer(viele, {}) is None  # zu viele: die ganze Karte
    karte = ["." * 400 for _ in range(400)]
    k = {
        "x0": 245,
        "y0": 174,
        "x1": 247,
        "y1": 174,
        "f": {
            (245, 174): (0, 0, 0, 0, 0, 0),
            (246, 174): (0, 0, 0, 0, 0, 0),
            (247, 174): (0xFF, 0, 1, 0, 0, 0),
        },
    }
    neu = W.flicken(karte, k)
    assert (
        neu[174][244:249] == ".##.." and neu[173] == karte[173] and karte[174] == "." * 400
    )  # die alte Karte bleibt


def test_ausschnitt_holen_nimmt_nur_die_passende_antwort(monkeypatch):
    kopf = {"tick": 5394, "x0": 230, "y0": 160, "x1": 260, "y1": 190, "f": {}}
    monkeypatch.setattr(W, "lesen", lambda pfad=None: dict(kopf))
    antwort = [
        "[villagestudio]: WEGKARTE Tick 5394 (230,160)-(260,190): 961 Felder, 900 mit Weg -> abzug/wegkarte.txt"
    ]
    assert (
        W.ausschnitt_holen(230, 160, 260, 190, befehl_fn=lambda b, w, bis=None: antwort)["tick"]
        == 5394
    )
    assert (
        W.ausschnitt_holen(230, 160, 261, 190, befehl_fn=lambda b, w, bis=None: antwort) is None
    )  # anderes Rechteck
    assert W.ausschnitt_holen(230, 160, 260, 190, befehl_fn=lambda b, w, bis=None: []) is None


def test_feld_ohne_eingang_ist_nicht_begehbar():
    """16.11.2026 (Probe 16): Wegpunkt (190, 158) auf einem Lagerplatz hatte Ausgaenge, aber keinen Eingang - das Spiel fuehrte den Laufbefehl
    nie aus. als_gelaende nennt nur betretbare Felder begehbar; flicken laesst Felder am Rand des Ausschnitts gelten (Nachbar draussen)."""
    from selfaware.services import wegkarte as WK

    alle = 0xFF
    f = {(x, y): (alle, 0, 0, 0, 0, -1) for x in range(5) for y in range(5)}
    for bit, (
        dx,
        dy,
    ) in WK.RICHTUNG.items():  # (2, 2): kein Nachbar fuehrt hinein, er selbst fuehrt hinaus
        f[(2 - dx, 2 - dy)] = (alle & ~bit, 0, 0, 0, 0, -1)
    k = {"f": f, "x0": 0, "y0": 0, "x1": 4, "y1": 4}
    gel = WK.als_gelaende(k, groesse=5)
    assert gel[2][2] == "#" and gel[0][0] == "." and gel[2][1] == "."
    zeilen = WK.flicken(["....."] * 5, {"f": f, "x0": 1, "y0": 1, "x1": 3, "y1": 3})
    assert zeilen[2][2] == "#" and zeilen[1][1] == ".", zeilen
