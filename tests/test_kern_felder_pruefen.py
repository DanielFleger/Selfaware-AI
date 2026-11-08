"""B-169: die Proben fuer die neuen Kern-Felder schlagen an, wenn ein Wert nicht stimmt (offline)."""

from selfaware.game import kern_leitung as KL
from selfaware.tools.experiments import kern_felder_pruefen as P


def _eigene(**w):
    e = dict.fromkeys(KL.EINHEIT_FELDER, 0)
    e.update(nr=5, besitzer=1, typ=70, x=160, y=50, feinx=1283, feiny=403, gruppe=3)
    e.update(w)
    return e


def _fremd(**w):
    e = {n: v for n, v in _eigene(nr=9, besitzer=2, **w).items() if n not in KL.NUR_EIGEN}
    return e


def _welt(einheiten, lord=0, trupps=None, geschosse=None):
    return KL.Weltbild(
        tick=10,
        epoche=1,
        ich=1,
        kern=21,
        graben_geplant=0,
        graben_ausgehoben=0,
        einheiten={e["nr"]: e for e in einheiten},
        gebaeude={},
        vorrat={},
        trupps={3: dict(nr=3, zustand=1, zielx=1, ziely=1, zielgebaeude=0, zielgebaeude_uid=0)}
        if trupps is None
        else trupps,
        geschosse=geschosse or {},
        lord_feindabstand=lord,
    )


def _verstoesse(*args, **kw):
    p = P.Pruefung()
    p.bild(_welt(*args, **kw))
    return p.verstoss


def test_stimmiges_bild_ohne_verstoss():
    assert not _verstoesse([_eigene(), _fremd()])


def test_feinposition_die_nicht_zum_feld_passt():
    assert _verstoesse([_eigene(feinx=900)])["feinposition_passt"] == 1


def test_fremde_einheit_mit_verbotenem_schluessel():
    fremd = _fremd()
    fremd["planx"] = 3
    assert _verstoesse([_eigene(), fremd])["fremd_geschwaerzt"] == 1


def test_eigene_gruppe_fehlt_in_der_tabelle():
    assert _verstoesse([_eigene()], trupps={})["eigene_gruppe_in_trupptabelle"] == 1


def test_lordabstand_weicht_ab():
    assert (
        _verstoesse([_eigene(typ=P.LORD, feindabstand=7)], lord=9)["lordabstand_gleich_einheit"]
        == 1
    )


def test_naechstes_wegfeld_weit_weg():
    assert _verstoesse([_eigene(naechstesfeld=P.feld_aus(210, 50))])["naechstes_feld_nebenan"] == 1
    assert not _verstoesse([_eigene(naechstesfeld=P.feld_aus(161, 51))])


def test_feld_umrechnung_wie_im_kern_gemessen():
    assert [P.feld_aus(199, 0), P.feld_aus(198, 1), P.feld_aus(197, 2)] == [0, 2, 6]
    for x, y in ((199, 0), (200, 0), (198, 1), (150, 77), (5, 195)):
        assert P.feld_xy(P.feld_aus(x, y)) == (x, y)


def test_geschossfeld():
    q = dict.fromkeys(KL.GESCHOSS_FELDER, 0)
    q.update(nr=1, typ=24, x=160, y=50, feld=P.feld_aus(160, 50), vcos=0.6, vsin=0.8)
    assert not _verstoesse([_eigene()], geschosse={1: q})
    assert _verstoesse([_eigene()], geschosse={1: {**q, "feld": 5}})["geschoss_feld_passt"] == 1


def test_angreiferzahl_ist_eine_kleine_zahl():
    assert _verstoesse([_eigene(nahangreifer=500)])["angreiferzahl_klein"] == 1
    assert not _verstoesse([_eigene(nahangreifer=16)])
