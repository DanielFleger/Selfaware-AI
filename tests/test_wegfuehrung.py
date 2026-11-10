"""B-182 Wegfuehrung fuer alle Einheiten (Plan_Wegfuehrung.md), ohne Spiel."""

import selfaware.services.schussfeld as SF
from selfaware.micro import wegfuehrung as W


def _e(besitzer, typ, x, y, leben=10000):
    return {"besitzer": besitzer, "typ": typ, "x": x, "y": y, "leben": leben}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte, bis=None):
        self.liste.append(b["angriff"])


def _runde(w, L, G=None):
    b = Befehle()
    st = w.schritt(L, G or {}, b)
    return st, b.liste


def test_fernkaempfer_laeuft_bis_in_reichweite_und_greift_dann_an():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, b = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    assert st[1] == "unterwegs" and "lauf" in b[0] and b[0]["lauf"][0] > 100
    st, b = _runde(w, {1: _e(1, 22, 212, 100), 50: _e(2, 3, 250, 100)})  # 38 Felder: Reichweite 40 minus 2
    assert st[1] == "greift_an" and b == [{"einheiten": [1], "ziel": 50}]


def test_neue_gefahr_im_weg_wird_umgangen():
    """Daniel 11.11.: 'er sollte immer adjustieren sollte im lauf eine gefahr in den weg kommen'."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    L = {1: _e(1, 22, 100, 100), 50: _e(2, 3, 300, 100)}
    _, b1 = _runde(w, L)
    L2 = {**L, 60: _e(2, 22, 150, 100), 61: _e(2, 22, 150, 104)}  # zwei Bogenschuetzen mitten auf dem Weg
    _, b2 = _runde(w, L2)
    assert b2 and b2[0]["lauf"] != b1[0]["lauf"]
    assert SF.gefahr_am(tuple(b2[0]["lauf"]), W.gefahren(L2, {}, 1)) == 0


def test_ziel_in_gefahr_kein_befehl():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, b = _runde(w, {1: _e(1, 71, 100, 100), 60: _e(2, 22, 205, 100)}, {7: _e(2, 3, 200, 100)})
    assert st[1] == "gefahr" and b == []


def test_fernkaempfer_haelt_abstand_zu_kuerzerer_reichweite_nicht_zu_gleicher():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, _ = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 72, 250, 100)})  # Schleuderer 22: Standplatz 36 ist sicher
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "einheit", 51)
    st, b = _runde(w2, {1: _e(1, 22, 100, 100), 51: _e(2, 22, 250, 100)})  # Bogenschuetze 44: jeder Standplatz in seiner Reichweite
    assert st[1] == "gefahr" and b == []


def test_hoechstens_acht_befehle_je_runde_und_keine_wiederholung():
    w = W.Wegfuehrung(1)
    L = {}
    for i in range(12):
        L[i + 1] = _e(1, 22, 100, 100 + 2 * i)
        L[100 + i] = _e(2, 3, 300, 100 + 2 * i)
        w.fuehre(i + 1, "einheit", 100 + i)
    _, b1 = _runde(w, L)
    _, b2 = _runde(w, L)
    _, b3 = _runde(w, L)
    assert len(b1) == W.BUDGET and len(b2) == 12 - W.BUDGET and b3 == []


def test_wiedervergebene_nummer_ist_kein_ziel():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 3, 250, 100)})
    st, b = _runde(w, {1: _e(1, 22, 100, 100), 50: _e(2, 1, 260, 100)})  # Nummer 50 traegt jetzt einen Bauern
    assert st[1] == "ziel_weg" and b == []


def test_verborgene_fallgrube_ist_keine_gefahr_ein_turm_schon():
    """FAIRNESS F12: Holzfallen und Pech des Gegners sind verborgen; Tuerme sind sichtbar."""
    w = W.Wegfuehrung(1)
    w.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 8: _e(2, 67, 201, 100)})
    assert st[1] == "unterwegs"
    w2 = W.Wegfuehrung(1)
    w2.fuehre(1, "gebaeude", 7)
    st, _ = _runde(w2, {1: _e(1, 71, 100, 100)}, {7: _e(2, 3, 200, 100), 9: _e(2, 77, 210, 100)})
    assert st[1] == "gefahr"


def test_nahkaempfer_darf_an_einen_soldaten_heran():
    w = W.Wegfuehrung(1)
    w.fuehre(1, "einheit", 50)
    st, b = _runde(w, {1: _e(1, 75, 100, 100), 50: _e(2, 24, 200, 100)})  # Speertraeger: seine eigene Naehe zaehlt nicht
    assert st[1] == "unterwegs" and "lauf" in b[0]


def test_brandtrupp_gibt_den_weg_ab_und_wechselt_bei_gefahr_das_ziel():
    """Plan_Wegfuehrung.md: der Brandtrupp waehlt das Ziel, die Wegfuehrung den Weg; meldet sie Gefahr, nimmt er ein anderes."""
    from selfaware.micro.tasks import raids as RA

    bt = RA.Brandtrupp(1, lambda nr: 0)
    w = W.Wegfuehrung(1)
    bt.weg = w
    L = {1: _e(1, 71, 100, 100)}
    G = {7: _e(2, 3, 200, 100), 8: _e(2, 3, 100, 200)}
    b = Befehle()
    bt.schritt(L, G, b)
    assert b.liste == [] and w.fuehrt(1)  # der Brandtrupp selbst befiehlt nichts mehr
    erstes = bt.ziel[1]
    st, b = _runde(w, L, G)
    assert st[1] == "unterwegs" and "lauf" in b[0]
    L2 = {**L, 60: _e(2, 22, G[erstes]["x"] + 5, G[erstes]["y"])}  # ein Bogenschuetze stellt sich ans Ziel
    st, _ = _runde(w, L2, G)
    assert st[1] == "gefahr"
    bt.schritt(L2, G, Befehle())
    assert bt.ziel.get(1) not in (None, erstes) and w.fuehrt(1)
