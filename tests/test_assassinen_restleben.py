"""Daniel 16.11.2026 19:42 (Bild DD-Berichte/SAI/SAI_2026-11-16_bilder/daniel_1942_kornspeicher_fast_kaputt.webp): "warum hier eine assassine
sich nicht opfert um den kornspeicher der fast kaputt ist zu nehmen, die einheiten sollten die lebenspunkte der gebaeude kennen".
Die Zielwahl der Assassinen rechnet mit der Arbeit, die am Gebaeude noch fehlt."""

from selfaware.micro.tasks import assassinen as AS


class _Sicht:
    def sicht_abstand(self, p):
        return 50


def _assassine(beschuss=0.0):
    a = object.__new__(AS.Einzeln)
    a._route_sperre, a.jetzt, a.entdeckt = {}, 0, {}
    a._gb_max = {7: 1000, 8: 1000}
    a._beschuss_angriff = lambda gn, G, ort: beschuss
    a._sicht = _Sicht()
    return a


L = {1: {"leben": 12500, "x": 100, "y": 100}}
G = {
    7: {
        "typ": 19,
        "x": 110,
        "y": 100,
        "leben": 1000,
        "besitzer": 1,
    },  # Kornspeicher heil, 10 Felder
    8: {
        "typ": 19,
        "x": 114,
        "y": 100,
        "leben": 100,
        "besitzer": 1,
    },  # Kornspeicher fast kaputt, 14 Felder
}
K = [(7, (110, 100), 19, True, 0, 0, 0, None, 0), (8, (114, 100), 19, True, 0, 0, 0, None, 0)]


def test_fast_zerstoertes_gebaeude_wird_gewaehlt():
    beste = _assassine()._ziel_bewerten(1, (100, 100), K, {}, L, G, None, {}, 0.10, 0.05)
    assert beste[1][0] == 8


def test_restleben_senkt_das_todesrisiko_am_ziel():
    # unter Beschuss am Ziel: am fast zerstoerten Gebaeude steht die Assassine kuerzer, das Risiko faellt unter die Grenze
    # (Grenzen wie im Spiel: ZIEL_RISIKO_WEG 0,10, ZIEL_RISIKO 0,05 fuer beobachtete Ziele)
    a = _assassine(beschuss=2.0)
    heil = a._ziel_bewerten(
        1, (100, 100), K[:1], {}, L, G, None, {}, a.ZIEL_RISIKO_WEG, a.ZIEL_RISIKO
    )
    kaputt = a._ziel_bewerten(
        1, (100, 100), K[1:], {}, L, G, None, {}, a.ZIEL_RISIKO_WEG, a.ZIEL_RISIKO
    )
    assert heil is None  # Risiko 2 x (202 + 10 x 16) / 12.500 = 5,8 % - ueber der Grenze
    assert kaputt is not None and kaputt[2] <= a.ZIEL_RISIKO  # 2 x (20 + 14 x 16) / 12.500 = 3,9 %


def test_rest_anteil():
    a = _assassine()
    assert (
        a._rest_anteil(7, G) == 1.0 and a._rest_anteil(8, G) == 0.1 and a._rest_anteil(99, G) == 1.0
    )
