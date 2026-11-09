"""B-175: Sklaven im Brandtrupp laufen im Zickzack, ohne Spiel."""

from selfaware.micro.tasks import raids as RA


def _e(typ, x, y, besitzer=1, leben=6000):
    return {"typ": typ, "x": x, "y": y, "besitzer": besitzer, "leben": leben}


def _sklaven(*orte):
    return {n: _e(RA.SKLAVE, x, y) for n, (x, y) in enumerate(orte, 1)}


def _G(*orte):
    return {100 + i: {"typ": 3, "x": x, "y": y, "besitzer": 2} for i, (x, y) in enumerate(orte)}


class Kern:
    def __init__(self, geht=True):
        self.ausweichend, self.frei, self.auf, self.geht = [], [], [], geht
        self.gesendet = []

    def ausweichen(self, einheiten, ziel, trupp=1):
        self.ausweichend.append((list(einheiten), tuple(ziel), trupp))
        return self.geht

    def senden(self, liste):
        self.gesendet += [b["angriff"] for b in liste]
        return [] if self.geht else liste

    def freigeben(self, einheiten):
        self.frei.append(list(einheiten))

    def aufraeumen(self, lebend):
        self.auf.append(set(lebend))

    def bericht(self):
        return "kern"


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte, bis=None):
        self.liste.append(b["angriff"])


class ImmerFeuer:
    def neue_runde(self, L, G):
        pass

    def unter_feuer(self, nr, e):
        return True


def _trupp(kern=None):
    t = RA.Brandtrupp(1, lambda nr: 0, kern=kern)
    t.schuss = ImmerFeuer()
    return t


def test_ohne_beschuss_laeuft_der_sklave_gerade_mit_normalem_angriff():
    k, b = Kern(), Befehle()
    t = RA.Brandtrupp(1, lambda nr: 0, kern=k)
    t.schritt(_sklaven((100, 100)), _G((150, 100)), b)
    assert k.ausweichend == [] and k.gesendet == [{"einheiten": [1], "gebaeude": 100}]


def test_ein_schuetze_in_reichweite_loest_das_ausweichen_aus():
    k, b = Kern(), Befehle()
    t = RA.Brandtrupp(1, lambda nr: 0, kern=k)
    L = _sklaven((100, 100))
    L[9] = _e(22, 110, 100, besitzer=2)
    t.schritt(L, _G((160, 100)), b)
    assert len(k.ausweichend) == 1 and k.gesendet == []
    assert t.im_ausweichen == 1


def test_nach_dem_feuer_laeuft_er_wieder_gerade():
    k, b = Kern(), Befehle()
    t = RA.Brandtrupp(1, lambda nr: 0, kern=k)
    G = _G((160, 100))
    L = _sklaven((100, 100))
    L[9] = _e(22, 110, 100, besitzer=2)
    t.schritt(L, G, b)
    frei = _sklaven((120, 100))
    for _ in range(2):  # Nachlauf: der naechste Pfeil kann noch kommen
        t.schritt(frei, G, b)
    assert t.im_ausweichen == 1 and k.gesendet == []
    t.schritt(frei, G, b)
    assert t.im_ausweichen == 0 and k.gesendet == [{"einheiten": [1], "gebaeude": 100}]


def test_ohne_kern_geht_der_angriff_ans_modul():
    b = Befehle()
    t = _trupp()
    t.schritt(_sklaven((100, 100)), _G((150, 100)), b)
    assert b.liste == [{"einheiten": [1], "gebaeude": 100}]
    assert t.im_ausweichen == 0 and "kern" not in t.bericht()


def test_mit_kern_laeuft_der_sklave_im_zickzack_zum_halt_vor_dem_gebaeude():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    t.schritt(_sklaven((100, 100)), _G((150, 100)), b)
    assert b.liste == [] and k.frei == [] and k.auf == [{1}]
    assert k.ausweichend == [([1], (150 - RA.AUSWEICH_HALT, 100), RA.AUSWEICH_TRUPP + 1)]
    assert t.im_ausweichen == 1 and "kern" in t.bericht()


def test_das_ziel_des_zickzacks_bleibt_stehen_solange_das_gebaeude_gleich_ist():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    G = _G((150, 100))
    t.schritt(_sklaven((100, 100)), G, b)
    for _ in range(RA.NEU_ALLE - 1):
        t.schritt(_sklaven((107, 101)), G, b)
    assert len(k.ausweichend) == 1  # dazwischen wird nur nachgesehen, nicht geschickt
    t.schritt(_sklaven((120, 104)), G, b)
    assert len(k.ausweichend) == 2 and k.ausweichend[0][1] == k.ausweichend[1][1]


def test_nah_am_gebaeude_uebernimmt_der_normale_angriff():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    G = _G((150, 100))
    t.schritt(_sklaven((100, 100)), G, b)
    t.schritt(_sklaven((150 - RA.AUSWEICH_NAH - 1, 100)), G, b)
    assert b.liste == [] and t.im_ausweichen == 1
    t.schritt(_sklaven((150 - RA.AUSWEICH_NAH, 100)), G, b)
    assert k.gesendet == [
        {"einheiten": [1], "gebaeude": 100}
    ]  # ueber den Kern, das beendet dort den Zickzack
    assert b.liste == [] and k.frei == [] and t.im_ausweichen == 0


def test_es_sind_hoechstens_acht_im_zickzack_der_rest_laeuft_normal():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    orte = [(100, 100 + i) for i in range(10)]
    G = _G(*[(150, 80 + 4 * i) for i in range(10)])
    t.schritt(_sklaven(*orte), G, b)
    assert len(k.ausweichend) == RA.AUSWEICH_MAX == t.im_ausweichen
    assert len(k.gesendet) == 10 - RA.AUSWEICH_MAX and b.liste == []
    assert len({z[2] for z in k.ausweichend}) == RA.AUSWEICH_MAX


def test_voller_ring_laesst_das_modul_angreifen():
    k, b = Kern(geht=False), Befehle()
    t = _trupp(k)
    t.schritt(_sklaven((100, 100)), _G((150, 100)), b)
    assert b.liste == [
        {"einheiten": [1], "gebaeude": 100}
    ]  # der Ring nimmt nichts: Das Modul greift an
    assert t.im_ausweichen == 0


def test_ein_verschwundenes_ziel_laesst_den_sklaven_beim_kern_los():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    L = _sklaven((100, 100))
    t.schritt(L, _G((150, 100)), b)
    t.schritt(L, {}, b)
    assert k.frei == [[1]] and t.im_ausweichen == 0


def test_ein_toter_sklave_fliegt_ohne_freigabe_heraus():
    k, b = Kern(), Befehle()
    t = _trupp(k)
    t.schritt(_sklaven((100, 100)), _G((150, 100)), b)
    t.schritt({}, _G((150, 100)), b)
    assert k.auf[-1] == set() and k.frei == [] and t.im_ausweichen == 0


def test_brennt_das_gebaeude_laeuft_er_zum_naechsten_im_zickzack():
    k, b = Kern(), Befehle()
    t = RA.Brandtrupp(1, lambda nr: 50 if nr == 100 else 0, kern=k)
    t.schuss = ImmerFeuer()
    G = _G((150, 100), (150, 200))
    t.schritt(_sklaven((110, 100)), G, b)
    assert k.ausweichend[-1][1][1] == 100
    t.ausweichend.discard(1)  # nah am Gebaeude hat das Modul uebernommen
    L = _sklaven((147, 100))
    L[1]["zustand"] = 0  # der Sklave steht: Dann bekommt er seinen naechsten Befehl sofort
    t.schritt(L, G, b)
    x, y = k.ausweichend[-1][1]
    assert abs(x - 150) <= 1 and y == 200 - RA.AUSWEICH_HALT and t.im_ausweichen == 1
