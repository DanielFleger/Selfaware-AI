"""B-145 S4: der Leser des gemeinsamen Speichers versteht den Aufbau 3 und lehnt einen fremden ab (offline)."""

import struct

import pytest

from selfaware.game import kern_leitung as KL


def _puffer(aufbau=KL.AUFBAU):
    b = bytearray(KL.GROESSE)
    struct.pack_into(KL.KOPF_FORMAT, b, 0, KL.KENNUNG, aufbau, 4, 40471, 2, 1, 2, 1, 9, 63, 9, 3)
    struct.pack_into(
        KL.EINHEIT_FORMAT, b, KL.KOPF, 85, 12000, 1, 70, 163, 192, 6, 163, 192, 16, 17, 0, 0, 0
    )
    struct.pack_into(
        KL.EINHEIT_FORMAT,
        b,
        KL.KOPF + KL.EINHEIT,
        91,
        28000,
        1,
        26,
        162,
        191,
        2,
        162,
        191,
        16,
        17,
        0,
        0,
        -1,
    )
    start = KL.KOPF + KL.MAX_EINHEITEN * KL.EINHEIT
    struct.pack_into(
        KL.GEBAEUDE_FORMAT, b, start, 239, 46, 2, 149, 104, 1500, 46
    )  # B-150: Feuerwert 46 = brennt
    struct.pack_into("<i", b, KL.VORRAT_START + (1 * KL.WAREN + 15) * 4, 5000)
    struct.pack_into("<i", b, KL.VORRAT_START + (1 * KL.WAREN + 2) * 4, 120)
    return bytes(b)


def test_aufbau_3_wird_vollstaendig_gelesen():
    w = KL.entpacken(_puffer())
    assert (w.tick, w.epoche, w.ich, w.kern, w.graben_geplant, w.graben_ausgehoben) == (
        40471,
        2,
        1,
        9,
        9,
        63,
    )
    assert set(w.einheiten) == {85, 91}
    assert w.einheiten[85]["laufx"] == 163 and w.einheiten[85]["gruppe"] == 16
    assert w.einheiten[91]["nahziel"] == -1
    assert w.beschuss == 3
    assert w.gebaeude == {
        239: {"nr": 239, "typ": 46, "besitzer": 2, "x": 149, "y": 104, "leben": 1500, "feuer": 46}
    }
    assert w.vorrat[1]["gold"] == 5000 and w.vorrat[1]["holz"] == 120 and w.vorrat[2]["gold"] == 0


def test_fremder_aufbau_wird_abgelehnt():
    with pytest.raises(KL.FalscherAufbau):
        KL.entpacken(_puffer(aufbau=2))
