"""10.11.2026 (Daniel beim Zuschauen): Bierkette nach Bedarf - Schenke erst mit Bier im Lager, Hopfen und Brauereien nach dem Lager,
keine feste Obergrenze. Ohne Spiel."""

from selfaware.macro import bierkette as BK


def kette():
    return BK.Bierkette(1, lambda *a: True, lambda typ, kern, r: [(10, 10)], lambda typ, ware: 0)


def arten(b, st, hopfen=0, brauerei=0, schenke=0):
    return [
        t for t, _ in b.reihe(st, {BK.HOPFEN: hopfen, BK.BRAUEREI: brauerei, BK.SCHENKE: schenke})
    ]


def fenster(b, werte):
    """werte: [(hopfen, bier)] gleichmaessig ueber ein ganzes Fenster."""
    for i, (h, bier) in enumerate(werte):
        b._merken({"t": i * b.FENSTER // (len(werte) - 1), "hopfen": h, "bier": bier})


def test_schenke_erst_wenn_bier_im_lager_ist():
    b = kette()
    assert BK.SCHENKE not in arten(b, {"leute": 60, "bier": 0, "hopfen": 2}, hopfen=1, brauerei=1)
    assert arten(b, {"leute": 60, "bier": 3, "hopfen": 0}, hopfen=1, brauerei=1)[0] == BK.SCHENKE


def test_brauerei_sobald_hopfen_liegt_und_erste_hopfenfarm_ab_dreissig_einwohnern():
    b = kette()
    assert arten(b, {"leute": 20}) == []
    assert arten(b, {"leute": 30}) == [BK.HOPFEN]
    assert arten(b, {"leute": 30, "hopfen": 3}, hopfen=1) == [BK.BRAUEREI]


def test_weitere_hopfenfarm_nur_wenn_brauereien_hungern_ohne_feste_grenze():
    b = kette()
    fenster(b, [(0, 0)] * 6)
    assert BK.HOPFEN in arten(
        b, {"leute": 200, "hopfen": 0, "bier": 0}, hopfen=5, brauerei=5, schenke=5
    )
    b = kette()
    fenster(b, [(0, 1), (0, 2), (0, 3), (0, 4)])  # Bier staut sich: genug Hopfen
    assert BK.HOPFEN not in arten(
        b, {"leute": 200, "hopfen": 0, "bier": 4}, hopfen=2, brauerei=2, schenke=2
    )


def test_zweite_schenke_nur_wenn_bier_sich_staut_und_einwohner_reichen():
    b = kette()
    fenster(b, [(0, 2), (0, 3), (0, 5), (0, 6)])
    assert BK.SCHENKE in arten(b, {"leute": 60, "bier": 6}, hopfen=1, brauerei=1, schenke=1)
    assert BK.SCHENKE not in arten(b, {"leute": 30, "bier": 6}, hopfen=1, brauerei=1, schenke=1)


def test_kausal_planer_baut_mit_bier_keinen_hopfen():
    """Daniel 21:43: 15 Hopfenfarmen kamen vom Kausal-Planer, der Hopfen als Ware rechnet; mit bier=ja gehoert Hopfen der Bierkette."""
    import pathlib

    lenker = (
        pathlib.Path(__file__).resolve().parents[1] / "src/selfaware/runtime/live/erstes_spiel.py"
    ).read_text(encoding="utf-8")
    assert "for typ_a in (3, 32, 7, 5, 20) + (() if BIER else (31,)):" in lenker
