"""#360 Sklaven hinter dem Gebaeude (Daniel 16.11.2026 00:22: "sklaven stehen einfach rum und machen nichts anstatt sich aufzusplitten
hinterum zu gehen und einzeln auf gebaeude zu gehen in einer art dass sie sich hinter den gebaeuden dodgen vor schuetzen").
Probe 5 (lage_20261116_002033_i2_sp2, Takt 7.300-10.700): alte Regel 0,1 freie Ziele je Runde, neue 12,1 (Messung:
DD-Berichte/SAI/SAI_2026-11-15_bestand/sklaven_deckung_messen.py)."""

from selfaware.micro import wegfuehrung as W
from selfaware.micro.tasks import raids as RA


def _e(owner, typ, x=100, y=100, leben=10000):
    return {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte=None, bis=None):
        self.liste.append(b)


def _trupp():
    bt = RA.Brandtrupp(1, lambda nr: 0)
    bt.weg = W.Wegfuehrung(1)
    return bt


# Holzfaellerhuette (Typ 3, 3x3: Felder 200-202 x 100-102), ein Bogenschuetze 40 Felder noerdlich
G = {7: _e(2, 3, 200, 100)}
SCHUETZE = {60: _e(2, 22, 201, 60)}


def test_deckungsplatz_liegt_hinter_dem_gebaeude():
    bild = W.Gefahr(dict(SCHUETZE), G, 1)
    gefahr, platz, ring = bild.deckung(7, G[7], RA.SKLAVE)
    assert gefahr == 0 and platz[1] == 103, (
        platz
    )  # Suedseite: das Gebaeude liegt zwischen Schuetze und Platz
    assert bild.an((201, 99), RA.SKLAVE) == 1  # Nordseite: getroffen
    assert (201, 103) in ring and (201, 101) not in ring


def test_ein_schuetze_vor_dem_gebaeude_sperrt_es_nicht_mehr():
    bt = _trupp()
    L = {**SCHUETZE, 1: _e(1, 71, 100, 100)}
    bt.schritt(L, G, Befehle())
    assert bt.ziel.get(1) == 7, bt.absicht
    assert bt.moeglich(7, L, G)


def test_schuetzen_auf_beiden_seiten_sperren_es():
    bt = _trupp()
    L = {**SCHUETZE, 61: _e(2, 22, 201, 142), 1: _e(1, 71, 100, 100)}
    bt.schritt(L, G, Befehle())
    assert 1 not in bt.ziel and bt.absicht[1][2] == "no_free_target"


def test_sklaven_teilen_sich_auf():
    bt = _trupp()
    G2 = {**G, 8: _e(2, 3, 200, 120), 9: _e(2, 3, 220, 110)}
    L = {**SCHUETZE, 1: _e(1, 71, 100, 100), 2: _e(1, 71, 100, 101), 3: _e(1, 71, 101, 100)}
    bt.schritt(L, G2, Befehle())
    assert sorted(bt.ziel.values()) == [7, 8, 9], bt.ziel
    assert not bt.dazu


def test_angriff_erst_auf_der_gedeckten_seite():
    w = W.Wegfuehrung(1)
    # Sklave noerdlich, 2 Felder vor dem Ankerfeld: frueher sofort Angriff (4 Felder), jetzt erst laufen auf die Suedseite
    L = {**SCHUETZE, 1: _e(1, 71, 201, 98)}
    b = Befehle()
    w.fuehre(1, "gebaeude", 7, "brandtrupp")
    st = w.schritt(L, G, b)
    assert st[1] == "unterwegs", st
    lauf = [x["angriff"] for x in b.liste]
    assert lauf and "gebaeude" not in lauf[0], lauf
    # am Deckungsplatz: Angriff
    L[1] = _e(1, 71, 201, 103)
    b = Befehle()
    st = w.schritt(L, G, b)
    assert st[1] == "greift_an" and b.liste[0]["angriff"].get("gebaeude") == 7, (st, b.liste)


def test_andere_zwecke_wie_bisher():
    w = W.Wegfuehrung(1)
    L = {**SCHUETZE, 1: _e(1, 24, 201, 98)}
    b = Befehle()
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    st = w.schritt(L, G, b)
    # Nahkampf-Raid: noch ohne Deckungsplatz (nur auf Daniels Wort) - der Standplatz ist das Ankerfeld, das in Gefahr liegt
    assert st[1] in ("greift_an", "gefahr"), st


def test_ohne_wegfuehrung_alte_regel():
    # Schuetze 15 Felder noerdlich: die alte Regel (jeder Schuetze bis 20 Felder) sperrt, mit Wegfuehrung deckt das Gebaeude die Suedseite
    L = {60: _e(2, 22, 201, 85), 1: _e(1, 71, 100, 100)}
    assert not RA.Brandtrupp(1, lambda nr: 0).moeglich(7, L, G)
    assert _trupp().moeglich(7, L, G)
