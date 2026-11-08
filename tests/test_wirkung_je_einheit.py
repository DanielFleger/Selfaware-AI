"""B-171: Zuordnung von Toden und zerstoerten Gebaeuden in den Lageaufzeichnungen (offline)."""

from selfaware.tools.analysis import wirkung_je_einheit as W


def _e(nr, besitzer, typ, x=100, y=100, **w):
    return {
        "nr": nr,
        "besitzer": besitzer,
        "typ": typ,
        "x": x,
        "y": y,
        "nahziel": 0,
        "zieleinheit": 0,
        **w,
    }


def _g(nr, besitzer, typ, x=100, y=100, **w):
    return {"nr": nr, "besitzer": besitzer, "typ": typ, "x": x, "y": y, "feuer": 0, **w}


def _bild(t, einheiten=(), gebaeude=()):
    return {
        "t": t,
        "einheiten": {e["nr"]: e for e in einheiten},
        "gebaeude": {g["nr"]: g for g in gebaeude},
    }


def test_tabelle_liest_kopf_und_zeilen():
    t = W.tabelle("tick 5\nnr besitzer typ\n1 2 73\n2 x 3\n")
    assert t == {1: {"nr": 1, "besitzer": 2, "typ": 73}}


def test_tod_mit_ziel_wird_dem_schlaeger_gutgeschrieben():
    a = _bild(100, [_e(1, 1, 73, nahziel=2), _e(2, 2, 22)])
    ev = W.vergleiche(a, _bild(130, [_e(1, 1, 73, nahziel=0)]))
    assert len(ev) == 1 and ev[0]["sicher"] == "ziel" and ev[0]["art"] == "soldat"
    assert [u["nr"] for u in ev[0]["taeter"]] == [1]


def test_umwandlung_ist_kein_tod():
    a = _bild(100, [_e(1, 1, 1)])
    assert W.vergleiche(a, _bild(130, [_e(1, 1, 24)])) == []


def test_neuer_bewohner_desselben_platzes_ist_ein_tod():
    a = _bild(100, [_e(1, 1, 24), _e(2, 2, 26, x=101)])
    b = _bild(130, [_e(1, 1, 24, x=300), _e(2, 2, 26, x=101)])
    ev = W.vergleiche(a, b)
    assert [e["opfer"]["nr"] for e in ev] == [1]


def test_arbeiter_ohne_verursacher_zaehlt_nicht_als_verlust():
    a = _bild(100, [_e(1, 1, 3), _e(2, 2, 26, x=250)])
    ev = W.vergleiche(a, _bild(130, [_e(2, 2, 26, x=250)]))
    assert ev[0]["sicher"] == "keine" and ev[0]["taeter"] == []
    p = W.Partie()
    p.nimm(a, _bild(130, [_e(2, 2, 26, x=250)]))
    s = {
        "takte": {k[1:]: v for k, v in p.takte.items()},
        "gut": {k[1:]: v for k, v in p.gut.items()},
        "ver": {k[1:]: v for k, v in p.ver.items()},
    }
    assert W._kennzahlen(s)["arbeiter_verloren"] == 0


def test_schuetze_in_reichweite_gilt_als_nah():
    a = _bild(100, [_e(1, 1, 73), _e(2, 2, 22, x=130)])
    ev = W.vergleiche(a, _bild(130, [_e(2, 2, 22, x=130)]))
    assert ev[0]["sicher"] == "nah" and [u["nr"] for u in ev[0]["taeter"]] == [2]


def test_nahkaempfer_ausser_reichweite_gilt_nicht():
    a = _bild(100, [_e(1, 1, 73), _e(2, 2, 26, x=110)])
    assert W.vergleiche(a, _bild(130, [_e(2, 2, 26, x=110)]))[0]["sicher"] == "keine"


def test_mehrere_teilen_sich_die_gutschrift():
    a = _bild(100, [_e(1, 1, 73), _e(2, 2, 26, nahziel=1), _e(3, 2, 26, nahziel=1)])
    p = W.Partie()
    p.nimm(a, _bild(130, [_e(2, 2, 26), _e(3, 2, 26)]))
    assert sum(v for k, v in p.gut.items() if k[2] == "soldat") == 1


def test_gebaeude_mit_angreifer_und_abriss_ohne():
    a = _bild(100, [_e(1, 1, 71, zielgebaeude=7)], [_g(7, 2, 3), _g(8, 2, 3, x=300)])
    ev = W.vergleiche(a, _bild(130, [_e(1, 1, 71)]))
    arten = {e["opfer"]["nr"]: e["sicher"] for e in ev}
    assert arten == {7: "ziel", 8: "keine"}


def test_brennendes_gebaeude_wird_dem_zuendler_in_der_naehe_gutgeschrieben():
    a = _bild(100, [_e(1, 1, 71, x=108)], [_g(7, 2, 3, feuer=40)])
    ev = W.vergleiche(a, _bild(130, [_e(1, 1, 71, x=108)]))
    assert ev[0]["sicher"] == "nah" and [u["nr"] for u in ev[0]["taeter"]] == [1]


def test_grosse_luecke_wird_nicht_gewertet():
    p = W.Partie()
    assert p.nimm(_bild(100, [_e(1, 1, 73)]), _bild(100 + W.MAX_DT + 1)) == []
    assert p.luecken == 1 and not p.ver


def test_zeit_heim_und_draussen():
    p = W.Partie()
    a = _bild(100, [_e(1, 1, 73, x=105), _e(2, 1, 73, x=200)], [_g(9, 1, 41)])
    p.nimm(a, _bild(130, [_e(1, 1, 73, x=105), _e(2, 1, 73, x=200)], [_g(9, 1, 41)]))
    assert p.takte[(1, 73, "heim", "frueh")] == 30 and p.takte[(1, 73, "draussen", "frueh")] == 30


def test_einordnung_erkennt_zweitaufzeichnung_und_daniel():
    a = W.einordnen(
        [
            "20261019_181822_i4",
            "20261019_181822_i4_sp2",
            "20261018_011802_i1",
            "20261019_224031_i4_sp2",
            "ablauf_fein",
        ]
    )
    assert a == {
        "20261019_181822_i4": "selbst",
        "20261019_181822_i4_sp2": None,
        "20261018_011802_i1": "ki",
        "20261019_224031_i4_sp2": "daniel",
        "ablauf_fein": None,
    }


def test_unverletzter_arbeiter_in_schussweite_zaehlt_nicht_als_getoetet():
    a = _bild(
        100, [_e(1, 1, 3, leben=10000), _e(4, 1, 3, leben=10000), _e(2, 2, 22, x=130, leben=10000)]
    )
    ev = W.vergleiche(a, _bild(130, [_e(4, 1, 3, leben=10000), _e(2, 2, 22, x=130, leben=10000)]))
    assert ev[0]["sicher"] == "keine" and ev[0]["taeter"] == []


def test_verletzter_arbeiter_in_schussweite_zaehlt():
    a = _bild(
        100, [_e(1, 1, 3, leben=3000), _e(4, 1, 3, leben=10000), _e(2, 2, 22, x=130, leben=10000)]
    )
    ev = W.vergleiche(a, _bild(130, [_e(4, 1, 3, leben=10000), _e(2, 2, 22, x=130, leben=10000)]))
    assert ev[0]["sicher"] == "nah" and [u["nr"] for u in ev[0]["taeter"]] == [2]
