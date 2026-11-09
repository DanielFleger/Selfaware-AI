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


class Kern:
    def __init__(self, geht=True):
        self.ausweichend, self.frei, self.auf, self.geht = [], [], [], geht

    def ausweichen(self, einheiten, ziel, trupp=1):
        self.ausweichend.append((einheiten, tuple(ziel), trupp))
        return self.geht

    def freigeben(self, einheiten):
        self.frei.append(list(einheiten))

    def aufraeumen(self, lebend):
        self.auf.append(set(lebend))

    def bericht(self):
        return "kern"


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


def test_ohne_beschuss_rueckt_der_vorstoss_gerade_vor():
    k = Kern()
    L = _L(_e(1, 22, 100, 100), _e(2, 3, 200, 100))
    _, b, _ = _lauf(L, v=V.Vorstoss(1, HEIM, kern=k))
    assert k.ausweichend == [] and k.frei == [[1]] and b[0]["lauf"][0] == 100 + V.SCHRITT


def test_zickzack_fuehrt_der_kern_und_das_modul_bekommt_nichts():
    k = Kern()
    L = _L(_e(1, 22, 100, 100), _e(1, 22, 100, 101), _e(2, 3, 200, 100))
    for n in L:
        L[n]["leben"] = 10000
    v0 = V.Vorstoss(1, HEIM, kern=k)
    v0.schuss.leben = {1: 12000, 2: 12000}  # beide haben gerade Leben verloren
    v, b, aus = _lauf(L, v=v0)
    assert b == [] and k.frei == [] and k.auf == [{1, 2}]
    x = 100 + V.SCHRITT
    assert k.ausweichend == [
        ([1], (x, 97), 1),
        ([2], (x, 102), 2),
    ]  # quer zum Weg, LUECKE Felder auseinander
    assert "rueckt vor" in aus[0] and "kern" in v.bericht()


def _plaetze(anzahl, ziel=(200, 100), start=(100, 100)):
    v = V.Vorstoss(1, HEIM)
    v.lage = {i: _e(1, 22, start[0], start[1] + i) for i in range(anzahl)}
    return v, v._aufstellung(list(range(anzahl)), ziel)


def test_breite_aufstellung_haelt_ueberall_die_luecke():
    for n in (1, 2, 3, 4, 5, 8):
        for ziel in ((200, 100), (0, 100), (100, 300), (100, 0)):
            _, p = _plaetze(n, ziel)
            assert len(p) == n and sorted(e[0][0] for e in p) == list(range(n))
            orte = [e[1] for e in p]
            for i, a in enumerate(orte):
                for b in orte[i + 1 :]:
                    assert V.schach(a, b) >= V.LUECKE - 1, (n, ziel, orte)


def test_breite_aufstellung_steht_quer_zum_weg_mit_reihen_dahinter():
    _, p = _plaetze(8, (200, 100))
    assert sorted({e[1][1] for e in p}) == [92, 97, 102, 107]  # vier Spalten quer zum Weg
    assert sorted({e[1][0] for e in p}) == [195, 200]  # die zweite Reihe dahinter, nicht davor
    _, p = _plaetze(8, (100, 0))
    assert sorted({e[1][1] for e in p}) == [0, 5]


def test_mehr_als_acht_teilen_sich_die_plaetze():
    _, p = _plaetze(12)
    assert len(p) == V.TRUPPS and sum(len(e[0]) for e in p) == 12 and all(e[0] for e in p)


def test_plaetze_bleiben_solange_die_gruppe_gleich_ist():
    v, p = _plaetze(5)
    for i in v.lage:
        v.lage[i]["y"] = 200 - v.lage[i]["y"]  # die Reihenfolge quer zum Weg dreht sich um
    assert [e[0] for e in v._aufstellung(list(range(5)), (200, 100))] == [e[0] for e in p]
    del v.lage[4]
    assert sum(len(e[0]) for e in v._aufstellung(list(range(4)), (200, 100))) == 4


def test_der_brandtrupp_nimmt_dem_vorstoss_plaetze_weg():
    v, _ = _plaetze(8)
    v.plaetze_setzen(5)
    assert v.plaetze == 3 and len(v._aufstellung(list(range(8)), (200, 100))) == 3
    v.plaetze_setzen(8)
    assert v.plaetze == 0 and v._aufstellung(list(range(8)), (200, 100)) == []
    v.plaetze_setzen(20)
    assert v.plaetze == 0


def test_ohne_freien_platz_laeuft_der_vorstoss_gerade_ueber_das_modul():
    k = Kern()
    v = V.Vorstoss(1, HEIM, kern=k)
    v.schuss.leben = {1: 12000}
    v.plaetze_setzen(8)
    L = _L(_e(1, 22, 100, 100), _e(2, 3, 200, 100))
    _, b, _ = _lauf(L, v=v)
    assert k.ausweichend == [] and k.frei == [[1]] and b[0]["lauf"][0] == 100 + V.SCHRITT


def test_abziehen_laeuft_im_zickzack():
    k = Kern()
    fern = [_e(2, 23, 132, 100 + i) for i in range(4)]
    L = _L(_e(1, 22, 100, 100), _e(1, 22, 100, 101), _e(1, 22, 100, 102), *fern)
    _, b, aus = _lauf(L, v=V.Vorstoss(1, HEIM, kern=k))
    assert b == [] and k.ausweichend[0][1][0] < 100 and "Schussfeld" in aus[0]


def test_schiessen_und_weichen_gibt_der_kern_vorher_her():
    k = Kern()
    _, b, _ = _lauf(_L(_e(1, 22, 100, 100), _e(2, 3, 110, 100)), v=V.Vorstoss(1, HEIM, kern=k))
    assert k.ausweichend == [] and k.frei == [[1]] and b == [{"einheiten": [1], "ziel": 2}]
    k = Kern()
    _, b, _ = _lauf(_L(_e(1, 22, 100, 100), _e(2, 26, 105, 100)), v=V.Vorstoss(1, HEIM, kern=k))
    assert k.ausweichend == [] and k.frei == [[1]] and b[0]["lauf"][0] < 100


def test_voller_ring_laesst_das_modul_gerade_laufen():
    k = Kern(geht=False)
    L = _L(_e(1, 22, 100, 100), _e(2, 3, 200, 100))
    v0 = V.Vorstoss(1, HEIM, kern=k)
    v0.schuss.leben = {1: 12000}
    _, b, _ = _lauf(L, v=v0)
    assert len(k.ausweichend) == 1 and k.frei == [[1]] and b[0]["lauf"][0] == 100 + V.SCHRITT


def test_alarm_und_ende_geben_die_einheiten_beim_kern_frei():
    k = Kern()
    v = V.Vorstoss(1, HEIM, bis=1000, kern=k)
    b = Befehle()
    v.schritt(500, _L(_e(1, 22, 150, 150), _e(2, 3, 300, 150)), {}, b)
    feinde = [_e(2, 24, 110, 100 + i) for i in range(V.ALARM_N)]
    v.schritt(600, _L(_e(1, 22, 150, 150), *feinde), {}, b)
    assert k.frei[-1] == [1] and v.mitglieder == set()
    k = Kern()
    v = V.Vorstoss(1, HEIM, bis=1000, kern=k)
    v.schritt(500, _L(_e(1, 22, 100, 100), _e(2, 3, 300, 100)), {}, b)
    v.schritt(1000, _L(_e(1, 22, 100, 100), _e(2, 3, 300, 100)), {}, b)
    assert k.frei[-1] == [1] and v.mitglieder == set()


def test_ziel_ohne_schaden_wird_aufgegeben():
    L = _L(_e(1, 22, 100, 100), _e(2, 24, 130, 100, leben=500), _e(2, 24, 131, 100, leben=500))
    v = V.Vorstoss(1, HEIM)
    b = Befehle()
    for t in range(V.STUR_RUNDEN + 3):
        v.schritt(500 + t, L, {}, b)
    assert {x["ziel"] for x in b.liste} == {2, 3}
