"""B-182 Rolle je Einheit, jede Runde neu (micro/rollen.py). Daniel 13.11.2026 23:07: "Was macht der gegner und wird verteidigung,
raid oder angriff gebraucht? Und dann wird bestimt was pro einheit passiert"; 23:14 "Ja, bauen"."""

import os

from selfaware.micro import rollen as RO
from selfaware.micro import zuweisung as ZW

QUELLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "selfaware")


def _e(sp, typ, x, y, **k):
    d = {
        "besitzer": sp,
        "typ": typ,
        "x": x,
        "y": y,
        "leben": 10000,
        "zustand": 1,
        "laufx": x,
        "laufy": y,
        "nahziel": 0,
        "zieleinheit": 0,
    }
    d.update(k)
    return d


def test_ohne_bedrohung_raiden_die_freien_speertraeger_wie_in_partie_7():
    # Partie 20261113_225710 Takt 665: 333-335 frei (330-332/336 graben, die Bogenschuetzen fuehrt der Vorstoss), kein Feind daheim
    L = {n: _e(1, 24, 151, 281) for n in (333, 334, 335)}
    L[900] = _e(2, 24, 240, 160)  # ein Feind weit weg an seiner eigenen Burg
    rollen, text = RO.verteilen(L, [(146, 272), (153, 284)], 1, {333, 334, 335}, set(L) - {900})
    assert (
        rollen == {333: RO.RAID, 334: RO.RAID, 335: RO.RAID} and text == "keine Bedrohung - 3 raid"
    )
    rollen, _ = RO.verteilen(L, [(146, 272)], 1, {333, 334, 335}, set(), raid=False)
    assert set(rollen.values()) == {RO.WAECHTER}  # ohne Nahkampf-Raid bleiben sie beim Waechter


def test_bei_bedrohung_verteidigt_die_kleinste_gruppe_der_rest_raidet():
    gebaeude = [(150, 160), (145, 215), (150, 200)]
    L = {
        60: _e(1, 24, 155, 158),
        61: _e(1, 24, 156, 158),
        62: _e(1, 75, 156, 159),
        63: _e(1, 24, 200, 100),
        156: _e(2, 71, 148, 163),
    }  # ein feindlicher Sklave an unserem Gebaeude (150,160)
    kand = {60, 61, 62, 63}
    rollen, text = RO.verteilen(L, gebaeude, 1, kand, kand)
    wir = [
        dict(nr=n, typ=L[n]["typ"], leben=L[n]["leben"], x=L[n]["x"], y=L[n]["y"])
        for n in sorted(kand)
    ]
    gewaehlt, gewinnt, _ = ZW.kleinste_gruppe(
        wir, [dict(typ=71, leben=10000, x=148, y=163, steht=True)]
    )
    assert gewinnt and {n for n, r in rollen.items() if r == RO.VERTEIDIGUNG} == set(gewaehlt)
    assert rollen[63] == RO.RAID and 0 < len(gewaehlt) < 4
    assert text.startswith("Bedrohung 1 Feinde: %d verteidigen" % len(gewaehlt))


def test_gewinnt_keine_gruppe_bleiben_alle_beim_waechter():
    L = {60: _e(1, 24, 155, 158)}
    L.update(
        {200 + i: _e(2, 28, 150 + i % 3, 162) for i in range(12)}
    )  # zwoelf Ritter an unserem Gebaeude
    rollen, text = RO.verteilen(L, [(150, 160)], 1, {60}, {60})
    assert rollen == {60: RO.WAECHTER} and "keine Gruppe gewinnt" in text


def test_die_bedrohung_ist_die_regel_des_waechters():
    geb = [(100, 100)]
    assert RO.an_gebaeuden({1: _e(2, 24, 109, 100)}, geb, 1) == {}  # 9 Felder: noch nicht
    assert set(RO.an_gebaeuden({1: _e(2, 24, 108, 100)}, geb, 1)) == {1}  # 8 Felder
    assert set(RO.an_gebaeuden({1: _e(2, 24, 150, 100, laufx=106, laufy=100)}, geb, 1)) == {
        1
    }  # Laufziel 6 Felder
    assert RO.an_gebaeuden({1: _e(2, 7, 100, 100)}, geb, 1) == {}  # ein Arbeiter ist keine Truppe
    far = {1: _e(2, 24, 141, 100, nahziel=5), 2: _e(2, 24, 140, 100, nahziel=5)}
    assert RO.angreifer(far, geb, 1, {5}) == {2}  # bis ANGREIFER_R 40 Felder


def test_der_nahkampf_raid_nimmt_und_gibt_einheiten_nach_der_rolle():
    from selfaware.micro.tasks.nahkampf import NahkampfRaid

    nk = NahkampfRaid(1)
    nk.mitglieder = {10}
    nk.ziel = {10: ("g", 5)}
    nk.zuteilen({11, 12}, {10})
    assert nk.mitglieder == {11, 12} and 10 not in nk.ziel


def test_der_lenker_verteilt_die_rollen_vor_dem_schritt_des_waechters():
    quelle = open(
        os.path.join(QUELLE, "runtime", "live", "erstes_spiel.py"), encoding="utf-8"
    ).read()
    v, z, w = (
        quelle.find("RO.verteilen("),
        quelle.find("nk.zuteilen("),
        quelle.find("ereignis = w.schritt("),
    )
    assert 0 < v < z < w
