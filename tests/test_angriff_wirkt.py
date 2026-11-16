"""#362 Nahangriff, der nicht wirkt (Daniel 16.11.2026 00:43 "bis nachweislich alle einheiten optimal eingesetzt werden"). Probe 6: Speertraeger
standen in 40 % ihrer Angriffsrunden am Ziel ohne Kampf (Median 251, hoechstens 1.442 Takte); Speer 218 bekam bei Takt 3.959 den Angriff,
stand ab 4.222 still (Zustand 2) und verlor unter Beschuss 12.000 Leben - der gleiche Befehl kam erst nach NEU_ALLE Runden wieder."""

from selfaware.micro import wegfuehrung as W


def _e(owner, typ, x=100, y=100, leben=10000, **k):
    d = {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}
    d.update(k)
    return d


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte=None, bis=None):
        self.liste.append(b)


def _runden(zustaende, leben=None):
    """Speertraeger 1 steht neben Holzfaellerhuette 7; je Runde ein Zustand (und Leben der Huette). -> [(Status, Zahl Befehle)]"""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7, "nahkampfraid")
    aus = []
    for i, z in enumerate(zustaende):
        L = {1: _e(1, 24, 199, 101, zustand=z)}
        G = {7: _e(2, 3, 200, 100, leben=(leben[i] if leben else 60))}
        b = Befehle()
        st = w.schritt(L, G, b)
        aus.append((st[1], len(b.liste)))
    return aus


def test_steht_ohne_kampf_bekommt_sofort_einen_neuen_befehl_und_dann_ein_anderes_ziel():
    aus = _runden([2, 2, 2, 2])
    assert aus[0] == ("greift_an", 1)
    assert aus[1] == ("greift_an", 1) and aus[2] == ("greift_an", 1), (
        aus
    )  # frueher: 0 Befehle bis NEU_ALLE
    assert aus[3][0] == "kein_weg", aus  # nach LEER_RUNDEN Runden ohne Wirkung


def test_kaempft_kein_neuer_befehl():
    aus = _runden([2, 107, 107, 107])
    assert aus[0] == ("greift_an", 1) and all(x == ("greift_an", 0) for x in aus[1:]), aus


def test_ziel_verliert_leben_wirkt_auch_ohne_kampfzustand():
    # Probe 6, Feld B19 (Typ 33): Leben 150 -> 110 -> 50 -> 10, die Speertraeger daneben mit Zustand 2
    aus = _runden([2, 2, 2, 2], leben=[150, 110, 50, 10])
    assert aus[0] == ("greift_an", 1) and all(x == ("greift_an", 0) for x in aus[1:]), aus
