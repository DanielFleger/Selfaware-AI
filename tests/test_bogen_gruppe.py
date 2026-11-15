"""#361 Bogenschuetzen entscheiden als Gruppe (Daniel 16.11.2026 00:27: "jo alleine sterbe ich - aber gemeinsam koennten sie gewinnen und
dann so - dann versuch ichs erst gar nicht. Dabei ist das androhen schon meist genug gegen spieler ... die bogenschuetzen koennten extrem
gut wirtschaft stoeren"). Probe 5: Takt 879 "danger_at_stand" fuer alle 5, Takt 1.450 "advance_refused_by_path" - die Wegfuehrung lehnte
jeden Schuetzen einzeln ab, sobald ihn ein Feind treffen konnte."""

from selfaware.micro import wegfuehrung as W
from selfaware.micro.tasks import vorstoss as VS


def _e(owner, typ, x=100, y=100, leben=10000):
    return {"besitzer": owner, "typ": typ, "x": x, "y": y, "leben": leben}


class Befehle:
    def __init__(self):
        self.liste = []

    def __call__(self, b, _warte=None, bis=None):
        self.liste.append(b)


def _gruppe():
    return {
        n: _e(1, 22, 100 + n, 100) for n in range(1, 7)
    }  # 6 eigene Bogenschuetzen um (103, 100)


def _vorstoss():
    v = VS.Vorstoss(1, (100, 300), bis=40000)
    v.weg = W.Wegfuehrung(1)
    v.mitglieder = set(range(1, 7))  # setzt sonst schritt, bevor es Ziele prueft
    return v


def test_freigabe_je_auftrag_uebergeht_die_gefahr_am_platz():
    L = {1: _e(1, 22, 100, 100), 60: _e(2, 22, 150, 100)}
    for trotz, erwartet in ((False, "gefahr"), (True, "unterwegs")):
        w = W.Wegfuehrung(1)
        w.fuehre(1, "ort", (140, 100), "vorstoss", trotz=trotz)
        assert w.schritt(L, {}, Befehle())[1] == erwartet


def test_gedeckter_arbeiter_wird_ziel_wenn_die_gruppe_gewinnt():
    L = {
        **_gruppe(),
        50: _e(2, 3, 200, 100),
        60: _e(2, 22, 200, 100),
    }  # ein Bogenschuetze steht beim Holzfaeller
    v = _vorstoss()
    assert not v._sicher_zu_beschiessen(50, L, {}, (103, 100))  # kein Platz, an dem er nicht trifft
    assert v._darf(50, L, {}, (103, 100)) == "sieg"
    v.schritt(1000, L, {}, Befehle())
    a = v.weg.auftraege
    assert all(a[n].ziel in (50, 60) and a[n].trotz for n in range(1, 7)), {
        n: (a[n].ziel, a[n].trotz) for n in a
    }
    st = v.weg.schritt(L, {}, Befehle())
    assert all(st[n] != "gefahr" for n in range(1, 7)), (
        st
    )  # alle gehen zusammen, keiner bleibt stehen


def test_ohne_sieg_kein_angriff():
    L = {
        **_gruppe(),
        50: _e(2, 3, 200, 100),
        **{60 + i: _e(2, 22, 200 + i % 4, 100 + i // 4) for i in range(12)},
    }
    v = _vorstoss()
    assert v._darf(50, L, {}, (103, 100)) is None


def test_beschuss_auf_dem_weg_zaehlt_mit():
    L = {**_gruppe(), 50: _e(2, 3, 200, 100), 60: _e(2, 22, 200, 100)}
    L.update(
        {70 + i: _e(2, 22, 125 + i % 5, 140 + i // 5) for i in range(10)}
    )  # treffen den geraden Weg (40 Felder), nicht den Platz (56)
    v = _vorstoss()
    stand = VS._schritt_auf((200, 100), (103, 100), VS.SCHUSS - VS.STAND_VOR)
    assert v._gewinnt(stand, L) and not v._gewinnt(stand, L, von=(103, 100))
    assert v._darf(50, L, {}, (103, 100)) is None


def test_vorruecken_haelt_keinen_einzelnen_an():
    L = {**_gruppe(), 52: _e(2, 3, 300, 100)}  # ferner Arbeiter: Vorruecken
    v = _vorstoss()
    v.schritt(1000, L, {}, Befehle())
    a = v.weg.auftraege
    assert a and all(x.art == "ort" and x.trotz for x in a.values()), {
        n: (x.art, x.ziel, x.trotz) for n, x in a.items()
    }
