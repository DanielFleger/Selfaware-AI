"""B-172: Vorstoss der Schuetzen, ohne Spiel."""

from selfaware.micro.tasks import vorstoss as V


def _e(besitzer, typ, x, y, leben=10000):
    return {"besitzer": besitzer, "typ": typ, "x": x, "y": y, "leben": leben}


def _L(*einheiten):
    return dict(enumerate(einheiten, 1))


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte, bis=None):
        self.liste.append(b["angriff"])


HEIM = (100, 100)


def _lauf(L, G=None, t=500, v=None):
    v = v or V.Vorstoss(1, HEIM)
    b = Befehle()
    aus = v.schritt(t, L, G or {}, b)
    return v, b.liste, aus


def test_rueckt_auf_den_naechsten_arbeiter_vor():
    L = _L(_e(1, 22, 100, 100), _e(1, 22, 100, 101), _e(2, 3, 200, 100))
    v, b, _ = _lauf(L)
    assert b[0]["lauf"][0] == 100 + V.SCHRITT and sorted(b[0]["einheiten"]) == [1, 2]
    assert v.mitglieder == {1, 2}


def test_schiesst_auf_feind_in_reichweite_und_nennt_soldaten_vor_arbeitern():
    L = _L(_e(1, 22, 100, 100), _e(2, 3, 110, 100), _e(2, 24, 130, 100))
    _, b, _ = _lauf(L)
    assert b == [{"einheiten": [1], "ziel": 3}]


def test_weicht_nahkaempfern_aus_und_laeuft_von_ihnen_weg():
    L = _L(_e(1, 22, 100, 100), _e(2, 26, 105, 100))
    _, b, aus = _lauf(L)
    assert b[0]["lauf"][0] < 100 and "weicht" in aus[0]


def test_sklaven_scheucht_sie_nicht_weg_sondern_werden_beschossen():
    L = _L(_e(1, 22, 100, 100), _e(2, 71, 105, 100))
    _, b, _ = _lauf(L)
    assert b == [{"einheiten": [1], "ziel": 2}]


def test_rueckt_nicht_in_eine_uebermacht_an_schuetzen():
    fern = [_e(2, 22, 150, 100 + i) for i in range(3)]
    L = _L(_e(1, 22, 100, 100), *fern, _e(2, 3, 200, 100))
    v = V.Vorstoss(1, HEIM)
    b = Befehle()
    v.schritt(500, L, {}, b)
    assert b.liste == []


def test_rueckt_nicht_vor_einen_turm():
    L = _L(_e(1, 22, 100, 100), _e(2, 3, 200, 100))
    G = {9: {"besitzer": 2, "typ": 75, "x": 150, "y": 100}}
    _, b, _ = _lauf(L, G)
    assert b == []


def test_bleibt_vor_gebaeuden_auf_abstand():
    L = _L(_e(1, 22, 100, 100))
    G = {9: {"besitzer": 2, "typ": 3, "x": 100 + V.HALT_VOR, "y": 100}}
    _, b, _ = _lauf(L, G)
    assert b == []


def test_alarm_gibt_die_schuetzen_frei_und_danach_zurueck():
    feinde = [_e(2, 24, 110, 100 + i) for i in range(V.ALARM_N)]
    v, b, aus = _lauf(_L(_e(1, 22, 150, 150), *feinde))
    assert v.mitglieder == set() and b == [] and "Abwehr" in aus[0]
    b2 = Befehle()
    aus2 = v.schritt(600, _L(_e(1, 22, 150, 150), _e(2, 3, 300, 150)), {}, b2)
    assert v.mitglieder == {1} and "ruhig" in aus2[0]


def test_nach_der_fruehphase_sind_die_schuetzen_wieder_frei():
    v = V.Vorstoss(1, HEIM, bis=1000)
    b = Befehle()
    v.schritt(500, _L(_e(1, 22, 100, 100), _e(2, 3, 300, 100)), {}, b)
    assert v.mitglieder == {1}
    aus = v.schritt(1000, _L(_e(1, 22, 100, 100), _e(2, 3, 300, 100)), {}, b)
    assert v.mitglieder == set() and "Ende" in aus[0]


def test_gleicher_befehl_wird_nicht_jede_runde_wiederholt():
    L = _L(_e(1, 22, 100, 100), _e(2, 24, 130, 100))
    v = V.Vorstoss(1, HEIM)
    b = Befehle()
    for t in range(V.NEU_ALLE):
        v.schritt(500 + t, L, {}, b)
    assert len(b.liste) == 1
    v.schritt(600, L, {}, b)
    assert len(b.liste) == 2


def test_zieht_aus_dem_schussfeld_einer_ueberzahl_ab():
    fern = [_e(2, 23, 132, 100 + i) for i in range(4)]
    _, b, aus = _lauf(_L(_e(1, 22, 100, 100), _e(1, 22, 100, 101), _e(1, 22, 100, 102), *fern))
    assert b[0]["lauf"][0] < 100 and "Schussfeld" in aus[0]


def test_steht_nicht_gegen_vereinzelte_schuetzen_auf():
    fern = _e(2, 23, 132, 100)
    _, b, _ = _lauf(_L(*[_e(1, 22, 100, 100 + i) for i in range(5)], fern))
    assert b[0]["ziel"] == 6


def test_arbeiter_ohne_deckung_geht_vor_dem_gedeckten():
    gedeckt = _e(2, 3, 170, 100)
    fern = [_e(2, 23, 175, 100 + i) for i in range(3)]
    frei = _e(2, 3, 100, 200)
    L = _L(_e(1, 22, 100, 100), gedeckt, *fern, frei)
    _, b, aus = _lauf(L)
    assert b[0]["lauf"][1] > 100 and b[0]["lauf"][0] == 100 and "Ziel (100, 200)" in aus[0]


def test_ziel_ohne_schaden_wird_aufgegeben():
    L = _L(_e(1, 22, 100, 100), _e(2, 24, 130, 100, leben=500), _e(2, 24, 131, 100, leben=500))
    v = V.Vorstoss(1, HEIM)
    b = Befehle()
    for t in range(V.STUR_RUNDEN + 3):
        v.schritt(500 + t, L, {}, b)
    assert {x["ziel"] for x in b.liste} == {2, 3}
