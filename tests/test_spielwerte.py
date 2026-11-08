"""P3 (B-155): Spielwerte aus der Messung und die umgestellten Module (offline, ohne Spiel)."""

import math
import os

import pytest

import selfaware.services.gefecht as gefecht
import selfaware.services.schussfeld as schussfeld
import selfaware.services.spielwerte as sw
from selfaware import workspace

# sicht.py liest beim Laden VillageStudio/lib/gebaeude.json - das Nachbar-Repo fehlt in der Pruefung auf GitHub
GEBAEUDE_DA = os.path.isfile(os.path.join(workspace.VILLAGE_STUDIO, "lib", "gebaeude.json"))


def test_erfassen_wie_gemessen():
    # S9: Pfeil und Bolzen 40, Stein 18, Feuer 11
    assert sw.ERFASSEN_FERN == {22: 40, 23: 40, 70: 40, 74: 40, 72: 18, 76: 11}


def test_reichweite_ist_luftlinie():
    assert sw.in_reichweite((0, 0), (40, 0), 22)
    assert not sw.in_reichweite((0, 0), (41, 0), 22)
    assert sw.in_reichweite((0, 0), (28, 28), 22)  # 39,6 Felder
    assert not sw.in_reichweite((0, 0), (29, 29), 22)  # 41,0 Felder, im Schach-Abstand nur 29
    assert not sw.in_reichweite((0, 0), (1, 0), 24)  # Speertraeger schiesst nicht


def test_gefahr_erfassen_plus_zielzeit():
    assert sw.gefahr(22) == 44  # 40 + max(4, 56/16)
    assert math.isclose(sw.gefahr(23), 40 + 137 / 16.0)  # Armbrust zielt 137 Takte
    assert sw.gefahr(72) == 22
    assert sw.gefahr(76) == 15
    assert sw.gefahr(24) is None
    assert sw.in_gefahr((0, 0), (44, 0), 22)
    assert not sw.in_gefahr((0, 0), (45, 0), 22)


def test_tempo_haengt_am_befehl():
    assert 15.5 < sw.takte_je_feld(22, "direkt") < 16.5
    assert 11.5 < sw.takte_je_feld(22, "trupp") < 12.5
    assert sw.takte_je_feld(22, "angriff") == sw.takte_je_feld(22, "trupp")
    assert 23.5 < sw.takte_je_feld(23, "trupp") < 24.5  # Armbrust immer 24
    assert 15.5 < sw.takte_je_feld(73, "trupp") < 16.5  # Assassine auch im Trupp 16
    assert sw.takte_je_feld(9999, "direkt") == 16.0
    assert sw.takte_je_feld(9999, "trupp") == 12.0


def test_nahkampf_je_art():
    assert sw.nahkampf_je_takt(24, 73) == 25  # Speer an Assassine
    assert sw.nahkampf_je_takt(27, 73) == 150  # Schwert an Assassine
    assert sw.nahkampf_je_takt(9999, 73, 60) == 60  # ungemessen -> Ersatz


def test_ersatz_ohne_messdatei():
    w = sw._laden("gibt_es_nicht.json")
    assert w["erfassen"][22] == 40
    assert w["tempo"][("trupp", 73)] == 16.0
    assert "Ersatz" in w["quelle"]


@pytest.mark.skipif(not GEBAEUDE_DA, reason="VillageStudio fehlt (sicht.py braucht gebaeude.json)")
def test_module_nutzen_dieselbe_quelle():
    import selfaware.services.sicht as sicht

    assert sicht.REICHWEITE == gefecht.FERN_REICH == sw.ERFASSEN_FERN
    assert schussfeld.REICHWEITE == {t: sw.gefahr(t) for t in sw.ERFASSEN_FERN}
    assert gefecht.TEMPO_ART[73] == sw.takte_je_feld(73, "trupp")


def test_schussfeld_zaehlt_luftlinie():
    sch = [((100, 100), 44)]
    assert schussfeld.gefahr_am((130, 130), sch) == 1  # 42,4 Felder
    assert schussfeld.gefahr_am((132, 132), sch) == 0  # 45,3 Felder, im Schach-Abstand 32


def _bogen_gegen(x, y):
    schaden = {22: {24: 10.0}, 24: {22: 0.0}}
    wir = [dict(typ=22, leben=100, x=0, y=0, steht=True)]
    sie = [dict(typ=24, leben=1000, x=x, y=y, steht=True)]
    return gefecht.simuliere(wir, sie, schaden=schaden, bis=10)[1]


def test_gefecht_schiesst_nur_in_luftlinie():
    assert _bogen_gegen(40, 0) < 1000  # 40 Felder gerade: in Reichweite
    assert _bogen_gegen(29, 29) == 1000  # 41 Felder schraeg: ausser Reichweite


def _rest_nach(typ, bis):
    wir = [dict(typ=typ, leben=1000, x=0, y=0)]
    sie = [dict(typ=71, leben=1000, x=49, y=0, steht=True)]
    return gefecht.simuliere(wir, sie, schaden={typ: {71: 1.0}, 71: {typ: 0.0}}, bis=bis)[1]


def test_gefecht_laeuft_mit_tempo_der_art():
    # 48 Felder bis zur Beruehrung: Speertraeger im Angriffsbefehl 12 Takte je Feld -> ~580 Takte
    # (mit dem alten Pauschaltempo 15 waeren es ~720); Assassine 16 Takte je Feld -> ~770 Takte
    assert _rest_nach(24, 560) == 1000
    assert _rest_nach(24, 620) < 1000
    assert _rest_nach(73, 740) == 1000
    assert _rest_nach(73, 800) < 1000


def test_gefecht_haengt_nicht_an_der_seitenfolge():
    # beide Seiten ziehen gleichzeitig: dasselbe Duell, Seiten getauscht, gleiches Ergebnis
    a = dict(typ=73, leben=12500, x=100, y=100)
    b = dict(typ=73, leben=6000, x=110, y=100)
    r_ab = gefecht.simuliere([dict(a)], [dict(b)])
    r_ba = gefecht.simuliere([dict(b)], [dict(a)])
    assert math.isclose(r_ab[0], r_ba[1])
    assert math.isclose(r_ab[1], r_ba[0])
    assert r_ab[2] == r_ba[2]
